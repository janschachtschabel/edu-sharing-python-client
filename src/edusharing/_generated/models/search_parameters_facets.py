from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.mds_query_criteria import MdsQueryCriteria
    from ..models.search_facet import SearchFacet


T = TypeVar("T", bound="SearchParametersFacets")


@_attrs_define
class SearchParametersFacets:
    """
    Attributes:
        facets (list[SearchFacet]):
        criteria (list[MdsQueryCriteria]):
        facet_min_count (int | Unset):  Default: 5.
        facet_limit (int | Unset):  Default: 10.
        facet_suggest (str | Unset):
    """

    facets: list[SearchFacet]
    criteria: list[MdsQueryCriteria]
    facet_min_count: int | Unset = 5
    facet_limit: int | Unset = 10
    facet_suggest: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        facets = []
        for facets_item_data in self.facets:
            facets_item = facets_item_data.to_dict()
            facets.append(facets_item)

        criteria = []
        for criteria_item_data in self.criteria:
            criteria_item = criteria_item_data.to_dict()
            criteria.append(criteria_item)

        facet_min_count = self.facet_min_count

        facet_limit = self.facet_limit

        facet_suggest = self.facet_suggest

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "facets": facets,
                "criteria": criteria,
            }
        )
        if facet_min_count is not UNSET:
            field_dict["facetMinCount"] = facet_min_count
        if facet_limit is not UNSET:
            field_dict["facetLimit"] = facet_limit
        if facet_suggest is not UNSET:
            field_dict["facetSuggest"] = facet_suggest

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.mds_query_criteria import MdsQueryCriteria
        from ..models.search_facet import SearchFacet

        d = dict(src_dict)
        facets = []
        _facets = d.pop("facets")
        for facets_item_data in _facets:
            facets_item = SearchFacet.from_dict(facets_item_data)

            facets.append(facets_item)

        criteria = []
        _criteria = d.pop("criteria")
        for criteria_item_data in _criteria:
            criteria_item = MdsQueryCriteria.from_dict(criteria_item_data)

            criteria.append(criteria_item)

        facet_min_count = d.pop("facetMinCount", UNSET)

        facet_limit = d.pop("facetLimit", UNSET)

        facet_suggest = d.pop("facetSuggest", UNSET)

        search_parameters_facets = cls(
            facets=facets,
            criteria=criteria,
            facet_min_count=facet_min_count,
            facet_limit=facet_limit,
            facet_suggest=facet_suggest,
        )

        search_parameters_facets.additional_properties = d
        return search_parameters_facets

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
