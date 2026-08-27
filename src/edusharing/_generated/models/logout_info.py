from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="LogoutInfo")


@_attrs_define
class LogoutInfo:
    """Logout configuration (URL, local/SSO-specific URLs, session destruction, AJAX)

    Attributes:
        url (str | Unset): URL to navigate to on logout
        local_url (str | Unset): URL for local users (overrides url if set)
        sso_url (str | Unset): URL for Shibboleth/SSO users (overrides url if set)
        destroy_session (bool | Unset): If true, destroy the edu-sharing session before navigating to URL
        ajax (bool | Unset): If true, call URL via AJAX; if false, navigate via browser
        next_ (str | Unset): URL to navigate to after AJAX call completes (only if ajax=true)
    """

    url: str | Unset = UNSET
    local_url: str | Unset = UNSET
    sso_url: str | Unset = UNSET
    destroy_session: bool | Unset = UNSET
    ajax: bool | Unset = UNSET
    next_: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        url = self.url

        local_url = self.local_url

        sso_url = self.sso_url

        destroy_session = self.destroy_session

        ajax = self.ajax

        next_ = self.next_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if url is not UNSET:
            field_dict["url"] = url
        if local_url is not UNSET:
            field_dict["localUrl"] = local_url
        if sso_url is not UNSET:
            field_dict["ssoUrl"] = sso_url
        if destroy_session is not UNSET:
            field_dict["destroySession"] = destroy_session
        if ajax is not UNSET:
            field_dict["ajax"] = ajax
        if next_ is not UNSET:
            field_dict["next"] = next_

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        url = d.pop("url", UNSET)

        local_url = d.pop("localUrl", UNSET)

        sso_url = d.pop("ssoUrl", UNSET)

        destroy_session = d.pop("destroySession", UNSET)

        ajax = d.pop("ajax", UNSET)

        next_ = d.pop("next", UNSET)

        logout_info = cls(
            url=url,
            local_url=local_url,
            sso_url=sso_url,
            destroy_session=destroy_session,
            ajax=ajax,
            next_=next_,
        )

        logout_info.additional_properties = d
        return logout_info

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
