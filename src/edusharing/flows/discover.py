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
from collections.abc import Sequence
from dataclasses import replace
from typing import TYPE_CHECKING, Any

from .. import placement as placement_api
from ..childobjects import ORDER_PROPERTY
from ..errors import EduSharingError, ValidationError
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
    "describe_many",
    "field_property",
    "find_collections",
    "placement",
    "related",
    "relations",
    "search",
    "search_all",
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
        name, type, access, public, has_content, keywords, properties}``.
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
        ``{id, title, path, collections, scope}``.

        ``path`` runs **top down**, ready to print as a breadcrumb -- unlike
        ``node.parents()``, which mirrors the endpoint and gives the nearest
        first. ``scope`` says how far the path reaches: it stops at the
        boundary of what the account may read, and saying so keeps a truncated
        path from passing as a complete one.

    Raises:
        NotFoundError: when no node carries this id.
        PermissionDeniedError: when the way up is refused.
    """
    ancestry, collections = await asyncio.gather(
        placement_api.ancestry_of(repo.nodes, node_id),
        placement_api.collections_of(repo.nodes, node_id),
    )
    return {
        "id": node_id,
        # From the parents answer, where the node is the first entry -- so the
        # title costs no request of its own.
        "title": ancestry.node.title if ancestry.node else None,
        "path": [_step(n) for n in reversed(ancestry.parents)],
        "collections": [_step(n) for n in collections],
        "scope": ancestry.scope,
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


#: What "more of this" is decided by, unless the caller says otherwise. Two
#: topical fields; ``license`` or ``difficulty`` would say nothing about what a
#: resource is about.
RELATED_ON = ("subject", "level")


async def related(
    repo: AsyncRepository,
    node_id: str,
    *,
    on: Sequence[str] = RELATED_ON,
    limit: int = 10,
) -> dict[str, Any]:
    """More material like this one.

    **Not a relation.** ``/relation/v1`` links two nodes because somebody said
    they belong together; this takes the seed's own fields, searches with them
    as filters, and drops the seed from the result. Both are called "related",
    and the difference is worth stating: one is an assertion, the other a
    resemblance.

    Args:
        repo: the connection.
        node_id: the node to start from.
        on: which short names decide the resemblance. The default is topical;
            which short names exist at all is the instance's metadata set.
        limit: how many to return.

    Returns:
        ``{seed, based_on, hits, unresolved, reason}``. ``based_on`` names the
        values the search was built from -- without it nobody can judge the
        resemblance. ``unresolved`` names the ones the instance could not
        resolve: those did **not** narrow the search, so the result is broader
        than it looks. When the seed carries none of the fields, ``hits`` is
        empty and ``reason`` says so -- an unfiltered search would answer
        "more of this" with anything.

    Raises:
        ValidationError: for a short name the search does not know -- a typo
            must not pass as "no filter".
        NotFoundError: when no node carries this id.
    """
    aliases = repo.searcher.field_aliases
    unknown = [name for name in on if name not in aliases]
    if unknown:
        raise ValidationError(
            f"Unknown short name(s) for related(): {', '.join(unknown)}. "
            f"This instance knows: {', '.join(sorted(aliases))}."
        )

    seed = await describe(repo, node_id)
    based_on = {
        name: list(seed["fields"][name])
        for name in on
        if seed["fields"].get(name)
    }
    if not based_on:
        return {
            "seed": {"id": node_id, "title": seed.get("title")},
            "based_on": {},
            "hits": [],
            "unresolved": [],
            "reason": (
                f"The node carries none of {', '.join(on)}, and a search "
                "without them would answer 'more of this' with anything."
            ),
        }

    found = await search(repo, None, filters=None, limit=limit + 1, **based_on)
    hits = [h for h in found["hits"] if h["id"] != node_id][:limit]
    return {
        "seed": {"id": node_id, "title": seed.get("title")},
        "based_on": based_on,
        "hits": hits,
        "unresolved": found["unresolved"],
        "reason": "",
    }


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


async def search_all(
    repo: AsyncRepository,
    text: str,
    *,
    filters: dict[str, str | list[str]] | None = None,
    facets: list[str] | None = None,
    limit: int = 10,
    rerank: bool = False,
    pool: int = DEFAULT_POOL,
    language: LanguageProfile = GERMAN,
    deduplicate: bool = True,
    **aliases: str | list[str],
) -> dict[str, Any]:
    """Material **and** collections for one query, in a single call.

    Asking a repository about a topic usually means both questions at once: the
    individual resources, and the collections in which somebody has already put
    together what belongs to it. They are different endpoints with different
    answer shapes, so the two stay in separate buckets rather than being merged
    into one ranking that would compare things that do not compare.

    Args:
        repo: the connection.
        text: what to search for. Required here -- a filter-only search has no
            counterpart on the collection side.
        filters, facets, limit, rerank, pool, language, deduplicate, aliases:
            as in ``search``. ``limit`` applies **per bucket**, so neither
            crowds out the other.

    Returns:
        ``{query, materials, collections}``. Each bucket is exactly what
        ``search`` and ``find_collections`` return on their own, including
        their own ``total`` -- the collection figure is a lower bound, the
        material one is not, and a joint sum would blur that.

        ``collections.filters_ignored`` names the filters that could **not** be
        applied to the collections. Measured: that query accepts
        ``ngsearchword`` and nothing else; any further criterion ends in
        ``400 DAOValidationException``. Applying a filter to one bucket and
        silently not to the other would claim a narrowing that did not happen.

    Raises:
        ValidationError: on an empty query, or an unknown short name.
        EduSharingError: for anything the repository refuses.
    """
    if not text or not text.strip():
        raise ValidationError(
            "search_all needs a query -- the collection search takes a search "
            "word and nothing else, so there is no filter-only variant here. "
            "Use search() for that."
        )

    materials, collections = await asyncio.gather(
        search(repo, text, filters=filters, facets=facets, limit=limit,
               rerank=rerank, pool=pool, language=language,
               deduplicate=deduplicate, **aliases),
        find_collections(repo, text, limit=limit),
    )
    collections["filters_ignored"] = [*(filters or {}), *aliases]
    return {
        "query": {"text": text, "metadataset": repo.metadataset, "limit": limit},
        "materials": materials,
        "collections": collections,
    }


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
