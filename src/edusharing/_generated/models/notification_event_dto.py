from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.notification_event_dto_status import NotificationEventDTOStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.user_data_dto import UserDataDTO


T = TypeVar("T", bound="NotificationEventDTO")


@_attrs_define
class NotificationEventDTO:
    """
    Attributes:
        field_class_ (str):
        timestamp (datetime.datetime | Unset):
        creator (UserDataDTO | Unset):
        receiver (UserDataDTO | Unset):
        status (NotificationEventDTOStatus | Unset):
        field_id (str | Unset):
    """

    field_class_: str
    timestamp: datetime.datetime | Unset = UNSET
    creator: UserDataDTO | Unset = UNSET
    receiver: UserDataDTO | Unset = UNSET
    status: NotificationEventDTOStatus | Unset = UNSET
    field_id: str | Unset = UNSET
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

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
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

        notification_event_dto = cls(
            field_class_=field_class_,
            timestamp=timestamp,
            creator=creator,
            receiver=receiver,
            status=status,
            field_id=field_id,
        )

        notification_event_dto.additional_properties = d
        return notification_event_dto

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
