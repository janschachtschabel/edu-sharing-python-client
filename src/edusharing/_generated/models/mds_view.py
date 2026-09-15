from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.mds_view_rel import MdsViewRel
from ..types import UNSET, Unset

T = TypeVar("T", bound="MdsView")


@_attrs_define
class MdsView:
    """
    Attributes:
        id (str | Unset):
        caption (str | Unset):
        icon (str | Unset):
        html (str | Unset):
        rel (MdsViewRel | Unset):
        hide_if_empty (bool | Unset):
        is_extended (bool | Unset):
    """

    id: str | Unset = UNSET
    caption: str | Unset = UNSET
    icon: str | Unset = UNSET
    html: str | Unset = UNSET
    rel: MdsViewRel | Unset = UNSET
    hide_if_empty: bool | Unset = UNSET
    is_extended: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        caption = self.caption

        icon = self.icon

        html = self.html

        rel: str | Unset = UNSET
        if not isinstance(self.rel, Unset):
            rel = self.rel.value

        hide_if_empty = self.hide_if_empty

        is_extended = self.is_extended

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if caption is not UNSET:
            field_dict["caption"] = caption
        if icon is not UNSET:
            field_dict["icon"] = icon
        if html is not UNSET:
            field_dict["html"] = html
        if rel is not UNSET:
            field_dict["rel"] = rel
        if hide_if_empty is not UNSET:
            field_dict["hideIfEmpty"] = hide_if_empty
        if is_extended is not UNSET:
            field_dict["isExtended"] = is_extended

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        caption = d.pop("caption", UNSET)

        icon = d.pop("icon", UNSET)

        html = d.pop("html", UNSET)

        _rel = d.pop("rel", UNSET)
        rel: MdsViewRel | Unset
        if isinstance(_rel, Unset):
            rel = UNSET
        else:
            rel = MdsViewRel(_rel)

        hide_if_empty = d.pop("hideIfEmpty", UNSET)

        is_extended = d.pop("isExtended", UNSET)

        mds_view = cls(
            id=id,
            caption=caption,
            icon=icon,
            html=html,
            rel=rel,
            hide_if_empty=hide_if_empty,
            is_extended=is_extended,
        )

        mds_view.additional_properties = d
        return mds_view

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
