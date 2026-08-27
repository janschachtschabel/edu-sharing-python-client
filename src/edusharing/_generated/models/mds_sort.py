from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.mds_sort_column import MdsSortColumn
    from ..models.mds_sort_default import MdsSortDefault


T = TypeVar("T", bound="MdsSort")


@_attrs_define
class MdsSort:
    """
    Attributes:
        id (str):
        columns (list[MdsSortColumn] | Unset):
        default (MdsSortDefault | Unset):
        default_search (MdsSortDefault | Unset):
    """

    id: str
    columns: list[MdsSortColumn] | Unset = UNSET
    default: MdsSortDefault | Unset = UNSET
    default_search: MdsSortDefault | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        columns: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.columns, Unset):
            columns = []
            for columns_item_data in self.columns:
                columns_item = columns_item_data.to_dict()
                columns.append(columns_item)

        default: dict[str, Any] | Unset = UNSET
        if not isinstance(self.default, Unset):
            default = self.default.to_dict()

        default_search: dict[str, Any] | Unset = UNSET
        if not isinstance(self.default_search, Unset):
            default_search = self.default_search.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
            }
        )
        if columns is not UNSET:
            field_dict["columns"] = columns
        if default is not UNSET:
            field_dict["default"] = default
        if default_search is not UNSET:
            field_dict["defaultSearch"] = default_search

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.mds_sort_column import MdsSortColumn
        from ..models.mds_sort_default import MdsSortDefault

        d = dict(src_dict)
        id = d.pop("id")

        _columns = d.pop("columns", UNSET)
        columns: list[MdsSortColumn] | Unset = UNSET
        if _columns is not UNSET:
            columns = []
            for columns_item_data in _columns:
                columns_item = MdsSortColumn.from_dict(columns_item_data)

                columns.append(columns_item)

        _default = d.pop("default", UNSET)
        default: MdsSortDefault | Unset
        if isinstance(_default, Unset):
            default = UNSET
        else:
            default = MdsSortDefault.from_dict(_default)

        _default_search = d.pop("defaultSearch", UNSET)
        default_search: MdsSortDefault | Unset
        if isinstance(_default_search, Unset):
            default_search = UNSET
        else:
            default_search = MdsSortDefault.from_dict(_default_search)

        mds_sort = cls(
            id=id,
            columns=columns,
            default=default,
            default_search=default_search,
        )

        mds_sort.additional_properties = d
        return mds_sort

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
