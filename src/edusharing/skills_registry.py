"""The skill registry of a content collection -- which skills it has approved.

The reverse of the skill search. Not "which skills exist" but "which apply
here": an editorial team files ONE prompt document in the collection whose
``::: ki-skill`` blocks name the approved skills, grouped by headings into
working contexts. This module finds that document, reads it and turns it into
a catalogue.

Found through the collection's file listing, never through the search index.
The index and the node store are separate systems, and a record can fall out
of the former while sitting perfectly in the latter -- the MCP saw that happen
to a live collection on 2026-08-09. An approval list must not depend on it.

The document is uploaded content, exactly like a skill: data for a model to
weigh, never an instruction this library follows.
"""

from __future__ import annotations

import asyncio
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from .content import MAX_TEXT_BYTES, decode_text
from .dto import first, node_id_of, page_cut, page_total, title_of
from .errors import ContentTooLargeError, NotFoundError, PermissionDeniedError
from .skills import WLO_SKILLS, SkillConventions, registry_mark
from .skills_markdown import (
    RegistryContext,
    RegistryGeneral,
    SkillReference,
    layout_contexts,
    parse_blocks,
)
from .urls import path_segment

if TYPE_CHECKING:  # pragma: no cover
    from .repository import AsyncRepository

__all__ = ["RegistryEntry", "SkillRegistry", "load_registry",
           "REGISTRY_MAX", "REGISTRY_POOL", "REGISTRY_SCAN_MAX"]

#: File children read while looking for the registry. A content collection is
#: not a harvest folder; the registry is one document among its own material.
REGISTRY_SCAN_MAX = 50
#: Entries one answer carries. A curated approval list of sixty is legitimate;
#: an unbounded one must not turn one call into unbounded reads. Disclosed.
REGISTRY_MAX = 100
#: Heads resolved at once.
REGISTRY_POOL = 10
_MARKDOWN_MEDIATYPE = "file-markdown"


@dataclass(frozen=True)
class RegistryEntry:
    """One approved skill. Title and id come from the block; description and
    keywords from the record, when the heads were resolved."""

    node_id: str
    title: str
    description: str = ""
    keywords: list[str] = field(default_factory=list)
    #: The context it was declared under (``RegistryContext.path``), ``None``
    #: for the general part that applies always.
    context: str | None = None


@dataclass(frozen=True)
class SkillRegistry:
    """A collection's approval list, or why there is none."""

    collection_id: str
    #: ``""`` when no registry was found -- then ``reason`` says why.
    registry_id: str = ""
    registry_title: str = ""
    #: The document as stored, ``None`` when it could not be read.
    markdown: str | None = None
    entries: list[RegistryEntry] = field(default_factory=list)
    #: Blocks that name no readable record: ``{title, node_id}``.
    unresolved: list[dict[str, str]] = field(default_factory=list)
    contexts: list[RegistryContext] = field(default_factory=list)
    general: RegistryGeneral = field(default_factory=lambda: RegistryGeneral(None, []))
    #: How many candidates could have been the registry, when more than one.
    ambiguous: int = 0
    #: ``(listed, referenced)`` when the document declares more than one answer carries.
    truncated: tuple[int, int] | None = None
    contexts_truncated: tuple[int, int] | None = None
    #: ``""``, ``collection_not_found``, ``no_registry``, ``unreadable`` or
    #: ``too_large`` (the document exceeds ``MAX_TEXT_BYTES``; not downloaded).
    reason: str = ""
    #: ``all`` (no context asked), ``exact``, or ``missing`` -- a miss never
    #: narrows, so ``entries`` then holds everything and ``contexts`` says what
    #: exists.
    context_match: str = "all"
    #: ``(scanned, total)`` when the file listing was cut short -- then
    #: ``no_registry`` is not a finding of absence.
    #:
    #: ``total`` is what the repository stated. Where it stated none, it is
    #: what was **seen** instead -- one over the scan cap, and a lower bound,
    #: not the count. Reading it as the count would understate a collection
    #: that holds far more (review 2026-09-09).
    scan_truncated: tuple[int, int] | None = None


