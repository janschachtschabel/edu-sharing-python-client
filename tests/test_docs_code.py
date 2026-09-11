"""Die Code-Bloecke in den Dokumenten laufen gegen die echte Oberflaeche.

Die vierte Doku-Wache, und die letzte Luecke der drei anderen.
``test_docs_complete`` fragt, ob jeder oeffentliche Name **vorkommt**;
``test_docs_inventories``, ob die Verzeichnisse **stimmen**;
``test_docstrings``, ob die Erklaerung **da** ist und ihre Verweise auf etwas
zeigen. Keine fragt, ob der Code, den jemand aus einem Dokument **kopiert**,
ueberhaupt laeuft.

Die Beispiele in ``docs/examples`` werden ausgefuehrt (``test_live_examples``).
Die Bloecke in README, FLOWS, REFERENCE und SKILL fuehrt niemand aus -- und
das ist die groessere Flaeche: ueber tausend Attributzugriffe.

Gemessen am 09.09.2026, beim ersten Lauf dieser Wache:

* ``await repo.resolve(...)`` in beiden READMEs -- die **synchrone** Fassade
  hat ``resolve``, die asynchrone nicht; dort heisst es ``repo.vocab.resolve``.
  Ein Aufruf, der kopiert einen ``AttributeError`` wirft.
* ein Block in FLOWS, als ``python`` ausgezeichnet, der HTTP enthaelt.
* ein Block in REFERENCE, der eine Zeichenkette ueber zwei Zeilen offen laesst.

Zwei Fragen, mehr nicht: parst der Block, und gibt es, was er aufruft.
Was ein Aufruf *tut*, steht anderswo.
"""

import ast
import functools
import importlib
import inspect
import re
import textwrap
from pathlib import Path

import httpx
import pytest

from edusharing import (
    STANDARD_FIELD_ALIASES,
    WRITE_FIELD_ALIASES,
    AsyncRepository,
    Repository,
    ValidationError,
)
from edusharing._sync import SyncFlows, SyncNode
from edusharing.agent import plan_update
from edusharing.bapi import BapiTemplates, BildungsAPI
from edusharing.childobjects import ChildObjects
from edusharing.collections import Collections
from edusharing.content import NodeContent
from edusharing.flows import Flows
from edusharing.flows import collections as sammlungsablaeufe
from edusharing.metadata_agent import MetadataAgent
from edusharing.nodes import Node, Nodes
from edusharing.people import People
from edusharing.relations import Relations
from edusharing.search import Search
from edusharing.skills import Skills
from edusharing.vocab import Vocabulary

WURZEL = Path(__file__).resolve().parent.parent

#: Jedes Dokument, dessen Bloecke jemand kopieren koennte.
DOKUMENTE = [
    "README.md", "README.de.md",
    "docs/FLOWS.md", "docs/FLOWS.de.md",
    "docs/REFERENCE.md", "docs/REFERENCE.de.md",
    "docs/ARCHITECTURE.md", "docs/ARCHITECTURE.de.md",
    ".claude/skills/edu-sharing-python/SKILL.md",
    ".claude/skills/edu-sharing-python/SKILL.de.md",
    ".claude/skills/edu-sharing-python/reference/TRAPS.md",
    ".claude/skills/edu-sharing-python/reference/TRAPS.de.md",
]

#: Was hier steht, ist eine bewusste Ausnahme mit Begruendung, kein Rueckstand.
#: Der Schluessel ist ``(Datei, erste Zeile des Blocks)`` -- eine Blocknummer
#: verschoebe sich beim naechsten eingefuegten Absatz.
NICHT_PYTHON = {
    # ARCHITECTURE zeigt, was der Generator aus der unveraenderten
    # Spezifikation macht: ein ``def`` mit einem Parameter ohne Vorgabe hinter
    # einem mit. Dass es **nicht** parst, ist die Aussage des Absatzes.
    ("docs/ARCHITECTURE.md", "def _get_kwargs("),
    ("docs/ARCHITECTURE.de.md", "def _get_kwargs("),
}

_BLOCK = re.compile(r"```(?:python|py)\n(.*?)```", re.S)

#: Variablenname -> Klasse. Nur, was eindeutig ist: ``kind`` etwa steht in der
#: README fuer eine Inhaltsart und nicht fuer ein Kindobjekt. ``api`` und
#: ``agent`` seit dem 11.09.2026 -- gemessen stehen sie in jedem Block fuer
#: ``BildungsAPI`` und ``MetadataAgent``; ``extraction`` nicht, es fehlt hier.
_WURZELN_ASYNC = {"repo": AsyncRepository, "node": Node, "knoten": Node,
                  "templates": BapiTemplates, "api": BildungsAPI,
                  "agent": MetadataAgent}

