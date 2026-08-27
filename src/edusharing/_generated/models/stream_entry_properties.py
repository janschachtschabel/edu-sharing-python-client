from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.stream_entry_properties_additional_property import (
        StreamEntryPropertiesAdditionalProperty,
    )


T = TypeVar("T", bound="StreamEntryProperties")


@_attrs_define
class StreamEntryProperties:
    """ """

    additional_properties: dict[str, StreamEntryPropertiesAdditionalProperty] = _attrs_field(
        init=False, factory=dict
    )

    def to_dict(self) -> dict[str, Any]:

        field_dict: dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = prop.to_dict()

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.stream_entry_properties_additional_property import (
            StreamEntryPropertiesAdditionalProperty,
        )

        d = dict(src_dict)
        stream_entry_properties = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():
            additional_property = StreamEntryPropertiesAdditionalProperty.from_dict(prop_dict)

            additional_properties[prop_name] = additional_property

        stream_entry_properties.additional_properties = additional_properties
        return stream_entry_properties

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> StreamEntryPropertiesAdditionalProperty:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: StreamEntryPropertiesAdditionalProperty) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
