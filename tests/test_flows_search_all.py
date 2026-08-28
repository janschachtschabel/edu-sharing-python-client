"""Material und Sammlungen in einem Aufruf.

Der wlo-mcp-sc nennt das sein Standardwerkzeug, und zu Recht: wer nach einem
Thema fragt, will beides -- die einzelnen Materialien und die Sammlungen, in
denen jemand schon zusammengestellt hat, was dazugehoert. Zwei Endpunkte, zwei
Antwortformen, und bisher zwei Aufrufe.

Der Haken, den dieser Ablauf sichtbar machen muss: **die Sammlungssuche nimmt
keine Filter.** Gemessen und in ``collections.py`` festgehalten -- die Abfrage
akzeptiert ``ngsearchword`` und sonst nichts, jedes weitere Kriterium endet in
``400 DAOValidationException``. Wer ``search_all("Zelle", subject="Biologie")``
aufruft, bekommt gefiltertes Material und **ungefilterte** Sammlungen. Das
stillschweigend zu tun hiesse, eine Einschraenkung zu behaupten, die es nicht
gibt.
"""

import json

import httpx

from edusharing import AsyncRepository

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

async def test_filter_gelten_nur_fuer_das_material():
    """Und der Ablauf sagt es. Gemessen: die Sammlungsabfrage nimmt nur
    ngsearchword, jedes weitere Kriterium endet in 400."""
    instanz = Instanz()
    async with instanz.repo() as repo:
        ergebnis = await repo.flows.search_all("Zelle", subject="Biologie")
    assert ergebnis["collections"]["filters_ignored"] == ["subject"]


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
