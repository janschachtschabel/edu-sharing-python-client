"""Jede oeffentliche Methode erklaert sich im Quelltext.

Die dritte Frage neben den beiden anderen Doku-Wachen. ``test_docs_complete``
fragt, ob jeder oeffentliche Name in den Dokumenten *vorkommt*;
``test_docs_inventories`` fragt, ob die Verzeichnisse *stimmen*. Hier steht:
findet jemand die Erklaerung dort, wo er sie sucht -- an der Sache selbst?

Ein Docstring ist das, was ``help()``, der Editor beim Ueberfahren und jedes
Werkzeug anzeigt, das eine Bibliothek einliest. Wer ``node.raw`` sieht und
nicht weiss, ob das der Datensatz oder ein Rohkoerper ist, findet ohne
Docstring nichts -- die Referenz zu durchsuchen ist der Umweg, den ein
Docstring erspart (Audit MNT-5, dort auch als DOC-8 gefuehrt).

Gemessen am 03.09.2026 fehlten 20 ueber ``edusharing.__all__``; am 08.09.2026
waren es dieselben 20.

**Ueber die ganze Handschicht, nicht ueber ``__all__``.** Die erste Fassung
sah nur die 29 Klassen der Paketoberflaeche -- der Audit hatte MNT-5 so
eingegrenzt. Erreichbar sind aber mehr: ``repo.flows``, ``node.children``,
``repo.permissions`` liefern Objekte, deren Klassen nicht in ``__all__``
stehen, und dort fehlten weitere 16 Docstrings, genau die Geschwister der
zwanzig (Pruefung 08.09.2026). Eine Wache, deren Ueberschrift mehr verspricht
als ihre Auswahl haelt, ist an der Ueberschrift zu messen.
"""

import ast
import functools
import importlib
import inspect
import pkgutil
import re
import types
from pathlib import Path
from typing import Any

import pytest

import edusharing

#: Was diese Wache **nicht** verlangt: einen Kommentar an jedem Datenfeld.
#: ``FacetValue.value`` und ``.count`` tragen keinen, und das ist richtig --
#: der Klassendocstring ("One facet value with its hit count") sagt beides,
#: und ein ``#: The value.`` darueber waere Nacherzaehlung. Wo ein Feld etwas
#: traegt, das sein Name nicht sagt, steht es als ``#:``-Kommentar dabei, wie
#: bei ``VocabularyValue.uri``. Beides ist eine Frage des Urteils und nicht
#: maschinell zu entscheiden; Methoden und Eigenschaften sind es schon, denn
#: sie *tun* etwas.


def _handschicht() -> dict[str, type]:
    """Jede oeffentliche Klasse jedes handgeschriebenen Moduls.

    Nach dem Modul benannt, in dem sie **definiert** ist: ein Name, den zwei
    Module re-exportieren, ist eine Klasse und soll einmal geprueft werden.
    """
    gefunden: dict[str, type] = {}
    for modul in pkgutil.walk_packages(edusharing.__path__, "edusharing."):
        if "_generated" in modul.name:
            continue
        geladen = importlib.import_module(modul.name)
        for name, wert in vars(geladen).items():
            if (inspect.isclass(wert) and not name.startswith("_")
                    and wert.__module__ == modul.name):
                gefunden[f"{modul.name}.{name}"] = wert
    return gefunden


KLASSEN = _handschicht()


#: Bauformen, die kein Docstring brauchen -- die Gegenprobe unten darf sie
#: uebergehen. ``member_descriptor`` ist das Feld einer
#: ``slots=True``-Dataclass, also ein Datenfeld, und genau die verlangt diese
#: Wache ausdruecklich nicht. Uebergangen wird nur, was hier steht: alles
#: andere Unbekannte meldet die Gegenprobe.
OHNE_DOCSTRING = (types.MemberDescriptorType,)


def _bauform(wert: Any) -> tuple[str, Any] | None:
    """Die Bauform eines Members und das, woran sein Docstring haengt.

    ``None`` fuer alles, was kein Docstring braucht -- ein Datenwert, eine
    verschachtelte Klasse.

    ``cached_property`` steht ausdruecklich dabei: die erste Fassung kannte
    nur ``property``, sodass ein Umstellen darauf einen Member **still** aus
    der Wache genommen haette (Pruefung 08.09.2026). Was hier nicht
    aufgezaehlt ist und trotzdem aufrufbar oder ein Deskriptor ist, faellt in
    ``test_keine_unbekannte_bauform_faellt_durch`` auf, statt zu verschwinden.
    """
    if isinstance(wert, property):
        return ("Eigenschaft", wert.fget)
    if isinstance(wert, functools.cached_property):
        return ("gemerkte Eigenschaft", wert.func)
    if isinstance(wert, classmethod | staticmethod):
        return ("Klassenmethode", wert.__func__)
    if inspect.isfunction(wert):
        return ("Methode", wert)
    return None


