from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="General")


@_attrs_define
class General:
    """
    Attributes:
        referenced_in_name (str | Unset):
        referenced_in_type (str | Unset):
        referenced_in_instance (str | Unset):
    """

    referenced_in_name: str | Unset = UNSET
    referenced_in_type: str | Unset = UNSET
    referenced_in_instance: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        referenced_in_name = self.referenced_in_name

        referenced_in_type = self.referenced_in_type

        referenced_in_instance = self.referenced_in_instance

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if referenced_in_name is not UNSET:
            field_dict["referencedInName"] = referenced_in_name
        if referenced_in_type is not UNSET:
            field_dict["referencedInType"] = referenced_in_type
        if referenced_in_instance is not UNSET:
            field_dict["referencedInInstance"] = referenced_in_instance

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        referenced_in_name = d.pop("referencedInName", UNSET)

        referenced_in_type = d.pop("referencedInType", UNSET)

        referenced_in_instance = d.pop("referencedInInstance", UNSET)

        general = cls(
            referenced_in_name=referenced_in_name,
            referenced_in_type=referenced_in_type,
            referenced_in_instance=referenced_in_instance,
        )

        general.additional_properties = d
        return general

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
