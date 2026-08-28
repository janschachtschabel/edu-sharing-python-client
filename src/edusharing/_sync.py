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

__all__ = ["LoopThread", "SyncTransport", "SyncNode", "SyncNodeContent",
           "SyncChildObjects", "SyncFlows", "SyncRelations"]

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
    def children(self) -> SyncChildObjects:
        """Further documents belonging to this one. Its methods block."""
        return SyncChildObjects(self._node.children, self._loop)

    @property
    def content(self) -> SyncNodeContent:
        """The binary content, blocking."""
        return SyncNodeContent(self._node.content, self._loop)

    @property
    def permissions(self) -> SyncNodePermissions:
        """Who may do what with this node, blocking."""
        return SyncNodePermissions(self._node.permissions, self._loop)

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

    def parents(self) -> list[SyncNode]:
        """Like ``Node.parents``, blocking."""
        return [SyncNode(n, self._loop) for n in self._loop.run(self._node.parents())]

    def collections(self) -> list[SyncNode]:
        """Like ``Node.collections``, blocking."""
        return [SyncNode(n, self._loop)
                for n in self._loop.run(self._node.collections())]

    def delete(self, **kwargs: Any) -> None:
        """Like ``Node.delete``, blocking."""
        self._loop.run(self._node.delete(**kwargs))

    def __repr__(self) -> str:
        return f"SyncNode(id={self._node.id!r}, title={self._node.title!r})"


class SyncNodePermissions:
    """A node's permissions for the synchronous surface.

    Here for the same reason as ``SyncNodeContent``: without it
    ``SyncNode.permissions`` would hand back an object whose methods return
    coroutines. A forgotten ``await`` on ``publish()`` does nothing, reports
    nothing, and leaves material every caller believes to be public.
    """

    def __init__(self, permissions: Any, loop: LoopThread) -> None:
        self._permissions = permissions
        self._loop = loop

    def get(self) -> Any:
        """Like ``NodePermissions.get``, blocking."""
        return self._loop.run(self._permissions.get())

    def grant(self, authority: str, *permissions: str, **kwargs: Any) -> bool:
        """Like ``NodePermissions.grant``, blocking."""
        return self._loop.run(
            self._permissions.grant(authority, *permissions, **kwargs))

    def revoke(self, authority: str, *permissions: str) -> bool:
        """Like ``NodePermissions.revoke``, blocking."""
        return self._loop.run(self._permissions.revoke(authority, *permissions))

    def publish(self) -> bool:
        """Like ``NodePermissions.publish``, blocking."""
        return self._loop.run(self._permissions.publish())

    def unpublish(self) -> bool:
        """Like ``NodePermissions.unpublish``, blocking."""
        return self._loop.run(self._permissions.unpublish())

    def __repr__(self) -> str:
        return f"Sync{self._permissions!r}"


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


class SyncFlows:
    """Synchronous pass-through to ``Flows``.

    Exists because the asynchronous surface grew and the synchronous one did not
    -- twice, and both times the call silently returned a coroutine instead of a
    result (see test_sync_surface.py). Flows are exactly the layer a notebook
    reaches for first, so the pass-through is not optional.
    """

    def __init__(self, flows: Any, loop: LoopThread) -> None:
        self._flows = flows
        self._loop = loop

    def search(self, text: str | None = None, **kwargs: Any) -> dict[str, Any]:
        """Like ``Flows.search``, blocking."""
        return self._loop.run(self._flows.search(text, **kwargs))

    def search_all(self, text: str, **kwargs: Any) -> dict[str, Any]:
        """Like ``Flows.search_all``, blocking."""
        return self._loop.run(self._flows.search_all(text, **kwargs))

    def vocabulary(self, field: str, **kwargs: Any) -> dict[str, Any]:
        """Like ``Flows.vocabulary``, blocking."""
        return self._loop.run(self._flows.vocabulary(field, **kwargs))

    def describe(self, node_id: str) -> dict[str, Any]:
        """Like ``Flows.describe``, blocking."""
        return self._loop.run(self._flows.describe(node_id))

    def child_objects(self, node_id: str) -> dict[str, Any]:
        """Like ``Flows.child_objects``, blocking."""
        return self._loop.run(self._flows.child_objects(node_id))

    def relations(self, node_id: str) -> dict[str, Any]:
        """Like ``Flows.relations``, blocking."""
        return self._loop.run(self._flows.relations(node_id))

    def find_collections(self, text: str, **kwargs: Any) -> dict[str, Any]:
        """Like ``Flows.find_collections``, blocking."""
        return self._loop.run(self._flows.find_collections(text, **kwargs))

    def collection_contents(self, collection_id: str, **kwargs: Any) -> dict[str, Any]:
        """Like ``Flows.collection_contents``, blocking."""
        return self._loop.run(self._flows.collection_contents(collection_id, **kwargs))

    def placement(self, node_id: str) -> dict[str, Any]:
        """Like ``Flows.placement``, blocking."""
        return self._loop.run(self._flows.placement(node_id))

    def update_material(self, node_id: str, **kwargs: Any) -> dict[str, Any]:
        """Like ``Flows.update_material``, blocking."""
        return self._loop.run(self._flows.update_material(node_id, **kwargs))

    def add_material(self, title: str, **kwargs: Any) -> dict[str, Any]:
        """Like ``Flows.add_material``, blocking."""
        return self._loop.run(self._flows.add_material(title, **kwargs))

    def build_collection(self, title: str, **kwargs: Any) -> dict[str, Any]:
        """Like ``Flows.build_collection``, blocking."""
        return self._loop.run(self._flows.build_collection(title, **kwargs))

    def delete(self, node_id: str, **kwargs: Any) -> dict[str, Any]:
        """Like ``Flows.delete``, blocking."""
        return self._loop.run(self._flows.delete(node_id, **kwargs))

    def __repr__(self) -> str:
        return f"SyncFlows({self._flows!r})"


class SyncRelations:
    """Synchronous pass-through to ``Relations``."""

    def __init__(self, relations: Any, loop: LoopThread) -> None:
        self._relations = relations
        self._loop = loop

    def of(self, node_id: str) -> Any:
        """Like ``Relations.of``, blocking."""
        return self._loop.run(self._relations.of(node_id))

    def create(self, from_node: str, relation_type: str, to_node: str,
               **kwargs: Any) -> None:
        """Like ``Relations.create``, blocking."""
        self._loop.run(
            self._relations.create(from_node, relation_type, to_node, **kwargs))

    def delete(self, from_node: str, relation_type: str, to_node: str) -> None:
        """Like ``Relations.delete``, blocking."""
        self._loop.run(self._relations.delete(from_node, relation_type, to_node))

    def approve(self, from_node: str, relation_type: str, to_node: str) -> None:
        """Like ``Relations.approve``, blocking."""
        self._loop.run(self._relations.approve(from_node, relation_type, to_node))

    def __repr__(self) -> str:
        return f"SyncRelations({self._relations!r})"


class SyncChildObjects:
    """Synchronous pass-through to ``ChildObjects``."""

    def __init__(self, children: Any, loop: LoopThread) -> None:
        self._children = children
        self._loop = loop

    def list(self) -> Any:
        """Like ``ChildObjects.list``, blocking."""
        return [SyncNode(child, self._loop)
                for child in self._loop.run(self._children.list())]

    def add(self, data: bytes, **kwargs: Any) -> Any:
        """Like ``ChildObjects.add``, blocking."""
        return SyncNode(self._loop.run(self._children.add(data, **kwargs)), self._loop)

    def __repr__(self) -> str:
        return f"SyncChildObjects({self._children!r})"
