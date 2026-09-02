"""Sammlungen finden und auslesen, Material aendern.

Die drei Luecken im Kreis, die der Abgleich mit den Werkzeugen des wlo-mcp-sc
gezeigt hat: Sammlungen liessen sich anlegen und fuellen, aber nicht suchen und
nicht auslesen, und Material liess sich anlegen und loeschen, aber nicht aendern.

Endpunkte gemessen gegen Staging am 27.08.2026:

    /node/v1/nodes/-home-/{id}/children                    Materialien (filter=files)
    /collection/v1/collections/-home-/{id}/children/collections   Untersammlungen

Gemessen an einer Sammlung mit zwei Untersammlungen: filter=files liefert null
Knoten. Wer nur das Material abfragt, haelt sie fuer leer. (Unter filter=folders
tauchen sie auf -- genommen wird trotzdem der Sammlungs-Endpunkt, weil er der
dafuer vorgesehene ist und Sammlungs-Metadaten liefert.)
"""

import json

import httpx
import pytest

from edusharing import AsyncRepository
from edusharing.errors import EduSharingError

REPO = "https://repo.test/edu-sharing"

FAECHER = {"values": [
    {"key": "http://x/080", "displayString": "Biologie"},
    {"key": "http://x/460", "displayString": "Physik"},
]}


def _knoten(node_id: str, titel: str, **props) -> dict:
    return {"ref": {"id": node_id}, "title": titel, "type": "ccm:io",
            "access": ["Read", "Write"], "content": {"hash": "-1"},
            "properties": {"cclom:title": [titel], **props}}


class Instanz:
    def __init__(self) -> None:
        self.anfragen: list[httpx.Request] = []
        self.geschrieben: dict[str, dict] = {}

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.anfragen.append(request)
        pfad, methode = request.url.path, request.method

        if "/values" in pfad:
            return httpx.Response(200, json=FAECHER)
        if pfad.endswith("/children/collections"):
            return httpx.Response(200, json={"collections": [
                {"ref": {"id": "unter-1"}, "title": "Untersammlung",
                 "collection": {"scope": "MY"}}],
                "pagination": {"total": 1, "from": 0, "count": 1}})
        if pfad.endswith("/children"):
            return httpx.Response(200, json={
                "nodes": [_knoten("m1", "Material eins"), _knoten("m2", "Material zwei")],
                "pagination": {"total": 26, "from": 0, "count": 2}})
        if "queries" in pfad or "collections" in pfad:
            return httpx.Response(200, json={
                "nodes": [_knoten("c1", "Physik-Sammlung")],
                "pagination": {"total": 48, "from": 0, "count": 1}})
        if methode == "PUT" and pfad.endswith("/metadata"):
            knoten_id = pfad.split("/-home-/")[1].split("/")[0]
            self.geschrieben.setdefault(knoten_id, {}).update(json.loads(request.content))
            return httpx.Response(200, json={"node": self._stand(knoten_id)})
        # Auch der Lesezugriff muss den geschriebenen Stand kennen: die
        # Rueckleseprobe liest nach dem Schreiben erneut, und ein Mock mit
        # fester Antwort wuerde sie zu Recht ausloesen.
        knoten_id = pfad.split("/-home-/")[1].split("/")[0] if "/-home-/" in pfad else "m1"
        return httpx.Response(200, json={"node": self._stand(knoten_id)})

    def _stand(self, knoten_id: str) -> dict:
        props = {"cclom:title": ["Material eins"], **self.geschrieben.get(knoten_id, {})}
        return {"ref": {"id": knoten_id}, "type": "ccm:io",
                "access": ["Read", "Write"], "content": {"hash": "-1"},
                "properties": props, "title": (props.get("cclom:title") or [""])[0]}


def _repo(instanz, **kwargs) -> AsyncRepository:
    return AsyncRepository(
        REPO, metadataset="mds_oeh", backoff_base=0.0,
        client=httpx.AsyncClient(transport=httpx.MockTransport(instanz)), **kwargs)


# --- find_collections -----------------------------------------------------

