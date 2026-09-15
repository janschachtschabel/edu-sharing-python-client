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

import logging
from typing import TYPE_CHECKING, Any

from .dto import page_cut, page_total, render_url
from .errors import EduSharingError, ValidationError
from .urls import path_segment

if TYPE_CHECKING:  # pragma: no cover
    from .nodes import Node, Nodes

__all__ = ["CHILD_ASPECT", "LIST_MAX", "ORDER_PROPERTY", "ChildObjects"]

#: See ``edusharing.transport.logger``. Used for one thing only: a child node
#: that was created, could not be filled, and could not be removed either.
logger = logging.getLogger(__name__)

#: How many child objects one listing reads. Every other listing in this
#: library either takes a ``limit`` or has a named ceiling with a reason
#: (``DESCRIBE_MANY_MAX`` 50, ``SKILL_VISIT_MAX`` 30); this one took a bare
#: ``200`` and said nothing when there were more (audit MNT-4). 200 is kept:
#: attachments to one piece of material are a handful in practice, and the
#: number was the measured default here long before it had a name. One record
#: **more** than this is fetched, which is how a listing knows whether it is
#: complete without depending on a total -- see ``dto.page_cut``.
LIST_MAX = 200

#: The aspect that marks a child node as one of these. Other children exist
#: under a node -- versions, for instance -- and filtering on this is what tells
#: them apart.
CHILD_ASPECT = "ccm:io_childobject"

#: Where the display order lives.
ORDER_PROPERTY = "ccm:childobject_order"

#: Sorts a child without an order to the end. A missing order must not put a
#: document first by accident.
_NO_ORDER = 10**6

#: The raw child records of one page. Named, because ``list`` inside
#: ``ChildObjects`` is the **method**: an annotation written there resolves
#: to it and ``mypy --strict`` refuses it. A function body still sees the
#: builtin at runtime, so only the type checker catches this.
_Records = list[dict[str, Any]]


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

        Raises:
            EduSharingError: when the node has more children than ``LIST_MAX``.
                A shortened list of attachments is wrong for every use there is
                -- downloading them, showing them, counting them -- and the
                return type has no room to say "incomplete" (audit MNT-4).
        """
        antwort = await self._seite()
        roh = list(antwort.get("nodes") or [])
        if page_cut(roh, antwort, LIST_MAX):
            raise EduSharingError(
                f"This node has {_wie_viele(roh, antwort)} children and this "
                f"listing reads at most {LIST_MAX}. Returning the first "
                f"{LIST_MAX} would look like the whole set. Read them through "
                f"the children endpoint with your own paging.",
                url=render_url(self._nodes.repository_url, self._node.id),
            )
        children = _anhaenge(roh)
        children.sort(key=_order_key)
        return [self._nodes.wrap(data) for data in children]

    async def _seite(self) -> dict[str, Any]:
        """One page of child records -- one more than the cap.

        ``LIST_MAX + 1``, so that the page answers for itself whether it is all
        of them: one record over the cap means there are more, fewer means there
        are not. See ``dto.page_cut``.

        Shared by ``list()`` and ``_next_position()`` so that both read the same
        page the same way. What each does with a cut page stays with it, because
        the advice differs: read them yourself, or name the position yourself.
        """
        response: dict[str, Any] = await self._nodes.transport.json(
            "GET",
            f"/node/v1/nodes/-home-/{path_segment(self._node.id)}/children",
            params={"maxItems": LIST_MAX + 1, "propertyFilter": "-all-"},
        )
        return response

    async def _next_position(self) -> int:
        """One past the highest position the attachments hold.

        Not their number, and not the number of children. ``add()`` promises
        *after the existing ones*, and a count says that only while the
        positions run from 0 without gaps. Audit MNT-4 prescribed the count --
        "order from a ``limit=1`` page's total" -- and it does not carry the
        promise: measured on 2026-09-09, two attachments placed at 5 and 6 with
        ``order=`` gave the next one position 2, which ``list()`` then sorted
        **first**. Deleting an attachment leaves the same kind of gap, and there
        the repeated number is invisible here -- ``list()`` breaks the tie by
        creation time -- but not to anything else reading the property.

        Only children carrying the aspect are asked, because only they hold a
        position. Counting every child raised the number instead, which was
        defended as a harmless skip; the skip was never needed, and the two ways
        of counting were what collided twice (reviews 2026-09-08 and -09).
        """
        antwort = await self._seite()
        roh = list(antwort.get("nodes") or [])
        if page_cut(roh, antwort, LIST_MAX):
            raise EduSharingError(
                f"This node has {_wie_viele(roh, antwort)} children and this "
                f"listing reads at most {LIST_MAX}, so the highest position in "
                f"use cannot be read and the next free one cannot be "
                f"determined. Pass ``order=`` to say where this attachment "
                f"goes.",
                url=render_url(self._nodes.repository_url, self._node.id),
            )
        vergeben = [
            order
            for order, _ in map(_order_key, _anhaenge(roh))
            if order != _NO_ORDER
        ]
        return max(vergeben) + 1 if vergeben else 0

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
            order: display position. One past the highest in use when
                omitted -- otherwise two documents compete for the same slot.
                Passing it saves the request that reads the existing ones.

        Returns:
            The new child node, with its content already uploaded.

        Raises:
            ValidationError: on an empty filename.
            PermissionDeniedError: without write access to the parent.
            EduSharingError: for anything else the repository refuses -- the
                half-created child is cleaned up first -- and, before
                anything is created, when ``order`` was omitted and the node
                has more children than one listing reads, so the highest
                position in use cannot be seen. That one names ``order=`` as
                the way through.
        """
        if not filename or not filename.strip():
            raise ValidationError(
                "A child object needs a filename -- it decides the download name."
            )

        if order is None:
            order = await self._next_position()

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
        child = self._nodes.wrap(response.get("node") or {})
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
            except EduSharingError as cleanup_failed:
                # Swallowed, but not unsaid: the caller gets the upload error,
                # and that one does not know the child. Without this line an
                # empty node stays behind that nobody can attribute afterwards.
                logger.warning(
                    "child object %s could not be filled and could not be "
                    "removed either; it stays behind empty (%s)",
                    child.id, cleanup_failed,
                )
            raise

    def __repr__(self) -> str:
        return f"ChildObjects(node={self._node.id!r})"


def _anhaenge(roh: _Records) -> _Records:
    """Only the records carrying ``CHILD_ASPECT``.

    A node has other children -- versions among them -- and handing those
    back as attachments would be wrong in a way nobody notices until a
    version shows up in a download list.
    """
    return [data for data in roh if CHILD_ASPECT in (data.get("aspects") or [])]


def _wie_viele(roh: _Records, response: dict[str, Any]) -> str:
    """How many children to name in a refusal.

    The stated total only when it is larger than what arrived -- a total
    equal to the page size says nothing beyond what was counted, and naming
    it as *the* number would overstate what is known.
    """
    gesagt = page_total(response, default=-1)
    return str(gesagt) if gesagt > len(roh) else f"at least {len(roh)}"


def _order_key(data: dict[str, Any]) -> tuple[int, str]:
    properties = data.get("properties") or {}
    raw = (properties.get(ORDER_PROPERTY) or [None])[0]
    try:
        order = int(raw)
    except (TypeError, ValueError):
        order = _NO_ORDER
    return order, str(data.get("createdAt") or "")
