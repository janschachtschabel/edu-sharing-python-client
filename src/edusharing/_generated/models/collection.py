from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.user import User


T = TypeVar("T", bound="Collection")


@_attrs_define
class Collection:
    """
    Attributes:
        level0 (bool):
        title (str):
        type_ (str):
        from_user (bool):
        description (str | Unset):
        viewtype (str | Unset):
        order_mode (str | Unset):
        x (int | Unset):
        y (int | Unset):
        z (int | Unset):
        color (str | Unset):
        owner (User | Unset):
        pinned (bool | Unset):
        child_collections_count (int | Unset):
        child_references_count (int | Unset):
        scope (str | Unset):
        author_freetext (str | Unset):
        order_ascending (bool | Unset):
    """

    level0: bool
    title: str
    type_: str
    from_user: bool
    description: str | Unset = UNSET
    viewtype: str | Unset = UNSET
    order_mode: str | Unset = UNSET
    x: int | Unset = UNSET
    y: int | Unset = UNSET
    z: int | Unset = UNSET
    color: str | Unset = UNSET
    owner: User | Unset = UNSET
    pinned: bool | Unset = UNSET
    child_collections_count: int | Unset = UNSET
    child_references_count: int | Unset = UNSET
    scope: str | Unset = UNSET
    author_freetext: str | Unset = UNSET
    order_ascending: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        level0 = self.level0

        title = self.title

        type_ = self.type_

        from_user = self.from_user

        description = self.description

        viewtype = self.viewtype

        order_mode = self.order_mode

        x = self.x

        y = self.y

        z = self.z

        color = self.color

        owner: dict[str, Any] | Unset = UNSET
        if not isinstance(self.owner, Unset):
            owner = self.owner.to_dict()

        pinned = self.pinned

        child_collections_count = self.child_collections_count

        child_references_count = self.child_references_count

        scope = self.scope

        author_freetext = self.author_freetext

        order_ascending = self.order_ascending

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "level0": level0,
                "title": title,
                "type": type_,
                "fromUser": from_user,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if viewtype is not UNSET:
            field_dict["viewtype"] = viewtype
        if order_mode is not UNSET:
            field_dict["orderMode"] = order_mode
        if x is not UNSET:
            field_dict["x"] = x
        if y is not UNSET:
            field_dict["y"] = y
        if z is not UNSET:
            field_dict["z"] = z
        if color is not UNSET:
            field_dict["color"] = color
        if owner is not UNSET:
            field_dict["owner"] = owner
        if pinned is not UNSET:
            field_dict["pinned"] = pinned
        if child_collections_count is not UNSET:
            field_dict["childCollectionsCount"] = child_collections_count
        if child_references_count is not UNSET:
            field_dict["childReferencesCount"] = child_references_count
        if scope is not UNSET:
            field_dict["scope"] = scope
        if author_freetext is not UNSET:
            field_dict["authorFreetext"] = author_freetext
        if order_ascending is not UNSET:
            field_dict["orderAscending"] = order_ascending

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.user import User

        d = dict(src_dict)
        level0 = d.pop("level0")

        title = d.pop("title")

        type_ = d.pop("type")

        from_user = d.pop("fromUser")

        description = d.pop("description", UNSET)

        viewtype = d.pop("viewtype", UNSET)

        order_mode = d.pop("orderMode", UNSET)

        x = d.pop("x", UNSET)

        y = d.pop("y", UNSET)

        z = d.pop("z", UNSET)

        color = d.pop("color", UNSET)

        _owner = d.pop("owner", UNSET)
        owner: User | Unset
        if isinstance(_owner, Unset):
            owner = UNSET
        else:
            owner = User.from_dict(_owner)

        pinned = d.pop("pinned", UNSET)

        child_collections_count = d.pop("childCollectionsCount", UNSET)

        child_references_count = d.pop("childReferencesCount", UNSET)

        scope = d.pop("scope", UNSET)

        author_freetext = d.pop("authorFreetext", UNSET)

        order_ascending = d.pop("orderAscending", UNSET)

        collection = cls(
            level0=level0,
            title=title,
            type_=type_,
            from_user=from_user,
            description=description,
            viewtype=viewtype,
            order_mode=order_mode,
            x=x,
            y=y,
            z=z,
            color=color,
            owner=owner,
            pinned=pinned,
            child_collections_count=child_collections_count,
            child_references_count=child_references_count,
            scope=scope,
            author_freetext=author_freetext,
            order_ascending=order_ascending,
        )

        collection.additional_properties = d
        return collection

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
