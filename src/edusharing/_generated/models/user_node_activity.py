from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="UserNodeActivity")


@_attrs_define
class UserNodeActivity:
    """
    Attributes:
        id (str):
        type_ (str):
        timestamp (datetime.datetime):
        node_id (str):
        username (str):
        occurred_at (datetime.datetime):
    """

    id: str
    type_: str
    timestamp: datetime.datetime
    node_id: str
    username: str
    occurred_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        type_ = self.type_

        timestamp = self.timestamp.isoformat()

        node_id = self.node_id

        username = self.username

        occurred_at = self.occurred_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "type": type_,
                "timestamp": timestamp,
                "nodeId": node_id,
                "username": username,
                "occurredAt": occurred_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        id = d.pop("id")

        type_ = d.pop("type")

        timestamp = datetime.datetime.fromisoformat(d.pop("timestamp"))

        node_id = d.pop("nodeId")

        username = d.pop("username")

        occurred_at = datetime.datetime.fromisoformat(d.pop("occurredAt"))

        user_node_activity = cls(
            id=id,
            type_=type_,
            timestamp=timestamp,
            node_id=node_id,
            username=username,
            occurred_at=occurred_at,
        )

        user_node_activity.additional_properties = d
        return user_node_activity

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
