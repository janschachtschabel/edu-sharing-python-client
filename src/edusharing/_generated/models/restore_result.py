from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="RestoreResult")


@_attrs_define
class RestoreResult:
    """
    Attributes:
        archive_node_id (str):
        node_id (str):
        parent (str):
        path (str):
        name (str):
        restore_status (str):
    """

    archive_node_id: str
    node_id: str
    parent: str
    path: str
    name: str
    restore_status: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        archive_node_id = self.archive_node_id

        node_id = self.node_id

        parent = self.parent

        path = self.path

        name = self.name

        restore_status = self.restore_status

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "archiveNodeId": archive_node_id,
                "nodeId": node_id,
                "parent": parent,
                "path": path,
                "name": name,
                "restoreStatus": restore_status,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        archive_node_id = d.pop("archiveNodeId")

        node_id = d.pop("nodeId")

        parent = d.pop("parent")

        path = d.pop("path")

        name = d.pop("name")

        restore_status = d.pop("restoreStatus")

        restore_result = cls(
            archive_node_id=archive_node_id,
            node_id=node_id,
            parent=parent,
            path=path,
            name=name,
            restore_status=restore_status,
        )

        restore_result.additional_properties = d
        return restore_result

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
