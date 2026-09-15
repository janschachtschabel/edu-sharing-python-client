from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.organization_user_deprovisioning_mode import OrganizationUserDeprovisioningMode
from ..types import UNSET, Unset

T = TypeVar("T", bound="OrganizationUserDeprovisioning")


@_attrs_define
class OrganizationUserDeprovisioning:
    """
    Attributes:
        mode (OrganizationUserDeprovisioningMode | Unset): Shall the user data within this organization be cleaned up
        receiver (str | Unset): Receiver authority if mode == assign
    """

    mode: OrganizationUserDeprovisioningMode | Unset = UNSET
    receiver: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        mode: str | Unset = UNSET
        if not isinstance(self.mode, Unset):
            mode = self.mode.value

        receiver = self.receiver

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if mode is not UNSET:
            field_dict["mode"] = mode
        if receiver is not UNSET:
            field_dict["receiver"] = receiver

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        _mode = d.pop("mode", UNSET)
        mode: OrganizationUserDeprovisioningMode | Unset
        if isinstance(_mode, Unset):
            mode = UNSET
        else:
            mode = OrganizationUserDeprovisioningMode(_mode)

        receiver = d.pop("receiver", UNSET)

        organization_user_deprovisioning = cls(
            mode=mode,
            receiver=receiver,
        )

        organization_user_deprovisioning.additional_properties = d
        return organization_user_deprovisioning

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
