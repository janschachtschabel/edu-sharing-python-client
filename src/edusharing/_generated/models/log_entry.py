from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.level import Level


T = TypeVar("T", bound="LogEntry")


@_attrs_define
class LogEntry:
    """
    Attributes:
        class_name (str | Unset):
        level (Level | Unset):
        date (int | Unset):
        message (str | Unset):
    """

    class_name: str | Unset = UNSET
    level: Level | Unset = UNSET
    date: int | Unset = UNSET
    message: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        class_name = self.class_name

        level: dict[str, Any] | Unset = UNSET
        if not isinstance(self.level, Unset):
            level = self.level.to_dict()

        date = self.date

        message = self.message

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if class_name is not UNSET:
            field_dict["className"] = class_name
        if level is not UNSET:
            field_dict["level"] = level
        if date is not UNSET:
            field_dict["date"] = date
        if message is not UNSET:
            field_dict["message"] = message

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.level import Level

        d = dict(src_dict)
        class_name = d.pop("className", UNSET)

        _level = d.pop("level", UNSET)
        level: Level | Unset
        if isinstance(_level, Unset):
            level = UNSET
        else:
            level = Level.from_dict(_level)

        date = d.pop("date", UNSET)

        message = d.pop("message", UNSET)

        log_entry = cls(
            class_name=class_name,
            level=level,
            date=date,
            message=message,
        )

        log_entry.additional_properties = d
        return log_entry

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
