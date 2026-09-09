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
the comparison normalises **by component** -- scheme and host are
case-insensitive as RFC 3986 says, path and query are not. A trailing slash
distinguishes two real pages, and so does ``/A`` from ``/a``; a wrong
"already exists" blocks a legitimate record, and with ``if_exists="return"``
hands back the wrong one. Until 2026-09-09 the whole address was lowered
(F10).

One limit, also measured (staging, 2026-09-02): the check sees what the search
index sees, and the index trails the node store. A record created a moment ago
was findable by its address after 5.3 seconds, not before. Two creations for
the same address within that window therefore both succeed; a caller that
batches imports should de-duplicate its own input first.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from urllib.parse import urlsplit, urlunsplit

from ..errors import ConflictError, ValidationError

if TYPE_CHECKING:  # pragma: no cover
    from ..repository import AsyncRepository

__all__ = ["find_by_url", "check_before_create", "validate_if_exists", "DUPLICATE_SCAN_LIMIT"]

#: Hits compared per check. The exact address ranks first when it exists; the
#: rest of the page is neighbours, and twenty is plenty of room for them.
DUPLICATE_SCAN_LIMIT = 20
_NOT_A_CRITERION = (
    "{url!r} could not be sent as a ccm:wwwurl criterion -- the search takes only "
    "http(s) addresses -- so the duplicate check did not run."
)


def _comparable(url: str) -> str | None:
    """The address as a comparison key -- scheme and authority lowered, the
    rest left exactly as it is -- or ``None`` when it cannot be read at all.

    Until 2026-09-09 the **whole** address was lowered, path and query
    included, and the module said so ("ignores case and nothing else"). It was
    a deliberate choice taken over from the MCP, and it was wrong about what a
    URL means: RFC 3986 makes scheme and host case-insensitive and the path
    character-exact. Measured, a record with ``https://example.test/A`` was
    returned as the duplicate of ``https://example.test/a`` -- and with
    ``if_exists="return"`` an application then hands back the wrong existing
    record instead of creating the one that was asked for (F10).

    Anything that is not an absolute address is compared as given: there is
    nothing to normalise, and guessing would be the same mistake again.

    ``urlsplit`` raises on some addresses -- ``https://[broken`` gives
    ``ValueError: Invalid IPv6 URL``. A stored ``ccm:wwwurl`` comes from
    whoever created the record and need not be syntactically valid, and
    measured 2026-09-09 such a neighbour ended the whole check with an
    exception from the standard library (R09). The old raw string comparison
    was wrong about paths but could not fail here; a fix that introduces a new
    kind of failure is not finished.
    """
    try:
        teile = urlsplit(url.strip())
    except ValueError:
        return None
    if not teile.scheme or not teile.netloc:
        return url.strip()
    return urlunsplit((teile.scheme.lower(), teile.netloc.lower(),
                       teile.path, teile.query, teile.fragment))


async def find_by_url(repo: AsyncRepository, url: str) -> dict[str, Any] | None:
    """The record already carrying this address, or ``None``.

    Returns:
        ``{id, title, url}`` -- ``url`` as stored, which may differ from the
        input in the case of its scheme and host. Compared is ``_comparable``:
        those two are case-insensitive, path and query are not.

    A stored address that cannot be read is **skipped**, not complained
    about: it is not the same address as a readable one, so it is not the
    duplicate being looked for. The address the *caller* passes is a different
    matter -- there an unreadable value is a ``ValidationError``, because
    nobody else can fix it.

    Raises:
        ValidationError: when the metadata set does not accept ``ccm:wwwurl``
            as a criterion -- or when the search could not take this value
            as one (it passes only ``http(s)://`` addresses through; anything
            else lands in ``unresolved`` and is not sent) -- or when ``url``
            itself cannot be read as an address. Not swallowed: the caller
            decides whether a check that cannot run is a warning or a refusal.
    """
    if not url.strip():
        return None
    wanted = _comparable(url)
    if wanted is None:
        raise ValidationError(
            f"{url!r} cannot be read as an address, so it cannot be compared "
            "against anything -- the duplicate check did not run."
        )
    if not wanted.lower().startswith(("http://", "https://")):
        # The search takes only http(s) addresses as a criterion. Asking anyway
        # would cost a vocabulary lookup and an unfiltered search for the same
        # answer; the check below stays as the second line of defence.
        raise ValidationError(_NOT_A_CRITERION.format(url=url))
    result = await repo.search(filters={"ccm:wwwurl": url.strip()}, limit=DUPLICATE_SCAN_LIMIT)
    if result.unresolved:
        # Not sent means not filtered: the hits below would be neighbours of
        # nothing, and "no duplicate" a guess.
        raise ValidationError(_NOT_A_CRITERION.format(url=url))
    for hit in result.hits:
        stored = (hit.source_url or "").strip()
        if stored and _comparable(stored) == wanted:  # None never equals it
            return {"id": hit.id, "title": hit.title, "url": stored}
    return None


def validate_if_exists(if_exists: str) -> None:
    """``return``, ``raise`` or ``create`` -- anything else is a misspelled wish."""
    if if_exists not in ("return", "raise", "create"):
        raise ValidationError(
            f"if_exists={if_exists!r} is not one of return, raise, create."
        )


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
    validate_if_exists(if_exists)
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
