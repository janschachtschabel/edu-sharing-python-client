"""Search: full text, filters given as labels, facets.

The call this library exists to make possible::

    await repo.search("Photosynthese", subject="Biologie")

Three things keep that repository-independent:

* **Filter values are resolved against THIS instance's metadata set** (see
  ``vocab``), not against a shipped table.
* **What cannot be resolved is reported, not dropped.** A silently discarded
  constraint returns hits nobody asked for -- more damaging than an empty result
  list, because it looks like an answer.
* **The field aliases are a convention, not an assumption.** ``subject`` points
  at ``ccm:taxonid`` because that is its name on the instances checked -- and it
  is overridable, because elsewhere it may differ.

Response shape measured (edu-sharing 11.0, staging, 2026-08-27): ``nodes``,
``pagination {total, from, count}``, ``facets``, ``suggests``, ``ignored``.
An **unknown** property, incidentally, does not land in ``ignored`` but ends the
request with ``400 DAOValidationException``.
"""

from __future__ import annotations

from typing import Any

from .errors import ValidationError
from .results import (
    Facet,
    FacetValue,
    SearchHit,
    SearchResult,
    UnresolvedFilter,
)
from .transport import Transport
from .urls import path_segment
from .vocab import DEFAULT_METADATASET, DEFAULT_QUERY, Vocabulary

__all__ = ["Search", "STANDARD_FIELD_ALIASES"]

#: Short names for commonly filtered properties.
#:
#: Derived from the intersection of two metadata sets (``mds`` and ``mds_oeh``,
#: staging 2026-08-27) and **checked individually against ngsearch** -- because
#: carrying a vocabulary and being filterable are two different things (see
#: ``_UNKNOWN_CRITERION``). ``ccm:educationaltypicalagerangecluster`` was
#: therefore left out: it has a vocabulary but is accepted as a criterion by
#: **neither** metadata set.
#:
#: This is a **convention**, not a universal: which properties an instance
#: carries, and which of them are filterable, is decided by its metadata set.
#: ``field_aliases`` sets a mapping of your own.
STANDARD_FIELD_ALIASES: dict[str, str] = {
    "subject": "ccm:taxonid",
    "level": "ccm:educationalcontext",
    "type": "ccm:oeh_lrt_aggregated",
    "difficulty": "ccm:educationaldifficulty",
    "license": "license",
}

#: How to recognise the answer to a criterion this metadata set does not know.
#: Measured: ``ccm:taxonid`` is filterable in ``mds_oeh`` and not in
#: ``-default-``, although both carry a vocabulary for it.
_UNKNOWN_CRITERION = "could not find parameter"

DEFAULT_LIMIT = 10
DEFAULT_FACET_LIMIT = 20

#: ngsearch's full-text criterion.
SEARCHWORD = "ngsearchword"


