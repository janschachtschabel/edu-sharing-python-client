"""Bindet jeder Aufruf in den Dokumenten an die echte Signatur?

Die zweite Haelfte von ``test_docs_code``, herausgeloest, weil sie eine eigene
Frage stellt: jene prueft, ob es ``node.set_property`` **gibt**, diese, ob
``node.set_property(value="x")`` es **trifft**. Gemessen am 11.09.2026 zeigte
der Skill fuer 15 Methoden die Pflichtparameter nirgends; ein Modell, das einen
Aufruf nachbaut, raet sie, und ein Block, der sie falsch zeigt, lehrt den
Fehler gleich mit.

Dazu gehoert, was ``**aliases`` und ``*keywords`` schlucken: beides bindet
immer und scheitert trotzdem -- ``update(subject=…)`` mit einem
``ValidationError``, ``add_keywords(["a"])`` mit einem ``AttributeError``. Die
Kurznamen-Tabelle unten ist von Hand gepflegt und wird nicht geglaubt:
``test_die_kurznamentabelle_stimmt`` ruft jeden Eintrag offline.

Die Wurzeln, die Blockzerlegung und die Frage nach der Existenz stehen in
``test_docs_code`` und werden von dort geholt.
"""

import ast
import functools
import inspect
import textwrap

import httpx
import pytest
from test_docs_code import (
    _WEITER,
    _WURZELN_ASYNC,
    _WURZELN_SYNC,
    DOKUMENTE,
    NICHT_PYTHON,
    _bloecke,
    _kette,
    _unbekannte_aufrufe,
)

from edusharing import (
    STANDARD_FIELD_ALIASES,
    WRITE_FIELD_ALIASES,
    AsyncRepository,
    Repository,
    ValidationError,
)
from edusharing._sync import SyncFlows
from edusharing.agent import plan_update
from edusharing.flows import Flows
from edusharing.flows import collections as sammlungsablaeufe
from edusharing.nodes import Node, Nodes
from edusharing.search import Search
from edusharing.skills import Skills

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


@functools.cache
def _weitergereicht(funktion: object) -> object | None:
    """Die Funktion, an die eine Fassade ihr ``**kwargs`` weitergibt.

    Eine Ebene tief und aus dem Quelltext gelesen, statt gepflegt:
    ``return await modul.name(self._repo, …, **kwargs)`` -- so sind alle
    Ablaeufe gebaut. Der Modulname ist der **Alias** im Importblock
    (``collection_search``), deshalb wird er im Modul der Fassade
    nachgeschlagen und nicht als Pfad geraten.

    ``None``, wo nichts weitergereicht wird oder das Ziel nicht so steht --
    etwa ``self.nodes.children(...)`` in einer blockierenden Fassade, die zwei
    Ebenen tief zeigt. Dort bleibt die Luecke.
    """
    try:
        quelle = textwrap.dedent(inspect.getsource(funktion))
    except (OSError, TypeError):
        return None
    modul = inspect.getmodule(funktion)
    for knoten in ast.walk(ast.parse(quelle)):
        if not isinstance(knoten, ast.Return) or knoten.value is None:
            continue
        aufruf = knoten.value.value if isinstance(knoten.value, ast.Await) else knoten.value
        if not isinstance(aufruf, ast.Call):
            continue
        if not any(kw.arg is None for kw in aufruf.keywords):
            continue             # ohne ``**kwargs`` ist es keine Weitergabe
        teile = _kette(aufruf.func)
        if not teile or len(teile) != 2:
            continue
        ziel = getattr(getattr(modul, teile[0], None), teile[1], None)
        if callable(ziel):
            return ziel
    return None


