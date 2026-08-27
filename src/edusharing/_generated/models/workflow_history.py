from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.authority import Authority
    from ..models.user_simple import UserSimple


T = TypeVar("T", bound="WorkflowHistory")


@_attrs_define
class WorkflowHistory:
    """
    Attributes:
        time (int | Unset):
        editor (UserSimple | Unset):
        receiver (list[Authority] | Unset):
        status (str | Unset):
        comment (str | Unset):
    """

    time: int | Unset = UNSET
    editor: UserSimple | Unset = UNSET
    receiver: list[Authority] | Unset = UNSET
    status: str | Unset = UNSET
    comment: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        time = self.time

        editor: dict[str, Any] | Unset = UNSET
        if not isinstance(self.editor, Unset):
            editor = self.editor.to_dict()

        receiver: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.receiver, Unset):
            receiver = []
            for receiver_item_data in self.receiver:
                receiver_item = receiver_item_data.to_dict()
                receiver.append(receiver_item)

        status = self.status

        comment = self.comment

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if time is not UNSET:
            field_dict["time"] = time
        if editor is not UNSET:
            field_dict["editor"] = editor
        if receiver is not UNSET:
            field_dict["receiver"] = receiver
        if status is not UNSET:
            field_dict["status"] = status
        if comment is not UNSET:
            field_dict["comment"] = comment

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.authority import Authority
        from ..models.user_simple import UserSimple

        d = dict(src_dict)
        time = d.pop("time", UNSET)

        _editor = d.pop("editor", UNSET)
        editor: UserSimple | Unset
        if isinstance(_editor, Unset):
            editor = UNSET
        else:
            editor = UserSimple.from_dict(_editor)

        _receiver = d.pop("receiver", UNSET)
        receiver: list[Authority] | Unset = UNSET
        if _receiver is not UNSET:
            receiver = []
            for receiver_item_data in _receiver:
                receiver_item = Authority.from_dict(receiver_item_data)

                receiver.append(receiver_item)

        status = d.pop("status", UNSET)

        comment = d.pop("comment", UNSET)

        workflow_history = cls(
            time=time,
            editor=editor,
            receiver=receiver,
            status=status,
            comment=comment,
        )

        workflow_history.additional_properties = d
        return workflow_history

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