async def test_sammlungen_suchen_liefert_json():
    instanz = Instanz()
    async with _repo(instanz) as repo:
        ergebnis = await repo.flows.find_collections("Physik")
    assert ergebnis["hits"][0]["id"] == "c1"
    assert ergebnis["query"]["text"] == "Physik"
    json.dumps(ergebnis)


async def test_sammlungssuche_meldet_die_untere_schranke():
    """Die Sammlungssuche fragt zwei Wege ab und legt sie zusammen. Die
    Gesamtzahl ist deshalb eine untere Schranke -- wer sie als Tatsache
    weitergibt, behauptet etwas, das keine ist."""
    instanz = Instanz()
    async with _repo(instanz) as repo:
        ergebnis = await repo.flows.find_collections("Physik")
    assert ergebnis["total_is_lower_bound"] is True


# --- collection_contents --------------------------------------------------

async def test_sammlungsinhalt_liefert_material_und_untersammlungen():
    """Beides, weil eine Sammlung beides enthaelt. Gemessen: eine Sammlung mit
    zwei Untersammlungen liefert unter filter=files null Knoten -- wer nur das
    Material abfragt, haelt sie fuer leer."""
    instanz = Instanz()
    async with _repo(instanz) as repo:
        ergebnis = await repo.flows.collection_contents("c1")

    assert [m["id"] for m in ergebnis["materials"]] == ["m1", "m2"]
    assert [c["id"] for c in ergebnis["collections"]] == ["unter-1"]
    assert ergebnis["total_materials"] == 26
    json.dumps(ergebnis)


async def test_sammlungsinhalt_fragt_beide_wege_ab():
    instanz = Instanz()
    async with _repo(instanz) as repo:
        await repo.flows.collection_contents("c1")
    pfade = [r.url.path for r in instanz.anfragen]
    assert any(p.endswith("/children") for p in pfade)
    assert any(p.endswith("/children/collections") for p in pfade)


async def test_sammlungsinhalt_fordert_die_eigenschaften_an():
    """Live aufgefallen am 27.08.2026: ohne propertyFilter liefert /children
    **null** Eigenschaften. Die Materialien kamen dann ohne Metadaten zurueck --
    "fields" war live immer leer, waehrend der Mock brav welche mitlieferte.

    Genau die Sorte Fehler, die ein Mock-Test nicht faengt: er antwortet, was
    man ihm sagt.
    """
    instanz = Instanz()
    async with _repo(instanz) as repo:
        await repo.flows.collection_contents("c1")
    kinder = next(r for r in instanz.anfragen if r.url.path.endswith("/children"))
    assert kinder.url.params.get("propertyFilter") == "-all-", (
        "ohne diesen Parameter kommen die Materialien ohne Metadaten")


async def test_sammlungsinhalt_haelt_das_limit_ein():
    instanz = Instanz()
    async with _repo(instanz) as repo:
        await repo.flows.collection_contents("c1", limit=7)
    kinder = next(r for r in instanz.anfragen if r.url.path.endswith("/children"))
    assert kinder.url.params.get("maxItems") == "7"


async def test_materialien_tragen_lesbare_werte():
    """Dieselbe Form wie ein Suchtreffer -- ein Aufrufer soll nicht zwei
    Trefferformate auseinanderhalten muessen."""
    instanz = Instanz()
    async with _repo(instanz) as repo:
        ergebnis = await repo.flows.collection_contents("c1")
    assert set(ergebnis["materials"][0]) >= {"id", "title", "url", "fields"}


# --- update_material ------------------------------------------------------

async def test_material_aendern_loest_vokabular_auf():
    """Derselbe Gewinn wie beim Anlegen: "Biologie" statt des URI."""
    instanz = Instanz()
    async with _repo(instanz) as repo:
        ergebnis = await repo.flows.update_material("m1", subject="Biologie")
    assert instanz.geschrieben["m1"]["ccm:taxonid"] == ["http://x/080"]
    assert not ergebnis["unresolved"]


async def test_teilweise_unaufloesbare_aenderung_geht_durch_und_wird_gemeldet():
    """Der Rest der Aenderung soll ankommen -- gemeldet wird, was fehlt."""
    instanz = Instanz()
    async with _repo(instanz) as repo:
        ergebnis = await repo.flows.update_material(
            "m1", title="Neuer Titel", subject="Gibtsnicht")
    assert ergebnis["unresolved"][0]["field"] == "subject"
    assert "ccm:taxonid" not in instanz.geschrieben.get("m1", {})
    assert instanz.geschrieben["m1"]["cclom:title"] == ["Neuer Titel"]


