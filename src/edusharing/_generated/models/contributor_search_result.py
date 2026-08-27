from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.contributor_data import ContributorData
    from ..models.pagination import Pagination


T = TypeVar("T", bound="ContributorSearchResult")


@_attrs_define
class ContributorSearchResult:
    """
    Attributes:
        contributors (list[ContributorData]):
        pagination (Pagination):
    """

    contributors: list[ContributorData]
    pagination: Pagination
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        contributors = []
        for contributors_item_data in self.contributors:
            contributors_item = contributors_item_data.to_dict()
            contributors.append(contributors_item)

        pagination = self.pagination.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "contributors": contributors,
                "pagination": pagination,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.contributor_data import ContributorData
        from ..models.pagination import Pagination

        d = dict(src_dict)
        contributors = []
        _contributors = d.pop("contributors")
        for contributors_item_data in _contributors:
            contributors_item = ContributorData.from_dict(contributors_item_data)

            contributors.append(contributors_item)

        pagination = Pagination.from_dict(d.pop("pagination"))

        contributor_search_result = cls(
            contributors=contributors,
            pagination=pagination,
        )

        contributor_search_result.additional_properties = d
        return contributor_search_result

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
