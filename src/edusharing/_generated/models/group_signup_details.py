from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.group_signup_details_signup_method import GroupSignupDetailsSignupMethod
from ..types import UNSET, Unset

T = TypeVar("T", bound="GroupSignupDetails")


@_attrs_define
class GroupSignupDetails:
    """
    Attributes:
        signup_method (GroupSignupDetailsSignupMethod | Unset):
        signup_password (str | Unset):
    """

    signup_method: GroupSignupDetailsSignupMethod | Unset = UNSET
    signup_password: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        signup_method: str | Unset = UNSET
        if not isinstance(self.signup_method, Unset):
            signup_method = self.signup_method.value

        signup_password = self.signup_password

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if signup_method is not UNSET:
            field_dict["signupMethod"] = signup_method
        if signup_password is not UNSET:
            field_dict["signupPassword"] = signup_password

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        _signup_method = d.pop("signupMethod", UNSET)
        signup_method: GroupSignupDetailsSignupMethod | Unset
        if isinstance(_signup_method, Unset):
            signup_method = UNSET
        else:
            signup_method = GroupSignupDetailsSignupMethod(_signup_method)

        signup_password = d.pop("signupPassword", UNSET)

        group_signup_details = cls(
            signup_method=signup_method,
            signup_password=signup_password,
        )

        group_signup_details.additional_properties = d
        return group_signup_details

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
