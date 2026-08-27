from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.config_workflow_list import ConfigWorkflowList


T = TypeVar("T", bound="ConfigWorkflow")


@_attrs_define
class ConfigWorkflow:
    """Workflow configuration (default receiver, default status, comment required, workflow states)

    Attributes:
        default_receiver (str | Unset): Default group/user pre-filled as responsible party
        default_status (str | Unset): Default target status pre-filled in workflow dialog
        comment_required (bool | Unset): If true (default), comment is required in workflow dialog
        workflows (list[ConfigWorkflowList] | Unset): Workflow status definitions
    """

    default_receiver: str | Unset = UNSET
    default_status: str | Unset = UNSET
    comment_required: bool | Unset = UNSET
    workflows: list[ConfigWorkflowList] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        default_receiver = self.default_receiver

        default_status = self.default_status

        comment_required = self.comment_required

        workflows: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.workflows, Unset):
            workflows = []
            for workflows_item_data in self.workflows:
                workflows_item = workflows_item_data.to_dict()
                workflows.append(workflows_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if default_receiver is not UNSET:
            field_dict["defaultReceiver"] = default_receiver
        if default_status is not UNSET:
            field_dict["defaultStatus"] = default_status
        if comment_required is not UNSET:
            field_dict["commentRequired"] = comment_required
        if workflows is not UNSET:
            field_dict["workflows"] = workflows

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.config_workflow_list import ConfigWorkflowList

        d = dict(src_dict)
        default_receiver = d.pop("defaultReceiver", UNSET)

        default_status = d.pop("defaultStatus", UNSET)

        comment_required = d.pop("commentRequired", UNSET)

        _workflows = d.pop("workflows", UNSET)
        workflows: list[ConfigWorkflowList] | Unset = UNSET
        if _workflows is not UNSET:
            workflows = []
            for workflows_item_data in _workflows:
                workflows_item = ConfigWorkflowList.from_dict(workflows_item_data)

                workflows.append(workflows_item)

        config_workflow = cls(
            default_receiver=default_receiver,
            default_status=default_status,
            comment_required=comment_required,
            workflows=workflows,
        )

        config_workflow.additional_properties = d
        return config_workflow

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
