"""Reading flows that start from an id: what this node is.

What a flow is and why it exists is in the package docstring. These describe
the node itself -- its fields, where it sits, who has taken it up. What hangs
off it is in ``contents``.
"""

from __future__ import annotations

import asyncio
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from .. import placement as placement_api
from ..errors import EduSharingError
from ..results import SearchHit
from .serialize import hit_as_dict

if TYPE_CHECKING:  # pragma: no cover
    from ..nodes import Node
    from ..repository import AsyncRepository
__all__ = [
    "describe",
    "describe_many",
    "placement",
]


async def describe(repo: AsyncRepository, node_id: str) -> dict[str, Any]:
    """Everything about one node, as JSON.

    One request -- ``GET /node/v1/nodes/-home-/{id}/metadata`` -- exactly like
    ``repo.node(id)`` at the API level. This flow saves no round trip; what it
    does is hand back a ``dict`` with the vocabulary fields already resolved to
    labels and keyed by the configured short names, instead of a ``Node``
    object.

    Args:
        repo: the connection.
        node_id: the node's id.

    Returns:
        ``{id, title, url, description, source_url, mimetype, mediatype, fields,
        name, type, aspects, original_id, access, public, has_content, keywords,
        properties, duplicate_ids}``. ``original_id`` is the record behind a
        reference -- a listing id names one -- and ``None`` on an original.
        ``duplicate_ids`` is empty here -- the key comes from the shared hit
        shape, where a deduplicated search fills it.
        ``public`` says whether anyone may read the node -- inherited access
        included, and free, because the node response carries it.
        ``properties`` holds the raw edu-sharing properties for anything the
        short names do not cover.

    Raises:
        NotFoundError: when no node carries this id.
        PermissionDeniedError: when it exists but is not readable.
    """
    node = await repo.nodes.get(node_id)
    hit = SearchHit.from_node(node.raw, repo.url)
    data = hit_as_dict(hit, repo.searcher.field_aliases)
    data.update({
        "name": node.name,
        "type": node.type,
        "aspects": list(node.aspects),
        # A listing id names a reference; this is the record behind it, and
        # the id a write goes to. ``None`` on an original.
        "original_id": node.original_id,
        "access": list(node.access),
        "public": node.is_public,
        "has_content": node.content.has_content,
        "keywords": list(node.keywords),
        "properties": node.properties,
    })
    return data


async def placement(repo: AsyncRepository, node_id: str) -> dict[str, Any]:
    """Where a node sits and who has curated it, as JSON.

    Two requests, sent together: the way up, and the collections holding a
    reference. They answer different questions -- a node in ten collections
    still has one parent chain -- and asking both is the usual way to explain
    to a person, or to a model, what a hit actually is.

    Args:
        repo: the connection.
        node_id: the node's id.

    Returns:
        ``{id, original_id, title, path, collections, scope, failed}``.
        ``original_id`` is the record behind a reference and ``None`` on an
        original; the collections are always asked for that record, because a
        listing id is a reference and the usage endpoint knows only originals.

        ``path`` runs **top down**, ready to print as a breadcrumb -- unlike
        ``node.parents()``, which mirrors the endpoint and gives the nearest
        first. ``scope`` says how far the path reaches: it stops at the
        boundary of what the account may read, and saying so keeps a truncated
        path from passing as a complete one.

        **Read ``failed``.** The two halves are asked together and one may be
        refused on its own -- an anonymous read of a node inside a collection
        answers ``500 AccessDeniedException`` for the way up while the
        collections come back fine. ``path`` is then empty, and without
        ``failed`` that reads as "this node sits nowhere" instead of "you may
        not see where it sits". Each entry carries ``part`` and ``reason``.

    Raises:
        NotFoundError: when no node carries this id.
        PermissionDeniedError: when the way up is refused.
    """
    # One read first: a listing id is a reference, and the collections have to
    # be asked for the original behind it (see ``collections_of``). When the
    # node itself cannot be read, both halves are still asked with the id as
    # given -- that keeps the partial answer the docstring promises, and the
    # unresolved id is named in ``failed`` rather than passed off as resolved.
    failed: list[dict[str, str]] = []
    original_id: str | None = None
    try:
        node = await repo.nodes.get(node_id)
        original_id = node.original_id
    except EduSharingError as exc:
        failed.append({"part": "original",
                       "reason": f"{type(exc).__name__}: {exc}"})

    ancestry, collections = await asyncio.gather(
        placement_api.ancestry_of(repo, node_id),
        placement_api.collections_of(repo, node_id, original_id=original_id or node_id),
        return_exceptions=True,
    )
    if isinstance(ancestry, BaseException) and isinstance(collections, BaseException):
        # Nothing to report is not a partial result: an empty answer would
        # claim the node sits nowhere. ``collections.find`` draws the same line.
        raise ancestry

    if isinstance(ancestry, BaseException):
        failed.append({"part": "path",
                       "reason": f"{type(ancestry).__name__}: {ancestry}"})
        ancestry = placement_api.Ancestry(node=None, parents=(), scope="")
    if isinstance(collections, BaseException):
        failed.append({"part": "collections",
                       "reason": f"{type(collections).__name__}: {collections}"})
        collections = []

    return {
        "id": node_id,
        # ``None`` on an original; on a reference the record the collections
        # were asked for -- and the id a write would have to target.
        "original_id": original_id,
        # From the parents answer, where the node is the first entry -- so the
        # title costs no request of its own.
        "title": ancestry.node.title if ancestry.node else None,
        "path": [_step(n) for n in reversed(ancestry.parents)],
        "collections": [_step(n) for n in collections],
        "scope": ancestry.scope,
        "failed": failed,
    }


def _step(node: Node) -> dict[str, Any]:
    """One station of a path or one collection -- what a breadcrumb needs."""
    return {"id": node.id, "title": node.title or node.name, "type": node.type}


async def describe_many(
    repo: AsyncRepository, node_ids: Sequence[str]
) -> dict[str, Any]:
    """Describe several nodes at once, surviving the ones that are gone.

    Sent together, so the wall clock is one request rather than *n* -- the
    transport's own concurrency limit still applies.

    **A missing node is reported, not raised.** Measured on 2026-08-27, **4 of
    25** search hits were no longer retrievable: an index that outlives its
    nodes is the ordinary case here, and losing the whole list because one
    entry is gone makes a search result unusable.

    Args:
        repo: the connection.
        node_ids: the nodes to describe. Duplicates are fetched once.

    Returns:
        ``{requested, found, nodes, failed}``. ``nodes`` keeps the order of the
        request, so a caller can line the answer up with what it asked for.
        ``failed`` names each id and why.
    """
    wanted = list(dict.fromkeys(node_ids))
    if not wanted:
        return {"requested": 0, "found": 0, "nodes": [], "failed": []}

    async def one(node_id: str) -> tuple[str, dict[str, Any] | str]:
        try:
            return node_id, await describe(repo, node_id)
        except EduSharingError as exc:
            return node_id, f"{type(exc).__name__}: {exc}"

    results = await asyncio.gather(*(one(i) for i in wanted))
    nodes = [r for _, r in results if isinstance(r, dict)]
    failed = [
        {"id": node_id, "reason": reason}
        for node_id, reason in results
        if isinstance(reason, str)
    ]
    return {
        "requested": len(wanted),
        "found": len(nodes),
        "nodes": nodes,
        "failed": failed,
    }
