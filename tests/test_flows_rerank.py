"""Die Suche mit rerank=True.

Der Ablauf faehrt mehrere Anfragevarianten, mischt die Ranglisten und ordnet
nach Textqualitaet neu. Das kostet mehrere Anfragen und ist deshalb nicht die
Vorgabe -- wer es einschaltet, tauscht Anfragen gegen Trefferqualitaet.

Die wichtigste Eigenschaft steht im letzten Abschnitt: scheitern **alle**
Varianten, ist das kein leeres Ergebnis, sondern eine Suche, die nicht
stattgefunden hat. Der Unterschied entscheidet, ob ein Sprachmodell "nichts
gefunden" oder "ich konnte nicht suchen" sagt.
"""

import httpx
import pytest

from edusharing import AsyncRepository
from edusharing.errors import EduSharingError

REPO = "https://repo.test/edu-sharing"

FAECHER = {"values": [
    {"key": "http://x/080", "displayString": "Biologie"},
]}


def _knoten(node_id: str, titel: str, **props) -> dict:
    return {
        "ref": {"id": node_id},
        "title": titel,
        "properties": {"cclom:title": [titel], **props},
    }


class Instanz:
    """Ein Mock, der je Suchtext eine eigene Trefferliste liefert."""

    def __init__(self, nach_text: dict[str, list[dict]], total: int = 100) -> None:
        self.nach_text = nach_text
        self.total = total
        self.gesuchte_texte: list[str] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        if "/values" in request.url.path:
            return httpx.Response(200, json=FAECHER)
        import json as _json
        koerper = _json.loads(request.content) if request.content else {}
        text = ""
        for kriterium in koerper.get("criteria", []):
            if kriterium.get("property") == "ngsearchword":
                text = (kriterium.get("values") or [""])[0]
        self.gesuchte_texte.append(text)
        knoten = self.nach_text.get(text, [])
        return httpx.Response(200, json={
            "nodes": knoten,
            "pagination": {"total": self.total, "from": 0, "count": len(knoten)},
        })


def _repo(instanz, **kwargs) -> AsyncRepository:
    return AsyncRepository(
        REPO, metadataset="mds_oeh", backoff_base=0.0,
        client=httpx.AsyncClient(transport=httpx.MockTransport(instanz)), **kwargs)


# --- Rahmenwoerter im Ablauf ---------------------------------------------

async def test_rahmenwoerter_werden_wirklich_zusaetzlich_gesucht():
    """Der gemessene Fall: die volle Formulierung findet nichts, das Thema
    allein findet alles. Ohne die Themenvariante meldet der Ablauf null."""
    instanz = Instanz({
        "Ich suche ein Arbeitsblatt zur Bruchrechnung": [],
        "bruchrechnung": [_knoten("a", "Bruchrechnung üben")],
    })
    async with _repo(instanz) as repo:
        ergebnis = await repo.flows.search(
            "Ich suche ein Arbeitsblatt zur Bruchrechnung", rerank=True)

    assert "bruchrechnung" in instanz.gesuchte_texte
    assert ergebnis["returned"] == 1
    assert ergebnis["hits"][0]["id"] == "a"


async def test_ohne_rerank_bleibt_es_bei_einer_anfrage():
    """Die Vorgabe kostet nichts extra."""
    instanz = Instanz({"Arbeitsblatt zur Bruchrechnung": []})
    async with _repo(instanz) as repo:
        await repo.flows.search("Arbeitsblatt zur Bruchrechnung")
    assert len(instanz.gesuchte_texte) == 1


# --- Neuordnung -----------------------------------------------------------

async def test_titeltreffer_wird_nach_oben_sortiert():
    """Das Repositorium ordnet nach seinem Indexwert. Der weiss nicht, dass ein
    Titeltreffer mehr wiegt als eine Erwaehnung im Fliesstext."""
    instanz = Instanz({"Photosynthese": [
        _knoten("schwach", "Botanik allgemein",
                **{"cclom:general_description": ["am Rande auch Photosynthese"]}),
        _knoten("stark", "Photosynthese"),
    ]})
    async with _repo(instanz) as repo:
        ergebnis = await repo.flows.search("Photosynthese", rerank=True)
    assert [h["id"] for h in ergebnis["hits"]] == ["stark", "schwach"]


