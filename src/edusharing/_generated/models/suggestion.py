from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Suggestion")


@_attrs_define
class Suggestion:
    """
    Attributes:
        replacement_string (str):
        display_string (str):
        translation (str | Unset):
        key (str | Unset):
    """

    replacement_string: str
    display_string: str
    translation: str | Unset = UNSET
    key: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        replacement_string = self.replacement_string

        display_string = self.display_string

        translation = self.translation

        key = self.key

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "replacementString": replacement_string,
                "displayString": display_string,
            }
        )
        if translation is not UNSET:
            field_dict["translation"] = translation
        if key is not UNSET:
            field_dict["key"] = key

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        replacement_string = d.pop("replacementString")

        display_string = d.pop("displayString")

        translation = d.pop("translation", UNSET)

        key = d.pop("key", UNSET)

        suggestion = cls(
            replacement_string=replacement_string,
            display_string=display_string,
            translation=translation,
            key=key,
        )

        suggestion.additional_properties = d
        return suggestion

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
