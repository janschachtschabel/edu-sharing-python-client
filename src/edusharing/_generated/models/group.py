from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.group_authority_type import GroupAuthorityType
from ..models.group_signup_method import GroupSignupMethod
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.group_profile import GroupProfile
    from ..models.group_properties import GroupProperties
    from ..models.node_ref import NodeRef
    from ..models.organization import Organization


T = TypeVar("T", bound="Group")


@_attrs_define
class Group:
    """
    Attributes:
        authority_name (str):
        authority_type (GroupAuthorityType | Unset):
        properties (GroupProperties | Unset):
        editable (bool | Unset):
        signup_method (GroupSignupMethod | Unset):
        group_name (str | Unset):
        profile (GroupProfile | Unset):
        ref (NodeRef | Unset):
        aspects (list[str] | Unset):
        organizations (list[Organization] | Unset):
    """

    authority_name: str
    authority_type: GroupAuthorityType | Unset = UNSET
    properties: GroupProperties | Unset = UNSET
    editable: bool | Unset = UNSET
    signup_method: GroupSignupMethod | Unset = UNSET
    group_name: str | Unset = UNSET
    profile: GroupProfile | Unset = UNSET
    ref: NodeRef | Unset = UNSET
    aspects: list[str] | Unset = UNSET
    organizations: list[Organization] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        authority_name = self.authority_name

        authority_type: str | Unset = UNSET
        if not isinstance(self.authority_type, Unset):
            authority_type = self.authority_type.value

        properties: dict[str, Any] | Unset = UNSET
        if not isinstance(self.properties, Unset):
            properties = self.properties.to_dict()

        editable = self.editable

        signup_method: str | Unset = UNSET
        if not isinstance(self.signup_method, Unset):
            signup_method = self.signup_method.value

        group_name = self.group_name

        profile: dict[str, Any] | Unset = UNSET
        if not isinstance(self.profile, Unset):
            profile = self.profile.to_dict()

        ref: dict[str, Any] | Unset = UNSET
        if not isinstance(self.ref, Unset):
            ref = self.ref.to_dict()

        aspects: list[str] | Unset = UNSET
        if not isinstance(self.aspects, Unset):
            aspects = self.aspects

        organizations: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.organizations, Unset):
            organizations = []
            for organizations_item_data in self.organizations:
                organizations_item = organizations_item_data.to_dict()
                organizations.append(organizations_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "authorityName": authority_name,
            }
        )
        if authority_type is not UNSET:
            field_dict["authorityType"] = authority_type
        if properties is not UNSET:
            field_dict["properties"] = properties
        if editable is not UNSET:
            field_dict["editable"] = editable
        if signup_method is not UNSET:
            field_dict["signupMethod"] = signup_method
        if group_name is not UNSET:
            field_dict["groupName"] = group_name
        if profile is not UNSET:
            field_dict["profile"] = profile
        if ref is not UNSET:
            field_dict["ref"] = ref
        if aspects is not UNSET:
            field_dict["aspects"] = aspects
        if organizations is not UNSET:
            field_dict["organizations"] = organizations

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.group_profile import GroupProfile
        from ..models.group_properties import GroupProperties
        from ..models.node_ref import NodeRef
        from ..models.organization import Organization

        d = dict(src_dict)
        authority_name = d.pop("authorityName")

        _authority_type = d.pop("authorityType", UNSET)
        authority_type: GroupAuthorityType | Unset
        if isinstance(_authority_type, Unset):
            authority_type = UNSET
        else:
            authority_type = GroupAuthorityType(_authority_type)

        _properties = d.pop("properties", UNSET)
        properties: GroupProperties | Unset
        if isinstance(_properties, Unset):
            properties = UNSET
        else:
            properties = GroupProperties.from_dict(_properties)

        editable = d.pop("editable", UNSET)

        _signup_method = d.pop("signupMethod", UNSET)
        signup_method: GroupSignupMethod | Unset
        if isinstance(_signup_method, Unset):
            signup_method = UNSET
        else:
            signup_method = GroupSignupMethod(_signup_method)

        group_name = d.pop("groupName", UNSET)

        _profile = d.pop("profile", UNSET)
        profile: GroupProfile | Unset
        if isinstance(_profile, Unset):
            profile = UNSET
        else:
            profile = GroupProfile.from_dict(_profile)

        _ref = d.pop("ref", UNSET)
        ref: NodeRef | Unset
        if isinstance(_ref, Unset):
            ref = UNSET
        else:
            ref = NodeRef.from_dict(_ref)

        aspects = cast(list[str], d.pop("aspects", UNSET))

        _organizations = d.pop("organizations", UNSET)
        organizations: list[Organization] | Unset = UNSET
        if _organizations is not UNSET:
            organizations = []
            for organizations_item_data in _organizations:
                organizations_item = Organization.from_dict(organizations_item_data)

                organizations.append(organizations_item)

        group = cls(
            authority_name=authority_name,
            authority_type=authority_type,
            properties=properties,
            editable=editable,
            signup_method=signup_method,
            group_name=group_name,
            profile=profile,
            ref=ref,
            aspects=aspects,
            organizations=organizations,
        )

        group.additional_properties = d
        return group

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
