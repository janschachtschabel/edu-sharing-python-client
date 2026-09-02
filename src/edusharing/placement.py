"""Where a node sits -- and who has curated it.

Two questions that look alike and are not. **Parents** is where the node
physically lives: the folder it was created in, and that folder's folder.
**Collections** is who has picked it up: a collection holds a *reference*, and
the referenced node's own parent usually lives somewhere else entirely. A node
in ten collections still has exactly one parent chain.

Measured against staging on 2026-08-28 in a throwaway folder:

* ``GET .../parents`` returns the node **itself** as the first entry, then its
  ancestors, nearest first. Leaving it in makes every breadcrumb one step too
  long, with the node as its own ancestor.
* ``fullPath=true`` answers **403** for an ordinary account -- the complete path
  runs through areas it may not read. Without the parameter the answer reaches
  as far as the account is allowed and names that boundary in ``scope``.
* Without ``propertyFilter=-all-`` the ancestors come back with **empty**
  ``properties``: names yes, titles no. A path without titles is useless as a
  breadcrumb.
* ``GET /usage/v1/usages/node/{id}/collections`` answers with a **list**, not an
  object, and each entry carries a complete node under ``collection`` --
  properties, title and ``isPublic`` included. Nothing has to be read back.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from .urls import path_segment

if TYPE_CHECKING:  # pragma: no cover
    from .nodes import Node, Nodes

__all__ = ["Ancestry", "ancestry_of", "collections_of"]


@dataclass(frozen=True)
class Ancestry:
    """What the parents endpoint says about one node.

    Attributes:
        node: the node itself, as the endpoint reports it -- it is the first
            entry of the answer. ``None`` if the answer was empty.
        parents: its ancestors, nearest first.
        scope: how far the answer reaches, e.g. ``MY_FILES``. The path stops at
            the boundary of what the account may read, and this names it -- so
            a truncated path is not mistaken for a complete one.
    """

    node: Node | None
    parents: tuple[Node, ...]
    scope: str

    def __repr__(self) -> str:
        return f"Ancestry(parents={len(self.parents)}, scope={self.scope!r})"


def _nodes_of(repo: Any) -> Nodes:
    """Accept the connection or its ``nodes`` accessor.

    Every other free function takes the connection; these two took ``Nodes``
    and the reference documented ``repo`` -- so both are accepted, and the
    documented form is the one that works.
    """
    nodes: Nodes = getattr(repo, "nodes", repo)
    return nodes


async def ancestry_of(repo: Any, node_id: str) -> Ancestry:
    """Read the way up from a node.

    ``fullPath`` is deliberately not sent: measured, asking for the complete
    path answers 403 for an ordinary account, because it runs through areas the
    account may not read. What comes back reaches as far as the account is
    allowed, and ``Ancestry.scope`` says how far that was.

    Args:
        repo: the connection -- or its ``nodes`` accessor, which is also accepted.
        node_id: the node's id.

    Raises:
        PermissionDeniedError: when even the permitted part is refused. Not
            swallowed into an empty list -- "no way up" and "a refused way up"
            are different answers.
    """
    from .nodes import Node as _Node  # local: nodes imports this module

    nodes = _nodes_of(repo)
    response = await nodes.transport.json(
        "GET",
        f"/node/v1/nodes/-home-/{path_segment(node_id)}/parents",
        # Without this the ancestors arrive with an empty properties object --
        # names but no titles, and a breadcrumb needs the titles.
        params={"propertyFilter": "-all-"},
    )
    found = [_Node(data, nodes) for data in (response.get("nodes") or [])]
    itself = next((n for n in found if n.id == node_id), None)
    return Ancestry(
        node=itself,
        parents=tuple(n for n in found if n.id != node_id),
        scope=str(response.get("scope") or ""),
    )


async def collections_of(
    repo: Any, node_id: str, *, original_id: str | None = None
) -> list[Node]:
    """The collections holding a reference to this node.

    Not the parent chain: a collection references nodes whose own parent lives
    elsewhere, so this answers "who has curated it", not "where does it live".

    **The question always goes to the original.** A collection listing hands
    out the ids of *references*, and the usage endpoint knows only originals:
    measured on 2026-09-02 against staging, it answered ``200`` with an empty
    list for a listing id and named two collections for the original behind
    it. Asked with the listing id, this function used to report "in no
    collection" for material that sits in two. So the node is read first and
    its ``original_id`` is what gets asked -- unless the caller already holds
    the node and passes it, which saves that read.

    Each entry comes back as a full node -- measured, with properties, title
    and ``isPublic`` -- so nothing has to be read a second time.

    Args:
        repo: the connection -- or its ``nodes`` accessor, which is also accepted.
        node_id: the node's id -- an original's or a reference's.
        original_id: the id to ask for, when the caller has already resolved
            it (``node.original_id or node.id``). ``None`` reads the node.

    Raises:
        NotFoundError: when no node carries this id.
        PermissionDeniedError: when the node may not be read.
    """
    from .nodes import Node as _Node  # local: nodes imports this module

    nodes = _nodes_of(repo)
    if original_id is None:
        node = await nodes.get(node_id)
        original_id = node.original_id or node.id
    response: Any = await nodes.transport.json(
        "GET", f"/usage/v1/usages/node/{path_segment(original_id)}/collections"
    )
    # A list, not an object -- and a list of *usages*, so an entry without a
    # collection block would become a node without an id.
    return [
        _Node(usage["collection"], nodes)
        for usage in (response or [])
        if isinstance(usage, dict) and usage.get("collection")
    ]
