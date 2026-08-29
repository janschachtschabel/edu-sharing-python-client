"""The text behind a linked resource -- edu-sharing's extraction service.

A repository stores the full text of the files it hosts and answers for them
under ``/textContent`` (see ``content.py``). For material that merely *links*
somewhere -- ``ccm:wwwurl`` -- it has nothing, because the page is not its
file. An edu-sharing installation normally runs a second service for that: the
openeduhub text-extraction service, which fetches a public URL and returns its
text.

It is a **separate service with its own address**, like the b-api, and it is
built the same way: on its own, from its own environment variable, with no
default. The MCP tried a default once and took it back -- pointing at the
staging service sent production material URLs into another environment.

Measured 2026-08-28 against ``https://text-extraction.staging.openeduhub.net``
(FastAPI, version ``c766f2e5``):

* **Three routes:** ``/_ping``, ``/from-url``, ``/metrics``. No ``/health``,
  no ``/``.
* **``POST /from-url``** takes ``{url*, method, browser_location, lang,
  output_format, preference}``; only ``url`` is required. The service's own
  defaults are ``method="simple"``, ``lang="auto"``, ``output_format="txt"``,
  ``preference="none"``.
* **A 200 answers ``{text, lang, status, version}``.** ``status`` is the HTTP
  status of the **target page**, not of the service -- a 200 from the service
  can carry a 404 from the page.
* **424, not 400.** An unusable address, a page without text, a private host --
  all end in ``424 Failed Dependency`` with ``{"detail": {error_message,
  status, reason, version}}``. A missing required field gives ``422``.
* **An edu-sharing download URL gives 424.** The service cannot read what the
  repository itself hosts; ``/textContent`` stays responsible for that.
* **``method="browser"`` is not simply better.** On one measured page
  ``simple`` returned the article and ``browser`` returned the cookie banner.
  They are two attempts, not a ranking.

**The URL is chosen by the caller and fetched by someone else.** So every check
that can be made runs *before* anything is sent -- a check that answers
correctly after the service has already made the request has guarded nothing.
One gap cannot be closed here: between our resolution and the service's lies a
window, and a redirect happens inside its process, where this library cannot
see it. Measured, the service answers 424 for a private host, but that is its
network and its deployment, not a guarantee to build on.
"""

from __future__ import annotations

import asyncio
import logging
import os
import socket
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Self
from urllib.parse import urlsplit

import httpx

from .errors import EduSharingError, at_least
from .urls import is_unroutable_host

__all__ = ["ExtractedText", "TextExtraction", "METHODS"]

#: See ``edusharing.transport.logger``. Never the URL, only the host -- a
#: caller-chosen URL can carry a token in its query, and a refusal must not be
#: the thing that logs it. Every address this service is given is the caller's,
#: so the host is all that is ever left; ``Transport._for_log`` applies the
#: same rule to a repository that also builds addresses of its own.
logger = logging.getLogger(__name__)

#: The two the service accepts. Checked here so a typo fails at the call site
#: rather than coming back as a 422 from a remote machine.
METHODS = ("simple", "browser")

DEFAULT_TIMEOUT = 60.0
DEFAULT_MAX_RETRIES = 2
DEFAULT_BACKOFF_BASE = 1.0

_RETRYABLE = frozenset({429, 500, 502, 503, 504})


@dataclass(frozen=True)
class ExtractedText:
    """What the service made of one address."""

    #: Normalised, exactly as sent. Reporting the raw input would name an
    #: address that was never requested.
    url: str
    text: str
    #: The language the service detected, or ``""`` when there is no text.
    lang: str
    #: The HTTP status of the **target page** -- ``0`` when the service did not
    #: report one. Not the status of the service's own answer.
    status: int
    #: Length before truncation, so a caller can see what it is missing.
    char_count: int
    truncated: bool
    #: ``""`` when there is text. Otherwise ``not_http``, ``private_host``,
    #: ``dns_failed`` or ``no_text`` -- separate causes, so "we would not fetch
    #: that" never looks like "the page had no text".
    reason: str = ""
    #: The service's own words when it found nothing. Free text, for a human.
    detail: str = ""

    def __repr__(self) -> str:
        what = f"{self.char_count} chars" if self.text else f"reason={self.reason!r}"
        return f"ExtractedText({self.url!r}, {what})"