#: Synchron gilt ``Repository`` selbst -- die Fassade ist ausgeschrieben und
#: damit genau pruefbar (``resolve`` gibt es dort und asynchron nicht).
#: Fuer den Knoten gilt ``Node``: ``SyncNode`` reicht jeden Lesezugriff per
#: ``__getattr__`` weiter, und was eine Klasse dynamisch aufloest, kann
#: ``hasattr`` nicht sehen -- so gemeldet stuenden ``node.get``,
#: ``node.get_all`` und ``node.properties`` faelschlich als Fehler da
#: (Messung 09.09.2026).
_WURZELN_SYNC = {"repo": Repository, "node": Node, "knoten": Node,
                 "templates": BapiTemplates, "api": BildungsAPI,
                 "agent": MetadataAgent}

#: Wo ein Attribut selbst wieder eine Oberflaeche ist.
_WEITER = {
    (AsyncRepository, "flows"): Flows,
    (AsyncRepository, "skills"): Skills,
    (AsyncRepository, "nodes"): Nodes,
    (AsyncRepository, "collections"): Collections,
    (AsyncRepository, "people"): People,
    (AsyncRepository, "relations"): Relations,
    (AsyncRepository, "vocab"): Vocabulary,
    (AsyncRepository, "searcher"): Search,
    (Node, "content"): NodeContent,
    (Node, "children"): ChildObjects,
    # Blockierend ``SyncFlows``: Name fuer Name dieselben Ablaeufe, jeder reicht
    # an ``Flows`` weiter. Nur hier gleichgesetzt -- ``SyncNodes`` etwa hat kein
    # ``wrap``, dort waere die asynchrone Flaeche zu nachsichtig.
    (Repository, "flows"): Flows,
}

_SCHREIBEN = frozenset(WRITE_FIELD_ALIASES)
_SUCHEN = frozenset(STANDARD_FIELD_ALIASES)

#: Wo ``**kwargs`` in einer Kurznamen-Tabelle endet: ``(Klasse, Methode)`` ->
#: ``(die Funktion, deren Parameter dort noch gelten, die Tabelle)``. Eine
#: Fassade reicht an die Funktion weiter, deren benannte Parameter sie selbst
#: nicht nennt -- ``repo.search(limit=5)`` ist ``Search.search``s ``limit``.
#: Von Hand gepflegt, aber nicht geglaubt: ``test_die_kurznamentabelle_stimmt``
#: ruft jeden Eintrag offline mit einem erfundenen Kurznamen.
_KURZNAMEN = {
    (Node, "update"): (Node.update, _SCHREIBEN),
    (Nodes, "create"): (Nodes.create, _SCHREIBEN),
    (AsyncRepository, "create_node"): (Nodes.create, _SCHREIBEN),
    (Repository, "create_node"): (Nodes.create, _SCHREIBEN),
    (AsyncRepository, "search"): (Search.search, _SUCHEN),
    (Repository, "search"): (Search.search, _SUCHEN),
    (Search, "search"): (Search.search, _SUCHEN),
    (Flows, "search"): (Flows.search, _SUCHEN),
    (Flows, "search_all"): (sammlungsablaeufe.search_all, _SUCHEN),
    (Flows, "find_collections"): (sammlungsablaeufe.find_collections, _SUCHEN),
    (Flows, "add_material"): (Flows.add_material, _SUCHEN),
    (Flows, "update_material"): (Flows.update_material, _SUCHEN),
    (Skills, "search"): (Skills.search, _SUCHEN),
}

#: Freie Funktionen, die Bloecke ohne ``import`` rufen -- der Text davor tut es.
_FREIE = {"plan_update": (plan_update, _SCHREIBEN)}


def _bloecke(rel: str) -> list[tuple[str, str]]:
    """Jeder ``python``-Block einer Datei, mit seiner ersten Zeile als Namen."""
    text = (WURZEL / rel).read_text(encoding="utf-8")
    gefunden = []
    for quelle in _BLOCK.findall(text):
        zeilen = [z for z in quelle.splitlines() if z.strip()]
        gefunden.append((zeilen[0].strip() if zeilen else "", quelle))
    return gefunden


