from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.feedback_data_data import FeedbackDataData


T = TypeVar("T", bound="FeedbackData")


@_attrs_define
class FeedbackData:
    """
    Attributes:
        authority (str | Unset):
        data (FeedbackDataData | Unset):
        created_at (datetime.datetime | Unset):
        modified_at (datetime.datetime | Unset):
    """

    authority: str | Unset = UNSET
    data: FeedbackDataData | Unset = UNSET
    created_at: datetime.datetime | Unset = UNSET
    modified_at: datetime.datetime | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        authority = self.authority

        data: dict[str, Any] | Unset = UNSET
        if not isinstance(self.data, Unset):
            data = self.data.to_dict()

        created_at: str | Unset = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        modified_at: str | Unset = UNSET
        if not isinstance(self.modified_at, Unset):
            modified_at = self.modified_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if authority is not UNSET:
            field_dict["authority"] = authority
        if data is not UNSET:
            field_dict["data"] = data
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at
        if modified_at is not UNSET:
            field_dict["modifiedAt"] = modified_at

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.feedback_data_data import FeedbackDataData

        d = dict(src_dict)
        authority = d.pop("authority", UNSET)

        _data = d.pop("data", UNSET)
        data: FeedbackDataData | Unset
        if isinstance(_data, Unset):
            data = UNSET
        else:
            data = FeedbackDataData.from_dict(_data)

        _created_at = d.pop("createdAt", UNSET)
        created_at: datetime.datetime | Unset
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = datetime.datetime.fromisoformat(_created_at)

        _modified_at = d.pop("modifiedAt", UNSET)
        modified_at: datetime.datetime | Unset
        if isinstance(_modified_at, Unset):
            modified_at = UNSET
        else:
            modified_at = datetime.datetime.fromisoformat(_modified_at)

        feedback_data = cls(
            authority=authority,
            data=data,
            created_at=created_at,
            modified_at=modified_at,
        )

        feedback_data.additional_properties = d
        return feedback_data

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
