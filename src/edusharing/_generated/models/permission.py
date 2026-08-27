from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.permission_role import PermissionRole

if TYPE_CHECKING:
    from ..models.authority import Authority


T = TypeVar("T", bound="Permission")


@_attrs_define
class Permission:
    """
    Attributes:
        authority (Authority):
        role (PermissionRole): Role within an assignment context
            * ASSIGNEE: User who is assigned to complete or participate in the assignment (only valid for assignments of
            type SUBMISSION)
            * COORDINATOR: User who can manage and oversee the assignment, including monitoring progress and managing
            participants
    """

    authority: Authority
    role: PermissionRole
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        authority = self.authority.to_dict()

        role = self.role.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "authority": authority,
                "role": role,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.authority import Authority

        d = dict(src_dict)
        authority = Authority.from_dict(d.pop("authority"))

        role = PermissionRole(d.pop("role"))

        permission = cls(
            authority=authority,
            role=role,
        )

        permission.additional_properties = d
        return permission

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