def _kette(knoten: ast.AST) -> list[str] | None:
    """``a.b.c`` -> ``['a', 'b', 'c']``; alles andere -> ``None``."""
    teile = []
    while isinstance(knoten, ast.Attribute):
        teile.append(knoten.attr)
        knoten = knoten.value
    if not isinstance(knoten, ast.Name):
        return None
    teile.append(knoten.id)
    return list(reversed(teile))


@functools.cache
def _instanzattribute(klasse: type) -> frozenset[str]:
    """Was ``__init__`` als ``self.x`` setzt -- auch geerbt.

    ``hasattr`` fragt die Klasse, und dort steht ``api.last_model`` nicht:
    ``BildungsAPI.__init__`` setzt es erst am Objekt.
    """
    gefunden: set[str] = set()
    for k in klasse.__mro__:
        init = vars(k).get("__init__")
        if not inspect.isfunction(init):
            continue
        try:
            baum = ast.parse(textwrap.dedent(inspect.getsource(init)))
        except (OSError, TypeError):   # ohne Quelltext: nichts zu lesen
            continue
        for knoten in ast.walk(baum):
            ziele = (knoten.targets if isinstance(knoten, ast.Assign)
                     else [knoten.target] if isinstance(knoten, ast.AnnAssign) else [])
            gefunden.update(z.attr for z in ziele
                            if isinstance(z, ast.Attribute) and isinstance(z.value, ast.Name)
                            and z.value.id == "self")
    return frozenset(gefunden)


def _unbekannte_aufrufe(quelle: str, baum: ast.AST) -> list[str]:
    """Jeder ``wurzel.a.b``, den es an der Oberflaeche nicht gibt.

    Welche Fassade gilt, sagt der Block selbst: steht ein ``await`` darin, ist
    er asynchron. Der Unterschied ist keine Feinheit -- ``resolve`` gibt es
    an der synchronen Fassade und an der asynchronen nicht.
    """
    wurzeln = _WURZELN_ASYNC if "await " in quelle else _WURZELN_SYNC
    fehlend = []
    for k in ast.walk(baum):
        if not isinstance(k, ast.Attribute):
            continue
        teile = _kette(k)
        if not teile or teile[0] not in wurzeln:
            continue
        klasse: type | None = wurzeln[teile[0]]
        pfad = teile[0]
        for name in teile[1:]:
            if klasse is None:
                break            # hinter einem unbekannten Rueckgabewert
            if not hasattr(klasse, name) and name not in _instanzattribute(klasse):
                fehlend.append(f"{pfad}.{name}")
                break
            pfad = f"{pfad}.{name}"
            klasse = _WEITER.get((klasse, name))
    return fehlend


def _gibt_es(modul: str, name: str | None = None) -> bool:
    """Ob ``import modul`` (und darin ``name``, als Wert oder Untermodul) gelingt."""
    try:
        geladen = importlib.import_module(modul)
    except ImportError:
        return False
    if name is None or hasattr(geladen, name):
        return True
    try:
        importlib.import_module(f"{modul}.{name}")
    except ImportError:
        return False
    return True


def _unbekannte_importe(baum: ast.AST) -> list[str]:
    """Jeder Import aus ``edusharing``, den es nicht gibt."""
    fehlend = []
    for k in ast.walk(baum):
        if isinstance(k, ast.Import):
            fehlend += [f"import {a.name}" for a in k.names
                        if a.name.split(".")[0] == "edusharing" and not _gibt_es(a.name)]
        elif (isinstance(k, ast.ImportFrom) and not k.level and k.module
              and k.module.split(".")[0] == "edusharing"):
            if not _gibt_es(k.module):
                fehlend.append(f"from {k.module} import ...")
                continue
            fehlend += [f"from {k.module} import {a.name}" for a in k.names
                        if a.name != "*" and not _gibt_es(k.module, a.name)]
    return fehlend


def _ziel(k: ast.Call, wurzeln: dict[str, type]) -> tuple[str, type | None, str, object] | None:
    """``(Anzeige, Klasse, Name, Rohwert)`` hinter einem Aufruf -- ``None``, wo
    er nicht an einer bekannten Wurzel haengt. Eine freie Funktion aus
    ``_FREIE`` hat keine Klasse."""
    if isinstance(k.func, ast.Name) and k.func.id in _FREIE:
        return k.func.id, None, k.func.id, _FREIE[k.func.id][0]
    teile = _kette(k.func)
    if not teile or len(teile) < 2 or teile[0] not in wurzeln:
        return None
    klasse: type | None = wurzeln[teile[0]]
    for name in teile[1:-1]:
        klasse = _WEITER.get((klasse, name))
        if klasse is None:
            return None          # hinter einem unbekannten Rueckgabewert
    return ".".join(teile), klasse, teile[-1], inspect.getattr_static(klasse, teile[-1], None)


