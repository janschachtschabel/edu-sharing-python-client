from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.user_event_event_type import UserEventEventType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.node import Node
    from ..models.user_simple import UserSimple


T = TypeVar("T", bound="UserEvent")


@_attrs_define
class UserEvent:
    """
    Attributes:
        node (Node | Unset):
        initiator (UserSimple | Unset):
        timestamp (datetime.datetime | Unset):
        event_type (UserEventEventType | Unset):
    """

    node: Node | Unset = UNSET
    initiator: UserSimple | Unset = UNSET
    timestamp: datetime.datetime | Unset = UNSET
    event_type: UserEventEventType | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        node: dict[str, Any] | Unset = UNSET
        if not isinstance(self.node, Unset):
            node = self.node.to_dict()

        initiator: dict[str, Any] | Unset = UNSET
        if not isinstance(self.initiator, Unset):
            initiator = self.initiator.to_dict()

        timestamp: str | Unset = UNSET
        if not isinstance(self.timestamp, Unset):
            timestamp = self.timestamp.isoformat()

        event_type: str | Unset = UNSET
        if not isinstance(self.event_type, Unset):
            event_type = self.event_type.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if node is not UNSET:
            field_dict["node"] = node
        if initiator is not UNSET:
            field_dict["initiator"] = initiator
        if timestamp is not UNSET:
            field_dict["timestamp"] = timestamp
        if event_type is not UNSET:
            field_dict["eventType"] = event_type

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.node import Node
        from ..models.user_simple import UserSimple

        d = dict(src_dict)
        _node = d.pop("node", UNSET)
        node: Node | Unset
        if isinstance(_node, Unset):
            node = UNSET
        else:
            node = Node.from_dict(_node)

        _initiator = d.pop("initiator", UNSET)
        initiator: UserSimple | Unset
        if isinstance(_initiator, Unset):
            initiator = UNSET
        else:
            initiator = UserSimple.from_dict(_initiator)

        _timestamp = d.pop("timestamp", UNSET)
        timestamp: datetime.datetime | Unset
        if isinstance(_timestamp, Unset):
            timestamp = UNSET
        else:
            timestamp = datetime.datetime.fromisoformat(_timestamp)

        _event_type = d.pop("eventType", UNSET)
        event_type: UserEventEventType | Unset
        if isinstance(_event_type, Unset):
            event_type = UNSET
        else:
            event_type = UserEventEventType(_event_type)

        user_event = cls(
            node=node,
            initiator=initiator,
            timestamp=timestamp,
            event_type=event_type,
        )

        user_event.additional_properties = d
        return user_event

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
