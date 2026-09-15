from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="NodeLTIDeepLink")


@_attrs_define
class NodeLTIDeepLink:
    """Node LTI deep linking information

    Attributes:
        lti_deep_link_return_url (str | Unset):
        jwt_deep_link_response (str | Unset):
    """

    lti_deep_link_return_url: str | Unset = UNSET
    jwt_deep_link_response: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        lti_deep_link_return_url = self.lti_deep_link_return_url

        jwt_deep_link_response = self.jwt_deep_link_response

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if lti_deep_link_return_url is not UNSET:
            field_dict["ltiDeepLinkReturnUrl"] = lti_deep_link_return_url
        if jwt_deep_link_response is not UNSET:
            field_dict["jwtDeepLinkResponse"] = jwt_deep_link_response

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        lti_deep_link_return_url = d.pop("ltiDeepLinkReturnUrl", UNSET)

        jwt_deep_link_response = d.pop("jwtDeepLinkResponse", UNSET)

        node_lti_deep_link = cls(
            lti_deep_link_return_url=lti_deep_link_return_url,
            jwt_deep_link_response=jwt_deep_link_response,
        )

        node_lti_deep_link.additional_properties = d
        return node_lti_deep_link

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