def _benannte(sig: inspect.Signature) -> set[str]:
    return {p.name for p in sig.parameters.values()
            if p.kind in (p.POSITIONAL_OR_KEYWORD, p.KEYWORD_ONLY)}


def _einzelwerte(anzeige: str, sig: inspect.Signature, k: ast.Call) -> list[str]:
    """Eine Liste an ``*keywords: str`` bindet als **ein** Wert -- und scheitert
    am ersten ``.strip()``."""
    parameter = list(sig.parameters.values())
    stern = next((p for p in parameter if p.kind is p.VAR_POSITIONAL), None)
    if stern is None or stern.annotation not in ("str", str):
        return []
    vorne = sum(p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD) for p in parameter)
    return [f"{anzeige}(...): *{stern.name} nimmt einzelne Werte -- eine Liste wird ein "
            "einziger Wert" for a in k.args[vorne:]
            if isinstance(a, (ast.List, ast.Tuple, ast.Set, ast.ListComp))]


def _kurznamen(anzeige: str, klasse: type | None, name: str, sig: inspect.Signature,
               k: ast.Call) -> list[str]:
    """Was in ``**aliases`` landet, muss ein Kurzname der Tabelle sein -- oder
    ein Parameter der Funktion, an die eine Fassade weiterreicht."""
    eintrag = _FREIE.get(name) if klasse is None else _KURZNAMEN.get((klasse, name))
    if eintrag is None or any(kw.arg is None for kw in k.keywords):
        return []
    endpunkt, tabelle = eintrag
    erlaubt = set(tabelle) | _benannte(sig) | _benannte(inspect.signature(endpunkt))
    return [f"{anzeige}(...): {kw.arg}= ist hier weder Parameter noch Kurzname -- "
            f"Kurznamen: {', '.join(sorted(tabelle))}"
            for kw in k.keywords if kw.arg is not None and kw.arg not in erlaubt]


def _falsch_gebundene_aufrufe(quelle: str, baum: ast.AST) -> list[str]:
    """Jeder ``wurzel.a.b(...)``, dessen Argumente die echte Signatur nicht nimmt.

    ``Signature.bind`` mit Platzhaltern: zu viele Positionen, ein Name, den es
    nicht gibt, ein fehlender Pflichtparameter. Was ``**aliases`` schluckt,
    bindet immer -- dort prueft ``_kurznamen`` gegen die Tabelle; was
    ``*keywords`` schluckt, ``_einzelwerte``. Anderes ``**kwargs``, das
    weitergereicht wird, prueft das nicht. ``f(...)`` ist in einem Dokument ein
    Platzhalter fuer ausgelassene Argumente, kein Aufruf mit ``Ellipsis``; er
    bleibt aussen vor, ebenso ``*args`` und ``**kw``, deren Inhalt der Block
    nicht zeigt (dort nur ``bind_partial``).
    """
    wurzeln = _WURZELN_ASYNC if "await " in quelle else _WURZELN_SYNC
    falsch = []
    for k in ast.walk(baum):
        if not isinstance(k, ast.Call):
            continue
        ziel = _ziel(k, wurzeln)
        if ziel is None:
            continue
        if [type(a) for a in k.args] == [ast.Constant] and k.args[0].value is Ellipsis:
            continue
        anzeige, klasse, name, roh = ziel
        if isinstance(roh, (classmethod, staticmethod)):
            funktion, ohne_erstes = roh.__func__, isinstance(roh, classmethod)
        elif inspect.isfunction(roh):
            funktion, ohne_erstes = roh, klasse is not None
        else:
            continue             # gibt es nicht (sagt die Wache oben) oder ohne Python-Rumpf
        sig = inspect.signature(funktion)
        if ohne_erstes:
            sig = sig.replace(parameters=list(sig.parameters.values())[1:])
        offen = (any(isinstance(a, ast.Starred) for a in k.args)
                 or any(kw.arg is None for kw in k.keywords))
        positionen = [None for a in k.args if not isinstance(a, ast.Starred)]
        namen = {kw.arg: None for kw in k.keywords if kw.arg is not None}
        try:
            (sig.bind_partial if offen else sig.bind)(*positionen, **namen)
        except TypeError as fehler:
            falsch.append(f"{anzeige}(...): {fehler} -- Signatur {sig}")
            continue
        falsch.extend(_einzelwerte(anzeige, sig, k))
        falsch.extend(_kurznamen(anzeige, klasse, name, sig, k))
    return falsch


