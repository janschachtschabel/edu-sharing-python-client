"""``text`` -- the full text of one material, and why there is none.

Three sources, asked in this order and only as far as needed:

1. **The repository's own text** (``/textContent``). Present for the large
   majority of records -- the MCP counted 29 of 32 sampled live records on
   2026-07-28 -- for linked pages as well as attached files.
2. **The file itself**, when the record carries a ``text/*`` upload. Measured
   on 2026-08-27 by uploading one sentence in five formats: ``/textContent``
   returns **nothing** for ``text/markdown`` and ``application/json`` although
   the file has text (see ``NodeContent.text``). A skill's ``SKILL.md`` is
   exactly that case. Bytes of a binary file are not text, so a PDF without an
   extract is not downloaded.
3. **The linked page**, for material that is merely linked (``ccm:wwwurl``),
   through the text-extraction service -- and only when the caller passes one:
   the library knows no service address (E4), and the address of a page is
   not something to fetch behind a caller's back.

No text is a normal outcome, not an error. ``reason`` names which of the six
causes it was, so "we would not fetch that" never looks like "the page was
empty" -- and a model told "there is no text" can say so instead of inventing
one. Example 15 did all of this by hand in 215 lines; the MCP offers it as
``get_wlo_content_text``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..agent.format import cap_text
from ..errors import EduSharingError, NotFoundError, PermissionDeniedError

if TYPE_CHECKING:  # pragma: no cover
    from ..extraction import TextExtraction
    from ..repository import AsyncRepository

__all__ = ["text", "DEFAULT_MAX_CHARS"]

#: The same ceiling the MCP settled on (2026-08-20): an instruction or a
#: worksheet must arrive whole, and real articles run to ~120 000 characters.
DEFAULT_MAX_CHARS = 200_000


async def text(
    repo: AsyncRepository,
    node_id: str,
    *,
    extraction: TextExtraction | None = None,
    max_chars: int = DEFAULT_MAX_CHARS,
) -> dict[str, Any]:
    """The text of one material -- repository first, then the file, then the page.

    Args:
        repo: the connection.
        node_id: the material. A reference id from a collection listing works
            as well: the text is read from the node itself, which for a
            reference is the same content.
        extraction: the text-extraction client for the linked-page fallback.
            ``None`` means the page is not fetched, and the answer says so.
        max_chars: cut longer text at a word boundary; ``truncated`` says when,
            ``char_count`` says how long it really was.

    Returns:
        ``{id, title, text, source, source_url, char_count, truncated, reason,
        detail}``. ``source`` is ``repository``, ``download``, ``extraction`` or
        ``none``. With ``none``, ``reason`` is one of ``node_not_found``,
        ``access_denied``, ``no_text_no_url``, ``no_extraction_service`` or
        ``extraction_failed``, and ``detail`` carries the service's or the
        error's own words. ``source_url`` is the linked page whenever there is
        one, so a caller without a service can still decide to fetch it.

    Raises:
        Nothing of its own. A refused or missing node is reported in
        ``reason`` -- the question was "is there text", and "no, because" is
        the answer.
    """
    answer: dict[str, Any] = {
        "id": node_id, "title": None, "text": "", "source": "none",
        "source_url": None, "char_count": 0, "truncated": False,
        "reason": "", "detail": "",
    }
    try:
        node = await repo.nodes.get(node_id)
    except NotFoundError as exc:
        return {**answer, "reason": "node_not_found", "detail": str(exc)}
    except PermissionDeniedError as exc:
        return {**answer, "reason": "access_denied", "detail": str(exc)}
    answer["title"] = node.title or None

    stored = await node.content.text()
    if stored:
        return _capped(answer, stored, "repository", max_chars)

    if node.content.has_content and (node.content.mimetype or "").startswith("text/"):
        decoded = (await node.content.download()).decode("utf-8", errors="replace")
        if decoded:
            return _capped(answer, decoded, "download", max_chars)

    linked = node.get("ccm:wwwurl")
    if not linked:
        return {**answer, "reason": "no_text_no_url"}
    answer["source_url"] = linked
    if extraction is None:
        return {**answer, "reason": "no_extraction_service"}

    try:
        got = await extraction.text_of(linked, max_chars=max_chars)
    except EduSharingError as exc:
        # A broken service is not "the page has no text", but for the caller
        # both are "no text, and this is why" -- the words tell them apart.
        return {**answer, "reason": "extraction_failed", "detail": str(exc)}
    if not got.text:
        detail = f"{got.reason}: {got.detail}" if got.detail else got.reason
        return {**answer, "reason": "extraction_failed", "detail": detail}
    return {
        **answer, "text": got.text, "source": "extraction",
        "char_count": got.char_count, "truncated": got.truncated,
    }


def _capped(answer: dict[str, Any], full: str, source: str, max_chars: int) -> dict[str, Any]:
    """Cut at a word boundary, without a marker inside the text: a caller may
    process it further, and the flag says what happened."""
    shown = cap_text(full, max_chars, marker="")
    return {
        **answer, "text": shown, "source": source,
        "char_count": len(full), "truncated": len(shown) < len(full),
    }
