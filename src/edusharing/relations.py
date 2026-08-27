"""Links between nodes that sit side by side.

edu-sharing keeps a separate API for these (``/relation/v1``), and it is what
models a series: the parts point at the series with ``isPartOf``, siblings point
at each other with ``references``. Not to be confused with a collection, which
is a container — a relation joins two nodes that stand on their own.

Measured against edu-sharing 11.0 (staging, 2026-08-27):

* **The opposite direction is kept for you.** Create ``isPartOf`` from part to
  series, and the series reports ``hasPart`` — without setting it twice.
* **Only seven of the twelve types can be set.** The other five are those
  opposites; asking for one directly answers HTTP 400 with nothing that says
  why, which is what ``RELATION_TYPES`` and the check below are for.
* **The API is built for machine-made links.** ``isAiGenerated`` and an
  ``approve`` step exist so a model may propose and a person confirms. That
  matters here: this library exists to be driven by AI applications, and a
  suggestion that cannot be told apart from curated data is a liability.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .errors import ValidationError
from .transport import Transport
from .urls import path_segment

__all__ = ["RELATION_TYPES", "Relation", "Relations"]

#: The types that can be created. The remaining five (``hasPart``,
#: ``isBasisFor``, ``isRequiredBy``, ``isReplacedBy``, ``isFormatOf``) arise as
#: the opposite of one of these and are read-only.
RELATION_TYPES: tuple[str, ...] = (
    "isPartOf",
    "isBasedOn",
    "references",
    "isDuplicateOf",
    "requires",
    "replaces",
    "hasFormat",
)

#: Which type describes the same link seen from the other node. ``references``
#: and ``isDuplicateOf`` are their own opposite -- the relation is symmetric.
_OPPOSITES: dict[str, str] = {
    "isPartOf": "hasPart",
    "isBasedOn": "isBasisFor",
    "requires": "isRequiredBy",
    "replaces": "isReplacedBy",
    "hasFormat": "isFormatOf",
    "references": "references",
    "isDuplicateOf": "isDuplicateOf",
}
_OPPOSITES.update({v: k for k, v in _OPPOSITES.items() if v not in _OPPOSITES})


@dataclass(frozen=True)
class Relation:
    """One link, as seen from the node that was asked."""

    type: str
    from_id: str
    to_id: str
    from_title: str = ""
    to_title: str = ""
    #: Whether a machine proposed this link rather than a person.
    ai_generated: bool = False
    #: Whether a person has confirmed it. A machine-made link that nobody
    #: approved is a suggestion, not a fact.
    approved: bool = False
    created_by: str = ""
    created_at: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def opposite_of(relation_type: str) -> str | None:
        """The type describing this link from the other node's side.

        ``None`` for an unknown type -- guessing one would invent a link
        direction that does not exist.
        """
        return _OPPOSITES.get(relation_type)

    @classmethod
    def from_response(cls, data: dict[str, Any]) -> Relation:
        source = data.get("fromNode") or {}
        target = data.get("toNode") or {}
        evaluation = data.get("evaluation") or {}
        creator = data.get("createdBy") or {}
        return cls(
            type=data.get("type") or "",
            from_id=(source.get("ref") or {}).get("id") or "",
            to_id=(target.get("ref") or {}).get("id") or "",
            from_title=source.get("title") or source.get("name") or "",
            to_title=target.get("title") or target.get("name") or "",
            # The response carries both spellings; they agree, and reading only
            # one of them would depend on which version answers.
            ai_generated=bool(data.get("aiGenerated") or data.get("isAiGenerated")),
            approved=bool(evaluation.get("isApproved") or evaluation.get("approved")),
            created_by=creator.get("userName") or creator.get("authorityName") or "",
            created_at=data.get("createdAt") or "",
            metadata=data.get("metadata") or {},
            raw=data,
        )

    def __repr__(self) -> str:
        return f"Relation({self.from_id!r} -{self.type}-> {self.to_id!r})"


def _check(from_node: str, relation_type: str, to_node: str) -> None:
    """Reject what the API would refuse, with a message that says why.

    Both checks exist because the server's answer does not help: an unsettable
    type and a self-link both come back as a bare HTTP 400.
    """
    if relation_type not in RELATION_TYPES:
        allowed = ", ".join(RELATION_TYPES)
        opposite = Relation.opposite_of(relation_type)
        hint = ""
        if opposite:
            hint = (
                f" {relation_type!r} is the opposite of {opposite!r} and is kept "
                f"automatically -- create {opposite!r} the other way round."
            )
        raise ValidationError(
            f"{relation_type!r} cannot be created. Allowed: {allowed}.{hint}"
        )
    if not from_node or not to_node:
        raise ValidationError("A relation needs both a source and a target node.")
    if from_node == to_node:
        raise ValidationError(
            f"A node cannot be related to itself ({from_node!r})."
        )


class Relations:
    """The relations of one repository connection. Reached as ``repo.relations``."""

    def __init__(self, transport: Transport) -> None:
        self._transport = transport

    async def of(self, node_id: str) -> list[Relation]:
        """Every relation this node takes part in, from its own point of view.

        Both directions are included: a node that is part of a series and is
        referenced by a sibling reports both.

        Raises:
            NotFoundError: when no node carries this id.
        """
        response = await self._transport.json(
            "GET", f"/relation/v1/-home-/{path_segment(node_id)}"
        )
        entries = response if isinstance(response, list) else (
            response.get("relations") or []
        )
        return [Relation.from_response(entry) for entry in entries]

    async def create(
        self,
        from_node: str,
        relation_type: str,
        to_node: str,
        *,
        ai_generated: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Link ``from_node`` to ``to_node``.

        Args:
            from_node: the node the relation starts at.
            relation_type: one of ``RELATION_TYPES``.
            to_node: the node it points to.
            ai_generated: mark this as proposed by a machine. Set it when a
                model chose the link -- whoever reviews later needs to tell
                suggestions apart from curated data.
            metadata: free-form data stored with the relation.

        Raises:
            ValidationError: for an unsettable type, a missing id, or a link
                from a node to itself.
        """
        _check(from_node, relation_type, to_node)
        body: dict[str, Any] = {
            "fromNode": from_node,
            "toNode": to_node,
            "type": relation_type,
            "isAiGenerated": ai_generated,
        }
        if metadata:
            body["metadata"] = metadata
        await self._transport.request("POST", "/relation/v1/-home-", json=body)

    async def delete(self, from_node: str, relation_type: str, to_node: str) -> None:
        """Remove one relation. The nodes themselves are untouched.

        Raises:
            ValidationError: for an unsettable type or a missing id.
        """
        _check(from_node, relation_type, to_node)
        await self._transport.request(
            "DELETE",
            f"/relation/v1/-home-/{path_segment(from_node)}"
            f"/{path_segment(relation_type)}/{path_segment(to_node)}",
        )

    async def approve(self, from_node: str, relation_type: str, to_node: str) -> None:
        """Confirm a relation -- the human half of a machine suggestion.

        Raises:
            ValidationError: for an unsettable type or a missing id.
        """
        _check(from_node, relation_type, to_node)
        await self._transport.request(
            "POST",
            f"/relation/v1/-home-/{path_segment(from_node)}"
            f"/{path_segment(relation_type)}/{path_segment(to_node)}/approve",
        )

    def __repr__(self) -> str:
        return f"Relations({self._transport.repository_url!r})"
