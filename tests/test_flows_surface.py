"""Die Fassade der Ablaeufe deckt sich mit den Ablaeufen.

``Flows`` ist eine Durchreiche: alle 26 oeffentlichen Methoden geben
``await <modul>.<gleicher name>(self._repo, ...)`` zurueck. Die Signatur steht
damit zweimal da -- einmal im Ablauf, einmal in der Methode -- und bei
``search`` sogar dreimal, weil der Aufruf die dreizehn Namen noch einmal
aufzaehlt. Ein vierter Ort ist ``_sync.SyncFlows``.

Fuer die synchrone Fassade gibt es die Wache seit Review C6
(``test_sync_surface.test_die_synchrone_fassade_spiegelt_die_vorgaben``). Fuer
diese Ebene gab es keine: wer ``find.search`` einen Knopf hinzufuegt und
``Flows.search`` vergisst, bricht nichts -- der Knopf ist ueber
``repo.flows.search`` nur einfach nicht da, und ``**aliases`` schluckt ihn als
Feldnamen. Das faellt niemandem auf, der die Methode nicht daraufhin liest
(Audit MNT-3).

Die Wiederholung selbst bleibt, und zwar mit Absicht: sie kauft die
Typisierung und die Vervollstaendigung im Editor, die ein ``**kwargs``-Durchgriff
verlieren wuerde -- bei einer Bibliothek mit ``py.typed`` und ``mypy --strict``
ist das der teurere Verlust. Bewacht ist sie hier.
"""

import ast
import inspect
from pathlib import Path

import pytest

from edusharing import flows as flows_paket
from edusharing.flows import Flows

QUELLE = Path(flows_paket.__file__)

#: Der erste Parameter jeder Ablauffunktion ist das Repositorium; die Methode
#: nimmt ihn nicht, sie *hat* es.
_REPO = "repo"

#: Methoden, die bewusst durchreichen, statt die Knoepfe zu benennen:
#: ``browse_tree(collection_id, **kwargs)``. Wer hier nachschlaegt, liest den
#: Docstring des Ablaufs -- die Fassade hat dazu nichts zu sagen.
#:
#: Warum eine Liste und keine Ableitung "hat ``**kwargs``, also erlaubt": bei
#: ``search`` heisst der Sammelparameter ``**aliases`` und bedeutet etwas
#: anderes -- **Metadatenfelder**. Ein vergessener Knopf landete dort als
#: Feldname, und statt eines ``TypeError`` gaebe es eine stille Suche nach
#: einem Feld, das es nicht gibt. Genau der Fall, den diese Wache verhindern
#: soll, waere von der Ableitung erlaubt worden.
#:
#: Die Liste kann nur zu *streng* veralten: eine neue Durchreiche-Methode steht
#: nicht darauf, faellt hier auf und muss bewusst eingetragen werden.
DURCHREICHER = {
    "browse_tree", "collection_stats", "find_collections", "find_pages",
    "page", "related", "search_all", "search_in_collection", "text",
}


def _durchreichen() -> dict[str, tuple[str, ast.Call]]:
    """Methodenname -> (``modul.funktion``, der Aufruf), aus dem Rumpf gelesen.

    Aus dem Quelltext statt aus einer Liste: eine Liste waere eine zweite
    Stelle, die veraltet, und die Zuordnung steht ohnehin schon in der letzten
    Zeile jeder Methode.

    Der **Aufruf** kommt mit, nicht nur sein Ziel. Die erste Fassung las nur
    ``ruf.func`` und damit zwei der drei Stellen, an denen die Namen stehen;
    ``offset=offset`` aus dem Aufruf zu entfernen liess die ganze Suite gruen
    und machte ``repo.flows.search(offset=20)`` still zu Seite 1 (Pruefung
    08.09.2026).
    """
    baum = ast.parse(QUELLE.read_text(encoding="utf-8"))
    klasse = next(k for k in baum.body
                  if isinstance(k, ast.ClassDef) and k.name == "Flows")
    gefunden = {}
    for m in klasse.body:
        if not isinstance(m, ast.AsyncFunctionDef) or m.name.startswith("_"):
            continue
        letzte = m.body[-1]
        if not (isinstance(letzte, ast.Return) and isinstance(letzte.value, ast.Await)):
            continue
        ruf = letzte.value.value
        if (isinstance(ruf, ast.Call) and isinstance(ruf.func, ast.Attribute)
                and isinstance(ruf.func.value, ast.Name)):
            gefunden[m.name] = (f"{ruf.func.value.id}.{ruf.func.attr}", ruf)
    return gefunden


DURCHREICHEN = {name: ziel for name, (ziel, _) in _durchreichen().items()}
AUFRUFE = {name: ruf for name, (_, ruf) in _durchreichen().items()}


def test_jede_methode_reicht_an_einen_ablauf_durch():
    """Gegenprobe: eine Wache ueber einer leeren Menge ist gruen und prueft
    nichts. Faende diese Zuordnung nichts mehr, waeren alle Tests unten still
    erfolgreich."""
    oeffentlich = [n for n, _ in inspect.getmembers(Flows, inspect.isfunction)
                   if not n.startswith("_")]
    assert len(DURCHREICHEN) == len(oeffentlich), (
        f"{len(DURCHREICHEN)} von {len(oeffentlich)} Methoden gelesen -- "
        "eine Methode hat ihre Bauform geaendert, die Wache liest sie nicht mehr")
    assert len(DURCHREICHEN) > 20, DURCHREICHEN


def _ablauf(pfad: str):
    modul, name = pfad.split(".")
    return getattr(getattr(flows_paket, modul), name)


