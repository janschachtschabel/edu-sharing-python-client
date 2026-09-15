from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.submission_info_request_status import SubmissionInfoRequestStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="SubmissionInfoRequest")


@_attrs_define
class SubmissionInfoRequest:
    """
    Attributes:
        status (SubmissionInfoRequestStatus | Unset):
        user_notes (str | Unset):
    """

    status: SubmissionInfoRequestStatus | Unset = UNSET
    user_notes: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status: str | Unset = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        user_notes = self.user_notes

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if status is not UNSET:
            field_dict["status"] = status
        if user_notes is not UNSET:
            field_dict["userNotes"] = user_notes

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        _status = d.pop("status", UNSET)
        status: SubmissionInfoRequestStatus | Unset
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = SubmissionInfoRequestStatus(_status)

        user_notes = d.pop("userNotes", UNSET)

        submission_info_request = cls(
            status=status,
            user_notes=user_notes,
        )

        submission_info_request.additional_properties = d
        return submission_info_request

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
