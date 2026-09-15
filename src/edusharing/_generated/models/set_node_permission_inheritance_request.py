from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.node_permission_inheritance import NodePermissionInheritance


T = TypeVar("T", bound="SetNodePermissionInheritanceRequest")


@_attrs_define
class SetNodePermissionInheritanceRequest:
    """
    Attributes:
        inheritance_list (list[NodePermissionInheritance]):
    """

    inheritance_list: list[NodePermissionInheritance]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        inheritance_list = []
        for inheritance_list_item_data in self.inheritance_list:
            inheritance_list_item = inheritance_list_item_data.to_dict()
            inheritance_list.append(inheritance_list_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "inheritanceList": inheritance_list,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.node_permission_inheritance import NodePermissionInheritance

        d = dict(src_dict)
        inheritance_list = []
        _inheritance_list = d.pop("inheritanceList")
        for inheritance_list_item_data in _inheritance_list:
            inheritance_list_item = NodePermissionInheritance.from_dict(inheritance_list_item_data)

            inheritance_list.append(inheritance_list_item)

        set_node_permission_inheritance_request = cls(
            inheritance_list=inheritance_list,
        )

        set_node_permission_inheritance_request.additional_properties = d
        return set_node_permission_inheritance_request

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
