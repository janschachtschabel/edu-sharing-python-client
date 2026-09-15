from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.notification_intervals_add_to_collection_event import (
    NotificationIntervalsAddToCollectionEvent,
)
from ..models.notification_intervals_added_to_inbox_event import (
    NotificationIntervalsAddedToInboxEvent,
)
from ..models.notification_intervals_comment_event import NotificationIntervalsCommentEvent
from ..models.notification_intervals_invite_event import NotificationIntervalsInviteEvent
from ..models.notification_intervals_metadata_suggestion_event import (
    NotificationIntervalsMetadataSuggestionEvent,
)
from ..models.notification_intervals_node_issue_event import NotificationIntervalsNodeIssueEvent
from ..models.notification_intervals_propose_for_collection_event import (
    NotificationIntervalsProposeForCollectionEvent,
)
from ..models.notification_intervals_rating_event import NotificationIntervalsRatingEvent
from ..models.notification_intervals_workflow_event import NotificationIntervalsWorkflowEvent
from ..types import UNSET, Unset

T = TypeVar("T", bound="NotificationIntervals")


@_attrs_define
class NotificationIntervals:
    """
    Attributes:
        added_to_inbox_event (NotificationIntervalsAddedToInboxEvent | Unset):
        add_to_collection_event (NotificationIntervalsAddToCollectionEvent | Unset):
        propose_for_collection_event (NotificationIntervalsProposeForCollectionEvent | Unset):
        comment_event (NotificationIntervalsCommentEvent | Unset):
        invite_event (NotificationIntervalsInviteEvent | Unset):
        node_issue_event (NotificationIntervalsNodeIssueEvent | Unset):
        rating_event (NotificationIntervalsRatingEvent | Unset):
        workflow_event (NotificationIntervalsWorkflowEvent | Unset):
        metadata_suggestion_event (NotificationIntervalsMetadataSuggestionEvent | Unset):
    """

    added_to_inbox_event: NotificationIntervalsAddedToInboxEvent | Unset = UNSET
    add_to_collection_event: NotificationIntervalsAddToCollectionEvent | Unset = UNSET
    propose_for_collection_event: NotificationIntervalsProposeForCollectionEvent | Unset = UNSET
    comment_event: NotificationIntervalsCommentEvent | Unset = UNSET
    invite_event: NotificationIntervalsInviteEvent | Unset = UNSET
    node_issue_event: NotificationIntervalsNodeIssueEvent | Unset = UNSET
    rating_event: NotificationIntervalsRatingEvent | Unset = UNSET
    workflow_event: NotificationIntervalsWorkflowEvent | Unset = UNSET
    metadata_suggestion_event: NotificationIntervalsMetadataSuggestionEvent | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        added_to_inbox_event: str | Unset = UNSET
        if not isinstance(self.added_to_inbox_event, Unset):
            added_to_inbox_event = self.added_to_inbox_event.value

        add_to_collection_event: str | Unset = UNSET
        if not isinstance(self.add_to_collection_event, Unset):
            add_to_collection_event = self.add_to_collection_event.value

        propose_for_collection_event: str | Unset = UNSET
        if not isinstance(self.propose_for_collection_event, Unset):
            propose_for_collection_event = self.propose_for_collection_event.value

        comment_event: str | Unset = UNSET
        if not isinstance(self.comment_event, Unset):
            comment_event = self.comment_event.value

        invite_event: str | Unset = UNSET
        if not isinstance(self.invite_event, Unset):
            invite_event = self.invite_event.value

        node_issue_event: str | Unset = UNSET
        if not isinstance(self.node_issue_event, Unset):
            node_issue_event = self.node_issue_event.value

        rating_event: str | Unset = UNSET
        if not isinstance(self.rating_event, Unset):
            rating_event = self.rating_event.value

        workflow_event: str | Unset = UNSET
        if not isinstance(self.workflow_event, Unset):
            workflow_event = self.workflow_event.value

        metadata_suggestion_event: str | Unset = UNSET
        if not isinstance(self.metadata_suggestion_event, Unset):
            metadata_suggestion_event = self.metadata_suggestion_event.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if added_to_inbox_event is not UNSET:
            field_dict["addedToInboxEvent"] = added_to_inbox_event
        if add_to_collection_event is not UNSET:
            field_dict["addToCollectionEvent"] = add_to_collection_event
        if propose_for_collection_event is not UNSET:
            field_dict["proposeForCollectionEvent"] = propose_for_collection_event
        if comment_event is not UNSET:
            field_dict["commentEvent"] = comment_event
        if invite_event is not UNSET:
            field_dict["inviteEvent"] = invite_event
        if node_issue_event is not UNSET:
            field_dict["nodeIssueEvent"] = node_issue_event
        if rating_event is not UNSET:
            field_dict["ratingEvent"] = rating_event
        if workflow_event is not UNSET:
            field_dict["workflowEvent"] = workflow_event
        if metadata_suggestion_event is not UNSET:
            field_dict["metadataSuggestionEvent"] = metadata_suggestion_event

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        _added_to_inbox_event = d.pop("addedToInboxEvent", UNSET)
        added_to_inbox_event: NotificationIntervalsAddedToInboxEvent | Unset
        if isinstance(_added_to_inbox_event, Unset):
            added_to_inbox_event = UNSET
        else:
            added_to_inbox_event = NotificationIntervalsAddedToInboxEvent(_added_to_inbox_event)

        _add_to_collection_event = d.pop("addToCollectionEvent", UNSET)
        add_to_collection_event: NotificationIntervalsAddToCollectionEvent | Unset
        if isinstance(_add_to_collection_event, Unset):
            add_to_collection_event = UNSET
        else:
            add_to_collection_event = NotificationIntervalsAddToCollectionEvent(
                _add_to_collection_event
            )

        _propose_for_collection_event = d.pop("proposeForCollectionEvent", UNSET)
        propose_for_collection_event: NotificationIntervalsProposeForCollectionEvent | Unset
        if isinstance(_propose_for_collection_event, Unset):
            propose_for_collection_event = UNSET
        else:
            propose_for_collection_event = NotificationIntervalsProposeForCollectionEvent(
                _propose_for_collection_event
            )

        _comment_event = d.pop("commentEvent", UNSET)
        comment_event: NotificationIntervalsCommentEvent | Unset
        if isinstance(_comment_event, Unset):
            comment_event = UNSET
        else:
            comment_event = NotificationIntervalsCommentEvent(_comment_event)

        _invite_event = d.pop("inviteEvent", UNSET)
        invite_event: NotificationIntervalsInviteEvent | Unset
        if isinstance(_invite_event, Unset):
            invite_event = UNSET
        else:
            invite_event = NotificationIntervalsInviteEvent(_invite_event)

        _node_issue_event = d.pop("nodeIssueEvent", UNSET)
        node_issue_event: NotificationIntervalsNodeIssueEvent | Unset
        if isinstance(_node_issue_event, Unset):
            node_issue_event = UNSET
        else:
            node_issue_event = NotificationIntervalsNodeIssueEvent(_node_issue_event)

        _rating_event = d.pop("ratingEvent", UNSET)
        rating_event: NotificationIntervalsRatingEvent | Unset
        if isinstance(_rating_event, Unset):
            rating_event = UNSET
        else:
            rating_event = NotificationIntervalsRatingEvent(_rating_event)

        _workflow_event = d.pop("workflowEvent", UNSET)
        workflow_event: NotificationIntervalsWorkflowEvent | Unset
        if isinstance(_workflow_event, Unset):
            workflow_event = UNSET
        else:
            workflow_event = NotificationIntervalsWorkflowEvent(_workflow_event)

        _metadata_suggestion_event = d.pop("metadataSuggestionEvent", UNSET)
        metadata_suggestion_event: NotificationIntervalsMetadataSuggestionEvent | Unset
        if isinstance(_metadata_suggestion_event, Unset):
            metadata_suggestion_event = UNSET
        else:
            metadata_suggestion_event = NotificationIntervalsMetadataSuggestionEvent(
                _metadata_suggestion_event
            )

        notification_intervals = cls(
            added_to_inbox_event=added_to_inbox_event,
            add_to_collection_event=add_to_collection_event,
            propose_for_collection_event=propose_for_collection_event,
            comment_event=comment_event,
            invite_event=invite_event,
            node_issue_event=node_issue_event,
            rating_event=rating_event,
            workflow_event=workflow_event,
            metadata_suggestion_event=metadata_suggestion_event,
        )

        notification_intervals.additional_properties = d
        return notification_intervals

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
