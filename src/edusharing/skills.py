"""Skills: records whose content type says "instruction" and whose file is the
``SKILL.md``.

A skill is an ordinary ``ccm:io`` -- its metadata says what it is for, its
keywords when to reach for it, and its attached Markdown is the instruction a
model applies to a task. Nothing here is edu-sharing's API; it is how ONE
repository, WLO, files its skills. So everything that names a convention --
the content-type URIs, how a registry document gives itself away, the block
kinds inside the Markdown -- is a ``SkillConventions`` value with WLO's
defaults, and another repository passes its own. That stands next to E4 the
way ``metadataset="-default-"`` does: a value every caller can replace, not
one the library relies on.

Measured against staging on 2026-09-02, anonymously, with ``mds_oeh``:

* 34 skills answer to ``ccm:oeh_extendedType``; ``-default-`` refuses the
  criterion, so the metadata set has to be the one that knows it.
* A ``SKILL.md`` is read with ``download()``. ``/textContent`` is **empty**
  for Markdown (14 493 bytes against 0 characters) -- see ``NodeContent.text``.
* ``virtual:primaryparent_nodeid`` arrives with ``/metadata``; the folder
  behind it answered **403** anonymously. Companion files need rights, and
  that is a reason the document carries, not a failure of the fetch.
* A skill reached through a collection is a reference. Its folder hangs off
  the ORIGINAL, so the original is read first (one extra request).

Trust boundary: a skill is uploaded content. What comes back here is data for
a model to weigh, never an instruction this library follows -- wrap it with
``agent.as_untrusted`` before it reaches a prompt.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from .errors import PermissionDeniedError
from .flows.fields import resolve_vocabulary
from .flows.ranking import query_terms, term_matches
from .results import original_id_of
from .skills_markdown import SkillReference, parse_blocks
from .urls import path_segment

if TYPE_CHECKING:  # pragma: no cover
    from .nodes import Node
    from .repository import AsyncRepository
    from .skills_registry import SkillRegistry

__all__ = [
    "SkillConventions",
    "SkillDocument",
    "SkillFile",
    "SkillSearch",
    "SkillSummary",
    "Skills",
    "WLO_SKILLS",
    "SKILL_BUNDLE_MAX",
    "SKILL_SEARCH_PAGE",
    "SKILL_VISIT_MAX",
]

#: Hits fetched per repository-wide search, whatever ``limit`` says: the
#: ranking reads keywords, which the index's own score does not, and one page
#: costs the same request.
SKILL_SEARCH_PAGE = 50
#: Companion files listed before a folder counts as somebody's inbox. Measured
#: by the MCP: a real harvest folder held 484 files and took seconds to list.
SKILL_BUNDLE_MAX = 50
#: Collections one scoped walk may read -- a curated skills tree is small, and
#: a wrong id must not turn a lookup into a crawl.
SKILL_VISIT_MAX = 30
#: Levels below the given collection the walk follows: root -> skillsets -> skills.
SKILL_DEPTH_MAX = 2
_PAGE = 50


@dataclass(frozen=True)
class SkillConventions:
    """How one repository marks its skills. WLO's values are the defaults."""

    #: The property that carries the content type.
    type_property: str = "ccm:oeh_extendedType"
    #: The vocabulary entry that makes a record a skill. The full URI: the bare
    #: slug matches nothing in the index (measured by the MCP, 2026-08-08).
    skill_type: str = "http://w3id.org/openeduhub/vocabs/contentTypes/ai_skill"
    #: The entry a registry document carries -- a prompt document ABOUT skills.
    registry_type: str = "http://w3id.org/openeduhub/vocabs/contentTypes/ai_prompt"
    #: How a registry names itself, in ``cm:name`` or the title. A tie-break
    #: among candidates, never the condition: every upload is called SKILL.md.
    registry_mark: str = r"skill[\s_-]*(registry|catalogue|catalog|katalog)"
    #: What the repository reports for Markdown. ``text/x-web-markdown`` is
    #: edu-sharing's own spelling and the only one staging produces.
    markdown_mimetypes: frozenset[str] = frozenset(
        {"text/x-web-markdown", "text/markdown", "text/x-markdown"})
    #: The ``:::`` block kinds a document may carry.
    block_kinds: tuple[str, ...] = ("ki-skill", "wlo-material")


WLO_SKILLS = SkillConventions()


@dataclass(frozen=True)
class SkillSummary:
    """Enough to choose a skill -- not enough to act on it."""

    id: str
    #: The record behind a reference; equals ``id`` on an original.
    original_id: str
    title: str
    description: str
    keywords: list[str] = field(default_factory=list)
    url: str = ""
    download_url: str | None = None


@dataclass(frozen=True)
class SkillFile:
    """One file beside a skill's ``SKILL.md``."""

    id: str
    title: str
    mimetype: str | None
    size: int | None
    download_url: str | None


