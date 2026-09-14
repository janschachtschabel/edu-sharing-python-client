"""Jede Option steht bei ihrer Methode -- in beiden Sprachen.

``test_docs_complete`` fragt, ob jeder oeffentliche **Name** vorkommt. Ein
Parameter ist kein Name in dem Sinn: ``rename_if_exists`` stand am 11.09.2026
nirgends, ebenso ``sort`` und ``only`` an ``nodes.children``, ``temperature``
an ``api.chat``, ``version_comment`` an ``upload`` und die
Verbindungseinstellungen (``timeout``, ``max_retries``, …) der vier Einstiege.
Der Skill verspricht das Gegenteil: „… stands for optional parameters, all in
REFERENCE.md". 66 von 144 fehlten.

Geprüft wird die REFERENCE allein: die Skill-Legende verspricht dort alle
Optionen. Der Besitzer gehört zur Identität: ``node.delete`` ist nicht
``repo.flows.delete``. Flows aus ``__init__.py`` und über mehrere Fassaden
weitergereichte Optionen gehören dazu. Mehrzeilige Aufrufe werden als Python
gelesen; ein Parameter eines inneren Aufrufs gilt nicht für den äußeren.
"""

import ast
import dataclasses
import functools
import inspect
import re
import textwrap
from pathlib import Path

import pytest
from test_docs_code import _WEITER
from test_docs_complete import _klassen_der_bibliothek

from edusharing import AsyncRepository, MetadataProfile
from edusharing.bapi import BapiTemplates, BildungsAPI
from edusharing.extraction import TextExtraction
from edusharing.flows import Flows
from edusharing.metadata_agent import MetadataAgent

WURZEL = Path(__file__).resolve().parent.parent

#: Je Sprache die Dateien, in denen eine Option stehen darf.
SPRACHEN = {
    "englisch": ("docs/REFERENCE.md",),
    "deutsch": ("docs/REFERENCE.de.md",),
}

#: Die fünf Einstiege: ihre Konstruktoren sind Nutzerflaeche. Alles andere wird
#: von der Bibliothek gebaut und steht als Objekt in der Referenz, nicht als
#: Konstruktor.
EINSTIEGE = {"AsyncRepository": AsyncRepository, "BildungsAPI": BildungsAPI,
             "BapiTemplates": BapiTemplates, "TextExtraction": TextExtraction,
             "MetadataAgent": MetadataAgent, "MetadataProfile": MetadataProfile}

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


PFADE = {
    "AsyncRepository": {"repo"}, "Repository": {"repo"},
    "BildungsAPI": {"api", "llm"}, "BapiTemplates": {"templates"},
    "MetadataAgent": {"agent"}, "TextExtraction": {"service", "extraction"},
    "Node": {"node", "knoten"}, "Nodes": {"repo.nodes"},
    "NodeContent": {"node.content"}, "NodePermissions": {"node.permissions"},
    "ChildObjects": {"node.children"}, "Comments": {"node.comments"},
    "Suggestions": {"node.suggestions"}, "Workflow": {"node.workflow"},
    "Collections": {"repo.collections"}, "Flows": {"repo.flows"},
    "People": {"repo.people"}, "Relations": {"repo.relations"},
    "Search": {"repo.searcher"}, "Skills": {"repo.skills"},
    "MetadataCatalog": {"repo.metadata"}, "MetadataProfile": {"profile"},
    "Transport": {"repo.raw"}, "Vocabulary": {"repo.vocab"},
}


def _namen(klasse: str, methode: str) -> set[str]:
    if klasse == methode:
        return {klasse}
    return ({f"{pfad}.{methode}" for pfad in PFADE.get(klasse, set())}
            | {f"repo.{name}" for name in AUCH_ALS.get((klasse, methode), set())})


def _ziel(fn, ausdruck):
    if isinstance(ausdruck, ast.Name):
        if ausdruck.id == "repo":
            return AsyncRepository
        name = fn.__qualname__.split(".")[0] if ausdruck.id == "self" else ausdruck.id
        return fn.__globals__.get(name)
    if isinstance(ausdruck, ast.Attribute):
        basis = _ziel(fn, ausdruck.value)
        if basis is Flows and ausdruck.attr == "_repo":
            return AsyncRepository
        if basis is None:
            return None
        return _WEITER.get((basis, ausdruck.attr),
                           inspect.getattr_static(basis, ausdruck.attr, None))
    return None


