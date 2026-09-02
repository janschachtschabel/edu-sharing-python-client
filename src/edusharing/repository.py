"""The entry point: a connection to an edu-sharing repository.

``AsyncRepository`` is the actual implementation, ``Repository`` passes it
through synchronously. Both answer two questions about the instance itself:

* ``about()`` -- what kind of instance is this, and what can it do?
* ``whoami()`` -- who am I actually running as?

The second matters more than it sounds. Without it an application does not
notice that it is working as a guest, and instead trips over an HTTP 500
somewhere unrelated to the cause.
"""

from __future__ import annotations

import os
from dataclasses import replace
from typing import Any, Self

import httpx

from ._sync import (
    LoopThread,
    SyncFlows,
    SyncNode,
    SyncPeople,
    SyncRelations,
    SyncTransport,
)
from .auth import ANONYMOUS, BasicCredential, Credential, credential_from
from .collections import Collections
from .errors import EduSharingError
from .flows import Flows
from .info import About, Identity, MetadataSet
from .nodes import Node, Nodes
from .people import People
from .relations import Relations
from .results import SearchResult
from .search import Search
from .transport import (
    DEFAULT_BACKOFF_BASE,
    DEFAULT_MAX_CONCURRENCY,
    DEFAULT_MAX_RETRIES,
    Transport,
)
from .vocab import DEFAULT_METADATASET, DEFAULT_QUERY, Vocabulary

__all__ = ["AsyncRepository", "Repository"]

ENV_URL = "EDU_SHARING_URL"


def _url_from_env(cls: type) -> str:
    """Read ``EDU_SHARING_URL``. Shared by both surfaces so their behaviour
    cannot drift apart.

    Raises:
        EduSharingError: when the variable is missing. The message names the
            call for whichever class is in use.
    """
    url = os.environ.get(ENV_URL)
    if not url:
        raise EduSharingError(
            f"{ENV_URL} is not set. Either set the variable or pass the address "
            f"directly: {cls.__name__}('https://...')."
        )
    return url


