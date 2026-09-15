from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.submission_validation_request_validation_status import (
    SubmissionValidationRequestValidationStatus,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="SubmissionValidationRequest")


@_attrs_define
class SubmissionValidationRequest:
    """
    Attributes:
        validation_notes (str | Unset):
        feedback (str | Unset):
        validation_status (SubmissionValidationRequestValidationStatus | Unset):
    """

    validation_notes: str | Unset = UNSET
    feedback: str | Unset = UNSET
    validation_status: SubmissionValidationRequestValidationStatus | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        validation_notes = self.validation_notes

        feedback = self.feedback

        validation_status: str | Unset = UNSET
        if not isinstance(self.validation_status, Unset):
            validation_status = self.validation_status.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if validation_notes is not UNSET:
            field_dict["validationNotes"] = validation_notes
        if feedback is not UNSET:
            field_dict["feedback"] = feedback
        if validation_status is not UNSET:
            field_dict["validationStatus"] = validation_status

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        validation_notes = d.pop("validationNotes", UNSET)

        feedback = d.pop("feedback", UNSET)

        _validation_status = d.pop("validationStatus", UNSET)
        validation_status: SubmissionValidationRequestValidationStatus | Unset
        if isinstance(_validation_status, Unset):
            validation_status = UNSET
        else:
            validation_status = SubmissionValidationRequestValidationStatus(_validation_status)

        submission_validation_request = cls(
            validation_notes=validation_notes,
            feedback=feedback,
            validation_status=validation_status,
        )

        submission_validation_request.additional_properties = d
        return submission_validation_request

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
