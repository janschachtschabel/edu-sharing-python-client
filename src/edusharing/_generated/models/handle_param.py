from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.handle_param_doi_service import HandleParamDoiService
from ..models.handle_param_handle_service import HandleParamHandleService
from ..types import UNSET, Unset

T = TypeVar("T", bound="HandleParam")


@_attrs_define
class HandleParam:
    """
    Attributes:
        handle_service (HandleParamHandleService | Unset):
        doi_service (HandleParamDoiService | Unset):
    """

    handle_service: HandleParamHandleService | Unset = UNSET
    doi_service: HandleParamDoiService | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        handle_service: str | Unset = UNSET
        if not isinstance(self.handle_service, Unset):
            handle_service = self.handle_service.value

        doi_service: str | Unset = UNSET
        if not isinstance(self.doi_service, Unset):
            doi_service = self.doi_service.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if handle_service is not UNSET:
            field_dict["handleService"] = handle_service
        if doi_service is not UNSET:
            field_dict["doiService"] = doi_service

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        _handle_service = d.pop("handleService", UNSET)
        handle_service: HandleParamHandleService | Unset
        if isinstance(_handle_service, Unset):
            handle_service = UNSET
        else:
            handle_service = HandleParamHandleService(_handle_service)

        _doi_service = d.pop("doiService", UNSET)
        doi_service: HandleParamDoiService | Unset
        if isinstance(_doi_service, Unset):
            doi_service = UNSET
        else:
            doi_service = HandleParamDoiService(_doi_service)

        handle_param = cls(
            handle_service=handle_service,
            doi_service=doi_service,
        )

        handle_param.additional_properties = d
        return handle_param

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
