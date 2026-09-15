from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.notification_event_dto_status import NotificationEventDTOStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.node_data_dto import NodeDataDTO
    from ..models.user_data_dto import UserDataDTO


T = TypeVar("T", bound="CommentEventDTO")


@_attrs_define
class CommentEventDTO:
    """
    Attributes:
        field_class_ (str):
        timestamp (datetime.datetime | Unset):
        creator (UserDataDTO | Unset):
        receiver (UserDataDTO | Unset):
        status (NotificationEventDTOStatus | Unset):
        field_id (str | Unset):
        node (NodeDataDTO | Unset):
        comment_content (str | Unset):
        comment_reference (str | Unset):
        event (str | Unset):
    """

    field_class_: str
    timestamp: datetime.datetime | Unset = UNSET
    creator: UserDataDTO | Unset = UNSET
    receiver: UserDataDTO | Unset = UNSET
    status: NotificationEventDTOStatus | Unset = UNSET
    field_id: str | Unset = UNSET
    node: NodeDataDTO | Unset = UNSET
    comment_content: str | Unset = UNSET
    comment_reference: str | Unset = UNSET
    event: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_class_ = self.field_class_

        timestamp: str | Unset = UNSET
        if not isinstance(self.timestamp, Unset):
            timestamp = self.timestamp.isoformat()

        creator: dict[str, Any] | Unset = UNSET
        if not isinstance(self.creator, Unset):
            creator = self.creator.to_dict()

        receiver: dict[str, Any] | Unset = UNSET
        if not isinstance(self.receiver, Unset):
            receiver = self.receiver.to_dict()

        status: str | Unset = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        field_id = self.field_id

        node: dict[str, Any] | Unset = UNSET
        if not isinstance(self.node, Unset):
            node = self.node.to_dict()

        comment_content = self.comment_content

        comment_reference = self.comment_reference

        event = self.event

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "_class": field_class_,
            }
        )
        if timestamp is not UNSET:
            field_dict["timestamp"] = timestamp
        if creator is not UNSET:
            field_dict["creator"] = creator
        if receiver is not UNSET:
            field_dict["receiver"] = receiver
        if status is not UNSET:
            field_dict["status"] = status
        if field_id is not UNSET:
            field_dict["_id"] = field_id
        if node is not UNSET:
            field_dict["node"] = node
        if comment_content is not UNSET:
            field_dict["commentContent"] = comment_content
        if comment_reference is not UNSET:
            field_dict["commentReference"] = comment_reference
        if event is not UNSET:
            field_dict["event"] = event

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.node_data_dto import NodeDataDTO
        from ..models.user_data_dto import UserDataDTO

        d = dict(src_dict)
        field_class_ = d.pop("_class")

        _timestamp = d.pop("timestamp", UNSET)
        timestamp: datetime.datetime | Unset
        if isinstance(_timestamp, Unset):
            timestamp = UNSET
        else:
            timestamp = datetime.datetime.fromisoformat(_timestamp)

        _creator = d.pop("creator", UNSET)
        creator: UserDataDTO | Unset
        if isinstance(_creator, Unset):
            creator = UNSET
        else:
            creator = UserDataDTO.from_dict(_creator)

        _receiver = d.pop("receiver", UNSET)
        receiver: UserDataDTO | Unset
        if isinstance(_receiver, Unset):
            receiver = UNSET
        else:
            receiver = UserDataDTO.from_dict(_receiver)

        _status = d.pop("status", UNSET)
        status: NotificationEventDTOStatus | Unset
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = NotificationEventDTOStatus(_status)

        field_id = d.pop("_id", UNSET)

        _node = d.pop("node", UNSET)
        node: NodeDataDTO | Unset
        if isinstance(_node, Unset):
            node = UNSET
        else:
            node = NodeDataDTO.from_dict(_node)

        comment_content = d.pop("commentContent", UNSET)

        comment_reference = d.pop("commentReference", UNSET)

        event = d.pop("event", UNSET)

        comment_event_dto = cls(
            field_class_=field_class_,
            timestamp=timestamp,
            creator=creator,
            receiver=receiver,
            status=status,
            field_id=field_id,
            node=node,
            comment_content=comment_content,
            comment_reference=comment_reference,
            event=event,
        )

        comment_event_dto.additional_properties = d
        return comment_event_dto

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