def _entries_of(
    with_id: list[tuple[SkillReference, str | None]],
    heads: dict[str, dict[str, Any] | None],
    *,
    resolve: bool,
) -> tuple[list[RegistryEntry], list[dict[str, str]]]:
    """The catalogue entries, plus the ones whose record could not be read.

    A block names a skill; the record says what it currently is. Both are
    needed, which is why this is a merge and not a mapping.
    """
    entries: list[RegistryEntry] = []
    unresolved: list[dict[str, str]] = []
    for block, path in with_id:
        head = heads[block.node_id]
        if resolve and head is None:
            unresolved.append({"title": block.title, "node_id": block.node_id})
            continue
        props = (head or {}).get("properties") or {}
        entries.append(RegistryEntry(
            node_id=block.node_id,
            # The record wins over the block: the document goes stale, the
            # record is what ``get`` will actually return.
            title=(head or {}).get("title") or block.title,
            description=first(props.get("cclom:general_description")) or "",
            keywords=[str(k) for k in (props.get("cclom:general_keyword") or [])],
            context=path,
        ))
    return entries, unresolved


def _by_context(
    entries: list[RegistryEntry],
    contexts: Sequence[RegistryContext],
    context: str | None,
) -> tuple[list[RegistryEntry], str]:
    """The entries under one heading, and whether the heading was found.

    ``"all"`` when nothing was asked for, ``"missing"`` for a heading this
    document does not have -- and then **everything** comes back, unnarrowed.
    A wrong heading must not look like an empty catalogue.

    The general part always travels along: those skills belong to every
    context, which is what makes them general.
    """
    if context is None:
        return entries, "all"
    wanted = context.strip().lower()
    exact = next((c for c in contexts if c.path.lower() == wanted), None)
    if exact is None:
        return entries, "missing"
    prefix = exact.path + "/"
    return [e for e in entries
            if e.context is None or e.context == exact.path
            or e.context.startswith(prefix)], "exact"


async def load_registry(
    repo: AsyncRepository,
    collection_id: str,
    *,
    context: str | None = None,
    resolve: bool = True,
    conventions: SkillConventions = WLO_SKILLS,
) -> SkillRegistry:
    """Find a collection's registry document and turn it into a catalogue.

    Args:
        repo: the connection.
        collection_id: the collection whose approval list is wanted.
        context: a heading of the document (``"Unterricht vorbereiten"`` or
            ``"Unterricht vorbereiten/Wochenplanung"``): only that group plus
            the general part. A name that does not match narrows nothing.
        resolve: read each named skill's record, for description and keywords.
            ``False`` is the cheap pass: titles and ids from the blocks only.
        conventions: which values mark a registry here.
    """
    seg = path_segment(collection_id)
    try:
        listing = await repo.raw.json(
            "GET", f"/node/v1/nodes/-home-/{seg}/children",
            # Eine Datei mehr als der Deckel: kommt sie an, liegt die Registry
            # vielleicht dahinter. Aus der genannten Gesamtzahl allein gelesen
            # war das nie so -- die Vorgabe war die gelieferte Zahl, und die
            # ist nie kleiner als sie selbst (Pruefung 09.09.2026).
            params={"filter": "files", "maxItems": REGISTRY_SCAN_MAX + 1,
                    "skipCount": 0,
                    "propertyFilter": ["-all-", conventions.type_property]},
        )
    except NotFoundError:
        return SkillRegistry(collection_id, reason="collection_not_found")
    except PermissionDeniedError:
        # A refusal is a finding about the collection; a transport or
        # server failure is not, and raises like everywhere else.
        return SkillRegistry(collection_id, reason="unreadable")

    roh = list(listing.get("nodes") or [])
    nodes = roh[:REGISTRY_SCAN_MAX]
    gesagt = page_total(listing, default=-1)
    # Ohne genannte Zahl das Gesehene: eine untere Schranke, und mit dem
    # Hinweis daneben liest sie sich auch als eine.
    total = gesagt if gesagt >= 0 else len(roh)
    scan_truncated = ((len(nodes), total)
                      if page_cut(roh, listing, REGISTRY_SCAN_MAX) else None)
    candidates = [n for n in nodes if _is_registry_candidate(n, conventions)]
    if not candidates:
        return SkillRegistry(collection_id, reason="no_registry", scan_truncated=scan_truncated)
    mark = registry_mark(conventions)
    marked = [n for n in candidates if mark.search(_name(n)) or mark.search(_title(n))]
    pool = marked or candidates
    # The smallest id: the same collection must resolve to the same registry
    # on every call, whatever order the repository listed the children in.
    chosen = min(pool, key=node_id_of)
    registry_id = node_id_of(chosen)
    base = SkillRegistry(
        collection_id, registry_id=registry_id, registry_title=_title(chosen),
        ambiguous=len(candidates) if len(candidates) > 1 else 0,
        scan_truncated=scan_truncated,
    )
    markdown, why = await _document_of(repo, chosen, registry_id)
    if markdown is None:
        return _with(base, reason=why)

    blocks = parse_blocks(markdown, conventions.block_kinds)
    layout = layout_contexts(markdown, blocks, skill_kind=conventions.skill_kind)
    skills = [(b, layout.paths[i]) for i, b in enumerate(blocks)
              if b.kind == conventions.skill_kind]
    capped = skills[:REGISTRY_MAX]
    truncated = (len(capped), len(skills)) if len(skills) > len(capped) else None

    ohne_id = [{"title": b.title, "node_id": ""} for b, _ in capped if not b.node_id]
    with_id = [(b, path) for b, path in capped if b.node_id]
    # One read per record: a skill filed under two contexts is two entries,
    # not two requests.
    unique = list(dict.fromkeys(b.node_id for b, _ in with_id))
    heads: dict[str, dict[str, Any] | None] = dict.fromkeys(unique)
    if resolve:
        heads = dict(zip(unique, await _read_heads(repo, unique), strict=True))
    entries, ungelesen = _entries_of(with_id, heads, resolve=resolve)
    unresolved = ohne_id + ungelesen
    entries, match = _by_context(entries, layout.contexts, context)

    return SkillRegistry(
        collection_id, registry_id=registry_id, registry_title=base.registry_title,
        markdown=markdown, entries=entries, unresolved=unresolved,
        contexts=layout.contexts, general=layout.general,
        ambiguous=base.ambiguous, truncated=truncated,
        contexts_truncated=layout.truncated, context_match=match,
        scan_truncated=scan_truncated,
    )


