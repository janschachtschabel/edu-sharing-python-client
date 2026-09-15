from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.invite_event_share_status import InviteEventShareStatus
from ..models.invite_event_share_type import InviteEventShareType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.authority import Authority
    from ..models.node import Node


T = TypeVar("T", bound="InviteEvent")


@_attrs_define
class InviteEvent:
    """
    Attributes:
        node (Node | Unset):
        id (str | Unset):
        shared_by (Authority | Unset):
        shared_with (Authority | Unset):
        timestamp (datetime.datetime | Unset):
        share_type (InviteEventShareType | Unset):
        share_status (InviteEventShareStatus | Unset):
    """

    node: Node | Unset = UNSET
    id: str | Unset = UNSET
    shared_by: Authority | Unset = UNSET
    shared_with: Authority | Unset = UNSET
    timestamp: datetime.datetime | Unset = UNSET
    share_type: InviteEventShareType | Unset = UNSET
    share_status: InviteEventShareStatus | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        node: dict[str, Any] | Unset = UNSET
        if not isinstance(self.node, Unset):
            node = self.node.to_dict()

        id = self.id

        shared_by: dict[str, Any] | Unset = UNSET
        if not isinstance(self.shared_by, Unset):
            shared_by = self.shared_by.to_dict()

        shared_with: dict[str, Any] | Unset = UNSET
        if not isinstance(self.shared_with, Unset):
            shared_with = self.shared_with.to_dict()

        timestamp: str | Unset = UNSET
        if not isinstance(self.timestamp, Unset):
            timestamp = self.timestamp.isoformat()

        share_type: str | Unset = UNSET
        if not isinstance(self.share_type, Unset):
            share_type = self.share_type.value

        share_status: str | Unset = UNSET
        if not isinstance(self.share_status, Unset):
            share_status = self.share_status.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if node is not UNSET:
            field_dict["node"] = node
        if id is not UNSET:
            field_dict["id"] = id
        if shared_by is not UNSET:
            field_dict["sharedBy"] = shared_by
        if shared_with is not UNSET:
            field_dict["sharedWith"] = shared_with
        if timestamp is not UNSET:
            field_dict["timestamp"] = timestamp
        if share_type is not UNSET:
            field_dict["shareType"] = share_type
        if share_status is not UNSET:
            field_dict["shareStatus"] = share_status

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.authority import Authority
        from ..models.node import Node

        d = dict(src_dict)
        _node = d.pop("node", UNSET)
        node: Node | Unset
        if isinstance(_node, Unset):
            node = UNSET
        else:
            node = Node.from_dict(_node)

        id = d.pop("id", UNSET)

        _shared_by = d.pop("sharedBy", UNSET)
        shared_by: Authority | Unset
        if isinstance(_shared_by, Unset):
            shared_by = UNSET
        else:
            shared_by = Authority.from_dict(_shared_by)

        _shared_with = d.pop("sharedWith", UNSET)
        shared_with: Authority | Unset
        if isinstance(_shared_with, Unset):
            shared_with = UNSET
        else:
            shared_with = Authority.from_dict(_shared_with)

        _timestamp = d.pop("timestamp", UNSET)
        timestamp: datetime.datetime | Unset
        if isinstance(_timestamp, Unset):
            timestamp = UNSET
        else:
            timestamp = datetime.datetime.fromisoformat(_timestamp)

        _share_type = d.pop("shareType", UNSET)
        share_type: InviteEventShareType | Unset
        if isinstance(_share_type, Unset):
            share_type = UNSET
        else:
            share_type = InviteEventShareType(_share_type)

        _share_status = d.pop("shareStatus", UNSET)
        share_status: InviteEventShareStatus | Unset
        if isinstance(_share_status, Unset):
            share_status = UNSET
        else:
            share_status = InviteEventShareStatus(_share_status)

        invite_event = cls(
            node=node,
            id=id,
            shared_by=shared_by,
            shared_with=shared_with,
            timestamp=timestamp,
            share_type=share_type,
            share_status=share_status,
        )

        invite_event.additional_properties = d
        return invite_event

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
