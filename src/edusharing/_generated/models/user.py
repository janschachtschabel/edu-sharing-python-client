from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.user_authority_type import UserAuthorityType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.node_ref import NodeRef
    from ..models.organization import Organization
    from ..models.user_profile import UserProfile
    from ..models.user_properties import UserProperties
    from ..models.user_quota import UserQuota
    from ..models.user_status import UserStatus


T = TypeVar("T", bound="User")


@_attrs_define
class User:
    """
    Attributes:
        authority_name (str):
        authority_type (UserAuthorityType | Unset):
        properties (UserProperties | Unset):
        editable (bool | Unset):
        user_name (str | Unset):
        profile (UserProfile | Unset):
        status (UserStatus | Unset):
        organizations (list[Organization] | Unset):
        home_folder (NodeRef | Unset):
        shared_folders (list[NodeRef] | Unset):
        quota (UserQuota | Unset):
    """

    authority_name: str
    authority_type: UserAuthorityType | Unset = UNSET
    properties: UserProperties | Unset = UNSET
    editable: bool | Unset = UNSET
    user_name: str | Unset = UNSET
    profile: UserProfile | Unset = UNSET
    status: UserStatus | Unset = UNSET
    organizations: list[Organization] | Unset = UNSET
    home_folder: NodeRef | Unset = UNSET
    shared_folders: list[NodeRef] | Unset = UNSET
    quota: UserQuota | Unset = UNSET
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

        user_name = self.user_name

        profile: dict[str, Any] | Unset = UNSET
        if not isinstance(self.profile, Unset):
            profile = self.profile.to_dict()

        status: dict[str, Any] | Unset = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.to_dict()

        organizations: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.organizations, Unset):
            organizations = []
            for organizations_item_data in self.organizations:
                organizations_item = organizations_item_data.to_dict()
                organizations.append(organizations_item)

        home_folder: dict[str, Any] | Unset = UNSET
        if not isinstance(self.home_folder, Unset):
            home_folder = self.home_folder.to_dict()

        shared_folders: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.shared_folders, Unset):
            shared_folders = []
            for shared_folders_item_data in self.shared_folders:
                shared_folders_item = shared_folders_item_data.to_dict()
                shared_folders.append(shared_folders_item)

        quota: dict[str, Any] | Unset = UNSET
        if not isinstance(self.quota, Unset):
            quota = self.quota.to_dict()

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
        if user_name is not UNSET:
            field_dict["userName"] = user_name
        if profile is not UNSET:
            field_dict["profile"] = profile
        if status is not UNSET:
            field_dict["status"] = status
        if organizations is not UNSET:
            field_dict["organizations"] = organizations
        if home_folder is not UNSET:
            field_dict["homeFolder"] = home_folder
        if shared_folders is not UNSET:
            field_dict["sharedFolders"] = shared_folders
        if quota is not UNSET:
            field_dict["quota"] = quota

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.node_ref import NodeRef
        from ..models.organization import Organization
        from ..models.user_profile import UserProfile
        from ..models.user_properties import UserProperties
        from ..models.user_quota import UserQuota
        from ..models.user_status import UserStatus

        d = dict(src_dict)
        authority_name = d.pop("authorityName")

        _authority_type = d.pop("authorityType", UNSET)
        authority_type: UserAuthorityType | Unset
        if isinstance(_authority_type, Unset):
            authority_type = UNSET
        else:
            authority_type = UserAuthorityType(_authority_type)

        _properties = d.pop("properties", UNSET)
        properties: UserProperties | Unset
        if isinstance(_properties, Unset):
            properties = UNSET
        else:
            properties = UserProperties.from_dict(_properties)

        editable = d.pop("editable", UNSET)

        user_name = d.pop("userName", UNSET)

        _profile = d.pop("profile", UNSET)
        profile: UserProfile | Unset
        if isinstance(_profile, Unset):
            profile = UNSET
        else:
            profile = UserProfile.from_dict(_profile)

        _status = d.pop("status", UNSET)
        status: UserStatus | Unset
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = UserStatus.from_dict(_status)

        _organizations = d.pop("organizations", UNSET)
        organizations: list[Organization] | Unset = UNSET
        if _organizations is not UNSET:
            organizations = []
            for organizations_item_data in _organizations:
                organizations_item = Organization.from_dict(organizations_item_data)

                organizations.append(organizations_item)

        _home_folder = d.pop("homeFolder", UNSET)
        home_folder: NodeRef | Unset
        if isinstance(_home_folder, Unset):
            home_folder = UNSET
        else:
            home_folder = NodeRef.from_dict(_home_folder)

        _shared_folders = d.pop("sharedFolders", UNSET)
        shared_folders: list[NodeRef] | Unset = UNSET
        if _shared_folders is not UNSET:
            shared_folders = []
            for shared_folders_item_data in _shared_folders:
                shared_folders_item = NodeRef.from_dict(shared_folders_item_data)

                shared_folders.append(shared_folders_item)

        _quota = d.pop("quota", UNSET)
        quota: UserQuota | Unset
        if isinstance(_quota, Unset):
            quota = UNSET
        else:
            quota = UserQuota.from_dict(_quota)

        user = cls(
            authority_name=authority_name,
            authority_type=authority_type,
            properties=properties,
            editable=editable,
            user_name=user_name,
            profile=profile,
            status=status,
            organizations=organizations,
            home_folder=home_folder,
            shared_folders=shared_folders,
            quota=quota,
        )

        user.additional_properties = d
        return user

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
