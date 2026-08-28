"""Deciding whether a URL may be fetched.

A service that passes repository content to a language model will sooner or
later encounter a URL that came from foreign data: the ``ccm:wwwurl`` of some
record, a link inside a description. If it points at ``localhost`` or into an
internal network, the service fetches it with **its own** network privileges --
and becomes the instrument (server-side request forgery).

Checking happens without network access: scheme, shape, and for IP literals the
range. The range check uses ``ipaddress`` from the standard library rather than
hand-rolled prefix comparisons -- those are the usual source of mistakes
(``172.16.0.0/12`` reaches only to ``172.31``, not to ``172.255``).

**A limit callers must know about:** a *name* is not resolved here.
``internal-service.example.com`` may point to ``10.0.0.5`` and still pass. If
you must rule that out, re-check the address after resolution or put an
outbound proxy in front. Resolving here would be security theatre anyway: the
answer can change between check and fetch (DNS rebinding).
"""

from __future__ import annotations

import ipaddress
from urllib.parse import urlsplit

from ..errors import EduSharingError
from ..urls import is_unroutable_host

__all__ = ["UnsafeUrlError", "is_safe_url", "check_url"]

ALLOWED_SCHEMES = frozenset({"http", "https"})

#: Names and suffixes that by convention never point at the public internet.
#: An IP literal is already caught by the range check; this covers names that
#: should not even be resolved.
BLOCKED_NAMES = frozenset({"localhost"})
BLOCKED_SUFFIXES = (".local", ".internal", ".localhost", ".home.arpa")


class UnsafeUrlError(EduSharingError):
    """The URL must not be fetched."""


def _address_reason(host: str) -> str | None:
    """Why this literal must not be fetched -- as precisely as it allows.

    ``is_unroutable_host`` owns the decision; this only names it. "Not
    routable" is true for every case below but tells a caller far less than
    "loopback" does.
    """
    if not is_unroutable_host(host):
        return None
    try:
        address = ipaddress.ip_address(host.strip("[]"))
    except ValueError:
        return f"{host!r} is neither a valid hostname nor a dotted-quad address"
    if address.is_loopback:
        return f"{host} is a local (loopback) address"
    if address.is_link_local:
        # 169.254.169.254 is the metadata service of most cloud providers, and
        # therefore the single most rewarding target of an SSRF attack.
        return f"{host} is a link-local address"
    if address.is_private or address.is_reserved or address.is_multicast:
        return f"{host} is a private or reserved address"
    return f"{host} is not a globally routable address"


def _reason(url: str) -> str | None:
    """Why ``url`` must not be fetched -- or ``None`` if it may."""
    if not url or not url.strip():
        return "empty address"

    try:
        parts = urlsplit(url.strip())
    except ValueError as exc:
        return f"unparseable ({exc})"

    if parts.scheme.lower() not in ALLOWED_SCHEMES:
        return f"scheme {parts.scheme or '(none)'!r} -- only http and https are allowed"

    # Credentials in the URL are a known way to confuse checks: some parsers
    # read the host differently than the later fetch does.
    if "@" in parts.netloc:
        return "the address embeds credentials (user:pass@host)"

    try:
        host = parts.hostname
    except ValueError as exc:
        return f"host unparseable ({exc})"
    if not host:
        return "no host"

    host = host.lower().rstrip(".")
    if host in BLOCKED_NAMES or host.endswith(BLOCKED_SUFFIXES):
        return f"{host!r} is a local name"

    # A literal, in any spelling. A name falls through -- see the module
    # docstring on what is deliberately not checked here.
    return _address_reason(host)


def is_safe_url(url: str) -> bool:
    """Whether ``url`` may be fetched.

    ``False`` when in doubt: an unparseable address counts as unsafe.
    """
    return _reason(url) is None


def check_url(url: str) -> str:
    """Return ``url`` if it may be fetched.

    Raises:
        UnsafeUrlError: otherwise, with the reason in the message.
    """
    reason = _reason(url)
    if reason is not None:
        raise UnsafeUrlError(f"Address not fetchable: {url!r} -- {reason}.")
    return url