@dataclass(frozen=True)
class SkillDocument(SkillSummary):
    """A skill with its instruction and what belongs to it."""

    #: The Markdown as stored -- ``None`` when the record carries no file.
    content: str | None = None
    references: list[SkillReference] = field(default_factory=list)
    #: The other files in the skill's folder. Empty when there are none --
    #: or when ``files_reason`` says why they could not be listed.
    files: list[SkillFile] = field(default_factory=list)
    #: ``""``, ``no_folder``, ``folder_unreadable`` or ``too_many``.
    files_reason: str = ""
    #: Set with ``too_many``: how many files the folder holds.
    folder_file_count: int | None = None


@dataclass(frozen=True)
class SkillSearch:
    """What a skill search found."""

    hits: list[SkillSummary]
    #: Short-name values the vocabulary did not know -- not applied.
    unresolved: list[dict[str, Any]] = field(default_factory=list)
    #: Whether a cap cut the candidates short: the search page, or the walk.
    truncated: bool = False


class Skills:
    """Reached as ``repo.skills``."""

    def __init__(self, repo: AsyncRepository) -> None:
        self._repo = repo

    async def search(
        self,
        text: str = "",
        *,
        collection_id: str | None = None,
        include_subcollections: bool = False,
        limit: int = 10,
        conventions: SkillConventions = WLO_SKILLS,
        **aliases: str | list[str],
    ) -> SkillSearch:
        """Find skills -- repository-wide, or the ones filed in a collection.

        Repository-wide the content type travels as a search criterion, and
        the short names (``subject="Physik"``) with it. In a collection the
        listing takes no criteria, so both are checked against each record
        locally. A skill that is both an original and a reference into a
        collection comes back once -- as the original, the id a write may
        target.

        Ranked by relevance: a term in the title counts 3, in the keywords 2,
        in the description 1. Without ``text`` the catalogue keeps its order.

        Args:
            text: what the task is about. May be empty.
            collection_id: look only here instead of searching.
            include_subcollections: with ``collection_id``, walk two levels of
                sub-collections too (at most ``SKILL_VISIT_MAX`` collections).
            limit: how many to return.
            conventions: which values mark a skill here.
            **aliases: configured short names, resolved against the vocabulary.
        """
        wanted, unresolved = await resolve_vocabulary(self._repo, aliases)
        if collection_id:
            raw_nodes, truncated = await self._walk(
                collection_id, include_subcollections, conventions)
            candidates = [
                n for n in raw_nodes
                if _is(n, conventions.type_property, conventions.skill_type)
                and all(_carries(n, prop, values) for prop, values in wanted.items())
            ]
        else:
            result = await self._repo.search(
                text or None,
                filters={conventions.type_property: conventions.skill_type, **wanted},
                limit=SKILL_SEARCH_PAGE,
            )
            candidates = [hit.raw for hit in result.hits]
            truncated = result.total > len(result.hits)
        summaries = _dedupe_by_original([self._summary(n) for n in candidates])
        terms = query_terms(text)
        if terms:
            summaries.sort(key=lambda s: -_score(s, terms))
        return SkillSearch(hits=summaries[:limit], unresolved=unresolved, truncated=truncated)

    async def get(
        self, node_id: str, *, include_files: bool = True,
        conventions: SkillConventions = WLO_SKILLS,
    ) -> SkillDocument:
        """One skill with its instruction, its references and its companions.

        The content type is not re-checked: a search has applied it, and a
        repository where the field is not yet maintained would otherwise deny a
        record that is plainly there.

        Raises:
            NotFoundError: when no node carries this id.
            PermissionDeniedError: when it may not be read.
        """
        node = await self._repo.node(node_id)
        content: str | None = None
        if node.content.has_content:
            content = (await node.content.download()).decode("utf-8", errors="replace")
        files: list[SkillFile] = []
        reason, count = "", None
        if include_files:
            files, reason, count = await self._bundle(node)
        summary = self._summary(node.raw)
        return SkillDocument(
            **summary.__dict__,
            content=content,
            references=parse_blocks(content or "", conventions.block_kinds),
            files=files, files_reason=reason, folder_file_count=count,
        )

    async def registry(
        self, collection_id: str, *, context: str | None = None, resolve: bool = True,
        conventions: SkillConventions = WLO_SKILLS,
    ) -> SkillRegistry:
        """Which skills ONE collection has approved. See ``skills_registry``."""
        from .skills_registry import load_registry

        return await load_registry(
            self._repo, collection_id, context=context, resolve=resolve, conventions=conventions)

    async def pick(
        self, text: str, **kwargs: Any
    ) -> tuple[SkillDocument, list[SkillSummary]] | None:
        """The best match with its instruction, plus the runners-up.

        The others come along so a wrong pick stays visible to the caller.
        ``None`` when nothing matched at all.
        """
        kwargs.setdefault("limit", 5)
        conventions = kwargs.get("conventions", WLO_SKILLS)
        found = await self.search(text, **kwargs)
        if not found.hits:
            return None
        best = await self.get(found.hits[0].id, conventions=conventions)
        return best, found.hits[1:]

    # --- Internals --------------------------------------------------------

    def _summary(self, raw: dict[str, Any]) -> SkillSummary:
        props = raw.get("properties") or {}
        node_id = (raw.get("ref") or {}).get("id") or ""
        return SkillSummary(
            id=node_id,
            original_id=original_id_of(raw) or node_id,
            title=(raw.get("title") or _first(props.get("cclom:title"))
                   or _first(props.get("cm:name")) or ""),
            description=_first(props.get("cclom:general_description")) or "",
            keywords=[str(k) for k in (props.get("cclom:general_keyword") or [])],
            url=f"{self._repo.url}/components/render/{node_id}",
            download_url=raw.get("downloadUrl") or None,
        )

    async def _bundle(self, node: Node) -> tuple[list[SkillFile], str, int | None]:
        """The files beside a skill -- listed from the ORIGINAL's folder."""
        owner = node
        if node.original_id:
            owner = await self._repo.node(node.original_id)
        folder = owner.get("virtual:primaryparent_nodeid")
        if not folder:
            return [], "no_folder", None
        try:
            page = await self._repo.nodes.children(folder, limit=SKILL_BUNDLE_MAX + 1)
        except PermissionDeniedError:
            return [], "folder_unreadable", None
        if page.total > SKILL_BUNDLE_MAX:
            return [], "too_many", page.total
        skip = {node.id, owner.id}
        return [
            SkillFile(id=n.id, title=n.title or n.name, mimetype=n.content.mimetype,
                      size=n.content.size, download_url=n.content.download_url)
            for n in page.nodes if n.id not in skip
        ], "", None

    async def _walk(
        self, root: str, include_subcollections: bool, conventions: SkillConventions
    ) -> tuple[list[dict[str, Any]], bool]:
        """Breadth-first over a skills tree: the root's files, then its sub-collections'."""
        found: list[dict[str, Any]] = []
        visited = {root}
        level = [root]
        truncated = False
        for _depth in range(SKILL_DEPTH_MAX + 1):
            next_level: list[str] = []
            for collection_id in level:
                listing = await self._repo.raw.json(
                    "GET", f"/node/v1/nodes/-home-/{path_segment(collection_id)}/children",
                    params={"filter": "files", "maxItems": _PAGE, "skipCount": 0,
                            # Both, measured: the collection route returns the
                            # content type under -all-, the node route only
                            # when asked for it by name (MCP, 2026-08-08).
                            "propertyFilter": ["-all-", conventions.type_property]},
                )
                found.extend(listing.get("nodes") or [])
                if int((listing.get("pagination") or {}).get("total") or 0) > _PAGE:
                    truncated = True
                if not include_subcollections:
                    continue
                subs = await self._repo.raw.json(
                    "GET", f"/collection/v1/collections/-home-/{path_segment(collection_id)}"
                           "/children/collections",
                    params={"maxItems": _PAGE},
                )
                for sub in subs.get("collections") or []:
                    sub_id = (sub.get("ref") or {}).get("id") or ""
                    if not sub_id or sub_id in visited:
                        continue
                    if len(visited) >= SKILL_VISIT_MAX:
                        truncated = True
                        continue
                    visited.add(sub_id)
                    next_level.append(sub_id)
            if not next_level:
                break
            level = next_level
        return found, truncated


