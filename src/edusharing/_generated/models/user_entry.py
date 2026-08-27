from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.user import User


T = TypeVar("T", bound="UserEntry")


@_attrs_define
class UserEntry:
    """
    Attributes:
        person (User):
        edit_profile (bool | Unset):
    """

    person: User
    edit_profile: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        person = self.person.to_dict()

        edit_profile = self.edit_profile

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "person": person,
            }
        )
        if edit_profile is not UNSET:
            field_dict["editProfile"] = edit_profile

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.user import User

        d = dict(src_dict)
        person = User.from_dict(d.pop("person"))

        edit_profile = d.pop("editProfile", UNSET)

        user_entry = cls(
            person=person,
            edit_profile=edit_profile,
        )

        user_entry.additional_properties = d
        return user_entry

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
