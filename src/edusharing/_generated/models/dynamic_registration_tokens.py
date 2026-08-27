from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.dynamic_registration_token import DynamicRegistrationToken


T = TypeVar("T", bound="DynamicRegistrationTokens")


@_attrs_define
class DynamicRegistrationTokens:
    """
    Attributes:
        registration_links (list[DynamicRegistrationToken] | Unset):
    """

    registration_links: list[DynamicRegistrationToken] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        registration_links: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.registration_links, Unset):
            registration_links = []
            for registration_links_item_data in self.registration_links:
                registration_links_item = registration_links_item_data.to_dict()
                registration_links.append(registration_links_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if registration_links is not UNSET:
            field_dict["registrationLinks"] = registration_links

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.dynamic_registration_token import DynamicRegistrationToken

        d = dict(src_dict)
        _registration_links = d.pop("registrationLinks", UNSET)
        registration_links: list[DynamicRegistrationToken] | Unset = UNSET
        if _registration_links is not UNSET:
            registration_links = []
            for registration_links_item_data in _registration_links:
                registration_links_item = DynamicRegistrationToken.from_dict(
                    registration_links_item_data
                )

                registration_links.append(registration_links_item)

        dynamic_registration_tokens = cls(
            registration_links=registration_links,
        )

        dynamic_registration_tokens.additional_properties = d
        return dynamic_registration_tokens

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
