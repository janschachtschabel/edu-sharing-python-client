"""Error types, and mapping an HTTP response onto one of them.

On failure edu-sharing answers with three fields::

    {"error": "org.edu_sharing.restservices.DAOMissingException",
     "message": "InvalidNodeRefException: Node does not exist: ...",
     "stacktrace": "\\njava.lang.Exception: ...\\n\\tat org.edu_sharing...."}

``error`` carries the Java class name and is the more precise category -- the
HTTP status alone is not enough, as ``ServerError`` below shows.

The ``stacktrace`` stays reachable as an attribute but never appears in
``str()``: it holds internal class paths and line numbers that have no place in
a message an application shows its users.
"""

from __future__ import annotations

import json

__all__ = [
    "at_least",
    "details_withheld",
    "EduSharingError",
    "TransportError",
    "AuthenticationError",
    "PermissionDeniedError",
    "NotFoundError",
    "ValidationError",
    "ContentTooLargeError",
    "ConflictError",
    "RateLimitedError",
    "ServerError",
    "SilentDropError",
    "error_class_for",
    "error_from_response",
]


class EduSharingError(Exception):
    """Base of every error in this library.

    Catch this type if you do not need to tell them apart.

    Attributes:
        status: HTTP status code, or ``None`` when the request never reached
            the server (see ``TransportError``).
        url: the requested URL.
        error_class: the Java class name from the ``error`` field, if the
            response was JSON.
        stacktrace: the Java stack trace. For debugging only -- do not display.
        retry_after: seconds the server asked to be left alone for, from the
            ``Retry-After`` header. Filled for ``RateLimitedError``; ``None``
            everywhere else, including when a 429 named no time.
    """

    def __init__(
        self,
        message: str,
        *,
        status: int | None = None,
        url: str | None = None,
        error_class: str | None = None,
        stacktrace: str | None = None,
        retry_after: float | None = None,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.url = url
        self.error_class = error_class
        self.stacktrace = stacktrace
        self.retry_after = retry_after


class TransportError(EduSharingError):
    """The request never reached the server: timeout, DNS, TLS, connection.

    Kept apart from ``ServerError`` because the difference matters to the
    caller: here it is unclear whether anything happened. A write that runs into
    a timeout may still have been carried out.
    """


class AuthenticationError(EduSharingError):
    """Not signed in, or the credentials are wrong.

    Measured on WLO instances: wrong credentials give ``401`` on EVERY endpoint
    -- there is no fallback to "public read only". A typo in the password
    therefore paralyses the whole application instead of letting it run with
    reduced access.
    """


class PermissionDeniedError(EduSharingError):
    """Signed in, but without the necessary right.

    edu-sharing has two permission layers: the ACL on the node and the tool
    permissions on the account. Both land here.
    """


class NotFoundError(EduSharingError):
    """The node, collection or endpoint does not exist."""


class ValidationError(EduSharingError):
    """The repository rejected the request (``DAOValidationException``).

    Typically: a search criterion the addressed query does not know.
    """


class ConflictError(EduSharingError):
    """The operation collides with the existing state.

    Typically: a name that already exists under the same parent.
    """


class SilentDropError(EduSharingError):
    """The repository reported ``200 OK`` and stored nothing.

    Measured (edu-sharing 11.0, staging, on a throwaway node): a
    ``PUT /metadata`` carrying a property the metadata set does not know answers
    with **200** -- and the value is absent afterwards. The same holds for a
    wholly invented field.

    A status code is therefore no proof of persistence. Without a read-back an
    application reports success for data that no longer exists.

    Attributes:
        dropped: the properties that were missing after reading back.
    """

    def __init__(
        self, message: str, *, dropped: list[str] | None = None, **kwargs: object
    ) -> None:
        super().__init__(message, **kwargs)  # type: ignore[arg-type]
        self.dropped = dropped or []


class ContentTooLargeError(EduSharingError):
    """A download is larger than the caller allowed (``max_bytes``).

    Raised before the request when the repository reports the size
    (``NodeContent.size``), otherwise while the bytes arrive -- either way
    nothing beyond the limit is held in memory (audit SEC-2, 2026-09-06).
    """


class RateLimitedError(EduSharingError):
    """HTTP 429: too many requests for now.

    Unlike a 5xx this says the request was **not** carried out -- the server
    refused it before doing anything -- so even a write may be sent again.
    That is why the retry loops treat it apart from the idempotency rule
    (audit API-2, 2026-09-03).

    ``retry_after`` carries the seconds the server named, in either form
    RFC 9110 allows, or ``None`` when it named none. While that wait is short
    the loops sit it out themselves; when the server asks for longer than
    ``retry.DEFAULT_MAX_RETRY_AFTER`` this error reaches the caller with the
    number on it, because sleeping an hour inside a library call is a hang,
    not a retry.
    """


class ServerError(EduSharingError):
    """A genuine failure on the other side.

    Only those 5xx that on inspection are NOT a disguised authentication or
    permission question -- see ``error_from_response``.
    """


# A guest hitting a protected endpoint gets HTTP 500, not 401. Measured on
# GET /iam/v1/people/-home-/-me-/preferences without credentials:
#   500  {"error": "java.lang.Exception", "message": "Not allowed for guest user"}
# The status is misleading, and the confusion is expensive: as a ServerError the
# transport would retry it -- three times the same request that can never
# succeed, because only the sign-in is missing.
_GUEST_HINT = "not allowed for guest"

# The same disguise for permissions, twice over: /rating/v1/ratings/.../history
# answers 500 NotAnAdminException, and /node/v1/nodes/.../parents answers 500
# AccessDeniedException for foreign material -- while the very same endpoint
# says a proper 403 for a node of one's own. Measured 2026-08-28.
_PERMISSION_HINTS = ("notanadmin", "accessdenied")

# And a missing node: /usage/v1/usages/node/{id}/collections answers 500 for an
# id the node endpoint answers 404 for. Measured 2026-08-28. It matters because
# the search index holds nodes that no longer exist -- 4 of 25 hits, measured on
# staging -- so anything chaining search to a usage lookup meets this, gets it
# retried three times, and never sees the NotFoundError it catches for.
_MISSING_HINT = "node does not exist"

# An instance can withhold the message that the two hints above read. Measured
# 2026-08-28 against redaktion.openeduhub.net, which answers the guest case with
#   {"error": "java.lang.Exception", "message": "Details hidden: ..."}
# where staging answers "Not allowed for guest user". The disguise is then
# undetectable, the error stays a ServerError, and the transport retries it --
# measured 4 requests against production where staging needs 1.
#
# Guessing is not an option: what the server withholds cannot be inferred. What
# can be done is to say so, so nobody puzzles over the same library returning
# different error types against two instances.
_HIDDEN_HINT = "details hidden"

_HIDDEN_NOTE = (
    " -- this instance withholds error messages "
    "(security.logging.displayLevel), so this library could not tell an "
    "authentication or permission problem from a genuine server fault, and "
    "retried accordingly. Raise that setting on the instance, or read the "
    "server's own log."
)


def _parse_body(body: str) -> tuple[str | None, str, str | None]:
    """Split the response body into (error_class, message, stacktrace).

    Falls back to ``(None, "", None)`` when the body is not JSON: a 401 arrives
    empty, and a reverse proxy answers with HTML.
    """
    if not body:
        return None, "", None
    try:
        data = json.loads(body)
    except (ValueError, TypeError):
        return None, "", None
    if not isinstance(data, dict):
        return None, "", None
    return (
        data.get("error") or None,
        str(data.get("message") or ""),
        data.get("stacktrace") or None,
    )


def _short(error_class: str | None) -> str:
    """``org.edu_sharing.restservices.DAOMissingException`` -> ``DAOMissingException``."""
    return error_class.rsplit(".", 1)[-1] if error_class else ""


def error_class_for(
    status: int, error_class: str | None = None, message: str = ""
) -> type[EduSharingError]:
    """Which error type a status stands for.

    The HTTP status is the first hint but not the last: for 5xx the content
    decides whether the server is genuinely broken or whether merely the
    sign-in, respectively a permission, is missing. Separate from
    ``error_from_response`` because the b-api client needs the type without
    the edu-sharing message shape -- it reports under ``message``.
    """
    if status >= 500:
        lowered = message.lower()
        if _GUEST_HINT in lowered:
            return AuthenticationError
        if _MISSING_HINT in lowered:
            return NotFoundError
        if any(h in (error_class or "").lower() for h in _PERMISSION_HINTS):
            return PermissionDeniedError
        return ServerError
    return {
        400: ValidationError,
        401: AuthenticationError,
        403: PermissionDeniedError,
        404: NotFoundError,
        409: ConflictError,
        429: RateLimitedError,
    }.get(status, EduSharingError)


def error_from_response(
    status: int, url: str, body: str, retry_after: float | None = None
) -> EduSharingError:
    """Build the matching error type from a failure response.

    ``retry_after`` comes from the ``Retry-After`` header, already read by
    ``retry.parse_retry_after`` -- this module stays a leaf and does not
    import the retry policy.
    """
    error_class, message, stacktrace = _parse_body(body)
    cls = error_class_for(status, error_class, message)

    parts = [f"HTTP {status}"]
    if error_class:
        parts.append(_short(error_class))
    text = " ".join(parts)
    if message:
        text = f"{text}: {message}"
    if status >= 500 and _HIDDEN_HINT in message.lower():
        text += _HIDDEN_NOTE

    return cls(
        text,
        status=status,
        url=url,
        error_class=error_class,
        stacktrace=stacktrace,
        # Only the 429. RFC 9110 allows ``Retry-After`` on a 503 as well, but
        # honouring it there was never measured and never documented -- and it
        # rewrote the backoff for every 5xx: three pauses of 0.5 to 2 seconds
        # became three of whatever a proxy said, and a long value took the
        # retries away entirely (review 2026-09-08).
        retry_after=retry_after if cls is RateLimitedError else None,
    )


def details_withheld(error: EduSharingError) -> bool:
    """Whether the instance withheld the message this error needed.

    The 5xx classification reads the server's message. An instance that hides
    it (``security.logging.displayLevel``) leaves every disguised authentication
    or permission failure looking like a genuine server fault -- and the
    transport then retries what can never succeed. It reads its own note rather
    than the server's phrasing, which may differ between versions.
    """
    return _HIDDEN_NOTE in str(error)


def at_least(name: str, value: float, limit: float) -> None:
    """Reject a parameter that yields no sensible operation.

    Early and loud rather than late and puzzling: ``max_retries=-1`` would never
    enter the retry loop at all, and the caller would see an error with no cause
    whatsoever.

    Type and finiteness are checked before the comparison. A bare ``<`` let two
    things past that this function exists to stop (audit A14): ``None`` raised a
    ``TypeError`` rather than an ``EduSharingError``, so the library's own error
    type did not cover its own input; and ``nan`` passed, because every
    comparison with it is false -- httpx then received a timeout that never
    elapses.

    Shared by ``Transport``, ``BildungsAPI`` and ``TextExtraction``: all three
    run a retry loop, and the b-api client had this check missing (audit F3,
    2026-08-27).
    """
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise EduSharingError(
            f"{name}={value!r} is not a number -- a value of at least {limit} "
            "is expected."
        )
    if value != value:  # nan: the only value that is not equal to itself
        raise EduSharingError(
            f"{name}=nan is not allowed -- a value of at least {limit} is "
            "expected, and nan compares false against every limit."
        )
    if value < limit:
        raise EduSharingError(
            f"{name}={value!r} is not allowed -- at least {limit} is expected."
        )