def _first(value: Any) -> str | None:
    if isinstance(value, list):
        return str(value[0]) if value else None
    return str(value) if value else None


def _is(raw: dict[str, Any], prop: str, value: str) -> bool:
    return value in ((raw.get("properties") or {}).get(prop) or [])


def _carries(raw: dict[str, Any], prop: str, values: list[str]) -> bool:
    stored = (raw.get("properties") or {}).get(prop) or []
    return any(v in stored for v in values)


def _dedupe_by_original(skills: list[SkillSummary]) -> list[SkillSummary]:
    """One entry per record: the original wins over a reference to it."""
    by_original: dict[str, SkillSummary] = {}
    for skill in skills:
        seen = by_original.get(skill.original_id)
        seen_is_reference = seen is not None and seen.id != seen.original_id
        if seen is None or (seen_is_reference and skill.id == skill.original_id):
            by_original[skill.original_id] = skill
    return list(by_original.values())


def _score(skill: SkillSummary, terms: list[str]) -> int:
    """Title before keywords before description: the title names what a skill
    does, the keywords when to reach for it, the description elaborates."""
    title, keywords, description = (
        skill.title.lower(), " ".join(skill.keywords).lower(), skill.description.lower())
    return sum(
        (3 if term_matches(t, title) else 0)
        + (2 if term_matches(t, keywords) else 0)
        + (1 if term_matches(t, description) else 0)
        for t in terms
    )


#: Precompiled once; the pattern is a convention and a parameter.
def registry_mark(conventions: SkillConventions) -> re.Pattern[str]:
    return re.compile(conventions.registry_mark, re.I)
