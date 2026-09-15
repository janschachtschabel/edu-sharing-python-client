"""Build a reviewable material draft using configured metadata and live catalogs."""

from __future__ import annotations

from dataclasses import asdict
from typing import TYPE_CHECKING, Any

from ..errors import EduSharingError, ValidationError
from ..fields import field_property, name_from_title
from ..nodes_write import fields_of
from .duplicates import find_by_url
from .text import DEFAULT_MAX_CHARS

if TYPE_CHECKING:
    from ..extraction import TextExtraction
    from ..repository import AsyncRepository


async def prepare_material(
    repo: AsyncRepository, url: str, *, title: str | None = None,
    name: str | None = None, description: str | None = None,
    keywords: list[str] | None = None, properties: dict[str, Any] | None = None,
    labels: dict[str, str | list[str]] | None = None, locale: str | None = None,
    extraction: TextExtraction | None = None, max_chars: int = DEFAULT_MAX_CHARS,
) -> dict[str, Any]:
    """Return a raw draft, duplicate status, validation gaps and optional text.

    No writes or LLM calls. Extraction runs only on an explicitly supplied
    service. Labels accept aliases/full properties; ambiguous labels are
    reported with candidates, never guessed. Use exact keys or raw properties.
    ``ready_to_create`` means the visible duplicate check and required-field
    check passed, not that the server will accept every property or permission.
    Pass the reviewed ``draft`` to ``add_material`` with a parent of your choice.
    """
    if not url.strip():
        raise ValidationError("prepare_material needs a non-empty URL.")
    if isinstance(max_chars, bool) or not isinstance(max_chars, int) or max_chars < 1:
        raise ValidationError("max_chars must be a positive integer.")
    direct = {key: value for key, value in {
        "url": url, "title": title, "description": description, "keywords": keywords,
    }.items() if value is not None}
    draft_props = fields_of(properties, direct, metadata_profile=repo.metadata_profile)
    label_props = {field_property(repo, key): value for key, value in (labels or {}).items()}
    if draft_props.keys() & label_props.keys():
        raise ValidationError("A property cannot be in both draft properties and labels.")
    resolved, unresolved = await _labels(repo, label_props, locale)
    draft_props.update(resolved)
    draft_name = name if name is not None else name_from_title(title) if title else ""
    duplicate = await _duplicate(repo, url)
    validation = await _validate(repo, draft_props, draft_name, locale)
    extracted = None
    warnings: list[str] = []
    if extraction is not None:
        try:
            extracted = asdict(await extraction.text_of(url, max_chars=max_chars))
        except EduSharingError as exc:
            warnings.append(f"extraction failed: {exc}")
    return {
        "draft": {"name": draft_name, "url": url, "properties": draft_props},
        "duplicate": duplicate, "unresolved": unresolved, "validation": validation,
        "extraction": extracted, "warnings": warnings,
        "ready_to_create": (duplicate["status"] == "absent" and not unresolved
                            and validation["checked"] and not validation["missing"]),
    }


async def _labels(
    repo: AsyncRepository, labels: dict[str, str | list[str]], locale: str | None,
) -> tuple[dict[str, list[str]], list[dict[str, Any]]]:
    resolved: dict[str, list[str]] = {}
    unresolved: list[dict[str, Any]] = []
    for prop, raw in labels.items():
        values = [raw] if isinstance(raw, str) else raw
        accepted: list[str] = []
        for value in values:
            candidates = await repo.vocab.resolve_all(prop, value, locale=locale)
            if len(candidates) == 1:
                accepted.extend(candidates)
            else:
                unresolved.append({"field": prop, "value": value, "candidates": candidates,
                                   "reason": "ambiguous" if candidates else "unknown"})
        if accepted:
            resolved[prop] = list(dict.fromkeys(accepted))
    return resolved, unresolved


async def _duplicate(repo: AsyncRepository, url: str) -> dict[str, Any]:
    try:
        node = await find_by_url(repo, url)
        return {"status": "exists" if node else "absent", "node": node, "reason": ""}
    except EduSharingError as exc:
        return {"status": "unknown", "node": None, "reason": str(exc)}


async def _validate(
    repo: AsyncRepository, properties: dict[str, list[str]], name: str, locale: str | None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "checked": False, "scope": "required_fields_only", "server_validation_required": True,
        "missing": [] if name.strip() else ["cm:name"], "missing_for_publish": [], "reason": "",
    }
    try:
        fields = await repo.metadata.fields(locale=locale)
    except EduSharingError as exc:
        return {**result, "reason": str(exc)}
    for widget in fields:
        prop = widget["id"]
        values = [name] if prop == "cm:name" else properties.get(prop, [])
        if any(str(value).strip() for value in values):
            continue
        required = widget.get("isRequired")
        if required == "mandatory":
            result["missing"].append(prop)
        elif required == "mandatoryForPublish":
            result["missing_for_publish"].append(prop)
    result["missing"] = list(dict.fromkeys(result["missing"]))
    result["missing_for_publish"] = list(dict.fromkeys(result["missing_for_publish"]))
    return {**result, "checked": True}
