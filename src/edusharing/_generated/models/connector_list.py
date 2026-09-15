from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.connector import Connector


T = TypeVar("T", bound="ConnectorList")


@_attrs_define
class ConnectorList:
    """
    Attributes:
        url (str | Unset):
        connectors (list[Connector] | Unset):
        simple_connectors (list[Connector] | Unset):
    """

    url: str | Unset = UNSET
    connectors: list[Connector] | Unset = UNSET
    simple_connectors: list[Connector] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        url = self.url

        connectors: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.connectors, Unset):
            connectors = []
            for connectors_item_data in self.connectors:
                connectors_item = connectors_item_data.to_dict()
                connectors.append(connectors_item)

        simple_connectors: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.simple_connectors, Unset):
            simple_connectors = []
            for simple_connectors_item_data in self.simple_connectors:
                simple_connectors_item = simple_connectors_item_data.to_dict()
                simple_connectors.append(simple_connectors_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if url is not UNSET:
            field_dict["url"] = url
        if connectors is not UNSET:
            field_dict["connectors"] = connectors
        if simple_connectors is not UNSET:
            field_dict["simpleConnectors"] = simple_connectors

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.connector import Connector

        d = dict(src_dict)
        url = d.pop("url", UNSET)

        _connectors = d.pop("connectors", UNSET)
        connectors: list[Connector] | Unset = UNSET
        if _connectors is not UNSET:
            connectors = []
            for connectors_item_data in _connectors:
                connectors_item = Connector.from_dict(connectors_item_data)

                connectors.append(connectors_item)

        _simple_connectors = d.pop("simpleConnectors", UNSET)
        simple_connectors: list[Connector] | Unset = UNSET
        if _simple_connectors is not UNSET:
            simple_connectors = []
            for simple_connectors_item_data in _simple_connectors:
                simple_connectors_item = Connector.from_dict(simple_connectors_item_data)

                simple_connectors.append(simple_connectors_item)

        connector_list = cls(
            url=url,
            connectors=connectors,
            simple_connectors=simple_connectors,
        )

        connector_list.additional_properties = d
        return connector_list

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
