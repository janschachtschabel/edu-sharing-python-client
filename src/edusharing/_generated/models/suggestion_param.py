from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.mds_query_criteria import MdsQueryCriteria
    from ..models.value_parameters import ValueParameters


T = TypeVar("T", bound="SuggestionParam")


@_attrs_define
class SuggestionParam:
    """
    Attributes:
        value_parameters (ValueParameters | Unset):
        criteria (list[MdsQueryCriteria] | Unset):
    """

    value_parameters: ValueParameters | Unset = UNSET
    criteria: list[MdsQueryCriteria] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        value_parameters: dict[str, Any] | Unset = UNSET
        if not isinstance(self.value_parameters, Unset):
            value_parameters = self.value_parameters.to_dict()

        criteria: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.criteria, Unset):
            criteria = []
            for criteria_item_data in self.criteria:
                criteria_item = criteria_item_data.to_dict()
                criteria.append(criteria_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if value_parameters is not UNSET:
            field_dict["valueParameters"] = value_parameters
        if criteria is not UNSET:
            field_dict["criteria"] = criteria

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.mds_query_criteria import MdsQueryCriteria
        from ..models.value_parameters import ValueParameters

        d = dict(src_dict)
        _value_parameters = d.pop("valueParameters", UNSET)
        value_parameters: ValueParameters | Unset
        if isinstance(_value_parameters, Unset):
            value_parameters = UNSET
        else:
            value_parameters = ValueParameters.from_dict(_value_parameters)

        _criteria = d.pop("criteria", UNSET)
        criteria: list[MdsQueryCriteria] | Unset = UNSET
        if _criteria is not UNSET:
            criteria = []
            for criteria_item_data in _criteria:
                criteria_item = MdsQueryCriteria.from_dict(criteria_item_data)

                criteria.append(criteria_item)

        suggestion_param = cls(
            value_parameters=value_parameters,
            criteria=criteria,
        )

        suggestion_param.additional_properties = d
        return suggestion_param

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