def _nicht_parsende(rel: str, bloecke: list[tuple[str, str]]) -> list[str]:
    """Welche Bloecke nicht parsen -- getrennt, damit die Gegenprobe sie
    fuettern kann.

    Ohne die Trennung ist die Wache still gruen, sobald alle Bloecke parsen:
    ihren ``except``-Zweig zu entfernen faellt dann niemandem auf.
    """
    kaputt = []
    for erste, quelle in bloecke:
        if (rel, erste) in NICHT_PYTHON:
            continue
        try:
            ast.parse(quelle)
        except SyntaxError as fehler:
            kaputt.append(f"{erste!r}: {fehler.msg}")
    return kaputt


@pytest.mark.parametrize("rel", DOKUMENTE)
def test_jeder_codeblock_parst(rel: str):
    """Wer einen Block kopiert, bekommt keinen Syntaxfehler.

    Ein Block, der als ``python`` ausgezeichnet ist und keiner ist, ist zweimal
    falsch: die Hervorhebung stimmt nicht, und wer ihn nimmt, kann ihn nicht
    ausfuehren.
    """
    kaputt = _nicht_parsende(rel, _bloecke(rel))
    assert not kaputt, (
        f"{rel}: Block als ``python`` ausgezeichnet, parst aber nicht -- "
        "entweder die Auszeichnung aendern (``text``) oder in NICHT_PYTHON "
        "eintragen, mit dem Grund:\n  " + "\n  ".join(kaputt))


@pytest.mark.parametrize("rel", DOKUMENTE)
def test_jeder_codeblock_ruft_nur_vorhandenes(rel: str):
    """Kopierter Code darf nicht am ersten Aufruf scheitern."""
    fehlend = []
    for erste, quelle in _bloecke(rel):
        if (rel, erste) in NICHT_PYTHON:
            continue
        try:
            baum = ast.parse(quelle)
        except SyntaxError:
            continue             # sagt der andere Test
        fehlend.extend(_unbekannte_aufrufe(quelle, baum))
    assert not fehlend, (
        f"{rel}: das Dokument ruft, was es nicht gibt:\n  "
        + "\n  ".join(sorted(set(fehlend))))


def test_die_parsewache_kann_rot_werden():
    """Gefuettert statt gehofft: ein Block, der nicht parst, muss auffallen
    -- und die Ausnahme muss ihn durchlassen."""
    bloecke = [("gut = 1", "gut = 1\n"), ("def kaputt(", "def kaputt(\n")]
    assert _nicht_parsende("egal.md", bloecke) == [
        "'def kaputt(': '(' was never closed"]
    assert _nicht_parsende("docs/ARCHITECTURE.md", [
        ("def _get_kwargs(", "def _get_kwargs(\n")]) == []


def test_die_codewache_sieht_ueberhaupt_etwas():
    """Eine Wache ohne Fund ist still gruen -- also wird sie gefuettert."""
    gut = "await repo.flows.search('x')\nawait node.content.download()"
    schlecht = "await repo.gibt_es_nicht()\nawait node.content.auch_nicht()"
    assert _unbekannte_aufrufe(gut, ast.parse(gut)) == []
    assert _unbekannte_aufrufe(schlecht, ast.parse(schlecht)) == [
        "repo.gibt_es_nicht", "node.content.auch_nicht"]


def test_die_codewache_prueft_den_template_modus():
    """``templates`` steht in den Dokumenten fuer ``BapiTemplates`` (seit dem
    11.09.2026) -- ein Aufruf, den es dort nicht gibt, muss auffallen."""
    gut = "await templates.chat(chain, context_node_id=k)"
    schlecht = "await templates.template_chat(chain)"
    assert _unbekannte_aufrufe(gut, ast.parse(gut)) == []
    assert _unbekannte_aufrufe(schlecht, ast.parse(schlecht)) == [
        "templates.template_chat"]


def test_die_codewache_kennt_was_der_konstruktor_setzt():
    """``api.last_model`` sagt, welches Modell geantwortet hat -- gesetzt in
    ``BildungsAPI.__init__``, nicht an der Klasse. ``hasattr`` sieht es nicht."""
    gut = "await api.chat('Hallo')\nprint(api.last_model)"
    schlecht = "print(api.letztes_modell)"
    assert _unbekannte_aufrufe(gut, ast.parse(gut)) == []
    assert _unbekannte_aufrufe(schlecht, ast.parse(schlecht)) == ["api.letztes_modell"]


