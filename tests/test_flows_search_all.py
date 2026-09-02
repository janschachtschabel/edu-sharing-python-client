"""Material und Sammlungen in einem Aufruf.

Der wlo-mcp-sc nennt das sein Standardwerkzeug, und zu Recht: wer nach einem
Thema fragt, will beides -- die einzelnen Materialien und die Sammlungen, in
denen jemand schon zusammengestellt hat, was dazugehoert. Zwei Endpunkte, zwei
Antwortformen, und bisher zwei Aufrufe.

Der Haken, den dieser Ablauf sichtbar machen muss: **die Sammlungssuche nimmt
keine Filter.** Gemessen und in ``collections.py`` festgehalten -- die Abfrage
akzeptiert ``ngsearchword`` und sonst nichts, jedes weitere Kriterium endet in
``400 DAOValidationException``. Wer ``search_all("Zelle", subject="Biologie")``
aufruft, bekam gefiltertes Material und **ungefilterte** Sammlungen -- bis
``find_collections`` Kurznamen lokal anwendet (02.09.2026). Seitdem gilt ein
Kurzname fuer beide Koerbe; nur rohe ``filters`` bleiben den Sammlungen fremd
und werden genannt. Das stillschweigend zu tun hiesse, eine Einschraenkung
zu behaupten, die es nicht gibt.
"""

import json

import httpx
import pytest

from edusharing import AsyncRepository
from edusharing.errors import EduSharingError

REPO = "https://repo.test/edu-sharing"

FAECHER = {"values": [{"key": "http://vocab.test/080", "displayString": "Biologie"}]}


def _knoten(node_id: str, titel: str) -> dict:
    return {"ref": {"id": node_id}, "title": titel, "type": "ccm:io",
            "properties": {"cclom:title": [titel],
                           "ccm:wwwurl": [f"https://x/{node_id}"]}}


class Instanz:
    def __init__(self, *, material: list | None = None,
                 sammlungen: list | None = None) -> None:
        self.material = [_knoten("m-1", "Zellteilung")] if material is None else material
        self.sammlungen = ([_knoten("s-1", "Sammlung Biologie")]
                           if sammlungen is None else sammlungen)
        self.anfragen: list[str] = []

    def handler(self, request: httpx.Request) -> httpx.Response:
        pfad = str(request.url.path)
        self.anfragen.append(pfad)
        if "/values" in pfad:
            return httpx.Response(200, json=FAECHER)
        if pfad.endswith("/collections") and "/search/v1" in pfad:
            return httpx.Response(200, json={
                "nodes": self.sammlungen,
                "pagination": {"total": 7, "from": 0, "count": len(self.sammlungen)}})
        if pfad.endswith("/collections/-home-/search"):
            return httpx.Response(200, json={"collections": self.sammlungen})
        return httpx.Response(200, json={
            "nodes": self.material,
            "pagination": {"total": 42, "from": 0, "count": len(self.material)}})

    def repo(self) -> AsyncRepository:
        return AsyncRepository(
            REPO, metadataset="mds_oeh", backoff_base=0.0,
            client=httpx.AsyncClient(transport=httpx.MockTransport(self.handler)))


# --- Die beiden Koerbe ----------------------------------------------------

async def test_material_und_sammlungen_getrennt():
    instanz = Instanz()
    async with instanz.repo() as repo:
        ergebnis = await repo.flows.search_all("Zelle")
    assert [h["id"] for h in ergebnis["materials"]["hits"]] == ["m-1"]
    assert [h["id"] for h in ergebnis["collections"]["hits"]] == ["s-1"]


async def test_jeder_korb_behaelt_seine_eigene_zaehlung():
    """Die Sammlungssuche fragt zwei Wege ab und fuehrt sie zusammen -- ihre
    Gesamtzahl ist eine Untergrenze, die des Materials nicht. Eine gemeinsame
    Summe wuerde beides vermischen."""
    instanz = Instanz()
    async with instanz.repo() as repo:
        ergebnis = await repo.flows.search_all("Zelle")
    assert ergebnis["materials"]["total"] == 42
    assert ergebnis["materials"]["total_is_lower_bound"] is False
    assert ergebnis["collections"]["total_is_lower_bound"] is True


async def test_die_antwort_ist_json():
    instanz = Instanz()
    async with instanz.repo() as repo:
        json.dumps(await repo.flows.search_all("Zelle"))


async def test_leere_treffer_sind_kein_fehler():
    instanz = Instanz(material=[], sammlungen=[])
    async with instanz.repo() as repo:
        ergebnis = await repo.flows.search_all("gibtesnicht")
    assert ergebnis["materials"]["hits"] == []
    assert ergebnis["collections"]["hits"] == []


# --- Der Haken ------------------------------------------------------------

