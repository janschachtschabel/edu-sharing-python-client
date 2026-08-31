"""Model choice and request shape for the b-api -- the rules, without the network.

Separate from the client because this is where the actual knowledge sits: which
model family requires which body layout, and which model to use right now. As
pure functions both are testable without network access.

The quirks are not optional. All were measured against the b-api:

* **The GPT-5 and o series** need ``max_completion_tokens`` instead of
  ``max_tokens`` and reject a deviating ``temperature`` -- otherwise 400.
* **Qwen3** gets thinking switched off through ``chat_template_kwargs``, worth
  a factor of 7 to 9 (17.33 s versus 1.96 s on the same task). ``/no_think`` in
  the prompt does **not** work -- that is Qwen2.5 syntax.
* **Mistral rejects the very same flag with 400**
  (``chat_template is not supported for Mistral tokenizers``). Sending it
  generically is exactly where you fall over.
* **Reasoning models count their thinking.** Once the budget is spent,
  ``content`` is null and the text sits in ``reasoning``.

``demand`` is the only load information available, and it predicts waiting time
well: measured below 0.6 s at 0 and 30 to 41 s at 5. The scale is undocumented
by GWDG and open-ended.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

__all__ = [
    "Model", "pick_model", "rank_models", "build_body", "read_answer",
    "DEFAULT_EFFORT", "DEFAULT_VERBOSITY", "UNSET", "ReasoningParam",
]

#: Model families with a deviating body layout.
_MAX_COMPLETION_PREFIXES = ("gpt-5", "o1", "o3", "o4")
_THINKING_PREFIXES = ("qwen3",)
_NO_CHAT_TEMPLATE = ("mistral",)

#: Families that accept ``reasoning_effort`` and ``verbosity``. The same
#: prefixes as above today, but for a different reason -- body layout there,
#: reasoning capability here -- so they are named separately and may diverge.
#: Measured 2026-08-31: ``gpt-5.6-luna`` and ``gpt-5-nano`` take both;
#: ``gpt-4o-mini`` and ``gpt-3.5-turbo`` answer 400.
_REASONING_PREFIXES = ("gpt-5", "o1", "o3", "o4")

DEFAULT_MAX_TOKENS = 1000

#: The default effort and verbosity. Low, because it is measurably cheaper:
#: ``gpt-5.6-luna`` spent 14 reasoning tokens without the parameter and 0 with
#: ``low`` on the same question (measured 2026-08-31).
DEFAULT_EFFORT = "low"
DEFAULT_VERBOSITY = "low"


class _Vorgabe:
    """Marks "the library's own default", distinguishable from a caller's value.

    The distinction carries a rule: a default may be dropped where the model
    does not know it, a caller's explicit value may not. Silently dropping the
    second would make an answer produced with low effort look exactly like one
    produced with high effort.
    """

    def __repr__(self) -> str:  # pragma: no cover - for error messages only
        return "<library default>"


#: Sentinel for "not chosen by the caller". ``None`` means "do not send it".
UNSET = _Vorgabe()

#: What ``reasoning_effort`` and ``verbosity`` accept. Three states, not two:
#: a value the caller chose, ``None`` for "do not send it", and ``UNSET`` for
#: "the library decides". Only the third may be dropped for an older model.
ReasoningParam = str | _Vorgabe | None


@dataclass(frozen=True)
class Model:
    """A model as ``/models`` reports it."""

    id: str
    #: Load. ``None`` when the provider does not report it (OpenAI).
    demand: int | None = None
    status: str | None = None
    input: tuple[str, ...] = ()
    output: tuple[str, ...] = ()
    owned_by: str | None = None
    name: str | None = None
    #: The day the provider switches it off, ``YYYY-MM-DD``. OpenAI reports it
    #: for 57 of its 132 models (measured 2026-08-31); the AcademicCloud does
    #: not report the field at all.
    shutdown_date: str | None = None

    def is_retired_on(self, day: date) -> bool:
        """Whether ``shutdown_date`` has arrived by ``day``.

        Takes the day rather than reading the clock, so a caller can ask about
        a planned run and a test stays deterministic.

        A model past its date may still be listed and may still answer --
        measured 2026-08-31, the earliest date in the list was 2026-07-23 and
        the model was still there. This reports the fact, it does not decide.

        An unparseable value is not a retirement: an unexpected format is a
        reason to claim nothing, not a reason to declare the model dead.
        """
        if not self.shutdown_date:
            return False
        try:
            return date.fromisoformat(self.shutdown_date) <= day
        except ValueError:
            return False

    @property
    def is_ready(self) -> bool:
        """Whether the model reports itself as usable.

        A provider without ``status`` (OpenAI) counts as ready -- the field is
        absent there, not negative.
        """
        return self.status is None or self.status == "ready"

    @property
    def can_chat(self) -> bool:
        """Whether it emits text.

        An embedding or audio model at ``/chat/completions`` answers with
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
            shutdown_date=data.get("shutdown_date"),
        )