class TextExtraction:
    """Client for the text-extraction service of one edu-sharing installation.

    Args:
        base_url: the service's address -- scheme and host only. A value that
            cannot serve as a base is refused rather than warned about: a typo
            here sends material URLs to a host nobody chose.
        timeout: seconds until a single request is abandoned. Generous by
            default; ``method="browser"`` renders the page.
        max_retries: retries in addition to the first attempt, for what the
            service could temporarily not deliver.
        backoff_base: base wait; doubles with each attempt.
        resolve: how a hostname is resolved, for the private-network check --
            a plain callable returning addresses. An injection point for tests;
            DNS does not belong in a unit test.
        client: your own httpx client, e.g. for tests.

    Not attached to ``Repository``: this is a second service with its own
    address, and the connection to a repository says nothing about whether it
    exists. Build it yourself, as with ``BildungsAPI``.
    """

    ENV_BASE_URL = "EDU_SHARING_TEXT_EXTRACTION_URL"

    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_base: float = DEFAULT_BACKOFF_BASE,
        resolve: Callable[[str], Any] | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        at_least("max_retries", max_retries, 0)
        at_least("timeout", timeout, 0.001)
        self.base_url = _check_base(base_url)
        self.max_retries = max_retries
        self.backoff_base = backoff_base
        self._resolve = resolve
        self._client = client or httpx.AsyncClient(timeout=timeout)

    @classmethod
    def from_env(cls, **kwargs: Any) -> TextExtraction:
        """Build from ``EDU_SHARING_TEXT_EXTRACTION_URL``.

        Raises:
            EduSharingError: when the variable is unset or empty. There is no
                default on purpose -- each installation runs its own service,
                and guessing at one sends material URLs into a foreign
                environment.
        """
        value = os.environ.get(cls.ENV_BASE_URL, "").strip()
        if not value:
            raise EduSharingError(
                f"{cls.ENV_BASE_URL} is not set. Point it at the extraction "
                "service of your own repository -- there is no default, "
                "because a wrong one sends material URLs somewhere you did "
                "not choose."
            )
        return cls(value, **kwargs)

    async def ping(self) -> dict[str, Any]:
        """Ask the service whether it is there.

        Returns:
            Its own answer, measured ``{"status", "version", "timestamp"}``.
        """
        response = await self._request("GET", "/_ping")
        return dict(response.json())

    async def text_of(
        self,
        url: str,
        *,
        method: str = "simple",
        output_format: str = "txt",
        lang: str = "auto",
        max_chars: int | None = None,
    ) -> ExtractedText:
        """The text behind ``url``.

        Args:
            url: a public http(s) address. Typically a record's ``ccm:wwwurl``.
            method: ``simple`` reads the delivered HTML, ``browser`` renders the
                page first. Neither is the better one -- measured, ``simple``
                returned an article where ``browser`` returned a cookie banner.
                If one yields nothing, the other is the sensible second try.
            output_format: ``txt`` (the service's default) or ``markdown``.
            lang: ``auto``, or a language code to insist on.
            max_chars: cut the text at a word boundary. ``truncated`` says
                whether it bit; ``char_count`` keeps the full length.

        Returns:
            An ``ExtractedText``. **No text is a normal outcome, not an
            error** -- ``reason`` says which of the four causes it was.

        Raises:
            ValueError: for an unknown ``method`` or a ``max_chars`` below one.
            EduSharingError: when the service itself fails -- a rejected body
                (422) or an error it kept answering with after the retries.
        """
        if method not in METHODS:
            raise ValueError(
                f"method={method!r} is unknown -- the service accepts "
                f"{' and '.join(METHODS)}."
            )
        if max_chars is not None and max_chars < 1:
            raise ValueError(
                f"max_chars={max_chars!r} would keep no text at all -- leave it "
                "out to keep everything."
            )

        target = urlsplit(url.strip())
        if target.scheme not in ("http", "https") or not target.hostname:
            return _miss(url, "not_http")
        # Rebuilt, not echoed: a raw input may differ from what was sent, and
        # then the answer names an address nobody requested.
        normalised = target.geturl()

        refusal = await self._judge(target.hostname)
        if refusal:
            return _miss(normalised, refusal)

        response = await self._request("POST", "/from-url", json={
            "url": normalised,
            "method": method,
            "output_format": output_format,
            "lang": lang,
            # The service's own default, sent explicitly so a change on its
            # side does not silently change what this library asks for.
            "preference": "none",
        })
        return _result(normalised, response, max_chars)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.aclose()

    def __repr__(self) -> str:
        return f"TextExtraction({self.base_url!r})"

    # --- Internals --------------------------------------------------------

    async def _judge(self, host: str) -> str:
        """``""`` when the host may be fetched, otherwise the refusal reason.

        Cheapest and most certain first: a literal address needs no resolver,
        a name does.
        """
        if is_unroutable_host(host):
            logger.warning("text extraction refused a private host: %s", host)
            return "private_host"

        try:
            addresses = await self._addresses(host)
        except OSError as exc:
            logger.warning("text extraction could not resolve %s: %s", host, exc)
            # Refused, not waved through: the service may resolve what we could
            # not, and then the check would have checked nothing.
            return "dns_failed"

        if any(is_unroutable_host(address) for address in addresses):
            logger.warning("text extraction refused %s by resolution", host)
            return "private_host"
        return ""

    async def _addresses(self, host: str) -> list[str]:
        if self._resolve is not None:
            return list(self._resolve(host))
        infos = await asyncio.get_running_loop().getaddrinfo(
            host, None, type=socket.SOCK_STREAM
        )
        return [str(info[4][0]) for info in infos]

    async def _request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        last: EduSharingError | None = None
        for attempt in range(self.max_retries + 1):
            if attempt:
                await asyncio.sleep(self.backoff_base * (2 ** (attempt - 1)))
            try:
                response = await self._client.request(
                    method, f"{self.base_url}{path}", **kwargs
                )
            except httpx.HTTPError as exc:
                last = EduSharingError(f"{type(exc).__name__}: {exc}")
                continue
            # 424 is an answer about the page, not a failure of the service --
            # ``_result`` turns it into a reason.
            if response.status_code < 400 or response.status_code == 424:
                return response
            last = EduSharingError(
                f"The extraction service answered HTTP {response.status_code} "
                f"for {path}: {response.text[:200]}"
            )
            if response.status_code not in _RETRYABLE:
                raise last
        raise last  # type: ignore[misc]


