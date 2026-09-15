"""JSON snapshot format and validation; no file I/O or network operations."""

from __future__ import annotations

import math
import time
from typing import Any

from .errors import ValidationError
from .vocab_values import VocabularyValue

Cache = dict[tuple[str, str | None], tuple[float, list[VocabularyValue]]]


def context(repository: str, metadataset: str, query: str, scope: str) -> dict[str, str]:
    if not isinstance(scope, str) or not scope.strip():
        raise ValidationError("Snapshot scope must identify the visibility context, e.g. 'public'.")
    return {"repository": repository, "metadataset": metadataset, "query": query, "scope": scope}


def snapshot(cache: Cache, identity: dict[str, str], ttl: float) -> dict[str, Any]:
    now, monotonic = time.time(), time.monotonic()
    entries = [
        {"property": prop, "locale": locale, "loaded_at": now - (monotonic - loaded),
         "values": [{"value": v.uri, "label": v.label} for v in values]}
        for (prop, locale), (loaded, values) in cache.items()
        if monotonic - loaded < ttl
    ]
    return {"version": 1, "context": dict(identity), "entries": entries}


def restore(data: dict[str, Any], identity: dict[str, str], ttl: float) -> Cache:
    """Validate everything before returning a replacement, retaining original age."""
    if (not isinstance(data, dict) or data.get("version") != 1
            or data.get("context") != identity):
        raise ValidationError("Vocabulary snapshot version or context does not match.")
    entries = data.get("entries")
    if not isinstance(entries, list):
        raise ValidationError("Vocabulary snapshot entries must be a list.")
    now, monotonic = time.time(), time.monotonic()
    result: Cache = {}
    seen = set()
    for entry in entries:
        key, loaded_at, values = _entry(entry, now)
        if key in seen:
            raise ValidationError("Vocabulary snapshot contains a duplicate field/locale entry.")
        seen.add(key)
        age = now - loaded_at
        if age < ttl:
            result[key] = (monotonic - age, values)
    return result


def _entry(entry: Any, now: float) -> tuple[tuple[str, str | None], float, list[VocabularyValue]]:
    if not isinstance(entry, dict):
        raise ValidationError("Invalid vocabulary snapshot entry.")
    prop, locale, loaded = entry.get("property"), entry.get("locale"), entry.get("loaded_at")
    if (not isinstance(prop, str) or not prop.strip()
            or (locale is not None and not isinstance(locale, str))):
        raise ValidationError("Invalid vocabulary snapshot property/locale.")
    if (isinstance(loaded, bool) or not isinstance(loaded, (int, float))
            or not math.isfinite(loaded) or loaded < 0 or loaded > now):
        raise ValidationError("Invalid vocabulary snapshot loaded_at timestamp.")
    raw = entry.get("values")
    if not isinstance(raw, list):
        raise ValidationError("Vocabulary snapshot values must be a list.")
    values = []
    for item in raw:
        if (not isinstance(item, dict) or not isinstance(item.get("value"), str)
                or not item["value"] or not isinstance(item.get("label"), str)):
            raise ValidationError("Invalid vocabulary snapshot value/label pair.")
        values.append(VocabularyValue(item["value"], item["label"]))
    return (prop, locale), float(loaded), values
