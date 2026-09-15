from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.create_assignment_request_status import CreateAssignmentRequestStatus
from ..models.create_assignment_request_type import CreateAssignmentRequestType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.assignment_file_request import AssignmentFileRequest
    from ..models.permission_request import PermissionRequest


T = TypeVar("T", bound="CreateAssignmentRequest")


@_attrs_define
class CreateAssignmentRequest:
    """
    Attributes:
        title (str):
        summary (str):
        status (CreateAssignmentRequestStatus): Status of the assignment
            * DRAFT: Assignment is in draft state, only visible to creator
            * ASSIGNED: Assignment is assigned and visible to all users with assignee permission
            * CORRECTED: All submissions of this Assignment have been finished (only for type submission)
            * FINISHED: Assignment has been completed
            * CANCELED: Assignment has been canceled
        type_ (CreateAssignmentRequestType): Type of the assignment
            * DEFAULT: Standard assignment type without specific submission requirements
            * SUBMISSION: Assignment that requires participants to submit documents or materials
        allow_additional_document_submissions (bool):
        permissions (list[PermissionRequest]):
        assignment_files (list[AssignmentFileRequest]):
        id (str | Unset):
        end_time (datetime.datetime | Unset):
    """

    title: str
    summary: str
    status: CreateAssignmentRequestStatus
    type_: CreateAssignmentRequestType
    allow_additional_document_submissions: bool
    permissions: list[PermissionRequest]
    assignment_files: list[AssignmentFileRequest]
    id: str | Unset = UNSET
    end_time: datetime.datetime | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        title = self.title

        summary = self.summary

        status = self.status.value

        type_ = self.type_.value

        allow_additional_document_submissions = self.allow_additional_document_submissions

        permissions = []
        for permissions_item_data in self.permissions:
            permissions_item = permissions_item_data.to_dict()
            permissions.append(permissions_item)

        assignment_files = []
        for assignment_files_item_data in self.assignment_files:
            assignment_files_item = assignment_files_item_data.to_dict()
            assignment_files.append(assignment_files_item)

        id = self.id

        end_time: str | Unset = UNSET
        if not isinstance(self.end_time, Unset):
            end_time = self.end_time.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "title": title,
                "summary": summary,
                "status": status,
                "type": type_,
                "allowAdditionalDocumentSubmissions": allow_additional_document_submissions,
                "permissions": permissions,
                "assignmentFiles": assignment_files,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id
        if end_time is not UNSET:
            field_dict["endTime"] = end_time

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.assignment_file_request import AssignmentFileRequest
        from ..models.permission_request import PermissionRequest

        d = dict(src_dict)
        title = d.pop("title")

        summary = d.pop("summary")

        status = CreateAssignmentRequestStatus(d.pop("status"))

        type_ = CreateAssignmentRequestType(d.pop("type"))

        allow_additional_document_submissions = d.pop("allowAdditionalDocumentSubmissions")

        permissions = []
        _permissions = d.pop("permissions")
        for permissions_item_data in _permissions:
            permissions_item = PermissionRequest.from_dict(permissions_item_data)

            permissions.append(permissions_item)

        assignment_files = []
        _assignment_files = d.pop("assignmentFiles")
        for assignment_files_item_data in _assignment_files:
            assignment_files_item = AssignmentFileRequest.from_dict(assignment_files_item_data)

            assignment_files.append(assignment_files_item)

        id = d.pop("id", UNSET)

        _end_time = d.pop("endTime", UNSET)
        end_time: datetime.datetime | Unset
        if isinstance(_end_time, Unset):
            end_time = UNSET
        else:
            end_time = datetime.datetime.fromisoformat(_end_time)

        create_assignment_request = cls(
            title=title,
            summary=summary,
            status=status,
            type_=type_,
            allow_additional_document_submissions=allow_additional_document_submissions,
            permissions=permissions,
            assignment_files=assignment_files,
            id=id,
            end_time=end_time,
        )

        create_assignment_request.additional_properties = d
        return create_assignment_request

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
