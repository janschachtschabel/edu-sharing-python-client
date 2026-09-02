"""``accept_suggestion`` -- apply a proposal, read it back, and only then mark it.

Measured on 2026-08-28: ``PATCH ?status=ACCEPTED`` writes **nothing** into the
node. A proposal marked accepted leaves the property exactly as it was, so
"accepted" on its own is a record of something that never happened. The order
here is the one the MCP settled on for ``wlo_decide_suggestion``: write the
value, read it back, and mark the proposal only when the value is there. When
it is not, the proposal stays open and ``failed`` says why -- an accepted
proposal without effect is the state this flow exists to prevent.

Declining needs no flow: ``node.suggestions.decide(ids, accept=False)`` touches
nothing but the proposal, which is exactly what declining means.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..errors import EduSharingError, NotFoundError
from ..nodes_write import KEYWORD_PROPERTY

if TYPE_CHECKING:  # pragma: no cover
    from ..repository import AsyncRepository

__all__ = ["accept_suggestion"]


async def accept_suggestion(
    repo: AsyncRepository, node_id: str, suggestion_id: str
) -> dict[str, Any]:
    """Accept one proposal: write its value, verify, then mark it accepted.

    The value is written with ``set_property`` -- past the metadata set's
    filtering, because a proposal may name a property the set does not list,
    and with the read-back every write in this library has. One exception:
    a proposal for the shared keyword list is **added** with
    ``add_keywords``, never written over it -- replacing the list would
    delete every other keyword, silently. For any other property the
    values that were there before come back as ``replaced``.

    Args:
        repo: the connection.
        node_id: the node the proposal belongs to.
        suggestion_id: the proposal, from ``node.suggestions.list()``.

    Returns:
        ``{id, suggestion_id, property, value, applied, status, failed,
        replaced}``. ``applied`` is ``True`` only when the value was read back
        and the proposal is now ``ACCEPTED``. Otherwise ``status`` is what it
        still is and ``failed`` names the part that stopped it: ``status`` for
        a proposal already decided, ``apply`` for a value the repository did
        not keep -- then nothing was marked, and the proposal stays open --
        and ``mark`` when the value IS on the node but the proposal could not
        be marked. ``replaced`` lists the values the proposal displaced.

    Raises:
        NotFoundError: when the node or the proposal does not exist.
        PermissionDeniedError: when the node may not be read.
    """
    node = await repo.nodes.get(node_id)
    proposals = await node.suggestions.list()
    match = next((p for p in proposals if p.id == suggestion_id), None)
    if match is None:
        raise NotFoundError(
            f"No proposal {suggestion_id!r} on node {node_id!r} -- "
            f"{len(proposals)} proposal(s) exist there."
        )
    answer: dict[str, Any] = {
        "id": node_id, "suggestion_id": suggestion_id,
        "property": match.property, "value": match.value,
        "applied": False, "status": match.status, "failed": [], "replaced": [],
    }
    if match.status != "PENDING":
        answer["failed"].append({"part": "status", "reason": f"already {match.status}"})
        return answer
    try:
        if match.property == KEYWORD_PROPERTY:
            # The shared list: a proposal adds a keyword, it does not take
            # the editors' work away.
            await node.add_keywords(match.value)
        else:
            before = node.get_all(match.property)
            await node.set_property(match.property, match.value)
            answer["replaced"] = [v for v in before if v != match.value]
    except EduSharingError as exc:
        # Not marked: the value is not there, and a proposal marked accepted
        # over a value that never arrived is the record this flow refuses to
        # write.
        answer["failed"].append({"part": "apply", "reason": f"{type(exc).__name__}: {exc}"})
        return answer
    try:
        await node.suggestions.decide([suggestion_id], accept=True)
    except EduSharingError as exc:
        # The value is on the node -- that must not get lost with the error.
        answer["failed"].append({
            "part": "mark",
            "reason": f"value written and read back, proposal not marked: "
                      f"{type(exc).__name__}: {exc}",
        })
        return answer
    return {**answer, "applied": True, "status": "ACCEPTED"}