# --- Und bindet der Aufruf? (11.09.2026) ----------------------------------
#
# Die Wache oben fragt, ob es ``node.set_property`` gibt -- nicht, ob
# ``node.set_property(value="x")`` es trifft. Gemessen am 11.09.2026 zeigte
# der Skill fuer 15 Methoden die Pflichtparameter nirgends; ein Modell, das
# einen Aufruf nachbaut, raet sie. Ein Block, der sie falsch zeigt, lehrt den
# Fehler gleich mit.

def test_die_signaturwache_sieht_ein_erfundenes_argument():
    """Gefuettert statt gehofft: jede Art, eine Signatur zu verfehlen."""
    gut = ('await node.set_property("cclom:title", "Neu")\n'
           "await templates.chat(chain, context_node_id=k)\n"
           'await api.chat("Hallo", model="gemma")\n'
           "await repo.search(...)\n")
    schlecht = ('await node.set_property("cclom:title", "Neu", pruefen=True)\n'
                "await templates.chat(chain)\n"
                'await api.chat("Hallo", modell="gemma")\n'
                'await node.set_property(value="Neu")\n'
                "await repo.node('a', 'b')\n")
    assert _falsch_gebundene_aufrufe(gut, ast.parse(gut)) == []
    befunde = _falsch_gebundene_aufrufe(schlecht, ast.parse(schlecht))
    erwartet = ["pruefen", "context_node_id", "modell", "'prop'", "too many positional"]
    assert len(befunde) == len(erwartet), befunde
    for befund, stueck in zip(befunde, erwartet, strict=True):
        assert stueck in befund, (stueck, befund)


def test_die_signaturwache_kennt_kurznamen_und_einzelwerte():
    """Was ``**aliases`` und ``*keywords`` schlucken, bindet immer -- und scheitert
    trotzdem. Beides stand bis zum 11.09.2026 in REFERENCE: ``update(subject=…)``
    wirft ValidationError, ``add_keywords(["a"])`` einen AttributeError."""
    gut = ('await node.update(title="x", keywords=["a"])\n'
           'await repo.search("x", subject="Mathematik", limit=5)\n'
           'await repo.create_node(p, name="n", title="t", properties={})\n'
           'await repo.flows.find_collections("x", subject="Physik", limit=3)\n'
           'await node.add_keywords("a", "b")\n'
           'await plan_update(node, title="x")\n')
    schlecht = ('await node.update(subject="Mathematik")\n'
                'await repo.search("x", fach="Mathematik")\n'
                'await plan_update(node, subject="Mathematik")\n'
                'await node.add_keywords(["a", "b"])\n'
                'await repo.flows.find_collections("x", grenze=3)\n')
    assert _falsch_gebundene_aufrufe(gut, ast.parse(gut)) == []
    befunde = _falsch_gebundene_aufrufe(schlecht, ast.parse(schlecht))
    erwartet = ["subject=", "fach=", "subject=", "*keywords", "grenze="]
    assert len(befunde) == len(erwartet), befunde
    for befund, stueck in zip(befunde, erwartet, strict=True):
        assert stueck in befund, (stueck, befund)


def test_die_wache_liest_ablaeufe_auch_am_blockierenden_repository():
    """``repo.flows`` ist blockierend ``SyncFlows`` -- Name fuer Name dieselben
    Ablaeufe wie ``Flows`` (``test_sync_surface`` haelt das), und jeder reicht
    weiter. Ein blockierender Block wird also gegen ``Flows`` geprueft."""
    gut = 'hits = repo.flows.search("x", subject="Physik", limit=3)["hits"]\n'
    schlecht = ('repo.flows.search("x", fach="Physik")\n'
                "repo.flows.gibt_es_nicht()\n")
    assert _falsch_gebundene_aufrufe(gut, ast.parse(gut)) == []
    assert _unbekannte_aufrufe(gut, ast.parse(gut)) == []
    assert "fach=" in " ".join(_falsch_gebundene_aufrufe(schlecht, ast.parse(schlecht)))
    assert _unbekannte_aufrufe(schlecht, ast.parse(schlecht)) == ["repo.flows.gibt_es_nicht"]
    assert set(dir(Flows)) - set(dir(SyncFlows)) <= {n for n in dir(Flows) if n.startswith("_")}