async def test_vollstaendig_unaufloesbare_aenderung_wirft():
    """Hier ist gar nichts passiert. Ein Rueckgabewert mit "unresolved" saehe
    aus wie ein Teilerfolg -- und der Aufrufer glaubte, der Rest sei
    angekommen. Es gibt keinen Rest."""
    instanz = Instanz()
    async with _repo(instanz) as repo:
        with pytest.raises(EduSharingError) as fehler:
            await repo.flows.update_material("m1", subject="Gibtsnicht")
    assert "Gibtsnicht" in str(fehler.value), "die Meldung muss den Grund nennen"
    assert not instanz.geschrieben, "es darf nichts geschrieben worden sein"


async def test_aenderung_ohne_felder_wird_abgelehnt():
    """Ein leeres PUT ueberschriebe nichts und meldete trotzdem Erfolg."""
    instanz = Instanz()
    async with _repo(instanz) as repo:
        with pytest.raises(EduSharingError):
            await repo.flows.update_material("m1")


async def test_aenderung_gibt_den_neuen_stand_zurueck():
    instanz = Instanz()
    async with _repo(instanz) as repo:
        ergebnis = await repo.flows.update_material("m1", title="Neuer Titel")
    assert ergebnis["id"] == "m1"
    assert ergebnis["title"] == "Neuer Titel"
    json.dumps(ergebnis)


class MitReferenz(Instanz):
    """ref-1 ist eine Referenz auf m1 -- ein Sammlungs-Listing gibt solche IDs aus."""

    def _stand(self, knoten_id: str) -> dict:
        data = super()._stand("m1" if knoten_id == "ref-1" else knoten_id)
        if knoten_id == "ref-1":
            data = {**data, "ref": {"id": "ref-1"}, "originalId": "m1",
                    "aspects": ["ccm:collection_io_reference"]}
        return data


async def test_aenderung_an_einer_referenz_weist_die_umleitung_aus():
    """Die Antwort traegt die ID des Originals -- und muss sagen, dass der
    Aufrufer eine andere uebergeben hat. describe, placement und delete tun
    das; update_material verschwieg es bis heute."""
    instanz = MitReferenz()
    async with _repo(instanz) as repo:
        ergebnis = await repo.flows.update_material("ref-1", title="Neuer Titel")
    assert ergebnis["id"] == "m1"
    assert ergebnis["redirected_from"] == "ref-1"
    assert "ref-1" not in instanz.geschrieben
    assert instanz.geschrieben["m1"]["cclom:title"] == ["Neuer Titel"]


async def test_aenderung_an_einem_original_ist_nicht_umgeleitet():
    instanz = Instanz()
    async with _repo(instanz) as repo:
        ergebnis = await repo.flows.update_material("m1", title="Neuer Titel")
    assert ergebnis["redirected_from"] is None


# --- Paket 4: find_collections mit Filtern und Elternbereich ---------------
#
# Die Sammlungssuche nimmt ngsearchword und sonst nichts (gemessen). Fach und
# Stufe koennen also nicht gesendet werden -- sie werden hier auf die
# Eigenschaften der Treffer angewandt, nachdem die Labels aufgeloest sind. Wer
# einen Elternbereich nennt, sucht nicht: der Teilbaum wird gegangen und der
# Text lokal verglichen -- so macht es der MCP mit parentNodeId.

