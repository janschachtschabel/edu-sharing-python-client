"""Value objects for what an instance reports about itself.

Kept apart from ``repository`` because they answer a question of their own --
*what kind of repository is this, and who am I working as in it* -- and because
``repository`` would otherwise become a catch-all once the node operations move
in.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = ["About", "Identity", "MetadataSet", "GUEST_AUTHORITY"]

#: What edu-sharing calls unauthenticated access. The value is configurable per
#: instance (``repository.guest.username``); ``esguest`` is the default and what
#: the instances checked here return.
GUEST_AUTHORITY = "esguest"


@dataclass(frozen=True)
class About:
    """What the instance reports, from ``GET /_about``.

    ``services``, ``plugins`` and ``features`` are the way to check capabilities
    rather than assume them -- for instance whether this instance ships the
    b-api.
    """

    repository_version: str | None = None
    renderservice_version: str | None = None
    api_version: str | None = None
    services: list[str] = field(default_factory=list)
    plugins: list[str] = field(default_factory=list)
    features: list[str] = field(default_factory=list)
    themes_url: str | None = None
    #: The complete response, for anything not mapped here.
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_response(cls, data: dict[str, Any]) -> About:
        version = data.get("version") or {}
        major, minor = version.get("major"), version.get("minor")
        return cls(
            repository_version=version.get("repository"),
            renderservice_version=version.get("renderservice"),
            api_version=f"{major}.{minor}" if major is not None else None,
            services=[s.get("name") for s in (data.get("services") or []) if s.get("name")],
            plugins=[p.get("id") for p in (data.get("plugins") or []) if p.get("id")],
            features=[f.get("id") for f in (data.get("features") or []) if f.get("id")],
            themes_url=data.get("themesUrl"),
            raw=data,
        )


@dataclass(frozen=True, slots=True)
class MetadataSet:
    """A metadata set this instance carries.

    Which one is right is the application's call: the choice changes which
    properties are filterable and what gets found.
    """

    id: str
    name: str


@dataclass(frozen=True)
class Identity:
    """Who the application is working as, from ``GET /iam/v1/people/-home-/-me-``."""

    authority: str
    username: str
    display_name: str
    is_anonymous: bool
    #: The user's own folder -- where material goes when nobody says where.
    #: Empty for the guest account, which has none.
    home_folder: str = ""
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_response(cls, data: dict[str, Any]) -> Identity:
        person = data.get("person") or {}
        authority = person.get("authorityName") or ""
        profile = person.get("profile") or {}
        name = " ".join(
            part for part in (profile.get("firstName"), profile.get("lastName")) if part
        )
        return cls(
            authority=authority,
            username=person.get("userName") or authority,
            display_name=name or authority,
            is_anonymous=authority == GUEST_AUTHORITY,
            home_folder=(person.get("homeFolder") or {}).get("id") or "",
            raw=data,
        )
