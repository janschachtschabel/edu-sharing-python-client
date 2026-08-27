from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.authority import Authority
    from ..models.group_profile import GroupProfile
    from ..models.user_profile import UserProfile


T = TypeVar("T", bound="ACE")


@_attrs_define
class ACE:
    """
    Attributes:
        authority (Authority):
        permissions (list[str]):
        from_ (int | Unset):
        to (int | Unset):
        editable (bool | Unset):
        user (UserProfile | Unset):
        group (GroupProfile | Unset):
    """

    authority: Authority
    permissions: list[str]
    from_: int | Unset = UNSET
    to: int | Unset = UNSET
    editable: bool | Unset = UNSET
    user: UserProfile | Unset = UNSET
    group: GroupProfile | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        authority = self.authority.to_dict()

        permissions = self.permissions

        from_ = self.from_

        to = self.to

        editable = self.editable

        user: dict[str, Any] | Unset = UNSET
        if not isinstance(self.user, Unset):
            user = self.user.to_dict()

        group: dict[str, Any] | Unset = UNSET
        if not isinstance(self.group, Unset):
            group = self.group.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "authority": authority,
                "permissions": permissions,
            }
        )
        if from_ is not UNSET:
            field_dict["from"] = from_
        if to is not UNSET:
            field_dict["to"] = to
        if editable is not UNSET:
            field_dict["editable"] = editable
        if user is not UNSET:
            field_dict["user"] = user
        if group is not UNSET:
            field_dict["group"] = group

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.authority import Authority
        from ..models.group_profile import GroupProfile
        from ..models.user_profile import UserProfile

        d = dict(src_dict)
        authority = Authority.from_dict(d.pop("authority"))

        permissions = cast(list[str], d.pop("permissions"))

        from_ = d.pop("from", UNSET)

        to = d.pop("to", UNSET)

        editable = d.pop("editable", UNSET)

        _user = d.pop("user", UNSET)
        user: UserProfile | Unset
        if isinstance(_user, Unset):
            user = UNSET
        else:
            user = UserProfile.from_dict(_user)

        _group = d.pop("group", UNSET)
        group: GroupProfile | Unset
        if isinstance(_group, Unset):
            group = UNSET
        else:
            group = GroupProfile.from_dict(_group)

        ace = cls(
            authority=authority,
            permissions=permissions,
            from_=from_,
            to=to,
            editable=editable,
            user=user,
            group=group,
        )

        ace.additional_properties = d
        return ace

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
