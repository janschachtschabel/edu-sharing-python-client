from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AvailableMds")


@_attrs_define
class AvailableMds:
    """Array of allowed metadata sets per repository

    Attributes:
        repository (str | Unset): Repository ID ('-home-' for local, or app-id from properties file)
        mds (list[str] | Unset): Array of allowed metadata set IDs for this repository
    """

    repository: str | Unset = UNSET
    mds: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        repository = self.repository

        mds: list[str] | Unset = UNSET
        if not isinstance(self.mds, Unset):
            mds = self.mds

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if repository is not UNSET:
            field_dict["repository"] = repository
        if mds is not UNSET:
            field_dict["mds"] = mds

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        repository = d.pop("repository", UNSET)

        mds = cast(list[str], d.pop("mds", UNSET))

        available_mds = cls(
            repository=repository,
            mds=mds,
        )

        available_mds.additional_properties = d
        return available_mds

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
