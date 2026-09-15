"""Word lists the ranking needs — kept apart from the algorithm that uses them.

These are data, not logic, and they change for different reasons: a synonym is
added when someone notices a missed search, while the scoring formula changes
almost never. Same split as in ``wlo-mcp-sc``, which is also where the lists
come from (Apache-2.0, same as this library). The measurements quoted below
were taken there and re-verified against staging on 2026-08-27.

The lists are German because the repositories this library was written for hold
German material. They are **not** wired in: ``LanguageProfile`` is a parameter
everywhere, so an instance in another language supplies its own without touching
the ranking code. That is the same promise as E4 in ARCHITECTURE — profile
independence would be worthless if the ranking quietly assumed German.
"""

from __future__ import annotations

from dataclasses import dataclass, field

__all__ = ["GERMAN", "LanguageProfile"]


@dataclass(frozen=True)
class LanguageProfile:
    """The vocabulary the ranking reasons about.

    Args:
        stopwords: words that carry no signal. They are not merely useless --
            German stopwords sit inside ordinary words ("Stu-**die**-n",
            "Me-**die**-n"), so leaving them in actively creates false matches.
        framing: nouns and verbs that frame a request instead of naming its
            subject. See ``GERMAN_FRAMING`` for why these matter more than they
            look.
        synonyms: ``{term: [alternatives]}``, matched at word boundaries.
    """

    stopwords: frozenset[str] = field(default_factory=frozenset)
    framing: frozenset[str] = field(default_factory=frozenset)
    synonyms: dict[str, list[str]] = field(default_factory=dict)


GERMAN_STOPWORDS = frozenset({
    "der", "die", "das", "den", "dem", "des", "ein", "eine", "einer", "einem",
    "einen", "eines", "und", "oder", "aber", "als", "auch", "auf", "aus", "bei",
    "bis", "für", "mit", "nach", "von", "vor", "wie", "über", "unter", "durch",
    "gegen", "ohne", "zwischen", "ich", "du", "er", "sie", "wir", "ihr", "uns",
    "sich", "ist", "sind", "war", "hat", "wird", "kann", "soll", "zum", "zur",
    "vom", "nicht", "noch", "nur", "sehr", "schon", "dann", "wenn", "dass",
    "weil", "im", "am", "an", "in", "zu", "so", "es", "ob",
})

#: Words that describe the *shape* of a request rather than its subject.
#:
#: This list is the reason the reranking exists at all. edu-sharing ANDs every
#: word of a query, and these words appear in almost no record -- so a single
#: one of them empties the result set. Measured against staging on 2026-08-27:
#:
#: ===================================  =======  ============================
#: query                                  hits   without the framing word
#: ===================================  =======  ============================
#: "Bruchrechnung"                         1591
#: "Ich suche ein Arbeitsblatt zur          **0**  1591
#:  Bruchrechnung"
#: "Französische Revolution"                637
#: "Unterrichtsstunde Französische          **0**  637
#:  Revolution"
#: "Optik"                                 1345
#: "Bildungsinhalte zur Optik"                4   1345
#: ===================================  =======  ============================
#:
#: A language model phrases exactly like this. Left alone it reports "no
#: material found" about a subject with fifteen hundred records -- and a person
#: believes it.
#:
#: Where a word is also a real filter value (Video -> type, Sekundarstufe ->
#: level), the filter is where it belongs anyway.
GERMAN_FRAMING = frozenset({
    # medium -- belongs in the `type` filter
    "video", "videos", "erklärvideo", "erklärvideos", "lernvideo", "lernvideos",
    "film", "filme", "podcast", "bild", "bilder", "grafik", "grafiken",
    "simulation", "simulationen", "arbeitsblatt", "arbeitsblätter",
    "übung", "übungen", "aufgabe", "aufgaben",
    # the generic word for "anything at all"
    "material", "materialien", "unterrichtsmaterial", "unterrichtsmaterialien",
    "medien", "medium", "bildungsinhalt", "bildungsinhalte", "inhalt", "inhalte",
    "beispiel", "beispiele",
    # teaching frame
    "unterricht", "unterrichtsstunde", "unterrichtsstunden", "unterrichtseinheit",
    "stunde", "lerneinheit",
    # level -- belongs in the `level` filter
    "klasse", "klassenstufe", "jahrgangsstufe", "sekundarstufe",
    # the act of asking
    "suche", "suchen", "brauche", "benötige", "finde", "finden",
    "zeig", "zeige", "gib", "möchte", "hätte", "mir", "bitte",
})

GERMAN_SYNONYMS: dict[str, list[str]] = {
    "ki": ["künstliche intelligenz"],
    "künstliche intelligenz": ["ki"],
    "oer": ["open educational resources", "freie bildungsmaterialien"],
    "mathe": ["mathematik"],
    "mathematik": ["mathe"],
    "bio": ["biologie"],
    "biologie": ["bio"],
    "geo": ["geographie", "erdkunde"],
    "geographie": ["erdkunde", "geo"],
    "erdkunde": ["geographie", "geo"],
    "info": ["informatik"],
    "informatik": ["info"],
    "grundschule": ["primarstufe"],
    "primarstufe": ["grundschule"],
    "klima": ["klimawandel", "klimaschutz"],
    "klimawandel": ["klima", "klimaschutz"],
    "nachhaltigkeit": ["nachhaltige entwicklung", "bne"],
    "bne": ["bildung für nachhaltige entwicklung", "nachhaltigkeit"],
}

#: The default profile. German, because that is what the repositories hold.
GERMAN = LanguageProfile(
    stopwords=GERMAN_STOPWORDS,
    framing=GERMAN_FRAMING,
    synonyms=GERMAN_SYNONYMS,
)
