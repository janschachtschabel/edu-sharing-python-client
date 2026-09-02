"""Flows that answer *which collections* -- and the two questions at once.

Split out of ``find.py`` on 2026-09-02, when that module passed 400 lines and
was about to grow a second responsibility: a collection search with filters
and a parent scope. The seam is the endpoint. Material is found through the
metadata-set query with its criteria; collections through the two collection
routes, which take a search word and nothing else (measured) -- so whatever a
collection search narrows by has to be applied here, not sent.
"""

from __future__ import annotations

import asyncio
from collections.abc import Sequence
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Any

from ..errors import EduSharingError, ValidationError
from ..results import SearchHit, SearchResult
from .fields import carries, resolve_vocabulary
from .find import search
from .language import GERMAN, LanguageProfile
from .pages import pages_among
from .ranking import query_terms, term_matches
from .rerank import DEFAULT_POOL
from .serialize import result_as_dict
from .tree import DEFAULT_MAX_COLLECTIONS, walk_collections

if TYPE_CHECKING:  # pragma: no cover
    from ..repository import AsyncRepository

__all__ = ["find_collections", "search_all"]

#: Candidates fetched when a short-name filter has to be judged locally: five
#: times ``limit``, at most this many. Disclosed in ``warnings`` when the
#: search knew more.
_FILTER_SCAN_MAX = 100


async def find_collections(
    repo: AsyncRepository,
    text: str = "",
    *,
    limit: int = 10,
    parent_id: str | None = None,
    properties: Sequence[str] = (),
    **aliases: str | list[str],
) -> dict[str, Any]:
    """Search collections and return the outcome as JSON.

    Collections are how edu-sharing groups material for teaching, so finding
    them is a different question from finding single resources -- and it uses a
    different endpoint. That endpoint takes a search word and **nothing else**
    (measured: any further criterion ends in ``400 DAOValidationException``),
    so what narrows a collection search is applied here:

    * ``subject="Biologie"`` and the other short names are resolved against
      the vocabulary and matched against each hit's own properties. Because
      the endpoint cannot narrow, more candidates than ``limit`` are fetched
      (five times, at most 100) and judged here; ``total`` then counts the
      matches among them, and ``warnings`` says when the search knew more
      candidates than were judged. A hit that carries no properties at all
      cannot be judged -- one leg of the collection search has a fixed,
      empty projection -- and is counted in ``unjudged`` rather than
      silently kept or dropped.
    * ``parent_id`` does not search at all: the sub-collections below it are
      walked (two levels, see ``browse_tree``) and ``text`` is matched against
      their titles, every term. That is how the MCP scopes a collection search
      to a portal, because the repository cannot.

    Args:
        repo: the connection.
        text: what to search for. May be empty with ``parent_id`` -- then
            every collection below it is listed.
        limit: how many to return.
        parent_id: walk this collection's subtree instead of searching.
        properties: further properties to carry under ``fields``, as stored.
        **aliases: configured short names, applied locally.

    Returns:
        The same shape as ``search``, plus ``unjudged``: hits that carried no
        properties and could not be filtered. ``total_is_lower_bound`` is
        **true** for a search: the collection search asks two routes and
        merges them, so the figure counts at least this many, possibly more.
        With ``parent_id`` it is true only when the walk was cut short.
        ``query.filters`` echoes your words, as ``search`` does.
        ``unresolved`` names a filter value the vocabulary does not know --
        that filter was not applied, and the result is broader than asked.

    Raises:
        ValidationError: for an unknown short name.
        EduSharingError: for anything the repository refuses.
    """
    found = await _collections(repo, text, limit=limit, parent_id=parent_id, aliases=aliases)
    return _answer(repo, found.result, found.query, properties, found.unresolved,
                   found.unjudged)


@dataclass(frozen=True)
class _Found:
    """A collection search before serialisation -- the hits still carry their
    records, which is what the pages bucket reads."""

    result: SearchResult
    query: dict[str, Any]
    unresolved: list[dict[str, Any]]
    unjudged: int