@functools.cache
def _weitergaben(fn) -> tuple:
    """Follow the actual **kwargs variable, including nested/assigned calls.

    This reaches Flows.skill -> flows.skills.skill -> Skills.get, where the
    intermediate function wraps/assigns the answer instead of returning the
    delegated call directly. Provider-specific **extra inside JSON stays opaque.
    """
    variablen = {p.name for p in inspect.signature(fn).parameters.values()
                 if p.kind is p.VAR_KEYWORD}
    if not variablen:
        return ()
    baum = ast.parse(textwrap.dedent(inspect.getsource(fn)))
    ziele = []
    for k in ast.walk(baum):
        if isinstance(k, ast.Call) and any(
            kw.arg is None and isinstance(kw.value, ast.Name) and kw.value.id in variablen
            for kw in k.keywords
        ):
            ziel = _ziel(fn, k.func)
            if inspect.isfunction(ziel):
                ziele.append(ziel)
    return tuple(ziele)


def _parameter(fn, gesehen=None) -> set[str]:
    gesehen = set() if gesehen is None else gesehen
    if fn in gesehen:
        return set()
    gesehen.add(fn)
    namen = {p.name for p in inspect.signature(fn).parameters.values()
             if p.name not in ("self", "cls") and p.default is not inspect.Parameter.empty
             and p.kind not in (p.VAR_POSITIONAL, p.VAR_KEYWORD)}
    for ziel in _weitergaben(fn):
        namen.update(_parameter(ziel, gesehen))
    return namen


def _optionen() -> list[tuple[str, str, str]]:
    """``(Klasse, Methode, Parameter)`` fuer jede Option, die ein Nutzer setzt."""
    ziele: list[tuple[str, str, object]] = []
    klassen = {**_klassen_der_bibliothek(), "Flows": Flows}
    for name, klasse in sorted(klassen.items()):
        if name.startswith("Sync") or dataclasses.is_dataclass(klasse) \
                or issubclass(klasse, BaseException):
            continue
        for methode, wert in sorted(vars(klasse).items()):
            if not methode.startswith("_") and inspect.isfunction(wert):
                ziele.append((name, methode, wert))
    for name, klasse in EINSTIEGE.items():
        ziele.append((name, name, vars(klasse)["__init__"]))

    return [(klasse, methode, param) for klasse, methode, fn in ziele
            for param in sorted(_parameter(fn))]


def _steht_bei(texte: list[str], namen: set[str], param: str) -> bool:
    """Ob ``param`` in den Klammern eines Aufrufs von ``namen`` steht -- oder
    als `code` in derselben Zeile, wie die Tabellen es schreiben."""
    for text in texte:
        for name in namen:
            for treffer in re.finditer(rf"(?<![A-Za-z0-9_.]){re.escape(name)}\(", text):
                tiefe, i = 1, treffer.end()
                while i < len(text) and tiefe:
                    tiefe += {"(": 1, ")": -1}.get(text[i], 0)
                    i += 1
                if not tiefe and param in _aufruf_parameter(text[treffer.start():i]):
                    return True
                anfang = text.rfind("\n", 0, treffer.start()) + 1
                ende = text.find("\n", treffer.start())
                zeile = text[anfang:ende if ende >= 0 else len(text)]
                if zeile.startswith("|") and f"`{param}`" in zeile:
                    return True
    return False


def _aufruf_parameter(quelle: str) -> set[str]:
    try:
        aufruf = ast.parse(quelle.replace("…", "..."), mode="eval").body
    except SyntaxError:
        return set()
    if not isinstance(aufruf, ast.Call):
        return set()
    return ({kw.arg for kw in aufruf.keywords if kw.arg is not None}
            | {arg.id for arg in aufruf.args if isinstance(arg, ast.Name)})


@pytest.mark.parametrize("sprache", sorted(SPRACHEN))
def test_jede_option_steht_bei_ihrer_methode(sprache):
    """Wer eine Option hinzufuegt, schreibt sie in die Referenz -- sonst gibt es
    sie fuer ein Modell nicht, das nur die Doku hat."""
    texte = [(WURZEL / rel).read_text(encoding="utf-8") for rel in SPRACHEN[sprache]]
    fehlend = [f"{klasse}.{methode}({param}=...)"
               for klasse, methode, param in _optionen()
               if not _steht_bei(texte, _namen(klasse, methode), param)]
    assert not fehlend, (
        f"{len(fehlend)} Optionen stehen in {', '.join(SPRACHEN[sprache])} nicht "
        "bei ihrer Methode:\n  " + "\n  ".join(fehlend))


