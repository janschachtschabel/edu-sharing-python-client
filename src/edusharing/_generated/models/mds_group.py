from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.mds_group_rendering import MdsGroupRendering
from ..types import UNSET, Unset

T = TypeVar("T", bound="MdsGroup")


@_attrs_define
class MdsGroup:
    """
    Attributes:
        id (str | Unset):
        views (list[str] | Unset):
        rendering (MdsGroupRendering | Unset):
    """

    id: str | Unset = UNSET
    views: list[str] | Unset = UNSET
    rendering: MdsGroupRendering | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        views: list[str] | Unset = UNSET
        if not isinstance(self.views, Unset):
            views = self.views

        rendering: str | Unset = UNSET
        if not isinstance(self.rendering, Unset):
            rendering = self.rendering.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if views is not UNSET:
            field_dict["views"] = views
        if rendering is not UNSET:
            field_dict["rendering"] = rendering

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        views = cast(list[str], d.pop("views", UNSET))

        _rendering = d.pop("rendering", UNSET)
        rendering: MdsGroupRendering | Unset
        if isinstance(_rendering, Unset):
            rendering = UNSET
        else:
            rendering = MdsGroupRendering(_rendering)

        mds_group = cls(
            id=id,
            views=views,
            rendering=rendering,
        )

        mds_group.additional_properties = d
        return mds_group

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
