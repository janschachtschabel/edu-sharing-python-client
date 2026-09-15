from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.mds_index_data_type import MdsIndexDataType
from ..types import UNSET, Unset

T = TypeVar("T", bound="MdsIndex")


@_attrs_define
class MdsIndex:
    """
    Attributes:
        data_type (MdsIndexDataType | Unset):
    """

    data_type: MdsIndexDataType | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data_type: str | Unset = UNSET
        if not isinstance(self.data_type, Unset):
            data_type = self.data_type.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if data_type is not UNSET:
            field_dict["dataType"] = data_type

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        _data_type = d.pop("dataType", UNSET)
        data_type: MdsIndexDataType | Unset
        if isinstance(_data_type, Unset):
            data_type = UNSET
        else:
            data_type = MdsIndexDataType(_data_type)

        mds_index = cls(
            data_type=data_type,
        )

        mds_index.additional_properties = d
        return mds_index

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
