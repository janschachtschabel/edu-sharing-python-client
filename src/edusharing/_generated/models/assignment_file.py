from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.assignment_file_document_role import AssignmentFileDocumentRole
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.node import Node
    from ..models.node_ref import NodeRef


T = TypeVar("T", bound="AssignmentFile")


@_attrs_define
class AssignmentFile:
    """object of the original assignment file (if applicable)

    Attributes:
        ref (NodeRef):
        document_role (AssignmentFileDocumentRole):
        refer_node (Node | Unset):
        is_done (bool | Unset): Indicates whether the associated task for this file is complete.
            Only valid for Assignments of type DEFAULT
    """

    ref: NodeRef
    document_role: AssignmentFileDocumentRole
    refer_node: Node | Unset = UNSET
    is_done: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ref = self.ref.to_dict()

        document_role = self.document_role.value

        refer_node: dict[str, Any] | Unset = UNSET
        if not isinstance(self.refer_node, Unset):
            refer_node = self.refer_node.to_dict()

        is_done = self.is_done

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref": ref,
                "documentRole": document_role,
            }
        )
        if refer_node is not UNSET:
            field_dict["referNode"] = refer_node
        if is_done is not UNSET:
            field_dict["isDone"] = is_done

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.node import Node
        from ..models.node_ref import NodeRef

        d = dict(src_dict)
        ref = NodeRef.from_dict(d.pop("ref"))

        document_role = AssignmentFileDocumentRole(d.pop("documentRole"))

        _refer_node = d.pop("referNode", UNSET)
        refer_node: Node | Unset
        if isinstance(_refer_node, Unset):
            refer_node = UNSET
        else:
            refer_node = Node.from_dict(_refer_node)

        is_done = d.pop("isDone", UNSET)

        assignment_file = cls(
            ref=ref,
            document_role=document_role,
            refer_node=refer_node,
            is_done=is_done,
        )

        assignment_file.additional_properties = d
        return assignment_file

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
