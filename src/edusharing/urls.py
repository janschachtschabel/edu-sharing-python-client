"""Turning an address as people pass it around into a dependable base URL.

Operators name their repository sometimes as a bare domain, sometimes with
``/edu-sharing``, sometimes with the ``/rest`` from the API docs appended. All
of these mean the same thing, so all of them should work.

Two forms do NOT mean it and are rejected rather than silently guessed at: a
deep link to a page, and a doubled ``/edu-sharing``. Either would otherwise
make every single call end in 404 with nothing anywhere saying why.
"""

from __future__ import annotations

import re

from .errors import EduSharingError

__all__ = ["normalize_repository_url", "rest_base"]

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
