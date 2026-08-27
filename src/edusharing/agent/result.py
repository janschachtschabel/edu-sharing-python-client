"""Errors as results rather than exceptions.

A tool invoked by a language model must return something usable even when it
fails. A propagated exception ends the run instead -- and the model never learns
that merely a filter was unknown, or a node did not exist. Either would have
been actionable.

Only errors from **this library** are caught. A ``TypeError`` in your own code
is a defect; turning it into a friendly message hides it instead of fixing it.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

from ..errors import EduSharingError

__all__ = ["ToolResult", "as_result"]


@dataclass(frozen=True)
class ToolResult:
    """The outcome of a tool call -- successful or not.

    ``text`` is always populated: a tool needs something to emit in either case.
    """

    ok: bool
    text: str
    data: Any = None
    error: str | None = None
    #: The error's class name, e.g. ``"ValidationError"``. Lets a tool tell
    #: "rephrasing might help" from "credentials are missing" without parsing
    #: the message.
    error_type: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __bool__(self) -> bool:
        return self.ok


async def as_result(
    awaitable: Awaitable[Any],
    *,
    format: Callable[[Any], str] | None = None,
) -> ToolResult:
    """Run ``awaitable`` and wrap both success and failure.

    Args:
        awaitable: the work, e.g. ``repo.search("...")``.
        format: turns the result into text. Defaults to ``str()``.

    Returns:
        A ``ToolResult``. On an ``EduSharingError``, ``ok`` is false and
        ``error`` carries the message -- **without** the Java stack trace, since
        the text goes into a model context and possibly into a user interface.

    Raises:
        Anything that is not an ``EduSharingError``. Defects stay loud.
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
