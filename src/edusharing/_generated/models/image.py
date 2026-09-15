from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Image")


@_attrs_define
class Image:
    """Array of image replacements (src match, replace with)

    Attributes:
        src (str | Unset): Original image URL to match (matched with endsWith)
        replace (str | Unset): Replacement image URL
    """

    src: str | Unset = UNSET
    replace: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        src = self.src

        replace = self.replace

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if src is not UNSET:
            field_dict["src"] = src
        if replace is not UNSET:
            field_dict["replace"] = replace

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        src = d.pop("src", UNSET)

        replace = d.pop("replace", UNSET)

        image = cls(
            src=src,
            replace=replace,
        )

        image.additional_properties = d
        return image

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