def _weitergereichte_namen(anzeige: str, klasse: type | None, name: str,
                           sig: inspect.Signature, funktion: object,
                           k: ast.Call) -> list[str]:
    """Ein Schluesselwort, das die Fassade nur durchreicht und das Ziel nicht kennt.

    ``bind`` nimmt es an, weil ``**kwargs`` alles nimmt. Wo eine
    Kurznamen-Tabelle gilt, prueft ``_kurznamen`` schon gegen sie **und** gegen
    das Ziel; hier geht es um die uebrigen Ablaeufe.
    """
    if (klasse, name) in _KURZNAMEN or name in _FREIE:
        return []
    if not any(p.kind is p.VAR_KEYWORD for p in sig.parameters.values()):
        return []
    ziel = _weitergereicht(funktion)
    if ziel is None:
        return []
    ziel_sig = inspect.signature(ziel)
    if any(p.kind is p.VAR_KEYWORD for p in ziel_sig.parameters.values()):
        # Das Ziel reicht selbst weiter -- eine Ebene tiefer waere die Antwort,
        # und hier zu urteilen hiesse raten: ``find_skills`` nimmt so die
        # Kurznamen der Suche entgegen (gemessen 12.09.2026, sonst faelschlich
        # ``subject=`` gemeldet).
        return []
    erlaubt = _benannte(sig) | _benannte(ziel_sig)
    return [f"{anzeige}(...): {kw.arg}= kennt weder der Aufruf noch "
            f"{ziel.__name__}, an das er weiterreicht"
            for kw in k.keywords if kw.arg is not None and kw.arg not in erlaubt]


def _falsch_gebundene_aufrufe(quelle: str, baum: ast.AST) -> list[str]:
    """Jeder ``wurzel.a.b(...)``, dessen Argumente die echte Signatur nicht nimmt.

    ``Signature.bind`` mit Platzhaltern: zu viele Positionen, ein Name, den es
    nicht gibt, ein fehlender Pflichtparameter. Was ``**aliases`` schluckt,
    bindet immer -- dort prueft ``_kurznamen`` gegen die Tabelle; was
    ``*keywords`` schluckt, ``_einzelwerte``; was eine Fassade nur
    weiterreicht, ``_weitergereichte_namen`` gegen das Ziel. ``f(...)`` ist in einem Dokument ein
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
            continue             # gibt es nicht (sagt die Wache dort) oder ohne Python-Rumpf
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
        falsch.extend(_weitergereichte_namen(anzeige, klasse, name, sig, funktion, k))
    return falsch


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


def test_die_wache_folgt_weitergereichtem_kwargs():
    """Ein Ablauf nimmt ``**kwargs`` und reicht alles weiter -- ``bind`` sagt
    dazu nichts.

    ``Flows.page(self, collection_id, **kwargs)`` schluckt jeden Namen;
    ``pages.page`` dahinter kennt ihn nicht. Gemessen am 12.09.2026 band
    ``repo.flows.page("c", widgets_aufloesen=True)`` klaglos durch -- genau
    die Luecke, die der Docstring von ``_falsch_gebundene_aufrufe`` als offen
    nannte.
    """
    gut = ('repo.flows.page("c", resolve_widgets=True, max_widgets=8)\n'
           'repo.flows.text("n", extraction=service, max_chars=20000)\n'
           'repo.flows.browse_tree("c", depth=2, max_collections=30)\n'
           'repo.flows.delete("n", recycle=False)\n'
           # Das Ziel reicht selbst weiter: dort schweigt die Wache, statt zu raten.
           'repo.flows.find_skills("x", subject="Physik")\n')
    schlecht = ('repo.flows.page("c", widgets_aufloesen=True)\n'
                'repo.flows.text("n", extraktion=service)\n'
                'repo.flows.browse_tree("c", tiefe=2)\n')
    assert _falsch_gebundene_aufrufe(gut, ast.parse(gut)) == []
    befunde = _falsch_gebundene_aufrufe(schlecht, ast.parse(schlecht))
    erwartet = ["widgets_aufloesen", "extraktion", "tiefe"]
    assert len(befunde) == len(erwartet), befunde
    for befund, stueck in zip(befunde, erwartet, strict=True):
        assert stueck in befund, (stueck, befund)

    # Und sie greift nicht ins Leere. Gemessen am 12.09.2026 sind es sieben
    # Ablaeufe, deren Ziel aufgeloest ist und abschliesst: browse_tree,
    # collection_stats, find_pages, page, related, search_in_collection, text.
    # Die uebrigen schreiben ihre Parameter selbst aus -- die prueft ``bind``
    # ohnehin. Aendert sich die Bauform der Weitergabe, faellt es hier auf und
    # nicht erst, wenn ein falscher Name durchrutscht.
    urteilsfaehig = [
        name for name, fn in vars(Flows).items()
        if not name.startswith("_") and inspect.isfunction(fn)
        and (ziel := _weitergereicht(fn)) is not None
        and not any(p.kind is p.VAR_KEYWORD
                    for p in inspect.signature(ziel).parameters.values())
    ]
    assert len(urteilsfaehig) >= 7, urteilsfaehig


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
