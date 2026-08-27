from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.node import Node


T = TypeVar("T", bound="LTISession")


@_attrs_define
class LTISession:
    """
    Attributes:
        accept_multiple (bool | Unset):
        deeplink_return_url (str | Unset):
        accept_types (list[str] | Unset):
        accept_presentation_document_targets (list[str] | Unset):
        can_confirm (bool | Unset):
        title (str | Unset):
        text (str | Unset):
        custom_content_node (Node | Unset):
    """

    accept_multiple: bool | Unset = UNSET
    deeplink_return_url: str | Unset = UNSET
    accept_types: list[str] | Unset = UNSET
    accept_presentation_document_targets: list[str] | Unset = UNSET
    can_confirm: bool | Unset = UNSET
    title: str | Unset = UNSET
    text: str | Unset = UNSET
    custom_content_node: Node | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        accept_multiple = self.accept_multiple

        deeplink_return_url = self.deeplink_return_url

        accept_types: list[str] | Unset = UNSET
        if not isinstance(self.accept_types, Unset):
            accept_types = self.accept_types

        accept_presentation_document_targets: list[str] | Unset = UNSET
        if not isinstance(self.accept_presentation_document_targets, Unset):
            accept_presentation_document_targets = self.accept_presentation_document_targets

        can_confirm = self.can_confirm

        title = self.title

        text = self.text

        custom_content_node: dict[str, Any] | Unset = UNSET
        if not isinstance(self.custom_content_node, Unset):
            custom_content_node = self.custom_content_node.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if accept_multiple is not UNSET:
            field_dict["acceptMultiple"] = accept_multiple
        if deeplink_return_url is not UNSET:
            field_dict["deeplinkReturnUrl"] = deeplink_return_url
        if accept_types is not UNSET:
            field_dict["acceptTypes"] = accept_types
        if accept_presentation_document_targets is not UNSET:
            field_dict["acceptPresentationDocumentTargets"] = accept_presentation_document_targets
        if can_confirm is not UNSET:
            field_dict["canConfirm"] = can_confirm
        if title is not UNSET:
            field_dict["title"] = title
        if text is not UNSET:
            field_dict["text"] = text
        if custom_content_node is not UNSET:
            field_dict["customContentNode"] = custom_content_node

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.node import Node

        d = dict(src_dict)
        accept_multiple = d.pop("acceptMultiple", UNSET)

        deeplink_return_url = d.pop("deeplinkReturnUrl", UNSET)

        accept_types = cast(list[str], d.pop("acceptTypes", UNSET))

        accept_presentation_document_targets = cast(
            list[str], d.pop("acceptPresentationDocumentTargets", UNSET)
        )

        can_confirm = d.pop("canConfirm", UNSET)

        title = d.pop("title", UNSET)

        text = d.pop("text", UNSET)

        _custom_content_node = d.pop("customContentNode", UNSET)
        custom_content_node: Node | Unset
        if isinstance(_custom_content_node, Unset):
            custom_content_node = UNSET
        else:
            custom_content_node = Node.from_dict(_custom_content_node)

        lti_session = cls(
            accept_multiple=accept_multiple,
            deeplink_return_url=deeplink_return_url,
            accept_types=accept_types,
            accept_presentation_document_targets=accept_presentation_document_targets,
            can_confirm=can_confirm,
            title=title,
            text=text,
            custom_content_node=custom_content_node,
        )

        lti_session.additional_properties = d
        return lti_session

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
