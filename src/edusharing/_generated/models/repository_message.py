from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.repository_message_mode import RepositoryMessageMode
from ..models.repository_message_repeat import RepositoryMessageRepeat
from ..models.repository_message_severity import RepositoryMessageSeverity
from ..models.repository_message_user_mode import RepositoryMessageUserMode
from ..types import UNSET, Unset

T = TypeVar("T", bound="RepositoryMessage")


@_attrs_define
class RepositoryMessage:
    """
    Attributes:
        uuid (UUID): uuid of message
        contexts (list[str] | Unset):
        toolpermissions (list[str] | Unset):
        components (list[str] | Unset):
        user_mode (RepositoryMessageUserMode | Unset):
        mode (RepositoryMessageMode | Unset):
        repeat (RepositoryMessageRepeat | Unset):
        severity (RepositoryMessageSeverity | Unset):
        from_ (int | Unset): optional start date for message
        to (int | Unset): optional end date for message
        message (str | Unset): Message to display
    """

    uuid: UUID
    contexts: list[str] | Unset = UNSET
    toolpermissions: list[str] | Unset = UNSET
    components: list[str] | Unset = UNSET
    user_mode: RepositoryMessageUserMode | Unset = UNSET
    mode: RepositoryMessageMode | Unset = UNSET
    repeat: RepositoryMessageRepeat | Unset = UNSET
    severity: RepositoryMessageSeverity | Unset = UNSET
    from_: int | Unset = UNSET
    to: int | Unset = UNSET
    message: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        uuid = str(self.uuid)

        contexts: list[str] | Unset = UNSET
        if not isinstance(self.contexts, Unset):
            contexts = self.contexts

        toolpermissions: list[str] | Unset = UNSET
        if not isinstance(self.toolpermissions, Unset):
            toolpermissions = self.toolpermissions

        components: list[str] | Unset = UNSET
        if not isinstance(self.components, Unset):
            components = self.components

        user_mode: str | Unset = UNSET
        if not isinstance(self.user_mode, Unset):
            user_mode = self.user_mode.value

        mode: str | Unset = UNSET
        if not isinstance(self.mode, Unset):
            mode = self.mode.value

        repeat: str | Unset = UNSET
        if not isinstance(self.repeat, Unset):
            repeat = self.repeat.value

        severity: str | Unset = UNSET
        if not isinstance(self.severity, Unset):
            severity = self.severity.value

        from_ = self.from_

        to = self.to

        message = self.message

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "uuid": uuid,
            }
        )
        if contexts is not UNSET:
            field_dict["contexts"] = contexts
        if toolpermissions is not UNSET:
            field_dict["toolpermissions"] = toolpermissions
        if components is not UNSET:
            field_dict["components"] = components
        if user_mode is not UNSET:
            field_dict["userMode"] = user_mode
        if mode is not UNSET:
            field_dict["mode"] = mode
        if repeat is not UNSET:
            field_dict["repeat"] = repeat
        if severity is not UNSET:
            field_dict["severity"] = severity
        if from_ is not UNSET:
            field_dict["from"] = from_
        if to is not UNSET:
            field_dict["to"] = to
        if message is not UNSET:
            field_dict["message"] = message

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        uuid = UUID(d.pop("uuid"))

        contexts = cast(list[str], d.pop("contexts", UNSET))

        toolpermissions = cast(list[str], d.pop("toolpermissions", UNSET))

        components = cast(list[str], d.pop("components", UNSET))

        _user_mode = d.pop("userMode", UNSET)
        user_mode: RepositoryMessageUserMode | Unset
        if isinstance(_user_mode, Unset):
            user_mode = UNSET
        else:
            user_mode = RepositoryMessageUserMode(_user_mode)

        _mode = d.pop("mode", UNSET)
        mode: RepositoryMessageMode | Unset
        if isinstance(_mode, Unset):
            mode = UNSET
        else:
            mode = RepositoryMessageMode(_mode)

        _repeat = d.pop("repeat", UNSET)
        repeat: RepositoryMessageRepeat | Unset
        if isinstance(_repeat, Unset):
            repeat = UNSET
        else:
            repeat = RepositoryMessageRepeat(_repeat)

        _severity = d.pop("severity", UNSET)
        severity: RepositoryMessageSeverity | Unset
        if isinstance(_severity, Unset):
            severity = UNSET
        else:
            severity = RepositoryMessageSeverity(_severity)

        from_ = d.pop("from", UNSET)

        to = d.pop("to", UNSET)

        message = d.pop("message", UNSET)

        repository_message = cls(
            uuid=uuid,
            contexts=contexts,
            toolpermissions=toolpermissions,
            components=components,
            user_mode=user_mode,
            mode=mode,
            repeat=repeat,
            severity=severity,
            from_=from_,
            to=to,
            message=message,
        )

        repository_message.additional_properties = d
        return repository_message

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
