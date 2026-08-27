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
from typing import Any, Self

import httpx

from .auth import ANONYMOUS, Credential, credential_from
from .errors import (
    EduSharingError,
    ServerError,
    TransportError,
    at_least,
    error_from_response,
)
from .urls import normalize_repository_url, rest_base

__all__ = ["Transport"]

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
    """

    def __init__(
        self,
        repository_url: str,
        *,
        credential: object = ANONYMOUS,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        max_concurrency: int = DEFAULT_MAX_CONCURRENCY,
        backoff_base: float = DEFAULT_BACKOFF_BASE,
        client: httpx.AsyncClient | None = None,
    ) -> None:
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
        for attempt in range(self.max_retries + 1):
            if attempt:
                await asyncio.sleep(self.backoff_base * (2 ** (attempt - 1)))
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

            if response.status_code < 400:
                return response

            last = error_from_response(response.status_code, url, response.text)
            # Only what the server could temporarily not deliver gets retried.
            # A 500 that in truth means "not signed in" was already classified
            # as AuthenticationError and no longer counts as a ServerError here.
            if not isinstance(last, ServerError):
                raise last

        # ``max_retries >= 0`` is checked in the constructor, so the loop runs at
        # least once and has set ``last`` on every branch that does not itself
        # return or raise.
        raise last

    async def json(self, method: str, path: str, **kwargs: Any) -> Any:
        """Like ``request``, but returns the parsed JSON body."""
        response = await self.request(method, path, **kwargs)
        return response.json()

    def __repr__(self) -> str:
        return f"Transport({self.repository_url!r})"