def test_die_importwache_sieht_ein_modul_das_es_nicht_gibt():
    """``from edusharing.flows.ranking import query_terms`` stand bis zum
    11.09.2026 in REFERENCE -- das Modul heisst ``edusharing.ranking``."""
    gut = ("from edusharing import GERMAN, Repository\n"
           "from edusharing.ranking import query_terms\n"
           "from edusharing.agent import as_untrusted\nimport edusharing.bapi\n")
    schlecht = ("from edusharing.flows.ranking import query_terms\n"
                "from edusharing import Client\nimport edusharing.gibt_es_nicht\n")
    assert _unbekannte_importe(ast.parse(gut)) == []
    assert _unbekannte_importe(ast.parse(schlecht)) == [
        "from edusharing.flows.ranking import ...", "from edusharing import Client",
        "import edusharing.gibt_es_nicht"]


@pytest.mark.parametrize("rel", DOKUMENTE)
def test_jeder_import_gibt_es(rel: str):
    """Die erste Zeile, die kopierter Code ausfuehrt, ist der Import."""
    fehlend = []
    for erste, quelle in _bloecke(rel):
        if (rel, erste) in NICHT_PYTHON:
            continue
        try:
            fehlend.extend(_unbekannte_importe(ast.parse(quelle)))
        except SyntaxError:
            continue             # sagt der Parse-Test
    assert not fehlend, f"{rel} importiert, was es nicht gibt:\n  " + "\n  ".join(fehlend)


def _verboten(anfrage: httpx.Request) -> httpx.Response:
    raise AssertionError(f"gesendet, bevor geprueft wurde: {anfrage.method} {anfrage.url.path}")


async def test_die_kurznamentabelle_stimmt():
    """Von Hand gepflegt, aber nicht geglaubt: jeder Eintrag lehnt einen
    unbekannten Kurznamen ab -- offline, bevor er sendet. Gemessen am
    11.09.2026 fuer alle Eintraege; ``add_material`` braucht dafuer
    ``parent_id``, sonst fragt es erst nach dem Home-Ordner."""
    def client() -> httpx.AsyncClient:
        return httpx.AsyncClient(transport=httpx.MockTransport(_verboten), timeout=5)

    async with AsyncRepository("https://repo.test", client=client()) as repo:
        node = repo.nodes.wrap({"ref": {"id": "n1"}, "properties": {}, "access": ["Write"]})
        asynchron = {
            (Node, "update"): lambda: node.update(fach="x"),
            (Nodes, "create"): lambda: repo.nodes.create("p", name="n", fach="x"),
            (AsyncRepository, "create_node"): lambda: repo.create_node("p", name="n", fach="x"),
            (AsyncRepository, "search"): lambda: repo.search("x", fach="y"),
            (Search, "search"): lambda: repo.searcher.search("x", fach="y"),
            (Flows, "search"): lambda: repo.flows.search("x", fach="y"),
            (Flows, "search_all"): lambda: repo.flows.search_all("x", fach="y"),
            (Flows, "find_collections"): lambda: repo.flows.find_collections("x", fach="y"),
            (Flows, "add_material"): lambda: repo.flows.add_material("t", parent_id="p", fach="y"),
            (Flows, "update_material"): lambda: repo.flows.update_material("n1", fach="y"),
            (Skills, "search"): lambda: repo.skills.search("x", fach="y"),
            "plan_update": lambda: plan_update(node, fach="x"),
        }
        for aufruf in asynchron.values():
            with pytest.raises(ValidationError, match="fach"):
                await aufruf()
    blockierend = {
        (Repository, "create_node"): lambda r: r.create_node("p", name="n", fach="x"),
        (Repository, "search"): lambda r: r.search("x", fach="y"),
    }
    for aufruf in blockierend.values():
        sync = Repository("https://repo.test", client=client())
        try:
            with pytest.raises(ValidationError, match="fach"):
                aufruf(sync)
        finally:
            sync.close()
    geprueft = set(asynchron) | set(blockierend)
    assert geprueft == set(_KURZNAMEN) | set(_FREIE), (
        "ein Eintrag der Tabelle ohne Probe -- oder eine Probe ohne Eintrag")


@pytest.mark.parametrize("rel", DOKUMENTE)
def test_jeder_aufruf_bindet_an_die_signatur(rel: str):
    """Kopierter Code darf nicht am ersten Argument scheitern."""
    falsch = []
    for erste, quelle in _bloecke(rel):
        if (rel, erste) in NICHT_PYTHON:
            continue
        try:
            baum = ast.parse(quelle)
        except SyntaxError:
            continue             # sagt der Parse-Test
        falsch.extend(_falsch_gebundene_aufrufe(quelle, baum))
    assert not falsch, (
        f"{rel}: das Dokument ruft mit Argumenten, die die Signatur nicht "
        "nimmt:\n  " + "\n  ".join(falsch))