def _check_base(value: str) -> str:
    """Scheme and host, nothing else. Refused rather than warned about."""
    parts = urlsplit((value or "").strip())
    if parts.scheme not in ("http", "https") or not parts.netloc:
        raise EduSharingError(
            f"{value!r} is not a usable base address for the extraction "
            "service -- it needs a scheme and a host, e.g. "
            "https://text-extraction.example.org"
        )
    if parts.query or parts.fragment:
        raise EduSharingError(
            f"{value!r} carries a query or fragment. The base address is the "
            "service itself; the route is appended to it."
        )
    return f"{parts.scheme}://{parts.netloc}{parts.path.rstrip('/')}"


def _miss(url: str, reason: str) -> ExtractedText:
    return ExtractedText(url=url, text="", lang="", status=0, char_count=0,
                         truncated=False, reason=reason)


def _result(url: str, response: httpx.Response,
            max_chars: int | None) -> ExtractedText:
    body = _body(response)
    if response.status_code == 424:
        detail = body.get("detail")
        detail = detail if isinstance(detail, dict) else {}
        return ExtractedText(
            url=url, text="", lang="", status=int(detail.get("status") or 0),
            char_count=0, truncated=False, reason="no_text",
            detail=str(detail.get("error_message") or response.text[:200]),
        )

    text = str(body.get("text") or "")
    if not text.strip():
        return _miss(url, "no_text")

    full = len(text)
    cut, truncated = _cap(text, max_chars)
    return ExtractedText(
        url=url, text=cut, lang=str(body.get("lang") or ""),
        status=int(body.get("status") or 0), char_count=full,
        truncated=truncated,
    )


def _body(response: httpx.Response) -> dict[str, Any]:
    try:
        data = response.json()
    except ValueError:
        return {}
    return data if isinstance(data, dict) else {}


def _cap(text: str, max_chars: int | None) -> tuple[str, bool]:
    """Cut at a word boundary, or hard when there is none to cut at."""
    if max_chars is None or len(text) <= max_chars:
        return text, False
    head = text[:max_chars]
    boundary = head.rstrip().rfind(" ")
    return (head[:boundary] if boundary > 0 else head), True
