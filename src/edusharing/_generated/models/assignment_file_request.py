from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.assignment_file_request_document_role import AssignmentFileRequestDocumentRole
from ..types import UNSET, Unset

T = TypeVar("T", bound="AssignmentFileRequest")


@_attrs_define
class AssignmentFileRequest:
    """
    Attributes:
        ref_id (str):
        document_role (AssignmentFileRequestDocumentRole):
        is_done (bool | Unset): Indicates whether the associated task for this file is complete.
            Only valid for Assignments of type DEFAULT
    """

    ref_id: str
    document_role: AssignmentFileRequestDocumentRole
    is_done: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ref_id = self.ref_id

        document_role = self.document_role.value

        is_done = self.is_done

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "refId": ref_id,
                "documentRole": document_role,
            }
        )
        if is_done is not UNSET:
            field_dict["isDone"] = is_done

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        ref_id = d.pop("refId")

        document_role = AssignmentFileRequestDocumentRole(d.pop("documentRole"))

        is_done = d.pop("isDone", UNSET)

        assignment_file_request = cls(
            ref_id=ref_id,
            document_role=document_role,
            is_done=is_done,
        )

        assignment_file_request.additional_properties = d
        return assignment_file_request

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
