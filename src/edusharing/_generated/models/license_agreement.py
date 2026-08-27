from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.license_agreement_node import LicenseAgreementNode


T = TypeVar("T", bound="LicenseAgreement")


@_attrs_define
class LicenseAgreement:
    """License agreement display settings (node IDs with HTML content per language)

    Attributes:
        node_id (list[LicenseAgreementNode] | Unset): Array of license agreement entries (one per language, with
            fallback)
    """

    node_id: list[LicenseAgreementNode] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        node_id: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.node_id, Unset):
            node_id = []
            for node_id_item_data in self.node_id:
                node_id_item = node_id_item_data.to_dict()
                node_id.append(node_id_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if node_id is not UNSET:
            field_dict["nodeId"] = node_id

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.license_agreement_node import LicenseAgreementNode

        d = dict(src_dict)
        _node_id = d.pop("nodeId", UNSET)
        node_id: list[LicenseAgreementNode] | Unset = UNSET
        if _node_id is not UNSET:
            node_id = []
            for node_id_item_data in _node_id:
                node_id_item = LicenseAgreementNode.from_dict(node_id_item_data)

                node_id.append(node_id_item)

        license_agreement = cls(
            node_id=node_id,
        )

        license_agreement.additional_properties = d
        return license_agreement

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
