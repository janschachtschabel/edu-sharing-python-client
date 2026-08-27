from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.metadata_set_info import MetadataSetInfo


T = TypeVar("T", bound="MdsEntries")


@_attrs_define
class MdsEntries:
    """
    Attributes:
        metadatasets (list[MetadataSetInfo]):
    """

    metadatasets: list[MetadataSetInfo]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        metadatasets = []
        for metadatasets_item_data in self.metadatasets:
            metadatasets_item = metadatasets_item_data.to_dict()
            metadatasets.append(metadatasets_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "metadatasets": metadatasets,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.metadata_set_info import MetadataSetInfo

        d = dict(src_dict)
        metadatasets = []
        _metadatasets = d.pop("metadatasets")
        for metadatasets_item_data in _metadatasets:
            metadatasets_item = MetadataSetInfo.from_dict(metadatasets_item_data)

            metadatasets.append(metadatasets_item)

        mds_entries = cls(
            metadatasets=metadatasets,
        )

        mds_entries.additional_properties = d
        return mds_entries

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
