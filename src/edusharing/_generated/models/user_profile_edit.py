from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UserProfileEdit")


@_attrs_define
class UserProfileEdit:
    """
    Attributes:
        first_name (str | Unset):
        last_name (str | Unset):
        email (str | Unset):
        avatar (str | Unset):
        primary_affiliation (str | Unset):
        about (str | Unset):
        skills (list[None | str] | None | Unset):
        types (list[str] | Unset):
        size_quota (int | Unset):
        vcard (str | Unset):
    """

    first_name: str | Unset = UNSET
    last_name: str | Unset = UNSET
    email: str | Unset = UNSET
    avatar: str | Unset = UNSET
    primary_affiliation: str | Unset = UNSET
    about: str | Unset = UNSET
    skills: list[None | str] | None | Unset = UNSET
    types: list[str] | Unset = UNSET
    size_quota: int | Unset = UNSET
    vcard: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        first_name = self.first_name

        last_name = self.last_name

        email = self.email

        avatar = self.avatar

        primary_affiliation = self.primary_affiliation

        about = self.about

        skills: list[None | str] | None | Unset
        if isinstance(self.skills, Unset):
            skills = UNSET
        elif isinstance(self.skills, list):
            skills = []
            for skills_type_0_item_data in self.skills:
                skills_type_0_item: None | str
                skills_type_0_item = skills_type_0_item_data
                skills.append(skills_type_0_item)

        else:
            skills = self.skills

        types: list[str] | Unset = UNSET
        if not isinstance(self.types, Unset):
            types = self.types

        size_quota = self.size_quota

        vcard = self.vcard

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if first_name is not UNSET:
            field_dict["firstName"] = first_name
        if last_name is not UNSET:
            field_dict["lastName"] = last_name
        if email is not UNSET:
            field_dict["email"] = email
        if avatar is not UNSET:
            field_dict["avatar"] = avatar
        if primary_affiliation is not UNSET:
            field_dict["primaryAffiliation"] = primary_affiliation
        if about is not UNSET:
            field_dict["about"] = about
        if skills is not UNSET:
            field_dict["skills"] = skills
        if types is not UNSET:
            field_dict["types"] = types
        if size_quota is not UNSET:
            field_dict["sizeQuota"] = size_quota
        if vcard is not UNSET:
            field_dict["vcard"] = vcard

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        first_name = d.pop("firstName", UNSET)

        last_name = d.pop("lastName", UNSET)

        email = d.pop("email", UNSET)

        avatar = d.pop("avatar", UNSET)

        primary_affiliation = d.pop("primaryAffiliation", UNSET)

        about = d.pop("about", UNSET)

        def _parse_skills(data: object) -> list[None | str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                skills_type_0 = []
                _skills_type_0 = data
                for skills_type_0_item_data in _skills_type_0:

                    def _parse_skills_type_0_item(data: object) -> None | str:
                        if data is None:
                            return data
                        return cast(None | str, data)

                    skills_type_0_item = _parse_skills_type_0_item(skills_type_0_item_data)

                    skills_type_0.append(skills_type_0_item)

                return skills_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[None | str] | None | Unset, data)

        skills = _parse_skills(d.pop("skills", UNSET))

        types = cast(list[str], d.pop("types", UNSET))

        size_quota = d.pop("sizeQuota", UNSET)

        vcard = d.pop("vcard", UNSET)

        user_profile_edit = cls(
            first_name=first_name,
            last_name=last_name,
            email=email,
            avatar=avatar,
            primary_affiliation=primary_affiliation,
            about=about,
            skills=skills,
            types=types,
            size_quota=size_quota,
            vcard=vcard,
        )

        user_profile_edit.additional_properties = d
        return user_profile_edit

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
