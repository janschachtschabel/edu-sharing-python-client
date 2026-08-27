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
