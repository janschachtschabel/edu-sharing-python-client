from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.node import Node
    from ..models.person import Person


T = TypeVar("T", bound="SharingInfo")


@_attrs_define
class SharingInfo:
    """
    Attributes:
        password_matches (bool | Unset):
        password (bool | Unset):
        expired (bool | Unset):
        invited_by (Person | Unset): Owner of the node
        node (Node | Unset):
    """

    password_matches: bool | Unset = UNSET
    password: bool | Unset = UNSET
    expired: bool | Unset = UNSET
    invited_by: Person | Unset = UNSET
    node: Node | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        password_matches = self.password_matches

        password = self.password

        expired = self.expired

        invited_by: dict[str, Any] | Unset = UNSET
        if not isinstance(self.invited_by, Unset):
            invited_by = self.invited_by.to_dict()

        node: dict[str, Any] | Unset = UNSET
        if not isinstance(self.node, Unset):
            node = self.node.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if password_matches is not UNSET:
            field_dict["passwordMatches"] = password_matches
        if password is not UNSET:
            field_dict["password"] = password
        if expired is not UNSET:
            field_dict["expired"] = expired
        if invited_by is not UNSET:
            field_dict["invitedBy"] = invited_by
        if node is not UNSET:
            field_dict["node"] = node

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.node import Node
        from ..models.person import Person

        d = dict(src_dict)
        password_matches = d.pop("passwordMatches", UNSET)

        password = d.pop("password", UNSET)

        expired = d.pop("expired", UNSET)

        _invited_by = d.pop("invitedBy", UNSET)
        invited_by: Person | Unset
        if isinstance(_invited_by, Unset):
            invited_by = UNSET
        else:
            invited_by = Person.from_dict(_invited_by)

        _node = d.pop("node", UNSET)
        node: Node | Unset
        if isinstance(_node, Unset):
            node = UNSET
        else:
            node = Node.from_dict(_node)

        sharing_info = cls(
            password_matches=password_matches,
            password=password,
            expired=expired,
            invited_by=invited_by,
            node=node,
        )

        sharing_info.additional_properties = d
        return sharing_info

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
