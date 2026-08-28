"""Collapsing hits that are the same material seen more than once.

edu-sharing creates a separate node each time the same web page is imported.
Those nodes carry the same source address and differ only in the technical name
-- edu-sharing appends " - 2", " - 3" on a name collision.

Measured against staging on 2026-08-27: among 50 hits each for "Photosynthese"
and "Bruchrechnung", one pair with an identical source address. wlo-mcp-sc
measured eight nodes sharing one Wikipedia address on 2026-08-09. The rate is
low; the damage per occurrence is not. Whoever reads the list -- a person as
much as a language model -- takes two entries for two pieces of material.

**The source address, not the title.** Two genuinely different materials may
share a title, and measured they do. And not ``ccm:original`` either: measured
in wlo-mcp-sc, the duplicates there each pointed at themselves, so that rule
collapses nothing.

Nothing is hidden: the kept hit carries the ids of the ones folded into it.
"""

from __future__ import annotations

from ..results import SearchHit

__all__ = ["deduplicate"]


def deduplicate(
    hits: list[SearchHit],
) -> tuple[list[SearchHit], dict[str, list[str]]]:
    """Collapse hits sharing a source address.

    The **first** hit of a group wins. By the time this runs the order is
    already final -- the best-scored one under ``rerank`` -- so keeping a later
    one would throw away the better ranking.

    A hit without a source address is never a duplicate of anything. Measured,
    roughly one hit in fifty has none, and folding those together would collapse
    unrelated material into a single entry.

    Args:
        hits: the hits in their final order.

    Returns:
        ``(kept, folded)`` -- the surviving hits, and ``{kept_id: [dropped_ids]}``
        for those that were folded into another. ``folded`` is empty when
        nothing was collapsed.
    """
    kept: list[SearchHit] = []
    first_with_url: dict[str, str] = {}
    folded: dict[str, list[str]] = {}

    for hit in hits:
        source = (hit.source_url or "").strip()
        if not source:
            kept.append(hit)
            continue

        winner = first_with_url.get(source)
        if winner is None:
            first_with_url[source] = hit.id
            kept.append(hit)
            continue

        # A hit without an id cannot be referenced later, so it is kept rather
        # than folded away into a group nobody can trace back.
        if not hit.id:
            kept.append(hit)
            continue
        folded.setdefault(winner, []).append(hit.id)

    return kept, folded
