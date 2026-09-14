"""One bounded collection context, reusing contents for its statistics."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from ..dto import first
from ..errors import EduSharingError, ValidationError
from ..skills import WLO_SKILLS, SkillConventions
from .contents import collection_contents
from .describe import describe
from .skills import skill_registry
from .tree import stats_from_contents

if TYPE_CHECKING:
    from ..repository import AsyncRepository


async def collection_context(
    repo: AsyncRepository, collection_id: str, *, limit: int = 20,
    properties: Sequence[str] = (), include_registry: bool = False,
    registry_conventions: SkillConventions = WLO_SKILLS, registry_context: str | None = None,
) -> dict[str, Any]:
    """Description, one contents page, statistics and optional approved skills.

    ``stats`` describes the returned sample; ``complete`` and contents totals
    disclose the limit. A failed contents/registry read is None plus a named
    ``failed`` entry. A missing collection raises. Compendium text comes only
    from the profile's optional property on the already fetched description.
    No background cache is kept; ``loaded_at`` lets the caller manage one.
    """
    if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
        raise ValidationError("limit must be a positive integer.")
    collection = await describe(repo, collection_id)
    prop = repo.metadata_profile.compendium_property
    answer: dict[str, Any] = {
        "collection": collection, "contents": None, "stats": None,
        "compendium": {"property": prop, "text": first(collection["properties"].get(prop))
                       if prop else None},
        "registry": None, "failed": [],
        "loaded_at": datetime.now(UTC).isoformat(),
    }
    try:
        page = await collection_contents(repo, collection_id, limit=limit, properties=properties)
        answer.update(contents=page, stats=stats_from_contents(page))
    except EduSharingError as exc:
        answer["failed"].append({"part": "contents", "reason": str(exc)})
    if include_registry:
        try:
            answer["registry"] = await skill_registry(
                repo, collection_id, conventions=registry_conventions, context=registry_context)
        except EduSharingError as exc:
            answer["failed"].append({"part": "registry", "reason": str(exc)})
    return answer
