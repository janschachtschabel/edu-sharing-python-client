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

from . import curate, discover, pages, tree
from .language import GERMAN, LanguageProfile
from .rerank import DEFAULT_POOL

if TYPE_CHECKING:  # pragma: no cover
    from ..repository import AsyncRepository

__all__ = ["Flows", "LanguageProfile"]


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
        rerank: bool = False,
        pool: int = DEFAULT_POOL,
        language: LanguageProfile = GERMAN,
        deduplicate: bool = True,
        **aliases: str | list[str],
    ) -> dict[str, Any]:
        """Search for material, return JSON. See ``discover.search``.

        **Check ``unresolved`` in the answer**: non-empty means a filter was
        dropped and the result is broader than requested.

        ``rerank=True`` asks several query variants and reorders by relevance.
        It costs one request per variant and is what rescues a naturally
        phrased query -- measured: "Ich suche ein Arbeitsblatt zur
        Bruchrechnung" finds 0 records, "Bruchrechnung" finds 1591.
        """
        return await discover.search(
            self._repo, text, filters=filters, facets=facets,
            limit=limit, offset=offset, rerank=rerank, pool=pool,
            language=language, deduplicate=deduplicate, **aliases,
        )

    async def search_all(self, text: str, **kwargs: Any) -> dict[str, Any]:
        """Material **and** collections in one call. See ``discover.search_all``.

        **Read ``collections.filters_ignored``**: the collection search takes a
        search word and nothing else, so a filter narrows the material bucket
        and not the other one.
        """
        return await discover.search_all(self._repo, text, **kwargs)

    async def vocabulary(self, field: str, *, locale: str | None = None) -> dict[str, Any]:
        """The values a field accepts. See ``discover.vocabulary``."""
        return await discover.vocabulary(self._repo, field, locale=locale)

    async def describe(self, node_id: str) -> dict[str, Any]:
        """Everything about one node in a single call. See ``discover.describe``."""
        return await discover.describe(self._repo, node_id)

    async def describe_many(self, node_ids: Any) -> dict[str, Any]:
        """Describe several nodes at once. See ``discover.describe_many``.

        **Check ``failed``**: a node the search index still knows but the
        repository no longer has is reported there, not raised.
        """
        return await discover.describe_many(self._repo, node_ids)

    async def related(self, node_id: str, **kwargs: Any) -> dict[str, Any]:
        """More material like this one. See ``discover.related``.

        **Not a relation** -- ``flows.relations`` gives the links somebody
        asserted; this gives a resemblance computed from the node's own fields.
        **Read ``based_on``** to judge it, and **``unresolved``** for the
        values that did not narrow the search after all.
        """
        return await discover.related(self._repo, node_id, **kwargs)

    async def child_objects(self, node_id: str) -> dict[str, Any]:
        """Further documents belonging to one node. See ``discover.child_objects``."""
        return await discover.child_objects(self._repo, node_id)

    async def relations(self, node_id: str) -> dict[str, Any]:
        """What this node is linked to. See ``discover.relations``.

        **Read ``ai_generated`` and ``approved``**: a machine-proposed link that
        nobody confirmed is a suggestion, not a fact.
        """
        return await discover.relations(self._repo, node_id)

    async def placement(self, node_id: str) -> dict[str, Any]:
        """Where a node sits and who has curated it. See ``discover.placement``.

        **``path`` runs top down** here, ready to print -- ``node.parents()``
        mirrors the endpoint and gives the nearest first. And **read
        ``scope``**: the path stops at the boundary of what the account may
        read.
        """
        return await discover.placement(self._repo, node_id)

    async def page(self, collection_id: str, **kwargs: Any) -> dict[str, Any]:
        """The curated page a collection renders. See ``flows.pages.page``."""
        return await pages.page(self._repo, collection_id, **kwargs)

    async def find_pages(self, text: str = "", **kwargs: Any) -> dict[str, Any]:
        """Which collections carry one. See ``flows.pages.find_pages``."""
        return await pages.find_pages(self._repo, text, **kwargs)

    async def browse_tree(self, collection_id: str, **kwargs: Any) -> dict[str, Any]:
        """The collections underneath one collection. See ``tree.browse_tree``.

        **Read ``truncated``**: collections form a graph, and the walk is
        capped -- a shortened tree must not read as a complete one.
        """
        return await tree.browse_tree(self._repo, collection_id, **kwargs)

    async def search_in_collection(
        self, collection_id: str, query: str, **kwargs: Any
    ) -> dict[str, Any]:
        """Find material inside one collection. See ``tree.search_in_collection``.

        Walks and compares locally: a search cannot be scoped to a collection,
        measured three times. **Read ``truncated``** -- an empty result from a
        walk that stopped early is not "there is none".
        """
        return await tree.search_in_collection(
            self._repo, collection_id, query, **kwargs)

    async def collection_stats(
        self, collection_id: str, **kwargs: Any
    ) -> dict[str, Any]:
        """How much a collection holds, and what of. See ``tree.collection_stats``.

        The counts are exact; **the breakdown is a sample** -- ``sampled`` and
        ``complete`` say which.
        """
        return await tree.collection_stats(self._repo, collection_id, **kwargs)

    async def find_collections(self, text: str, *, limit: int = 10) -> dict[str, Any]:
        """Search collections. See ``discover.find_collections``.

        ``total_is_lower_bound`` is always true here -- two routes are merged.
        """
        return await discover.find_collections(self._repo, text, limit=limit)

    async def collection_contents(
        self, collection_id: str, *, limit: int = 20, offset: int = 0
    ) -> dict[str, Any]:
        """Material and sub-collections of one collection.
        See ``discover.collection_contents``."""
        return await discover.collection_contents(
            self._repo, collection_id, limit=limit, offset=offset)

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
        publish: bool = False,
        **aliases: Any,
    ) -> dict[str, Any]:
        """Create material, with vocabulary. See ``curate.add_material``.

        **Check ``unresolved`` in the answer**: those values were not written.

        **Check ``public``**: what is created here is readable by its creator
        and by nobody else. Filing it into a public collection does not change
        that -- measured. ``publish=True`` makes it world-readable, and is off
        by default because reading cannot be taken back.
        """
        return await curate.add_material(
            self._repo, title, url=url, parent_id=parent_id, name=name,
            description=description, keywords=keywords,
            collection_id=collection_id, properties=properties,
            publish=publish, **aliases,
        )

    async def update_material(
        self,
        node_id: str,
        *,
        title: str | None = None,
        url: str | None = None,
        description: str | None = None,
        keywords: list[str] | None = None,
        properties: dict[str, Any] | None = None,
        **aliases: Any,
    ) -> dict[str, Any]:
        """Change existing material, with vocabulary. See ``curate.update_material``.

        Only what is passed is written. **Check ``unresolved``.**
        """
        return await curate.update_material(
            self._repo, node_id, title=title, url=url, description=description,
            keywords=keywords, properties=properties, **aliases,
        )

    async def build_collection(
        self,
        title: str,
        *,
        description: str | None = None,
        parent_id: str | None = None,
        node_ids: list[str] | None = None,
        scope: str | None = None,
        publish: bool = False,
    ) -> dict[str, Any]:
        """Create a collection and fill it. See ``curate.build_collection``.

        **Check ``failed``**: the collection exists even when placing material
        did not fully work.

        **Check ``public``**: ``scope="PUBLIC"`` decides where the collection is
        listed, not who may open it -- measured, it comes back unreadable to
        others all the same. ``publish=True`` grants the read access.
        """
        return await curate.build_collection(
            self._repo, title, description=description, parent_id=parent_id,
            node_ids=node_ids, scope=scope, publish=publish,
        )

    async def delete(self, node_id: str, *, recycle: bool = True) -> dict[str, Any]:
        """Delete a node and report what it was. See ``curate.delete``.

        Goes into the bin by default; permanent deletion has to be spelled out.
        """
        return await curate.delete(self._repo, node_id, recycle=recycle)

    def __repr__(self) -> str:
        return f"Flows({self._repo.url!r})"
