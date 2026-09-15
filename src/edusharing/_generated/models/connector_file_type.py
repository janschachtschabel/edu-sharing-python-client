from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ConnectorFileType")


@_attrs_define
class ConnectorFileType:
    """
    Attributes:
        ccressourceversion (str | Unset):
        ccressourcetype (str | Unset):
        ccresourcesubtype (str | Unset):
        editor_type (str | Unset):
        mimetype (str | Unset):
        filetype (str | Unset):
        creatable (bool | Unset):
        editable (bool | Unset):
    """

    ccressourceversion: str | Unset = UNSET
    ccressourcetype: str | Unset = UNSET
    ccresourcesubtype: str | Unset = UNSET
    editor_type: str | Unset = UNSET
    mimetype: str | Unset = UNSET
    filetype: str | Unset = UNSET
    creatable: bool | Unset = UNSET
    editable: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ccressourceversion = self.ccressourceversion

        ccressourcetype = self.ccressourcetype

        ccresourcesubtype = self.ccresourcesubtype

        editor_type = self.editor_type

        mimetype = self.mimetype

        filetype = self.filetype

        creatable = self.creatable

        editable = self.editable

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if ccressourceversion is not UNSET:
            field_dict["ccressourceversion"] = ccressourceversion
        if ccressourcetype is not UNSET:
            field_dict["ccressourcetype"] = ccressourcetype
        if ccresourcesubtype is not UNSET:
            field_dict["ccresourcesubtype"] = ccresourcesubtype
        if editor_type is not UNSET:
            field_dict["editorType"] = editor_type
        if mimetype is not UNSET:
            field_dict["mimetype"] = mimetype
        if filetype is not UNSET:
            field_dict["filetype"] = filetype
        if creatable is not UNSET:
            field_dict["creatable"] = creatable
        if editable is not UNSET:
            field_dict["editable"] = editable

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        ccressourceversion = d.pop("ccressourceversion", UNSET)

        ccressourcetype = d.pop("ccressourcetype", UNSET)

        ccresourcesubtype = d.pop("ccresourcesubtype", UNSET)

        editor_type = d.pop("editorType", UNSET)

        mimetype = d.pop("mimetype", UNSET)

        filetype = d.pop("filetype", UNSET)

        creatable = d.pop("creatable", UNSET)

        editable = d.pop("editable", UNSET)

        connector_file_type = cls(
            ccressourceversion=ccressourceversion,
            ccressourcetype=ccressourcetype,
            ccresourcesubtype=ccresourcesubtype,
            editor_type=editor_type,
            mimetype=mimetype,
            filetype=filetype,
            creatable=creatable,
            editable=editable,
        )

        connector_file_type.additional_properties = d
        return connector_file_type

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
