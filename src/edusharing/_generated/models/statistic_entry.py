from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.statistic_entity import StatisticEntity


T = TypeVar("T", bound="StatisticEntry")


@_attrs_define
class StatisticEntry:
    """
    Attributes:
        property_ (str):
        entities (list[StatisticEntity]):
    """

    property_: str
    entities: list[StatisticEntity]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        property_ = self.property_

        entities = []
        for entities_item_data in self.entities:
            entities_item = entities_item_data.to_dict()
            entities.append(entities_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "property": property_,
                "entities": entities,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.statistic_entity import StatisticEntity

        d = dict(src_dict)
        property_ = d.pop("property")

        entities = []
        _entities = d.pop("entities")
        for entities_item_data in _entities:
            entities_item = StatisticEntity.from_dict(entities_item_data)

            entities.append(entities_item)

        statistic_entry = cls(
            property_=property_,
            entities=entities,
        )

        statistic_entry.additional_properties = d
        return statistic_entry

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
