"""Reading flows that answer *which nodes* -- by query, by field, or by example.

What a flow is and why it exists is in the package docstring. ``related`` is
the odd one: it starts from an id like the flows in ``describe`` do, but what
it answers is a search question, so it lives here with the rest of them.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import replace
from typing import TYPE_CHECKING, Any

from ..errors import ValidationError
from ..search import DEFAULT_FACET_LIMIT
from . import dedupe
from .describe import describe
from .language import GERMAN, LanguageProfile
from .rerank import DEFAULT_POOL, search_reranked
from .serialize import result_as_dict

if TYPE_CHECKING:  # pragma: no cover
    from ..repository import AsyncRepository
__all__ = [
    "EXCLUSION_MAX",
    "RELATED_ON",
    "field_property",
    "related",
    "search",
    "vocabulary",
]


#: The largest refill ``search`` adds after ``exclude_ids``; the caller's own
#: ``limit`` is never capped. A long exclusion list must not turn one call
#: into a request for thousands -- ``warnings`` says so instead.
EXCLUSION_MAX = 200


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
    exclude_ids: Sequence[str] = (),
    facet_limit: int = DEFAULT_FACET_LIMIT,
    properties: Sequence[str] = (),
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
        exclude_ids: hits to leave out -- the ones already shown. The page is
            refilled: that many more are asked for (up to ``EXCLUSION_MAX``),
            so eight requested and three excluded still yields eight. When
            the refill cannot fill the page -- more exclusions than the cap,
            or the excluded ids outnumber what one page holds -- ``warnings``
            says so rather than letting a short page read as "nothing left".
        facet_limit: values per facet, 20 by default and up to what the
            repository allows.
        properties: further properties to carry under ``fields`` by their
            full name, as stored -- for anything the short names do not
            cover, such as the content type.
        **aliases: configured short names, e.g. ``subject="Biologie"``.

    Returns:
        ``{query, total, total_is_lower_bound, returned, duplicates_removed,
        hits, facets, unresolved, ignored, warnings, suggestions}``.

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
    excluded = {i for i in exclude_ids if i}
    warnings: list[str] = []
    if excluded:
        query["exclude_ids"] = list(exclude_ids)
    # Ask for that many more, so the page stays full after dropping them. The
    # refill is capped; the caller's own limit is not.
    extra = min(len(excluded), EXCLUSION_MAX)
    if len(excluded) > EXCLUSION_MAX:
        warnings.append(
            f"{len(excluded)} ids excluded but refilled for {EXCLUSION_MAX} only: "
            "the page may come back short"
        )
    ask = limit + extra

    # Reranking needs something to rank against. A pure filter query has no
    # text, so there is nothing to expand and nothing to score.
    reranked = bool(rerank and text and text.strip())
    if reranked and text is not None:   # the second half only narrows the type
        result, variants = await search_reranked(
            repo, text,
            filters=filters, facets=facet_properties or None,
            # The pool must hold the refill too, or the exclusions eat into it.
            limit=ask, pool=max(pool, ask), language=language, facet_limit=facet_limit,
            **forwarded,
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
            limit=ask,
            offset=offset,
            facet_limit=facet_limit,
            **forwarded,
        )
    if excluded:
        result = replace(result, hits=[h for h in result.hits if h.id not in excluded])
        # Under rerank there is no offset -- the pool is the knob.
        beyond = result.total > (ask if reranked else offset + ask)
        if len(result.hits) < limit and beyond:
            knob = "a larger pool" if reranked else "a higher offset"
            warnings.append(
                f"page short after exclusions: {len(result.hits)} of {limit}, while "
                f"{result.total} exist -- ask again with {knob}"
            )

    folded: dict[str, list[str]] = {}
    if deduplicate:
        # After ranking, not before: the order decides which of a group is kept,
        # and under rerank that is the best-scored one.
        kept, folded = dedupe.deduplicate(result.hits)
        result = replace(result, hits=kept)
    if len(result.hits) > limit:
        result = replace(result, hits=result.hits[:limit])
    if warnings:
        result = replace(result, warnings=[*result.warnings, *warnings])
    return result_as_dict(
        result, query=query, aliases=repo.searcher.field_aliases, folded=folded,
        properties=properties)


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
