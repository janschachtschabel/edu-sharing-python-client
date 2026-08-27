from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.search_facet_args import SearchFacetArgs


T = TypeVar("T", bound="SearchFacet")


@_attrs_define
class SearchFacet:
    """
    Attributes:
        property_ (str | Unset):
        args (SearchFacetArgs | Unset):
    """

    property_: str | Unset = UNSET
    args: SearchFacetArgs | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        property_ = self.property_

        args: dict[str, Any] | Unset = UNSET
        if not isinstance(self.args, Unset):
            args = self.args.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if property_ is not UNSET:
            field_dict["property"] = property_
        if args is not UNSET:
            field_dict["args"] = args

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.search_facet_args import SearchFacetArgs

        d = dict(src_dict)
        property_ = d.pop("property", UNSET)

        _args = d.pop("args", UNSET)
        args: SearchFacetArgs | Unset
        if isinstance(_args, Unset):
            args = UNSET
        else:
            args = SearchFacetArgs.from_dict(_args)

        search_facet = cls(
            property_=property_,
            args=args,
        )

        search_facet.additional_properties = d
        return search_facet

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
