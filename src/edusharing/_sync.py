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
from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from .nodes import Node

__all__ = ["LoopThread", "SyncTransport", "SyncNode", "SyncNodeContent"]

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


class SyncTransport:
    """Synchroner Durchgriff auf einen ``Transport``.

    Der Notausgang zu den Endpunkten ohne eigene Methode muss auch dem
    synchronen Zugang offenstehen -- sonst waere er eine Sackgasse, sobald
    etwas gebraucht wird, das die Bibliothek noch nicht abdeckt.

    Absichtlich schmal: nur ``request`` und ``json``. Alles Weitere gehoert an
    den asynchronen Transport, nicht hierher dupliziert.
    """

    def __init__(self, transport: Any, loop: LoopThread) -> None:
        self._transport = transport
        self._loop = loop

    def request(self, method: str, path: str, **kwargs: Any) -> Any:
        """Wie ``Transport.request``, blockierend."""
        return self._loop.run(self._transport.request(method, path, **kwargs))

    def json(self, method: str, path: str, **kwargs: Any) -> Any:
        """Wie ``Transport.json``, blockierend."""
        return self._loop.run(self._transport.json(method, path, **kwargs))

    def __repr__(self) -> str:
        return f"SyncTransport({self._transport!r})"


class SyncNode:
    """Ein Knoten fuer den synchronen Zugang.

    Reicht die Methoden von ``Node`` blockierend durch. Ausgeschrieben statt
    dynamisch erzeugt: die Namen sollen in der IDE auffindbar und die
    Signaturen lesbar bleiben.
    """

    def __init__(self, node: Node, loop: Any) -> None:
        self._node = node
        self._loop = loop

    # Lesende Zugriffe sind ohnehin synchron und werden durchgereicht.
    def __getattr__(self, name: str) -> Any:
        return getattr(self._node, name)

    @property
    def content(self) -> SyncNodeContent:
        """Der Binaerinhalt, blockierend."""
        return SyncNodeContent(self._node.content, self._loop)

    def update(self, **kwargs: Any) -> SyncNode:
        """Wie ``Node.update``, blockierend."""
        return SyncNode(self._loop.run(self._node.update(**kwargs)), self._loop)

    def set_property(self, prop: str, value: Any, **kwargs: Any) -> SyncNode:
        """Wie ``Node.set_property``, blockierend."""
        return SyncNode(
            self._loop.run(self._node.set_property(prop, value, **kwargs)), self._loop
        )

    def add_keywords(self, *keywords: str) -> SyncNode:
        """Wie ``Node.add_keywords``, blockierend."""
        return SyncNode(self._loop.run(self._node.add_keywords(*keywords)), self._loop)

    def remove_keywords(self, *keywords: str) -> SyncNode:
        """Wie ``Node.remove_keywords``, blockierend."""
        return SyncNode(self._loop.run(self._node.remove_keywords(*keywords)), self._loop)

    def delete(self, **kwargs: Any) -> None:
        """Wie ``Node.delete``, blockierend."""
        self._loop.run(self._node.delete(**kwargs))

    def __repr__(self) -> str:
        return f"SyncNode(id={self._node.id!r}, title={self._node.title!r})"


class SyncNodeContent:
    """Der Binaerinhalt eines Knotens fuer den synchronen Zugang.

    Ohne diese Schicht gaebe ``SyncNode.content`` ein Objekt mit asynchronen
    Methoden zurueck -- der Aufruf liefe ins Leere und meldete nichts.
    """

    def __init__(self, content: Any, loop: LoopThread) -> None:
        self._content = content
        self._loop = loop

    def __getattr__(self, name: str) -> Any:
        return getattr(self._content, name)

    def upload(self, data: bytes, **kwargs: Any) -> Any:
        """Wie ``NodeContent.upload``, blockierend."""
        return SyncNode(self._loop.run(self._content.upload(data, **kwargs)), self._loop)

    def download(self) -> bytes:
        """Wie ``NodeContent.download``, blockierend."""
        return self._loop.run(self._content.download())

    def text(self, **kwargs: Any) -> str:
        """Wie ``NodeContent.text``, blockierend."""
        return self._loop.run(self._content.text(**kwargs))

    def __repr__(self) -> str:
        return f"SyncNodeContent({self._content!r})"
