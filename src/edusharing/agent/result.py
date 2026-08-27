"""Fehler als Ergebnis statt als Ausnahme.

Ein Werkzeug, das ein Sprachmodell aufruft, muss auch im Fehlerfall etwas
zurueckgeben, mit dem das Modell weiterarbeiten kann. Eine durchgereichte
Ausnahme beendet stattdessen den Durchlauf -- und das Modell erfaehrt nie, dass
bloss ein Filter unbekannt war oder ein Knoten nicht existiert. Beides waere
eine brauchbare Auskunft.

Aufgefangen werden **ausschliesslich** Fehler dieser Bibliothek. Ein
``TypeError`` im eigenen Code ist ein Programmierfehler; ihn in einen
freundlichen Text zu verwandeln versteckt ihn, statt ihn zu beheben.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

from ..errors import EduSharingError

__all__ = ["ToolResult", "as_result"]


@dataclass(frozen=True)
class ToolResult:
    """Das Ergebnis eines Werkzeugaufrufs -- gelungen oder nicht.

    ``text`` ist immer gefuellt: ein Werkzeug braucht in jedem Fall etwas
    Ausgebbares.
    """

    ok: bool
    text: str
    data: Any = None
    error: str | None = None
    #: Der Klassenname des Fehlers, etwa ``"ValidationError"``. Damit kann ein
    #: Werkzeug unterscheiden, ob eine andere Frage hilft oder die Anmeldung
    #: fehlt -- ohne den Fehlertext zu zerlegen.
    error_type: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __bool__(self) -> bool:
        return self.ok


async def as_result(
    awaitable: Awaitable[Any],
    *,
    format: Callable[[Any], str] | None = None,
) -> ToolResult:
    """Fuehre ``awaitable`` aus und verpacke Ausgang wie Fehlschlag.

    Args:
        awaitable: die Arbeit, etwa ``repo.search("...")``.
        format: macht aus dem Ergebnis den Text. Ohne Angabe wird ``str()``
            verwendet.

    Returns:
        Ein ``ToolResult``. Bei einem ``EduSharingError`` ist ``ok`` falsch und
        ``error`` traegt die Meldung -- **ohne** den Java-Stacktrace, denn der
        Text landet im Modellkontext und moeglicherweise in einer Oberflaeche.

    Raises:
        Alles, was kein ``EduSharingError`` ist. Programmierfehler bleiben laut.
    """
    try:
        ergebnis = await awaitable
    except EduSharingError as exc:
        meldung = str(exc)
        return ToolResult(
            ok=False,
            text=meldung,
            error=meldung,
            error_type=type(exc).__name__,
            metadata={"status": exc.status} if exc.status else {},
        )

    text = format(ergebnis) if format else str(ergebnis)
    return ToolResult(ok=True, text=text, data=ergebnis)
