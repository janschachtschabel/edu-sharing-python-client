"""Reading flows: one call where the API-level route needs several.

The API level is deliberately close to edu-sharing -- ``search`` returns a
``SearchResult``, ``node`` returns a ``Node``. That is right for anyone writing
Python against it, and wrong for anything that has to hand the outcome onwards
as data: an MCP tool, an HTTP endpoint, a language model.

These flows do the same work and return plain JSON structures. Nothing here
adds capability; it removes steps.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..errors import ValidationError
from ..results import SearchHit
from .language import GERMAN, LanguageProfile
from .rerank import DEFAULT_POOL, search_reranked
from .serialize import hit_as_dict, result_as_dict

if TYPE_CHECKING:  # pragma: no cover
    from ..repository import AsyncRepository

__all__ = ["describe", "field_property", "search", "vocabulary"]


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

    return result_as_dict(result, query=query, aliases=repo.searcher.field_aliases)


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
    """Everything about one node in a single call.

    The API-level route needs three: load the node, read its properties, ask
    which collections it sits in.

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