def test_die_fassaden_loesen_auf_wie_angenommen():
    """Woran die Zuordnung oben haengt.

    ``Repository`` ist ausgeschrieben, also genau pruefbar. ``SyncNode``
    delegiert -- bekaeme es eines Tages seine eigenen Lesezugriffe oder
    verloere die Delegation, waere die Zuordnung still falsch.
    """
    assert "__getattr__" not in vars(Repository), (
        "``Repository`` loest nicht mehr statisch auf -- dann ist die exakte "
        "Pruefung gegen es zu streng")
    assert "__getattr__" in vars(SyncNode), (
        "``SyncNode`` delegiert nicht mehr -- dann gilt fuer synchrone "
        "Bloecke wieder seine eigene Flaeche")


def test_die_codewache_unterscheidet_die_fassaden():
    """``resolve`` gibt es synchron und asynchron nicht -- genau daran haing
    der Befund vom 09.09.2026."""
    asynchron = "uri = await repo.resolve('a', 'b')"
    synchron = "uri = repo.resolve('a', 'b')"
    assert _unbekannte_aufrufe(asynchron, ast.parse(asynchron)) == ["repo.resolve"]
    assert _unbekannte_aufrufe(synchron, ast.parse(synchron)) == []


def test_die_ausnahmen_gibt_es_noch():
    """Eine Ausnahme fuer einen Block, den es nicht mehr gibt, ist eine
    Karteileiche -- und die naechste Person haelt sie fuer eine Regel."""
    vorhanden = {(rel, erste) for rel in DOKUMENTE for erste, _ in _bloecke(rel)}
    verwaist = sorted(NICHT_PYTHON - vorhanden)
    assert not verwaist, f"in NICHT_PYTHON, aber nicht mehr im Dokument: {verwaist}"


# --- "async only" in der Prosa (11.09.2026) ------------------------------
#
# Die Wachen oben lesen Code. Eine Tabellenzeile, die eine Flaeche "async
# only" nennt, ist kein Code -- und genau so eine hat den Fix vom 10.09.2026
# ueberlebt: vier Zeilen je Sprache nannten Flaechen asynchron, die ab da
# blockierten. Ein Agent, der den Skill liest, haette sie auf dem
# blockierenden Repository gemieden.
#
# Die Pruefung glaubt der Aussage nicht, sie misst sie: wer "async only" sagt,
# muss eine Flaeche meinen, die auf dem blockierenden Repository wirklich noch
# Koroutinen hergibt.

_NUR_ASYNC = re.compile(r"`repo\.(\w+)`\s*—\s*\*\*(?:async only|nur asynchron)\*\*")


def _ist_nur_asynchron(name: str) -> bool:
    """Gibt ``Repository`` fuer diese Flaeche noch Koroutinen her?"""
    repo = Repository("https://repo.test/edu-sharing")
    try:
        flaeche = getattr(repo, name, None)
        if flaeche is None:
            return True
        return any(
            inspect.iscoroutinefunction(getattr(flaeche, m, None))
            for m in dir(flaeche) if not m.startswith("_"))
    finally:
        repo.close()


@pytest.mark.parametrize("rel", [
    ".claude/skills/edu-sharing-python/SKILL.md",
    ".claude/skills/edu-sharing-python/SKILL.de.md",
    ".claude/skills/edu-sharing-python/reference/TRAPS.md",
    ".claude/skills/edu-sharing-python/reference/TRAPS.de.md",
    "docs/REFERENCE.md", "docs/REFERENCE.de.md",
    "docs/FLOWS.md", "docs/FLOWS.de.md",
    "README.md", "README.de.md",
])
def test_was_als_nur_asynchron_gilt_ist_es_auch(rel: str):
    text = (WURZEL / rel).read_text(encoding="utf-8")
    falsch = [name for name in _NUR_ASYNC.findall(text)
              if not _ist_nur_asynchron(name)]
    assert not falsch, (
        f"{rel} nennt diese Flaechen 'async only', die auf dem blockierenden "
        f"Repository blockieren: {', '.join('repo.' + n for n in falsch)}")


def test_die_nur_asynchron_wache_erkennt_eine_echte_ausnahme():
    """Die Gegenprobe: die Pruefung darf nicht jede Aussage verwerfen. Ein
    Name, den das blockierende Repository gar nicht hat, ist nur asynchron --
    oder gar nicht da; beides verbietet die Aussage nicht."""
    assert _ist_nur_asynchron("gibt_es_nicht") is True
    assert _ist_nur_asynchron("vocab") is False
