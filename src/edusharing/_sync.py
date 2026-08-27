"""An event loop in a thread of its own, for the synchronous surface.

The obvious route -- ``asyncio.run()`` per call -- fails at exactly the audience
the synchronous surface exists for: a Jupyter notebook already runs an event
loop, and two running loops in one thread do not exist. It would also throw away
the connection pool on every call.

So: one loop in one thread. Calls are handed over via
``run_coroutine_threadsafe`` and block the calling thread until the result
arrives -- which synchronous code expects anyway.
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
    """Runs an event loop in the background until ``close()`` is called."""

    def __init__(self) -> None:
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(
            target=self._loop.run_forever,
            name="edusharing-loop",
            daemon=True,
        )
        self._thread.start()

    def run(self, coro: Coroutine[Any, Any, T]) -> T:
        """Run ``coro`` on the background loop and wait for the result."""
        return asyncio.run_coroutine_threadsafe(coro, self._loop).result()

    def close(self) -> None:
        """Stop the loop and join the thread.

        Calling it repeatedly is fine -- ``close()`` typically sits in a
        ``finally`` and is also called by the context manager.
        """
        if self._loop.is_closed():
            return
        self._loop.call_soon_threadsafe(self._loop.stop)
        self._thread.join(timeout=_STOP_TIMEOUT)
        self._loop.close()


class SyncTransport:
    """Synchronous pass-through to a ``Transport``.

    The escape hatch to endpoints without a method of their own must be open to
    the synchronous surface too -- otherwise it becomes a dead end the moment
    something is needed that the library does not cover yet.

    Deliberately narrow: only ``request`` and ``json``. Everything else belongs
    on the asynchronous transport, not duplicated here.
    """

    def __init__(self, transport: Any, loop: LoopThread) -> None:
        self._transport = transport
        self._loop = loop

    def request(self, method: str, path: str, **kwargs: Any) -> Any:
        """Like ``Transport.request``, blocking."""
        return self._loop.run(self._transport.request(method, path, **kwargs))

    def json(self, method: str, path: str, **kwargs: Any) -> Any:
        """Like ``Transport.json``, blocking."""
        return self._loop.run(self._transport.json(method, path, **kwargs))

    def __repr__(self) -> str:
        return f"SyncTransport({self._transport!r})"


class SyncNode:
    """A node for the synchronous surface.

    Passes ``Node``'s methods through, blocking. Written out rather than
    generated: the names should stay discoverable in an IDE and the signatures
    readable.
    """

    def __init__(self, node: Node, loop: Any) -> None:
        self._node = node
        self._loop = loop

    # Reading access is synchronous anyway and is passed straight through.
    def __getattr__(self, name: str) -> Any:
        return getattr(self._node, name)

    @property
    def content(self) -> SyncNodeContent:
        """The binary content, blocking."""
        return SyncNodeContent(self._node.content, self._loop)

    def update(self, **kwargs: Any) -> SyncNode:
        """Like ``Node.update``, blocking."""
        return SyncNode(self._loop.run(self._node.update(**kwargs)), self._loop)

    def set_property(self, prop: str, value: Any, **kwargs: Any) -> SyncNode:
        """Like ``Node.set_property``, blocking."""
        return SyncNode(
            self._loop.run(self._node.set_property(prop, value, **kwargs)), self._loop
        )

    def add_keywords(self, *keywords: str) -> SyncNode:
        """Like ``Node.add_keywords``, blocking."""
        return SyncNode(self._loop.run(self._node.add_keywords(*keywords)), self._loop)

    def remove_keywords(self, *keywords: str) -> SyncNode:
        """Like ``Node.remove_keywords``, blocking."""
        return SyncNode(self._loop.run(self._node.remove_keywords(*keywords)), self._loop)

    def delete(self, **kwargs: Any) -> None:
        """Like ``Node.delete``, blocking."""
        self._loop.run(self._node.delete(**kwargs))

    def __repr__(self) -> str:
        return f"SyncNode(id={self._node.id!r}, title={self._node.title!r})"


class SyncNodeContent:
    """A node's binary content for the synchronous surface.

    Without this layer ``SyncNode.content`` would hand back an object with
    asynchronous methods -- the call would go nowhere and report nothing.
    """

    def __init__(self, content: Any, loop: LoopThread) -> None:
        self._content = content
        self._loop = loop

    def __getattr__(self, name: str) -> Any:
        return getattr(self._content, name)

    def upload(self, data: bytes, **kwargs: Any) -> Any:
        """Like ``NodeContent.upload``, blocking."""
        return SyncNode(self._loop.run(self._content.upload(data, **kwargs)), self._loop)

    def download(self) -> bytes:
        """Like ``NodeContent.download``, blocking."""
        return self._loop.run(self._content.download())

    def text(self, **kwargs: Any) -> str:
        """Like ``NodeContent.text``, blocking."""
        return self._loop.run(self._content.text(**kwargs))

    def __repr__(self) -> str:
        return f"SyncNodeContent({self._content!r})"