def _erklaerungsbeduerftig(klasse: type) -> list[tuple[str, str, Any]]:
    """Jede eigene oeffentliche Methode, Eigenschaft und Klassenmethode.

    ``vars`` statt ``dir``: geerbtes ist an seiner eigenen Klasse dokumentiert,
    und zweimal dieselbe Fundstelle zu melden macht die Liste unlesbar.
    """
    gefunden = []
    for name, wert in sorted(vars(klasse).items()):
        if name.startswith("_") or inspect.isclass(wert):
            continue
        if (form := _bauform(wert)) is not None:
            gefunden.append((name, form[0], form[1]))
    return gefunden


@pytest.mark.parametrize("klassenname", sorted(KLASSEN))
def test_jede_oeffentliche_methode_hat_einen_docstring(klassenname):
    """Ohne Docstring steht die Erklaerung nur in der Referenz -- also dort,
    wo niemand nachschaut, der gerade in seinem Editor steht."""
    fehlend = [f"{klassenname.split('.')[-1]}.{name} ({art})"
               for name, art, funktion in _erklaerungsbeduerftig(KLASSEN[klassenname])
               if not (getattr(funktion, "__doc__", None) or "").strip()]
    assert not fehlend, "ohne Docstring:\n  " + "\n  ".join(fehlend)


@pytest.mark.parametrize("klassenname", sorted(KLASSEN))
def test_jede_oeffentliche_klasse_hat_einen_docstring(klassenname):
    """Die Klasse selbst zuerst: sie beantwortet die Frage, die vor allen
    Methoden steht -- wofuer gibt es das?"""
    assert (KLASSEN[klassenname].__doc__ or "").strip(), f"{klassenname} ohne Docstring"


def test_jede_oeffentliche_funktion_hat_einen_docstring():
    """Dasselbe fuer das, was keine Klasse ist."""
    fehlend = [n for n in sorted(edusharing.__all__)
               if inspect.isfunction(getattr(edusharing, n))
               and not (getattr(edusharing, n).__doc__ or "").strip()]
    assert not fehlend, f"ohne Docstring: {fehlend}"


@pytest.mark.parametrize("klassenname", sorted(KLASSEN))
def test_keine_unbekannte_bauform_faellt_durch(klassenname):
    """Was ``_bauform`` nicht kennt, wird still uebergangen -- also muss
    auffallen, dass es das gibt.

    Ein Umstellen von ``@property`` auf ``@functools.cached_property`` nahm
    einen Member ohne ein Wort aus der Wache (Pruefung 08.09.2026). Diese
    Gegenprobe faengt die naechste Bauform: alles, was aufrufbar oder ein
    Deskriptor ist und keine bekannte Form hat, wird hier gemeldet, statt zu
    verschwinden.
    """
    unbekannt = [
        f"{name}: {type(wert).__module__}.{type(wert).__qualname__}"
        for name, wert in sorted(vars(KLASSEN[klassenname]).items())
        if not name.startswith("_") and not inspect.isclass(wert)
        and _bauform(wert) is None
        and not isinstance(wert, OHNE_DOCSTRING)
        and (callable(wert) or hasattr(type(wert), "__get__"))
    ]
    assert not unbekannt, (
        "Bauform, die ``_bauform`` nicht kennt -- entweder dort aufnehmen "
        f"oder hier ausnehmen: {unbekannt}")


def test_die_wache_sieht_ueberhaupt_etwas():
    """Gegenprobe. Eine Wache, die ueber einer leeren Menge laeuft, ist gruen
    und prueft nichts -- und genau so faellt es niemandem auf, wenn ein Filter
    zu eng wird oder ``__all__`` sich anders schreibt.
    """
    gezaehlt = sum(len(_erklaerungsbeduerftig(k)) for k in KLASSEN.values())
    assert len(KLASSEN) > 80, len(KLASSEN)
    assert gezaehlt > 300, gezaehlt


# --- Verweise, die ins Leere zeigen ----------------------------------------
#
# Die drei anderen Doku-Wachen fragen, ob ein Name irgendwo *vorkommt*. Diese
# fragt das Umgekehrte: zeigt das, was in einem Docstring steht, noch auf
# etwas? Ein Verweis auf einen geloeschten Helfer ist schlimmer als keiner --
# er schickt den Leser suchen, und die Suche endet nirgends.
#
# Gemessen am 09.09.2026: ein Umbau loeschte ``_ist_gekuerzt`` und benannte
# ``_count`` in ``_next_position`` um; fuenf Verweise darauf blieben stehen,
# ueber vier Dateien, Quelltext und Tests. Keine der vorhandenen Wachen sah
# es -- sie pruefen oeffentliche Namen.

#: Ein privater Name in doppelten Backticks, mit oder ohne Modul davor,
#: Klammern optional.
_VERWEIS = re.compile(r"``(?:([a-z_][a-z0-9_]*)\.)?(_[a-z][a-z0-9_]*)(?:\(\))?``")

