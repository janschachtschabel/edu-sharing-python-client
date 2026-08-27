from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.node import Node


T = TypeVar("T", bound="SignedNodeEntry")


@_attrs_define
class SignedNodeEntry:
    """
    Attributes:
        node (Node):
        jwt (str):
        signed_node (str):
        signature (str):
        signature_algorithm (str | Unset):
        rendering_base_url (str | Unset):
    """

    node: Node
    jwt: str
    signed_node: str
    signature: str
    signature_algorithm: str | Unset = UNSET
    rendering_base_url: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        node = self.node.to_dict()

        jwt = self.jwt

        signed_node = self.signed_node

        signature = self.signature

        signature_algorithm = self.signature_algorithm

        rendering_base_url = self.rendering_base_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "node": node,
                "jwt": jwt,
                "signedNode": signed_node,
                "signature": signature,
            }
        )
        if signature_algorithm is not UNSET:
            field_dict["signatureAlgorithm"] = signature_algorithm
        if rendering_base_url is not UNSET:
            field_dict["renderingBaseUrl"] = rendering_base_url

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.node import Node

        d = dict(src_dict)
        node = Node.from_dict(d.pop("node"))

        jwt = d.pop("jwt")

        signed_node = d.pop("signedNode")

        signature = d.pop("signature")

        signature_algorithm = d.pop("signatureAlgorithm", UNSET)

        rendering_base_url = d.pop("renderingBaseUrl", UNSET)

        signed_node_entry = cls(
            node=node,
            jwt=jwt,
            signed_node=signed_node,
            signature=signature,
            signature_algorithm=signature_algorithm,
            rendering_base_url=rendering_base_url,
        )

        signed_node_entry.additional_properties = d
        return signed_node_entry

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
