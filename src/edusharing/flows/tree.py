"""Walking the collection tree: browsing it, searching in it, counting it.

Three flows with one shared problem, and it is not a technical one.

**Collections form a directed graph, not a tree.** A sub-collection can hang
under several parents, and two collections can hang under each other.
Anything that does not de-duplicate by id walks in circles; anything that does
not cap its fan-out turns one call into a hundred.

**And a search cannot be scoped to a collection.** Measured three times -- by
wlo-mcp-sc on 2026-07-17, here on 2026-08-27 and again on 2026-08-28 --
``ngsearch`` with ``virtual:primaryparent_nodeid`` as a criterion answers HTTP
400. It would also be the wrong answer: a collection holds *references* to
nodes whose own parent lives somewhere else, so a parent-scoped search would
miss exactly the curated ones. So these flows walk and compare locally.

Every one of them says what it left out. Truncating in silence reads like
completeness, and a caller cannot tell an empty result from an unfinished one.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

from ..urls import path_segment
from .discover import collection_contents

if TYPE_CHECKING:  # pragma: no cover
    from ..repository import AsyncRepository

__all__ = [
    "DEFAULT_MAX_COLLECTIONS",
    "browse_tree",
    "collection_stats",
    "search_in_collection",
]

#: How many collections a walk may open before it stops and says so. Fifty
#: keeps an ordinary subject tree within reach while bounding a single call to
#: a size a caller can predict.
DEFAULT_MAX_COLLECTIONS = 50

#: How many children ``collection_stats`` tallies. The counts themselves come
#: from the pagination totals and are exact either way.
DEFAULT_SAMPLE = 100


async def browse_tree(
    repo: AsyncRepository,
    collection_id: str,
    *,
    depth: int = 2,
    max_collections: int = DEFAULT_MAX_COLLECTIONS,
) -> dict[str, Any]:
    """The collections underneath one collection, nested.

    Only the collections. Their material is a different question and a second
    request per node -- ``collection_stats`` counts it, ``collection_contents``
    lists it. Keeping them apart halves what a walk costs.

    The walk is depth-first and **sequential**: one request at a time, up to
    ``max_collections``. Fanning a level out in parallel would be faster and
    would put the de-duplication set into a race, and the cap already bounds
    the wait. If that becomes the bottleneck, the place to fix it is here.

    Args:
        repo: the connection.
        collection_id: where to start.
        depth: how many levels to descend. ``1`` is the direct children.
        max_collections: how many collections may be opened altogether.

    Returns:
        ``{id, collections, opened, truncated}``, nested. ``opened`` is how
        many were actually read, ``truncated`` whether the cap or a cycle cut
        the walk short.

    Raises:
        NotFoundError: when no collection carries this id.
    """
    seen: set[str] = {collection_id}
    state = {"opened": 0, "truncated": False}

    async def walk(node_id: str, left: int) -> list[dict[str, Any]]:
        if left <= 0:
            return []
        if state["opened"] >= max_collections:
            state["truncated"] = True
            return []
        state["opened"] += 1

        response = await repo.raw.json(
            "GET",
            f"/collection/v1/collections/-home-/{path_segment(node_id)}"
            "/children/collections",
            params={"maxItems": max_collections},
        )
        children = []
        for data in response.get("collections") or []:
            child_id = (data.get("ref") or {}).get("id") or ""
            if not child_id or child_id in seen:
                # A graph, not a tree: the same collection can be reached
                # twice, and following it again would either repeat work or
                # never end.
                continue
            seen.add(child_id)
            children.append({
                "id": child_id,
                "title": data.get("title") or data.get("name") or "",
                "collections": await walk(child_id, left - 1),
            })
        return children

    tree = await walk(collection_id, depth)
    return {
        "id": collection_id,
        "collections": tree,
        "opened": state["opened"],
        "truncated": state["truncated"],
    }


async def search_in_collection(
    repo: AsyncRepository,
    collection_id: str,
    query: str,
    *,
    depth: int = 2,
    max_collections: int = DEFAULT_MAX_COLLECTIONS,
    limit: int = 50,
) -> dict[str, Any]:
    """Find material inside one collection and the ones below it.

    Walks and compares locally, because the repository offers no way to scope a
    search to a collection -- see the module docstring for the measurement.

    **Compared are title, description and the resolved field labels** (subject,
    level, type), case-insensitively. Not the keywords: the serialised hit does
    not carry them, and adding them would change the shape every other flow
    returns. For full text across the whole repository, ``flows.search`` is the
    better tool -- this one answers "what in *this* collection is about X".

    Args:
        repo: the connection.
        collection_id: where to look.
        query: what to look for. Required -- without it this is
            ``collection_contents``.
        depth: how many levels to descend.
        max_collections: how many collections may be opened altogether.
        limit: how much material to read per collection.

    Returns:
        ``{query, hits, searched, truncated}``. **Read ``truncated``**: an
        empty result from a walk that stopped early is not "there is none".

    Raises:
        ValueError: on an empty query.
        NotFoundError: when no collection carries this id.
    """
    if not query or not query.strip():
        raise ValueError(
            "search_in_collection() needs a query -- without one it would be "
            "collection_contents(), which is a different flow."
        )
    needle = query.strip().lower()

    tree = await browse_tree(
        repo, collection_id, depth=depth, max_collections=max_collections
    )
    # The walk lists children it did not open -- they come free with their
    # parent's answer. Reading material from all of them would cost two
    # requests each and blow past the cap the caller set, so the same cap
    # applies here.
    found = [collection_id, *_ids_of(tree["collections"])]
    ids = found[:max_collections]

    pages = await asyncio.gather(
        *(collection_contents(repo, i, limit=limit) for i in ids)
    )
    hits = [
        hit
        for page in pages
        for hit in page["materials"]
        if _matches(hit, needle)
    ]
    return {
        "query": query,
        "hits": hits,
        "searched": len(ids),
        "truncated": tree["truncated"] or len(found) > len(ids),
    }


async def collection_stats(
    repo: AsyncRepository, collection_id: str, *, sample: int = DEFAULT_SAMPLE
) -> dict[str, Any]:
    """How much a collection holds, and what of.

    The counts are exact: they come from the pagination totals. The breakdown
    is tallied over the material actually read, up to ``sample`` -- which is
    why ``sampled`` and ``complete`` are in the answer. A breakdown over a
    hundred of five hundred records is useful; mistaking it for the whole is
    not.

    Not from a facet query: a collection curates *references* to nodes whose
    primary parent lives elsewhere, so a facet scoped by parent returns nothing
    for them. The children endpoint returns the referenced files with their
    ``*_DISPLAYNAME`` labels, so a local tally is both correct and readable.

    Args:
        repo: the connection.
        collection_id: the collection to profile.
        sample: how much material to tally.

    Returns:
        ``{id, materials, collections, sampled, complete, by}``. ``by`` holds
        one counter per short name the search knows.

        **The counters do not partition the sample.** A field is multi-valued:
        measured live, 15 materials carried 25 level assignments between them.
        Each counter says how many records mention a value, not what share of
        them it is.

    Raises:
        NotFoundError: when no collection carries this id.
    """
    page = await collection_contents(repo, collection_id, limit=sample)
    materials = page["materials"]

    by: dict[str, dict[str, int]] = {}
    for hit in materials:
        for field, values in (hit.get("fields") or {}).items():
            counter = by.setdefault(field, {})
            for value in values:
                counter[value] = counter.get(value, 0) + 1

    total = int(page.get("total_materials") or 0)
    return {
        "id": collection_id,
        "materials": total,
        "collections": len(page.get("collections") or []),
        "sampled": len(materials),
        "complete": len(materials) >= total,
        "by": by,
    }


# --- Internals ------------------------------------------------------------


def _ids_of(collections: list[dict[str, Any]]) -> list[str]:
    """Every id in a nested tree, flattened."""
    found: list[str] = []
    for entry in collections:
        found.append(entry["id"])
        found.extend(_ids_of(entry["collections"]))
    return found


def _matches(hit: dict[str, Any], needle: str) -> bool:
    """Whether a serialised hit mentions the term.

    Title, description and the resolved field labels -- what a serialised hit
    actually carries. Searching "Biologie" in a collection therefore also finds
    material whose subject says so, which is usually what was meant.
    """
    haystack = [hit.get("title") or "", hit.get("description") or ""]
    for labels in (hit.get("fields") or {}).values():
        haystack.extend(labels)
    return any(needle in str(part).lower() for part in haystack)
