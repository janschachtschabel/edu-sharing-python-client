from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.mds_list_columns import MdsListColumns


T = TypeVar("T", bound="MdsList")


@_attrs_define
class MdsList:
    """
    Attributes:
        id (str | Unset):
        columns (MdsListColumns | Unset):
    """

    id: str | Unset = UNSET
    columns: MdsListColumns | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        columns: dict[str, Any] | Unset = UNSET
        if not isinstance(self.columns, Unset):
            columns = self.columns.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if columns is not UNSET:
            field_dict["columns"] = columns

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.mds_list_columns import MdsListColumns

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        _columns = d.pop("columns", UNSET)
        columns: MdsListColumns | Unset
        if isinstance(_columns, Unset):
            columns = UNSET
        else:
            columns = MdsListColumns.from_dict(_columns)

        mds_list = cls(
            id=id,
            columns=columns,
        )

        mds_list.additional_properties = d
        return mds_list

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
