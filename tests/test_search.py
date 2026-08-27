"""Suche mit Filtern und Facetten.

Antwortformen gemessen gegen edu-sharing 11.0 (Staging, 27.08.2026):
``{nodes, pagination{total,from,count}, facets[{property,values[{value,count}],
sumOtherDocCount}], suggests, ignored}``.
"""

import json

import httpx
import pytest

from edusharing.errors import ValidationError
from edusharing.search import Search
from edusharing.transport import Transport
from edusharing.vocab import Vocabulary

REPO = "https://repository.staging.openeduhub.net/edu-sharing"

FAECHER = {"values": [
    {"key": "http://w3id.org/openeduhub/vocabs/discipline/080", "displayString": "Biologie"},
    {"key": "http://w3id.org/openeduhub/vocabs/discipline/460", "displayString": "Physik"},
]}

TREFFER = {
    "nodes": [{
        "ref": {"id": "1f71f84a-a67d-4b93-b55f-3ba4f39571d8", "repo": "local"},
        "title": "Feuerspuren im Satellitenbild",
        "mimetype": "text/html",
        "mediatype": "link",
        "downloadUrl": "https://repo.test/download",
        "properties": {
            "cclom:general_description": ["Ein Text ueber Oekosysteme"],
            "ccm:taxonid": ["http://w3id.org/openeduhub/vocabs/discipline/080"],
            "ccm:taxonid_DISPLAYNAME": ["Biologie"],
            "ccm:wwwurl": ["https://beispiel.test/material"],
        },
    }],
    "pagination": {"total": 211, "from": 0, "count": 1},
    "facets": [{
        "property": "ccm:taxonid",
        "values": [
            {"value": "http://w3id.org/openeduhub/vocabs/discipline/080", "count": 57},
            {"value": "http://w3id.org/openeduhub/vocabs/discipline/460", "count": 12},
        ],
        "sumOtherDocCount": 30,
    }],
    "suggests": [],
    "ignored": [],
}


def _suche(handler, aufrufe=None, **kwargs):
    def wrapped(request: httpx.Request) -> httpx.Response:
        if aufrufe is not None:
            aufrufe.append(request)
        return handler(request)

    transport = Transport(
        REPO, client=httpx.AsyncClient(transport=httpx.MockTransport(wrapped)),
        backoff_base=0.0,
    )
    vocab = Vocabulary(transport, metadataset="mds_oeh")
    return Search(transport, vocab, metadataset="mds_oeh", **kwargs)


def _router(request: httpx.Request) -> httpx.Response:
    if "/values" in str(request.url):
        return httpx.Response(200, json=FAECHER)
    return httpx.Response(200, json=TREFFER)


def _body(request: httpx.Request) -> dict:
    return json.loads(request.content)


# --- Ergebnisform ---------------------------------------------------------

async def test_treffer_tragen_id_titel_und_url():
    """Ohne ID und URL kann niemand auf einen Treffer zurueckkommen -- und ein
    Sprachmodell paraphrasiert genau diese beiden Angaben weg."""
    e = await _suche(_router).search("Photosynthese")
    treffer = e.hits[0]
    assert treffer.id == "1f71f84a-a67d-4b93-b55f-3ba4f39571d8"
    assert treffer.title == "Feuerspuren im Satellitenbild"
    assert treffer.url == f"{REPO}/components/render/1f71f84a-a67d-4b93-b55f-3ba4f39571d8"


async def test_gesamtzahl_kommt_aus_der_paginierung():
    e = await _suche(_router).search("Photosynthese")
    assert e.total == 211
    assert len(e.hits) == 1


async def test_beschreibung_und_quell_url():
    e = await _suche(_router).search("Photosynthese")
    assert e.hits[0].description == "Ein Text ueber Oekosysteme"
    assert e.hits[0].source_url == "https://beispiel.test/material"


async def test_labels_kommen_aus_den_displayname_feldern():
    """edu-sharing liefert zu jedem Vokabularfeld ein <prop>_DISPLAYNAME mit.
    Das erspart eine zweite Anfrage, nur um eine URI lesbar zu machen."""
    e = await _suche(_router).search("Photosynthese")
    assert e.hits[0].labels("ccm:taxonid") == ["Biologie"]


async def test_rohdaten_bleiben_erreichbar():
    e = await _suche(_router).search("Photosynthese")
    assert e.hits[0].raw["properties"]["ccm:wwwurl"] == ["https://beispiel.test/material"]


# --- Suchwort und Filter --------------------------------------------------

