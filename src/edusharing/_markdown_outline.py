"""Indexed ownership and prose spans for a registry's Markdown headings."""

from __future__ import annotations

from bisect import bisect_left, bisect_right
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .skills_markdown import MarkdownSection


class _Outline:
    """Build the outline once; lookups never scan all preceding headings."""

    def __init__(self, text: str, sections: list[MarkdownSection], offsets: list[int]) -> None:
        self.text = text
        self.sections = sections
        self.named = [s for s in sections if s.level in (2, 3) and s.title]
        self._boundaries = sorted(offsets)
        self._headings = [s.heading_start for s in sections if s.level <= 3]
        self._owners: list[MarkdownSection | None] = []
        self._paths: dict[int, str] = {}
        self._parents: dict[int, MarkdownSection | None] = {}
        self._transparent: dict[int | None, list[MarkdownSection]] = {}
        self._index()

    def _index(self) -> None:
        stack: list[MarkdownSection] = []
        for section in self.sections:
            if section.level > 3:
                continue
            while stack and stack[-1].end <= section.heading_start:
                stack.pop()
            parent = stack[-1] if stack else None
            if section.level in (2, 3) and section.title:
                start = section.heading_start
                self._parents[start] = parent
                self._paths[start] = (f"{parent.title}/{section.title}"
                                      if parent else section.title)
                stack.append(section)
            elif section.level in (2, 3):
                key = parent.heading_start if parent else None
                self._transparent.setdefault(key, []).append(section)
            self._owners.append(stack[-1] if stack else None)

    def owner_at(self, offset: int) -> MarkdownSection | None:
        index = bisect_right(self._headings, offset) - 1
        owner = self._owners[index] if index >= 0 else None
        if owner is not None and owner.heading_start == offset:
            owner = self._parents[owner.heading_start]
        return owner if owner is not None and offset < owner.end else None

    def path_of(self, section: MarkdownSection) -> str:
        return self._paths[section.heading_start]

    def prose(self, start: int, end: int) -> str | None:
        boundary = bisect_left(self._boundaries, start)
        heading = bisect_right(self._headings, start)
        if boundary < len(self._boundaries):
            end = min(end, self._boundaries[boundary])
        if heading < len(self._headings):
            end = min(end, self._headings[heading])
        return self.text[start:end].strip() or None

    def instruction_of(self, section: MarkdownSection) -> str | None:
        pieces = [self.prose(section.body_start, section.end)] + [
            self.prose(u.body_start, u.end)
            for u in self._transparent.get(section.heading_start, [])
        ]
        return "\n\n".join(p for p in pieces if p) or None

    def general_instruction(self) -> str | None:
        first_named = self.named[0].heading_start if self.named else len(self.text)
        lead_start = next((s.body_start for s in self.sections
                           if s.level == 1 and s.heading_start < first_named), 0)
        pieces = [self.prose(lead_start, first_named)] + [
            self.prose(s.body_start, s.end) for s in self._transparent.get(None, [])
        ]
        return "\n\n".join(p for p in pieces if p) or None
