"""Treffer fuer den Modellkontext aufbereiten.

Zwei Anforderungen, die sich widersprechen: der Kontext ist begrenzt, und
``id`` und ``url`` duerfen auf keinen Fall wegfallen -- genau die sind es, die
ein Sprachmodell beim Zusammenfassen als Erstes verliert, und ohne sie kann
niemand auf einen Treffer zurueckkommen.

Budgetiert wird in **Zeichen**, nicht in Token: Zeichen sind exakt zaehlbar,
eine Token-Schaetzung ohne den Tokenizer des Zielmodells waere geraten.
"""

import pytest

from edusharing.agent.format import cap_text, format_hit, format_results
from edusharing.results import SearchHit, SearchResult, UnresolvedFilter

REPO = "https://repo.test/edu-sharing"


def _hit(n: int = 1, beschreibung: str = "Eine Beschreibung") -> SearchHit:
    return SearchHit(
        id=f"id-{n}",
        title=f"Titel {n}",
        url=f"{REPO}/components/render/id-{n}",
        description=beschreibung,
        raw={"properties": {"ccm:taxonid_DISPLAYNAME": ["Biologie"]}},
    )


# --- cap_text --------------------------------------------------------------

def test_kurzer_text_bleibt_unveraendert():
    assert cap_text("kurz", 100) == "kurz"


def test_langer_text_wird_gekappt():
    assert len(cap_text("a" * 500, 100)) <= 100


def test_kappung_ist_sichtbar():
    """Ein stillschweigend abgeschnittener Text sieht aus wie ein
    vollstaendiger -- und ein Modell zitiert ihn als solchen."""
    gekappt = cap_text("Wort " * 200, 60)
    assert gekappt.endswith("…")


def test_kappung_bricht_nicht_mitten_im_wort():
    gekappt = cap_text("Donaudampfschifffahrt " * 20, 40)
    assert "Donaudampfschifff…" not in gekappt


def test_leere_eingabe():
    assert cap_text("", 10) == ""
    assert cap_text(None, 10) == ""


def test_unsinniges_budget_wird_abgelehnt():
    with pytest.raises(ValueError):
        cap_text("x", 0)


# --- format_hit ------------------------------------------------------------

def test_treffer_traegt_titel_id_und_url():
    text = format_hit(_hit())
    assert "Titel 1" in text
    assert "id-1" in text
    assert f"{REPO}/components/render/id-1" in text


def test_die_beschreibung_wird_gekuerzt_nicht_der_rueckverweis():
    text = format_hit(_hit(beschreibung="Sehr lang. " * 200), max_chars=200)
    assert f"{REPO}/components/render/id-1" in text
    assert len(text) <= 200
    assert text.rstrip().endswith("…"), "die Beschreibung muesste gekuerzt sein"


def test_rueckverweis_ueberlebt_auch_ein_budget_das_nicht_reicht():
    """Die bewusste Ausnahme: passt nicht einmal der Kopf ins Budget, gewinnt
    der Rueckverweis und das Budget wird ueberschritten.

    Ein Treffer ohne id und url ist wertlos -- niemand kann auf ihn
    zurueckkommen. Ein um wenige Zeichen zu langer Block ist dagegen ein
    Schoenheitsfehler. Wer hart begrenzen muss, prueft die Laenge selbst.
    """
    text = format_hit(_hit(beschreibung="Sehr lang. " * 200), max_chars=20)
    assert "id-1" in text
    assert f"{REPO}/components/render/id-1" in text
    assert len(text) > 20, "hier ist die Ueberschreitung beabsichtigt"


def test_ohne_platz_faellt_die_beschreibung_ganz_weg():
    text = format_hit(_hit(beschreibung="Eine Beschreibung"), max_chars=20)
    assert "Eine Beschreibung" not in text


async def test_fremdinhalt_wird_bereinigt():
    """Titel und Beschreibung stammen von beliebigen Personen."""
    hit = SearchHit(id="x", title="Titel\u200bmit\u202eTricks", url=f"{REPO}/x",
                    description="Be\u200cschreibung")
    text = format_hit(hit)
    assert "\u200b" not in text
    assert "\u202e" not in text


def test_fehlende_beschreibung_ist_kein_problem():
    hit = SearchHit(id="x", title="Nur Titel", url=f"{REPO}/x", description=None)
    assert "Nur Titel" in format_hit(hit)


def test_labels_werden_mitgegeben_wenn_vorhanden():
    """Ein Modell soll das Fach nennen koennen, ohne die URI aufzuloesen."""
    assert "Biologie" in format_hit(_hit())


