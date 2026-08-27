"""Ein Event-Loop in einem eigenen Thread, fuer den synchronen Zugang.

Der naheliegende Weg -- ``asyncio.run()`` pro Aufruf -- scheitert genau bei der
Zielgruppe, fuer die der synchrone Zugang gedacht ist: ein Jupyter-Notebook
betreibt bereits einen laufenden Event-Loop, und zwei laufende Loops in einem
Thread gibt es nicht. Ausserdem wuerde jeder Aufruf den Verbindungspool
wegwerfen.

Also ein eigener Loop in einem eigenen Thread. Aufrufe werden per
``run_coroutine_threadsafe`` hinuebergereicht und blockieren den aufrufenden
Thread, bis das Ergebnis da ist -- was synchroner Code ohnehin erwartet.
"""

from __future__ import annotations

import asyncio
import threading
from collections.abc import Coroutine
from typing import Any, TypeVar

__all__ = ["LoopThread"]

T = TypeVar("T")

_STOP_TIMEOUT = 5.0


class LoopThread:
    """Betreibt einen Event-Loop im Hintergrund, bis ``close()`` gerufen wird."""

    def __init__(self) -> None:
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(
            target=self._loop.run_forever,
            name="edusharing-loop",
            daemon=True,
        )
        self._thread.start()

    def run(self, coro: Coroutine[Any, Any, T]) -> T:
        """Fuehre ``coro`` im Hintergrund-Loop aus und warte auf das Ergebnis."""
        return asyncio.run_coroutine_threadsafe(coro, self._loop).result()

    def close(self) -> None:
        """Halte den Loop an und warte auf den Thread.

        Mehrfaches Aufrufen ist erlaubt -- ``close()`` steht typischerweise in
        einem ``finally`` und wird zusaetzlich vom Kontextmanager gerufen.
        """
        if self._loop.is_closed():
            return
        self._loop.call_soon_threadsafe(self._loop.stop)
        self._thread.join(timeout=_STOP_TIMEOUT)
        self._loop.close()
