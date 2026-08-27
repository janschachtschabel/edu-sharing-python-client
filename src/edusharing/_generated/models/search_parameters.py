from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.mds_query_criteria import MdsQueryCriteria
    from ..models.search_facet import SearchFacet


T = TypeVar("T", bound="SearchParameters")


@_attrs_define
class SearchParameters:
    """
    Attributes:
        criteria (list[MdsQueryCriteria]):
        facets (list[SearchFacet] | Unset):
        facet_min_count (int | Unset):  Default: 5.
        facet_limit (int | Unset):  Default: 10.
        facet_suggest (str | Unset):
        permissions (list[str] | Unset):
        resolve_collections (bool | Unset):
        resolve_usernames (bool | Unset):
        return_suggestions (bool | Unset):
        excludes (list[str] | Unset):
    """

    criteria: list[MdsQueryCriteria]
    facets: list[SearchFacet] | Unset = UNSET
    facet_min_count: int | Unset = 5
    facet_limit: int | Unset = 10
    facet_suggest: str | Unset = UNSET
    permissions: list[str] | Unset = UNSET
    resolve_collections: bool | Unset = UNSET
    resolve_usernames: bool | Unset = UNSET
    return_suggestions: bool | Unset = UNSET
    excludes: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        criteria = []
        for criteria_item_data in self.criteria:
            criteria_item = criteria_item_data.to_dict()
            criteria.append(criteria_item)

        facets: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.facets, Unset):
            facets = []
            for facets_item_data in self.facets:
                facets_item = facets_item_data.to_dict()
                facets.append(facets_item)

        facet_min_count = self.facet_min_count

        facet_limit = self.facet_limit

        facet_suggest = self.facet_suggest

        permissions: list[str] | Unset = UNSET
        if not isinstance(self.permissions, Unset):
            permissions = self.permissions

        resolve_collections = self.resolve_collections

        resolve_usernames = self.resolve_usernames

        return_suggestions = self.return_suggestions

        excludes: list[str] | Unset = UNSET
        if not isinstance(self.excludes, Unset):
            excludes = self.excludes

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "criteria": criteria,
            }
        )
        if facets is not UNSET:
            field_dict["facets"] = facets
        if facet_min_count is not UNSET:
            field_dict["facetMinCount"] = facet_min_count
        if facet_limit is not UNSET:
            field_dict["facetLimit"] = facet_limit
        if facet_suggest is not UNSET:
            field_dict["facetSuggest"] = facet_suggest
        if permissions is not UNSET:
            field_dict["permissions"] = permissions
        if resolve_collections is not UNSET:
            field_dict["resolveCollections"] = resolve_collections
        if resolve_usernames is not UNSET:
            field_dict["resolveUsernames"] = resolve_usernames
        if return_suggestions is not UNSET:
            field_dict["returnSuggestions"] = return_suggestions
        if excludes is not UNSET:
            field_dict["excludes"] = excludes

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.mds_query_criteria import MdsQueryCriteria
        from ..models.search_facet import SearchFacet

        d = dict(src_dict)
        criteria = []
        _criteria = d.pop("criteria")
        for criteria_item_data in _criteria:
            criteria_item = MdsQueryCriteria.from_dict(criteria_item_data)

            criteria.append(criteria_item)

        _facets = d.pop("facets", UNSET)
        facets: list[SearchFacet] | Unset = UNSET
        if _facets is not UNSET:
            facets = []
            for facets_item_data in _facets:
                facets_item = SearchFacet.from_dict(facets_item_data)

                facets.append(facets_item)

        facet_min_count = d.pop("facetMinCount", UNSET)

        facet_limit = d.pop("facetLimit", UNSET)

        facet_suggest = d.pop("facetSuggest", UNSET)

        permissions = cast(list[str], d.pop("permissions", UNSET))

        resolve_collections = d.pop("resolveCollections", UNSET)

        resolve_usernames = d.pop("resolveUsernames", UNSET)

        return_suggestions = d.pop("returnSuggestions", UNSET)

        excludes = cast(list[str], d.pop("excludes", UNSET))

        search_parameters = cls(
            criteria=criteria,
            facets=facets,
            facet_min_count=facet_min_count,
            facet_limit=facet_limit,
            facet_suggest=facet_suggest,
            permissions=permissions,
            resolve_collections=resolve_collections,
            resolve_usernames=resolve_usernames,
            return_suggestions=return_suggestions,
            excludes=excludes,
        )

        search_parameters.additional_properties = d
        return search_parameters

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
