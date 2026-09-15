from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.submission_file_validation_request_validation_status import (
    SubmissionFileValidationRequestValidationStatus,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="SubmissionFileValidationRequest")


@_attrs_define
class SubmissionFileValidationRequest:
    """JSON-Metadaten

    Attributes:
        validation_status (SubmissionFileValidationRequestValidationStatus | Unset):
    """

    validation_status: SubmissionFileValidationRequestValidationStatus | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        validation_status: str | Unset = UNSET
        if not isinstance(self.validation_status, Unset):
            validation_status = self.validation_status.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if validation_status is not UNSET:
            field_dict["validationStatus"] = validation_status

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        _validation_status = d.pop("validationStatus", UNSET)
        validation_status: SubmissionFileValidationRequestValidationStatus | Unset
        if isinstance(_validation_status, Unset):
            validation_status = UNSET
        else:
            validation_status = SubmissionFileValidationRequestValidationStatus(_validation_status)

        submission_file_validation_request = cls(
            validation_status=validation_status,
        )

        submission_file_validation_request.additional_properties = d
        return submission_file_validation_request

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