async def _collections(
    repo: AsyncRepository, text: str, *, limit: int, parent_id: str | None,
    aliases: dict[str, Any],
) -> _Found:
    """``find_collections`` up to the answer: the filtered, cut result."""
    wanted, unresolved = await resolve_vocabulary(repo, aliases, every_value=True)
    query = _query(repo, text, limit, aliases, parent_id)
    # With a local filter the page must hold candidates, not answers. Below a
    # parent the walk holds every record anyway: judge them all, cut after.
    if parent_id:
        result = await _below(repo, parent_id, text, None if wanted else limit)
    else:
        scan = min(limit * 5, _FILTER_SCAN_MAX) if wanted else limit
        result = await repo.collections.find(text, limit=scan)

    unjudged = 0
    if wanted:
        judged = len(result.hits)
        kept = []
        for hit in result.hits:
            props = hit.properties()
            if not props:
                unjudged += 1
                continue
            if all(carries(props, prop, values) for prop, values in wanted.items()):
                kept.append(hit)
        beyond = result.total > judged
        warnings = list(result.warnings)
        if beyond:
            warnings.append(
                f"filter applied locally to {judged} of {result.total} candidates -- "
                "matches beyond them are not counted"
            )
        # ``total`` now counts matches, not candidates -- and says so.
        result = replace(
            result, hits=kept[:limit], total=len(kept),
            total_is_lower_bound=result.total_is_lower_bound or beyond, warnings=warnings,
        )

    return _Found(result, query, unresolved, unjudged)


def _query(
    repo: AsyncRepository, text: str, limit: int, aliases: dict[str, Any],
    parent_id: str | None,
) -> dict[str, Any]:
    return {
        "text": text,
        "metadataset": repo.metadataset,
        "limit": limit,
        "kind": "collections",
        # The caller's words, as ``search`` echoes them; the URIs are applied.
        "filters": dict(aliases),
        "parent_id": parent_id,
    }


def _answer(
    repo: AsyncRepository, result: SearchResult, query: dict[str, Any],
    properties: Sequence[str], unresolved: list[dict[str, Any]], unjudged: int,
) -> dict[str, Any]:
    """The one shape a collection answer has -- filled or empty."""
    answer = result_as_dict(
        result, query=query, aliases=repo.searcher.field_aliases, properties=properties)
    answer["unresolved"] = unresolved
    answer["unjudged"] = unjudged
    return answer


def _empty_collections(
    repo: AsyncRepository, text: str, limit: int, failure: str, aliases: dict[str, Any]
) -> dict[str, Any]:
    """An empty ``find_collections`` answer naming the failure. Built through
    the same path as a filled one, so the two cannot drift apart."""
    return _answer(
        repo, SearchResult(total_is_lower_bound=True, warnings=[failure]),
        _query(repo, text, limit, aliases, None), properties=(), unresolved=[], unjudged=0,
    )


