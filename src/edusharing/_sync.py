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
           "SyncChildObjects", "SyncFlows", "SyncRelations", "SyncNodePage",
           "SyncNodePermissions", "SyncSuggestions", "SyncWorkflow", "SyncComments",
           "SyncSkills", "SyncPeople"]

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

    @property
    def page(self) -> SyncNodePage:
        """The curated page this node renders, blocking."""
        return SyncNodePage(self._node.page, self._loop)

    @property
    def comments(self) -> SyncComments:
        """What people wrote about this node, blocking."""
        return SyncComments(self._node.comments, self._loop)

    @property
    def suggestions(self) -> SyncSuggestions:
        """Metadata proposed for this node, blocking."""
        return SyncSuggestions(self._node.suggestions, self._loop)

    @property
    def workflow(self) -> SyncWorkflow:
        """The editorial history, blocking."""
        return SyncWorkflow(self._node.workflow, self._loop)

    def rate(self, value: float, text: str = "") -> Any:
        """Like ``Node.rate``, blocking."""
        return self._loop.run(self._node.rate(value, text))

    def unrate(self) -> Any:
        """Like ``Node.unrate``, blocking."""
        return self._loop.run(self._node.unrate())

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


class SyncNodePage:
    """A node's curated page for the synchronous surface.

    ``render`` is the reason this wrapper exists rather than handing the
    accessor through: an un-awaited coroutine there changes what every visitor
    of a public page sees -- or rather, does not change it, silently.
    """

    def __init__(self, page: Any, loop: LoopThread) -> None:
        self._page = page
        self._loop = loop

    def get(self) -> Any:
        """Like ``NodePage.get``, blocking. The page it returns is inert."""
        return self._loop.run(self._page.get())

    def render(self, variant_id: str) -> Any:
        """Like ``NodePage.render``, blocking."""
        return self._loop.run(self._page.render(variant_id))

    def __repr__(self) -> str:
        return f"SyncNodePage({self._page!r})"


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
        return bool(self._loop.run(
            self._permissions.grant(authority, *permissions, **kwargs)))

    def revoke(self, authority: str, *permissions: str) -> bool:
        """Like ``NodePermissions.revoke``, blocking."""
        return bool(self._loop.run(self._permissions.revoke(authority, *permissions)))

    def publish(self) -> bool:
        """Like ``NodePermissions.publish``, blocking."""
        return bool(self._loop.run(self._permissions.publish()))

    def unpublish(self) -> bool:
        """Like ``NodePermissions.unpublish``, blocking."""
        return bool(self._loop.run(self._permissions.unpublish()))

    def __repr__(self) -> str:
        return f"Sync{self._permissions!r}"


class SyncSuggestions:
    """A node's proposals for the synchronous surface."""

    def __init__(self, suggestions: Any, loop: LoopThread) -> None:
        self._suggestions = suggestions
        self._loop = loop

    def list(self) -> list[Any]:
        """Like ``Suggestions.list``, blocking."""
        return self._loop.run(self._suggestions.list())

    def propose(self, property: str, value: str, reason: str, **kwargs: Any) -> Any:
        """Like ``Suggestions.propose``, blocking."""
        return self._loop.run(
            self._suggestions.propose(property, value, reason, **kwargs))

    def decide(self, ids: Any, **kwargs: Any) -> None:
        """Like ``Suggestions.decide``, blocking. Writes nothing to the node."""
        self._loop.run(self._suggestions.decide(ids, **kwargs))

    def __repr__(self) -> str:
        return f"Sync{self._suggestions!r}"


class SyncWorkflow:
    """A node's editorial history for the synchronous surface."""

    def __init__(self, workflow: Any, loop: LoopThread) -> None:
        self._workflow = workflow
        self._loop = loop

    def history(self) -> list[Any]:
        """Like ``Workflow.history``, blocking."""
        return self._loop.run(self._workflow.history())

    def submit(self, receiver: Any, status: str, comment: str = "") -> Any:
        """Like ``Workflow.submit``, blocking."""
        return self._loop.run(self._workflow.submit(receiver, status, comment))

    def __repr__(self) -> str:
        return f"Sync{self._workflow!r}"


