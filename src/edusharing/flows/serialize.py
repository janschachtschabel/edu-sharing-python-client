"""Value objects into plain JSON structures.

Its own module because it is the one thing every flow does, and because the
shape it produces IS the contract with the caller. A change here changes what
every consumer sees, which is easier to notice in a file that does nothing else.

Two rules run through all of it:

**Readable values, not URIs.** ``ccm:taxonid`` holds
``http://w3id.org/openeduhub/vocabs/discipline/080``; a language model reading
that learns nothing. edu-sharing ships a ``<prop>_DISPLAYNAME`` next to every
vocabulary field, and that is what goes out.

**Short names, not properties.** The keys are the configured aliases
(``subject``), not the edu-sharing properties (``ccm:taxonid``). Otherwise the
output would be tied to one profile -- and a repository with a different
metadata set would produce a different shape.
"""

from __future__ import annotations

from typing import Any

from ..results import Facet, SearchHit, SearchResult, UnresolvedFilter

__all__ = ["hit_as_dict", "result_as_dict"]


def hit_as_dict(
    hit: SearchHit,
    aliases: dict[str, str],
    folded: dict[str, list[str]] | None = None,
) -> dict[str, Any]:
    """One hit as JSON.

    ``id`` and ``url`` are always present, even when empty: they are the two
    details without which nobody gets back to the material, and an absent key
    is easier to overlook than an empty one. ``duplicate_ids`` follows the same
    rule -- always there, usually empty.

    Args:
        hit: the hit.
        aliases: short name to property, deciding the keys under ``fields``.
        folded: ``{kept_id: [dropped_ids]}`` from ``dedupe.deduplicate``.
    """
    fields: dict[str, list[str]] = {}
    for short_name, prop in aliases.items():
        labels = hit.labels(prop)
        if labels:
            fields[short_name] = labels

    return {
        "id": hit.id,
        "title": hit.title,
        "url": hit.url,
        "description": hit.description,
        "source_url": hit.source_url,
        "mimetype": hit.mimetype,
        "mediatype": hit.mediatype,
        "fields": fields,
        # ``None`` on an original. A listing or a collection-scoped search hands
        # out reference ids; this is the record behind one -- and the id a
        # write goes to.
        "original_id": hit.original_id,
        # The records folded into this one. Empty in the normal case; non-empty
        # means the repository holds further nodes for the same source address.
        "duplicate_ids": list((folded or {}).get(hit.id, [])),
    }


def _facet_values(facet: Facet) -> list[dict[str, Any]]:
    return [{"value": v.value, "count": v.count} for v in facet.values]


def _unresolved_as_dict(
    item: UnresolvedFilter, by_property: dict[str, str]
) -> dict[str, Any]:
    """Report the field back in the caller's own words.

    The search layer reports the property (``ccm:taxonid``) because that is what
    it sent. But the caller wrote ``subject="Biologie"``, and answering in a
    vocabulary they did not use forces them to resolve the aliases backwards.
    For a language model that is the difference between correcting its query and
    not knowing which of its fields was meant.

    A property without a short name stays as it is -- that is what the caller
    used then, too.
    """
    return {
        "field": by_property.get(item.field, item.field),
        "value": item.value,
        "suggestions": list(item.suggestions),
    }


def result_as_dict(
    result: SearchResult,
    *,
    query: dict[str, Any],
    aliases: dict[str, str],
    folded: dict[str, list[str]] | None = None,
) -> dict[str, Any]:
    """A whole search result as JSON.

    ``query`` is echoed back deliberately. Without it a caller cannot tell which
    question this answer belongs to -- and a language model summarising several
    searches at once will attribute the wrong one.
    """
    by_property = {prop: short for short, prop in aliases.items()}

    facets: dict[str, list[dict[str, Any]]] = {}
    for facet in result.facets:
        name = by_property.get(facet.property, facet.property)
        facets[name] = _facet_values(facet)

    return {
        "query": query,
        "total": result.total,
        # True means: there are at least this many, possibly more. A caller
        # reporting "211 hits" from a lower bound states a number as fact that
        # is not one.
        "total_is_lower_bound": result.total_is_lower_bound,
        "returned": len(result.hits),
        # How many records were folded into another. Not a count of what the
        # repository holds -- a count of what this answer left out on purpose.
        "duplicates_removed": sum(len(v) for v in (folded or {}).values()),
        "hits": [hit_as_dict(h, aliases, folded) for h in result.hits],
        "facets": facets,
        # Non-empty means the result is BROADER than asked for.
        "unresolved": [_unresolved_as_dict(u, by_property) for u in result.unresolved],
        "ignored": list(result.ignored),
        "warnings": list(result.warnings),
        "suggestions": list(result.suggestions),
    }