class Gefiltert(Instanz):
    """Zwei Sammlungstreffer mit Fach, einer ohne Eigenschaften (Leg B)."""

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.anfragen.append(request)
        pfad = request.url.path
        if "/values" in pfad:
            return httpx.Response(200, json=FAECHER)
        if pfad.endswith("/children/collections"):
            eltern = pfad.split("/-home-/")[1].split("/")[0]
            kinder = {"wurzel": [("u-physik", "Optik in der Physik"), ("u-bio", "Zellen")],
                      "u-physik": [("uu-1", "Linsen und Optik")]}.get(eltern, [])
            return httpx.Response(200, json={"collections": [
                {"ref": {"id": i}, "title": t, "collection": {"scope": "MY"},
                 "properties": {"cclom:title": [t]}} for i, t in kinder]})
        if "queries" in pfad:
            return httpx.Response(200, json={"nodes": [
                _knoten("c-physik", "Physik-Sammlung", **{"ccm:taxonid": ["http://x/460"]}),
                _knoten("c-bio", "Bio-Sammlung", **{"ccm:taxonid": ["http://x/080"]}),
                {"ref": {"id": "c-blind"}, "title": "Ohne Eigenschaften", "type": "ccm:map"},
            ], "pagination": {"total": 3, "from": 0, "count": 3}})
        if "collections" in pfad:
            return httpx.Response(200, json={"nodes": [], "pagination": None})
        return httpx.Response(200, json={"node": self._stand("m1")})


class ZweiVokabulare(Gefiltert):
    """Physik steht in zwei Vokabularen (gemessen: 25 Faecher tun das); eine
    Sammlung traegt nur die zweite URI."""

    def __call__(self, request: httpx.Request) -> httpx.Response:
        if "/values" in request.url.path:
            return httpx.Response(200, json={"values": [
                *FAECHER["values"],
                {"key": "http://x/hochschule/460", "displayString": "Physik"},
            ]})
        if "queries" in request.url.path:
            return httpx.Response(200, json={"nodes": [
                _knoten("c-schule", "Physik AG", **{"ccm:taxonid": ["http://x/460"]}),
                _knoten("c-uni", "Physik Uni",
                        **{"ccm:taxonid": ["http://x/hochschule/460"]}),
            ], "pagination": {"total": 2, "from": 0, "count": 2}})
        return super().__call__(request)


async def test_ein_lesefilter_nimmt_jede_uri_eines_labels():
    """Schreiben nimmt EINE URI (eine Behauptung); Lesen muss beide nehmen,
    sonst findet der Filter die Haelfte und sieht vollstaendig aus."""
    instanz = ZweiVokabulare()
    async with _repo(instanz) as repo:
        got = await repo.flows.find_collections("Physik", subject="Physik")
    assert [h["id"] for h in got["hits"]] == ["c-schule", "c-uni"]
    assert sorted(got["query"]["filters"]["ccm:taxonid"]) == [
        "http://x/460", "http://x/hochschule/460"]


async def test_ein_fachfilter_wirkt_auf_die_sammlungen_lokal():
    instanz = Gefiltert()
    async with _repo(instanz) as repo:
        got = await repo.flows.find_collections("Physik", subject="Biologie")
    assert [h["id"] for h in got["hits"]] == ["c-bio"]
    assert got["unjudged"] == 1, "der Treffer ohne Eigenschaften kann nicht beurteilt werden"
    assert got["unresolved"] == []
    assert got["query"]["filters"] == {"ccm:taxonid": ["http://x/080"]}


async def test_ein_unaufloesbarer_filter_wird_gemeldet_und_verengt_nicht():
    instanz = Gefiltert()
    async with _repo(instanz) as repo:
        got = await repo.flows.find_collections("Physik", subject="Phsyik")
    assert [h["id"] for h in got["hits"]] == ["c-physik", "c-bio", "c-blind"]
    assert got["unresolved"] and got["unresolved"][0]["value"] == "Phsyik"


async def test_ein_elternbereich_wird_gegangen_statt_gesucht():
    instanz = Gefiltert()
    async with _repo(instanz) as repo:
        got = await repo.flows.find_collections("Optik", parent_id="wurzel")
    assert [h["id"] for h in got["hits"]] == ["u-physik", "uu-1"]
    assert not any("queries" in r.url.path for r in instanz.anfragen), "keine Suche"
    assert got["query"]["parent_id"] == "wurzel"


async def test_ohne_text_liefert_der_elternbereich_alles():
    instanz = Gefiltert()
    async with _repo(instanz) as repo:
        got = await repo.flows.find_collections("", parent_id="wurzel")
    assert [h["id"] for h in got["hits"]] == ["u-physik", "u-bio", "uu-1"]