class SyncComments:
    """A node's comments for the synchronous surface.

    Here for the same reason as ``SyncNodeContent``: without it the methods
    would hand back coroutines that do nothing and report nothing.
    """

    def __init__(self, comments: Any, loop: LoopThread) -> None:
        self._comments = comments
        self._loop = loop

    def list(self) -> list[Any]:
        """Like ``Comments.list``, blocking."""
        return self._loop.run(self._comments.list())

    def add(self, text: str, **kwargs: Any) -> Any:
        """Like ``Comments.add``, blocking."""
        return self._loop.run(self._comments.add(text, **kwargs))

    def edit(self, comment_id: str, text: str) -> Any:
        """Like ``Comments.edit``, blocking."""
        return self._loop.run(self._comments.edit(comment_id, text))

    def delete(self, comment_id: str) -> None:
        """Like ``Comments.delete``, blocking."""
        self._loop.run(self._comments.delete(comment_id))

    def __repr__(self) -> str:
        return f"Sync{self._comments!r}"


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
        return bytes(self._loop.run(self._content.download()))

    def text(self, **kwargs: Any) -> str:
        """Like ``NodeContent.text``, blocking."""
        return str(self._loop.run(self._content.text(**kwargs)))

    def set_preview(self, data: bytes, mimetype: str = "image/png") -> Any:
        """Like ``NodeContent.set_preview``, blocking."""
        return SyncNode(
            self._loop.run(self._content.set_preview(data, mimetype)), self._loop)

    def delete_preview(self) -> Any:
        """Like ``NodeContent.delete_preview``, blocking."""
        return SyncNode(self._loop.run(self._content.delete_preview()), self._loop)

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

    def text(self, node_id: str, **kwargs: Any) -> dict[str, Any]:
        """Like ``Flows.text``, blocking."""
        return self._loop.run(self._flows.text(node_id, **kwargs))

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

    def find_collections(self, text: str = "", **kwargs: Any) -> dict[str, Any]:
        """Like ``Flows.find_collections``, blocking."""
        return self._loop.run(self._flows.find_collections(text, **kwargs))

    def collection_contents(self, collection_id: str, **kwargs: Any) -> dict[str, Any]:
        """Like ``Flows.collection_contents``, blocking."""
        return self._loop.run(self._flows.collection_contents(collection_id, **kwargs))

    def placement(self, node_id: str) -> dict[str, Any]:
        """Like ``Flows.placement``, blocking."""
        return self._loop.run(self._flows.placement(node_id))

    def describe_many(self, node_ids: Any) -> dict[str, Any]:
        """Like ``Flows.describe_many``, blocking."""
        return self._loop.run(self._flows.describe_many(node_ids))

    def related(self, node_id: str, **kwargs: Any) -> dict[str, Any]:
        """Like ``Flows.related``, blocking."""
        return self._loop.run(self._flows.related(node_id, **kwargs))

    def page(self, collection_id: str, **kwargs: Any) -> dict[str, Any]:
        """Like ``Flows.page``, blocking."""
        return self._loop.run(self._flows.page(collection_id, **kwargs))

    def find_pages(self, text: str = "", **kwargs: Any) -> dict[str, Any]:
        """Like ``Flows.find_pages``, blocking."""
        return self._loop.run(self._flows.find_pages(text, **kwargs))

    def browse_tree(self, collection_id: str, **kwargs: Any) -> dict[str, Any]:
        """Like ``Flows.browse_tree``, blocking."""
        return self._loop.run(self._flows.browse_tree(collection_id, **kwargs))

    def search_in_collection(
        self, collection_id: str, query: str, **kwargs: Any
    ) -> dict[str, Any]:
        """Like ``Flows.search_in_collection``, blocking."""
        return self._loop.run(
            self._flows.search_in_collection(collection_id, query, **kwargs))

    def collection_stats(self, collection_id: str, **kwargs: Any) -> dict[str, Any]:
        """Like ``Flows.collection_stats``, blocking."""
        return self._loop.run(
            self._flows.collection_stats(collection_id, **kwargs))

    def update_material(self, node_id: str, **kwargs: Any) -> dict[str, Any]:
        """Like ``Flows.update_material``, blocking."""
        return self._loop.run(self._flows.update_material(node_id, **kwargs))

    def add_material(self, title: str, **kwargs: Any) -> dict[str, Any]:
        """Like ``Flows.add_material``, blocking."""
        return self._loop.run(self._flows.add_material(title, **kwargs))

    def accept_suggestion(self, node_id: str, suggestion_id: str) -> dict[str, Any]:
        """Like ``Flows.accept_suggestion``, blocking."""
        return self._loop.run(self._flows.accept_suggestion(node_id, suggestion_id))

    def find_skills(self, text: str = "", **kwargs: Any) -> dict[str, Any]:
        """Like ``Flows.find_skills``, blocking."""
        return self._loop.run(self._flows.find_skills(text, **kwargs))

    def skill(self, node_id: str, **kwargs: Any) -> dict[str, Any]:
        """Like ``Flows.skill``, blocking."""
        return self._loop.run(self._flows.skill(node_id, **kwargs))

    def skill_registry(self, collection_id: str, **kwargs: Any) -> dict[str, Any]:
        """Like ``Flows.skill_registry``, blocking."""
        return self._loop.run(self._flows.skill_registry(collection_id, **kwargs))

    def pick_skill(self, text: str, **kwargs: Any) -> dict[str, Any]:
        """Like ``Flows.pick_skill``, blocking."""
        return self._loop.run(self._flows.pick_skill(text, **kwargs))

    def build_collection(self, title: str, **kwargs: Any) -> dict[str, Any]:
        """Like ``Flows.build_collection``, blocking."""
        return self._loop.run(self._flows.build_collection(title, **kwargs))

    def delete(self, node_id: str, **kwargs: Any) -> dict[str, Any]:
        """Like ``Flows.delete``, blocking."""
        return self._loop.run(self._flows.delete(node_id, **kwargs))

    def __repr__(self) -> str:
        return f"SyncFlows({self._flows!r})"


