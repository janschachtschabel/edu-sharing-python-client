"""Turning one query into a few variants worth asking.

edu-sharing ANDs every word of a query. That makes one class of word
catastrophic: words describing the *shape* of a request rather than its subject.
They appear in almost no record, so a single one empties the result set.
Measured against staging on 2026-08-27:

    "Bruchrechnung"                                 1591 hits
    "Ich suche ein Arbeitsblatt zur Bruchrechnung"      0 hits

A language model phrases exactly like the second line. Without the ``topic``
variant it reports "nothing found" about a subject with fifteen hundred records,
and a person believes it.

Every variant costs one request, so the set is small and capped. Ported from
``wlo-mcp-sc`` (Apache-2.0), reduced to full-text variants: the property-scoped
variants there (``cclom:title``, ``cclom:general_keyword``) would have to bypass
this library's vocabulary resolution, and the measured effect comes from
``topic`` regardless.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .language import GERMAN, LanguageProfile

__all__ = ["MAX_VARIANTS", "QueryVariant", "expand_query"]

#: Upper bound on parallel requests per search. Variants are sorted by weight
#: and trimmed, so ``full`` always survives.
MAX_VARIANTS = 5


@dataclass(frozen=True)
class QueryVariant:
    """One query to actually send.

    Args:
        label: what this variant is, for logging and debugging.
        weight: how much its ranking counts in the fusion. The original
            phrasing weighs most; a synonym guess weighs least.
        text: the full-text term to search for.
    """

    label: str
    weight: float
    text: str


def _synonym_variants(query_lower: str, profile: LanguageProfile) -> list[str]:
    """Replace known terms with their alternatives, at word boundaries only.

    The boundary check is not cosmetic: a plain replace turns "klimawandel" into
    "klimawandelwandel" and "geographie" into "geographiegrafie".
    """
    out: list[str] = []
    for term, alternatives in profile.synonyms.items():
        pattern = re.compile(
            rf"(?<![^\W_]){re.escape(term)}(?![^\W_])", re.IGNORECASE | re.UNICODE
        )
        if not pattern.search(query_lower):
            continue
        for alternative in alternatives:
            replaced = pattern.sub(alternative, query_lower, count=1)
            if replaced != query_lower:
                out.append(replaced)
    return out


def expand_query(
    query: str, profile: LanguageProfile = GERMAN
) -> list[QueryVariant]:
    """Build the variants worth asking for one query.

    Returns:
        At most ``MAX_VARIANTS`` variants, heaviest first. Empty for an empty
        query. A profile without word lists yields just the original query --
        nothing is assumed about the language.
    """
    trimmed = query.strip()
    if not trimmed:
        return []

    variants = [QueryVariant("full", 1.0, trimmed)]
    seen = {trimmed.lower()}

    def add(label: str, weight: float, text: str) -> None:
        if text and text.lower() not in seen:
            seen.add(text.lower())
            variants.append(QueryVariant(label, weight, text))

    words = trimmed.lower().split()
    without_stopwords = [w for w in words if w not in profile.stopwords]
    topic_words = [w for w in without_stopwords if w not in profile.framing]

    # Only when framing words were actually removed AND something is left. An
    # unchanged query would repeat `full`; an emptied one would match everything,
    # which is a worse answer than the honest handful of hits.
    if topic_words and len(topic_words) < len(without_stopwords):
        add("topic", 0.92, " ".join(topic_words))

    if without_stopwords and len(without_stopwords) < len(words):
        add("nostop", 0.85, " ".join(without_stopwords))

    for text in _synonym_variants(trimmed.lower(), profile):
        add("syn", 0.6, text)

    variants.sort(key=lambda v: v.weight, reverse=True)
    return variants[:MAX_VARIANTS]
