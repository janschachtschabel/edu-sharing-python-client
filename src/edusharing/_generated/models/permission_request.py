from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.permission_request_role import PermissionRequestRole

T = TypeVar("T", bound="PermissionRequest")


@_attrs_define
class PermissionRequest:
    """
    Attributes:
        authority_name (str):
        role (PermissionRequestRole): Role within an assignment context
            * ASSIGNEE: User who is assigned to complete or participate in the assignment (only valid for assignments of
            type SUBMISSION)
            * COORDINATOR: User who can manage and oversee the assignment, including monitoring progress and managing
            participants
    """

    authority_name: str
    role: PermissionRequestRole
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        authority_name = self.authority_name

        role = self.role.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "authorityName": authority_name,
                "role": role,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        authority_name = d.pop("authorityName")

        role = PermissionRequestRole(d.pop("role"))

        permission_request = cls(
            authority_name=authority_name,
            role=role,
        )

        permission_request.additional_properties = d
        return permission_request

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