async def _document_of(
    repo: AsyncRepository, chosen: dict[str, Any], registry_id: str
) -> tuple[str | None, str]:
    """The registry Markdown, or ``None`` and why (``unreadable``, ``too_large``).

    The listing entry is a full record on this instance; only when it lacks
    what a download needs is the record read again. A candidate without a
    file is unreadable, not an error.
    """
    record = repo.nodes.wrap(chosen)
    try:
        if "content" not in chosen or not record.content.download_url:
            record = await repo.node(registry_id)
        if not record.content.has_content:
            return None, "unreadable"
        return decode_text(await record.content.download(max_bytes=MAX_TEXT_BYTES)), ""
    except (NotFoundError, PermissionDeniedError):
        return None, "unreadable"
    except ContentTooLargeError:
        return None, "too_large"


async def _read_heads(repo: AsyncRepository, ids: list[str]) -> list[dict[str, Any] | None]:
    """The records behind the blocks, a few at a time; a missing one is ``None``.

    ``REGISTRY_POOL`` is 10 and the transport's own pool defaults to 8, so at
    the default settings this gate never binds -- the transport's is stricter
    (audit PRF-3). It is not dead: it is this flow's own ceiling, and it holds
    for a caller who opens the transport wider, e.g.
    ``Repository(url, max_concurrency=32)``.
    """
    gate = asyncio.Semaphore(REGISTRY_POOL)

    async def one(node_id: str) -> dict[str, Any] | None:
        async with gate:
            try:
                return (await repo.node(node_id)).raw
            except (NotFoundError, PermissionDeniedError):
                return None

    return list(await asyncio.gather(*(one(i) for i in ids)))


def _is_registry_candidate(raw: dict[str, Any], conventions: SkillConventions) -> bool:
    props = raw.get("properties") or {}
    typed = conventions.registry_type in (props.get(conventions.type_property) or [])
    markdown = ((raw.get("mimetype") or "").lower() in conventions.markdown_mimetypes
                or raw.get("mediatype") == _MARKDOWN_MEDIATYPE)
    return typed and markdown


def _name(raw: dict[str, Any]) -> str:
    return first((raw.get("properties") or {}).get("cm:name")) or ""


def _title(raw: dict[str, Any]) -> str:
    return title_of(raw)


def _with(base: SkillRegistry, **changes: Any) -> SkillRegistry:
    return SkillRegistry(**{**base.__dict__, **changes})
