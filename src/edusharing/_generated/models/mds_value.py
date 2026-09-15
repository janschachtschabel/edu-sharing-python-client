from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="MdsValue")


@_attrs_define
class MdsValue:
    """
    Attributes:
        id (str):
        caption (str | Unset):
        icon (str | Unset):
        description (str | Unset):
        parent (str | Unset):
        url (str | Unset):
        alternative_ids (list[str] | Unset):
        abbreviation (str | Unset):
    """

    id: str
    caption: str | Unset = UNSET
    icon: str | Unset = UNSET
    description: str | Unset = UNSET
    parent: str | Unset = UNSET
    url: str | Unset = UNSET
    alternative_ids: list[str] | Unset = UNSET
    abbreviation: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        caption = self.caption

        icon = self.icon

        description = self.description

        parent = self.parent

        url = self.url

        alternative_ids: list[str] | Unset = UNSET
        if not isinstance(self.alternative_ids, Unset):
            alternative_ids = self.alternative_ids

        abbreviation = self.abbreviation

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
            }
        )
        if caption is not UNSET:
            field_dict["caption"] = caption
        if icon is not UNSET:
            field_dict["icon"] = icon
        if description is not UNSET:
            field_dict["description"] = description
        if parent is not UNSET:
            field_dict["parent"] = parent
        if url is not UNSET:
            field_dict["url"] = url
        if alternative_ids is not UNSET:
            field_dict["alternativeIds"] = alternative_ids
        if abbreviation is not UNSET:
            field_dict["abbreviation"] = abbreviation

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        id = d.pop("id")

        caption = d.pop("caption", UNSET)

        icon = d.pop("icon", UNSET)

        description = d.pop("description", UNSET)

        parent = d.pop("parent", UNSET)

        url = d.pop("url", UNSET)

        alternative_ids = cast(list[str], d.pop("alternativeIds", UNSET))

        abbreviation = d.pop("abbreviation", UNSET)

        mds_value = cls(
            id=id,
            caption=caption,
            icon=icon,
            description=description,
            parent=parent,
            url=url,
            alternative_ids=alternative_ids,
            abbreviation=abbreviation,
        )

        mds_value.additional_properties = d
        return mds_value

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
