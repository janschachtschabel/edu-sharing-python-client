"""Use-case flows: chains of calls with a JSON answer.

The library has two levels, and they answer different questions.

The **API level** is deliberately close to edu-sharing. ``repo.search()``
returns a ``SearchResult``, ``repo.node()`` a ``Node``. That is right for
anyone writing Python against it -- objects with methods, typed, composable.

The **flow level** answers: *how do I do this typical thing in one call, and
get something I can pass straight on?* An MCP tool, an HTTP endpoint or a
language model does not want a ``SearchResult``; it wants JSON. And it does not
want to call four endpoints to publish one piece of material.

Flows add no capability. They remove steps, and they end at ``dict`` instead of
at an object. Everything they do can be done at the API level -- with more code.

    hits = await repo.flows.search("Photosynthese", subject="Biologie")
    json.dumps(hits)   # works, that is the point

The facade below repeats the signatures of the functions in ``discover`` and
``curate`` rather than forwarding ``*args, **kwargs``. That is duplication, and
it is deliberate: the signature is half the documentation, and ``repo.flows.``
should complete properly in an editor.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from . import curate, discover

if TYPE_CHECKING:  # pragma: no cover
    from ..repository import AsyncRepository

__all__ = ["Flows"]


class Flows:
    """The flows of one connection. Reached as ``repo.flows``."""

    def __init__(self, repo: AsyncRepository) -> None:
        self._repo = repo

    async def search(
        self,
        text: str | None = None,
        *,
        filters: dict[str, str | list[str]] | None = None,
        facets: list[str] | None = None,
        limit: int = 10,
        offset: int = 0,
        **aliases: str | list[str],
    ) -> dict[str, Any]:
        """Search for material, return JSON. See ``discover.search``.

        **Check ``unresolved`` in the answer**: non-empty means a filter was
        dropped and the result is broader than requested.
        """
        return await discover.search(
            self._repo, text, filters=filters, facets=facets,
            limit=limit, offset=offset, **aliases,
        )

    async def vocabulary(self, field: str, *, locale: str | None = None) -> dict[str, Any]:
        """The values a field accepts. See ``discover.vocabulary``."""
        return await discover.vocabulary(self._repo, field, locale=locale)

    async def describe(self, node_id: str) -> dict[str, Any]:
        """Everything about one node in a single call. See ``discover.describe``."""
        return await discover.describe(self._repo, node_id)

    # --- writing ----------------------------------------------------------

    async def add_material(
        self,
        title: str,
        *,
        url: str | None = None,
        parent_id: str | None = None,
        name: str | None = None,
        description: str | None = None,
        keywords: list[str] | None = None,
        collection_id: str | None = None,
        properties: dict[str, Any] | None = None,
        **aliases: Any,
    ) -> dict[str, Any]:
        """Create material, with vocabulary. See ``curate.add_material``.

        **Check ``unresolved`` in the answer**: those values were not written.
        """
        return await curate.add_material(
            self._repo, title, url=url, parent_id=parent_id, name=name,
            description=description, keywords=keywords,
            collection_id=collection_id, properties=properties, **aliases,
        )

    async def build_collection(
        self,
        title: str,
        *,
        description: str | None = None,
        parent_id: str | None = None,
        node_ids: list[str] | None = None,
        scope: str | None = None,
    ) -> dict[str, Any]:
        """Create a collection and fill it. See ``curate.build_collection``.

        **Check ``failed``**: the collection exists even when placing material
        did not fully work.
        """
        return await curate.build_collection(
            self._repo, title, description=description, parent_id=parent_id,
            node_ids=node_ids, scope=scope,
        )

    async def delete(self, node_id: str, *, recycle: bool = True) -> dict[str, Any]:
        """Delete a node and report what it was. See ``curate.delete``.

        Goes into the bin by default; permanent deletion has to be spelled out.
        """
        return await curate.delete(self._repo, node_id, recycle=recycle)

    def __repr__(self) -> str:
        return f"Flows({self._repo.url!r})"
