from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Content")


@_attrs_define
class Content:
    """Content information

    Attributes:
        url (str | Unset):
        original_url (str | Unset):
        hash_ (str | Unset):
        version (str | Unset):
    """

    url: str | Unset = UNSET
    original_url: str | Unset = UNSET
    hash_: str | Unset = UNSET
    version: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        url = self.url

        original_url = self.original_url

        hash_ = self.hash_

        version = self.version

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if url is not UNSET:
            field_dict["url"] = url
        if original_url is not UNSET:
            field_dict["originalUrl"] = original_url
        if hash_ is not UNSET:
            field_dict["hash"] = hash_
        if version is not UNSET:
            field_dict["version"] = version

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        url = d.pop("url", UNSET)

        original_url = d.pop("originalUrl", UNSET)

        hash_ = d.pop("hash", UNSET)

        version = d.pop("version", UNSET)

        content = cls(
            url=url,
            original_url=original_url,
            hash_=hash_,
            version=version,
        )

        content.additional_properties = d
        return content

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