# --- format_results --------------------------------------------------------

def test_ergebnisliste_nennt_die_gesamtzahl():
    ergebnis = SearchResult(hits=[_hit(1), _hit(2)], total=211)
    text = format_results(ergebnis)
    assert "211" in text


def test_alle_treffer_erscheinen_wenn_das_budget_reicht():
    ergebnis = SearchResult(hits=[_hit(1), _hit(2), _hit(3)], total=3)
    text = format_results(ergebnis, max_chars=5000)
    assert all(f"id-{n}" in text for n in (1, 2, 3))


def test_budget_wird_eingehalten():
    ergebnis = SearchResult(hits=[_hit(n) for n in range(50)], total=50)
    text = format_results(ergebnis, max_chars=600)
    assert len(text) <= 600


def test_weggelassene_treffer_werden_benannt():
    """Sonst haelt das Modell die gezeigten fuer alle -- und antwortet
    zuversichtlich auf einer Teilmenge."""
    ergebnis = SearchResult(hits=[_hit(n) for n in range(50)], total=211)
    text = format_results(ergebnis, max_chars=600)
    assert "weitere" in text.lower() or "von 211" in text


def test_leeres_ergebnis_wird_als_solches_gemeldet():
    text = format_results(SearchResult(hits=[], total=0))
    assert "keine" in text.lower()


def test_korrekturvorschlaege_erscheinen():
    """Bei einem Tippfehler ist der Vorschlag die einzige brauchbare
    Information -- ohne ihn meldet das Modell nur Misserfolg."""
    ergebnis = SearchResult(hits=[], total=0, suggestions=["mathematik"])
    assert "mathematik" in format_results(ergebnis)


def test_unaufgeloeste_filter_erscheinen():
    """Das Ergebnis ist dann breiter als angefragt -- wer das verschweigt,
    laesst das Modell eine falsche Praemisse uebernehmen."""
    ergebnis = SearchResult(
        hits=[_hit(1)], total=1,
        unresolved=[UnresolvedFilter(field="ccm:taxonid", value="Bio",
                                     suggestions=["Biologie"])])
    text = format_results(ergebnis)
    assert "ccm:taxonid" in text
    assert "Biologie" in text


def test_warnungen_erscheinen():
    ergebnis = SearchResult(hits=[], total=0, warnings=["Ein Weg ist ausgefallen"])
    assert "ausgefallen" in format_results(ergebnis)


# --- Rauschen in der Ausgabe ----------------------------------------------

def test_null_labels_werden_nicht_ausgegeben():
    """Live gesehen: manche Datensaetze tragen den String 'null' als
    _DISPLAYNAME. Ihn dem Modell als Fachangabe vorzusetzen ist schlicht
    falsch."""
    hit = SearchHit(id="x", title="T", url=f"{REPO}/x", description=None,
                    raw={"properties": {"ccm:taxonid_DISPLAYNAME": ["Biologie", "null", ""]}})
    text = format_hit(hit)
    assert "Biologie" in text
    assert "null" not in text


def test_vorschlaege_nur_wenn_nichts_gefunden_wurde():
    """Live gesehen: der Server liefert 'Meinten Sie photosynthese?' auch bei
    57 Treffern. Im Modellkontext liest sich das wie ein Zweifel am Ergebnis."""
    mit_treffern = SearchResult(hits=[_hit(1)], total=57, suggestions=["photosynthese"])
    assert "Meinten Sie" not in format_results(mit_treffern)

    ohne = SearchResult(hits=[], total=0, suggestions=["mathematik"])
    assert "Meinten Sie" in format_results(ohne)


def test_labels_lassen_sich_einschraenken():
    """Welche Vokabularfelder in den Kontext gehoeren, entscheidet der
    Metadatensatz der Instanz -- nicht diese Bibliothek. Ohne Angabe kommen
    alle; wer weiss, welche zaehlen, nennt sie.

    Der Fall aus der Praxis: ccm:containsAdvertisement_DISPLAYNAME ist 'nein'
    -- ein korrekter Wert, der ohne sein Feld gelesen nur verwirrt.
    """
    hit = SearchHit(id="x", title="T", url=f"{REPO}/x", description=None, raw={
        "properties": {
            "ccm:taxonid_DISPLAYNAME": ["Biologie"],
            "ccm:containsAdvertisement_DISPLAYNAME": ["nein"],
        }})
    assert "nein" in format_hit(hit)
    beschraenkt = format_hit(hit, label_properties=["ccm:taxonid"])
    assert "Biologie" in beschraenkt
    assert "nein" not in beschraenkt
