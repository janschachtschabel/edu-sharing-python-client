"""One reading of a node record.

edu-sharing answers with one shape — ``{"ref": {"id": …}, "properties": {…},
"title": …}`` — and this library used to read it five different ways. Four
title chains, three ``_first`` (one of them answering ``""`` where the others
answered ``None``), two ``_bare``, the viewer URL built at five places, the
reference id read at twelve, ``pagination.total`` at eight. The same record
could therefore show a different title depending on which object it arrived
as, and renaming one field meant hunting it through a dozen files (audit
MNT-1, 2026-09-03).

These functions are that one reading. They are deliberately dull: no
requests, no classes, no state — just what a raw record means. Everything
that turns a record into an object of this library goes through here.
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "bare_id",
    "first",
    "node_id_of",
    "page_total",
    "render_url",
]


def first(value: Any) -> str | None:
    """The first value of a property, or ``None``.

    edu-sharing returns property values as lists, even single ones. In a list
    what counts is that the list is there, not what its first value is worth:
    ``[""]`` gives ``""``, only ``[]`` gives ``None``. A bare falsy value —
    ``""``, ``0``, ``None`` — counts as not set. Callers that want one answer
    for both write ``first(…) or ""``.
    """
    if isinstance(value, list):
        return str(value[0]) if value else None
    return str(value) if value else None


def node_id_of(raw: dict[str, Any]) -> str:
    """The node id from a record's ``ref``, or ``""``.

    Never ``None``: this value goes into URLs and routes, where a ``None``
    surfaces far from where it was lost.
    """
    return str((raw.get("ref") or {}).get("id") or "")


def bare_id(ref: str) -> str:
    """A node id without its store prefix.

    The page builder writes full store refs (``workspace://SpacesStore/<uuid>``)
    everywhere; every REST route in this library takes the bare id. Measured
    28/28 documents store the ref form, so this is the rule, not a fallback.
    """
    return ref.rsplit("/", 1)[-1] if ref else ""


def render_url(repository_url: str, node_id: str) -> str:
    """The viewer URL for a node — what you hand on to someone.

    Empty for an empty id: an address pointing at nothing is not an address,
    and the five places that built this string did not all agree on that.
    """
    return f"{repository_url}/components/render/{node_id}" if node_id else ""


def page_total(response: dict[str, Any], default: int = 0) -> int:
    """``pagination.total`` from a listing response.

    ``default`` for a response that carries no total: ``ngsearch`` answers
    with ``pagination: null``, and what should count instead is the caller's
    decision — usually 0, sometimes the number of records in hand.
    """
    total = (response.get("pagination") or {}).get("total")
    return int(total) if total else default
