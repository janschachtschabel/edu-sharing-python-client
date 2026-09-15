from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.ace import ACE
    from ..models.acl import ACL


T = TypeVar("T", bound="NodePermissions")


@_attrs_define
class NodePermissions:
    """
    Attributes:
        local_permissions (ACL):
        inherited_permissions (list[ACE]):
    """

    local_permissions: ACL
    inherited_permissions: list[ACE]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        local_permissions = self.local_permissions.to_dict()

        inherited_permissions = []
        for inherited_permissions_item_data in self.inherited_permissions:
            inherited_permissions_item = inherited_permissions_item_data.to_dict()
            inherited_permissions.append(inherited_permissions_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "localPermissions": local_permissions,
                "inheritedPermissions": inherited_permissions,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.ace import ACE
        from ..models.acl import ACL

        d = dict(src_dict)
        local_permissions = ACL.from_dict(d.pop("localPermissions"))

        inherited_permissions = []
        _inherited_permissions = d.pop("inheritedPermissions")
        for inherited_permissions_item_data in _inherited_permissions:
            inherited_permissions_item = ACE.from_dict(inherited_permissions_item_data)

            inherited_permissions.append(inherited_permissions_item)

        node_permissions = cls(
            local_permissions=local_permissions,
            inherited_permissions=inherited_permissions,
        )

        node_permissions.additional_properties = d
        return node_permissions

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
