"""Reading, creating, changing and deleting nodes -- with a read-back check.

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

``update()`` therefore reads back after every write and raises
``SilentDropError`` when a value is missing. There are two usual causes -- the
property is not provided for in the metadata set, or the write permission is
absent -- and neither can be told from the other by the response alone; the
error message names both, along with the way out.

Falling back to ``set_property`` automatically would be convenient and wrong:
the metadata set's filtering is a decision of the repository, not a glitch.
Bypassing it is a deliberate step.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from . import placement, ratings
from .childobjects import ChildObjects
from .comments import Comments
from .content import NodeContent
from .errors import SilentDropError, ValidationError
from .permissions import NodePermissions
from .ratings import Rating
from .suggestions import Suggestions
from .transport import Transport
from .urls import path_segment
from .workflow import Workflow

__all__ = ["ChildPage", "Node", "Nodes", "WRITE_FIELD_ALIASES",
           "KEYWORD_PROPERTY"]

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

DEFAULT_NODE_TYPE = "ccm:io"

#: The shared keyword list. Its own constant because it is needed in three
#: places and a typo here would write silently into nowhere.
KEYWORD_PROPERTY = "cclom:general_keyword"


def _as_list(value: Any) -> list[str]:
    """edu-sharing expects every property as a list, even single values."""
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return [str(v) for v in value]
    return [str(value)]


class Node:
    """A loaded node.

    Immutable: ``update()`` and ``set_property()`` return a **new** ``Node``
    carrying the read-back state instead of mutating this one. That way no
    object can claim a value the repository never accepted.
    """

    def __init__(self, data: dict[str, Any], nodes: Nodes) -> None:
        self._data = data
        self._nodes = nodes

    # --- Reading ----------------------------------------------------------

    @property
    def id(self) -> str:
        return (self._data.get("ref") or {}).get("id") or ""

    @property
    def name(self) -> str:
        return self._data.get("name") or ""

    @property
    def title(self) -> str:
        return self._data.get("title") or self.get("cclom:title") or ""

    @property
    def type(self) -> str:
        return self._data.get("type") or ""

    @property
    def url(self) -> str:
        """The viewer URL -- what you hand on to someone."""
        return f"{self._nodes.repository_url}/components/render/{self.id}"

    @property
    def access(self) -> list[str]:
        """Your own permissions on this node."""
        return list(self._data.get("access") or [])

    @property
    def can_write(self) -> bool:
        """Whether writing is permitted.

        Checkable up front -- otherwise a missing permission is
        indistinguishable from metadata-set filtering until after the write
        attempt.
        """
        return "Write" in self.access

    @property
    def is_public(self) -> bool:
        """Whether anyone may read this node -- inherited access included.

        Free: the repository puts ``isPublic`` into every node response, and
        measured on 2026-08-28 it agrees with the access control list in both
        directions, inheritance included.

        edu-sharing does **not** set this when material is referenced into a
        public collection. Something an application creates and files is
        therefore readable by its creator alone until ``permissions.publish()``
        says otherwise.
        """
        return bool(self.raw.get("isPublic"))

    @property
    def preview_url(self) -> str | None:
        """The node's own preview image, or ``None``.

        Free: the response carries it. ``None`` when the repository is serving
        a type icon rather than a picture of this node -- measured on
        2026-08-28, ``preview.url`` is set either way and even survives
        deleting the image. ``isIcon`` is what tells them apart, the same trap
        ``downloadUrl`` has.
        """
        preview = self.raw.get("preview") or {}
        url = preview.get("url")
        return str(url) if url and not preview.get("isIcon") else None

    @property
    def properties(self) -> dict[str, Any]:
        return self._data.get("properties") or {}

    @property
    def raw(self) -> dict[str, Any]:
        return self._data

    def get(self, prop: str) -> str | None:
        """The first value of a property, or ``None``."""
        values = self.properties.get(prop)
        if isinstance(values, list):
            return str(values[0]) if values else None
        return str(values) if values else None

    def get_all(self, prop: str) -> list[str]:
        """Every value of a property."""
        return _as_list(self.properties.get(prop))

    @property
    def children(self) -> ChildObjects:
        """Further documents belonging to this one -- an answer sheet, handouts.

        ``await node.children.list()``
        """
        return ChildObjects(self, self._nodes)

    @property
    def content(self) -> NodeContent:
        """The binary content: upload, download, full text."""
        return NodeContent(self)

    async def parents(self) -> list[Node]:
        """The folders this node sits in, nearest first.

        See ``placement.parents_of``. Not the collections it was curated into
        -- those are ``collections()``, and a node in ten collections still has
        one parent chain.
        """
        ancestry = await placement.ancestry_of(self._nodes, self.id)
        return list(ancestry.parents)

    async def collections(self) -> list[Node]:
        """The collections holding a reference to this node.

        See ``placement.collections_of``.
        """
        return await placement.collections_of(self._nodes, self.id)

    @property
    def workflow(self) -> Workflow:
        """The editorial history -- and the way into it.

        ``await node.workflow.submit("GROUP_redaktion", "100_tocheck")``
        """
        return Workflow(self)

    @property
    def suggestions(self) -> Suggestions:
        """Metadata proposed for this node but not written to it.

        ``await node.suggestions.propose("ccm:taxonid", uri, "why")``
        """
        return Suggestions(self)

    @property
    def comments(self) -> Comments:
        """What people wrote about this node.

        ``await node.comments.add("Sehr brauchbar")``
        """
        return Comments(self)

    @property
    def rating(self) -> Rating | None:
        """How this node was rated -- ``None`` when nobody has.

        Free: the response carries the summary. See ``ratings.rating_of``.
        """
        return ratings.rating_of(self)

    async def rate(self, value: float, text: str = "") -> Rating | None:
        """Rate this node and read the new summary back.

        See ``ratings.rate``. A vote of zero is refused -- it does not take a
        rating back, it lowers the average.
        """
        return await ratings.rate(self, value, text)

    async def unrate(self) -> Rating | None:
        """Take this account's vote back. See ``ratings.unrate``."""
        return await ratings.unrate(self)

    @property
    def permissions(self) -> NodePermissions:
        """Who may do what with this node -- and whether anyone may read it.

        ``await node.permissions.publish()``
        """
        return NodePermissions(self)

    # --- Writing ----------------------------------------------------------

    async def update(
        self,
        *,
        properties: dict[str, Any] | None = None,
        verify: bool = True,
        **aliases: Any,
    ) -> Node:
        """Change properties and read back whether they arrived.

        Args:
            properties: ``{property: value}``. Single values become lists.
            verify: the read-back check. Only switch it off when the extra
                request per write demonstrably hurts -- it is the only evidence
                that anything was stored.
            **aliases: short names from ``WRITE_FIELD_ALIASES``, e.g. ``title=``.

        Returns:
            A new ``Node`` carrying the read-back state.

        Raises:
            SilentDropError: when the repository reports 200 and values are
                missing afterwards.
            ValidationError: for an unknown short name.
        """
        fields = self._fields(properties, aliases)
        if not fields:
            return self

        await self._nodes.transport.json(
            "PUT", f"/node/v1/nodes/-home-/{path_segment(self.id)}/metadata", json=fields
        )
        if not verify:
            return self

        fresh = await self._nodes.get(self.id)
        fresh._check(fields, route="update")
        return fresh

    async def set_property(self, prop: str, value: Any, *, verify: bool = True) -> Node:
        """Set a single property past the metadata set.

        The route for fields the metadata set does not know -- and the reason
        ``update()`` does not divert here itself: bypassing the filtering should
        stay a deliberate decision.

        Args:
            value: the value, or ``None`` to delete.

        Raises:
            SilentDropError: when the value is not set afterwards.
        """
        if value is None:
            # Measured: both a "null" body and no body at all delete the
            # property. The explicit "null" is sent -- it is the documented
            # route, and an omission is something another version may read
            # differently.
            await self._nodes.transport.request(
                "POST",
                f"/node/v1/nodes/-home-/{path_segment(self.id)}/property",
                params={"property": prop},
                content=b"null",
                headers={"Content-Type": "application/json"},
            )
        else:
            await self._nodes.transport.request(
                "POST",
                f"/node/v1/nodes/-home-/{path_segment(self.id)}/property",
                params={"property": prop},
                json=_as_list(value),
            )
        if not verify:
            return self

        fresh = await self._nodes.get(self.id)
        if value is None:
            return fresh
        fresh._check({prop: _as_list(value)}, route="set_property")
        return fresh

    # --- Keywords ---------------------------------------------------------

    @property
    def keywords(self) -> list[str]:
        """This node's keywords (``cclom:general_keyword``)."""
        return self.get_all(KEYWORD_PROPERTY)

    async def add_keywords(self, *keywords: str) -> Node:
        """Add keywords without losing the existing ones.

        ``cclom:general_keyword`` is a **shared list**: several parties --
        editors, crawlers, other applications -- maintain it together. Setting
        it instead of extending it deletes the others' work, and silently.

        A fresh read happens before merging: this object may be stale, and
        merging onto its state would overwrite whatever has been added since.

        Note:
            There is a window between reading and writing. edu-sharing offers no
            version check to close it, so a concurrent foreign write can still
            be lost. The window is small, but it is there.
        """
        return await self._change_keywords(add=keywords, remove=())

    async def remove_keywords(self, *keywords: str) -> Node:
        """Remove keywords and leave the rest in place.

        Removing an unknown keyword is not an error.
        """
        return await self._change_keywords(add=(), remove=keywords)

    async def _change_keywords(
        self, *, add: tuple[str, ...], remove: tuple[str, ...]
    ) -> Node:
        if not add and not remove:
            return self

        fresh = await self._nodes.get(self.id)
        existing = fresh.keywords
        dropping = {k.strip().casefold() for k in remove}

        merged = [k for k in existing if k.strip().casefold() not in dropping]
        known = {k.strip().casefold() for k in merged}
        for k in add:
            if k.strip().casefold() not in known:
                merged.append(k)
                known.add(k.strip().casefold())

        if merged == existing:
            return fresh
        return await fresh.update(properties={KEYWORD_PROPERTY: merged})

    async def delete(self, *, recycle: bool = True) -> None:
        """Delete the node.

        Args:
            recycle: ``True`` puts it in the recycle bin. The switch is always
                sent explicitly, never left to the server default.

        Note:
            Recoverability cannot be proven at the moment of deletion -- the
            archive search answers unreliably. A deleted node therefore counts
            as gone.
        """
        await self._nodes.transport.request(
            "DELETE",
            f"/node/v1/nodes/-home-/{path_segment(self.id)}",
            params={"recycle": "true" if recycle else "false"},
        )

    # --- Internals --------------------------------------------------------

    def _fields(
        self, properties: dict[str, Any] | None, aliases: dict[str, Any]
    ) -> dict[str, list[str]]:
        fields: dict[str, list[str]] = {
            p: _as_list(v) for p, v in (properties or {}).items()
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
                fields[target] = _as_list(value)
        return fields

    def _check(self, expected: dict[str, list[str]], *, route: str) -> None:
        """Compare the read-back state against what was written."""
        lost = [
            prop for prop, values in expected.items()
            if self.get_all(prop) != values
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
            url=self.url,
        )

    def __repr__(self) -> str:
        return f"Node(id={self.id!r}, title={self.title!r})"


@dataclass(frozen=True)
class ChildPage:
    """One page of a node's children.

    Attributes:
        nodes: the children on this page.
        total: how many there are altogether.
        offset: where this page started.
    """

    nodes: tuple[Node, ...]
    total: int
    offset: int

    def __repr__(self) -> str:
        return f"ChildPage({len(self.nodes)} von {self.total}, ab {self.offset})"


class Nodes:
    """Access to a repository's nodes."""

    def __init__(self, transport: Transport) -> None:
        self.transport = transport

    @property
    def repository_url(self) -> str:
        return self.transport.repository_url

    async def get(self, node_id: str) -> Node:
        """Load a node with all its properties."""
        response = await self.transport.json(
            "GET",
            f"/node/v1/nodes/-home-/{path_segment(node_id)}/metadata",
            params={"propertyFilter": "-all-"},
        )
        return Node(response.get("node") or {}, self)

    async def create(
        self,
        parent_id: str,
        *,
        name: str,
        type: str = DEFAULT_NODE_TYPE,
        properties: dict[str, Any] | None = None,
        rename_if_exists: bool = True,
        verify: bool = True,
        **aliases: Any,
    ) -> Node:
        """Create a node under ``parent_id``.

        Args:
            name: ``cm:name`` -- the key within the parent. Mandatory, because
                otherwise the outcome depends on the server rather than being
                predictable.
            type: node type, ``ccm:io`` for material, ``cm:folder`` for folders.
            rename_if_exists: appends a counter on a name collision instead of
                failing with 409.
            verify: check the response against what was sent. Costs nothing --
                the response carries the created node -- and catches the case
                where the repository answers 200 and stores less than it was
                given. Switch it off only for a field you know is derived.
            **aliases: short names from ``WRITE_FIELD_ALIASES``.

        Raises:
            ValidationError: when ``name`` is empty.
            SilentDropError: when the repository accepted the call and did not
                store everything. Measured 2026-08-28:
                ``ccm:oeh_lrt_aggregated`` is derived from ``ccm:oeh_lrt`` and
                comes back absent, while ``ccm:taxonid`` in the same call
                arrives -- so a write can half-succeed and look complete.
        """
        if not name or not name.strip():
            raise ValidationError(
                "A node needs a name (cm:name) -- it is the key within the parent."
            )

        placeholder = Node({}, self)
        fields = placeholder._fields(properties, aliases)
        fields["cm:name"] = [name]

        response = await self.transport.json(
            "POST",
            f"/node/v1/nodes/-home-/{path_segment(parent_id)}/children",
            params={
                "type": type,
                "renameIfExists": "true" if rename_if_exists else "false",
            },
            json=fields,
        )
        node = Node(response.get("node") or {}, self)
        if verify:
            # Against the response, not a fresh read: measured, the response
            # already shows what was dropped, and a second request would only
            # cost a round trip.
            node._check(fields, route="create")
        return node

    async def children(
        self,
        node_id: str,
        *,
        limit: int = 50,
        offset: int = 0,
        sort: str = "cm:name",
        ascending: bool = True,
        only: str | None = None,
    ) -> ChildPage:
        """One page of what sits inside a folder or a node.

        Not the same as ``node.children``, which returns the **child objects**
        -- the documents belonging to one piece of material, filtered by the
        ``ccm:io_childobject`` aspect. This is the plain listing: everything
        the repository puts under the node, versions and all.

        Args:
            node_id: the parent.
            limit, offset: page size and starting point.
            sort: the property to order by. There is a default on purpose:
                paging over an unordered listing can repeat some entries and
                miss others, and the endpoint orders nothing by itself.
            ascending: the direction.
            only: ``"files"`` or ``"folders"`` to narrow it. Measured, both
                work; other values are the instance's business.

        Returns:
            A ``ChildPage`` with the nodes, the total and the offset.
        """
        params: dict[str, Any] = {
            "maxItems": limit,
            "skipCount": offset,
            "sortProperties": sort,
            "sortAscending": "true" if ascending else "false",
            # Without this the children arrive with an empty properties object
            # -- names but no titles.
            "propertyFilter": "-all-",
        }
        if only:
            params["filter"] = only

        response = await self.transport.json(
            "GET",
            f"/node/v1/nodes/-home-/{path_segment(node_id)}/children",
            params=params,
        )
        pagination = response.get("pagination") or {}
        return ChildPage(
            nodes=tuple(Node(data, self) for data in (response.get("nodes") or [])),
            total=int(pagination.get("total") or 0),
            offset=int(pagination.get("from") or 0),
        )

    def __repr__(self) -> str:
        return f"Nodes({self.repository_url!r})"
