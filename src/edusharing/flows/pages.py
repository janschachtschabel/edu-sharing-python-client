"""Curated pages as flows: read one out, find the collections that have one.

The flow-level counterpart of ``edusharing.pages`` -- plain dictionaries, ready
for JSON, for callers that want the page rather than the objects behind it.

Two measurements shape both flows (staging, 2026-08-28):

* **``ccm:page_config_ref`` cannot be filtered on.** ``400
  DAOValidationException: Widget ccm:page_config_ref was not found in the mds``.
  A page is recognised from the *answer*, never asked for in the question.
  Because the collection search now returns properties, that costs one request
  instead of one per candidate.
* **Leg B of the collection search has a fixed projection** and stays
  property-less. Hits only it found cannot be judged -- so ``find_pages``
  reports how many hits it could judge at all. Without that number, "no page
  found" reads as a statement about the repository when it was one about the
  projection.

**The same call does not return the same hits.** Measured six times on
2026-08-28 with the term "Deutsch": ``find_pages`` answered three different hit
sets, and ``checked`` swung between 50 and 100. Both legs of the collection
search are involved and neither is a superset of the other, so a caller must
treat one run as a sample, not as the catalogue -- and must not conclude from
one empty answer that the repository holds no pages.

Both flows report an empty page as an ordinary answer, never as a failure.
Measured: the collection ``Hexen`` carries a page whose single variant has a
readable document with an empty swimlane list. "Has a page" and "has content"
are different questions.

``resolve_widgets`` reads the widget nodes and reports what they hold. It does
**not** run their saved searches: those carry ``virtual:`` fields the metadata
set does not know, and guessing at them would produce a result nobody asked
for. The fixed list (``sortedNodeIds``) needs no guessing and is resolved.
"""

from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING, Any

from ..errors import EduSharingError
from ..pages import PAGE_REF, CuratedPage, PageVariant

if TYPE_CHECKING:  # pragma: no cover
    from ..repository import AsyncRepository

__all__ = ["DEFAULT_MAX_WIDGETS", "find_pages", "page"]

#: How many widget nodes ``resolve_widgets`` may read before it stops and says
#: so. The measured page carries ten; two dozen is headroom that still bounds a
#: single call to a size a caller can predict.
DEFAULT_MAX_WIDGETS = 24

_WIDGET_CONFIG = "ccm:widget_config"


async def page(
    repo: AsyncRepository,
    collection_id: str,
    *,
    variant: str | None = None,
    resolve_widgets: bool = False,
    max_widgets: int = DEFAULT_MAX_WIDGETS,
) -> dict[str, Any]:
    """The page a collection renders, as a plain dictionary.

    Three requests: the collection, its page folder, the folder's children.
    ``resolve_widgets`` adds one per distinct widget node, capped.

    A collection **without** a page is not an error -- most collections have
    none. The answer comes back empty with ``reason`` saying why.

    Args:
        repo: the connection.
        collection_id: the collection, not the page folder.
        variant: a specific variant. Defaults to the one that renders.
        resolve_widgets: read each widget node and report what it holds.
        max_widgets: cap for the above. ``truncated`` says whether it bit.

    Raises:
        ValueError: on ``max_widgets`` below one.
        NotFoundError: when no node carries ``collection_id``.

    Returns:
        ``{collection, folder_id, rendered, variants, swimlanes, node_ids,
        resolved, truncated, reason}``. ``variants`` lists every variant, not
        only the rendered one -- otherwise a caller cannot tell what it could
        switch to.
    """
    if max_widgets < 1:
        raise ValueError(
            f"max_widgets={max_widgets!r} would read no widget at all -- pass "
            "resolve_widgets=False to say that on purpose."
        )
    node = await repo.node(collection_id)
    collection = {"id": node.id, "title": node.title, "url": node.url}
    curated = await node.page.get()
    if curated is None:
        return _empty(collection, reason=(
            f"{node.id!r} carries no {PAGE_REF} -- it has no curated page. "
            "Most collections have none."))

    chosen, reason = _choose(curated, variant)
    if chosen is None:
        return _empty(collection, folder_id=curated.folder_id,
                      variants=curated.variants, reason=reason)

    lanes = [
        {"heading": lane.heading, "type": lane.type,
         "items": [{"widget": item.widget, "node_id": item.node_id}
                   for item in lane.items]}
        for lane in chosen.swimlanes
    ]
    truncated = False
    if resolve_widgets:
        truncated = await _resolve(repo, lanes, chosen.node_ids, max_widgets)

    return {
        "collection": collection,
        "folder_id": curated.folder_id,
        "rendered": {"id": chosen.id, "title": chosen.title,
                     "by_position": curated.by_position},
        "variants": [_variant(v) for v in curated.variants],
        "swimlanes": lanes,
        "node_ids": list(chosen.node_ids),
        "resolved": resolve_widgets,
        "truncated": truncated,
        "reason": reason,
    }


