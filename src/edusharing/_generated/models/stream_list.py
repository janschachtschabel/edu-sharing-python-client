from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.pagination import Pagination
    from ..models.stream_entry import StreamEntry


T = TypeVar("T", bound="StreamList")


@_attrs_define
class StreamList:
    """
    Attributes:
        stream (list[StreamEntry] | Unset):
        pagination (Pagination | Unset):
    """

    stream: list[StreamEntry] | Unset = UNSET
    pagination: Pagination | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        stream: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.stream, Unset):
            stream = []
            for stream_item_data in self.stream:
                stream_item = stream_item_data.to_dict()
                stream.append(stream_item)

        pagination: dict[str, Any] | Unset = UNSET
        if not isinstance(self.pagination, Unset):
            pagination = self.pagination.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if stream is not UNSET:
            field_dict["stream"] = stream
        if pagination is not UNSET:
            field_dict["pagination"] = pagination

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.pagination import Pagination
        from ..models.stream_entry import StreamEntry

        d = dict(src_dict)
        _stream = d.pop("stream", UNSET)
        stream: list[StreamEntry] | Unset = UNSET
        if _stream is not UNSET:
            stream = []
            for stream_item_data in _stream:
                stream_item = StreamEntry.from_dict(stream_item_data)

                stream.append(stream_item)

        _pagination = d.pop("pagination", UNSET)
        pagination: Pagination | Unset
        if isinstance(_pagination, Unset):
            pagination = UNSET
        else:
            pagination = Pagination.from_dict(_pagination)

        stream_list = cls(
            stream=stream,
            pagination=pagination,
        )

        stream_list.additional_properties = d
        return stream_list

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
