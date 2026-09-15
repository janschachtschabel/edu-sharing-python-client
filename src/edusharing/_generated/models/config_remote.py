from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.config_remote_rocketchat import ConfigRemoteRocketchat


T = TypeVar("T", bound="ConfigRemote")


@_attrs_define
class ConfigRemote:
    """Remote repository configuration

    Attributes:
        rocketchat (ConfigRemoteRocketchat | Unset):
    """

    rocketchat: ConfigRemoteRocketchat | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        rocketchat: dict[str, Any] | Unset = UNSET
        if not isinstance(self.rocketchat, Unset):
            rocketchat = self.rocketchat.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if rocketchat is not UNSET:
            field_dict["rocketchat"] = rocketchat

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.config_remote_rocketchat import ConfigRemoteRocketchat

        d = dict(src_dict)
        _rocketchat = d.pop("rocketchat", UNSET)
        rocketchat: ConfigRemoteRocketchat | Unset
        if isinstance(_rocketchat, Unset):
            rocketchat = UNSET
        else:
            rocketchat = ConfigRemoteRocketchat.from_dict(_rocketchat)

        config_remote = cls(
            rocketchat=rocketchat,
        )

        config_remote.additional_properties = d
        return config_remote

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
