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
    "ConflictError",
    "ServerError",
    "SilentDropError",
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
    """

    def __init__(
        self,
        message: str,
        *,
        status: int | None = None,
        url: str | None = None,
        error_class: str | None = None,
        stacktrace: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.url = url
        self.error_class = error_class
        self.stacktrace = stacktrace


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


def error_from_response(status: int, url: str, body: str) -> EduSharingError:
    """Build the matching error type from a failure response.

    The HTTP status is the first hint but not the last: for 5xx the content
    decides whether the server is genuinely broken or whether merely the
    sign-in, respectively a permission, is missing.
    """
    error_class, message, stacktrace = _parse_body(body)

    if status >= 500:
        lowered = message.lower()
        if _GUEST_HINT in lowered:
            cls: type[EduSharingError] = AuthenticationError
        elif _MISSING_HINT in lowered:
            cls = NotFoundError
        elif any(h in (error_class or "").lower() for h in _PERMISSION_HINTS):
            cls = PermissionDeniedError
        else:
            cls = ServerError
    else:
        cls = {
            400: ValidationError,
            401: AuthenticationError,
            403: PermissionDeniedError,
            404: NotFoundError,
            409: ConflictError,
        }.get(status, EduSharingError)

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
