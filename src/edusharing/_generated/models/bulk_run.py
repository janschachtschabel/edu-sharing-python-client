from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.bulk_run_state import BulkRunState
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.node import Node


T = TypeVar("T", bound="BulkRun")


@_attrs_define
class BulkRun:
    """
    Attributes:
        node (Node | Unset):
        state (BulkRunState | Unset):
    """

    node: Node | Unset = UNSET
    state: BulkRunState | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        node: dict[str, Any] | Unset = UNSET
        if not isinstance(self.node, Unset):
            node = self.node.to_dict()

        state: str | Unset = UNSET
        if not isinstance(self.state, Unset):
            state = self.state.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if node is not UNSET:
            field_dict["node"] = node
        if state is not UNSET:
            field_dict["state"] = state

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.node import Node

        d = dict(src_dict)
        _node = d.pop("node", UNSET)
        node: Node | Unset
        if isinstance(_node, Unset):
            node = UNSET
        else:
            node = Node.from_dict(_node)

        _state = d.pop("state", UNSET)
        state: BulkRunState | Unset
        if isinstance(_state, Unset):
            state = UNSET
        else:
            state = BulkRunState(_state)

        bulk_run = cls(
            node=node,
            state=state,
        )

        bulk_run.additional_properties = d
        return bulk_run

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
