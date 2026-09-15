"""Place existing material without confusing reference and original identities."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..errors import EduSharingError, ValidationError

if TYPE_CHECKING:
    from ..repository import AsyncRepository


async def place_material(
    repo: AsyncRepository, node_id: str, collection_id: str, *,
    publish: bool = False, remove_from: str | None = None,
) -> dict[str, Any]:
    """Place an original or reference; optionally publish and move its placement.

    Uses the reference id from the write response, without waiting for the
    membership index. On an existing placement (409) that id may be unknown.
    Failures after reading the node are reported under ``failed`` with their
    step. The old placement is removed only after the new placement and any
    requested publication succeed. Removal uses the original id, as required
    by the collection REST API. There is no cross-endpoint transaction.
    """
    if remove_from == collection_id:
        raise ValidationError("Source and destination collections must differ.")
    node = await repo.nodes.get(node_id)
    original_id = node.original_id or node.id
    answer: dict[str, Any] = {
        "input_id": node_id, "original_id": original_id,
        "collection_id": collection_id, "reference_id": None,
        "created": False, "placed": False, "public": None,
        "removed_from": None, "failed": [],
    }
    try:
        placement = await repo.collections.add_reference(collection_id, original_id)
    except EduSharingError as exc:
        answer["failed"].append({"step": "place", "reason": str(exc)})
        return answer
    answer.update(placement, placed=True)
    if publish:
        try:
            original = node if original_id == node.id else await repo.nodes.get(original_id)
            await original.permissions.publish()
            answer["public"] = True
        except EduSharingError as exc:
            answer["failed"].append({"step": "publish", "reason": str(exc)})
            return answer
    if remove_from:
        try:
            await repo.collections.remove(remove_from, original_id)
            answer["removed_from"] = remove_from
        except EduSharingError as exc:
            answer["failed"].append({"step": "remove", "reason": str(exc)})
    return answer
