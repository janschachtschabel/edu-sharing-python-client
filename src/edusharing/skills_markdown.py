"""What a skill document says about itself -- read without I/O.

An editorial team writes a skill's references and a registry's catalogue into
Markdown, as fenced blocks:

    ::: wlo-material
    ![Titel](…/preview?nodeId=<uuid>)
    [**Titel**](<Quelle>) — Lizenz: …
    :::

    ::: ki-skill
    [Titel](…/components/render/<uuid>)
    :::

and groups a registry's skills with headings. That is already a manifest; it
just sits inside prose. Parsing it here rather than leaving it to a model is
the point: a node id inside a URL inside a link inside a block is an extraction
task, and an extraction task has a failure rate. The block does not even say
which id belongs to what -- a material's title link points at the *source*, so
its id has to come from the preview image, while a skill's id is in the title
link. Getting that wrong yields a plausible id for the wrong thing.

Three pure functions, the rules those of the MCP (``skill-references.ts``,
``markdown-sections.ts``, ``registry-contexts.ts``), measured against staging on
2026-09-02: the live ``skill_registry.md`` carries seven ``::: ki-skill`` blocks
under three headings.

* ``parse_blocks`` -- the ``:::`` blocks, with kind, title, URL, node id and
  offset. An unclosed block matches nothing: a malformed document yields fewer
  references, never invented ones.
* ``parse_sections`` -- the ATX headings and the span of document under each.
  Setext headings and headings inside code fences are not headings.
* ``layout_contexts`` -- which named ``##``/``###`` a block sits under. A
  section without a title is *transparent*: its content belongs to the nearest
  named section above it, and failing that to the general part. Dropping
  untitled sections would have swallowed their skills without a trace.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

__all__ = [
    "ContextLayout",
    "MarkdownSection",
    "RegistryContext",
    "RegistryGeneral",
    "SkillReference",
    "REGISTRY_CONTEXT_MAX",
    "layout_contexts",
    "parse_blocks",
    "parse_sections",
]

#: Contexts one answer carries. Not a limit on what an editorial team may
#: write -- a document with more is reported as capped, never quietly cut. The
#: largest registry on staging had 28 sections, one per skill.
REGISTRY_CONTEXT_MAX = 50

DEFAULT_KINDS: tuple[str, ...] = ("ki-skill", "wlo-material")

_UUID = r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
#: The URL shapes that carry a node id. The FIRST occurrence in a block wins --
#: for a material that is the preview image, which is the record itself.
_NODE_ID = re.compile(r"(?:[?&]nodeId=|/components/render/)(" + _UUID + ")")
#: A Markdown link that is NOT an image: the first one is the title link.
_TITLE_LINK = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)\s]+)")
#: A backslash before ASCII punctuation means that character literally.
_ESCAPED = re.compile(r"\\([!-/:-@\[-`{-~])")
#: ``#`` to ``######``, at most three of indent, and a space after the hashes.
_HEADING = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+(.*?))?[ \t]*$")
_FENCE = re.compile(r"^ {0,3}(```|~~~)")


@dataclass(frozen=True)
class SkillReference:
    """One ``:::`` block: what the document points at."""

    #: ``ki-skill`` for another skill, ``wlo-material`` for teaching material.
    kind: str
    title: str
    #: The title link's target: the source for material, the render page for a skill.
    url: str
    #: Empty when the block carries no repository URL -- an external link only.
    node_id: str
    #: Where the opening fence sits in the document. The one coordinate shared
    #: with ``parse_sections``, which is how a block is assigned to a context.
    offset: int


@dataclass(frozen=True)
class MarkdownSection:
    """One ATX heading and the span of document that belongs under it."""

    #: 1 to 6, from the number of hashes.
    level: int
    #: The heading text, closing hashes removed. May be empty.
    title: str
    #: Offset of the ``#`` that opens the heading line.
    heading_start: int
    #: Offset just past the heading line -- where the body begins.
    body_start: int
    #: Offset of the next heading of the same or a higher level, else the end
    #: of the document. A lower level does not close a section: an H2 contains
    #: its H3s.
    end: int


@dataclass(frozen=True)
class RegistryContext:
    """A named group of skills, addressable by ``path``."""

    title: str
    #: 2 = context, 3 = sub-context.
    level: int
    #: ``"H2"`` or ``"H2/H3"`` -- the name a caller passes as ``context``.
    path: str
    #: What the editors wrote about this group, up to its first block.
    instruction: str | None
    #: Skill node ids declared here, in document order.
    skills: list[str] = field(default_factory=list)
    #: From the heading to the section's end -- an H2's range spans its H3s.
    range: tuple[int, int] = (0, 0)


@dataclass(frozen=True)
class RegistryGeneral:
    """What belongs to no named context and therefore applies always."""

    instruction: str | None
    skills: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ContextLayout:
    """How a registry document groups its blocks."""

    contexts: list[RegistryContext]
    general: RegistryGeneral
    #: Parallel to the blocks passed in: the path of each block's context, or
    #: ``None`` for the general part.
    paths: list[str | None]
    #: ``(listed, found)`` when the document outlines more contexts than listed.
    truncated: tuple[int, int] | None = None


def parse_blocks(text: str, kinds: tuple[str, ...] = DEFAULT_KINDS) -> list[SkillReference]:
    """The ``:::`` blocks of ``text``, in document order."""
    fence = re.compile(
        r"^:::[ \t]*(" + "|".join(re.escape(k) for k in kinds) + r")[ \t]*\r?$"
        r"(.*?)^:::[ \t]*\r?$",
        re.M | re.S,
    )
    refs: list[SkillReference] = []
    for m in fence.finditer(text):
        body = m.group(2)
        link = _TITLE_LINK.search(body)
        if not link:  # a block with no link references nothing
            continue
        node = _NODE_ID.search(body)
        refs.append(SkillReference(
            kind=m.group(1),
            title=_plain_title(link.group(1)),
            url=link.group(2),
            node_id=node.group(1) if node else "",
            offset=m.start(),
        ))
    return refs


def _plain_title(raw: str) -> str:
    """``**Titel**`` -> ``Titel``, then ``Skill\\_X`` -> ``Skill_X``.

    The order matters: unescaping first would turn ``\\*kein Stern\\*`` into
    ``*kein Stern*``, and the emphasis pass would strip the very asterisks the
    author marked as text.
    """
    stripped = re.sub(r"^\*{1,2}(.*?)\*{1,2}$", r"\1", raw, flags=re.S).strip()
    return _ESCAPED.sub(r"\1", stripped)


def parse_sections(text: str) -> list[MarkdownSection]:
    """The ATX headings of ``text``, each with the span under it."""
    heads: list[tuple[int, str, int, int]] = []  # level, title, start, body_start
    offset = 0
    in_fence: str | None = None
    for line in text.splitlines(keepends=True):
        stripped = line.rstrip("\r\n")
        fence = _FENCE.match(stripped)
        if fence:
            if in_fence is None:
                in_fence = fence.group(1)
            elif fence.group(1) == in_fence:
                in_fence = None
        elif in_fence is None:
            m = _HEADING.match(stripped)
            if m:
                title = (m.group(2) or "").rstrip("#").strip()
                heads.append((len(m.group(1)), title, offset, offset + len(line)))
        offset += len(line)

    sections: list[MarkdownSection] = []
    for i, (level, title, start, body_start) in enumerate(heads):
        end = len(text)
        for later_level, _, later_start, _ in heads[i + 1:]:
            if later_level <= level:
                end = later_start
                break
        sections.append(MarkdownSection(level, title, start, body_start, end))
    return sections


def layout_contexts(
    text: str, blocks: list[SkillReference], *, skill_kind: str = "ki-skill"
) -> ContextLayout:
    """Assign every block to the named ``##``/``###`` it sits under.

    ``skill_kind`` says which block kind names a skill -- only those fill the
    ``skills`` lists; every block gets a ``path``.
    """
    outline = _Outline(text, parse_sections(text), [b.offset for b in blocks])
    paths: list[str | None] = []
    skills_of: dict[int, list[str]] = {id(s): [] for s in outline.named}
    general_skills: list[str] = []
    for block in blocks:
        owner = outline.owner_at(block.offset)
        paths.append(outline.path_of(owner) if owner else None)
        if block.kind == skill_kind and block.node_id:
            (skills_of[id(owner)] if owner else general_skills).append(block.node_id)

    contexts = [
        RegistryContext(
            title=s.title, level=s.level, path=outline.path_of(s),
            instruction=outline.prose(s.body_start, s.end),
            skills=skills_of[id(s)], range=(s.heading_start, s.end),
        )
        for s in outline.named
    ]
    contexts, truncated = _capped(contexts)
    return ContextLayout(
        contexts=contexts,
        general=RegistryGeneral(instruction=outline.general_instruction(), skills=general_skills),
        paths=paths,
        truncated=truncated,
    )


class _Outline:
    """The headings of one document, and the questions the layout asks of them."""

    def __init__(self, text: str, sections: list[MarkdownSection], offsets: list[int]) -> None:
        self.text = text
        self.sections = sections
        self.named = [s for s in sections if s.level in (2, 3) and s.title]
        self._boundaries = sorted(offsets)
        self._headings = sorted(s.heading_start for s in sections)

    def owner_at(self, offset: int) -> MarkdownSection | None:
        # The last match in document order is the innermost: a named H2 spans
        # its H3s, so where both match, the H3 comes later.
        found = None
        for section in self.named:
            if section.heading_start < offset < section.end:
                found = section
        return found

    def path_of(self, section: MarkdownSection) -> str:
        if section.level == 3:
            parent = next((s for s in self.named if s.level == 2
                           and s.heading_start < section.heading_start < s.end), None)
            if parent is not None:
                return f"{parent.title}/{section.title}"
        return section.title

    def prose(self, start: int, end: int) -> str | None:
        # Up to the first block or heading inside the span: a block is a
        # catalogue entry, not instruction, and a sub-heading opens its own.
        cut = min([b for b in self._boundaries if start <= b < end]
                  + [h for h in self._headings if start < h < end] + [end])
        body = self.text[start:cut].strip()
        return body or None

    def general_instruction(self) -> str | None:
        """The prose before the first named context, plus that of untitled
        top-level sections -- each transparent, none dropped."""
        first_named = min((s.heading_start for s in self.named), default=len(self.text))
        lead_start = next((s.body_start for s in self.sections
                           if s.level == 1 and s.heading_start < first_named), 0)
        pieces = [self.prose(lead_start, first_named)] + [
            self.prose(s.body_start, s.end) for s in self.sections
            if s.level in (2, 3) and not s.title and self.owner_at(s.heading_start + 1) is None
        ]
        return "\n\n".join(p for p in pieces if p) or None


def _capped(
    contexts: list[RegistryContext],
) -> tuple[list[RegistryContext], tuple[int, int] | None]:
    """At most ``REGISTRY_CONTEXT_MAX`` -- and a note when the document had more."""
    if len(contexts) <= REGISTRY_CONTEXT_MAX:
        return contexts, None
    return contexts[:REGISTRY_CONTEXT_MAX], (REGISTRY_CONTEXT_MAX, len(contexts))
