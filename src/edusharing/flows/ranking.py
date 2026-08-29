"""Scoring hits for the reordering of search results.

Ported from ``wlo-mcp-sc`` (Apache-2.0, same licence as this library), where the
rules were measured against a running instance. Two things were changed on the
way, and both follow from this library being profile-independent:

* The word lists are a parameter (``LanguageProfile``), not a constant.
* The metadata-quality signals read the **configured short names**, not fixed
  WLO properties. An instance with a different metadata set scores its own
  fields; nothing here knows what ``ccm:taxonid`` is.

Why reorder at all: the repository ranks by its own index score, which does not
know that a title match beats a body match, and does not know that a record
carrying subject, level and a free licence is more usable in a classroom than a
bare one. Where the repository's order is already good, reranking barely moves
it -- the cost is one larger fetch, not a worse result.

Everything here is a pure function of the record and the query. The position a
record held in the repository's answer is deliberately not an input: that order
is measurably unstable, so it would make the ranking depend on which candidates
happened to arrive first. See ``rerank.py``.
"""

from __future__ import annotations

import re
from typing import Any

from ..results import SearchHit
from .language import GERMAN, LanguageProfile

__all__ = [
    "query_terms",
    "score_hit",
    "term_matches",
]

#: Up to this length a term must match at a word start; beyond it, anywhere.
#:
#: Measured in wlo-mcp-sc on 2026-08-03: the query "IT" put "s-IT-ting",
#: "Maur-IT-ius", "Pol-IT-ik" and "C-IT-izenship" in the top five. A longer term
#: keeps plain substring behaviour, which German compounds need -- "Rechnung"
#: belongs inside "Bruchrechnung".
SHORT_TERM_MAX = 3

_WORD_CHAR = re.compile(r"[^\W_]", re.UNICODE)


def term_matches(term: str, text: str) -> bool:
    """Does ``term`` occur in ``text`` as a signal rather than by accident?

    Both are expected lowercase.

    A plain substring test is right for German: "Rechnung" belongs inside
    "Bruchrechnung", "Mittelalter" inside "mittelalterlichen". For a short term
    the same test is mostly accident, so a short term must sit at a word start.
    Only the start is checked -- requiring a word end too would reject exactly
    the compounds this is meant to keep.
    """
    if not term:
        return False
    if len(term) > SHORT_TERM_MAX:
        return term in text

    start = 0
    while True:
        at = text.find(term, start)
        if at == -1:
            return False
        if at == 0 or not _WORD_CHAR.match(text[at - 1]):
            return True
        start = at + 1


def query_terms(query: str, profile: LanguageProfile = GERMAN) -> list[str]:
    """The words of a query that can carry a signal.

    Drops stopwords and single characters. A stopword is not merely useless: in
    German it sits inside ordinary words, so leaving it in creates matches that
    are not there. Measured in wlo-mcp-sc over a 60-node pool: "Bruchrechnung"
    matched 0 nodes and "die Bruchrechnung" matched 43 -- one article turned a
    correct rejection into a 72 % pass rate.
    """
    return [
        term
        for term in query.lower().split()
        if len(term) >= 2 and term not in profile.stopwords
    ]


def _text_of(hit: SearchHit) -> tuple[str, str, list[str]]:
    """Title, description and keywords of a hit, lowercased."""
    properties: dict[str, Any] = hit.raw.get("properties") or {}
    keywords = [str(k).lower() for k in (properties.get("cclom:general_keyword") or [])]
    return hit.title.lower(), (hit.description or "").lower(), keywords


def _title_score(title: str, query_lower: str, terms: list[str]) -> int:
    """The title, which is what a reader sees first and weighs heaviest.

    The whole query in the title beats the terms individually, and an exact
    title beats a title that merely contains it.
    """
    if term_matches(query_lower, title):
        if title == query_lower:
            return 50
        if title.startswith(query_lower):
            return 40
        return 30

    score = sum(8 for term in terms if term_matches(term, title))
    if len(terms) > 1 and all(term_matches(t, title) for t in terms):
        score += 12
    return score


def _keyword_score(keywords: list[str], terms: list[str]) -> int:
    """The keywords, where a whole-value hit is worth more than a substring.

    A keyword ``bruchrechnung`` answers the term; finding those letters inside
    ``bruchrechnung-uebungsblatt`` is weaker evidence, so it scores less.
    """
    joined = " ".join(keywords)
    score = 0
    whole_hits = 0
    for term in terms:
        if term in keywords:
            score += 10
            whole_hits += 1
        elif term_matches(term, joined):
            score += 5
    if len(terms) > 1 and whole_hits == len(terms):
        score += 10
    return score


def _description_score(description: str, query_lower: str, terms: list[str]) -> int:
    """The description, which supports a hit rather than making it."""
    if term_matches(query_lower, description):
        return 8
    return sum(3 for term in terms if term_matches(term, description))


def _off_topic_penalty(title: str, keywords: list[str], terms: list[str]) -> int:
    """Minus 20 when neither title nor keywords mention the query at all.

    Without this, a richly tagged record that does not mention the subject
    outranks a plain one that does.
    """
    joined = " ".join(keywords)
    mentioned = any(
        term_matches(t, title) or term_matches(t, joined) for t in terms
    )
    return 0 if mentioned else -20


def _text_score(hit: SearchHit, query: str, terms: list[str]) -> int:
    """How well the hit's text answers the query.

    Four questions, each with its own weight: does the title say it, do the
    keywords, does the description -- and if none of the first two do, the
    record is about something else.
    """
    title, description, keywords = _text_of(hit)
    query_lower = query.lower().strip()
    return (
        _title_score(title, query_lower, terms)
        + _keyword_score(keywords, terms)
        + _description_score(description, query_lower, terms)
        + _off_topic_penalty(title, keywords, terms)
    )


def _metadata_score(hit: SearchHit, aliases: dict[str, str]) -> int:
    """How usable the record is, independent of the query.

    Reads the configured short names rather than fixed properties: on an
    instance with a different metadata set, its own fields are what count.
    """
    properties: dict[str, Any] = hit.raw.get("properties") or {}
    score = 0

    for prop in aliases.values():
        if properties.get(prop):
            score += 2

    preview = hit.raw.get("preview") or {}
    if preview.get("url") and not preview.get("isIcon"):
        score += 3

    description = hit.description or ""
    if len(description) > 100:
        score += 2
    elif len(description) > 30:
        score += 1

    if hit.source_url:
        score += 1

    return score


def score_hit(hit: SearchHit, query: str, aliases: dict[str, str],
              profile: LanguageProfile = GERMAN) -> int:
    """Relevance of one hit for one query. Never negative."""
    terms = query_terms(query, profile)
    total = _text_score(hit, query, terms) + _metadata_score(hit, aliases)
    return max(total, 0)