def test_der_waechter_verlangt_die_methode_daneben():
    """Gegenprobe: der Parametername irgendwo im Text genuegt nicht.

    ``timeout`` steht in jeder Fehlerliste, ``limit`` in jedem zweiten Absatz.
    Gefragt ist die Zeile, die den Aufruf zeigt.
    """
    assert not _steht_bei(["Ein `timeout` beendet die Anfrage."], {"api.chat"}, "timeout")
    assert not _steht_bei(["`api.chat(prompt, model=…)` | `str` |"], {"api.chat"}, "timeout")
    assert _steht_bei(["`api.chat(prompt, timeout=…)` | `str` |"], {"api.chat"}, "timeout")
    assert _steht_bei(["| `api.chat(prompt)` | sendet `timeout` mit |"], {"api.chat"}, "timeout")
    assert _steht_bei(["`repo.create_node(parent_id, type=…)`"],
                      {"repo.nodes.create", "repo.create_node"}, "type")


def test_die_wache_prueft_genug_optionen():
    """Eine Wache, die zwei Parameter kennt, ist gruen und wertlos."""
    optionen = _optionen()
    # 247 measured after recursive forwarding was included (81 on Flows).
    assert len(optionen) >= 240, f"nur {len(optionen)} Optionen gefunden"
    assert ("Nodes", "create", "rename_if_exists") in optionen
    assert ("AsyncRepository", "AsyncRepository", "timeout") in optionen


def test_flows_and_forwarded_options_belong_to_the_inventory():
    optionen = _optionen()
    assert ("Flows", "search", "limit") in optionen
    assert ("Flows", "delete", "recycle") in optionen
    assert ("Flows", "page", "max_widgets") in optionen
    assert ("Flows", "skill", "include_files") in optionen
    assert ("Skills", "pick", "include_files") in optionen
    assert ("Flows", "pick_skill", "include_files") in optionen
    assert ("BildungsAPI", "respond", "provider") in optionen


def test_a_receiver_suffix_does_not_count_as_another_receiver():
    assert not _steht_bei(["`repo.flows.node.delete(recycle=False)`"],
                          {"node.delete"}, "recycle")
    assert not _steht_bei(["`repo.flows.delete(recycle=False)`"],
                          {"node.delete"}, "recycle")
    assert _steht_bei(["`node.delete(recycle=False)`"], {"node.delete"}, "recycle")


def test_options_can_be_documented_in_a_multiline_call():
    assert _steht_bei(["```python\nrepo.flows.page(\n    collection_id,\n"
                       "    max_widgets=12,\n)\n```"], {"repo.flows.page"}, "max_widgets")
    assert not _steht_bei(["`node.delete()`\n`repo.flows.delete(recycle=False)`"],
                          {"node.delete"}, "recycle")


def test_a_nested_call_or_string_value_does_not_document_the_outer_option():
    assert not _steht_bei(["`node.delete(repo.flows.delete(recycle=False))`"],
                          {"node.delete"}, "recycle")
    assert not _steht_bei(['`repo.search("limit")`'], {"repo.search"}, "limit")


@pytest.mark.parametrize("sprache", sorted(SPRACHEN))
def test_removing_only_node_delete_documentation_is_detected(sprache):
    text = (WURZEL / SPRACHEN[sprache][0]).read_text(encoding="utf-8")
    assert _steht_bei([text], _namen("Node", "delete"), "recycle")
    without = "\n".join(line for line in text.splitlines() if "node.delete(" not in line)
    assert _steht_bei([without], _namen("Flows", "delete"), "recycle")
    assert not _steht_bei([without], _namen("Node", "delete"), "recycle")


@pytest.mark.parametrize("sprache", sorted(SPRACHEN))
def test_removing_a_forwarded_flow_option_is_detected(sprache):
    text = (WURZEL / SPRACHEN[sprache][0]).read_text(encoding="utf-8")
    assert ("Flows", "page", "max_widgets") in _optionen()
    assert _steht_bei([text], _namen("Flows", "page"), "max_widgets")
    without = "\n".join(line for line in text.splitlines() if "repo.flows.page(" not in line)
    assert not _steht_bei([without], _namen("Flows", "page"), "max_widgets")


@pytest.mark.parametrize("sprache", sorted(SPRACHEN))
def test_removing_pick_include_files_is_detected(sprache):
    text = (WURZEL / SPRACHEN[sprache][0]).read_text(encoding="utf-8")
    for klasse, methode in (("Skills", "pick"), ("Flows", "pick_skill")):
        namen = _namen(klasse, methode)
        assert (klasse, methode, "include_files") in _optionen()
        assert _steht_bei([text], namen, "include_files")
        without = "\n".join(line for line in text.splitlines()
                            if not any(f"{name}(" in line for name in namen))
        assert _steht_bei([without], _namen("Skills", "get"), "include_files")
        assert not _steht_bei([without], namen, "include_files")
