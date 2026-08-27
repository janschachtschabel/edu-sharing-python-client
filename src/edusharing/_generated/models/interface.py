from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.interface_format import InterfaceFormat
from ..models.interface_type import InterfaceType
from ..types import UNSET, Unset

T = TypeVar("T", bound="Interface")


@_attrs_define
class Interface:
    """
    Attributes:
        url (str | Unset):
        set_ (str | Unset):
        metadata_prefix (str | Unset):
        documentation (str | Unset):
        format_ (InterfaceFormat | Unset):
        type_ (InterfaceType | Unset):
    """

    url: str | Unset = UNSET
    set_: str | Unset = UNSET
    metadata_prefix: str | Unset = UNSET
    documentation: str | Unset = UNSET
    format_: InterfaceFormat | Unset = UNSET
    type_: InterfaceType | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        url = self.url

        set_ = self.set_

        metadata_prefix = self.metadata_prefix

        documentation = self.documentation

        format_: str | Unset = UNSET
        if not isinstance(self.format_, Unset):
            format_ = self.format_.value

        type_: str | Unset = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if url is not UNSET:
            field_dict["url"] = url
        if set_ is not UNSET:
            field_dict["set"] = set_
        if metadata_prefix is not UNSET:
            field_dict["metadataPrefix"] = metadata_prefix
        if documentation is not UNSET:
            field_dict["documentation"] = documentation
        if format_ is not UNSET:
            field_dict["format"] = format_
        if type_ is not UNSET:
            field_dict["type"] = type_

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        url = d.pop("url", UNSET)

        set_ = d.pop("set", UNSET)

        metadata_prefix = d.pop("metadataPrefix", UNSET)

        documentation = d.pop("documentation", UNSET)

        _format_ = d.pop("format", UNSET)
        format_: InterfaceFormat | Unset
        if isinstance(_format_, Unset):
            format_ = UNSET
        else:
            format_ = InterfaceFormat(_format_)

        _type_ = d.pop("type", UNSET)
        type_: InterfaceType | Unset
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = InterfaceType(_type_)

        interface = cls(
            url=url,
            set_=set_,
            metadata_prefix=metadata_prefix,
            documentation=documentation,
            format_=format_,
            type_=type_,
        )

        interface.additional_properties = d
        return interface

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
