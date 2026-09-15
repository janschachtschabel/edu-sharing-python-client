"""Load and reuse the connected repository's actual metadata definition."""

from __future__ import annotations

import asyncio
import copy
import time
from typing import Any

from .errors import ValidationError, at_least
from .transport import Transport
from .urls import path_segment
from .vocab import DEFAULT_CACHE_SECONDS, DEFAULT_METADATASET

__all__ = ["MetadataCatalog"]


class MetadataCatalog:
    """A cached MDS definition, separate from the external MetadataAgent service.

    Definitions describe widgets and presentation, not guaranteed query support.
    Caller changes to returned dictionaries never modify the cached definition.
    """

    def __init__(self, transport: Transport, *, metadataset: str = DEFAULT_METADATASET,
                 cache_seconds: float = DEFAULT_CACHE_SECONDS) -> None:
        at_least("cache_seconds", cache_seconds, 0)
        self._transport = transport
        self.metadataset = metadataset
        self.cache_seconds = cache_seconds
        self._cache: dict[str | None, tuple[float, dict[str, Any]]] = {}
        self._locks: dict[str | None, asyncio.Lock] = {}
        self._generation = 0

    async def load(self, *, locale: str | None = None, refresh: bool = False) -> dict[str, Any]:
        """Return the full MDS as independent JSON data.

        locale selects the API language and a separate cache entry. refresh
        forces a new read. Network errors and malformed responses are not cached.
        """
        lock = self._locks.setdefault(locale, asyncio.Lock())
        async with lock:
            entry = self._cache.get(locale)
            if entry and not refresh and time.monotonic() - entry[0] < self.cache_seconds:
                return copy.deepcopy(entry[1])
            generation = self._generation
            response = await self._transport.json(
                "GET", f"/mds/v1/metadatasets/-home-/{path_segment(self.metadataset)}",
                headers={"locale": locale} if locale else None,
            )
            if not isinstance(response, dict) or not isinstance(response.get("widgets"), list):
                raise ValidationError("The metadata endpoint did not return an MDS with widgets.")
            if generation == self._generation:
                self._cache[locale] = (time.monotonic(), copy.deepcopy(response))
            return response

    async def fields(self, *, locale: str | None = None,
                     refresh: bool = False) -> list[dict[str, Any]]:
        """Return the named widgets as supplied by the MDS, without inferred filterability.

        Each entry preserves id, captions, values and declared requirements.
        Subwidget references remain references; this does not invent new fields.
        """
        definition = await self.load(locale=locale, refresh=refresh)
        return [widget for widget in definition["widgets"]
                if isinstance(widget, dict) and widget.get("id")]

    def clear_cache(self) -> None:
        """Invalidate all languages; in-flight reads cannot repopulate the old cache."""
        self._generation += 1
        self._cache.clear()
        self._locks.clear()

    def __repr__(self) -> str:
        return f"MetadataCatalog(metadataset={self.metadataset!r})"