async def test_geloeschte_platzhalter_fallen_heraus():
    """edu-sharing liefert geloeschte Elemente als Platzhalter mit -- fuer ein
    Sprachmodell sind das Treffer wie jeder andere."""
    instanz = Instanz({"Optik": [
        _knoten("weg", "Element wurde gelöscht"),
        _knoten("da", "Optik im Alltag"),
    ]})
    async with _repo(instanz) as repo:
        ergebnis = await repo.flows.search("Optik", rerank=True)
    assert [h["id"] for h in ergebnis["hits"]] == ["da"]


async def test_gleiche_kandidaten_ergeben_dieselbe_reihenfolge():
    """Die Zusage der Neuordnung: sie ist eine Formel ueber die Kandidaten, kein
    Nachsortieren der Serverreihenfolge.

    Der Grund, warum das zaehlt: die Suche liefert dieselbe Anfrage mit anderen
    Kandidaten in anderer Reihenfolge (gemessen 27.08.2026, 15 von 25
    unterschiedlich). Flosse die Position der Kandidaten in die Bewertung ein,
    truege die Neuordnung dieses Rauschen weiter -- und der Aufrufer koennte
    zwei Laeufe nicht vergleichen, ohne zu wissen, ob sich die Bewertung oder
    nur die Serverlaune geaendert hat.
    """
    import random

    kandidaten = [
        _knoten("n0", "Optik"),
        _knoten("n1", "Optik im Alltag", **{"ccm:taxonid": ["http://x/080"]}),
        _knoten("n2", "Einfuehrung in die Optik"),
        _knoten("n3", "Physik allgemein",
                **{"cclom:general_description": ["auch Optik"]}),
        _knoten("n4", "Optik", **{"ccm:educationalcontext": ["http://x/s1"]}),
        _knoten("n5", "Wellenoptik und Strahlenoptik"),
        _knoten("n6", "Akustik"),
    ]

    async def ergebnis_fuer(reihung):
        instanz = Instanz({"Optik": reihung})
        async with _repo(instanz) as repo:
            antwort = await repo.flows.search("Optik", rerank=True, limit=7)
        return [h["id"] for h in antwort["hits"]]

    erwartet = await ergebnis_fuer(kandidaten)
    wuerfel = random.Random(42)
    for lauf in range(15):
        gemischt = kandidaten[:]
        wuerfel.shuffle(gemischt)
        assert await ergebnis_fuer(gemischt) == erwartet, (
            f"Mischung {lauf} ergab eine andere Reihenfolge -- die Position der "
            "Kandidaten darf die Bewertung nicht beeinflussen")


async def test_reihenfolge_ist_bei_gleichem_wert_stabil():
    """Ohne festen Tie-Break wechselt die Reihenfolge zwischen Aufrufen und
    sieht fuer den Aufrufer zufaellig aus."""
    knoten = [_knoten(f"n{i}", "Optik") for i in range(5)]
    laeufe = []
    for _ in range(3):
        instanz = Instanz({"Optik": list(reversed(knoten))})
        async with _repo(instanz) as repo:
            ergebnis = await repo.flows.search("Optik", rerank=True)
        laeufe.append([h["id"] for h in ergebnis["hits"]])
    assert laeufe[0] == laeufe[1] == laeufe[2]


async def test_limit_wird_eingehalten():
    instanz = Instanz({"Optik": [_knoten(f"n{i}", f"Optik {i}") for i in range(20)]})
    async with _repo(instanz) as repo:
        ergebnis = await repo.flows.search("Optik", rerank=True, limit=3)
    assert ergebnis["returned"] == 3


async def test_gesamtzahl_bleibt_die_des_repositoriums():
    """Die Poolgroesse ist ein Werkzeug der Neuordnung, keine Aussage darueber,
    wie viel es gibt. Wer hier die Poolgroesse meldete, untertriebe massiv."""
    instanz = Instanz({"Optik": [_knoten("a", "Optik")]}, total=1345)
    async with _repo(instanz) as repo:
        ergebnis = await repo.flows.search("Optik", rerank=True, limit=1)
    assert ergebnis["total"] == 1345


async def test_die_gefahrenen_varianten_stehen_im_ergebnis():
    """Nachvollziehbarkeit: sonst ist nicht erklaerbar, warum ein Treffer oben
    steht."""
    instanz = Instanz({"Arbeitsblatt zur Optik": [], "optik": [_knoten("a", "Optik")]})
    async with _repo(instanz) as repo:
        ergebnis = await repo.flows.search("Arbeitsblatt zur Optik", rerank=True)
    assert ergebnis["query"]["reranked"] is True
    assert "topic" in ergebnis["query"]["variants"]


# --- Fehlerfall -----------------------------------------------------------