class AsyncRepository:
    """Connection to an edu-sharing repository.

    Args:
        url: address in any of the usual spellings.
        auth: ``None`` (anonymous), a ``(username, password)`` pair, or a ready
            ``Credential``. A bearer token is rejected.
        metadataset: metadata set for vocabulary and search. ``-default-`` is
            whichever the instance nominates; an instance may carry several, and
            the choice changes what is found (measured on staging: ``-default-``
            finds 2825 hits for "Physik", ``mds_oeh`` finds 17994).
        query: query context for vocabulary and search, ``ngsearch`` by
            convention.
        field_aliases: short names for filter properties (``subject`` ->
            ``ccm:taxonid``). ``None`` uses the default.
        timeout: seconds until a request is abandoned. Cannot be combined
            with ``client`` -- a client carries its own, and this one
            would be ignored.
        max_retries: retries in addition to the first attempt.
        max_concurrency: requests running at once.
        backoff_base: base wait between retries.
        client: your own httpx client, e.g. for tests.
    """

    def __init__(
        self,
        url: str,
        *,
        auth: object = None,
        metadataset: str = DEFAULT_METADATASET,
        query: str = DEFAULT_QUERY,
        field_aliases: dict[str, str] | None = None,
        timeout: float | None = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
        max_concurrency: int = DEFAULT_MAX_CONCURRENCY,
        backoff_base: float = DEFAULT_BACKOFF_BASE,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._transport = Transport(
            url,
            credential=credential_from(auth) if auth is not None else ANONYMOUS,
            timeout=timeout,
            max_retries=max_retries,
            max_concurrency=max_concurrency,
            backoff_base=backoff_base,
            client=client,
        )
        self.metadataset = metadataset
        self.query = query
        # Created once and kept: the vocabulary cache lives inside it, and a
        # fresh object per access would discard it on every call.
        self._vocab = Vocabulary(self._transport, metadataset=metadataset, query=query)
        self._search = Search(
            self._transport, self._vocab,
            metadataset=metadataset, query=query, field_aliases=field_aliases,
        )
        self._collections = Collections(self._transport, metadataset=metadataset)
        self._nodes = Nodes(self._transport)
        self._relations = Relations(self._transport)
        self._people = People(self._transport)
        self._flows = Flows(self)

    @classmethod
    def from_env(cls, **kwargs: Any) -> AsyncRepository:
        """Build a connection from ``EDU_SHARING_URL`` and the credentials.

        Raises:
            EduSharingError: when ``EDU_SHARING_URL`` is missing, or when only
                one of username and password is set.
        """
        return cls(_url_from_env(cls), auth=BasicCredential.from_env(), **kwargs)

    # --- State ------------------------------------------------------------

    @property
    def url(self) -> str:
        """The normalised repository URL."""
        return self._transport.repository_url

    @property
    def credential(self) -> Credential:
        """The credentials used unless stated otherwise."""
        return self._transport.credential

    @property
    def raw(self) -> Transport:
        """The transport, for endpoints without a method of their own.

        ``await repo.raw.json("GET", "/config/v1/values")``
        """
        return self._transport

    @property
    def vocab(self) -> Vocabulary:
        """This instance's vocabulary values -- labels instead of URIs.

        ``await repo.vocab.resolve("ccm:taxonid", "Physik")``
        """
        return self._vocab

    @property
    def searcher(self) -> Search:
        """The search layer, for access to its settings."""
        return self._search

    @property
    def relations(self) -> Relations:
        """Links between nodes that sit side by side -- a series and its parts,
        a resource and what it is based on.

        ``await repo.relations.of(node_id)``
        """
        return self._relations

    @property
    def flows(self) -> Flows:
        """Use-case flows -- several calls in one, answering in JSON.

        ``await repo.flows.search("Photosynthese", subject="Biologie")``
        """
        return self._flows

    @property
    def collections(self) -> Collections:
        """The collection search, for access to its settings."""
        return self._collections

    @property
    def people(self) -> People:
        """Groups and who belongs to them -- the "who may moderate" question.

        ``await repo.people.memberships()``
        """
        return self._people

    # --- Searching --------------------------------------------------------

    async def search(self, text: str | None = None, **kwargs: Any) -> SearchResult:
        """Search for material. See ``Search.search`` for every parameter.

        ``await repo.search("Photosynthese", subject="Biologie")``

        The result carries ``unresolved``: if it is non-empty, a filter could
        not be resolved and the result is broader than requested.
        """
        return await self._search.search(text, **kwargs)

    # --- Nodes ------------------------------------------------------------

    @property
    def nodes(self) -> Nodes:
        """The node layer."""
        return self._nodes

    async def node(self, node_id: str) -> Node:
        """Load a node with all its properties."""
        return await self._nodes.get(node_id)

    async def create_node(self, parent_id: str, **kwargs: Any) -> Node:
        """Create a node. See ``Nodes.create``."""
        return await self._nodes.create(parent_id, **kwargs)

    async def create_collection(self, title: str, **kwargs: Any) -> Node:
        """Create a collection. See ``Collections.create``."""
        return await self._collections.create(title, **kwargs)

    async def add_to_collection(self, collection_id: str, node_id: str) -> bool:
        """Place a resource into a collection as a reference."""
        return await self._collections.add(collection_id, node_id)

    async def remove_from_collection(self, collection_id: str, node_id: str) -> None:
        """Take a resource out of a collection. The original stays."""
        await self._collections.remove(collection_id, node_id)

    async def find_collections(self, text: str, **kwargs: Any) -> SearchResult:
        """Search collections across both routes edu-sharing offers.

        ``total`` is a lower bound -- see ``collections``.
        """
        return await self._collections.find(text, **kwargs)

    # --- What the instance reports ----------------------------------------

    async def about(self) -> About:
        """Version, services, plugins and features of this instance."""
        return About.from_response(await self._transport.json("GET", "/_about"))

    async def metadatasets(self) -> list[MetadataSet]:
        """Which metadata sets this instance carries.

        Cheap (a few hundred bytes) -- unlike a metadata set itself, which
        weighs 17 MB for ``mds_oeh``.
        """
        response = await self._transport.json("GET", "/mds/v1/metadatasets/-home-")
        return [
            MetadataSet(id=m.get("id") or "", name=m.get("name") or "")
            for m in (response.get("metadatasets") or [])
            if m.get("id")
        ]

    async def whoami(self) -> Identity:
        """Who this connection is working as.

        Anonymous is not an error but a valid mode -- but the application should
        know it rather than assume it.
        """
        data = await self._transport.json("GET", "/iam/v1/people/-home-/-me-")
        return Identity.from_response(data)

    # --- Lifecycle --------------------------------------------------------

    async def aclose(self) -> None:
        await self._transport.aclose()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        await self.aclose()

    def __repr__(self) -> str:
        return f"AsyncRepository({self.url!r})"


class Repository:
    """The synchronous surface -- for scripts and notebooks.

    Same signature as ``AsyncRepository``. Calls run on a background loop of
    their own, so they also work where an event loop is already running.
    """

    def __init__(self, url: str, **kwargs: Any) -> None:
        self._loop = LoopThread()
        self._async = AsyncRepository(url, **kwargs)
        self._closed = False

    @classmethod
    def from_env(cls, **kwargs: Any) -> Repository:
        """As ``AsyncRepository.from_env``."""
        return cls(_url_from_env(cls), auth=BasicCredential.from_env(), **kwargs)

    @property
    def url(self) -> str:
        return self._async.url

    @property
    def credential(self) -> Credential:
        return self._async.credential

    @property
    def raw(self) -> SyncTransport:
        """The transport, for endpoints without a method of their own.

        ``repo.raw.json("GET", "/config/v1/values")``
        """
        return SyncTransport(self._async.raw, self._loop)

    @property
    def metadataset(self) -> str:
        return self._async.metadataset

    @property
    def vocab(self) -> Vocabulary:
        """This instance's vocabulary values. Its methods are asynchronous --
        for the synchronous route see ``resolve()``."""
        return self._async.vocab

    @property
    def searcher(self) -> Search:
        """The search layer, for access to its settings."""
        return self._async.searcher

    @property
    def relations(self) -> SyncRelations:
        """Links between nodes that sit side by side.

        ``repo.relations.of(node_id)``
        """
        return SyncRelations(self._async.relations, self._loop)

    @property
    def people(self) -> SyncPeople:
        """Groups and who belongs to them, blocking.

        ``repo.people.memberships()``
        """
        return SyncPeople(self._async.people, self._loop)

    @property
    def flows(self) -> SyncFlows:
        """Use-case flows -- several calls in one, answering in JSON.

        ``repo.flows.search("Photosynthese", subject="Biologie")``
        """
        return SyncFlows(self._async.flows, self._loop)

    def search(self, text: str | None = None, **kwargs: Any) -> SearchResult:
        """Search for material. See ``Search.search`` for every parameter."""
        return self._loop.run(self._async.search(text, **kwargs))

    @property
    def collections(self) -> Collections:
        """The collection search, for access to its settings."""
        return self._async.collections

    def find_collections(self, text: str, **kwargs: Any) -> SearchResult:
        """Search collections across both routes. ``total`` is a lower bound."""
        return self._loop.run(self._async.find_collections(text, **kwargs))

    @property
    def nodes(self) -> Nodes:
        """The node layer. Its methods are asynchronous -- for the synchronous
        route see ``node()`` and ``create_node()``."""
        return self._async.nodes

    def create_collection(self, title: str, **kwargs: Any) -> SyncNode:
        """Create a collection. See ``Collections.create``."""
        return SyncNode(
            self._loop.run(self._async.create_collection(title, **kwargs)), self._loop
        )

    def add_to_collection(self, collection_id: str, node_id: str) -> bool:
        """Place a resource into a collection as a reference."""
        return self._loop.run(self._async.add_to_collection(collection_id, node_id))

    def remove_from_collection(self, collection_id: str, node_id: str) -> None:
        """Take a resource out of a collection. The original stays."""
        self._loop.run(self._async.remove_from_collection(collection_id, node_id))

    def children(self, node_id: str, **kwargs: Any) -> Any:
        """Like ``Nodes.children``, blocking. One page of a node's children."""
        seite = self._loop.run(self._async.nodes.children(node_id, **kwargs))
        # The page keeps its shape and swaps every node for its blocking
        # wrapper. ``Page`` is not generic over its node type, so the checker
        # reads this as the wrong item type; the whole sync facade does it.
        return replace(seite, nodes=tuple(
            SyncNode(n, self._loop)  # type: ignore[misc]
            for n in seite.nodes))

    def update_collection(self, collection_id: str, **kwargs: Any) -> SyncNode:
        """Like ``Collections.update``, blocking."""
        return SyncNode(
            self._loop.run(self._async.collections.update(collection_id, **kwargs)),
            self._loop)

    def node(self, node_id: str) -> SyncNode:
        """Load a node. Its write methods block."""
        return SyncNode(self._loop.run(self._async.node(node_id)), self._loop)

    def create_node(self, parent_id: str, **kwargs: Any) -> SyncNode:
        """Create a node. See ``Nodes.create``."""
        return SyncNode(
            self._loop.run(self._async.create_node(parent_id, **kwargs)), self._loop
        )

    def resolve(self, prop: str, label: str, *, locale: str | None = None) -> str | None:
        """Translate a label into the value the repository filters on.

        Only the first value. When the label may belong to two vocabularies,
        use ``resolve_all``.
        """
        return self._loop.run(self._async.vocab.resolve(prop, label, locale=locale))

    def resolve_all(
        self, prop: str, label: str, *, locale: str | None = None
    ) -> list[str]:
        """Every value carrying this label. See ``Vocabulary.resolve_all``.

        ``search`` resolves ambiguous labels by itself, so this is for code
        that wants to see the set rather than filter on it.
        """
        return self._loop.run(self._async.vocab.resolve_all(prop, label, locale=locale))

    def about(self) -> About:
        """Version, services, plugins and features of this instance."""
        return self._loop.run(self._async.about())

    def whoami(self) -> Identity:
        """Who this connection is working as."""
        return self._loop.run(self._async.whoami())

    def metadatasets(self) -> list[MetadataSet]:
        """Which metadata sets this instance carries."""
        return self._loop.run(self._async.metadatasets())

    def close(self) -> None:
        """Close the connection.

        Calling it repeatedly is allowed: ``close()`` typically sits in a
        ``finally`` **and** is called by the context manager, so the second call
        is the normal case, not an error. Without the guard the second one
        raises, because the loop is already gone.
        """
        if self._closed:
            return
        self._closed = True
        try:
            self._loop.run(self._async.aclose())
        finally:
            self._loop.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()

    def __repr__(self) -> str:
        return f"Repository({self.url!r})"
