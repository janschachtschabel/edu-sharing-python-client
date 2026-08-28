"""Reading flows: one call where the API-level route needs several.

The API level is deliberately close to edu-sharing -- ``search`` returns a
``SearchResult``, ``node`` returns a ``Node``. That is right for anyone writing
Python against it, and wrong for anything that has to hand the outcome onwards
as data: an MCP tool, an HTTP endpoint, a language model.

These flows do the same work and return plain JSON structures. Nothing here
adds capability; it removes steps.
"""

from __future__ import annotations

import asyncio
from dataclasses import replace
from typing import TYPE_CHECKING, Any

from ..childobjects import ORDER_PROPERTY
from ..errors import ValidationError
from ..results import SearchHit
from ..urls import path_segment
from . import dedupe
from .language import GERMAN, LanguageProfile
from .rerank import DEFAULT_POOL, search_reranked
from .serialize import hit_as_dict, result_as_dict

if TYPE_CHECKING:  # pragma: no cover
    from ..nodes import Node
    from ..repository import AsyncRepository

__all__ = [
    "child_objects",
    "collection_contents",
    "describe",
    "field_property",
    "find_collections",
    "relations",
    "search",
    "vocabulary",
]


def field_property(repo: AsyncRepository, field: str) -> str:
    """A short name or a property -- both are allowed as input.

    A property is recognised by its namespace colon. Anything else must be a
    configured short name, and an unknown one is an error rather than a silent
    fallback: searching without the intended constraint and presenting the
    result anyway is the worse outcome.
    """
    if ":" in field:
        return field
    aliases = repo.searcher.field_aliases
    prop = aliases.get(field)
    if prop is None:
        known = ", ".join(sorted(aliases)) or "(none)"
        raise ValidationError(
            f"Unknown field {field!r}. Known are: {known}. "
            "A property can also be given directly, e.g. 'ccm:taxonid'."
        )
    return prop


async def search(
    repo: AsyncRepository,
    text: str | None = None,
    *,
    filters: dict[str, str | list[str]] | None = None,
    facets: list[str] | None = None,
    limit: int = 10,
    offset: int = 0,
    rerank: bool = False,
    pool: int = DEFAULT_POOL,
    language: LanguageProfile = GERMAN,
    deduplicate: bool = True,
    **aliases: str | list[str],
) -> dict[str, Any]:
    """Search for material and return the outcome as JSON.

    Vocabularies are resolved against this instance's own metadata set, so
    ``subject="Biologie"`` works without anyone having to know the URI behind it.

    Args:
        repo: the connection.
        text: full-text term. Omittable when only filtering.
        filters: ``{property: value}`` for properties without a short name.
        facets: short names or properties to count server-side.
        limit, offset: page size and starting point.
        rerank: ask several query variants and reorder by relevance instead of
            taking the repository's own order. Costs one request per variant
            (at most 5) and ignores ``offset``. Off by default -- see
            ``rerank.search_reranked`` for what it buys.
        pool: candidates fetched per variant when reranking. Only read when
            ``rerank`` is on.
        language: word lists for reranking. German by default; supply your own
            ``LanguageProfile`` for an instance in another language.
        deduplicate: fold hits sharing a source address into one. On by
            default -- the repository holds a separate node per import of the
            same page, and two entries read as two pieces of material. The kept
            hit names the folded ones in ``duplicate_ids``; switch this off for
            the raw view.
        **aliases: configured short names, e.g. ``subject="Biologie"``.

    Returns:
        ``{query, total, total_is_lower_bound, returned, hits, facets,
        unresolved, ignored, warnings, suggestions}``.

        **Check ``unresolved``.** A non-empty list means a filter could not be
        resolved and was therefore not sent -- the result is broader than
        requested and looks complete regardless.

    Raises:
        ValidationError: for an unknown short name.
        EduSharingError: for anything the repository refuses.
    """
    facet_properties = [field_property(repo, f) for f in (facets or [])]
    query: dict[str, Any] = {
        "text": text,
        "filters": {**(filters or {}), **aliases},
        "metadataset": repo.metadataset,
        "limit": limit,
        "offset": offset,
    }

    # Reranking needs something to rank against. A pure filter query has no
    # text, so there is nothing to expand and nothing to score.
    if rerank and text and text.strip():
        result, variants = await search_reranked(
            repo, text,
            filters=filters, facets=facet_properties or None,
            limit=limit, pool=pool, language=language, **aliases,
        )
        query["reranked"] = True
        query["variants"] = variants
        # Paging and reranking do not combine: the pool is merged across
        # variants, so an offset into it would not mean what a caller expects.
        query.pop("offset")
    else:
        result = await repo.searcher.search(
            text,
            filters=filters,
            facets=facet_properties or None,
            limit=limit,
            offset=offset,
            **aliases,
        )

    folded: dict[str, list[str]] = {}
    if deduplicate:
        # After ranking, not before: the order decides which of a group is kept,
        # and under rerank that is the best-scored one.
        kept, folded = dedupe.deduplicate(result.hits)
        result = replace(result, hits=kept)

    return result_as_dict(
        result, query=query, aliases=repo.searcher.field_aliases, folded=folded)


