from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.connector_file_type import ConnectorFileType


T = TypeVar("T", bound="Connector")


@_attrs_define
class Connector:
    """
    Attributes:
        show_new (bool):
        id (str | Unset):
        icon (str | Unset):
        parameters (list[str] | Unset):
        filetypes (list[ConnectorFileType] | Unset):
        only_desktop (bool | Unset):
        has_view_mode (bool | Unset):
        mds_group (str | Unset):
    """

    show_new: bool
    id: str | Unset = UNSET
    icon: str | Unset = UNSET
    parameters: list[str] | Unset = UNSET
    filetypes: list[ConnectorFileType] | Unset = UNSET
    only_desktop: bool | Unset = UNSET
    has_view_mode: bool | Unset = UNSET
    mds_group: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        show_new = self.show_new

        id = self.id

        icon = self.icon

        parameters: list[str] | Unset = UNSET
        if not isinstance(self.parameters, Unset):
            parameters = self.parameters

        filetypes: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.filetypes, Unset):
            filetypes = []
            for filetypes_item_data in self.filetypes:
                filetypes_item = filetypes_item_data.to_dict()
                filetypes.append(filetypes_item)

        only_desktop = self.only_desktop

        has_view_mode = self.has_view_mode

        mds_group = self.mds_group

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "showNew": show_new,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id
        if icon is not UNSET:
            field_dict["icon"] = icon
        if parameters is not UNSET:
            field_dict["parameters"] = parameters
        if filetypes is not UNSET:
            field_dict["filetypes"] = filetypes
        if only_desktop is not UNSET:
            field_dict["onlyDesktop"] = only_desktop
        if has_view_mode is not UNSET:
            field_dict["hasViewMode"] = has_view_mode
        if mds_group is not UNSET:
            field_dict["mdsGroup"] = mds_group

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.connector_file_type import ConnectorFileType

        d = dict(src_dict)
        show_new = d.pop("showNew")

        id = d.pop("id", UNSET)

        icon = d.pop("icon", UNSET)

        parameters = cast(list[str], d.pop("parameters", UNSET))

        _filetypes = d.pop("filetypes", UNSET)
        filetypes: list[ConnectorFileType] | Unset = UNSET
        if _filetypes is not UNSET:
            filetypes = []
            for filetypes_item_data in _filetypes:
                filetypes_item = ConnectorFileType.from_dict(filetypes_item_data)

                filetypes.append(filetypes_item)

        only_desktop = d.pop("onlyDesktop", UNSET)

        has_view_mode = d.pop("hasViewMode", UNSET)

        mds_group = d.pop("mdsGroup", UNSET)

        connector = cls(
            show_new=show_new,
            id=id,
            icon=icon,
            parameters=parameters,
            filetypes=filetypes,
            only_desktop=only_desktop,
            has_view_mode=has_view_mode,
            mds_group=mds_group,
        )

        connector.additional_properties = d
        return connector

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
