"""Modellwahl und Request-Bau der b-api -- die Regeln, ohne das Netz.

Getrennt vom Client, weil hier das eigentliche Wissen liegt: welche
Modellfamilie welchen Body-Aufbau verlangt, und welches Modell gerade zu
nehmen ist. Als reine Funktionen ist beides ohne Netzzugriff pruefbar.

Die Eigenheiten sind nicht optional. Alle sind gegen die b-api gemessen:

* **GPT-5- und o-Serie** brauchen ``max_completion_tokens`` statt
  ``max_tokens`` und lehnen ein abweichendes ``temperature`` ab -- sonst 400.
* **Qwen3** wird ueber ``chat_template_kwargs`` das Denken abgeschaltet, was
  Faktor 7 bis 9 ausmacht (17,33 s gegen 1,96 s bei derselben Aufgabe).
  ``/no_think`` im Prompt wirkt **nicht**, das ist Qwen2.5-Syntax.
* **Mistral lehnt dasselbe Flag mit 400 ab**
  (``chat_template is not supported for Mistral tokenizers``). Wer es generisch
  mitsendet, faellt genau hier hin.
* **Reasoning-Modelle zaehlen ihr Denken mit.** Ist das Budget aufgebraucht,
  kommt ``content: null`` und der Text steht in ``reasoning``.

``demand`` ist die einzige Auslastungsinformation, die es gibt, und sie sagt
die Wartezeit gut vorher: gemessen unter 0,6 s bei 0 und 30 bis 41 s bei 5.
Die Skala ist von GWDG nicht dokumentiert und nach oben offen.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

__all__ = ["Model", "pick_model", "rank_models", "build_body", "read_answer"]

#: Modellfamilien mit abweichendem Body-Aufbau.
_MAX_COMPLETION_PRAEFIXE = ("gpt-5", "o1", "o3", "o4")
_THINKING_PRAEFIXE = ("qwen3",)
_KEIN_CHAT_TEMPLATE = ("mistral",)

DEFAULT_MAX_TOKENS = 1000


@dataclass(frozen=True)
class Model:
    """Ein Modell, wie ``/models`` es meldet."""

    id: str
    #: Auslastung. ``None``, wenn der Provider sie nicht liefert (OpenAI).
    demand: int | None = None
    status: str | None = None
    input: tuple[str, ...] = ()
    output: tuple[str, ...] = ()
    owned_by: str | None = None
    name: str | None = None

    @property
    def is_ready(self) -> bool:
        """Ob das Modell benutzbar gemeldet wird.

        Ein Provider ohne ``status`` (OpenAI) gilt als bereit -- die Angabe
        fehlt dort, sie ist nicht negativ.
        """
        return self.status is None or self.status == "ready"

    @property
    def can_chat(self) -> bool:
        """Ob es Text ausgibt.

        Ein Embedding- oder Audio-Modell an ``/chat/completions`` antwortet mit
        ``404 This is not a chat model``.
        """
        return not self.output or "text" in self.output

    @classmethod
    def from_response(cls, data: dict[str, Any]) -> Model:
        return cls(
            id=data.get("id") or "",
            demand=data.get("demand"),
            status=data.get("status"),
            input=tuple(data.get("input") or ()),
            output=tuple(data.get("output") or ()),
            owned_by=data.get("owned_by"),
            name=data.get("name"),
        )


def rank_models(models: list[Model]) -> list[Model]:
    """Alle brauchbaren Modelle, das am wenigsten ausgelastete zuerst.

    Gebraucht wird die ganze Reihenfolge, nicht nur der Erste: gemessen meldet
    ``apertus-70b-instruct-2509`` ``status: ready`` und ``demand: 0``,
    antwortet aber mit ``503 Model pricing unavailable``. Dass ein Modell
    untauglich ist, steht in keiner Modellliste -- man merkt es erst beim
    Fragen, und dann braucht man einen Nachfolger.
    """
    brauchbar = [m for m in models if m.is_ready and m.can_chat]
    # demand None (Provider ohne Auslastungsangabe) hinten einsortieren, damit
    # ein gemessener Wert einer fehlenden Angabe vorgezogen wird.
    return sorted(brauchbar, key=lambda m: (m.demand if m.demand is not None else 99, m.id))


def pick_model(models: list[Model], *, prefer: str | None = None) -> Model:
    """Waehle ein Modell -- das am wenigsten ausgelastete, das antworten kann.

    Args:
        prefer: gewuenschte Modell-ID. Ist sie nicht in der Liste, wird das
            gemeldet statt still auf ein anderes Modell zu wechseln. Modell-IDs
            aendern sich ohne Ankuendigung -- aus ``deepseek-v4-flash`` wurde
            binnen neun Tagen ``deepseek-v4-flash-0731``, der alte Name
            antwortet seither mit 503. Ein stiller Wechsel waere schlimmer als
            ein Fehler: die Antwort kaeme von einem anderen Modell, ohne dass
            es jemand merkt.

    Raises:
        ValueError: wenn ``prefer`` fehlt oder kein Modell brauchbar ist.
    """
    if prefer:
        for m in models:
            if m.id == prefer:
                return m
        verfuegbar = ", ".join(m.id for m in models) or "(keine)"
        raise ValueError(
            f"Modell {prefer!r} gibt es hier nicht. Verfuegbar: {verfuegbar}. "
            "Modell-IDs aendern sich ohne Ankuendigung -- vor einem festen "
            "Eintrag gegen /models pruefen."
        )

    rangfolge = rank_models(models)
    if not rangfolge:
        raise ValueError(
            f"Kein antwortbereites Textmodell unter {len(models)} gemeldeten."
        )
    return rangfolge[0]


def build_body(
    model: str,
    messages: list[dict[str, str]],
    *,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    temperature: float = 0.0,
    thinking: bool = False,
    stream: bool = False,
) -> dict[str, Any]:
    """Baue den Request-Body fuer die Modellfamilie von ``model``.

    Args:
        thinking: ``True`` laesst Qwen3 denken. Vorgabe ist ``False``, weil das
            Faktor 7 bis 9 ausmacht und fuer Extraktion oder Klassifikation
            nichts bringt.
    """
    kennung = model.lower()
    body: dict[str, Any] = {"model": model, "messages": messages}

    if kennung.startswith(_MAX_COMPLETION_PRAEFIXE):
        body["max_completion_tokens"] = max_tokens
        # temperature bewusst weggelassen -- diese Familie lehnt einen
        # abweichenden Wert mit 400 ab.
    else:
        body["max_tokens"] = max_tokens
        body["temperature"] = temperature

    if (
        not thinking
        and kennung.startswith(_THINKING_PRAEFIXE)
        and not any(k in kennung for k in _KEIN_CHAT_TEMPLATE)
    ):
        body["chat_template_kwargs"] = {"enable_thinking": False}

    if stream:
        body["stream"] = True
        # Ohne include_usage fehlt der Verbrauch im letzten Ereignis, und die
        # Wartezeit laesst sich nicht von der Generierzeit trennen.
        body["stream_options"] = {"include_usage": True}

    return body


def read_answer(response: dict[str, Any]) -> str:
    """Lies den Antworttext.

    Prueft ``content`` **und** ``reasoning``: ist das Token-Budget fuer das
    Denken draufgegangen, kommt ``content: null`` und der Text steht im
    zweiten Feld. Wer nur ``content`` liest, bekommt dort nichts.
    """
    auswahl = response.get("choices") or []
    if not auswahl:
        return ""
    nachricht = auswahl[0].get("message") or {}
    return str(nachricht.get("content") or nachricht.get("reasoning") or "")
