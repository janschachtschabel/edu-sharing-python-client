from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GdprEntry")


@_attrs_define
class GdprEntry:
    """GDPR entry definitions

    Attributes:
        regex (str | Unset): Regex pattern to match data types
        name (str | Unset): Display name for this GDPR entry
        ref (str | Unset): Reference identifier
    """

    regex: str | Unset = UNSET
    name: str | Unset = UNSET
    ref: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        regex = self.regex

        name = self.name

        ref = self.ref

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if regex is not UNSET:
            field_dict["regex"] = regex
        if name is not UNSET:
            field_dict["name"] = name
        if ref is not UNSET:
            field_dict["ref"] = ref

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        regex = d.pop("regex", UNSET)

        name = d.pop("name", UNSET)

        ref = d.pop("ref", UNSET)

        gdpr_entry = cls(
            regex=regex,
            name=name,
            ref=ref,
        )

        gdpr_entry.additional_properties = d
        return gdpr_entry

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