async def vocabulary(
    repo: AsyncRepository, field: str, *, locale: str | None = None
) -> dict[str, Any]:
    """The values a field accepts, as this instance defines them.

    Exists so that nothing has to guess. A language model asked to filter by
    subject will otherwise invent a plausible value, and the search silently
    returns everything.

    Args:
        repo: the connection.
        field: short name (``subject``) or property (``ccm:taxonid``).
        locale: language of the labels; the instance's default when omitted.

    Returns:
        ``{field, property, values, count}`` -- ``values`` are the readable
        labels, in the order the repository returns them.

    Raises:
        ValidationError: for an unknown short name.
    """
    prop = field_property(repo, field)
    values = await repo.vocab.values(prop, locale=locale)
    return {
        "field": field,
        "property": prop,
        "values": [v.label for v in values],
        "count": len(values),
    }


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
        name, type, access, has_content, keywords, properties}``.
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
        "access": list(node.access),
        "has_content": node.content.has_content,
        "keywords": list(node.keywords),
        "properties": node.properties,
    })
    return data


async def find_collections(
    repo: AsyncRepository, text: str, *, limit: int = 10
) -> dict[str, Any]:
    """Search collections and return the outcome as JSON.

    Collections are how edu-sharing groups material for teaching, so finding
    them is a different question from finding single resources -- and it uses a
    different endpoint.

    Args:
        repo: the connection.
        text: what to search for.
        limit: how many to return.

    Returns:
        The same shape as ``search``. ``total_is_lower_bound`` is **true**: the
        collection search asks two routes and merges them, so the figure counts
        at least this many, possibly more.

    Raises:
        EduSharingError: for anything the repository refuses.
    """
    result = await repo.collections.find(text, limit=limit)
    query: dict[str, Any] = {
        "text": text,
        "metadataset": repo.metadataset,
        "limit": limit,
        "kind": "collections",
    }
    return result_as_dict(result, query=query, aliases=repo.searcher.field_aliases)


