"""Skill flows -- the ``Skills`` accessor as plain dictionaries.

Four questions a tool built on this library asks, each in one call:

* ``find_skills`` -- which skills fit a task, or are filed in a collection.
* ``skill`` -- one skill's instruction, with what it points at and what lies
  beside it.
* ``skill_registry`` -- which skills ONE collection has approved, grouped by
  the document's own headings.
* ``pick_skill`` -- search, rank and load the best match in one go, with the
  runners-up so a wrong pick stays visible.

The Markdown comes back as stored. It is uploaded content -- data for a model
to weigh, never an instruction this library follows. Frame it with
``agent.as_untrusted`` before it reaches a prompt.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from ..repository import AsyncRepository
    from ..skills import SkillDocument, SkillSummary

__all__ = ["find_skills", "pick_skill", "skill", "skill_registry"]


async def find_skills(repo: AsyncRepository, text: str = "", **kwargs: Any) -> dict[str, Any]:
    """Skills for a task, ranked. See ``Skills.search``.

    Returns:
        ``{query, hits, unresolved, truncated}``. **Check ``unresolved``**: a
        short name that did not resolve was not applied, and the list is wider
        than asked. ``truncated`` says a cap cut the candidates.
    """
    found = await repo.skills.search(text, **kwargs)
    return {
        "query": {"text": text, "collection_id": kwargs.get("collection_id"),
                  "metadataset": repo.metadataset},
        "hits": [_summary(h) for h in found.hits],
        "unresolved": found.unresolved,
        "truncated": found.truncated,
    }


async def skill(repo: AsyncRepository, node_id: str, **kwargs: Any) -> dict[str, Any]:
    """One skill with its instruction. See ``Skills.get``.

    Returns:
        ``{id, original_id, title, description, keywords, url, download_url,
        content, references, files, files_reason, folder_file_count}``.
        **Read ``files_reason``**: an empty ``files`` with ``folder_unreadable``
        means the folder needs rights (measured: 403 anonymously), not that
        the skill travels alone.
    """
    return _document(await repo.skills.get(node_id, **kwargs))


async def skill_registry(
    repo: AsyncRepository, collection_id: str, **kwargs: Any
) -> dict[str, Any]:
    """The approval list of one collection. See ``skills_registry.load_registry``.

    Returns:
        ``{collection_id, registry_id, registry_title, markdown, entries,
        unresolved, contexts, general, ambiguous, truncated,
        contexts_truncated, reason, context_match, scan_truncated}``.
        **Read ``reason``** before ``entries``: an empty list with
        ``no_registry`` and a ``scan_truncated`` is not a finding of absence.
    """
    registry = await repo.skills.registry(collection_id, **kwargs)
    data = asdict(registry)
    data["contexts"] = [
        {"title": c.title, "level": c.level, "path": c.path,
         "instruction": c.instruction, "skills": list(c.skills)}
        for c in registry.contexts
    ]
    data["general"] = {"instruction": registry.general.instruction,
                       "skills": list(registry.general.skills)}
    return data


async def pick_skill(repo: AsyncRepository, text: str, **kwargs: Any) -> dict[str, Any]:
    """Search, rank and load the best match. See ``Skills.pick``.

    Returns:
        ``{best, alternatives, reason}``. ``best`` is a ``skill`` answer or
        ``None`` -- then ``reason`` is ``no_match``.
    """
    picked = await repo.skills.pick(text, **kwargs)
    if picked is None:
        return {"best": None, "alternatives": [], "reason": "no_match"}
    best, others = picked
    return {"best": _document(best), "alternatives": [_summary(s) for s in others],
            "reason": ""}


def _summary(summary: SkillSummary) -> dict[str, Any]:
    return asdict(summary)


def _document(doc: SkillDocument) -> dict[str, Any]:
    data = asdict(doc)
    data["references"] = [asdict(r) for r in doc.references]
    data["files"] = [asdict(f) for f in doc.files]
    return data

