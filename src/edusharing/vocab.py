"""Vocabulary values -- labels instead of URIs, asked for rather than shipped.

This is where it is decided whether the library is tied to one instance. A
built-in subject directory would be convenient and would be wrong for every
repository but one. So it asks::

    POST /mds/v1/metadatasets/{repo}/{mds}/values
    {"valueParameters": {"query": "ngsearch", "property": "ccm:taxonid",
                         "pattern": ""}, "criteria": []}

Two quirks, both measured (edu-sharing 11.0, staging, 2026-08-27):

* **``pattern: ""`` lists everything.** The obvious ``"-all-"`` returns an empty
  list -- silently, so nothing points at the mistake.
* **The response shape deviates from the OpenAPI specification.** That declares
  ``MdsValue {id, caption}``; what arrives is ``{key, displayString}``. Anyone
  relying on the generated layer here reads empty fields.

Resolution is **exact**, never fuzzy. The WLO MCP demonstrates where fuzzy
guessing leads: there ``bildungsinhalte`` resolves to **Bild** (image) and turns
a topic search into an image search. A ``None`` plus a suggestion from
``suggest()`` is more honest.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

from .transport import Transport
from .urls import path_segment

__all__ = ["VocabularyValue", "Vocabulary"]

DEFAULT_METADATASET = "-default-"
DEFAULT_QUERY = "ngsearch"

#: ``pattern`` meaning "all values" -- see the module docstring.
_ALL = ""


@dataclass(frozen=True, slots=True)
class VocabularyValue:
    """One value from a controlled vocabulary."""

    #: The value the repository filters on (usually a SKOS URI).
    uri: str
    #: The human-readable form in the requested language.
    label: str

    def __str__(self) -> str:
        return self.label


def _is_uri(value: str) -> bool:
    return value.startswith(("http://", "https://"))


class Vocabulary:
    """Vocabulary access for one metadata set.

    Args:
        transport: the connection to the repository.
        metadataset: the metadata set resolved against. ``-default-`` is
            whichever the instance nominates.
        query: the query context the property is defined in. ``ngsearch`` is the
            edu-sharing convention; the name does **not** appear in the MDS and
            can therefore only be set, not discovered.
    """

    def __init__(
        self,
        transport: Transport,
        *,
        metadataset: str = DEFAULT_METADATASET,
        query: str = DEFAULT_QUERY,
    ) -> None:
        self._transport = transport
        self.metadataset = metadataset
        self.query = query
        self._cache: dict[tuple[str, str | None], list[VocabularyValue]] = {}
        self._locks: dict[tuple[str, str | None], asyncio.Lock] = {}

    # --- Values -----------------------------------------------------------

    async def values(
        self, prop: str, *, locale: str | None = None
    ) -> list[VocabularyValue]:
        """Every value this instance knows for ``prop``.

        The result is cached -- vocabularies change rarely, and the same
        property is needed many times over during a fan-out. A failure does not
        enter the cache.

        Args:
            prop: property name, e.g. ``ccm:taxonid``.
            locale: label language, e.g. ``en_EN``. Cached separately.

        Returns:
            An empty list when the property has no vocabulary.
        """
        key = (prop, locale)
        if key in self._cache:
            return self._cache[key]

        # Without a lock, concurrent access loads the same vocabulary once per
        # caller -- during a fan-out, many times over.
        lock = self._locks.setdefault(key, asyncio.Lock())
        async with lock:
            if key in self._cache:
                return self._cache[key]
            values = await self._fetch(prop, _ALL, locale)
            self._cache[key] = values
            return values

    async def suggest(
        self, prop: str, text: str, *, locale: str | None = None
    ) -> list[VocabularyValue]:
        """Values whose label **contains** ``text`` -- a server-side search.

        Substring, not prefix: measured, ``"ysik"`` returns Physik, Atomphysik
        and Kernphysik. Anyone building a typeahead on it also gets hits that do
        not begin with the input -- usually desirable, but worth knowing.

        Not cached: every input is its own request, and a cache over that would
        only fill memory.
        """
        return await self._fetch(prop, text, locale)

    async def resolve(
        self, prop: str, label_or_uri: str, *, locale: str | None = None
    ) -> str | None:
        """Translate a label into the value the repository filters on.

        Args:
            label_or_uri: a label (``"Biologie"``) or already a URI -- the
                latter passes through unchanged, without a request.

        Returns:
            The filter value, or ``None`` when the label is unknown. No fuzzy
            matching: a wrongly guessed value narrows the search to something
            nobody asked for. For a follow-up question, ``suggest()`` provides
            candidates.
        """
        value = label_or_uri.strip()
        if _is_uri(value):
            return value
        wanted = value.casefold()
        for entry in await self.values(prop, locale=locale):
            if entry.label.strip().casefold() == wanted:
                return entry.uri
        return None

    def clear_cache(self) -> None:
        """Discard the cached vocabularies."""
        self._cache.clear()

    # --- Internals --------------------------------------------------------

    async def _fetch(
        self, prop: str, pattern: str, locale: str | None
    ) -> list[VocabularyValue]:
        response = await self._transport.json(
            "POST",
            f"/mds/v1/metadatasets/-home-/{path_segment(self.metadataset)}/values",
            json={
                "valueParameters": {
                    "query": self.query,
                    "property": prop,
                    "pattern": pattern,
                },
                # Required field, but it does not narrow: measured, the query
                # returns the same 416 values with and without criteria. It is a
                # vocabulary listing, not a context-dependent suggestion list.
                "criteria": [],
            },
            headers={"locale": locale} if locale else None,
        )
        return [
            VocabularyValue(uri=entry["key"], label=entry.get("displayString") or "")
            for entry in (response.get("values") or [])
            if entry.get("key")
        ]

    def __repr__(self) -> str:
        return f"Vocabulary(metadataset={self.metadataset!r}, query={self.query!r})"
