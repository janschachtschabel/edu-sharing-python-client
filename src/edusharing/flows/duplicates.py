"""Is there already a record for this address?

``ccm:wwwurl`` identifies linked material exactly, so a second record for the
same address is a duplicate by definition. Measured on 2026-09-02 against
staging: with ``mds_oeh`` the property is a search criterion (one hit, exactly
equal); ``-default-`` refuses it with a ``ValidationError`` -- whether the
check can run at all is a property of the metadata set, and the caller of
``add_material`` is told when it could not.

Two things make this stricter than the search it is built on, both measured by
the MCP (``services/write/duplicates.ts``): the search answers with neighbours
as well as the exact hit, so every hit's own ``ccm:wwwurl`` is compared; and
the comparison ignores case and nothing else -- a trailing slash can
distinguish two real pages, and a wrong "already exists" blocks a legitimate
record.

One limit, also measured (staging, 2026-09-02): the check sees what the search
index sees, and the index trails the node store. A record created a moment ago
was findable by its address after 5.3 seconds, not before. Two creations for
the same address within that window therefore both succeed; a caller that
batches imports should de-duplicate its own input first.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..errors import ConflictError, ValidationError

if TYPE_CHECKING:  # pragma: no cover
    from ..repository import AsyncRepository

__all__ = ["find_by_url", "check_before_create", "DUPLICATE_SCAN_LIMIT"]

#: Hits compared per check. The exact address ranks first when it exists; the
#: rest of the page is neighbours, and twenty is plenty of room for them.
DUPLICATE_SCAN_LIMIT = 20


async def find_by_url(repo: AsyncRepository, url: str) -> dict[str, Any] | None:
    """The record already carrying this address, or ``None``.

    Returns:
        ``{id, title, url}`` -- ``url`` as stored, which may differ from the
        input in case.

    Raises:
        ValidationError: when the metadata set does not accept ``ccm:wwwurl``
            as a criterion. Not swallowed: the caller decides whether a check
            that cannot run is a warning or a refusal.
    """
    wanted = url.strip().lower()
    if not wanted:
        return None
    result = await repo.search(filters={"ccm:wwwurl": url.strip()}, limit=DUPLICATE_SCAN_LIMIT)
    for hit in result.hits:
        stored = (hit.source_url or "").strip()
        if stored and stored.lower() == wanted:
            return {"id": hit.id, "title": hit.title, "url": stored}
    return None


async def check_before_create(
    repo: AsyncRepository, url: str, if_exists: str
) -> tuple[dict[str, Any] | None, list[str]]:
    """Apply ``if_exists`` to the address a caller is about to create a record for.

    Returns:
        ``(existing, warnings)``. ``existing`` is the record to hand back
        instead of creating one, or ``None``; ``warnings`` says when the check
        could not run. A default check may be dropped -- said, not silently --
        an explicit ``"raise"`` may not.

    Raises:
        ValidationError: for an ``if_exists`` value that is not ``return``,
            ``raise`` or ``create``.
        ConflictError: with ``"raise"``, when the record exists -- or when the
            metadata set cannot answer the question at all.
    """
    if if_exists not in ("return", "raise", "create"):
        raise ValidationError(
            f"if_exists={if_exists!r} is not one of return, raise, create."
        )
    if if_exists == "create":
        return None, []
    try:
        existing = await find_by_url(repo, url)
    except ValidationError as exc:
        if if_exists == "raise":
            raise ConflictError(
                f"Cannot tell whether {url!r} already exists: {exc}"
            ) from exc
        return None, [f"duplicate check skipped: {exc}"]
    if existing is not None and if_exists == "raise":
        raise ConflictError(
            f"{url!r} already exists as {existing['id']} ({existing['title']!r})."
        )
    return existing, []
