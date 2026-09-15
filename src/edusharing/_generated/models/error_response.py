from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.error_response_details import ErrorResponseDetails


T = TypeVar("T", bound="ErrorResponse")


@_attrs_define
class ErrorResponse:
    """
    Attributes:
        error (str):
        message (str):
        stacktrace (str | Unset):
        log_level (str | Unset):
        details (ErrorResponseDetails | Unset):
        stacktrace_array (list[str] | Unset):
    """

    error: str
    message: str
    stacktrace: str | Unset = UNSET
    log_level: str | Unset = UNSET
    details: ErrorResponseDetails | Unset = UNSET
    stacktrace_array: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        error = self.error

        message = self.message

        stacktrace = self.stacktrace

        log_level = self.log_level

        details: dict[str, Any] | Unset = UNSET
        if not isinstance(self.details, Unset):
            details = self.details.to_dict()

        stacktrace_array: list[str] | Unset = UNSET
        if not isinstance(self.stacktrace_array, Unset):
            stacktrace_array = self.stacktrace_array

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "error": error,
                "message": message,
            }
        )
        if stacktrace is not UNSET:
            field_dict["stacktrace"] = stacktrace
        if log_level is not UNSET:
            field_dict["logLevel"] = log_level
        if details is not UNSET:
            field_dict["details"] = details
        if stacktrace_array is not UNSET:
            field_dict["stacktraceArray"] = stacktrace_array

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.error_response_details import ErrorResponseDetails

        d = dict(src_dict)
        error = d.pop("error")

        message = d.pop("message")

        stacktrace = d.pop("stacktrace", UNSET)

        log_level = d.pop("logLevel", UNSET)

        _details = d.pop("details", UNSET)
        details: ErrorResponseDetails | Unset
        if isinstance(_details, Unset):
            details = UNSET
        else:
            details = ErrorResponseDetails.from_dict(_details)

        stacktrace_array = cast(list[str], d.pop("stacktraceArray", UNSET))

        error_response = cls(
            error=error,
            message=message,
            stacktrace=stacktrace,
            log_level=log_level,
            details=details,
            stacktrace_array=stacktrace_array,
        )

        error_response.additional_properties = d
        return error_response

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
