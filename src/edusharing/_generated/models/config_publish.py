from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ConfigPublish")


@_attrs_define
class ConfigPublish:
    """Publishing configuration

    Attributes:
        license_mandatory (bool | Unset):
        author_mandatory (bool | Unset):
    """

    license_mandatory: bool | Unset = UNSET
    author_mandatory: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        license_mandatory = self.license_mandatory

        author_mandatory = self.author_mandatory

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if license_mandatory is not UNSET:
            field_dict["licenseMandatory"] = license_mandatory
        if author_mandatory is not UNSET:
            field_dict["authorMandatory"] = author_mandatory

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        license_mandatory = d.pop("licenseMandatory", UNSET)

        author_mandatory = d.pop("authorMandatory", UNSET)

        config_publish = cls(
            license_mandatory=license_mandatory,
            author_mandatory=author_mandatory,
        )

        config_publish.additional_properties = d
        return config_publish

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
