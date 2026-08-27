from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ConfigWorkflowList")


@_attrs_define
class ConfigWorkflowList:
    """Workflow status definitions

    Attributes:
        id (str | Unset): Status identifier (typically numeric, e.g. '100_unchecked')
        color (str | Unset): HTML color code for this status
        has_receiver (bool | Unset): If true, receiver can be set for this status (false for release states)
        next_ (list[str] | Unset): Array of status IDs allowed as next states (client-side validation only)
    """

    id: str | Unset = UNSET
    color: str | Unset = UNSET
    has_receiver: bool | Unset = UNSET
    next_: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        color = self.color

        has_receiver = self.has_receiver

        next_: list[str] | Unset = UNSET
        if not isinstance(self.next_, Unset):
            next_ = self.next_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if color is not UNSET:
            field_dict["color"] = color
        if has_receiver is not UNSET:
            field_dict["hasReceiver"] = has_receiver
        if next_ is not UNSET:
            field_dict["next"] = next_

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        color = d.pop("color", UNSET)

        has_receiver = d.pop("hasReceiver", UNSET)

        next_ = cast(list[str], d.pop("next", UNSET))

        config_workflow_list = cls(
            id=id,
            color=color,
            has_receiver=has_receiver,
            next_=next_,
        )

        config_workflow_list.additional_properties = d
        return config_workflow_list

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
