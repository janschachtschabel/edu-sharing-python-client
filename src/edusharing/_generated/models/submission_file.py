from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.submission_file_validation_status import SubmissionFileValidationStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.assignment_file import AssignmentFile
    from ..models.node import Node
    from ..models.node_ref import NodeRef


T = TypeVar("T", bound="SubmissionFile")


@_attrs_define
class SubmissionFile:
    """
    Attributes:
        ref (NodeRef):
        content (Node):
        correction (Node | Unset):
        assignment_file (AssignmentFile | Unset): object of the original assignment file (if applicable)
        validation_status (SubmissionFileValidationStatus | Unset): only visible by the coordinator of the task
    """

    ref: NodeRef
    content: Node
    correction: Node | Unset = UNSET
    assignment_file: AssignmentFile | Unset = UNSET
    validation_status: SubmissionFileValidationStatus | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ref = self.ref.to_dict()

        content = self.content.to_dict()

        correction: dict[str, Any] | Unset = UNSET
        if not isinstance(self.correction, Unset):
            correction = self.correction.to_dict()

        assignment_file: dict[str, Any] | Unset = UNSET
        if not isinstance(self.assignment_file, Unset):
            assignment_file = self.assignment_file.to_dict()

        validation_status: str | Unset = UNSET
        if not isinstance(self.validation_status, Unset):
            validation_status = self.validation_status.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref": ref,
                "content": content,
            }
        )
        if correction is not UNSET:
            field_dict["correction"] = correction
        if assignment_file is not UNSET:
            field_dict["assignmentFile"] = assignment_file
        if validation_status is not UNSET:
            field_dict["validationStatus"] = validation_status

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.assignment_file import AssignmentFile
        from ..models.node import Node
        from ..models.node_ref import NodeRef

        d = dict(src_dict)
        ref = NodeRef.from_dict(d.pop("ref"))

        content = Node.from_dict(d.pop("content"))

        _correction = d.pop("correction", UNSET)
        correction: Node | Unset
        if isinstance(_correction, Unset):
            correction = UNSET
        else:
            correction = Node.from_dict(_correction)

        _assignment_file = d.pop("assignmentFile", UNSET)
        assignment_file: AssignmentFile | Unset
        if isinstance(_assignment_file, Unset):
            assignment_file = UNSET
        else:
            assignment_file = AssignmentFile.from_dict(_assignment_file)

        _validation_status = d.pop("validationStatus", UNSET)
        validation_status: SubmissionFileValidationStatus | Unset
        if isinstance(_validation_status, Unset):
            validation_status = UNSET
        else:
            validation_status = SubmissionFileValidationStatus(_validation_status)

        submission_file = cls(
            ref=ref,
            content=content,
            correction=correction,
            assignment_file=assignment_file,
            validation_status=validation_status,
        )

        submission_file.additional_properties = d
        return submission_file

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
