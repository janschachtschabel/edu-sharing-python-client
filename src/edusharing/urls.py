"""Turning an address as people pass it around into a dependable base URL.

Operators name their repository sometimes as a bare domain, sometimes with
``/edu-sharing``, sometimes with the ``/rest`` from the API docs appended. All
of these mean the same thing, so all of them should work.

Two forms do NOT mean it and are rejected rather than silently guessed at: a
deep link to a page, and a doubled ``/edu-sharing``. Either would otherwise
make every single call end in 404 with nothing anywhere saying why.
"""

from __future__ import annotations

import ipaddress
import re
from urllib.parse import quote

from .errors import EduSharingError

__all__ = ["normalize_repository_url", "path_segment", "rest_base",
           "is_unroutable_host"]

_APP_SEGMENT = "/edu-sharing"


def normalize_repository_url(raw: str) -> str:
    """Normalise a repository address to ``<scheme>://<host>[/path]/edu-sharing``.

    The result is the frontend base, not the REST base: both ``/rest/...`` and
    the viewer URLs ``/components/...`` derive from it.

    Raises:
        EduSharingError: on empty input, a deep link, or a doubled
            ``/edu-sharing``.
    """
    url = (raw or "").strip()
    if not url:
        raise EduSharingError(
            "No repository URL given. Something like "
            "'https://repository.staging.openeduhub.net' is expected."
        )

    url = url.rstrip("/")
    # We append /rest ourselves; anyone passing it would otherwise get /rest/rest.
    url = re.sub(r"/rest$", "", url, flags=re.IGNORECASE).rstrip("/")

    if not re.match(r"^https?://", url, flags=re.IGNORECASE):
        url = f"https://{url}"

    if re.search(r"/components(/|$)", url, flags=re.IGNORECASE):
        raise EduSharingError(
            f"The URL points at a page, not at the repository: {raw!r}. "
            "The base is expected, i.e. everything up to and including "
            "'/edu-sharing'."
        )

    # Lookahead rather than a group, so "/edu-sharing/edu-sharing" counts twice.
    count = len(re.findall(r"/edu-sharing(?=/|$)", url, flags=re.IGNORECASE))
    if count > 1:
        raise EduSharingError(
            f"The URL contains '/edu-sharing' more than once: {raw!r}."
        )
    if count == 0:
        url += _APP_SEGMENT

    return url


def rest_base(repository_url: str) -> str:
    """The REST root for a normalised repository URL."""
    return f"{repository_url}/rest"


def _is_address_shaped(host: str) -> bool:
    """Whether ``host`` spells an address in a form ``ipaddress`` will not read.

    Decimal (``2130706433``), hexadecimal (``0x7f000001``) and shortened
    (``127.1``) all denote ``127.0.0.1`` to many resolvers, and all raise
    ``ValueError`` in ``ipaddress`` -- so without this they pass as names
    (audit A7). Whether they reach loopback depends on the platform; measured,
    they do not resolve on Windows. Rejecting them costs nothing either way: a
    hostname whose rightmost label is all digits is not valid under RFC 1123.

    Only meaningful **after** ``ipaddress`` has refused the host. Every ordinary
    dotted quad ends in digits too, so calling this on its own rejects the
    entire public IPv4 space.
    """
    return host.startswith("0x") or host.rsplit(".", 1)[-1].isdigit()


def is_unroutable_host(host: str) -> bool:
    """Whether ``host`` must not be fetched, judged on its literal form alone.

    ``False`` for a name -- resolving is the caller's business, and what a name
    resolves to has to be re-checked after resolution anyway.

    **Both rule sets, deliberately.** This decision existed twice in the library
    until 2026-08-28 and the copies disagreed (audit A6): the enumeration let
    ``100.64.0.0/10`` through -- CGNAT, routine inside provider and corporate
    networks -- while ``not is_global`` let ``64:ff9b::/96`` (NAT64) through.
    Each had a hole the other did not, so both apply.

    It lives here rather than in ``agent.safety`` because ``extraction`` needs
    it too, and a layer-0 module may not import from layer 3.
    """
    bare = host.strip("[]")
    try:
        address = ipaddress.ip_address(bare)
    except ValueError:
        return _is_address_shaped(bare)
    return (
        not address.is_global
        or address.is_loopback
        or address.is_link_local
        or address.is_private
        or address.is_reserved
        or address.is_multicast
    )


def path_segment(value: str) -> str:
    """Percent-encode one identifier for use inside a URL path.

    ``safe=""`` is the whole point. ``quote`` leaves ``/`` untouched by default,
    and that is exactly what must not happen here: a segment that spans a path
    boundary reaches a different endpoint than the one the caller asked for.

    Measured against edu-sharing 11.0 (2026-08-27), without this function:

    * a node id of ``../../../admin/v1/applications`` turned
      ``/node/v1/nodes/-home-/{id}/metadata`` into
      ``/node/admin/v1/applications/metadata``
    * a node id of ``abc?admin=1`` swallowed the trailing ``/metadata`` entirely

    This matters most where identifiers are not typed by a developer but arrive
    from a language model -- the case ``edusharing.agent`` exists for.

    Raises:
        EduSharingError: on an empty value, which would collapse into a double
            slash and thus address a different path.
    """
    if not value:
        raise EduSharingError(
            "An empty identifier cannot be part of a URL path. "
            "Expected a node, collection or metadata-set id."
        )
    return quote(value, safe="")
