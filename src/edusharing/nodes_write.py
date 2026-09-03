"""The write path of a node -- and the read-back that proves a write happened.

The reason this module is not thin: **edu-sharing answers lost writes with
HTTP 200.** Measured on a throwaway node (edu-sharing 11.0, staging,
2026-08-27):

======================================  ====  ==========
Operation                               HTTP  stored
======================================  ====  ==========
``PUT /metadata``, property in the MDS   200  yes
``PUT /metadata``, property not in MDS   200  **no**
``POST /property``, same property        200  yes
``PUT /metadata``, invented field        200  **no**
======================================  ====  ==========

Twice a success code for something that did not happen. Relying on it means
telling your users their data is stored when it is not.

``update`` therefore reads back after every write and raises
``SilentDropError`` when a value is missing. There are two usual causes -- the
property is not provided for in the metadata set, or the write permission is
absent -- and neither can be told from the other by the response alone; the
error message names both, along with the way out.

Falling back to ``set_property`` automatically would be convenient and wrong:
the metadata set's filtering is a decision of the repository, not a glitch.
Bypassing it is a deliberate step.

The functions here are what ``Node.update``, ``Node.set_property`` and the
keyword methods call; the public surface stays on ``Node``. Split out of
``nodes.py`` on 2026-09-02, when the read model and the write discipline had
become two reasons to change one file.
"""

from __future__ import annotations

import contextlib
from collections.abc import Iterator
from typing import TYPE_CHECKING, Any, Literal

from .errors import EduSharingError, SilentDropError, ValidationError
from .urls import path_segment

if TYPE_CHECKING:  # pragma: no cover
    from .nodes import Node

__all__ = ["WRITE_FIELD_ALIASES", "KEYWORD_PROPERTY"]

#: Which write a read-back check follows -- the way out differs per route.
WriteRoute = Literal["update", "create", "set_property"]

#: Short names for write fields. Title and description deliberately go into
#: **both** namespaces: the edu-sharing interface renders ``cm:*`` and
#: ``cclom:*`` in different places, and setting only one makes the display show
#: something other than what the application wrote.
WRITE_FIELD_ALIASES: dict[str, tuple[str, ...]] = {
    "title": ("cm:title", "cclom:title"),
    "description": ("cm:description", "cclom:general_description"),
    "url": ("ccm:wwwurl",),
    "name": ("cm:name",),
    "author": ("ccm:author_freetext",),
    "keywords": ("cclom:general_keyword",),
}

#: The shared keyword list. Its own constant because it is needed in three
#: places and a typo here would write silently into nowhere.
KEYWORD_PROPERTY = "cclom:general_keyword"


def as_list(value: Any) -> list[str]:
    """edu-sharing expects every property as a list, even single values."""
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return [str(v) for v in value]
    return [str(value)]


def fields_of(
    properties: dict[str, Any] | None, aliases: dict[str, Any]
) -> dict[str, list[str]]:
    """The request body: every value a list, every short name expanded.

    Raises:
        ValidationError: for an unknown short name.
    """
    fields: dict[str, list[str]] = {
        p: as_list(v) for p, v in (properties or {}).items()
    }
    for name, value in aliases.items():
        targets = WRITE_FIELD_ALIASES.get(name)
        if targets is None:
            known = ", ".join(sorted(WRITE_FIELD_ALIASES))
            raise ValidationError(
                f"Unknown field {name!r}. Known are: {known}. A property can "
                "also be given directly: properties={'ccm:...': 'value'}."
            )
        for target in targets:
            fields[target] = as_list(value)
    return fields


