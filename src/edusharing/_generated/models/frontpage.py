from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.frontpage_mode import FrontpageMode
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.query import Query


T = TypeVar("T", bound="Frontpage")


@_attrs_define
class Frontpage:
    """
    Attributes:
        total_count (int | Unset):
        display_count (int | Unset):
        mode (FrontpageMode | Unset):
        timespan (int | Unset):
        timespan_all (bool | Unset):
        queries (list[Query] | Unset):
        collection (str | Unset):
        global_query (str | Unset): Elasticsearch DSL query which is always applied (without any condition). Not
            supported for mode collection
    """

    total_count: int | Unset = UNSET
    display_count: int | Unset = UNSET
    mode: FrontpageMode | Unset = UNSET
    timespan: int | Unset = UNSET
    timespan_all: bool | Unset = UNSET
    queries: list[Query] | Unset = UNSET
    collection: str | Unset = UNSET
    global_query: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        total_count = self.total_count

        display_count = self.display_count

        mode: str | Unset = UNSET
        if not isinstance(self.mode, Unset):
            mode = self.mode.value

        timespan = self.timespan

        timespan_all = self.timespan_all

        queries: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.queries, Unset):
            queries = []
            for queries_item_data in self.queries:
                queries_item = queries_item_data.to_dict()
                queries.append(queries_item)

        collection = self.collection

        global_query = self.global_query

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if total_count is not UNSET:
            field_dict["totalCount"] = total_count
        if display_count is not UNSET:
            field_dict["displayCount"] = display_count
        if mode is not UNSET:
            field_dict["mode"] = mode
        if timespan is not UNSET:
            field_dict["timespan"] = timespan
        if timespan_all is not UNSET:
            field_dict["timespanAll"] = timespan_all
        if queries is not UNSET:
            field_dict["queries"] = queries
        if collection is not UNSET:
            field_dict["collection"] = collection
        if global_query is not UNSET:
            field_dict["globalQuery"] = global_query

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.query import Query

        d = dict(src_dict)
        total_count = d.pop("totalCount", UNSET)

        display_count = d.pop("displayCount", UNSET)

        _mode = d.pop("mode", UNSET)
        mode: FrontpageMode | Unset
        if isinstance(_mode, Unset):
            mode = UNSET
        else:
            mode = FrontpageMode(_mode)

        timespan = d.pop("timespan", UNSET)

        timespan_all = d.pop("timespanAll", UNSET)

        _queries = d.pop("queries", UNSET)
        queries: list[Query] | Unset = UNSET
        if _queries is not UNSET:
            queries = []
            for queries_item_data in _queries:
                queries_item = Query.from_dict(queries_item_data)

                queries.append(queries_item)

        collection = d.pop("collection", UNSET)

        global_query = d.pop("globalQuery", UNSET)

        frontpage = cls(
            total_count=total_count,
            display_count=display_count,
            mode=mode,
            timespan=timespan,
            timespan_all=timespan_all,
            queries=queries,
            collection=collection,
            global_query=global_query,
        )

        frontpage.additional_properties = d
        return frontpage

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
