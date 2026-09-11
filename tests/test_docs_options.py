"""Jede Option steht bei ihrer Methode -- in beiden Sprachen.

``test_docs_complete`` fragt, ob jeder oeffentliche **Name** vorkommt. Ein
Parameter ist kein Name in dem Sinn: ``rename_if_exists`` stand am 11.09.2026
nirgends, ebenso ``sort`` und ``only`` an ``nodes.children``, ``temperature``
an ``api.chat``, ``version_comment`` an ``upload`` und die
Verbindungseinstellungen (``timeout``, ``max_retries``, …) der vier Einstiege.
Der Skill verspricht das Gegenteil: „… stands for optional parameters, all in
REFERENCE.md". 66 von 144 fehlten.

Gefragt ist nicht, ob der Parametername irgendwo im Text steht -- ``timeout``
kommt in jeder Fehlerliste vor -- sondern ob er **bei seiner Methode** steht:
in den Klammern eines Aufrufs, oder als `code` in derselben Zeile. Das ist die
Form, in der die Referenztabellen ohnehin geschrieben sind.
"""

import dataclasses
import inspect
import re
from pathlib import Path

import pytest
from test_docs_complete import _klassen_der_bibliothek

from edusharing import AsyncRepository
from edusharing.bapi import BapiTemplates, BildungsAPI
from edusharing.extraction import TextExtraction
from edusharing.metadata_agent import MetadataAgent

WURZEL = Path(__file__).resolve().parent.parent

#: Je Sprache die Dateien, in denen eine Option stehen darf.
SPRACHEN = {
    "englisch": ("docs/REFERENCE.md", "docs/FLOWS.md"),
    "deutsch": ("docs/REFERENCE.de.md", "docs/FLOWS.de.md"),
}

#: Die vier Einstiege: ihre Konstruktoren sind Nutzerflaeche. Alles andere wird
#: von der Bibliothek gebaut und steht als Objekt in der Referenz, nicht als
#: Konstruktor.
EINSTIEGE = {"AsyncRepository": AsyncRepository, "BildungsAPI": BildungsAPI,
             "BapiTemplates": BapiTemplates, "TextExtraction": TextExtraction,
             "MetadataAgent": MetadataAgent}

#: Dieselbe Methode, kuerzer erreichbar: die Referenz zeigt oft nur den kurzen
#: Weg, und das genuegt. Von Hand gepflegt -- eine Zeile je Fassade.
AUCH_ALS = {
    ("Nodes", "create"): {"create_node"}, ("Nodes", "get"): {"node"},
    ("Collections", "create"): {"create_collection"},
    ("Collections", "find"): {"find_collections"},
    ("Collections", "update"): {"update_collection"},
    ("Collections", "add"): {"add_to_collection"},
    ("Collections", "remove"): {"remove_from_collection"},
    ("Search", "search"): {"search"},
    ("Vocabulary", "resolve"): {"resolve"},
    ("Vocabulary", "resolve_all"): {"resolve_all"},
}


def _optionen() -> list[tuple[str, str, str]]:
    """``(Klasse, Methode, Parameter)`` fuer jede Option, die ein Nutzer setzt."""
    ziele: list[tuple[str, str, object]] = []
    for name, klasse in sorted(_klassen_der_bibliothek().items()):
        if name.startswith("Sync") or dataclasses.is_dataclass(klasse) \
                or issubclass(klasse, BaseException):
            continue
        for methode, wert in sorted(vars(klasse).items()):
            if not methode.startswith("_") and inspect.isfunction(wert):
                ziele.append((name, methode, wert))
    for name, klasse in EINSTIEGE.items():
        ziele.append((name, name, vars(klasse)["__init__"]))

    gefunden = []
    for klasse, methode, fn in ziele:
        for p in inspect.signature(fn).parameters.values():
            if p.name in ("self", "cls") or p.default is inspect.Parameter.empty:
                continue
            if p.kind in (p.VAR_POSITIONAL, p.VAR_KEYWORD):
                continue
            gefunden.append((klasse, methode, p.name))
    return gefunden


def _steht_bei(texte: list[str], namen: set[str], param: str) -> bool:
    """Ob ``param`` in den Klammern eines Aufrufs von ``namen`` steht -- oder
    als `code` in derselben Zeile, wie die Tabellen es schreiben."""
    wort = re.compile(rf"(?<![A-Za-z0-9_]){re.escape(param)}(?![A-Za-z0-9_])")
    for text in texte:
        for zeile in text.splitlines():
            for name in namen:
                for treffer in re.finditer(rf"(?<![A-Za-z0-9_]){name}\(", zeile):
                    tiefe, i = 1, treffer.end()
                    while i < len(zeile) and tiefe:
                        tiefe += {"(": 1, ")": -1}.get(zeile[i], 0)
                        i += 1
                    if wort.search(zeile[treffer.end():i]):
                        return True
                    if f"`{param}`" in zeile:
                        return True
    return False


@pytest.mark.parametrize("sprache", sorted(SPRACHEN))
def test_jede_option_steht_bei_ihrer_methode(sprache):
    """Wer eine Option hinzufuegt, schreibt sie in die Referenz -- sonst gibt es
    sie fuer ein Modell nicht, das nur die Doku hat."""
    texte = [(WURZEL / rel).read_text(encoding="utf-8") for rel in SPRACHEN[sprache]]
    fehlend = [f"{klasse}.{methode}({param}=...)"
               for klasse, methode, param in _optionen()
               if not _steht_bei(texte, {methode} | AUCH_ALS.get((klasse, methode), set()),
                                 param)]
    assert not fehlend, (
        f"{len(fehlend)} Optionen stehen in {', '.join(SPRACHEN[sprache])} nicht "
        "bei ihrer Methode:\n  " + "\n  ".join(fehlend))


def test_der_waechter_verlangt_die_methode_daneben():
    """Gegenprobe: der Parametername irgendwo im Text genuegt nicht.

    ``timeout`` steht in jeder Fehlerliste, ``limit`` in jedem zweiten Absatz.
    Gefragt ist die Zeile, die den Aufruf zeigt.
    """
    assert not _steht_bei(["Ein `timeout` beendet die Anfrage."], {"chat"}, "timeout")
    assert not _steht_bei(["`api.chat(prompt, model=…)` | `str` |"], {"chat"}, "timeout")
    assert _steht_bei(["`api.chat(prompt, timeout=…)` | `str` |"], {"chat"}, "timeout")
    assert _steht_bei(["| `api.chat(prompt)` | sendet `timeout` mit |"], {"chat"}, "timeout")
    assert _steht_bei(["`repo.create_node(parent_id, type=…)`"],
                      {"create", "create_node"}, "type")


def test_die_wache_prueft_genug_optionen():
    """Eine Wache, die zwei Parameter kennt, ist gruen und wertlos."""
    optionen = _optionen()
    assert len(optionen) >= 130, f"nur {len(optionen)} Optionen gefunden"
    assert ("Nodes", "create", "rename_if_exists") in optionen
    assert ("AsyncRepository", "AsyncRepository", "timeout") in optionen
