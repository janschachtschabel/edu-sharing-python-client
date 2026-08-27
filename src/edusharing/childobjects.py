"""Further documents belonging to one piece of material.

A worksheet and its answer sheet, a lesson plan and its handouts: edu-sharing
keeps those as **child objects** under the main node, not as separate material
and not as a collection. They travel with the parent and have no life of their
own.

The combination that creates one cannot be guessed, and getting it wrong answers
HTTP 500 with nothing that says why. Measured against staging on 2026-08-27:

===========================================  =====================================
attempt                                      outcome
===========================================  =====================================
``type=ccm:io_childobject``                  500 -- no such type exists
``type=ccm:io``, no ``assocType``            500 -- integrity violation
``type=ccm:io`` + ``assocType=ccm:childio``  created
+ ``aspects=ccm:io_childobject``
===========================================  =====================================

``ccm:io_childobject`` is an **aspect**, not a type. The working combination
comes from the Ideendatenbank, which uses it in production for attachments.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .errors import EduSharingError, ValidationError
from .urls import path_segment

if TYPE_CHECKING:  # pragma: no cover
    from .nodes import Node, Nodes

__all__ = ["CHILD_ASPECT", "ORDER_PROPERTY", "ChildObjects"]

#: The aspect that marks a child node as one of these. Other children exist
#: under a node -- versions, for instance -- and filtering on this is what tells
#: them apart.
CHILD_ASPECT = "ccm:io_childobject"

#: Where the display order lives.
ORDER_PROPERTY = "ccm:childobject_order"

#: Sorts a child without an order to the end. A missing order must not put a
#: document first by accident.
_NO_ORDER = 10**6


class ChildObjects:
    """The child objects of one node. Reached as ``node.children``."""

    def __init__(self, node: Node, nodes: Nodes) -> None:
        self._node = node
        self._nodes = nodes

    async def list(self) -> list[Node]:
        """The child objects, in display order.

        Only nodes carrying ``CHILD_ASPECT`` are returned. A node also has other
        children -- versions among them -- and handing those back as attachments
        would be wrong in a way nobody notices until a version shows up in a
        download list.

        Ordered by ``ccm:childobject_order``, then by creation time. The second
        key matters: two documents added in the same request can share a number.
        """
        response = await self._nodes.transport.json(
            "GET",
            f"/node/v1/nodes/-home-/{path_segment(self._node.id)}/children",
            params={"maxItems": 200, "propertyFilter": "-all-"},
        )
        from .nodes import Node  # local: nodes imports this module

        children = [
            data
            for data in (response.get("nodes") or [])
            if CHILD_ASPECT in (data.get("aspects") or [])
        ]
        children.sort(key=_order_key)
        return [Node(data, self._nodes) for data in children]

    async def add(
        self,
        data: bytes,
        *,
        filename: str,
        mimetype: str,
        order: int | None = None,
    ) -> Node:
        """Attach a further document to this node.

        Two requests: create the child, then upload the bytes. If the upload
        fails the child is removed again -- a node without content is rubbish
        that shows up in every listing and downloads as nothing.

        Args:
            data: the file's bytes.
            filename: ``cm:name`` of the child, which decides the download name.
            mimetype: content type of the file.
            order: display position. Appended after the existing ones when
                omitted -- otherwise two documents compete for the same slot.

        Returns:
            The new child node, with its content already uploaded.

        Raises:
            ValidationError: on an empty filename.
            PermissionDeniedError: without write access to the parent.
            EduSharingError: for anything else the repository refuses. The
                half-created child is cleaned up first.
        """
        if not filename or not filename.strip():
            raise ValidationError(
                "A child object needs a filename -- it decides the download name."
            )

        if order is None:
            order = len(await self.list())

        response = await self._nodes.transport.json(
            "POST",
            f"/node/v1/nodes/-home-/{path_segment(self._node.id)}/children/",
            params={
                "type": "ccm:io",
                "renameIfExists": "true",
                "assocType": "ccm:childio",
                "versionComment": "",
                "aspects": CHILD_ASPECT,
            },
            json={"cm:name": [filename], ORDER_PROPERTY: [str(order)]},
        )
        from .nodes import Node

        child = Node(response.get("node") or {}, self._nodes)
        if not child.id:
            raise EduSharingError(
                "The repository created a child object without returning an id."
            )

        try:
            return await child.content.upload(
                data, filename=filename, mimetype=mimetype
            )
        except EduSharingError:
            # Deliberately swallowing only the cleanup's own failure: the
            # original error is what the caller needs, and a failed cleanup must
            # not replace it.
            try:
                await child.delete(recycle=False)
            except EduSharingError:
                pass
            raise

    def __repr__(self) -> str:
        return f"ChildObjects(node={self._node.id!r})"


def _order_key(data: dict[str, Any]) -> tuple[int, str]:
    properties = data.get("properties") or {}
    raw = (properties.get(ORDER_PROPERTY) or [None])[0]
    try:
        order = int(raw)
    except (TypeError, ValueError):
        order = _NO_ORDER
    return order, str(data.get("createdAt") or "")
