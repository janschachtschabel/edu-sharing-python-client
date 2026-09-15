from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ServerUpdateInfo")


@_attrs_define
class ServerUpdateInfo:
    """
    Attributes:
        id (str | Unset):
        description (str | Unset):
        order (int | Unset):
        auto (bool | Unset):
        testable (bool | Unset):
        executed_at (int | Unset):
    """

    id: str | Unset = UNSET
    description: str | Unset = UNSET
    order: int | Unset = UNSET
    auto: bool | Unset = UNSET
    testable: bool | Unset = UNSET
    executed_at: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        description = self.description

        order = self.order

        auto = self.auto

        testable = self.testable

        executed_at = self.executed_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if description is not UNSET:
            field_dict["description"] = description
        if order is not UNSET:
            field_dict["order"] = order
        if auto is not UNSET:
            field_dict["auto"] = auto
        if testable is not UNSET:
            field_dict["testable"] = testable
        if executed_at is not UNSET:
            field_dict["executedAt"] = executed_at

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        description = d.pop("description", UNSET)

        order = d.pop("order", UNSET)

        auto = d.pop("auto", UNSET)

        testable = d.pop("testable", UNSET)

        executed_at = d.pop("executedAt", UNSET)

        server_update_info = cls(
            id=id,
            description=description,
            order=order,
            auto=auto,
            testable=testable,
            executed_at=executed_at,
        )

        server_update_info.additional_properties = d
        return server_update_info

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