#: Was hier steht, ist eine bewusste Ausnahme mit Begruendung, kein Rueckstand.
VERWEIS_ERLAUBT = {
    # Der Modulkopf von ``dto`` erzaehlt, was zusammengefuehrt **wurde**:
    # "drei ``_first`` ..., zwei ``_bare``". Dass die Namen nicht mehr
    # auffindbar sind, ist der Satz -- nicht sein Fehler. ``test_dto``
    # wiederholt ihn.
    ("dto.py", "_first"), ("dto.py", "_bare"),
    ("test_dto.py", "_first"), ("test_dto.py", "_bare"),
    # Kein Verweis, sondern Markdown: ``_so_`` steht dort fuer Kursivschrift,
    # und der Satz handelt gerade davon, dass sie escaped werden muss.
    ("test_skills_markdown.py", "_so_"),
}

#: Die Wurzeln, in denen ein Name stehen darf.
_QUELLEN = ("src/edusharing", "tests")


def _gebundene_namen(baum: ast.AST) -> set[str]:
    """Was diese Datei definiert -- Funktionen, Klassen **und** Attribute.

    Ohne die Attribute meldet die Wache jedes ``self._cache`` als tot, und ein
    Docstring darf auf das Feld zeigen, ueber das er spricht.
    """
    namen: set[str] = set()
    for k in ast.walk(baum):
        if isinstance(k, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            namen.add(k.name)
            continue
        ziele: list[ast.expr] = []
        if isinstance(k, ast.Assign):
            ziele = list(k.targets)
        elif isinstance(k, ast.AnnAssign):
            ziele = [k.target]
        for ziel in ziele:
            if isinstance(ziel, ast.Name):
                namen.add(ziel.id)
            elif isinstance(ziel, ast.Attribute):
                namen.add(ziel.attr)
    return namen


def _docstrings(baum: ast.AST) -> list[str]:
    gefunden = []
    for knoten in ast.walk(baum):
        if isinstance(knoten, ast.Module | ast.FunctionDef | ast.AsyncFunctionDef
                      | ast.ClassDef):
            text = ast.get_docstring(knoten)
            if text:
                gefunden.append(text)
    return gefunden


@functools.cache
def _bestand() -> tuple[dict[str, frozenset[str]], frozenset[str],
                        tuple[tuple[str, str], ...]]:
    """Je Modul seine Namen, alle zusammen, und alle Docstrings."""
    wurzel = Path(__file__).resolve().parent.parent
    je_modul: dict[str, set[str]] = {}
    texte: list[tuple[str, str]] = []
    for teil in _QUELLEN:
        for pfad in sorted((wurzel / teil).rglob("*.py")):
            if "_generated" in pfad.parts:
                continue
            baum = ast.parse(pfad.read_text(encoding="utf-8"), filename=str(pfad))
            je_modul.setdefault(pfad.stem, set()).update(_gebundene_namen(baum))
            texte.extend((pfad.name, t) for t in _docstrings(baum))
    alle = frozenset(n for namen in je_modul.values() for n in namen)
    return ({m: frozenset(n) for m, n in je_modul.items()}, alle, tuple(texte))


def test_kein_docstring_verweist_ins_leere():
    """Ein Verweis auf etwas, das es nicht mehr gibt, schickt den Leser suchen.

    Geprueft werden **private** Namen: die sind lokal aufzuloesen, und genau
    sie verschwinden bei Umbauten, ohne dass eine der anderen Wachen es merkt.
    Ein Verweis mit Modul davor muss in diesem Modul stehen, einer ohne
    irgendwo -- ein Testdocstring darf den Helfer nennen, den er prueft.
    """
    je_modul, alle, texte = _bestand()
    tote = []
    for datei, text in texte:
        for modul, name in _VERWEIS.findall(text):
            if (datei, name) in VERWEIS_ERLAUBT:
                continue
            if modul:
                if modul in je_modul and name not in je_modul[modul]:
                    tote.append(f"{datei}: ``{modul}.{name}``")
            elif name not in alle:
                tote.append(f"{datei}: ``{name}``")
    assert not tote, (
        "Docstring verweist auf einen Namen, den es nicht gibt -- entweder "
        "richtigstellen oder in VERWEIS_ERLAUBT eintragen, mit dem Grund:\n  "
        + "\n  ".join(sorted(set(tote))))


def test_die_verweiswache_sieht_ueberhaupt_etwas():
    """Gegenprobe: eine Wache, deren Ausdruck nichts trifft, ist still gruen."""
    treffer = _VERWEIS.findall(
        "siehe ``_order_key`` und ``childobjects._anhaenge()`` und ``page_cut``")
    assert treffer == [("", "_order_key"), ("childobjects", "_anhaenge")], treffer


def test_die_verweiswache_kennt_auch_attribute():
    """Ohne die Attribute meldete sie jedes Feld als tot -- gemessen an
    ``_cache``, ueber das ``test_vocab`` spricht."""
    _, alle, _ = _bestand()
    assert "_cache" in alle, "ein zugewiesenes Attribut zaehlt als definiert"


def test_die_verweiswache_kann_rot_werden():
    """Und ein Name, den es nirgends gibt, muss durchfallen."""
    _, alle, _ = _bestand()
    assert "_gibt_es_nicht_xyz" not in alle
