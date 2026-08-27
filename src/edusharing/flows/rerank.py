"""Searching several query variants at once and merging the rankings.

Its own module because it is the only part of the flow layer that turns one call
into several requests. That is a real cost, and it should be visible where it
happens rather than hidden inside ``search``.

The chain: expand the query into variants, ask them in parallel, fuse the
rankings (RRF), score every candidate for text and metadata quality, blend, and
return the best ones. Ported from ``wlo-mcp-sc``'s ``enhancedSearch``
(Apache-2.0).

What the score is built from, and what it deliberately is **not**: the position
a candidate held in the repository's own result list does not enter into it.

The original port used reciprocal rank fusion, which weighs that position. It
was removed after measuring twice. First, the repository's order is not stable:
the same query asked twice returns 25 hits of which 15 differ (2026-08-27), so
the position carries noise rather than information. Second, feeding it in made
the ranking depend on the order candidates arrived in -- of 30 shuffles of one
fixed candidate set, only 14 produced the same result.

What is left is order-independent by construction: the quality score of each
record (0.8) and how many variants returned it at all (0.2). Same candidates in,
same ranking out -- which is what makes two runs comparable, and what lets a
caller tell a changed ranking from a changed mood of the index.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

from ..errors import EduSharingError
from ..results import SearchHit, SearchResult
from .expand import expand_query
from .language import GERMAN, LanguageProfile
from .ranking import score_hit

if TYPE_CHECKING:  # pragma: no cover
    from ..repository import AsyncRepository

__all__ = ["DEFAULT_POOL", "search_reranked"]

#: Candidates fetched **per variant** for ranking -- not what is returned. A
#: bigger pool costs transfer and buys recall.
DEFAULT_POOL = 25

#: How much the record itself answers the query.
_QUALITY_WEIGHT = 0.8
#: How many of the asked variants returned it at all. Counting appearances, not
#: their positions -- that is what keeps the outcome order-independent.
_AGREEMENT_WEIGHT = 0.2

#: edu-sharing keeps deleted material in the index as a placeholder. To a
#: language model those look like hits.
_DELETED_MARKERS = ("element wurde gelöscht", "element was removed")


def _is_deleted(hit: SearchHit) -> bool:
    title = hit.title.lower()
    description = (hit.description or "").lower()
    if not hit.title.strip():
        return True
    return any(m in title or m in description for m in _DELETED_MARKERS)


async def search_reranked(
    repo: AsyncRepository,
    text: str,
    *,
    filters: dict[str, str | list[str]] | None = None,
    facets: list[str] | None = None,
    limit: int = 10,
    pool: int = DEFAULT_POOL,
    language: LanguageProfile = GERMAN,
    **aliases: str | list[str],
) -> tuple[SearchResult, list[str]]:
    """Run every query variant and return the merged, reordered result.

    Returns:
        The result and the labels of the variants that were actually asked.

    Raises:
        EduSharingError: when **no** variant could be executed. That is not an
            empty result -- it is a search that did not happen. Measured in
            wlo-mcp-sc on 2026-07-31: a wrong service password made every call
            401, and the search answered "0 hits found" with no error at all,
            turning a configuration fault into an apparent fact about the world.
    """
    variants = expand_query(text, language)
    if not variants:
        raise EduSharingError("An empty query cannot be reranked.")

    async def run(variant):
        return await repo.searcher.search(
            variant.text, filters=filters, facets=facets, limit=pool, **aliases
        )

    outcomes = await asyncio.gather(
        *(run(v) for v in variants), return_exceptions=True
    )

    successful: list[tuple[Any, SearchResult]] = []
    failures: list[str] = []
    for variant, outcome in zip(variants, outcomes, strict=True):
        if isinstance(outcome, BaseException):
            failures.append(f"{variant.label}: {outcome}")
            continue
        successful.append((variant, outcome))

    if not successful:
        raise EduSharingError(
            "The search could not be performed: every query variant failed. "
            + " | ".join(failures)
        )

    merged = _merge(successful, text, repo.searcher.field_aliases, language, limit)
    if failures:
        # One variant failing is what the parallel run is for -- but silence
        # would let a partial result pass as a complete one.
        merged.warnings.extend(f"query variant failed -- {f}" for f in failures)
    return merged, [v.label for v, _ in successful]


def _merge(
    successful: list[tuple[Any, SearchResult]],
    query: str,
    aliases: dict[str, str],
    language: LanguageProfile,
    limit: int,
) -> SearchResult:
    """Fuse the rankings, score the candidates, and take the best."""
    by_id: dict[str, SearchHit] = {}
    #: Sum of the weights of the variants that returned this record. Weighted,
    #: because being found by the original phrasing says more than being found
    #: by a synonym guess -- but the position within either is ignored.
    agreement: dict[str, float] = {}

    for variant, result in successful:
        for hit in result.hits:
            if not hit.id or _is_deleted(hit):
                continue
            by_id.setdefault(hit.id, hit)
            agreement[hit.id] = agreement.get(hit.id, 0.0) + variant.weight

    quality = {
        node_id: score_hit(hit, query, aliases, language)
        for node_id, hit in by_id.items()
    }

    # Normalised, so the two scales can be blended at all. The floors keep a
    # division by zero away when nothing scored.
    max_quality = max([*quality.values(), 1])
    max_agreement = max([*agreement.values(), 0.001])

    def final(node_id: str) -> float:
        return (
            quality[node_id] / max_quality * _QUALITY_WEIGHT
            + agreement[node_id] / max_agreement * _AGREEMENT_WEIGHT
        )

    # The id is the tie-breaker: without it the order of equally scored records
    # depends on insertion from a parallel gather and flips between identical
    # calls.
    ordered = sorted(by_id, key=lambda i: (-final(i), i))

    # The variant that actually found something speaks for the whole result.
    #
    # Taking the FIRST variant instead looks natural and is wrong: measured live
    # on 2026-08-27, "Ich suche ein Arbeitsblatt zur Bruchrechnung" made the
    # full-phrase variant report 0 while the topic variant found 1591 -- and the
    # answer read "3 hits, total 0". That is not untidy, it is contradictory: a
    # language model reads "there is nothing" and passes it on while three hits
    # sit next to it.
    #
    # The maximum, not the sum: overlapping variants cannot be added, so the
    # figure is a lower bound whenever more than one variant ran.
    leading = max(successful, key=lambda pair: pair[1].total)[1]
    first = successful[0][1]

    return SearchResult(
        hits=[by_id[i] for i in ordered[:limit]],
        # The pool is a ranking device, not a statement about how much exists.
        # Reporting its size here would understate a broad query enormously.
        total=leading.total,
        facets=leading.facets,
        suggestions=leading.suggestions,
        # Unresolved filters belong to the original query -- they are the same
        # for every variant, because only the text differs.
        unresolved=first.unresolved,
        ignored=first.ignored,
        warnings=list(first.warnings),
        total_is_lower_bound=len(successful) > 1 or first.total_is_lower_bound,
        raw=leading.raw,
    )