async def test_suchwort_wird_als_ngsearchword_gesendet():
    aufrufe = []
    await _suche(_router, aufrufe).search("Photosynthese")
    kriterien = _body(aufrufe[-1])["criteria"]
    assert {"property": "ngsearchword", "values": ["Photosynthese"]} in kriterien


async def test_filter_label_wird_zur_uri_aufgeloest():
    """Der Kern: die aufrufende Person schreibt 'Biologie', gefiltert wird auf
    die URI, die DIESE Instanz dafuer fuehrt."""
    aufrufe = []
    await _suche(_router, aufrufe).search("x", filters={"ccm:taxonid": "Biologie"})
    kriterien = _body(aufrufe[-1])["criteria"]
    assert {"property": "ccm:taxonid",
            "values": ["http://w3id.org/openeduhub/vocabs/discipline/080"]} in kriterien


async def test_mehrere_werte_je_filter():
    aufrufe = []
    await _suche(_router, aufrufe).search(
        "x", filters={"ccm:taxonid": ["Biologie", "Physik"]})
    werte = next(k["values"] for k in _body(aufrufe[-1])["criteria"]
                 if k["property"] == "ccm:taxonid")
    assert len(werte) == 2


async def test_unaufloesbarer_filter_wird_gemeldet_nicht_verschluckt():
    """Eine stillschweigend verworfene Einschraenkung liefert Treffer, die
    niemand angefragt hat -- schlimmer als gar kein Ergebnis."""
    e = await _suche(_router).search("x", filters={"ccm:taxonid": "Unterwasserkorbflechten"})
    assert e.unresolved
    assert e.unresolved[0].field == "ccm:taxonid"
    assert e.unresolved[0].value == "Unterwasserkorbflechten"


async def test_unaufloesbarer_filter_wird_nicht_mitgesendet():
    aufrufe = []
    await _suche(_router, aufrufe).search("x", filters={"ccm:taxonid": "Quatsch"})
    props = [k["property"] for k in _body(aufrufe[-1])["criteria"]]
    assert "ccm:taxonid" not in props


async def test_unaufloesbarer_filter_liefert_vorschlaege():
    """Damit eine Anwendung zurueckfragen kann statt nur zu scheitern."""
    e = await _suche(_router).search("x", filters={"ccm:taxonid": "Bio"})
    assert "Biologie" in e.unresolved[0].suggestions


async def test_suche_ohne_suchwort_ist_erlaubt():
    """Nur filtern, ohne Volltext -- etwa fuer 'alles Material zu Biologie'."""
    aufrufe = []
    await _suche(_router, aufrufe).search(filters={"ccm:taxonid": "Biologie"})
    props = [k["property"] for k in _body(aufrufe[-1])["criteria"]]
    assert "ngsearchword" not in props


# --- Feld-Aliase ----------------------------------------------------------

async def test_alias_wird_auf_die_property_abgebildet():
    """'fach' statt 'ccm:taxonid' -- das ist der 'wenig Code'-Teil."""
    aufrufe = []
    await _suche(_router, aufrufe).search("x", fach="Biologie")
    props = [k["property"] for k in _body(aufrufe[-1])["criteria"]]
    assert "ccm:taxonid" in props


async def test_aliase_sind_ueberschreibbar():
    """Eine Instanz mit anderen Feldnamen darf ihre eigene Zuordnung setzen --
    sonst waere die Bequemlichkeitsschicht eine versteckte Annahme."""
    aufrufe = []
    s = _suche(_router, aufrufe, field_aliases={"thema": "ccm:taxonid"})
    await s.search("x", thema="Biologie")
    props = [k["property"] for k in _body(aufrufe[-1])["criteria"]]
    assert "ccm:taxonid" in props


async def test_unbekannter_alias_wird_abgelehnt():
    """Ein Tippfehler im Feldnamen darf nicht als 'keine Einschraenkung'
    durchgehen."""
    with pytest.raises(ValidationError, match="voelligNeu"):
        await _suche(_router).search("x", voelligNeu="Biologie")


# --- Nicht filterbare Properties ------------------------------------------