async def test_wenn_alle_varianten_scheitern_ist_das_ein_fehler():
    """Die wichtigste Eigenschaft. Im wlo-mcp-sc gemessen am 31.07.2026: ein
    falsches Dienstpasswort machte jede Anfrage zu einem 401, und die Suche
    antwortete "Gefundene Treffer gesamt: 0" -- ohne jede Fehlermeldung.

    Damit wird ein Konfigurationsfehler zu einer scheinbaren Tatsache ueber die
    Welt, und das Modell gibt sie als solche weiter."""
    def kaputt(request: httpx.Request) -> httpx.Response:
        if "/values" in request.url.path:
            return httpx.Response(200, json=FAECHER)
        return httpx.Response(401, json={"error": "nicht angemeldet"})

    async with _repo(kaputt) as repo:
        with pytest.raises(EduSharingError):
            await repo.flows.search("Arbeitsblatt zur Optik", rerank=True)


async def test_eine_scheiternde_variante_ist_kein_grund_aufzugeben():
    """Dafuer sind mehrere Varianten da."""
    def teilweise(request: httpx.Request) -> httpx.Response:
        import json as _json
        if "/values" in request.url.path:
            return httpx.Response(200, json=FAECHER)
        koerper = _json.loads(request.content) if request.content else {}
        text = ""
        for k in koerper.get("criteria", []):
            if k.get("property") == "ngsearchword":
                text = (k.get("values") or [""])[0]
        if text == "optik":
            return httpx.Response(500, json={"error": "kaputt"})
        return httpx.Response(200, json={
            "nodes": [_knoten("a", "Optik")],
            "pagination": {"total": 5, "from": 0, "count": 1}})

    async with _repo(teilweise) as repo:
        ergebnis = await repo.flows.search("Arbeitsblatt zur Optik", rerank=True)
    assert ergebnis["returned"] == 1
    assert ergebnis["warnings"], "der Ausfall gehoert benannt, nicht verschwiegen"


async def test_gesamtzahl_folgt_der_variante_die_etwas_fand():
    """Live aufgefallen am 27.08.2026: die Grundvariante fand 0, die
    Themenvariante 1591 -- gemeldet wurden "3 Treffer, total 0".

    Das ist nicht bloss unschoen, es ist widerspruechlich. Ein Sprachmodell
    liest daraus "es gibt nichts" und gibt es so weiter, waehrend drei Treffer
    danebenstehen. Gemeldet wird deshalb das Maximum ueber die Varianten, und
    weil sich ueberlappende Varianten nicht addieren lassen, als untere
    Schranke."""
    class Verschieden(Instanz):
        def __call__(self, request):
            antwort = super().__call__(request)
            if "/values" in request.url.path:
                return antwort
            import json as _json
            daten = _json.loads(antwort.content)
            # Die volle Formulierung findet nichts, das Thema findet viel.
            gesucht = self.gesuchte_texte[-1]
            daten["pagination"]["total"] = 0 if gesucht.startswith("Ich suche") else 1591
            return httpx.Response(200, json=daten)

    instanz = Verschieden({
        "Ich suche ein Arbeitsblatt zur Bruchrechnung": [],
        "bruchrechnung": [_knoten("a", "Bruchrechnung")],
    })
    async with _repo(instanz) as repo:
        ergebnis = await repo.flows.search(
            "Ich suche ein Arbeitsblatt zur Bruchrechnung", rerank=True)

    assert ergebnis["returned"] == 1
    assert ergebnis["total"] == 1591, "0 zu melden waere das Gegenteil der Wahrheit"
    assert ergebnis["total_is_lower_bound"] is True


async def test_ein_treffer_ohne_titel_gilt_als_geloescht():
    """edu-sharing liefert geloeschte Elemente auch ohne Titel aus."""
    instanz = Instanz({"Optik": [
        {"ref": {"id": "leer"}, "title": "  ", "properties": {}},
        _knoten("da", "Optik"),
    ]})
    async with _repo(instanz) as repo:
        ergebnis = await repo.flows.search("Optik", rerank=True)
    assert [h["id"] for h in ergebnis["hits"]] == ["da"]


async def test_rerank_ohne_suchtext_faellt_auf_die_normale_suche_zurueck():
    """Eine reine Filteranfrage hat nichts, wogegen sich ordnen liesse."""
    instanz = Instanz({"": [_knoten("a", "Irgendwas")]})
    async with _repo(instanz) as repo:
        ergebnis = await repo.flows.search(None, rerank=True, subject="Biologie")
    assert "reranked" not in ergebnis["query"]
    assert len(instanz.gesuchte_texte) == 1