@pytest.mark.parametrize("methode", sorted(DURCHREICHEN))
def test_die_fassade_bietet_jeden_knopf_des_ablaufs(methode):
    """Was der Ablauf kann, muss ueber ``repo.flows`` erreichbar sein --
    ausser die Methode steht in ``DURCHREICHER`` und sagt damit, dass sie
    nichts eigenes zu nennen hat."""
    if methode in DURCHREICHER:
        pytest.skip("reicht bewusst durch")
    methoden_parameter = inspect.signature(getattr(Flows, methode)).parameters
    fehlend = [n for n, p in inspect.signature(_ablauf(DURCHREICHEN[methode])).parameters.items()
               if n != _REPO and p.kind is not inspect.Parameter.VAR_KEYWORD
               and n not in methoden_parameter]
    assert not fehlend, (
        f"Flows.{methode} bietet {fehlend} nicht, die "
        f"{DURCHREICHEN[methode]} kennt")


@pytest.mark.parametrize("methode", sorted(DURCHREICHEN))
def test_die_vorgaben_sind_dieselben(methode):
    """Eine abweichende Vorgabe ist schlimmer als ein fehlender Parameter:
    beide Wege laufen, und sie tun Verschiedenes."""
    methoden_parameter = inspect.signature(getattr(Flows, methode)).parameters
    abweichend = [
        f"{n}: Fassade {methoden_parameter[n].default!r} statt {p.default!r}"
        for n, p in inspect.signature(_ablauf(DURCHREICHEN[methode])).parameters.items()
        if n in methoden_parameter and n != _REPO
        and methoden_parameter[n].default != p.default
    ]
    assert not abweichend, f"Flows.{methode}: " + "; ".join(abweichend)


@pytest.mark.parametrize("methode", sorted(DURCHREICHEN))
def test_die_fassade_erfindet_keinen_knopf(methode):
    """Die andere Richtung. Ein Parameter, den die Methode nimmt und der Ablauf
    nicht kennt, wird stillschweigend verworfen oder landet in ``**aliases``
    -- als Metadatenfeld, das es nicht gibt."""
    ablauf_parameter = inspect.signature(_ablauf(DURCHREICHEN[methode])).parameters
    erfunden = [n for n, p in inspect.signature(getattr(Flows, methode)).parameters.items()
                if n != "self" and p.kind is not inspect.Parameter.VAR_KEYWORD
                and n not in ablauf_parameter]
    assert not erfunden, (
        f"Flows.{methode} nimmt {erfunden}, was {DURCHREICHEN[methode]} nicht kennt")


def test_die_liste_der_durchreicher_traegt_keinen_zuviel():
    """Eine Ausnahmeliste, die groesser ist als noetig, schaltet Wachen ab.

    Wer eine Methode nachtraeglich ausbaut, sodass sie ihre Knoepfe doch
    benennt, muss sie hier austragen -- sonst bleibt sie ungeprueft, ohne dass
    es noch einen Grund dafuer gibt.
    """
    unnoetig = []
    for methode in sorted(DURCHREICHER & set(DURCHREICHEN)):
        methoden_parameter = inspect.signature(getattr(Flows, methode)).parameters
        fehlend = [n for n, p in inspect.signature(
            _ablauf(DURCHREICHEN[methode])).parameters.items()
            if n != _REPO and p.kind is not inspect.Parameter.VAR_KEYWORD
            and n not in methoden_parameter]
        if not fehlend:
            unnoetig.append(methode)
    assert not unnoetig, (
        f"nennt inzwischen jeden Knopf, gehoert aus DURCHREICHER heraus: {unnoetig}")


def test_jeder_durchreicher_gibt_es_ueberhaupt():
    """Ein Name, der auf keine Methode mehr zeigt, ist eine Ausnahme fuer
    nichts -- und faellt sonst nie auf."""
    verwaist = sorted(DURCHREICHER - set(DURCHREICHEN))
    assert not verwaist, f"in DURCHREICHER, aber keine Methode: {verwaist}"


@pytest.mark.parametrize("methode", sorted(AUFRUFE))
def test_jeder_knopf_wird_auch_wirklich_weitergereicht(methode):
    """Die dritte Stelle: der Aufruf selbst.

    Eine Signatur, die einen Parameter nennt, und ein Aufruf, der ihn nicht
    weitergibt, ergeben zusammen einen Knopf ohne Wirkung -- kein Fehler, kein
    Hinweis, nur die Vorgabe. ``repo.flows.search(offset=20)`` gaebe dann still
    Seite 1 zurueck.

    Verlangt wird ``name=name``: derselbe Name auf beiden Seiten. Das faengt
    auch das Vertauschen, ``limit=offset``, das eine reine Anwesenheitspruefung
    durchliesse.
    """
    ruf = AUFRUFE[methode]
    positional = {a.id for a in ruf.args if isinstance(a, ast.Name)}
    benannt = {k.arg: k.value.id for k in ruf.keywords
               if k.arg and isinstance(k.value, ast.Name)}
    gesternt = {k.value.id for k in ruf.keywords
                if k.arg is None and isinstance(k.value, ast.Name)}

    fehlend, vertauscht = [], []
    for name, p in inspect.signature(getattr(Flows, methode)).parameters.items():
        if name == "self":
            continue
        if p.kind is inspect.Parameter.VAR_KEYWORD:
            if name not in gesternt:
                fehlend.append(f"**{name}")
        elif name in benannt:
            if benannt[name] != name:
                vertauscht.append(f"{name}={benannt[name]}")
        elif name not in positional:
            fehlend.append(name)

    assert not fehlend, (
        f"Flows.{methode} nimmt {fehlend}, reicht es aber nicht an "
        f"{DURCHREICHEN[methode]} weiter -- ein Knopf ohne Wirkung")
    assert not vertauscht, f"Flows.{methode} reicht {vertauscht} weiter"
