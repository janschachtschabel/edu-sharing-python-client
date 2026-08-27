"""Show what would happen -- then do it.

An agent writing on someone's behalf must be able to present the change before
it takes place. Otherwise all that person can do is believe the model, and the
difference between "title extended" and "title replaced" only shows in the
result.

``plan_update`` reads the current state, compares it with the intended one and
writes **nothing**. Only ``apply()`` executes -- through ``Node.update``, and
therefore including the read-back check.

The plan surfaces two things that would otherwise only show afterwards: changes
that are not changes (same value -- writing it merely creates a version), and a
missing write permission.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..nodes import Node
from .sanitize import sanitize_text

__all__ = ["ChangePlan", "plan_update"]


def _show(values: list[str], *, max_chars: int = 80) -> str:
    """Make values readable -- the current value is foreign repository text."""
    if not values:
        return "(empty)"
    text = ", ".join(sanitize_text(v) for v in values)
    return text if len(text) <= max_chars else text[: max_chars - 1] + "…"


@dataclass
class ChangePlan:
    """A prepared change that has not been executed."""

    node: Node
    #: ``{property: (current, intended)}`` -- only the fields that differ.
    changes: dict[str, tuple[list[str], list[str]]] = field(default_factory=dict)
    #: Fields whose intended value already equals the current one.
    unchanged: dict[str, list[str]] = field(default_factory=dict)

    @property
    def has_changes(self) -> bool:
        return bool(self.changes)

    @property
    def can_write(self) -> bool:
        """Whether the account may write to this node."""
        return self.node.can_write

    def describe(self) -> str:
        """What this plan would change, as text to present."""
        lines = [f"Node {self.node.id} ({sanitize_text(self.node.title) or 'untitled'})"]

        if not self.can_write:
            lines.append(
                "! No write permission on this node -- the change would fail or "
                "be discarded silently."
            )

        if not self.changes:
            lines.append("No change: every value is already set that way.")
            return "\n".join(lines)

        lines.append(f"{len(self.changes)} change(s):")
        for prop, (current, intended) in self.changes.items():
            lines.append(f"  {prop}: {_show(current)}  ->  {_show(intended)}")
        if self.unchanged:
            lines.append(f"  (unchanged: {', '.join(sorted(self.unchanged))})")
        return "\n".join(lines)

    async def apply(self, *, verify: bool = True) -> Node:
        """Execute the change.

        With nothing to change, nothing is written -- writing identical values
        only creates load and possibly a version.

        Returns:
            The node as read back.

        Raises:
            SilentDropError: as in ``Node.update``.
        """
        if not self.changes:
            return self.node
        return await self.node.update(
            properties={prop: intended for prop, (_, intended) in self.changes.items()},
            verify=verify,
        )

    def __repr__(self) -> str:
        return f"ChangePlan(node={self.node.id!r}, changes={len(self.changes)})"


async def plan_update(
    node: Node,
    *,
    properties: dict[str, Any] | None = None,
    **aliases: Any,
) -> ChangePlan:
    """Prepare a change without executing it.

    Takes the same arguments as ``Node.update``. The intended state is held
    against the loaded current state; nothing is written.

    Raises:
        ValidationError: for an unknown short name -- a typo should surface
            before the plan is presented, not after.
    """
    # Uses the same alias resolution as update(), so plan and execution cannot
    # drift apart.
    intended = node._fields(properties, aliases)

    changes: dict[str, tuple[list[str], list[str]]] = {}
    unchanged: dict[str, list[str]] = {}
    for prop, new_values in intended.items():
        current = node.get_all(prop)
        if current == new_values:
            unchanged[prop] = current
        else:
            changes[prop] = (current, new_values)

    return ChangePlan(node=node, changes=changes, unchanged=unchanged)