class Search:
    """Search against one metadata set.

    Args:
        transport: the connection to the repository.
        vocab: resolves filter labels against the same instance.
        metadataset: the metadata set searched against.
        query: query name, ``ngsearch`` by convention.
        field_aliases: short names for properties. ``None`` uses
            ``STANDARD_FIELD_ALIASES``.
    """

    def __init__(
        self,
        transport: Transport,
        vocab: Vocabulary,
        *,
        metadataset: str = DEFAULT_METADATASET,
        query: str = DEFAULT_QUERY,
        field_aliases: dict[str, str] | None = None,
    ) -> None:
        self._transport = transport
        self._vocab = vocab
        self.metadataset = metadataset
        self.query = query
        self.field_aliases = (
            STANDARD_FIELD_ALIASES if field_aliases is None else field_aliases
        )

    async def search(
        self,
        text: str | None = None,
        *,
        filters: dict[str, str | list[str]] | None = None,
        facets: list[str] | None = None,
        facet_limit: int = DEFAULT_FACET_LIMIT,
        limit: int = DEFAULT_LIMIT,
        offset: int = 0,
        content_type: str = "FILES",
        **aliases: str | list[str],
    ) -> SearchResult:
        """Search for material.

        Args:
            text: full-text term. Omittable when only filtering.
            filters: ``{property: label}`` -- labels are resolved, URIs taken
                unchanged.
            facets: properties to count server-side.
            facet_limit: how many values per facet.
            limit, offset: page size and starting point.
            content_type: ``FILES`` (default) or ``FILES_AND_FOLDERS``. This
                query does **not** return collections -- there is a separate one
                for those.
            **aliases: short names from ``field_aliases``, e.g.
                ``subject="Biologie"``.

        Returns:
            A ``SearchResult``. Check its ``unresolved``: if it is non-empty,
            less was constrained than requested.

        Raises:
            ValidationError: for a short name ``field_aliases`` does not know --
                a typo must not pass as "no constraint".
        """
        criteria, unresolved = await self._criteria(self._fields(filters, aliases))
        if text:
            criteria.insert(0, {"property": SEARCHWORD, "values": [text]})

        body: dict[str, Any] = {
            "criteria": criteria,
            # Without this flag a typo yields "no hits" and nothing to build a
            # second attempt from.
            "returnSuggestions": True,
        }
        if facets:
            body["facets"] = [{"property": p} for p in facets]
            body["facetLimit"] = facet_limit
            body["facetMinCount"] = 1

        try:
            response = await self._transport.json(
                "POST",
                f"/search/v1/queries/-home-/{path_segment(self.metadataset)}/{path_segment(self.query)}",
                idempotent=True,
                params={
                    "contentType": content_type,
                    "maxItems": limit,
                    "skipCount": offset,
                    "propertyFilter": "-all-",
                },
                json=body,
            )
        except ValidationError as exc:
            raise self._explain(exc) from exc
        return self._result(response, unresolved)

    # --- Internals --------------------------------------------------------

    def _fields(
        self,
        filters: dict[str, str | list[str]] | None,
        aliases: dict[str, str | list[str]],
    ) -> dict[str, str | list[str]]:
        """Merge explicitly named properties and short names.

        Raises:
            ValidationError: for an unknown short name. Ignoring it silently
                would mean searching without the intended constraint and
                presenting the result as hits anyway.
        """
        fields = dict(filters or {})
        for name, value in aliases.items():
            prop = self.field_aliases.get(name)
            if prop is None:
                known = ", ".join(sorted(self.field_aliases)) or "(none)"
                raise ValidationError(
                    f"Unknown search field {name!r}. Known are: {known}. "
                    "A property can also be given directly: "
                    "filters={'ccm:...': 'value'}."
                )
            fields[prop] = value
        return fields

    def _explain(self, exc: ValidationError) -> ValidationError:
        """Add to the server message what it leaves open.

        "Could not find parameter X in the query ngsearch" does not say that the
        cause is the chosen metadata set -- and that is exactly what one puzzles
        over for a long time, since the property demonstrably exists and even
        carries a vocabulary.

        Other validation errors pass through unchanged.
        """
        if _UNKNOWN_CRITERION not in str(exc).lower():
            return exc
        return ValidationError(
            f"{exc}\n"
            f"The metadata set {self.metadataset!r} does not accept this criterion "
            f"in the query {self.query!r}. That the property exists and even "
            f"carries a vocabulary says nothing about it -- filterability is a "
            f"property of the metadata set. Which ones the instance carries is "
            f"shown by GET /mds/v1/metadatasets/-home-; the choice is made via "
            f"AsyncRepository(url, metadataset=...).",
            status=exc.status,
            url=exc.url,
            error_class=exc.error_class,
            stacktrace=exc.stacktrace,
        )

    async def _criteria(
        self, filters: dict[str, str | list[str]]
    ) -> tuple[list[dict[str, Any]], list[UnresolvedFilter]]:
        """Resolve filter labels. What cannot be resolved is reported, not sent."""
        criteria: list[dict[str, Any]] = []
        unresolved: list[UnresolvedFilter] = []

        for prop, raw in filters.items():
            values = [raw] if isinstance(raw, str) else list(raw)
            resolved: list[str] = []
            for value in values:
                # All of them: one label can sit in two vocabularies, and
                # filtering on one of them answers half the question while
                # looking like the whole one. See ``Vocabulary.resolve_all``.
                uris = await self._vocab.resolve_all(prop, value)
                if uris:
                    resolved.extend(uris)
                else:
                    unresolved.append(
                        UnresolvedFilter(
                            field=prop,
                            value=value,
                            suggestions=[
                                v.label for v in await self._vocab.suggest(prop, value)
                            ][:5],
                        )
                    )
            if resolved:
                criteria.append({"property": prop, "values": resolved})

        return criteria, unresolved

    def _result(
        self, response: dict[str, Any], unresolved: list[UnresolvedFilter]
    ) -> SearchResult:
        base = self._transport.repository_url
        page = response.get("pagination") or {}
        return SearchResult(
            hits=[
                SearchHit.from_node(n, base) for n in (response.get("nodes") or [])
            ],
            total=int(page.get("total") or 0),
            facets=[
                Facet(
                    property=f.get("property") or "",
                    values=[
                        FacetValue(value=v.get("value") or "", count=int(v.get("count") or 0))
                        for v in (f.get("values") or [])
                    ],
                    other_count=int(f.get("sumOtherDocCount") or 0),
                )
                for f in (response.get("facets") or [])
            ],
            suggestions=[
                s.get("text") for s in (response.get("suggests") or []) if s.get("text")
            ],
            unresolved=unresolved,
            ignored=list(response.get("ignored") or []),
            raw=response,
        )

    def __repr__(self) -> str:
        return f"Search(metadataset={self.metadataset!r}, query={self.query!r})"