async def _below(
    repo: AsyncRepository, parent_id: str, text: str, limit: int | None
) -> SearchResult:
    """The collections below ``parent_id`` whose title matches every term."""
    entries, _opened, truncated = await walk_collections(
        repo, parent_id, depth=2, max_collections=DEFAULT_MAX_COLLECTIONS)
    terms = query_terms(text)
    # A query of stopwords only is still a query: matched as typed, not as
    # nothing -- "nothing" would have matched every collection.
    needle = text.strip().lower()
    hits: list[SearchHit] = []
    # Level by level: the direct sub-collections first, then theirs. A reader
    # scanning the answer expects the nearer ones before the deeper ones.
    level = entries
    while level:
        for entry in level:
            title = (entry.get("title") or "").lower()
            matched = (all(term_matches(term, title) for term in terms) if terms
                       else needle in title)
            if matched:
                # The record itself, so a short-name filter can judge the hit.
                hits.append(SearchHit.from_node(entry["raw"], repo.url))
        level = [child for entry in level for child in (entry.get("collections") or [])]
    warnings = ["the walk was cut short: its cap, or more sub-collections than a "
                "page lists"] if truncated else []
    return SearchResult(
        hits=hits[:limit], total=len(hits),
        total_is_lower_bound=truncated, warnings=warnings,
    )


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
    include_pages: bool = False,
    properties: Sequence[str] = (),
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
        include_pages: also say which of the collection hits carry a
            curated page and add them as ``pages`` -- read off the collection
            hits already fetched, so it costs no further request. Off by
            default so the answer stays small unless asked. When the
            collection search fails, ``pages`` comes back empty with
            ``error`` set, like the collection bucket.
        properties: further properties under ``fields``, as stored.

    Returns:
        ``{query, materials, collections}``. Each bucket is exactly what
        ``search`` and ``find_collections`` return on their own, including
        their own ``total`` -- the collection figure is a lower bound, the
        material one is not, and a joint sum would blur that.

        The short names reach both buckets: ``find_collections`` applies them
        locally, since the collection query accepts ``ngsearchword`` and
        nothing else (measured: any further criterion ends in
        ``400 DAOValidationException``). Raw ``filters`` have no local
        counterpart there; ``collections.filters_ignored`` names them, because
        applying a filter to one bucket and silently not to the other would
        claim a narrowing that did not happen.

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
    # ``return_exceptions=True``: each slot is a result OR the exception that
    # ended it; the annotations say so, because a checker cannot read it out
    # of ``gather``. Only what the repository refused is a partial answer -- a
    # bug in either bucket raises, or it would hide in an ``error`` field.
    material_outcome: dict[str, Any] | BaseException
    collection_outcome: _Found | BaseException
    material_outcome, collection_outcome = await asyncio.gather(
        search(repo, text, filters=filters, facets=facets, limit=limit,
               rerank=rerank, pool=pool, language=language,
               deduplicate=deduplicate, properties=properties, **forwarded),
        # The short names go along: ``find_collections`` applies them locally,
        # so only raw ``filters`` stay out of that bucket. Before
        # serialisation, because the pages bucket reads the records.
        _collections(repo, text, limit=limit, parent_id=None, aliases=forwarded),
        return_exceptions=True,
    )
    for outcome in (material_outcome, collection_outcome):
        if isinstance(outcome, BaseException) and not isinstance(outcome, EduSharingError):
            raise outcome
    if isinstance(material_outcome, BaseException):
        # The material bucket is the main question. Handing it back empty would
        # claim there is nothing, which is a different statement from "the
        # search failed".
        raise material_outcome
    materials: dict[str, Any] = material_outcome

    collections: dict[str, Any]
    pages: dict[str, Any] = {}
    if isinstance(collection_outcome, BaseException):
        # ``collections.find`` already says one level down that half a result
        # is usable and a faked empty one is not. Between the two buckets a
        # collection outage used to take the material hits with it (audit A9).
        failure = f"{type(collection_outcome).__name__}: {collection_outcome}"
        collections = _empty_collections(repo, text, limit, failure, aliases)
        collections["error"] = failure
        if include_pages:
            # The same path as a filled bucket, so the keys cannot drift.
            pages = {**pages_among(SearchResult(total_is_lower_bound=True), text),
                     "reason": failure, "error": failure}
    else:
        found: _Found = collection_outcome
        collections = _answer(repo, found.result, found.query, properties,
                              found.unresolved, found.unjudged)
        if include_pages:
            # Read off the hits already fetched: the same search, no second one.
            pages = {**pages_among(found.result, text), "error": ""}
    collections.setdefault("error", "")
    collections["filters_ignored"] = list(filters or {})
    answer = {
        "query": {"text": text, "metadataset": repo.metadataset, "limit": limit},
        "materials": materials,
        "collections": collections,
    }
    if include_pages:
        answer["pages"] = pages
    return answer