async def find_pages(
    repo: AsyncRepository, text: str = "", *, limit: int = 25
) -> dict[str, Any]:
    """Which collections carry a curated page.

    One request. A subset of ``find_collections``: every curated page is a
    collection, but few collections have one.

    ``checked`` is not decoration. Hits that only the property-less leg of the
    collection search found cannot be judged, and a caller that reads an empty
    ``hits`` without it concludes the repository has no pages.

    Args:
        repo: the connection.
        text: the search term. Empty lists what the search returns unfiltered.
        limit: how many collection hits to look at.

    Raises:
        ValueError: on a limit below one.

    Returns:
        ``{query, hits, checked, total, reason}``. ``total`` is the collection
        search's own total -- how many collections matched, not how many of
        them carry a page.
    """
    if limit < 1:
        raise ValueError(
            f"limit={limit!r} would look at no collection at all, and the "
            "answer would say 'no page found' about a search never run."
        )
    found = await repo.find_collections(text, limit=limit)
    checked = [hit for hit in found.hits if hit.properties()]
    hits = [
        {"id": hit.id, "title": hit.title, "url": hit.url,
         "folder_id": _bare(hit.properties()[PAGE_REF][0])}
        for hit in checked
        if hit.properties().get(PAGE_REF)
    ]
    blind = len(found.hits) - len(checked)
    return {
        "query": text,
        "hits": hits,
        "checked": len(checked),
        "total": found.total,
        "reason": "" if not blind else (
            f"{blind} of {len(found.hits)} hits carried no properties and could "
            "not be judged -- one leg of the collection search has a fixed "
            "projection. Read those nodes by id to be sure."),
    }


# --- Internals ------------------------------------------------------------


def _bare(ref: str) -> str:
    return ref.rsplit("/", 1)[-1] if ref else ""


def _variant(variant: PageVariant) -> dict[str, Any]:
    return {
        "id": variant.id,
        "title": variant.title,
        "is_template": variant.is_template,
        "target_group": variant.target_group,
        "educational_contexts": list(variant.educational_contexts),
        "intention": variant.intention,
        "education_levels": list(variant.education_levels),
        "readable": variant.readable,
    }


def _choose(curated: CuratedPage,
            variant: str | None) -> tuple[PageVariant | None, str]:
    """The variant to show, and why there is none."""
    if variant is None:
        if curated.rendered is None:
            return None, ("this page's folder holds no variants -- there is "
                          "nothing to render.")
        return curated.rendered, ""
    chosen = curated.variant(variant)
    if chosen is None:
        known = ", ".join(v.id for v in curated.variants) or "none"
        return None, f"{variant!r} is not a variant of this page (known: {known})."
    return chosen, ""


def _empty(collection: dict[str, Any], *, folder_id: str = "",
           variants: tuple[PageVariant, ...] = (), reason: str) -> dict[str, Any]:
    return {
        "collection": collection,
        "folder_id": folder_id,
        "rendered": None,
        "variants": [_variant(v) for v in variants],
        "swimlanes": [],
        "node_ids": [],
        "resolved": False,
        "truncated": False,
        "reason": reason,
    }


async def _resolve(repo: AsyncRepository, lanes: list[dict[str, Any]],
                   node_ids: tuple[str, ...], cap: int) -> bool:
    """Read the widget nodes and fold what they hold into the lanes.

    Returns whether the cap bit. A widget that has gone missing is reported on
    its item rather than raised: an index that outlives its nodes is the
    ordinary case here, and one dead widget must not cost the whole page.
    """
    wanted = list(node_ids)[:cap]

    async def one(node_id: str) -> tuple[str, dict[str, Any]]:
        try:
            node = await repo.nodes.get(node_id)
        except EduSharingError as exc:
            return node_id, {"unreachable": f"{type(exc).__name__}: {exc}"}
        return node_id, _widget(node.get(_WIDGET_CONFIG))

    resolved = dict(await asyncio.gather(*(one(i) for i in wanted)))
    for lane in lanes:
        for item in lane["items"]:
            item.update(resolved.get(item["node_id"], {}))
    return len(node_ids) > cap


def _widget(raw: str | None) -> dict[str, Any]:
    """What one widget node declares -- its list, or its unexecuted search.

    Like every page-builder document this one is validated by nobody, so an
    unreadable value is reported, never raised.
    """
    if raw is None:
        return {}
    try:
        doc = json.loads(raw)
    except (ValueError, TypeError):
        return {"unreadable": f"{_WIDGET_CONFIG} is not valid JSON"}
    if not isinstance(doc, dict):
        return {"unreadable": f"{_WIDGET_CONFIG} is not an object"}

    out: dict[str, Any] = {}
    if isinstance(doc.get("description"), str) and doc["description"]:
        out["description"] = doc["description"]
    listed = doc.get("sortedNodeIds")
    if isinstance(listed, list):
        out["node_ids"] = [_bare(str(i)) for i in listed if i]
    if "searchText" in doc or "propertyFilters" in doc:
        filters = doc.get("propertyFilters")
        out["search"] = {
            "text": doc.get("searchText") if isinstance(doc.get("searchText"), str) else "",
            "filters": filters if isinstance(filters, dict) else {},
        }
    return out
