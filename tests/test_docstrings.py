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

Gemessen am 03.09.2026 fehlten 20; am 08.09.2026 waren es dieselben 20.
"""

import inspect
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
KLASSEN = sorted(n for n in edusharing.__all__
                 if inspect.isclass(getattr(edusharing, n)))


def _erklaerungsbeduerftig(klasse: type) -> list[tuple[str, str, Any]]:
    """Jede eigene oeffentliche Methode, Eigenschaft und Klassenmethode.

    ``vars`` statt ``dir``: geerbtes ist an seiner eigenen Klasse dokumentiert,
    und zweimal dieselbe Fundstelle zu melden macht die Liste unlesbar.
    """
    gefunden = []
    for name, wert in sorted(vars(klasse).items()):
        if name.startswith("_"):
            continue
        if isinstance(wert, property):
            gefunden.append((name, "Eigenschaft", wert.fget))
        elif isinstance(wert, classmethod | staticmethod):
            gefunden.append((name, "Klassenmethode", wert.__func__))
        elif inspect.isfunction(wert):
            gefunden.append((name, "Methode", wert))
    return gefunden


@pytest.mark.parametrize("klassenname", KLASSEN)
def test_jede_oeffentliche_methode_hat_einen_docstring(klassenname):
    """Ohne Docstring steht die Erklaerung nur in der Referenz -- also dort,
    wo niemand nachschaut, der gerade in seinem Editor steht."""
    klasse = getattr(edusharing, klassenname)
    fehlend = [f"{klassenname}.{name} ({art})"
               for name, art, funktion in _erklaerungsbeduerftig(klasse)
               if not (getattr(funktion, "__doc__", None) or "").strip()]
    assert not fehlend, "ohne Docstring:\n  " + "\n  ".join(fehlend)


@pytest.mark.parametrize("klassenname", KLASSEN)
def test_jede_oeffentliche_klasse_hat_einen_docstring(klassenname):
    """Die Klasse selbst zuerst: sie beantwortet die Frage, die vor allen
    Methoden steht -- wofuer gibt es das?"""
    klasse = getattr(edusharing, klassenname)
    assert (klasse.__doc__ or "").strip(), f"{klassenname} hat keinen Docstring"


def test_jede_oeffentliche_funktion_hat_einen_docstring():
    """Dasselbe fuer das, was keine Klasse ist."""
    fehlend = [n for n in sorted(edusharing.__all__)
               if inspect.isfunction(getattr(edusharing, n))
               and not (getattr(edusharing, n).__doc__ or "").strip()]
    assert not fehlend, f"ohne Docstring: {fehlend}"


def test_die_wache_sieht_ueberhaupt_etwas():
    """Gegenprobe. Eine Wache, die ueber einer leeren Menge laeuft, ist gruen
    und prueft nichts -- und genau so faellt es niemandem auf, wenn ein Filter
    zu eng wird oder ``__all__`` sich anders schreibt.
    """
    gezaehlt = sum(len(_erklaerungsbeduerftig(getattr(edusharing, n)))
                   for n in KLASSEN)
    assert len(KLASSEN) > 20, KLASSEN
    assert gezaehlt > 100, gezaehlt
