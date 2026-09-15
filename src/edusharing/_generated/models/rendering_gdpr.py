from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="RenderingGdpr")


@_attrs_define
class RenderingGdpr:
    """GDPR configuration for rendering privacy

    Attributes:
        matcher (str | Unset): Pattern to match against file types
        name (str | Unset): Display name for privacy notice
        privacy_information_url (str | Unset): URL to privacy information
    """

    matcher: str | Unset = UNSET
    name: str | Unset = UNSET
    privacy_information_url: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        matcher = self.matcher

        name = self.name

        privacy_information_url = self.privacy_information_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if matcher is not UNSET:
            field_dict["matcher"] = matcher
        if name is not UNSET:
            field_dict["name"] = name
        if privacy_information_url is not UNSET:
            field_dict["privacyInformationUrl"] = privacy_information_url

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        matcher = d.pop("matcher", UNSET)

        name = d.pop("name", UNSET)

        privacy_information_url = d.pop("privacyInformationUrl", UNSET)

        rendering_gdpr = cls(
            matcher=matcher,
            name=name,
            privacy_information_url=privacy_information_url,
        )

        rendering_gdpr.additional_properties = d
        return rendering_gdpr

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
