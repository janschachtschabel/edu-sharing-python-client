from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.share_info_share_status import ShareInfoShareStatus
from ..models.share_info_share_type import ShareInfoShareType

T = TypeVar("T", bound="ShareInfo")


@_attrs_define
class ShareInfo:
    """
    Attributes:
        shared_by (str):
        share_type (ShareInfoShareType):
        share_status (ShareInfoShareStatus):
        id (int):
        timestamp (datetime.datetime):
        node_id (str):
        shared_with (str):
    """

    shared_by: str
    share_type: ShareInfoShareType
    share_status: ShareInfoShareStatus
    id: int
    timestamp: datetime.datetime
    node_id: str
    shared_with: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        shared_by = self.shared_by

        share_type = self.share_type.value

        share_status = self.share_status.value

        id = self.id

        timestamp = self.timestamp.isoformat()

        node_id = self.node_id

        shared_with = self.shared_with

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "sharedBy": shared_by,
                "shareType": share_type,
                "shareStatus": share_status,
                "id": id,
                "timestamp": timestamp,
                "nodeId": node_id,
                "sharedWith": shared_with,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        shared_by = d.pop("sharedBy")

        share_type = ShareInfoShareType(d.pop("shareType"))

        share_status = ShareInfoShareStatus(d.pop("shareStatus"))

        id = d.pop("id")

        timestamp = datetime.datetime.fromisoformat(d.pop("timestamp"))

        node_id = d.pop("nodeId")

        shared_with = d.pop("sharedWith")

        share_info = cls(
            shared_by=shared_by,
            share_type=share_type,
            share_status=share_status,
            id=id,
            timestamp=timestamp,
            node_id=node_id,
            shared_with=shared_with,
        )

        share_info.additional_properties = d
        return share_info

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
