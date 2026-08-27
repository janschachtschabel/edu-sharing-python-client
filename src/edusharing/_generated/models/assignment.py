from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.assignment_status import AssignmentStatus
from ..models.assignment_type import AssignmentType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.node_ref import NodeRef
    from ..models.permission import Permission
    from ..models.submission import Submission
    from ..models.user_simple import UserSimple


T = TypeVar("T", bound="Assignment")


@_attrs_define
class Assignment:
    """
    Attributes:
        ref (NodeRef):
        title (str):
        creator (UserSimple):
        created (datetime.datetime):
        status (AssignmentStatus): Status of the assignment
            * DRAFT: Assignment is in draft state, only visible to creator
            * ASSIGNED: Assignment is assigned and visible to all users with assignee permission
            * CORRECTED: All submissions of this Assignment have been finished (only for type submission)
            * FINISHED: Assignment has been completed
            * CANCELED: Assignment has been canceled
        type_ (AssignmentType): Type of the assignment
            * DEFAULT: Standard assignment type without specific submission requirements
            * SUBMISSION: Assignment that requires participants to submit documents or materials
        allow_additional_document_submissions (bool):
        permissions (list[Permission]):
        submissions (list[Submission]):
        is_coordinator (bool): Whether the current user is a coordinator of this assignment.
        summary (str | Unset):
        end_time (datetime.datetime | Unset):
        submitted (bool | Unset): For Assignee: Shows whether the the assignee has submitted the assignment or not.
            For Coordinator: Shows whether all assignees have submitted the assignment or not.
            Only valid for Assignments of type SUBMISSION
        modified (datetime.datetime | Unset):
    """

    ref: NodeRef
    title: str
    creator: UserSimple
    created: datetime.datetime
    status: AssignmentStatus
    type_: AssignmentType
    allow_additional_document_submissions: bool
    permissions: list[Permission]
    submissions: list[Submission]
    is_coordinator: bool
    summary: str | Unset = UNSET
    end_time: datetime.datetime | Unset = UNSET
    submitted: bool | Unset = UNSET
    modified: datetime.datetime | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ref = self.ref.to_dict()

        title = self.title

        creator = self.creator.to_dict()

        created = self.created.isoformat()

        status = self.status.value

        type_ = self.type_.value

        allow_additional_document_submissions = self.allow_additional_document_submissions

        permissions = []
        for permissions_item_data in self.permissions:
            permissions_item = permissions_item_data.to_dict()
            permissions.append(permissions_item)

        submissions = []
        for submissions_item_data in self.submissions:
            submissions_item = submissions_item_data.to_dict()
            submissions.append(submissions_item)

        is_coordinator = self.is_coordinator

        summary = self.summary

        end_time: str | Unset = UNSET
        if not isinstance(self.end_time, Unset):
            end_time = self.end_time.isoformat()

        submitted = self.submitted

        modified: str | Unset = UNSET
        if not isinstance(self.modified, Unset):
            modified = self.modified.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref": ref,
                "title": title,
                "creator": creator,
                "created": created,
                "status": status,
                "type": type_,
                "allowAdditionalDocumentSubmissions": allow_additional_document_submissions,
                "permissions": permissions,
                "submissions": submissions,
                "isCoordinator": is_coordinator,
            }
        )
        if summary is not UNSET:
            field_dict["summary"] = summary
        if end_time is not UNSET:
            field_dict["endTime"] = end_time
        if submitted is not UNSET:
            field_dict["submitted"] = submitted
        if modified is not UNSET:
            field_dict["modified"] = modified

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.node_ref import NodeRef
        from ..models.permission import Permission
        from ..models.submission import Submission
        from ..models.user_simple import UserSimple

        d = dict(src_dict)
        ref = NodeRef.from_dict(d.pop("ref"))

        title = d.pop("title")

        creator = UserSimple.from_dict(d.pop("creator"))

        created = datetime.datetime.fromisoformat(d.pop("created"))

        status = AssignmentStatus(d.pop("status"))

        type_ = AssignmentType(d.pop("type"))

        allow_additional_document_submissions = d.pop("allowAdditionalDocumentSubmissions")

        permissions = []
        _permissions = d.pop("permissions")
        for permissions_item_data in _permissions:
            permissions_item = Permission.from_dict(permissions_item_data)

            permissions.append(permissions_item)

        submissions = []
        _submissions = d.pop("submissions")
        for submissions_item_data in _submissions:
            submissions_item = Submission.from_dict(submissions_item_data)

            submissions.append(submissions_item)

        is_coordinator = d.pop("isCoordinator")

        summary = d.pop("summary", UNSET)

        _end_time = d.pop("endTime", UNSET)
        end_time: datetime.datetime | Unset
        if isinstance(_end_time, Unset):
            end_time = UNSET
        else:
            end_time = datetime.datetime.fromisoformat(_end_time)

        submitted = d.pop("submitted", UNSET)

        _modified = d.pop("modified", UNSET)
        modified: datetime.datetime | Unset
        if isinstance(_modified, Unset):
            modified = UNSET
        else:
            modified = datetime.datetime.fromisoformat(_modified)

        assignment = cls(
            ref=ref,
            title=title,
            creator=creator,
            created=created,
            status=status,
            type_=type_,
            allow_additional_document_submissions=allow_additional_document_submissions,
            permissions=permissions,
            submissions=submissions,
            is_coordinator=is_coordinator,
            summary=summary,
            end_time=end_time,
            submitted=submitted,
            modified=modified,
        )

        assignment.additional_properties = d
        return assignment

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
