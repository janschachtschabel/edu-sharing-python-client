"""Groups, and who belongs to them.

The question underneath is always the same: **who may moderate here.** The
Ideendatenbank answers it through these three endpoints.

Measured against staging on 2026-08-28 with the account ``sc25-14``:

* ``GET /iam/v1/people/-home-/-me-/memberships`` → ``{"groups": [...]}``. Each
  group carries ``authorityName`` (``GROUP_ORG_AI-Skills``), ``groupName``
  (``ORG_AI-Skills``), ``signupMethod`` and a ``profile`` with ``displayName``
  and ``groupType``.
* ``GET /iam/v1/groups/-home-/{g}`` answers **wrapped**: ``{"group": {...}}``.
* ``GET .../members`` answers **500 AccessDeniedException** ("User does not
  have permissions to manage this group") for a group one is merely a member
  of. That is a permission question, not a server failure, and
  ``error_from_response`` translates it -- otherwise the transport would retry
  three times what can never succeed.
* ``.../members`` defaults ``maxItems`` to **10**. A group of fifty would come
  back as a group of ten, silently. This module asks for a hundred and lets the
  caller raise it.
* ``POST /iam/v1/groups/-home-/{name}`` answers **403** for this account.

.. warning::

   **The writing operations below are not verified against a live instance.**
   The test account may not create groups, so ``create_group``,
   ``delete_group``, ``add_member`` and ``remove_member`` are tested offline
   against the measured request shape -- method, path, body -- and against the
   OpenAPI model. That the repository accepts them is unproven. The same holds
   for the exact shape of the member list, which no account here can read.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from .urls import path_segment

if TYPE_CHECKING:  # pragma: no cover
    from .transport import Transport

__all__ = ["Group", "Member", "People"]

#: The endpoint's own default is 10, which turns a group of fifty into a group
#: of ten without saying so. A hundred covers the ordinary case; the parameter
#: is there for the rest.
DEFAULT_MEMBER_LIMIT = 100


@dataclass(frozen=True)
class Group:
    """A group, as the repository describes it.

    Attributes:
        name: the authority name, e.g. ``GROUP_ORG_AI-Skills``. This is what
            every other endpoint wants -- permissions included.
        short_name: the same without the ``GROUP_`` prefix.
        display_name: what a person reads.
        type: the group type, e.g. ``EDITORIAL``. ``None`` when unset.
        signup: how one joins, e.g. ``simple``. ``None`` when joining is closed.
        raw: the untouched record, for anything an instance puts in
            ``properties`` that this shape does not cover.
    """

    name: str
    short_name: str
    display_name: str
    type: str | None
    signup: str | None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_response(cls, data: dict[str, Any]) -> Group:
        profile = data.get("profile") or {}
        name = str(data.get("authorityName") or "")
        return cls(
            name=name,
            short_name=str(data.get("groupName") or name.removeprefix("GROUP_")),
            display_name=str(profile.get("displayName") or name),
            type=profile.get("groupType") or None,
            signup=data.get("signupMethod") or None,
            raw=data,
        )

    def __repr__(self) -> str:
        return f"Group({self.name!r}, {self.display_name!r})"


@dataclass(frozen=True)
class Member:
    """One member of a group.

    ``is_group`` matters: a group can contain groups, and treating a nested
    group as a person is a mistake with consequences when the question is who
    may moderate.
    """

    name: str
    is_group: bool

    @classmethod
    def from_response(cls, data: dict[str, Any]) -> Member:
        return cls(
            name=str(data.get("authorityName") or ""),
            is_group=str(data.get("authorityType") or "").upper() == "GROUP",
        )

    def __repr__(self) -> str:
        return f"Member({self.name!r}, Gruppe)" if self.is_group \
            else f"Member({self.name!r})"


class People:
    """Groups and memberships. Reached as ``repo.people``."""

    def __init__(self, transport: Transport) -> None:
        self._transport = transport

    # --- Reading ----------------------------------------------------------

    async def memberships(self) -> list[Group]:
        """The groups this account belongs to."""
        response = await self._transport.json(
            "GET", "/iam/v1/people/-home-/-me-/memberships"
        )
        return [Group.from_response(g) for g in (response.get("groups") or [])]

    async def group(self, name: str) -> Group:
        """One group by its authority name, e.g. ``GROUP_ORG_AI-Skills``.

        Raises:
            NotFoundError: when no group carries this name.
            PermissionDeniedError: when the account may not see it.
        """
        response = await self._transport.json(
            "GET", f"/iam/v1/groups/-home-/{path_segment(name)}"
        )
        return Group.from_response(response.get("group") or response)

    async def members(
        self, group: str, *, limit: int = DEFAULT_MEMBER_LIMIT, offset: int = 0
    ) -> list[Member]:
        """Who belongs to a group -- people and nested groups alike.

        Args:
            group: the group's authority name.
            limit: how many to fetch. The endpoint's own default is 10, which
                truncates a larger group without saying so.
            offset: where to start.

        Raises:
            PermissionDeniedError: when the account does not manage this group.
                Measured: being a member is not enough, and the repository says
                so with a 500 that means 403.
        """
        response = await self._transport.json(
            "GET",
            f"/iam/v1/groups/-home-/{path_segment(group)}/members",
            params={"maxItems": limit, "skipCount": offset},
        )
        return [Member.from_response(a) for a in (response.get("authorities") or [])]

    # --- Writing ----------------------------------------------------------
    #
    # None of the four below is verified against a live instance -- see the
    # module docstring. Each says so again where it is read.

    async def create_group(
        self,
        name: str,
        *,
        display_name: str | None = None,
        type: str | None = None,
        parent: str | None = None,
    ) -> Group:
        """Create a group.

        **Not verified live**: the test account answers 403 here, so only the
        request shape is proven, not the repository's acceptance of it.

        Args:
            name: the authority name, conventionally prefixed ``GROUP_``.
            display_name: what a person reads. Defaults to ``name`` -- a
                profile without one leaves a nameless group in every interface.
            type: the group type, e.g. ``EDITORIAL``.
            parent: an existing group to nest this one under.
        """
        body: dict[str, Any] = {"displayName": display_name or name}
        if type:
            body["groupType"] = type
        response = await self._transport.json(
            "POST",
            f"/iam/v1/groups/-home-/{path_segment(name)}",
            params={"parent": parent} if parent else None,
            json=body,
        )
        return Group.from_response(response.get("group") or response)

    async def delete_group(self, name: str) -> None:
        """Remove a group. **Not verified live** -- see ``create_group``."""
        await self._transport.request(
            "DELETE", f"/iam/v1/groups/-home-/{path_segment(name)}"
        )

    async def add_member(self, group: str, authority: str) -> None:
        """Put a user or a group into a group.

        **Not verified live** -- see ``create_group``. Whether a repeated call
        is a no-op or an error is therefore unmeasured, and nothing here claims
        either.
        """
        await self._transport.request("PUT", self._member_path(group, authority))

    async def remove_member(self, group: str, authority: str) -> None:
        """Take a user or a group out of a group. **Not verified live.**"""
        await self._transport.request("DELETE", self._member_path(group, authority))

    # --- Internals --------------------------------------------------------

    @staticmethod
    def _member_path(group: str, authority: str) -> str:
        return (
            f"/iam/v1/groups/-home-/{path_segment(group)}"
            f"/members/{path_segment(authority)}"
        )

    def __repr__(self) -> str:
        return f"People({self._transport.repository_url!r})"