def rank_models(models: list[Model]) -> list[Model]:
    """All usable models, least loaded first.

    The whole ranking is needed, not just the first entry: measured,
    ``apertus-70b-instruct-2509`` reports ``status: ready`` and ``demand: 0``
    yet answers with ``503 Model pricing unavailable``. That a model is unusable
    appears in no model list -- you find out by asking, and then you need a
    successor.
    """
    usable = [m for m in models if m.is_ready and m.can_chat]
    # Sort demand None (providers without load info) last, so a measured value
    # is preferred over a missing one.
    return sorted(usable, key=lambda m: (m.demand if m.demand is not None else 99, m.id))


def pick_model(models: list[Model], *, prefer: str | None = None) -> Model:
    """Choose a model -- the least loaded one that can answer.

    Args:
        prefer: the wanted model id. If it is not in the list, that is reported
            rather than silently switching to another model. Model ids change
            without notice -- ``deepseek-v4-flash`` became
            ``deepseek-v4-flash-0731`` within nine days, and the old name has
            answered 503 ever since. A silent switch would be worse than an
            error: the answer would come from a different model without anyone
            noticing.

    Raises:
        ValueError: when ``prefer`` is absent or no model is usable.
    """
    if prefer:
        for m in models:
            if m.id == prefer:
                return m
        available = ", ".join(m.id for m in models) or "(none)"
        raise ValueError(
            f"Model {prefer!r} does not exist here. Available: {available}. "
            "Model ids change without notice -- check against /models before "
            "hard-coding one."
        )

    ranking = rank_models(models)
    if not ranking:
        raise ValueError(
            f"No ready text model among the {len(models)} reported."
        )
    return ranking[0]


def _reasoning_param(
    body: dict[str, Any], name: str, wert: Any, model: str, *, vorgabe: str
) -> None:
    """Put one reasoning parameter into the body, or account for why not.

    Raises:
        ValueError: when the caller asked for a value this model does not take.
    """
    if wert is None:
        return
    kann = model.lower().startswith(_REASONING_PREFIXES)
    if isinstance(wert, _Vorgabe):
        # A default: apply it where it works, drop it silently where it does
        # not. That is what makes it a default rather than a request.
        if kann:
            body[name] = vorgabe
        return
    if not kann:
        raise ValueError(
            f"Model {model!r} does not take {name}={wert!r} -- it answers 400. "
            f"Only the {', '.join(_REASONING_PREFIXES)} families accept it. "
            f"Pass {name}=None to leave it out, or choose a model that takes it. "
            "It is not dropped for you: an answer produced without it would be "
            "indistinguishable from one produced with it."
        )
    body[name] = wert


def build_body(
    model: str,
    messages: list[dict[str, str]],
    *,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    temperature: float = 0.0,
    thinking: bool = False,
    stream: bool = False,
    reasoning_effort: ReasoningParam = UNSET,
    verbosity: ReasoningParam = UNSET,
) -> dict[str, Any]:
    """Build the request body for the model family of ``model``.

    Args:
        thinking: ``True`` lets Qwen3 think. The default is ``False`` because
            it costs a factor of 7 to 9 and buys nothing for extraction or
            classification.
        reasoning_effort: ``low``, ``medium`` or ``high`` for the GPT-5 and o
            series. Left unset it defaults to ``low``, which is applied only
            where the model takes it. ``None`` leaves it out entirely.
        verbosity: how long the answer should be, same families, same rule.

    Raises:
        ValueError: when a caller's explicit ``reasoning_effort`` or
            ``verbosity`` goes to a model that does not accept it.
    """
    key = model.lower()
    body: dict[str, Any] = {"model": model, "messages": messages}

    if key.startswith(_MAX_COMPLETION_PREFIXES):
        body["max_completion_tokens"] = max_tokens
        # temperature deliberately omitted -- this family rejects a deviating
        # value with 400.
    else:
        body["max_tokens"] = max_tokens
        body["temperature"] = temperature

    if (
        not thinking
        and key.startswith(_THINKING_PREFIXES)
        and not any(k in key for k in _NO_CHAT_TEMPLATE)
    ):
        body["chat_template_kwargs"] = {"enable_thinking": False}

    _reasoning_param(body, "reasoning_effort", reasoning_effort, model,
                     vorgabe=DEFAULT_EFFORT)
    _reasoning_param(body, "verbosity", verbosity, model,
                     vorgabe=DEFAULT_VERBOSITY)

    if stream:
        body["stream"] = True
        # Without include_usage the final event carries no usage, and waiting
        # time cannot be told apart from generation time.
        body["stream_options"] = {"include_usage": True}

    return body


def read_answer(response: dict[str, Any]) -> str:
    """Read the answer text.

    Checks ``content`` **and** ``reasoning``: if the token budget went into
    thinking, ``content`` is null and the text sits in the second field. Reading
    only ``content`` yields nothing there.
    """
    choices = response.get("choices") or []
    if not choices:
        return ""
    message = choices[0].get("message") or {}
    return str(message.get("content") or message.get("reasoning") or "")