async def test_nicht_filterbare_property_wird_erklaert():
    """Gemessen: ``ccm:taxonid`` hat im Metadatensatz '-default-' ein
    Vokabular, ist dort aber NICHT filterbar -- die Abfrage endet mit
    ``400 Could not find parameter ccm:taxonid in the query ngsearch``.
    In 'mds_oeh' geht dieselbe Property.

    Ein Vokabular zu haben sagt also nichts ueber Filterbarkeit. Die nackte
    Servermeldung laesst genau das offen, deshalb ergaenzt die Bibliothek den
    entscheidenden Hinweis: es liegt am Metadatensatz.
    """
    def handler(request):
        if "/values" in str(request.url):
            return httpx.Response(200, json=FAECHER)
        return httpx.Response(400, json={
            "error": "org.edu_sharing.restservices.DAOValidationException",
            "message": "java.lang.IllegalArgumentException: Could not find "
                       "parameter ccm:taxonid in the query ngsearch",
        })

    with pytest.raises(ValidationError) as info:
        await _suche(handler).search("x", filters={"ccm:taxonid": "Biologie"})
    text = str(info.value)
    assert "ccm:taxonid" in text
    assert "mds_oeh" in text, "der verwendete Metadatensatz muss genannt werden"
    assert "metadataset" in text, "der Ausweg muss genannt werden"


async def test_urspruenglicher_fehler_bleibt_erhalten():
    """Die Servermeldung darf nicht verschwinden -- sie ist die Primaerquelle."""
    def handler(request):
        if "/values" in str(request.url):
            return httpx.Response(200, json=FAECHER)
        return httpx.Response(400, json={
            "error": "org.edu_sharing.restservices.DAOValidationException",
            "message": "Could not find parameter ccm:taxonid in the query ngsearch",
        })

    with pytest.raises(ValidationError) as info:
        await _suche(handler).search("x", filters={"ccm:taxonid": "Biologie"})
    assert info.value.__cause__ is not None
    assert "Could not find parameter" in str(info.value.__cause__)


async def test_andere_validierungsfehler_werden_nicht_umgedeutet():
    """Nur die 'unbekanntes Kriterium'-Meldung wird angereichert."""
    def handler(request):
        if "/values" in str(request.url):
            return httpx.Response(200, json=FAECHER)
        return httpx.Response(400, json={
            "error": "org.edu_sharing.restservices.DAOValidationException",
            "message": "irgendein anderes Problem",
        })

    with pytest.raises(ValidationError) as info:
        await _suche(handler).search("x")
    assert "metadataset" not in str(info.value)


# --- Facetten -------------------------------------------------------------

async def test_facetten_kommen_mit_zaehlern_zurueck():
    e = await _suche(_router).search("x", facets=["ccm:taxonid"])
    assert e.facets[0].property == "ccm:taxonid"
    assert e.facets[0].values[0].count == 57


async def test_facetten_werden_angefordert():
    aufrufe = []
    await _suche(_router, aufrufe).search("x", facets=["ccm:taxonid"], facet_limit=5)
    body = _body(aufrufe[-1])
    assert body["facets"] == [{"property": "ccm:taxonid"}]
    assert body["facetLimit"] == 5


async def test_ohne_facetten_wird_nichts_angefordert():
    """Facetten kosten serverseitige Aggregation ueber die ganze Ergebnismenge."""
    aufrufe = []
    await _suche(_router, aufrufe).search("x")
    assert "facets" not in _body(aufrufe[-1])


async def test_abgeschnittene_facette_ist_erkennbar():
    """sumOtherDocCount > 0 heisst: die Liste ist gekuerzt. Eine Summe darueber
    saehe autoritativ aus und waere zu klein."""
    e = await _suche(_router).search("x", facets=["ccm:taxonid"])
    assert e.facets[0].truncated is True
    assert e.facets[0].other_count == 30


# --- Paginierung und Optionen ---------------------------------------------

async def test_limit_und_offset_gehen_in_die_query():
    aufrufe = []
    await _suche(_router, aufrufe).search("x", limit=25, offset=50)
    url = str(aufrufe[-1].url)
    assert "maxItems=25" in url
    assert "skipCount=50" in url


async def test_vorschlaege_werden_angefordert():
    """Ohne das Flag bekommt ein Tippfehler 'keine Treffer' und nichts, womit
    sich ein zweiter Versuch bauen liesse."""
    aufrufe = []
    await _suche(_router, aufrufe).search("Mathematick")
    assert _body(aufrufe[-1])["returnSuggestions"] is True


async def test_suchwort_wird_nicht_gecacht_wie_vokabular():
    """Zwei verschiedene Suchen muessen zwei Anfragen ausloesen."""
    aufrufe = []
    s = _suche(_router, aufrufe)
    await s.search("a")
    await s.search("b")
    suchen = [r for r in aufrufe if "/ngsearch" in str(r.url)]
    assert len(suchen) == 2
