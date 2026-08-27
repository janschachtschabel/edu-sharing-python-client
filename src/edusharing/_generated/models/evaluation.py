from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Evaluation")


@_attrs_define
class Evaluation:
    """
    Attributes:
        approved_by (str | Unset):
        approved_at (datetime.datetime | Unset):
        approved (bool | Unset):
    """

    approved_by: str | Unset = UNSET
    approved_at: datetime.datetime | Unset = UNSET
    approved: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        approved_by = self.approved_by

        approved_at: str | Unset = UNSET
        if not isinstance(self.approved_at, Unset):
            approved_at = self.approved_at.isoformat()

        approved = self.approved

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if approved_by is not UNSET:
            field_dict["approvedBy"] = approved_by
        if approved_at is not UNSET:
            field_dict["approvedAt"] = approved_at
        if approved is not UNSET:
            field_dict["approved"] = approved

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        approved_by = d.pop("approvedBy", UNSET)

        _approved_at = d.pop("approvedAt", UNSET)
        approved_at: datetime.datetime | Unset
        if isinstance(_approved_at, Unset):
            approved_at = UNSET
        else:
            approved_at = datetime.datetime.fromisoformat(_approved_at)

        approved = d.pop("approved", UNSET)

        evaluation = cls(
            approved_by=approved_by,
            approved_at=approved_at,
            approved=approved,
        )

        evaluation.additional_properties = d
        return evaluation

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
