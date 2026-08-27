from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.mds_widget_expandable import MdsWidgetExpandable
from ..models.mds_widget_filter_mode import MdsWidgetFilterMode
from ..models.mds_widget_input_preprocessor_item import MdsWidgetInputPreprocessorItem
from ..models.mds_widget_interaction_type import MdsWidgetInteractionType
from ..models.mds_widget_is_required import MdsWidgetIsRequired
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.mds_ai_config import MdsAiConfig
    from ..models.mds_index import MdsIndex
    from ..models.mds_subwidget import MdsSubwidget
    from ..models.mds_value import MdsValue
    from ..models.mds_widget_condition import MdsWidgetCondition
    from ..models.mds_widget_ids import MdsWidgetIds


T = TypeVar("T", bound="MdsWidget")


@_attrs_define
class MdsWidget:
    """
    Attributes:
        ids (MdsWidgetIds | Unset):
        id (str | Unset):
        caption (str | Unset):
        bottom_caption (str | Unset):
        icon (str | Unset):
        type_ (str | Unset):
        link (str | Unset):
        template (list[str] | Unset):
        configuration (str | Unset):
        has_values (bool | Unset):
        values (list[MdsValue] | Unset):
        subwidgets (list[MdsSubwidget] | Unset):
        placeholder (str | Unset):
        unit (str | Unset):
        format_ (str | Unset):
        min_ (int | Unset):
        max_ (int | Unset):
        default_min (int | Unset):
        default_max (int | Unset):
        step (int | Unset):
        suggestion_source (str | Unset):
        allow_valuespace_suggestions (bool | Unset):
        hide_if_empty (bool | Unset):
        allowempty (bool | Unset):
        defaultvalue (str | Unset):
        count_defaultvalue_as_filter (bool | Unset): When true, a set defaultvalue will still trigger the search to show
            an active filter. When false (default), the defaultvalue will be shown as if no filter is active
        condition (MdsWidgetCondition | Unset):
        maxlength (int | Unset):
        interaction_type (MdsWidgetInteractionType | Unset):
        filter_mode (MdsWidgetFilterMode | Unset):
        expandable (MdsWidgetExpandable | Unset):
        input_preprocessor (list[MdsWidgetInputPreprocessorItem] | Unset):
        ai_configs (list[MdsAiConfig] | Unset):
        index (MdsIndex | Unset):
        is_extended (bool | Unset):
        is_required (MdsWidgetIsRequired | Unset):
        is_searchable (bool | Unset):
    """

    ids: MdsWidgetIds | Unset = UNSET
    id: str | Unset = UNSET
    caption: str | Unset = UNSET
    bottom_caption: str | Unset = UNSET
    icon: str | Unset = UNSET
    type_: str | Unset = UNSET
    link: str | Unset = UNSET
    template: list[str] | Unset = UNSET
    configuration: str | Unset = UNSET
    has_values: bool | Unset = UNSET
    values: list[MdsValue] | Unset = UNSET
    subwidgets: list[MdsSubwidget] | Unset = UNSET
    placeholder: str | Unset = UNSET
    unit: str | Unset = UNSET
    format_: str | Unset = UNSET
    min_: int | Unset = UNSET
    max_: int | Unset = UNSET
    default_min: int | Unset = UNSET
    default_max: int | Unset = UNSET
    step: int | Unset = UNSET
    suggestion_source: str | Unset = UNSET
    allow_valuespace_suggestions: bool | Unset = UNSET
    hide_if_empty: bool | Unset = UNSET
    allowempty: bool | Unset = UNSET
    defaultvalue: str | Unset = UNSET
    count_defaultvalue_as_filter: bool | Unset = UNSET
    condition: MdsWidgetCondition | Unset = UNSET
    maxlength: int | Unset = UNSET
    interaction_type: MdsWidgetInteractionType | Unset = UNSET
    filter_mode: MdsWidgetFilterMode | Unset = UNSET
    expandable: MdsWidgetExpandable | Unset = UNSET
    input_preprocessor: list[MdsWidgetInputPreprocessorItem] | Unset = UNSET
    ai_configs: list[MdsAiConfig] | Unset = UNSET
    index: MdsIndex | Unset = UNSET
    is_extended: bool | Unset = UNSET
    is_required: MdsWidgetIsRequired | Unset = UNSET
    is_searchable: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ids: dict[str, Any] | Unset = UNSET
        if not isinstance(self.ids, Unset):
            ids = self.ids.to_dict()

        id = self.id

        caption = self.caption

        bottom_caption = self.bottom_caption

        icon = self.icon

        type_ = self.type_

        link = self.link

        template: list[str] | Unset = UNSET
        if not isinstance(self.template, Unset):
            template = self.template

        configuration = self.configuration

        has_values = self.has_values

        values: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.values, Unset):
            values = []
            for values_item_data in self.values:
                values_item = values_item_data.to_dict()
                values.append(values_item)

        subwidgets: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.subwidgets, Unset):
            subwidgets = []
            for subwidgets_item_data in self.subwidgets:
                subwidgets_item = subwidgets_item_data.to_dict()
                subwidgets.append(subwidgets_item)

        placeholder = self.placeholder

        unit = self.unit

        format_ = self.format_

        min_ = self.min_

        max_ = self.max_

        default_min = self.default_min

        default_max = self.default_max

        step = self.step

        suggestion_source = self.suggestion_source

        allow_valuespace_suggestions = self.allow_valuespace_suggestions

        hide_if_empty = self.hide_if_empty

        allowempty = self.allowempty

        defaultvalue = self.defaultvalue

        count_defaultvalue_as_filter = self.count_defaultvalue_as_filter

        condition: dict[str, Any] | Unset = UNSET
        if not isinstance(self.condition, Unset):
            condition = self.condition.to_dict()

        maxlength = self.maxlength

        interaction_type: str | Unset = UNSET
        if not isinstance(self.interaction_type, Unset):
            interaction_type = self.interaction_type.value

        filter_mode: str | Unset = UNSET
        if not isinstance(self.filter_mode, Unset):
            filter_mode = self.filter_mode.value

        expandable: str | Unset = UNSET
        if not isinstance(self.expandable, Unset):
            expandable = self.expandable.value

        input_preprocessor: list[str] | Unset = UNSET
        if not isinstance(self.input_preprocessor, Unset):
            input_preprocessor = []
            for input_preprocessor_item_data in self.input_preprocessor:
                input_preprocessor_item = input_preprocessor_item_data.value
                input_preprocessor.append(input_preprocessor_item)

        ai_configs: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.ai_configs, Unset):
            ai_configs = []
            for ai_configs_item_data in self.ai_configs:
                ai_configs_item = ai_configs_item_data.to_dict()
                ai_configs.append(ai_configs_item)

        index: dict[str, Any] | Unset = UNSET
        if not isinstance(self.index, Unset):
            index = self.index.to_dict()

        is_extended = self.is_extended

        is_required: str | Unset = UNSET
        if not isinstance(self.is_required, Unset):
            is_required = self.is_required.value

        is_searchable = self.is_searchable

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if ids is not UNSET:
            field_dict["ids"] = ids
        if id is not UNSET:
            field_dict["id"] = id
        if caption is not UNSET:
            field_dict["caption"] = caption
        if bottom_caption is not UNSET:
            field_dict["bottomCaption"] = bottom_caption
        if icon is not UNSET:
            field_dict["icon"] = icon
        if type_ is not UNSET:
            field_dict["type"] = type_
        if link is not UNSET:
            field_dict["link"] = link
        if template is not UNSET:
            field_dict["template"] = template
        if configuration is not UNSET:
            field_dict["configuration"] = configuration
        if has_values is not UNSET:
            field_dict["hasValues"] = has_values
        if values is not UNSET:
            field_dict["values"] = values
        if subwidgets is not UNSET:
            field_dict["subwidgets"] = subwidgets
        if placeholder is not UNSET:
            field_dict["placeholder"] = placeholder
        if unit is not UNSET:
            field_dict["unit"] = unit
        if format_ is not UNSET:
            field_dict["format"] = format_
        if min_ is not UNSET:
            field_dict["min"] = min_
        if max_ is not UNSET:
            field_dict["max"] = max_
        if default_min is not UNSET:
            field_dict["defaultMin"] = default_min
        if default_max is not UNSET:
            field_dict["defaultMax"] = default_max
        if step is not UNSET:
            field_dict["step"] = step
        if suggestion_source is not UNSET:
            field_dict["suggestionSource"] = suggestion_source
        if allow_valuespace_suggestions is not UNSET:
            field_dict["allowValuespaceSuggestions"] = allow_valuespace_suggestions
        if hide_if_empty is not UNSET:
            field_dict["hideIfEmpty"] = hide_if_empty
        if allowempty is not UNSET:
            field_dict["allowempty"] = allowempty
        if defaultvalue is not UNSET:
            field_dict["defaultvalue"] = defaultvalue
        if count_defaultvalue_as_filter is not UNSET:
            field_dict["countDefaultvalueAsFilter"] = count_defaultvalue_as_filter
        if condition is not UNSET:
            field_dict["condition"] = condition
        if maxlength is not UNSET:
            field_dict["maxlength"] = maxlength
        if interaction_type is not UNSET:
            field_dict["interactionType"] = interaction_type
        if filter_mode is not UNSET:
            field_dict["filterMode"] = filter_mode
        if expandable is not UNSET:
            field_dict["expandable"] = expandable
        if input_preprocessor is not UNSET:
            field_dict["inputPreprocessor"] = input_preprocessor
        if ai_configs is not UNSET:
            field_dict["aiConfigs"] = ai_configs
        if index is not UNSET:
            field_dict["index"] = index
        if is_extended is not UNSET:
            field_dict["isExtended"] = is_extended
        if is_required is not UNSET:
            field_dict["isRequired"] = is_required
        if is_searchable is not UNSET:
            field_dict["isSearchable"] = is_searchable

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.mds_ai_config import MdsAiConfig
        from ..models.mds_index import MdsIndex
        from ..models.mds_subwidget import MdsSubwidget
        from ..models.mds_value import MdsValue
        from ..models.mds_widget_condition import MdsWidgetCondition
        from ..models.mds_widget_ids import MdsWidgetIds

        d = dict(src_dict)
        _ids = d.pop("ids", UNSET)
        ids: MdsWidgetIds | Unset
        if isinstance(_ids, Unset):
            ids = UNSET
        else:
            ids = MdsWidgetIds.from_dict(_ids)

        id = d.pop("id", UNSET)

        caption = d.pop("caption", UNSET)

        bottom_caption = d.pop("bottomCaption", UNSET)

        icon = d.pop("icon", UNSET)

        type_ = d.pop("type", UNSET)

        link = d.pop("link", UNSET)

        template = cast(list[str], d.pop("template", UNSET))

        configuration = d.pop("configuration", UNSET)

        has_values = d.pop("hasValues", UNSET)

        _values = d.pop("values", UNSET)
        values: list[MdsValue] | Unset = UNSET
        if _values is not UNSET:
            values = []
            for values_item_data in _values:
                values_item = MdsValue.from_dict(values_item_data)

                values.append(values_item)

        _subwidgets = d.pop("subwidgets", UNSET)
        subwidgets: list[MdsSubwidget] | Unset = UNSET
        if _subwidgets is not UNSET:
            subwidgets = []
            for subwidgets_item_data in _subwidgets:
                subwidgets_item = MdsSubwidget.from_dict(subwidgets_item_data)

                subwidgets.append(subwidgets_item)

        placeholder = d.pop("placeholder", UNSET)

        unit = d.pop("unit", UNSET)

        format_ = d.pop("format", UNSET)

        min_ = d.pop("min", UNSET)

        max_ = d.pop("max", UNSET)

        default_min = d.pop("defaultMin", UNSET)

        default_max = d.pop("defaultMax", UNSET)

        step = d.pop("step", UNSET)

        suggestion_source = d.pop("suggestionSource", UNSET)

        allow_valuespace_suggestions = d.pop("allowValuespaceSuggestions", UNSET)

        hide_if_empty = d.pop("hideIfEmpty", UNSET)

        allowempty = d.pop("allowempty", UNSET)

        defaultvalue = d.pop("defaultvalue", UNSET)

        count_defaultvalue_as_filter = d.pop("countDefaultvalueAsFilter", UNSET)

        _condition = d.pop("condition", UNSET)
        condition: MdsWidgetCondition | Unset
        if isinstance(_condition, Unset):
            condition = UNSET
        else:
            condition = MdsWidgetCondition.from_dict(_condition)

        maxlength = d.pop("maxlength", UNSET)

        _interaction_type = d.pop("interactionType", UNSET)
        interaction_type: MdsWidgetInteractionType | Unset
        if isinstance(_interaction_type, Unset):
            interaction_type = UNSET
        else:
            interaction_type = MdsWidgetInteractionType(_interaction_type)

        _filter_mode = d.pop("filterMode", UNSET)
        filter_mode: MdsWidgetFilterMode | Unset
        if isinstance(_filter_mode, Unset):
            filter_mode = UNSET
        else:
            filter_mode = MdsWidgetFilterMode(_filter_mode)

        _expandable = d.pop("expandable", UNSET)
        expandable: MdsWidgetExpandable | Unset
        if isinstance(_expandable, Unset):
            expandable = UNSET
        else:
            expandable = MdsWidgetExpandable(_expandable)

        _input_preprocessor = d.pop("inputPreprocessor", UNSET)
        input_preprocessor: list[MdsWidgetInputPreprocessorItem] | Unset = UNSET
        if _input_preprocessor is not UNSET:
            input_preprocessor = []
            for input_preprocessor_item_data in _input_preprocessor:
                input_preprocessor_item = MdsWidgetInputPreprocessorItem(
                    input_preprocessor_item_data
                )

                input_preprocessor.append(input_preprocessor_item)

        _ai_configs = d.pop("aiConfigs", UNSET)
        ai_configs: list[MdsAiConfig] | Unset = UNSET
        if _ai_configs is not UNSET:
            ai_configs = []
            for ai_configs_item_data in _ai_configs:
                ai_configs_item = MdsAiConfig.from_dict(ai_configs_item_data)

                ai_configs.append(ai_configs_item)

        _index = d.pop("index", UNSET)
        index: MdsIndex | Unset
        if isinstance(_index, Unset):
            index = UNSET
        else:
            index = MdsIndex.from_dict(_index)

        is_extended = d.pop("isExtended", UNSET)

        _is_required = d.pop("isRequired", UNSET)
        is_required: MdsWidgetIsRequired | Unset
        if isinstance(_is_required, Unset):
            is_required = UNSET
        else:
            is_required = MdsWidgetIsRequired(_is_required)

        is_searchable = d.pop("isSearchable", UNSET)

        mds_widget = cls(
            ids=ids,
            id=id,
            caption=caption,
            bottom_caption=bottom_caption,
            icon=icon,
            type_=type_,
            link=link,
            template=template,
            configuration=configuration,
            has_values=has_values,
            values=values,
            subwidgets=subwidgets,
            placeholder=placeholder,
            unit=unit,
            format_=format_,
            min_=min_,
            max_=max_,
            default_min=default_min,
            default_max=default_max,
            step=step,
            suggestion_source=suggestion_source,
            allow_valuespace_suggestions=allow_valuespace_suggestions,
            hide_if_empty=hide_if_empty,
            allowempty=allowempty,
            defaultvalue=defaultvalue,
            count_defaultvalue_as_filter=count_defaultvalue_as_filter,
            condition=condition,
            maxlength=maxlength,
            interaction_type=interaction_type,
            filter_mode=filter_mode,
            expandable=expandable,
            input_preprocessor=input_preprocessor,
            ai_configs=ai_configs,
            index=index,
            is_extended=is_extended,
            is_required=is_required,
            is_searchable=is_searchable,
        )

        mds_widget.additional_properties = d
        return mds_widget

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