def check(node: Node, expected: dict[str, list[str]], *, route: WriteRoute) -> None:
    """Compare the read-back state of ``node`` against what was written."""
    lost = [
        prop for prop, values in expected.items()
        if node.get_all(prop) != values
    ]
    if not lost:
        return

    if route == "update":
        way_out = "node.set_property(...) bypasses the metadata set's filtering."
    elif route == "create":
        way_out = (
            "A derived property is one more cause here: the repository "
            "computes it from another field and refuses it as input "
            "(measured: ccm:oeh_lrt_aggregated comes from ccm:oeh_lrt). "
            "Write the source field instead, or pass verify=False."
        )
    else:
        way_out = (
            "Check node.can_write -- without write permission this route is "
            "just as ineffective."
        )
    raise SilentDropError(
        f"Not stored: {', '.join(lost)} (HTTP 200, absent or different after "
        f"reading back). Two usual causes: the property is not provided for "
        f"in this instance's metadata set, or the write permission is "
        f"missing. {way_out}",
        dropped=lost,
        url=node.url,
    )


async def update(
    node: Node, *, properties: dict[str, Any] | None, verify: bool, aliases: dict[str, Any]
) -> Node:
    """``Node.update``: write, then read back -- at the original of a reference."""
    fields = fields_of(properties, aliases)
    if not fields:
        return node

    target = node.original_id or node.id
    with _naming_redirection(node, target):
        await node._nodes.transport.json(
            "PUT", f"/node/v1/nodes/-home-/{path_segment(target)}/metadata", json=fields,
            idempotent=True,
        )
    if not verify and target == node.id:
        return node

    # A redirected write is read back even without the check: the caller must
    # get the original, stamped, or the redirection goes unnoticed.
    fresh = await node._nodes.get(target)
    if verify:
        check(fresh, fields, route="update")
    return node._redirected(fresh)


async def set_property(node: Node, prop: str, value: Any, *, verify: bool) -> Node:
    """``Node.set_property``: one property past the metadata set, then read back."""
    # Same rule as ``update``: a reference is written through to its original.
    target = node.original_id or node.id
    route = f"/node/v1/nodes/-home-/{path_segment(target)}/property"
    # Measured: both a "null" body and no body at all delete the property. The
    # explicit "null" is sent -- it is the documented route, and an omission
    # is something another version may read differently.
    body: dict[str, Any] = (
        {"content": b"null", "headers": {"Content-Type": "application/json"}}
        if value is None else {"json": as_list(value)}
    )
    with _naming_redirection(node, target):
        await node._nodes.transport.request(
            "POST", route, params={"property": prop}, idempotent=True, **body
        )
    if not verify and target == node.id:
        return node

    fresh = await node._nodes.get(target)
    if verify and value is None and fresh.get_all(prop):
        # The 200 that proves nothing for a write proves nothing for a
        # deletion either: the property has to be gone after reading back.
        raise SilentDropError(
            f"Still present after deletion: {prop} (HTTP 200, value unchanged after "
            "reading back). A derived property cannot be removed this way; without "
            "write permission neither can any other.",
            dropped=[prop],
            url=fresh.url,
        )
    if verify and value is not None:
        check(fresh, {prop: as_list(value)}, route="set_property")
    return node._redirected(fresh)


async def change_keywords(
    node: Node, *, add: tuple[str, ...], remove: tuple[str, ...]
) -> Node:
    """Merge into the shared keyword list instead of replacing it."""
    if not add and not remove:
        return node

    # The list to merge into is the ORIGINAL's: a reference carries a copy
    # that stops inheriting the moment it is written to.
    fresh = await node._nodes.get(node.original_id or node.id)
    existing = fresh.keywords
    dropping = {k.strip().casefold() for k in remove}

    merged = [k for k in existing if k.strip().casefold() not in dropping]
    known = {k.strip().casefold() for k in merged}
    for k in add:
        if k.strip().casefold() not in known:
            merged.append(k)
            known.add(k.strip().casefold())

    if merged == existing:
        return node._redirected(fresh)
    return node._redirected(await fresh.update(properties={KEYWORD_PROPERTY: merged}))


@contextlib.contextmanager
def _naming_redirection(node: Node, target: str) -> Iterator[None]:
    """A failure at the original must say that the caller never held that id."""
    try:
        yield
    except EduSharingError as exc:
        if target != node.id:
            exc.add_note(f"write redirected from {node.id} to its original {target}")
        raise
