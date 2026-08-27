from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.create import Create
    from ..models.mds_ai_config import MdsAiConfig
    from ..models.mds_group import MdsGroup
    from ..models.mds_list import MdsList
    from ..models.mds_sort import MdsSort
    from ..models.mds_view import MdsView
    from ..models.mds_widget import MdsWidget


T = TypeVar("T", bound="Mds")


@_attrs_define
class Mds:
    """
    Attributes:
        id (str):
        name (str):
        widgets (list[MdsWidget]):
        views (list[MdsView]):
        groups (list[MdsGroup]):
        lists (list[MdsList]):
        sorts (list[MdsSort]):
        create (Create | Unset):
        ai_configs (list[MdsAiConfig] | Unset):
    """

    id: str
    name: str
    widgets: list[MdsWidget]
    views: list[MdsView]
    groups: list[MdsGroup]
    lists: list[MdsList]
    sorts: list[MdsSort]
    create: Create | Unset = UNSET
    ai_configs: list[MdsAiConfig] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        widgets = []
        for widgets_item_data in self.widgets:
            widgets_item = widgets_item_data.to_dict()
            widgets.append(widgets_item)

        views = []
        for views_item_data in self.views:
            views_item = views_item_data.to_dict()
            views.append(views_item)

        groups = []
        for groups_item_data in self.groups:
            groups_item = groups_item_data.to_dict()
            groups.append(groups_item)

        lists = []
        for lists_item_data in self.lists:
            lists_item = lists_item_data.to_dict()
            lists.append(lists_item)

        sorts = []
        for sorts_item_data in self.sorts:
            sorts_item = sorts_item_data.to_dict()
            sorts.append(sorts_item)

        create: dict[str, Any] | Unset = UNSET
        if not isinstance(self.create, Unset):
            create = self.create.to_dict()

        ai_configs: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.ai_configs, Unset):
            ai_configs = []
            for ai_configs_item_data in self.ai_configs:
                ai_configs_item = ai_configs_item_data.to_dict()
                ai_configs.append(ai_configs_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "widgets": widgets,
                "views": views,
                "groups": groups,
                "lists": lists,
                "sorts": sorts,
            }
        )
        if create is not UNSET:
            field_dict["create"] = create
        if ai_configs is not UNSET:
            field_dict["aiConfigs"] = ai_configs

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.create import Create
        from ..models.mds_ai_config import MdsAiConfig
        from ..models.mds_group import MdsGroup
        from ..models.mds_list import MdsList
        from ..models.mds_sort import MdsSort
        from ..models.mds_view import MdsView
        from ..models.mds_widget import MdsWidget

        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        widgets = []
        _widgets = d.pop("widgets")
        for widgets_item_data in _widgets:
            widgets_item = MdsWidget.from_dict(widgets_item_data)

            widgets.append(widgets_item)

        views = []
        _views = d.pop("views")
        for views_item_data in _views:
            views_item = MdsView.from_dict(views_item_data)

            views.append(views_item)

        groups = []
        _groups = d.pop("groups")
        for groups_item_data in _groups:
            groups_item = MdsGroup.from_dict(groups_item_data)

            groups.append(groups_item)

        lists = []
        _lists = d.pop("lists")
        for lists_item_data in _lists:
            lists_item = MdsList.from_dict(lists_item_data)

            lists.append(lists_item)

        sorts = []
        _sorts = d.pop("sorts")
        for sorts_item_data in _sorts:
            sorts_item = MdsSort.from_dict(sorts_item_data)

            sorts.append(sorts_item)

        _create = d.pop("create", UNSET)
        create: Create | Unset
        if isinstance(_create, Unset):
            create = UNSET
        else:
            create = Create.from_dict(_create)

        _ai_configs = d.pop("aiConfigs", UNSET)
        ai_configs: list[MdsAiConfig] | Unset = UNSET
        if _ai_configs is not UNSET:
            ai_configs = []
            for ai_configs_item_data in _ai_configs:
                ai_configs_item = MdsAiConfig.from_dict(ai_configs_item_data)

                ai_configs.append(ai_configs_item)

        mds = cls(
            id=id,
            name=name,
            widgets=widgets,
            views=views,
            groups=groups,
            lists=lists,
            sorts=sorts,
            create=create,
            ai_configs=ai_configs,
        )

        mds.additional_properties = d
        return mds

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
