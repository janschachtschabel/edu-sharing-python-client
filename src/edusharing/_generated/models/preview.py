from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Preview")


@_attrs_define
class Preview:
    """Preview/Thumbnail information

    Attributes:
        url (str):
        width (int):
        height (int):
        is_icon (bool):
        type_ (str | Unset):
        mimetype (str | Unset):
        data (str | Unset):
        is_generated (bool | Unset):
    """

    url: str
    width: int
    height: int
    is_icon: bool
    type_: str | Unset = UNSET
    mimetype: str | Unset = UNSET
    data: str | Unset = UNSET
    is_generated: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        url = self.url

        width = self.width

        height = self.height

        is_icon = self.is_icon

        type_ = self.type_

        mimetype = self.mimetype

        data = self.data

        is_generated = self.is_generated

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "url": url,
                "width": width,
                "height": height,
                "isIcon": is_icon,
            }
        )
        if type_ is not UNSET:
            field_dict["type"] = type_
        if mimetype is not UNSET:
            field_dict["mimetype"] = mimetype
        if data is not UNSET:
            field_dict["data"] = data
        if is_generated is not UNSET:
            field_dict["isGenerated"] = is_generated

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        url = d.pop("url")

        width = d.pop("width")

        height = d.pop("height")

        is_icon = d.pop("isIcon")

        type_ = d.pop("type", UNSET)

        mimetype = d.pop("mimetype", UNSET)

        data = d.pop("data", UNSET)

        is_generated = d.pop("isGenerated", UNSET)

        preview = cls(
            url=url,
            width=width,
            height=height,
            is_icon=is_icon,
            type_=type_,
            mimetype=mimetype,
            data=data,
            is_generated=is_generated,
        )

        preview.additional_properties = d
        return preview

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