async def collection_contents(
    repo: AsyncRepository, collection_id: str, *, limit: int = 20, offset: int = 0
) -> dict[str, Any]:
    """What is inside a collection: material and sub-collections.

    Both, because a collection holds both -- and the material listing alone
    does not show them. Measured on 2026-08-27 against a collection with two
    sub-collections: ``filter=files`` returns **zero** nodes. Asking only for
    material makes that collection look empty.

    Sub-collections do also appear under ``filter=folders`` (as ``ccm:map``).
    The collection endpoint is used regardless: it is the one meant for the job
    and carries collection metadata, where the folder filter is a detour that
    happens to work.

    **There is no search-based route to a collection's contents.** Scoping
    ``ngsearch`` with ``virtual:primaryparent_nodeid`` is the obvious idea and
    the repository rejects it with HTTP 400 (measured 2026-08-27, and by
    wlo-mcp-sc on 2026-07-17). It would also be the wrong answer: a curated
    collection holds *references* to nodes whose primary parent lives elsewhere,
    and a parent-scoped search would miss exactly those. The two routes that do
    exist are the two this function calls -- material and sub-collections.

    Args:
        repo: the connection.
        collection_id: the collection to open.
        limit, offset: page size and starting point, applied to the material.

    Returns:
        ``{id, materials, collections, total_materials, returned_materials}``.
        Materials carry the same shape as search hits.

    Raises:
        NotFoundError: when no collection carries this id.
    """
    segment = path_segment(collection_id)

    async def material() -> dict[str, Any]:
        return await repo.raw.json(
            "GET", f"/node/v1/nodes/-home-/{segment}/children",
            params={
                "maxItems": limit, "skipCount": offset, "filter": "files",
                # Without this the endpoint returns nodes with an EMPTY
                # properties object -- measured 2026-08-27. The materials then
                # arrive without subject, level or description, and the flow's
                # whole point is gone while it still looks like it worked.
                "propertyFilter": "-all-",
            },
        )

    async def sub_collections() -> dict[str, Any]:
        return await repo.raw.json(
            "GET", f"/collection/v1/collections/-home-/{segment}/children/collections",
            params={"maxItems": limit},
        )

    nodes_response, collections_response = await asyncio.gather(
        material(), sub_collections()
    )

    aliases = repo.searcher.field_aliases
    materials = [
        hit_as_dict(SearchHit.from_node(node, repo.url), aliases)
        for node in (nodes_response.get("nodes") or [])
    ]
    children = [
        hit_as_dict(SearchHit.from_node(node, repo.url), aliases)
        for node in (collections_response.get("collections") or [])
    ]

    pagination = nodes_response.get("pagination") or {}
    return {
        "id": collection_id,
        "materials": materials,
        "collections": children,
        "total_materials": int(pagination.get("total") or 0),
        "returned_materials": len(materials),
    }


async def relations(repo: AsyncRepository, node_id: str) -> dict[str, Any]:
    """What this node is linked to, as JSON.

    Relations join nodes that stand side by side -- the parts of a series, a
    resource and what it is based on. A collection is a container; this is not.

    The perspective is the asked node's: a part reports ``isPartOf`` and the
    series reports ``hasPart`` for the same link. Each entry names the node at
    the *other* end.

    Args:
        repo: the connection.
        node_id: the node to look at.

    Returns:
        ``{id, count, relations}``. Each relation carries ``type``, the other
        node's ``id``/``title``/``url``, and two flags worth reading:
        ``ai_generated`` (a machine proposed this) and ``approved`` (a person
        confirmed it). An unapproved machine suggestion is not a fact.

    Raises:
        NotFoundError: when no node carries this id.
    """
    found = await repo.relations.of(node_id)
    entries = []
    for relation in found:
        # The other end: whichever side is not the node we asked about.
        other_id = relation.to_id if relation.from_id == node_id else relation.from_id
        other_title = (
            relation.to_title if relation.from_id == node_id else relation.from_title
        )
        entries.append({
            "type": relation.type,
            "id": other_id,
            "title": other_title,
            "url": f"{repo.url}/components/render/{other_id}" if other_id else "",
            "ai_generated": relation.ai_generated,
            "approved": relation.approved,
        })
    return {"id": node_id, "count": len(entries), "relations": entries}


async def child_objects(repo: AsyncRepository, node_id: str) -> dict[str, Any]:
    """The further documents belonging to one node, as JSON.

    A worksheet's answer sheet, a lesson plan's handouts. They belong to the
    parent rather than standing on their own, which is what separates them from
    a collection's contents.

    Args:
        repo: the connection.
        node_id: the main node.

    Returns:
        ``{id, count, children}``. Each child carries ``id``, ``name``,
        ``title``, ``url``, ``mimetype``, ``order`` and ``has_content``.

    Raises:
        NotFoundError: when no node carries this id.
    """
    node = await repo.nodes.get(node_id)
    children = await node.children.list()
    return {
        "id": node_id,
        "count": len(children),
        "children": [
            {
                "id": child.id,
                "name": child.name,
                "title": child.title,
                "url": child.url,
                "mimetype": child.content.mimetype,
                "has_content": child.content.has_content,
                "order": _order_of(child),
            }
            for child in children
        ],
    }


def _order_of(child: Node) -> int | None:
    """The display position, or ``None`` when the child carries none."""
    raw = child.get(ORDER_PROPERTY)
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None
