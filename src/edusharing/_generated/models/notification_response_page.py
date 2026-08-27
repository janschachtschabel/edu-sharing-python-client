from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.notification_event_dto import NotificationEventDTO
    from ..models.pageable import Pageable
    from ..models.sort import Sort


T = TypeVar("T", bound="NotificationResponsePage")


@_attrs_define
class NotificationResponsePage:
    """
    Attributes:
        content (list[NotificationEventDTO] | Unset):
        pageable (Pageable | Unset):
        total_pages (int | Unset):
        total_elements (int | Unset):
        last (bool | Unset):
        first (bool | Unset):
        size (int | Unset):
        number (int | Unset):
        sort (Sort | Unset):
        number_of_elements (int | Unset):
        empty (bool | Unset):
    """

    content: list[NotificationEventDTO] | Unset = UNSET
    pageable: Pageable | Unset = UNSET
    total_pages: int | Unset = UNSET
    total_elements: int | Unset = UNSET
    last: bool | Unset = UNSET
    first: bool | Unset = UNSET
    size: int | Unset = UNSET
    number: int | Unset = UNSET
    sort: Sort | Unset = UNSET
    number_of_elements: int | Unset = UNSET
    empty: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        content: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.content, Unset):
            content = []
            for content_item_data in self.content:
                content_item = content_item_data.to_dict()
                content.append(content_item)

        pageable: dict[str, Any] | Unset = UNSET
        if not isinstance(self.pageable, Unset):
            pageable = self.pageable.to_dict()

        total_pages = self.total_pages

        total_elements = self.total_elements

        last = self.last

        first = self.first

        size = self.size

        number = self.number

        sort: dict[str, Any] | Unset = UNSET
        if not isinstance(self.sort, Unset):
            sort = self.sort.to_dict()

        number_of_elements = self.number_of_elements

        empty = self.empty

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if content is not UNSET:
            field_dict["content"] = content
        if pageable is not UNSET:
            field_dict["pageable"] = pageable
        if total_pages is not UNSET:
            field_dict["totalPages"] = total_pages
        if total_elements is not UNSET:
            field_dict["totalElements"] = total_elements
        if last is not UNSET:
            field_dict["last"] = last
        if first is not UNSET:
            field_dict["first"] = first
        if size is not UNSET:
            field_dict["size"] = size
        if number is not UNSET:
            field_dict["number"] = number
        if sort is not UNSET:
            field_dict["sort"] = sort
        if number_of_elements is not UNSET:
            field_dict["numberOfElements"] = number_of_elements
        if empty is not UNSET:
            field_dict["empty"] = empty

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.notification_event_dto import NotificationEventDTO
        from ..models.pageable import Pageable
        from ..models.sort import Sort

        d = dict(src_dict)
        _content = d.pop("content", UNSET)
        content: list[NotificationEventDTO] | Unset = UNSET
        if _content is not UNSET:
            content = []
            for content_item_data in _content:
                content_item = NotificationEventDTO.from_dict(content_item_data)

                content.append(content_item)

        _pageable = d.pop("pageable", UNSET)
        pageable: Pageable | Unset
        if isinstance(_pageable, Unset):
            pageable = UNSET
        else:
            pageable = Pageable.from_dict(_pageable)

        total_pages = d.pop("totalPages", UNSET)

        total_elements = d.pop("totalElements", UNSET)

        last = d.pop("last", UNSET)

        first = d.pop("first", UNSET)

        size = d.pop("size", UNSET)

        number = d.pop("number", UNSET)

        _sort = d.pop("sort", UNSET)
        sort: Sort | Unset
        if isinstance(_sort, Unset):
            sort = UNSET
        else:
            sort = Sort.from_dict(_sort)

        number_of_elements = d.pop("numberOfElements", UNSET)

        empty = d.pop("empty", UNSET)

        notification_response_page = cls(
            content=content,
            pageable=pageable,
            total_pages=total_pages,
            total_elements=total_elements,
            last=last,
            first=first,
            size=size,
            number=number,
            sort=sort,
            number_of_elements=number_of_elements,
            empty=empty,
        )

        notification_response_page.additional_properties = d
        return notification_response_page

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
