from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.submission_submission_status import SubmissionSubmissionStatus
from ..models.submission_validation_status import SubmissionValidationStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.node_ref import NodeRef
    from ..models.user_simple import UserSimple


T = TypeVar("T", bound="Submission")


@_attrs_define
class Submission:
    """
    Attributes:
        ref (NodeRef):
        assignee (UserSimple):
        submission_status (SubmissionSubmissionStatus):
        validation_status (SubmissionValidationStatus):
        validation_notes (str | Unset): internal note (not visible for assignee)
        feedback (str | Unset):
        submission_date (datetime.datetime | Unset): The date of submission (from the assignee)
        return_date (datetime.datetime | Unset): The date of getting it back (from the coordinator)
        user_notes (str | Unset): notes from the assignee (only modifiable by assignee)
    """

    ref: NodeRef
    assignee: UserSimple
    submission_status: SubmissionSubmissionStatus
    validation_status: SubmissionValidationStatus
    validation_notes: str | Unset = UNSET
    feedback: str | Unset = UNSET
    submission_date: datetime.datetime | Unset = UNSET
    return_date: datetime.datetime | Unset = UNSET
    user_notes: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ref = self.ref.to_dict()

        assignee = self.assignee.to_dict()

        submission_status = self.submission_status.value

        validation_status = self.validation_status.value

        validation_notes = self.validation_notes

        feedback = self.feedback

        submission_date: str | Unset = UNSET
        if not isinstance(self.submission_date, Unset):
            submission_date = self.submission_date.isoformat()

        return_date: str | Unset = UNSET
        if not isinstance(self.return_date, Unset):
            return_date = self.return_date.isoformat()

        user_notes = self.user_notes

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref": ref,
                "assignee": assignee,
                "submissionStatus": submission_status,
                "validationStatus": validation_status,
            }
        )
        if validation_notes is not UNSET:
            field_dict["validationNotes"] = validation_notes
        if feedback is not UNSET:
            field_dict["feedback"] = feedback
        if submission_date is not UNSET:
            field_dict["submissionDate"] = submission_date
        if return_date is not UNSET:
            field_dict["returnDate"] = return_date
        if user_notes is not UNSET:
            field_dict["userNotes"] = user_notes

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.node_ref import NodeRef
        from ..models.user_simple import UserSimple

        d = dict(src_dict)
        ref = NodeRef.from_dict(d.pop("ref"))

        assignee = UserSimple.from_dict(d.pop("assignee"))

        submission_status = SubmissionSubmissionStatus(d.pop("submissionStatus"))

        validation_status = SubmissionValidationStatus(d.pop("validationStatus"))

        validation_notes = d.pop("validationNotes", UNSET)

        feedback = d.pop("feedback", UNSET)

        _submission_date = d.pop("submissionDate", UNSET)
        submission_date: datetime.datetime | Unset
        if isinstance(_submission_date, Unset):
            submission_date = UNSET
        else:
            submission_date = datetime.datetime.fromisoformat(_submission_date)

        _return_date = d.pop("returnDate", UNSET)
        return_date: datetime.datetime | Unset
        if isinstance(_return_date, Unset):
            return_date = UNSET
        else:
            return_date = datetime.datetime.fromisoformat(_return_date)

        user_notes = d.pop("userNotes", UNSET)

        submission = cls(
            ref=ref,
            assignee=assignee,
            submission_status=submission_status,
            validation_status=validation_status,
            validation_notes=validation_notes,
            feedback=feedback,
            submission_date=submission_date,
            return_date=return_date,
            user_notes=user_notes,
        )

        submission.additional_properties = d
        return submission

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
