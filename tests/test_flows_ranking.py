"""Textabgleich und Bewertung fuer die Neuordnung von Treffern.

Die Regeln hier sind nicht erfunden, sondern aus dem wlo-mcp-sc uebernommen,
wo sie gegen eine laufende Instanz gemessen wurden. Die Messungen, auf denen
sie beruhen, stehen jeweils am Test.

Zwei Dinge trennen diese Datei von einer Portierung: die Wortlisten sind
austauschbar (die Bibliothek ist profilunabhaengig), und die Qualitaetssignale
kommen aus den konfigurierten Kurznamen statt aus festen WLO-Eigenschaften.
"""

import pytest

from edusharing.flows.language import GERMAN, LanguageProfile
from edusharing.flows.ranking import query_terms, score_hit, term_matches
from edusharing.results import SearchHit

ALIASES = {"subject": "ccm:taxonid", "level": "ccm:educationalcontext",
           "type": "ccm:oeh_lrt_aggregated", "license": "license"}


def _hit(title="", description=None, keywords=(), props=None, **kwargs) -> SearchHit:
    eigenschaften = {"cclom:general_keyword": list(keywords), **(props or {})}
    return SearchHit(
        id=kwargs.pop("id", "n1"), title=title, url="https://x/y",
        description=description, raw={"properties": eigenschaften, **kwargs},
    )


# --- Termabgleich ---------------------------------------------------------

def test_langer_term_trifft_auch_im_wortinneren():
    """Deutsche Komposita: "Rechnung" gehoert in "Bruchrechnung", und
    "Mittelalter" in "mittelalterlichen"."""
    assert term_matches("rechnung", "bruchrechnung uebungen")
    assert term_matches("mittelalter", "im mittelalterlichen europa")


@pytest.mark.parametrize("text", ["sitting", "mauritius", "politik", "citizenship"])
def test_kurzer_term_trifft_nicht_zufaellig_im_wortinneren(text):
    """Gemessen im wlo-mcp-sc am 03.08.2026: die Anfrage "IT" brachte
    "s-IT-ting", "Maur-IT-ius", "Pol-IT-ik" und "C-IT-izenship" unter die
    ersten fuenf Treffer."""
    assert not term_matches("it", text)


@pytest.mark.parametrize("term,text", [("eu", "europäische union"), ("bio", "biologie"),
                                       ("it", "it-sicherheit"), ("it", "die it")])
def test_kurzer_term_trifft_am_wortanfang(term, text):
    """Gegenprobe: nur der Wortanfang wird verlangt, nicht auch das Wortende --
    sonst fielen genau die Komposita heraus, um die es geht."""
    assert term_matches(term, text)


def test_leerer_term_trifft_nie():
    assert not term_matches("", "irgendwas")


# --- Signaltragende Woerter ----------------------------------------------

def test_stopwoerter_zaehlen_nicht_als_signal():
    """Gemessen im wlo-mcp-sc am 03.08.2026 ueber 60 Knoten: "Bruchrechnung"
    traf 0 Knoten, "die Bruchrechnung" traf 43. Der Grund ist, dass deutsche
    Stopwoerter in gewoehnlichen Woertern stecken -- "Stu-die-n", "Me-die-n"."""
    assert query_terms("die Bruchrechnung", GERMAN) == ["bruchrechnung"]


def test_einzelne_zeichen_zaehlen_nicht():
    assert query_terms("a b Optik", GERMAN) == ["optik"]


def test_eigene_wortliste_ersetzt_die_deutsche():
    """Die Bibliothek ist profilunabhaengig. Eine fest verdrahtete deutsche
    Wortliste waere genau der Bruch, den E4 vermeiden soll."""
    englisch = LanguageProfile(stopwords=frozenset({"the", "of"}),
                               framing=frozenset(), synonyms={})
    assert query_terms("the theory of optics", englisch) == ["theory", "optics"]
    # Gegenprobe: mit dem deutschen Profil bleiben "the" und "of" stehen.
    assert "the" in query_terms("the theory of optics", GERMAN)


# --- Bewertung ------------------------------------------------------------

def test_titeltreffer_wiegt_schwerer_als_beschreibungstreffer():
    im_titel = score_hit(_hit(title="Photosynthese erklärt"), "Photosynthese", ALIASES)
    in_beschreibung = score_hit(
        _hit(title="Botanik", description="unter anderem Photosynthese"),
        "Photosynthese", ALIASES)
    assert im_titel > in_beschreibung


def test_exakter_titel_wiegt_am_schwersten():
    exakt = score_hit(_hit(title="Photosynthese"), "Photosynthese", ALIASES)
    anfang = score_hit(_hit(title="Photosynthese im Detail"), "Photosynthese", ALIASES)
    irgendwo = score_hit(_hit(title="Die Photosynthese im Detail"), "Photosynthese", ALIASES)
    assert exakt > anfang > irgendwo


def test_treffer_ohne_bezug_wird_abgestraft():
    """Ohne Strafe landen Treffer oben, die das Wort nirgends tragen und nur
    viele Metadaten haben."""
    ohne = score_hit(_hit(title="Etwas ganz anderes"), "Photosynthese", ALIASES)
    mit = score_hit(_hit(title="Photosynthese"), "Photosynthese", ALIASES)
    assert ohne < mit


