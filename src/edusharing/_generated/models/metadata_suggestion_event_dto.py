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
    from ..models.widget_data_dto import WidgetDataDTO


T = TypeVar("T", bound="MetadataSuggestionEventDTO")


@_attrs_define
class MetadataSuggestionEventDTO:
    """
    Attributes:
        field_class_ (str):
        timestamp (datetime.datetime | Unset):
        creator (UserDataDTO | Unset):
        receiver (UserDataDTO | Unset):
        status (NotificationEventDTOStatus | Unset):
        field_id (str | Unset):
        node (NodeDataDTO | Unset):
        caption_id (str | Unset):
        caption (str | Unset):
        parent_id (str | Unset):
        parent_caption (str | Unset):
        widget (WidgetDataDTO | Unset):
    """

    field_class_: str
    timestamp: datetime.datetime | Unset = UNSET
    creator: UserDataDTO | Unset = UNSET
    receiver: UserDataDTO | Unset = UNSET
    status: NotificationEventDTOStatus | Unset = UNSET
    field_id: str | Unset = UNSET
    node: NodeDataDTO | Unset = UNSET
    caption_id: str | Unset = UNSET
    caption: str | Unset = UNSET
    parent_id: str | Unset = UNSET
    parent_caption: str | Unset = UNSET
    widget: WidgetDataDTO | Unset = UNSET
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

        caption_id = self.caption_id

        caption = self.caption

        parent_id = self.parent_id

        parent_caption = self.parent_caption

        widget: dict[str, Any] | Unset = UNSET
        if not isinstance(self.widget, Unset):
            widget = self.widget.to_dict()

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
        if caption_id is not UNSET:
            field_dict["captionId"] = caption_id
        if caption is not UNSET:
            field_dict["caption"] = caption
        if parent_id is not UNSET:
            field_dict["parentId"] = parent_id
        if parent_caption is not UNSET:
            field_dict["parentCaption"] = parent_caption
        if widget is not UNSET:
            field_dict["widget"] = widget

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.node_data_dto import NodeDataDTO
        from ..models.user_data_dto import UserDataDTO
        from ..models.widget_data_dto import WidgetDataDTO

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

        caption_id = d.pop("captionId", UNSET)

        caption = d.pop("caption", UNSET)

        parent_id = d.pop("parentId", UNSET)

        parent_caption = d.pop("parentCaption", UNSET)

        _widget = d.pop("widget", UNSET)
        widget: WidgetDataDTO | Unset
        if isinstance(_widget, Unset):
            widget = UNSET
        else:
            widget = WidgetDataDTO.from_dict(_widget)

        metadata_suggestion_event_dto = cls(
            field_class_=field_class_,
            timestamp=timestamp,
            creator=creator,
            receiver=receiver,
            status=status,
            field_id=field_id,
            node=node,
            caption_id=caption_id,
            caption=caption,
            parent_id=parent_id,
            parent_caption=parent_caption,
            widget=widget,
        )

        metadata_suggestion_event_dto.additional_properties = d
        return metadata_suggestion_event_dto

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
