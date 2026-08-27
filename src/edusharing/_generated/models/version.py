from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Version")


@_attrs_define
class Version:
    """
    Attributes:
        full (str | Unset):
        major (str | Unset):
        minor (str | Unset):
        patch (str | Unset):
        qualifier (str | Unset):
        build (str | Unset):
    """

    full: str | Unset = UNSET
    major: str | Unset = UNSET
    minor: str | Unset = UNSET
    patch: str | Unset = UNSET
    qualifier: str | Unset = UNSET
    build: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        full = self.full

        major = self.major

        minor = self.minor

        patch = self.patch

        qualifier = self.qualifier

        build = self.build

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if full is not UNSET:
            field_dict["full"] = full
        if major is not UNSET:
            field_dict["major"] = major
        if minor is not UNSET:
            field_dict["minor"] = minor
        if patch is not UNSET:
            field_dict["patch"] = patch
        if qualifier is not UNSET:
            field_dict["qualifier"] = qualifier
        if build is not UNSET:
            field_dict["build"] = build

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        full = d.pop("full", UNSET)

        major = d.pop("major", UNSET)

        minor = d.pop("minor", UNSET)

        patch = d.pop("patch", UNSET)

        qualifier = d.pop("qualifier", UNSET)

        build = d.pop("build", UNSET)

        version = cls(
            full=full,
            major=major,
            minor=minor,
            patch=patch,
            qualifier=qualifier,
            build=build,
        )

        version.additional_properties = d
        return version

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
