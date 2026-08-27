"""Anfragevarianten.

Der Kern dieser Datei ist eine einzige gemessene Beobachtung: edu-sharing
UND-verknuepft jedes Wort einer Anfrage. Woerter, die nur die *Form* einer Bitte
beschreiben ("Arbeitsblatt", "ich suche"), stehen in fast keinem Datensatz --
also leert ein einziges davon die Trefferliste.

Gemessen gegen Staging am 27.08.2026:

    "Bruchrechnung"                                 1591 Treffer
    "Ich suche ein Arbeitsblatt zur Bruchrechnung"     0 Treffer

Ein Sprachmodell formuliert genau so. Ohne diese Varianten meldet es "nichts
gefunden" ueber ein Thema mit fuenfzehnhundert Datensaetzen -- und ein Mensch
glaubt es.
"""

import pytest

from edusharing.flows.expand import expand_query
from edusharing.flows.language import GERMAN, LanguageProfile


def _labels(varianten) -> list[str]:
    return [v.label for v in varianten]


def _by_label(varianten, prefix: str):
    return next((v for v in varianten if v.label.startswith(prefix)), None)


# --- Die Grundvariante ----------------------------------------------------

def test_die_urspruengliche_anfrage_ist_immer_dabei():
    """Wer die volle Formulierung trifft, soll oben stehen. Die Varianten sind
    eine Ergaenzung, kein Ersatz."""
    varianten = expand_query("Photosynthese", GERMAN)
    voll = _by_label(varianten, "full")
    assert voll is not None
    assert voll.text == "Photosynthese"
    assert voll.weight == max(v.weight for v in varianten)


def test_leere_anfrage_gibt_keine_varianten():
    assert expand_query("   ", GERMAN) == []


# --- Rahmenwoerter --------------------------------------------------------

def test_rahmenwoerter_werden_zu_einer_eigenen_variante():
    """Der eigentliche Gewinn."""
    varianten = expand_query("Ich suche ein Arbeitsblatt zur Bruchrechnung", GERMAN)
    thema = _by_label(varianten, "topic")
    assert thema is not None
    assert thema.text == "bruchrechnung"


def test_ohne_rahmenwoerter_entsteht_keine_themenvariante():
    """Sie waere eine Wiederholung der Grundvariante und kostete eine Anfrage."""
    varianten = expand_query("Photosynthese", GERMAN)
    assert _by_label(varianten, "topic") is None


def test_nur_rahmenwoerter_ergeben_keine_themenvariante():
    """"Ich suche ein Video" hat kein Thema. Eine leere Themenvariante wuerde
    alles finden -- eine schlechtere Antwort als die ehrliche Handvoll."""
    varianten = expand_query("Ich suche ein Video", GERMAN)
    assert _by_label(varianten, "topic") is None


def test_themenvariante_wiegt_weniger_als_die_volle_anfrage():
    """Ein Treffer, der die ganze Formulierung traegt, bleibt vorn."""
    varianten = expand_query("Arbeitsblatt zur Bruchrechnung", GERMAN)
    assert _by_label(varianten, "topic").weight < _by_label(varianten, "full").weight


# --- Stopwoerter ----------------------------------------------------------

def test_stopwoerter_ergeben_eine_eigene_variante():
    varianten = expand_query("die Photosynthese und der Stoffwechsel", GERMAN)
    ohne = _by_label(varianten, "nostop")
    assert ohne is not None
    assert "die" not in ohne.text.split()
    assert "photosynthese" in ohne.text


# --- Synonyme -------------------------------------------------------------

def test_synonyme_werden_eingesetzt():
    varianten = expand_query("KI im Unterricht", GERMAN)
    synonym = _by_label(varianten, "syn")
    assert synonym is not None
    assert "künstliche intelligenz" in synonym.text


def test_synonym_greift_nur_am_ganzen_wort():
    """"klima" darf nicht in "klimawandel" zuenden -- sonst entstuende
    "klimawandelwandel"."""
    varianten = expand_query("Klimawandel", GERMAN)
    for v in varianten:
        assert "wandelwandel" not in v.text


# --- Grenzen --------------------------------------------------------------

def test_die_zahl_der_varianten_ist_gedeckelt():
    """Jede Variante ist eine eigene Anfrage an das Repositorium."""
    varianten = expand_query(
        "Ich suche bitte ein Erklärvideo zur KI und zur Mathematik für die "
        "Grundschule und zum Klimawandel", GERMAN)
    assert len(varianten) <= 5


def test_varianten_sind_nach_gewicht_geordnet():
    varianten = expand_query("Arbeitsblatt zur KI in der Grundschule", GERMAN)
    gewichte = [v.weight for v in varianten]
    assert gewichte == sorted(gewichte, reverse=True)


def test_keine_doppelten_suchtexte():
    """Zwei Varianten mit demselben Text kosten zwei Anfragen und bringen eine
    Antwort."""
    varianten = expand_query("die Bruchrechnung", GERMAN)
    texte = [v.text for v in varianten]
    assert len(texte) == len(set(texte))


# --- Profilunabhaengigkeit ------------------------------------------------

def test_ein_leeres_profil_erzeugt_nur_die_grundvariante():
    """Gegenprobe: ohne Wortlisten gibt es nichts zu expandieren. Wer eine
    Instanz in einer anderen Sprache betreibt, bekommt kein deutsches
    Verhalten aufgezwungen."""
    leer = LanguageProfile()
    varianten = expand_query("Ich suche ein Arbeitsblatt zur Bruchrechnung", leer)
    assert _labels(varianten) == ["full"]


@pytest.mark.parametrize("anfrage", ["a", "ein", "  x  "])
def test_sehr_kurze_anfragen_stuerzen_nicht_ab(anfrage):
    expand_query(anfrage, GERMAN)
