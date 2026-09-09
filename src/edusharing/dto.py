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

from collections.abc import Sequence
from typing import Any

__all__ = [
    "bare_id",
    "first",
    "node_id_of",
    "page_cut",
    "page_total",
    "title_of",
    "render_url",
    "stored_title_of",
]


def first(value: Any) -> str | None:
    """The first value of a property, or ``None``.

    edu-sharing returns property values as lists, even single ones. **Only
    absence and the empty list are not values**: ``[""]`` gives ``""``, a bare
    ``0`` gives ``"0"``, and only ``None`` and ``[]`` give ``None``.

    The bare case counted as not set until 2026-09-08 (audit COR-9). No
    measured failure came of it: every call site reads ``properties.get(...)``
    and edu-sharing sends lists, so the scalar branch is a safety net that in
    practice never carried a bare ``0``. What was wrong is that the net had a
    different rule from the one ``flows/serialize.py`` states for the same
    question -- "``0`` and ``False`` are values; only absence and an empty
    list are not" -- and a safety net that disagrees with the rule it backs up
    is the wrong shape for the day it does catch something.

    Callers that want ``""`` for a missing value write ``first(…) or ""``.
    Inside a list nothing is skipped, so a JSON ``null`` there comes back as
    the string ``"None"`` -- edu-sharing has not been seen to send one, and
    inventing a rule for it would hide it if it ever did.
    """
    if isinstance(value, list):
        return str(value[0]) if value else None
    return None if value is None else str(value)


def node_id_of(raw: dict[str, Any]) -> str:
    """The node id from a record's ``ref``, or ``""``.

    Never ``None``: this value goes into URLs and routes, where a ``None``
    surfaces far from where it was lost.
    """
    return str((raw.get("ref") or {}).get("id") or "")


def title_of(raw: dict[str, Any]) -> str:
    """The one title of a node record.

    Four objects used to answer this differently: a hit fell from ``title``
    straight to ``cm:name``, a node stopped at ``cclom:title``, a skill went
    ``cclom:title`` then ``cm:name``, the registry ``cclom:title`` then
    ``cm:title``. The same record could therefore arrive as
    "arbeitsblatt.pdf" in a search and as "Bruchrechnung" as a node (audit
    MNT-1, 2026-09-03).

    The chain, most deliberate first: what the API itself displays, the LOM
    title an editor fills in, Alfresco's own title, and last the file name --
    a name beats an empty string, but every stated title beats the name.
    """
    props = raw.get("properties") or {}
    return str(
        raw.get("title")
        or first(props.get("cclom:title"))
        or first(props.get("cm:title"))
        or first(props.get("cm:name"))
        or ""
    )


def stored_title_of(raw: dict[str, Any]) -> str:
    """The title a record actually carries -- without the file-name fallback.

    The sibling of ``title_of`` and the one to use when **writing**: a call
    that only changes a description must preserve the title, and preserving a
    fallback would store it. Measured on a collection without a title:
    ``title_of`` reads its ``cm:name``, and an update of the description alone
    then wrote that name into ``cm:title`` -- metadata nobody asked for
    (review 2026-09-08).
    """
    props = raw.get("properties") or {}
    return str(
        raw.get("title")
        or first(props.get("cclom:title"))
        or first(props.get("cm:title"))
        or ""
    )


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

    A stated ``0`` is an answer, not a missing one, and is returned as such.
    The eight call sites this replaced all wrote ``or``, which handed a caller
    with a non-zero ``default`` that default for an empty listing (review
    2026-09-08).
    """
    total = (response.get("pagination") or {}).get("total")
    # ``""`` steht neben ``None`` fuer "nicht gesagt": ``int("")`` wuerde
    # werfen, und eine Auflistung an einer leeren Zahl scheitern zu lassen
    # waere schlechter als die Vorgabe zu nehmen. Eine genannte ``0`` ist
    # davon nicht betroffen.
    return default if total in (None, "") else int(total)


def page_cut(records: Sequence[Any], response: dict[str, Any], limit: int) -> bool:
    """Whether a page fetched with ``maxItems=limit + 1`` is missing some.

    Ask for one record over the cap and the page answers for itself: ``limit +
    1`` arriving means there are more than ``limit``, and fewer arriving means
    there are not — the question needs no total. Measured against edu-sharing
    11.0 on 2026-09-09, both listing endpoints honour ``maxItems`` exactly: a
    folder of 205 children answers ``maxItems=201`` with 201 records, and a
    collection of six sub-collections answers ``maxItems=5`` with five and
    ``maxItems=7`` with six.

    The stated total still counts, because a repository that says 250 while
    handing over 201 has answered the question itself. Neither half suffices
    alone, and both blind spots were measured: reading the total alone made the
    answer ``False`` exactly where nothing was stated — the shape ``page_total``
    names for ``ngsearch`` — and believed a repository that states the *page
    size* as its total; counting records alone cannot see past what it asked
    for.

    ``default=-1`` says “nothing stated” rather than “nought”, but here the two
    are the same answer: both are below any ``limit``, so the record count
    carries the decision either way. Replacing it with ``0`` changes no
    outcome — measured by mutation on 2026-09-09, after this docstring first
    claimed the choice was load-bearing. It is kept because it says what it
    means, not because it decides anything.

    Args:
        records: what the response actually carried, unsliced.
        response: the listing response, for its stated total.
        limit: the cap the caller promises its own reader — **not** the
            ``maxItems`` that was sent, which is one higher.
    """
    return len(records) > limit or page_total(response, default=-1) > limit
