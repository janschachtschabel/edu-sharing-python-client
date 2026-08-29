"""Reading flows that answer *which nodes* -- by query, by field, or by example.

What a flow is and why it exists is in the package docstring. ``related`` is
the odd one: it starts from an id like the flows in ``describe`` do, but what
it answers is a search question, so it lives here with the rest of them.
"""

from __future__ import annotations

import asyncio
from collections.abc import Sequence
from dataclasses import replace
from typing import TYPE_CHECKING, Any

from ..errors import ValidationError
from ..results import SearchResult
from . import dedupe
from .describe import describe
from .language import GERMAN, LanguageProfile
from .rerank import DEFAULT_POOL, search_reranked
from .serialize import result_as_dict

if TYPE_CHECKING:  # pragma: no cover
    from ..repository import AsyncRepository
__all__ = [
    "RELATED_ON",
    "field_property",
    "find_collections",
    "related",
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
    # Which short names exist is configured per instance -- ``subject``,
    # ``level``, whatever this metadata set carries. No signature can list
    # them, so the wider type says that instead of pretending otherwise.
    forwarded: dict[str, Any] = dict(aliases)
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
            limit=limit, pool=pool, language=language, **forwarded,
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
            **forwarded,
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

    # As in ``search()``: the short names are configured, not declarable.
    forwarded: dict[str, Any] = dict(aliases)
    # Two names per bucket: what the gather handed back, which may be an
    # exception, and the usable value. Overwriting the first with the second
    # hid from the reader that they are different things.
    # ``return_exceptions=True`` means each slot is a result OR the exception
    # that ended it; the annotation says so, because a checker cannot read it
    # out of ``gather``.
    material_outcome: dict[str, Any] | BaseException
    collection_outcome: dict[str, Any] | BaseException
    material_outcome, collection_outcome = await asyncio.gather(
        search(repo, text, filters=filters, facets=facets, limit=limit,
               rerank=rerank, pool=pool, language=language,
               deduplicate=deduplicate, **forwarded),
        find_collections(repo, text, limit=limit),
        return_exceptions=True,
    )
    if isinstance(material_outcome, BaseException):
        # The material bucket is the main question. Handing it back empty would
        # claim there is nothing, which is a different statement from "the
        # search failed".
        raise material_outcome
    materials: dict[str, Any] = material_outcome

    collections: dict[str, Any]
    if isinstance(collection_outcome, BaseException):
        # ``collections.find`` already says one level down that half a result
        # is usable and a faked empty one is not. It applies that between its
        # two routes; between the two buckets it did not, so a collection
        # outage took the material hits with it (audit A9).
        #
        # Built through ``result_as_dict`` rather than written out, so the
        # empty bucket cannot drift away from the filled one.
        failure = f"{type(collection_outcome).__name__}: {collection_outcome}"
        collections = result_as_dict(
            SearchResult(total_is_lower_bound=True, warnings=[failure]),
            query={"text": text, "metadataset": repo.metadataset,
                   "limit": limit, "kind": "collections"},
            aliases=repo.searcher.field_aliases,
        )
        collections["error"] = failure
    else:
        collections = collection_outcome
    collections.setdefault("error", "")
    collections["filters_ignored"] = [*(filters or {}), *aliases]
    return {
        "query": {"text": text, "metadataset": repo.metadataset, "limit": limit},
        "materials": materials,
        "collections": collections,
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
    based_on: dict[str, Any] = {
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
