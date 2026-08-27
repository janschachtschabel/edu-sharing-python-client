"""Credentials -- who is making a request.

Its own module because a security boundary lives here, and a security boundary
should be findable by its file name. It carries two properties:

**Credentials are values, not global state.** Every request gets its own. A
service that serves many people -- an MCP server, say -- cannot otherwise keep
straight who is asking.

**Bearer tokens are rejected.** The OpenAPI specification of edu-sharing
declares exactly two schemes, ``basicAuth`` and ``cookieAuth``. An
``Authorization: Bearer ...`` is **ignored, not rejected** by the server: the
request looks authenticated and runs as a guest. Whoever writes with it gets a
500 "Not allowed for guest user" somewhere unrelated to the actual problem.
"""

from __future__ import annotations

import base64
import os
from typing import Protocol, runtime_checkable

from .errors import EduSharingError

__all__ = ["Credential", "AnonymousCredential", "ANONYMOUS", "BasicCredential",
           "credential_from"]

ENV_USER = "EDU_SHARING_USER"
ENV_PASSWORD = "EDU_SHARING_PASSWORD"


@runtime_checkable
class Credential(Protocol):
    """What the transport needs from credentials."""

    def headers(self) -> dict[str, str]:
        """The headers that go to the repository."""
        ...

    @property
    def is_anonymous(self) -> bool:
        """Whether work happens without signing in."""
        ...


class AnonymousCredential:
    """No sign-in. A valid mode -- much is publicly readable."""

    def headers(self) -> dict[str, str]:
        return {}

    @property
    def is_anonymous(self) -> bool:
        return True

    def __repr__(self) -> str:
        return "AnonymousCredential()"


ANONYMOUS: Credential = AnonymousCredential()


class BasicCredential:
    """Username and password per RFC 7617.

    The password appears in neither ``repr`` nor ``str``: both end up in
    tracebacks and log lines.
    """

    __slots__ = ("_header", "_username")

    def __init__(self, username: str, password: str) -> None:
        self._username = username
        # UTF-8 pinned rather than left to the platform: otherwise a sign-in
        # with an umlaut depends on which system the client runs on.
        raw = f"{username}:{password}".encode()
        self._header = "Basic " + base64.b64encode(raw).decode("ascii")

    @classmethod
    def from_raw_header(cls, header: str) -> BasicCredential:
        """Adopt a ready ``Basic ...`` header without taking it apart.

        For cases where the credentials come from a forwarded request and are
        not available in the clear at all.
        """
        obj = cls.__new__(cls)
        object.__setattr__(obj, "_username", "<from header>")
        object.__setattr__(obj, "_header", header)
        return obj

    @classmethod
    def from_env(cls) -> BasicCredential | None:
        """Read ``EDU_SHARING_USER`` / ``EDU_SHARING_PASSWORD``.

        Returns:
            ``None`` when both are absent -- then work happens anonymously.

        Raises:
            EduSharingError: when only one of the two is set. Continuing
                anonymously would obscure the misconfiguration -- and measured,
                edu-sharing answers wrong credentials with 401 everywhere
                rather than with reduced access.
        """
        user = os.environ.get(ENV_USER)
        password = os.environ.get(ENV_PASSWORD)
        if not user and not password:
            return None
        if not user or not password:
            missing = ENV_PASSWORD if user else ENV_USER
            raise EduSharingError(
                f"Incomplete credentials: {missing} is missing. Either set both "
                f"{ENV_USER} and {ENV_PASSWORD}, or neither."
            )
        return cls(user, password)

    def headers(self) -> dict[str, str]:
        return {"Authorization": self._header}

    @property
    def is_anonymous(self) -> bool:
        return False

    @property
    def username(self) -> str:
        return self._username

    def __repr__(self) -> str:
        return f"BasicCredential(username={self._username!r}, password=<hidden>)"

    __str__ = __repr__


def credential_from(value: object) -> Credential:
    """Turn whatever a caller passes into credentials.

    Accepted: ``None`` (anonymous), a ``(username, password)`` pair, a ready
    ``Basic ...`` header, and an already-built ``Credential``.

    Raises:
        EduSharingError: on a bearer token or an unknown shape.
    """
    if value is None:
        return ANONYMOUS
    if isinstance(value, (AnonymousCredential, BasicCredential)):
        return value
    if isinstance(value, tuple) and len(value) == 2:
        user, password = value
        return BasicCredential(str(user), str(password))
    if isinstance(value, str):
        # The token itself must not reach the message -- it is a secret, even a
        # useless one here.
        if value.lower().startswith("bearer "):
            raise EduSharingError(
                "Bearer tokens are not supported by edu-sharing. The API knows "
                "only Basic auth and session cookies, and it IGNORES a Bearer "
                "header rather than rejecting it -- the request would then run "
                "as a guest without anyone noticing. Please pass username and "
                "password: Repository(url, auth=(user, password))."
            )
        if value.lower().startswith("basic "):
            return BasicCredential.from_raw_header(value)
        raise EduSharingError(
            f"Unknown credential shape: {value.split(' ', 1)[0]!r}. A "
            "(username, password) pair or a 'Basic ...' header is expected."
        )
    raise EduSharingError(
        f"Credentials cannot be built from {type(value).__name__}. Expected "
        "None, a (username, password) pair, or a 'Basic ...' header."
    )
