from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="HelpMenuOptions")


@_attrs_define
class HelpMenuOptions:
    """Custom help menu options (key, icon, URL) - replaces helpUrl + whatsNewUrl

    Attributes:
        key (str | Unset): Button ID (used in translation: HELP.key or related)
        icon (str | Unset): Material Design icon identifier
        url (str | Unset): URL to open on button click
    """

    key: str | Unset = UNSET
    icon: str | Unset = UNSET
    url: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        key = self.key

        icon = self.icon

        url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if key is not UNSET:
            field_dict["key"] = key
        if icon is not UNSET:
            field_dict["icon"] = icon
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        key = d.pop("key", UNSET)

        icon = d.pop("icon", UNSET)

        url = d.pop("url", UNSET)

        help_menu_options = cls(
            key=key,
            icon=icon,
            url=url,
        )

        help_menu_options.additional_properties = d
        return help_menu_options

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