class SyncSkills:
    """Synchronous pass-through to ``Skills``."""

    def __init__(self, skills: Any, loop: LoopThread) -> None:
        self._skills = skills
        self._loop = loop

    def search(self, text: str = "", **kwargs: Any) -> Any:
        """Like ``Skills.search``, blocking."""
        return self._loop.run(self._skills.search(text, **kwargs))

    def get(self, node_id: str, **kwargs: Any) -> Any:
        """Like ``Skills.get``, blocking."""
        return self._loop.run(self._skills.get(node_id, **kwargs))

    def registry(self, collection_id: str, **kwargs: Any) -> Any:
        """Like ``Skills.registry``, blocking."""
        return self._loop.run(self._skills.registry(collection_id, **kwargs))

    def pick(self, text: str, **kwargs: Any) -> Any:
        """Like ``Skills.pick``, blocking."""
        return self._loop.run(self._skills.pick(text, **kwargs))


class SyncPeople:
    """Groups and memberships for the synchronous surface."""

    def __init__(self, people: Any, loop: LoopThread) -> None:
        self._people = people
        self._loop = loop

    def memberships(self) -> list[Any]:
        """Like ``People.memberships``, blocking."""
        return self._loop.run(self._people.memberships())

    def group(self, name: str) -> Any:
        """Like ``People.group``, blocking."""
        return self._loop.run(self._people.group(name))

    def members(self, group: str, **kwargs: Any) -> list[Any]:
        """Like ``People.members``, blocking."""
        return self._loop.run(self._people.members(group, **kwargs))

    def create_group(self, name: str, **kwargs: Any) -> Any:
        """Like ``People.create_group``, blocking. Not verified live."""
        return self._loop.run(self._people.create_group(name, **kwargs))

    def delete_group(self, name: str) -> None:
        """Like ``People.delete_group``, blocking. Not verified live."""
        self._loop.run(self._people.delete_group(name))

    def add_member(self, group: str, authority: str) -> None:
        """Like ``People.add_member``, blocking. Not verified live."""
        self._loop.run(self._people.add_member(group, authority))

    def remove_member(self, group: str, authority: str) -> None:
        """Like ``People.remove_member``, blocking. Not verified live."""
        self._loop.run(self._people.remove_member(group, authority))

    def __repr__(self) -> str:
        return f"Sync{self._people!r}"


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
