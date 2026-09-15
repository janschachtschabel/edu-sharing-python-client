from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ChildobjectsConfig")


@_attrs_define
class ChildobjectsConfig:
    """
    Attributes:
        ignored_inherit_metadata (list[str] | Unset):
    """

    ignored_inherit_metadata: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ignored_inherit_metadata: list[str] | Unset = UNSET
        if not isinstance(self.ignored_inherit_metadata, Unset):
            ignored_inherit_metadata = self.ignored_inherit_metadata

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if ignored_inherit_metadata is not UNSET:
            field_dict["ignoredInheritMetadata"] = ignored_inherit_metadata

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        ignored_inherit_metadata = cast(list[str], d.pop("ignoredInheritMetadata", UNSET))

        childobjects_config = cls(
            ignored_inherit_metadata=ignored_inherit_metadata,
        )

        childobjects_config.additional_properties = d
        return childobjects_config

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
