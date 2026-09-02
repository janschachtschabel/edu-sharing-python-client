"""Value objects for search results.

Their own module because they have two callers: the material search and the
collection search. Living in either one would force the other to import from
there -- and the dependency would point the wrong way.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = ["SearchHit", "FacetValue", "Facet", "UnresolvedFilter", "SearchResult"]


@dataclass(frozen=True)
class SearchHit:
    """A single hit.

    ``id`` and ``url`` are the two details without which nobody can get back to
    the hit -- and exactly the ones a language model paraphrases away first when
    summarising.
    """

    id: str
    title: str
    url: str
    description: str | None = None
    source_url: str | None = None
    mimetype: str | None = None
    mediatype: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)
    #: The record behind a reference -- ``None`` on an original. A search
    #: scoped to a collection, and every collection listing, hands out
    #: reference ids; see ``original_id_of``.
    original_id: str | None = None

    def properties(self) -> dict[str, Any]:
        return self.raw.get("properties") or {}

    def labels(self, prop: str) -> list[str]:
        """The readable values of a vocabulary property.

        edu-sharing ships a ``<prop>_DISPLAYNAME`` alongside every vocabulary
        field; that saves a second request just to make a URI readable.
        """
        return list(self.properties().get(f"{prop}_DISPLAYNAME") or [])

    @classmethod
    def from_node(cls, node: dict[str, Any], repository_url: str) -> SearchHit:
        node_id = (node.get("ref") or {}).get("id") or ""
        props = node.get("properties") or {}
        return cls(
            id=node_id,
            title=node.get("title") or _first(props.get("cm:name")) or "",
            url=f"{repository_url}/components/render/{node_id}",
            description=_first(props.get("cclom:general_description"))
            or _first(props.get("cm:description")),
            source_url=_first(props.get("ccm:wwwurl")),
            mimetype=node.get("mimetype"),
            mediatype=node.get("mediatype"),
            raw=node,
            original_id=original_id_of(node),
        )


def original_id_of(node: dict[str, Any]) -> str | None:
    """The record a node response is a reference to -- ``None`` on an original.

    A collection holds **references**: adding material creates a node with its
    own id, and that id is what a listing hands out. Measured on 2026-09-02
    against staging, a reference's response carries ``originalId``; the usage
    endpoint knows only the original (empty list for the reference, two
    collections for the original behind it), and the MCP measured on
    2026-08-17 that a write aimed at a reference is stored on the reference
    and never reaches the original.

    The DTO field is read first. ``ccm:original`` is only the fallback for a
    repository that does not send it, and only when it names another node: on
    an original the property points at the record **itself** (3/3 measured),
    so reading it without that comparison would report every record as a
    reference to itself. One rule, used by ``Node`` and ``SearchHit`` alike.
    """
    dto = node.get("originalId")
    if dto:
        return str(dto)
    node_id = (node.get("ref") or {}).get("id") or ""
    prop = _first((node.get("properties") or {}).get("ccm:original"))
    return prop if prop and prop != node_id else None


@dataclass(frozen=True, slots=True)
class FacetValue:
    """One facet value with its hit count."""

    value: str
    count: int


@dataclass(frozen=True)
class Facet:
    """Server-side aggregation across the whole result set."""

    property: str
    values: list[FacetValue] = field(default_factory=list)
    #: Hits that fell into none of the returned values.
    other_count: int = 0

    # ``property: str`` above shadows the builtin inside this class body.
    # An annotation without a value binds nothing, so the decorator still
    # resolves to the builtin at runtime -- but a checker reads the
    # annotation. Renaming the field would break the public surface.
    @property  # type: ignore[operator]
    def truncated(self) -> bool:
        """Whether the value list has been cut short.

        Matters to anything summing facet counts: a truncated list looks
        authoritative and is too small.
        """
        return self.other_count > 0


@dataclass(frozen=True)
class UnresolvedFilter:
    """A filter value this instance's metadata set does not know."""

    field: str
    value: str
    # Same shadowing as ``Facet.property``: ``field: str`` above hides
    # ``dataclasses.field`` for the checker, not for the interpreter.
    suggestions: list[str] = field(default_factory=list)  # type: ignore[operator]

    def __str__(self) -> str:
        text = f"{self.field}={self.value!r} is unknown"
        if self.suggestions:
            text += f" -- did you mean: {', '.join(self.suggestions)}?"
        return text


@dataclass(frozen=True)
class SearchResult:
    """The outcome of a search."""

    hits: list[SearchHit] = field(default_factory=list)
    total: int = 0
    facets: list[Facet] = field(default_factory=list)
    #: "Did you mean ...?" from the index -- populated when nothing was found.
    suggestions: list[str] = field(default_factory=list)
    #: Filters that could not be resolved and were therefore NOT sent. Non-empty
    #: means: the result is broader than requested.
    unresolved: list[UnresolvedFilter] = field(default_factory=list)
    #: Criteria the repository itself discarded.
    ignored: list[str] = field(default_factory=list)
    #: What is incomplete about the result -- a sub-query that failed, for
    #: instance. Non-empty means: something may be missing here.
    warnings: list[str] = field(default_factory=list)
    #: Whether ``total`` is only a lower bound. True when the result comes from
    #: several queries and not all of them report a total.
    total_is_lower_bound: bool = False
    raw: dict[str, Any] = field(default_factory=dict)

    def __len__(self) -> int:
        return len(self.hits)

    def __iter__(self):
        return iter(self.hits)


def _first(value: Any) -> str | None:
    """edu-sharing always returns property values as lists, even single ones."""
    if isinstance(value, list):
        return str(value[0]) if value else None
    return str(value) if value else None
