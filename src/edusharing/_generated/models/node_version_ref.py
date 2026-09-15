from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.node_ref import NodeRef


T = TypeVar("T", bound="NodeVersionRef")


@_attrs_define
class NodeVersionRef:
    """
    Attributes:
        node (NodeRef):
        major (int):
        minor (int):
    """

    node: NodeRef
    major: int
    minor: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        node = self.node.to_dict()

        major = self.major

        minor = self.minor

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "node": node,
                "major": major,
                "minor": minor,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.node_ref import NodeRef

        d = dict(src_dict)
        node = NodeRef.from_dict(d.pop("node"))

        major = d.pop("major")

        minor = d.pop("minor")

        node_version_ref = cls(
            node=node,
            major=major,
            minor=minor,
        )

        node_version_ref.additional_properties = d
        return node_version_ref

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