async def test_kurznamen_gelten_fuer_beide_koerbe():
    """Gemessen nimmt die Sammlungsabfrage nur ngsearchword -- aber
    find_collections wendet Kurznamen seit dem 02.09.2026 lokal an. Also gilt
    subject= fuer beide Koerbe; nur rohe filters bleiben den Sammlungen fremd."""
    instanz = Instanz()
    async with instanz.repo() as repo:
        ergebnis = await repo.flows.search_all("Zelle", subject="Biologie")
    assert ergebnis["collections"]["filters_ignored"] == []
    assert ergebnis["collections"]["hits"] == [], "die Sammlung traegt kein Fach"
    assert ergebnis["collections"]["query"]["filters"] == {"subject": "Biologie"}


async def test_ohne_filter_ist_nichts_zu_melden():
    instanz = Instanz()
    async with instanz.repo() as repo:
        ergebnis = await repo.flows.search_all("Zelle")
    assert ergebnis["collections"]["filters_ignored"] == []


async def test_auch_filters_als_wortverzeichnis_wird_gemeldet():
    instanz = Instanz()
    async with instanz.repo() as repo:
        ergebnis = await repo.flows.search_all(
            "Zelle", filters={"ccm:taxonid": "Biologie"})
    assert ergebnis["collections"]["filters_ignored"] == ["ccm:taxonid"]


async def test_der_filter_erreicht_das_material_wirklich():
    """Die Gegenprobe: gemeldet wird nur, was die Sammlungen nicht koennen --
    das Material soll gefiltert sein."""
    instanz = Instanz()
    async with instanz.repo() as repo:
        ergebnis = await repo.flows.search_all("Zelle", subject="Biologie")
    assert ergebnis["materials"]["unresolved"] == []
    assert any("/values" in p for p in instanz.anfragen), "Vokabular wurde gefragt"


async def test_beide_koerbe_haben_im_ausfall_dieselben_schluessel():
    """Die dokumentierte Form gilt auch, wenn die Sammlungssuche ausfaellt --
    sonst ist answer["collections"]["unjudged"] nur in Produktion ein KeyError."""
    heil = Instanz()
    kaputt = Instanz()
    urspruenglich = kaputt.handler

    def handler(request: httpx.Request) -> httpx.Response:
        if "collection" in str(request.url).lower():
            return httpx.Response(503, json={"error": "x", "message": "Dienst weg"})
        return urspruenglich(request)

    kaputt.handler = handler
    async with heil.repo() as a, kaputt.repo() as b:
        gut = await a.flows.search_all("Zelle", subject="Biologie", include_pages=True)
        leer = await b.flows.search_all("Zelle", subject="Biologie", include_pages=True)
    assert set(gut["collections"]) == set(leer["collections"])
    assert set(gut["pages"]) == set(leer["pages"])
    assert set(gut["collections"]["query"]) == set(leer["collections"]["query"])
    assert leer["collections"]["unjudged"] == 0 and leer["collections"]["unresolved"] == []


async def test_ein_ausfall_der_sammlungen_kostet_auch_mit_seiten_nicht_das_material():
    """Audit A9, mit include_pages wieder eingebaut: find_pages lief ausserhalb
    der Ausfallbehandlung, ein 503 der Sammlungsrouten warf und verlor die
    Materialtreffer."""
    instanz = Instanz()
    urspruenglich = instanz.handler

    def handler(request: httpx.Request) -> httpx.Response:
        if "collection" in str(request.url).lower():
            return httpx.Response(503, json={"error": "x", "message": "Dienst weg"})
        return urspruenglich(request)

    instanz.handler = handler
    async with instanz.repo() as repo:
        ergebnis = await repo.flows.search_all("Zelle", include_pages=True)
    assert [h["id"] for h in ergebnis["materials"]["hits"]] == ["m-1"]
    assert ergebnis["pages"]["hits"] == [] and "503" in ergebnis["pages"]["error"]
    assert ergebnis["collections"]["hits"] == []
    json.dumps(ergebnis)


async def test_der_seitenkorb_traegt_ohne_ausfall_ein_leeres_error():
    instanz = MitSeiten()
    async with instanz.repo() as repo:
        mit = await repo.flows.search_all("Zelle", include_pages=True)
    assert mit["pages"]["error"] == ""


# --- Kosten ---------------------------------------------------------------

async def test_drei_anfragen_statt_zweier_aufrufe():
    """Eine fuer das Material, zwei fuer die Sammlungen -- deren Suche fragt
    zwei Wege ab. Alle gemeinsam gesendet."""
    instanz = Instanz()
    async with instanz.repo() as repo:
        await repo.flows.search_all("Zelle")
    assert len(instanz.anfragen) == 3, instanz.anfragen


async def test_mit_filter_kommt_eine_vierte_hinzu():
    """Das Auflösen des Vokabulars. So steht es auch in der Kostentabelle --
    3 bis 4, nicht pauschal 3."""
    instanz = Instanz()
    async with instanz.repo() as repo:
        await repo.flows.search_all("Zelle", subject="Biologie")
    assert len(instanz.anfragen) == 4, instanz.anfragen