def test_gepflegte_metadaten_heben_den_wert():
    """Der Punkt ist die Reihenfolge bei gleichem Text: wer Fach, Stufe und eine
    freie Lizenz traegt, ist fuer den Unterricht brauchbarer."""
    nackt = _hit(title="Photosynthese")
    gepflegt = _hit(title="Photosynthese", props={
        "ccm:taxonid": ["http://x/080"],
        "ccm:educationalcontext": ["http://x/sek1"],
        "license": ["CC_BY"],
    })
    assert (score_hit(gepflegt, "Photosynthese", ALIASES)
            > score_hit(nackt, "Photosynthese", ALIASES))


def test_qualitaetssignale_folgen_den_kurznamen():
    """Gegenprobe zur Generizitaet: wer andere Kurznamen konfiguriert, dessen
    Felder zaehlen -- die WLO-Eigenschaften sind dann bedeutungslos."""
    eigene = {"fach": "ccm:custom_subject"}
    passend = _hit(title="Optik", props={"ccm:custom_subject": ["x"]})
    unpassend = _hit(title="Optik", props={"ccm:taxonid": ["x"]})
    assert score_hit(passend, "Optik", eigene) > score_hit(unpassend, "Optik", eigene)


def test_bewertung_ist_nie_negativ():
    assert score_hit(_hit(title="Nichts"), "Photosynthese", ALIASES) >= 0


# --- Einzelne Signale -----------------------------------------------------
#
# Jeder Zweig der Bewertung verschiebt die Reihenfolge. Ein falsches Vorzeichen
# darin faellt sonst niemandem auf: das Ergebnis sieht weiter plausibel aus.

def test_alle_terme_im_titel_wiegen_mehr_als_einer():
    beide = score_hit(_hit(title="Optik und Akustik"), "Optik Akustik", ALIASES)
    einer = score_hit(_hit(title="Optik und Mechanik"), "Optik Akustik", ALIASES)
    assert beide > einer


def test_schlagwort_zaehlt_exakt_mehr_als_teilweise():
    exakt = score_hit(_hit(title="X", keywords=["optik"]), "Optik", ALIASES)
    teil = score_hit(_hit(title="X", keywords=["optikgeschichte"]), "Optik", ALIASES)
    assert exakt > teil > score_hit(_hit(title="X", keywords=["akustik"]), "Optik", ALIASES)


def test_alle_terme_in_schlagworten_geben_einen_zuschlag():
    alle = score_hit(_hit(title="X", keywords=["optik", "akustik"]),
                     "Optik Akustik", ALIASES)
    eines = score_hit(_hit(title="X", keywords=["optik"]), "Optik Akustik", ALIASES)
    assert alle > eines


def test_term_in_der_beschreibung_zaehlt_wenn_die_phrase_fehlt():
    mit = score_hit(_hit(title="X", keywords=["optik"],
                         description="handelt von Akustik"), "Optik Akustik", ALIASES)
    ohne = score_hit(_hit(title="X", keywords=["optik"],
                          description="handelt von Geologie"), "Optik Akustik", ALIASES)
    assert mit > ohne


def test_echtes_vorschaubild_zaehlt_ein_platzhaltersymbol_nicht():
    """isIcon markiert das generische Symbol, das edu-sharing setzt, wenn es
    kein Vorschaubild gibt."""
    echt = score_hit(_hit(title="Optik", preview={"url": "https://x/p.png"}),
                     "Optik", ALIASES)
    symbol = score_hit(_hit(title="Optik",
                            preview={"url": "https://x/i.png", "isIcon": True}),
                       "Optik", ALIASES)
    assert echt > symbol


def test_laengere_beschreibung_zaehlt_mehr():
    lang = score_hit(_hit(title="Optik", description="x" * 150), "Optik", ALIASES)
    mittel = score_hit(_hit(title="Optik", description="x" * 50), "Optik", ALIASES)
    kurz = score_hit(_hit(title="Optik", description="x" * 10), "Optik", ALIASES)
    assert lang > mittel > kurz


def test_eine_quelladresse_zaehlt():
    with_url = SearchHit(id="a", title="Optik", url="https://x/y",
                         source_url="https://quelle.test/m", raw={"properties": {}})
    without = SearchHit(id="a", title="Optik", url="https://x/y", raw={"properties": {}})
    assert score_hit(with_url, "Optik", ALIASES) > score_hit(without, "Optik", ALIASES)


# Die Rangfusion ist am 27.08.2026 entfernt worden. Sie gewichtete die Position
# eines Treffers in der Serverantwort -- und die ist gemessen nicht stabil (15
# von 25 Treffern unterscheiden sich zwischen zwei identischen Anfragen). Damit
# hing die Reihenfolge daran, in welcher Folge die Kandidaten eintrafen: von 30
# Mischungen derselben Kandidatenmenge ergaben nur 14 dasselbe Ergebnis.
#
# Was die Uebereinstimmung ueber Varianten angeht, bleibt in rerank.py erhalten
# -- gezaehlt wird jetzt, WELCHE Varianten einen Treffer lieferten, nicht an
# welcher Stelle. Der Nachweis dafuer steht in test_flows_rerank.py unter
# test_gleiche_kandidaten_ergeben_dieselbe_reihenfolge.
