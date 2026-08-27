from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.node_ref import NodeRef
    from ..models.user_simple import UserSimple


T = TypeVar("T", bound="Comment")


@_attrs_define
class Comment:
    """
    Attributes:
        ref (NodeRef | Unset):
        reply_to (NodeRef | Unset):
        creator (UserSimple | Unset):
        created (int | Unset):
        comment (str | Unset):
    """

    ref: NodeRef | Unset = UNSET
    reply_to: NodeRef | Unset = UNSET
    creator: UserSimple | Unset = UNSET
    created: int | Unset = UNSET
    comment: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ref: dict[str, Any] | Unset = UNSET
        if not isinstance(self.ref, Unset):
            ref = self.ref.to_dict()

        reply_to: dict[str, Any] | Unset = UNSET
        if not isinstance(self.reply_to, Unset):
            reply_to = self.reply_to.to_dict()

        creator: dict[str, Any] | Unset = UNSET
        if not isinstance(self.creator, Unset):
            creator = self.creator.to_dict()

        created = self.created

        comment = self.comment

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if ref is not UNSET:
            field_dict["ref"] = ref
        if reply_to is not UNSET:
            field_dict["replyTo"] = reply_to
        if creator is not UNSET:
            field_dict["creator"] = creator
        if created is not UNSET:
            field_dict["created"] = created
        if comment is not UNSET:
            field_dict["comment"] = comment

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.node_ref import NodeRef
        from ..models.user_simple import UserSimple

        d = dict(src_dict)
        _ref = d.pop("ref", UNSET)
        ref: NodeRef | Unset
        if isinstance(_ref, Unset):
            ref = UNSET
        else:
            ref = NodeRef.from_dict(_ref)

        _reply_to = d.pop("replyTo", UNSET)
        reply_to: NodeRef | Unset
        if isinstance(_reply_to, Unset):
            reply_to = UNSET
        else:
            reply_to = NodeRef.from_dict(_reply_to)

        _creator = d.pop("creator", UNSET)
        creator: UserSimple | Unset
        if isinstance(_creator, Unset):
            creator = UNSET
        else:
            creator = UserSimple.from_dict(_creator)

        created = d.pop("created", UNSET)

        comment = d.pop("comment", UNSET)

        comment = cls(
            ref=ref,
            reply_to=reply_to,
            creator=creator,
            created=created,
            comment=comment,
        )

        comment.additional_properties = d
        return comment

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
