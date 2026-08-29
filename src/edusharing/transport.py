"""The one way out.

Every request to a repository passes through here. That is not an end in
itself: three decisions must be made in exactly one place, or their copies
drift apart.

**Who receives the password.** Credentials go only to the configured repository
URL. Absolute URLs partly come from response data (previews, downloads), and one
of them may point elsewhere.

**What gets retried.** Only what a retry can fix. The decision is made on the
error type from ``errors``, not on the status code -- because with edu-sharing
an HTTP 500 can simply mean "not signed in".

**How much runs at once.** A fan-out across many nodes otherwise creates more
load than the repository tolerates.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Self

import httpx

from .auth import ANONYMOUS, Credential, credential_from
from .errors import (
    EduSharingError,
    ServerError,
    TransportError,
    at_least,
    details_withheld,
    error_from_response,
)
from .urls import normalize_repository_url, rest_base

__all__ = ["Transport"]

#: Silent by default, as a library should be. A service switches it on with
#: ``logging.getLogger("edusharing").setLevel(logging.DEBUG)``.
#:
#: Never logged: headers. That is where the credentials live, and a log line is
#: aggregated, searched and kept -- see test_logging.py.
logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 3
DEFAULT_MAX_CONCURRENCY = 8
DEFAULT_BACKOFF_BASE = 0.5


class Transport:
    """HTTP access to an edu-sharing repository.

    Args:
        repository_url: repository address in any of the usual spellings; it is
            normalised.
        credential: default for every request. Overridable per request.
        timeout: seconds until a single request is abandoned.
        max_retries: retries in addition to the first attempt.
        max_concurrency: requests running at once.
        backoff_base: base wait; doubles with each attempt.
        client: your own httpx client, e.g. for tests.

    Only a ``ServerError`` is retried -- what the server could temporarily not
    deliver. A rejected request is not: retrying it is the same request again,
    three times the load, and the same answer.

    **One exception, measured.** A ``401`` on a connection that *is* signed in
    is retried exactly once. Measured against edu-sharing 11.0 (staging,
    2026-08-28) with valid credentials, 20 nodes per round over 5 rounds::

        one after another    0 of 100 requests answered 401
        all at once          9 of 100 requests answered 401

    Same nodes, same credentials. Under concurrency a ``401`` is a statement
    about the moment, not about the credentials -- and it lands on every batch
    flow in this library. With the single retry in place the same measurement
    answered 1, 0 and 0 of 100 over three runs. Once, not ``max_retries``
    times: an extra request is a fair price for the measured hiccup, three
    would be a penalty for a typo in a password. Anonymous connections are
    excluded, because there a ``401`` means "this needs a login" and will mean
    it again. A ``500`` that is really "not signed in" is excluded too -- that
    one is a statement about the login.
    """

    def __init__(
        self,
        repository_url: str,
        *,
        credential: object = ANONYMOUS,
        timeout: float | None = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
        max_concurrency: int = DEFAULT_MAX_CONCURRENCY,
        backoff_base: float = DEFAULT_BACKOFF_BASE,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        if timeout is not None and client is not None:
            # The timeout belongs to the client. Accepting both silently meant
            # the parameter was validated and then discarded -- measured,
            # ``timeout=0.5`` with an injected client yielded ``Timeout(5.0)``
            # (audit A11). Saying so beats guessing which one the caller meant.
            raise EduSharingError(
                "timeout and client cannot both be given: a client carries its "
                "own timeout, and this one would be ignored. Set it on the "
                "client -- httpx.AsyncClient(timeout=...) -- or leave the "
                "client out."
            )
        if timeout is None:
            timeout = DEFAULT_TIMEOUT
        at_least("timeout", timeout, 0.001)
        at_least("max_retries", max_retries, 0)
        at_least("max_concurrency", max_concurrency, 1)
        at_least("backoff_base", backoff_base, 0)

        self.repository_url = normalize_repository_url(repository_url)
        self.rest_url = rest_base(self.repository_url)
        self.credential = credential_from(credential)
        self.max_retries = max_retries
        self.backoff_base = backoff_base
        self._semaphore = asyncio.Semaphore(max_concurrency)
        self._client = client or httpx.AsyncClient(timeout=timeout)
        self._owns_client = client is None

    # --- Lifecycle --------------------------------------------------------

    async def aclose(self) -> None:
        """Close the client, if it was created here."""
        if self._owns_client:
            await self._client.aclose()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        await self.aclose()

    # --- The boundary: who receives the credentials -----------------------

    def is_repository_url(self, url: str) -> bool:
        """Whether ``url`` addresses the configured repository.

        Prefix AND boundary, so a look-alike host
        (``https://repo.example.test.attacker.test``) cannot slip through.
        """
        base = self.repository_url
        return url == base or url.startswith((f"{base}/", f"{base}?"))

    def _resolve(self, path: str) -> str:
        """Append relative paths to the REST root, leave absolute ones alone."""
        if path.startswith(("http://", "https://")):
            return path
        return f"{self.rest_url}{path if path.startswith('/') else '/' + path}"

    def _headers(
        self, url: str, credential: Credential, extra: dict[str, str] | None
    ) -> dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.is_repository_url(url):
            headers.update(credential.headers())
        if extra:
            headers.update(extra)
        return headers

    # --- Requests ---------------------------------------------------------

    async def request(
        self,
        method: str,
        path: str,
        *,
        credential: object | None = None,
        params: dict[str, Any] | None = None,
        json: Any = None,
        content: bytes | str | None = None,
        files: Any = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        """Make a request and return the response.

        Args:
            path: path relative to the REST root (``/_about``) or an absolute URL.
            credential: credentials for this request only.

        Raises:
            EduSharingError: on any status from 400 up, as the matching subtype.
            TransportError: when the request never reached the server.
        """
        url = self._resolve(path)
        cred = self.credential if credential is None else credential_from(credential)
        request_headers = self._headers(url, cred, headers)

        last: EduSharingError | None = None
        # Spent at most once per request -- see the note at ``_retry_401``.
        may_retry_401 = not cred.is_anonymous
        # Likewise once, and for the same reason: an instance that withholds its
        # error messages leaves a disguised "not signed in" looking like a
        # server fault. Measured 2026-08-28 -- 4 requests against production
        # where staging needs 1, to an address that can never answer.
        may_retry_withheld = True
        for attempt in range(self.max_retries + 1):
            if attempt:
                logger.info(
                    "retrying %s %s (attempt %d of %d) after %s",
                    method, url, attempt + 1, self.max_retries + 1,
                    type(last).__name__,
                )
                await asyncio.sleep(self.backoff_base * (2 ** (attempt - 1)))
            logger.debug("%s %s", method, url)
            try:
                async with self._semaphore:
                    response = await self._client.request(
                        method, url,
                        params=params, json=json, content=content,
                        files=files, headers=request_headers,
                    )
            except httpx.HTTPError as exc:
                # Network layer: timeout, DNS, TLS, dropped connection.
                last = TransportError(
                    f"{type(exc).__name__}: {exc}", url=url,
                )
                continue

            if 300 <= response.status_code < 400:
                # Reported, not followed. ``follow_redirects`` stays at httpx's
                # default of ``False`` on purpose: following one off the
                # repository would carry the credentials to whatever it names.
                # Not reporting it was worse -- the empty body of a redirect
                # came back as success, which for ``Content.download`` means
                # zero bytes instead of the file (audit A8).
                raise EduSharingError(
                    f"HTTP {response.status_code}: the repository redirected to "
                    f"{response.headers.get('location') or '(no Location header)'!r}. "
                    "This client does not follow redirects -- a redirect off "
                    "the repository would take the credentials with it. If your "
                    "installation sits behind a proxy that bounces, point "
                    "EDU_SHARING_URL at the address it bounces to.",
                    status=response.status_code, url=url,
                )
            if response.status_code < 400:
                return response

            last = error_from_response(response.status_code, url, response.text)
            if response.status_code == 401 and may_retry_401:
                may_retry_401 = False
                continue
            # Only what the server could temporarily not deliver gets retried.
            # A 500 that in truth means "not signed in" was already classified
            # as AuthenticationError and no longer counts as a ServerError here.
            if not isinstance(last, ServerError):
                raise last
            if details_withheld(last):
                if not may_retry_withheld:
                    raise last
                may_retry_withheld = False

        # ``max_retries >= 0`` is checked in the constructor, so the loop runs at
        # least once and has set ``last`` on every branch that does not itself
        # return or raise. A checker cannot see that; an assert would vanish
        # under ``python -O`` and turn this into ``raise None``.
        raise last  # type: ignore[misc]

    async def json(self, method: str, path: str, **kwargs: Any) -> Any:
        """Like ``request``, but returns the parsed JSON body."""
        response = await self.request(method, path, **kwargs)
        return response.json()

    def __repr__(self) -> str:
        return f"Transport({self.repository_url!r})"
