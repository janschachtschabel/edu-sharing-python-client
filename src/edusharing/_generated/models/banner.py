from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Banner")


@_attrs_define
class Banner:
    """Banner configuration (URL, href link, components where shown)

    Attributes:
        url (str | Unset): URL to banner image (fixed 150px height, wide width recommended)
        href (str | Unset): Link to open on banner click
        components (list[str] | Unset): Components where banner should appear: 'search', 'render', 'collections'
    """

    url: str | Unset = UNSET
    href: str | Unset = UNSET
    components: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        url = self.url

        href = self.href

        components: list[str] | Unset = UNSET
        if not isinstance(self.components, Unset):
            components = self.components

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if url is not UNSET:
            field_dict["url"] = url
        if href is not UNSET:
            field_dict["href"] = href
        if components is not UNSET:
            field_dict["components"] = components

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        url = d.pop("url", UNSET)

        href = d.pop("href", UNSET)

        components = cast(list[str], d.pop("components", UNSET))

        banner = cls(
            url=url,
            href=href,
            components=components,
        )

        banner.additional_properties = d
        return banner

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