async def test_das_limit_gilt_je_korb():
    """Zehn Materialien und zehn Sammlungen, nicht zehn zusammen -- sonst
    verdraengte der eine Korb den anderen."""
    instanz = Instanz(material=[_knoten(f"m-{i}", f"M {i}") for i in range(5)],
                      sammlungen=[_knoten(f"s-{i}", f"S {i}") for i in range(5)])
    async with instanz.repo() as repo:
        ergebnis = await repo.flows.search_all("Zelle", limit=5)
    assert ergebnis["materials"]["returned"] == 5
    assert ergebnis["collections"]["returned"] == 5


# --- Wenn ein Korb ganz ausfaellt (Audit A9) ------------------------------

async def test_ein_ausgefallener_sammlungskorb_kostet_nicht_das_material():
    """``collections.find`` sagt eine Ebene tiefer: "half a result is usable, a
    faked empty one is not" -- und wendet das zwischen seinen zwei Wegen an.
    Zwischen den zwei Koerben galt es nicht: fielen beide Sammlungswege aus,
    verlor der Aufrufer die Materialtreffer gleich mit, obwohl sie da waren.
    """
    instanz = Instanz()
    urspruenglich = instanz.handler

    def handler(request: httpx.Request) -> httpx.Response:
        if "collection" in str(request.url).lower():
            instanz.anfragen.append(str(request.url.path))
            return httpx.Response(503, json={"error": "x", "message": "Dienst weg"})
        return urspruenglich(request)

    instanz.handler = handler
    async with instanz.repo() as repo:
        ergebnis = await repo.flows.search_all("Zelle", limit=3)
    assert [h["id"] for h in ergebnis["materials"]["hits"]] == ["m-1"]
    assert ergebnis["collections"]["hits"] == []
    assert "503" in ergebnis["collections"]["error"]
    json.dumps(ergebnis)


async def test_faellt_das_material_aus_wird_geworfen():
    """Der Materialkorb ist die Hauptfrage. Ihn stillschweigend leer zu
    liefern hiesse zu behaupten, es gebe nichts."""
    instanz = Instanz()
    urspruenglich = instanz.handler

    def handler(request: httpx.Request) -> httpx.Response:
        if "/ngsearch" in str(request.url):
            instanz.anfragen.append(str(request.url.path))
            return httpx.Response(503, json={"error": "x", "message": "weg"})
        return urspruenglich(request)

    instanz.handler = handler
    async with instanz.repo() as repo:
        with pytest.raises(EduSharingError):
            await repo.flows.search_all("Zelle")


async def test_ohne_ausfall_ist_error_leer():
    instanz = Instanz()
    async with instanz.repo() as repo:
        ergebnis = await repo.flows.search_all("Zelle")
    assert ergebnis["collections"]["error"] == ""


# --- Paket 4: der dritte Topf ----------------------------------------------

class MitSeiten(Instanz):
    """Eine der Sammlungen traegt eine Seite (ccm:page_config_ref)."""

    def __init__(self) -> None:
        super().__init__(sammlungen=[
            _knoten("s-1", "Sammlung ohne Seite"),
            {**_knoten("s-2", "Themenseite Biologie"),
             "properties": {"cclom:title": ["Themenseite Biologie"],
                            "ccm:page_config_ref": ["workspace://SpacesStore/ordner-2"]}},
        ])


async def test_seiten_kommen_nur_auf_wunsch():
    instanz = MitSeiten()
    async with instanz.repo() as repo:
        ohne = await repo.flows.search_all("Zelle")
        mit = await repo.flows.search_all("Zelle", include_pages=True)
    assert "pages" not in ohne
    assert [h["id"] for h in mit["pages"]["hits"]] == ["s-2"]
    assert mit["pages"]["hits"][0]["folder_id"] == "ordner-2"


async def test_seiten_kosten_keine_weitere_anfrage():
    """Review C11: find_pages suchte die Sammlungen ein zweites Mal. Die Seiten
    werden jetzt aus den schon geholten Sammlungstreffern gelesen."""
    instanz = MitSeiten()
    async with instanz.repo() as repo:
        mit = await repo.flows.search_all("Zelle", include_pages=True)
    assert [h["id"] for h in mit["pages"]["hits"]] == ["s-2"]
    assert len(instanz.anfragen) == 3, instanz.anfragen


async def test_ein_kurzname_behaelt_die_passende_sammlung():
    """Die Gegenprobe zum leeren Korb: eine Sammlung mit dem Fach bleibt."""
    instanz = Instanz(sammlungen=[
        {**_knoten("s-bio", "Bio"), "properties": {"cclom:title": ["Bio"],
                                                    "ccm:taxonid": ["http://vocab.test/080"]}},
        _knoten("s-1", "Ohne Fach"),
    ])
    async with instanz.repo() as repo:
        ergebnis = await repo.flows.search_all("Zelle", subject="Biologie")
    assert [h["id"] for h in ergebnis["collections"]["hits"]] == ["s-bio"]
    assert ergebnis["collections"]["unjudged"] == 0
