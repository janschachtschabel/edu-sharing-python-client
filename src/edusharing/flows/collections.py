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
from dataclasses import replace
from typing import TYPE_CHECKING, Any

from ..errors import ValidationError
from ..results import SearchHit, SearchResult
from .fields import resolve_vocabulary
from .find import search
from .language import GERMAN, LanguageProfile
from .pages import find_pages
from .ranking import query_terms, term_matches
from .rerank import DEFAULT_POOL
from .serialize import result_as_dict
from .tree import browse_tree

if TYPE_CHECKING:  # pragma: no cover
    from ..repository import AsyncRepository

__all__ = ["find_collections", "search_all"]


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
      the vocabulary and matched against each hit's own properties. A hit that
      carries no properties at all cannot be judged -- one leg of the
      collection search has a fixed, empty projection -- and is counted in
      ``unjudged`` rather than silently kept or dropped.
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
        ``unresolved`` names a filter value the vocabulary does not know --
        that filter was not applied, and the result is broader than asked.

    Raises:
        ValidationError: for an unknown short name.
        EduSharingError: for anything the repository refuses.
    """
    wanted, unresolved = await resolve_vocabulary(repo, aliases, every_value=True)
    query: dict[str, Any] = {
        "text": text,
        "metadataset": repo.metadataset,
        "limit": limit,
        "kind": "collections",
        "filters": wanted,
        "parent_id": parent_id,
    }
    if parent_id:
        result = await _below(repo, parent_id, text, limit)
    else:
        result = await repo.collections.find(text, limit=limit)

    unjudged = 0
    if wanted:
        kept = []
        for hit in result.hits:
            props = hit.properties()
            if not props:
                unjudged += 1
                continue
            if all(_carries(props, prop, values) for prop, values in wanted.items()):
                kept.append(hit)
        result = replace(result, hits=kept)

    answer = result_as_dict(
        result, query=query, aliases=repo.searcher.field_aliases, properties=properties)
    answer["unresolved"] = unresolved
    answer["unjudged"] = unjudged
    return answer


def _carries(props: dict[str, Any], prop: str, values: list[str]) -> bool:
    """Whether the hit carries one of the wanted values for ``prop``."""
    stored = props.get(prop) or []
    stored = stored if isinstance(stored, list) else [stored]
    return any(v in stored for v in values)


async def _below(
    repo: AsyncRepository, parent_id: str, text: str, limit: int
) -> SearchResult:
    """The collections below ``parent_id`` whose title matches every term."""
    tree = await browse_tree(repo, parent_id, depth=2)
    terms = query_terms(text)
    hits: list[SearchHit] = []
    # Level by level: the direct sub-collections first, then theirs. A reader
    # scanning the answer expects the nearer ones before the deeper ones.
    level = list(tree["collections"])
    while level:
        for entry in level:
            title = entry.get("title") or ""
            if all(term_matches(term, title.lower()) for term in terms):
                hits.append(SearchHit(
                    id=entry["id"], title=title,
                    url=f"{repo.url}/components/render/{entry['id']}",
                ))
        level = [child for entry in level for child in (entry.get("collections") or [])]
    warnings = ["the walk was cut short by its cap"] if tree["truncated"] else []
    return SearchResult(
        hits=hits[:limit], total=len(hits),
        total_is_lower_bound=tree["truncated"], warnings=warnings,
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
        include_pages: also ask which of the collection hits carry a
            curated page (``find_pages``) and add them as ``pages``. Off by
            default: it costs the collection search a second time.
        properties: further properties under ``fields``, as stored.

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
               deduplicate=deduplicate, properties=properties, **forwarded),
        find_collections(repo, text, limit=limit, properties=properties),
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
    answer = {
        "query": {"text": text, "metadataset": repo.metadataset, "limit": limit},
        "materials": materials,
        "collections": collections,
    }
    if include_pages:
        answer["pages"] = await find_pages(repo, text, limit=limit)
    return answer
