from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.user_status_status import UserStatusStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="UserStatus")


@_attrs_define
class UserStatus:
    """
    Attributes:
        status (UserStatusStatus | Unset):
        date (int | Unset):
    """

    status: UserStatusStatus | Unset = UNSET
    date: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status: str | Unset = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        date = self.date

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if status is not UNSET:
            field_dict["status"] = status
        if date is not UNSET:
            field_dict["date"] = date

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        _status = d.pop("status", UNSET)
        status: UserStatusStatus | Unset
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = UserStatusStatus(_status)

        date = d.pop("date", UNSET)

        user_status = cls(
            status=status,
            date=date,
        )

        user_status.additional_properties = d
        return user_status

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
