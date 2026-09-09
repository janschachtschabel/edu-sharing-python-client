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
    """Der Aufrufer bekommt hoechstens ``limit`` Materialien.

    Gefragt wird seit dem 09.09.2026 nach **einem mehr** -- daran haengt die
    Auskunft ueber eine Kappung --, ausgeliefert wird das Limit. Vorher pinnte
    dieser Test nur den Parameter; er pinnt jetzt auch, was ankommt.
    """
    instanz = Instanz()
    async with _repo(instanz) as repo:
        antwort = await repo.flows.collection_contents("c1", limit=1)
    kinder = next(r for r in instanz.anfragen if r.url.path.endswith("/children"))
    assert kinder.url.params.get("maxItems") == "2", str(kinder.url)
    assert len(antwort["materials"]) == 1, "die Attrappe liefert zwei"


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
            fach = {"u-physik": {"ccm:taxonid": ["http://x/460"]}}
            return httpx.Response(200, json={"collections": [
                {"ref": {"id": i}, "title": t, "collection": {"scope": "MY"},
                 "properties": {"cclom:title": [t], **fach.get(i, {})}} for i, t in kinder],
                "pagination": {"total": len(kinder), "from": 0, "count": len(kinder)}})
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
    assert got["query"]["filters"] == {"subject": "Physik"}


async def test_ein_fachfilter_wirkt_auf_die_sammlungen_lokal():
    instanz = Gefiltert()
    async with _repo(instanz) as repo:
        got = await repo.flows.find_collections("Physik", subject="Biologie")
    assert [h["id"] for h in got["hits"]] == ["c-bio"]
    assert got["unjudged"] == 1, "der Treffer ohne Eigenschaften kann nicht beurteilt werden"
    assert got["unresolved"] == []
    assert got["query"]["filters"] == {"subject": "Biologie"}, "die Worte des Aufrufers"


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


async def test_ein_filter_beurteilt_mehr_kandidaten_als_das_limit():
    """Die Sammlungsrouten nehmen den Filter nicht; wird er lokal angewandt,
    muss die Seite Kandidaten halten, nicht Antworten -- sonst ist limit=1
    mit Fachfilter meist leer. total zaehlt danach die Treffer, nicht die
    Kandidaten."""
    instanz = Gefiltert()
    async with _repo(instanz) as repo:
        got = await repo.flows.find_collections("Physik", subject="Biologie", limit=1)
    suche = [r for r in instanz.anfragen if "queries" in r.url.path]
    assert suche and suche[0].url.params.get("maxItems") == "5", "fuenfmal das Limit"
    assert [h["id"] for h in got["hits"]] == ["c-bio"]
    assert got["total"] == 1 and got["returned"] == 1


class VieleKandidaten(Gefiltert):
    """Die Suche kennt 48 Sammlungen, liefert aber drei -- der Rest bleibt unbeurteilt."""

    def __call__(self, request: httpx.Request) -> httpx.Response:
        antwort = super().__call__(request)
        if "queries" in request.url.path:
            data = antwort.json()
            data["pagination"]["total"] = 48
            return httpx.Response(200, json=data)
        return antwort


async def test_unbeurteilte_kandidaten_werden_gesagt():
    instanz = VieleKandidaten()
    async with _repo(instanz) as repo:
        got = await repo.flows.find_collections("Physik", subject="Biologie")
    assert got["total"] == 1 and got["total_is_lower_bound"] is True
    assert any("48" in w for w in got["warnings"]), got["warnings"]


async def test_unter_einem_elternbereich_traegt_ein_treffer_seine_eigenschaften():
    """Bisher baute der Gang Treffer ohne Rohdaten: mit parent_id UND Kurzname
    war jeder Treffer unjudged, die Antwort immer leer."""
    instanz = Gefiltert()
    async with _repo(instanz) as repo:
        got = await repo.flows.find_collections("", parent_id="wurzel", subject="Physik")
    assert [h["id"] for h in got["hits"]] == ["u-physik"]
    assert got["unjudged"] == 0


class MehrAlsEineSeite(Gefiltert):
    def __call__(self, request: httpx.Request) -> httpx.Response:
        antwort = super().__call__(request)
        if request.url.path.endswith("/children/collections"):
            data = antwort.json()
            data["pagination"] = {"total": 120, "from": 0, "count": len(data["collections"])}
            return httpx.Response(200, json=data)
        return antwort


async def test_mehr_untersammlungen_als_eine_seite_sind_eine_untergrenze():
    instanz = MehrAlsEineSeite()
    async with _repo(instanz) as repo:
        got = await repo.flows.find_collections("", parent_id="wurzel")
    assert got["total_is_lower_bound"] is True and got["warnings"]


async def test_ein_text_aus_stoppwoertern_filtert_trotzdem():
    """query_terms streicht Stoppwoerter; ein Text nur aus solchen ergab leere
    Begriffe, und leer passte auf alles."""
    instanz = Gefiltert()
    async with _repo(instanz) as repo:
        nichts = await repo.flows.find_collections("die", parent_id="wurzel")
        teil = await repo.flows.find_collections("in der", parent_id="wurzel")
    assert nichts["hits"] == []
    assert [h["id"] for h in teil["hits"]] == ["u-physik"]


async def test_ohne_text_liefert_der_elternbereich_alles():
    instanz = Gefiltert()
    async with _repo(instanz) as repo:
        got = await repo.flows.find_collections("", parent_id="wurzel")
    assert [h["id"] for h in got["hits"]] == ["u-physik", "u-bio", "uu-1"]


class VieleUnter(Gefiltert):
    """Sieben Untersammlungen, nur die letzte traegt das Fach."""

    def __call__(self, request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/wurzel/children/collections"):
            kinder = [{"ref": {"id": f"u{i}"}, "title": f"Unter {i}", "collection": {"scope": "MY"},
                       "properties": {"cclom:title": [f"Unter {i}"],
                                      **({"ccm:taxonid": ["http://x/460"]} if i == 7 else {})}}
                      for i in range(1, 8)]
            return httpx.Response(200, json={"collections": kinder,
                                             "pagination": {"total": 7, "from": 0, "count": 7}})
        return super().__call__(request)


async def test_unter_einem_elternbereich_wird_erst_beurteilt_und_dann_geschnitten():
    """Der Gang haelt alle Datensaetze -- die Kappung auf 5xlimit bindet dort
    keine Anfrage und verwarf einen Treffer, der schon im Speicher lag."""
    instanz = VieleUnter()
    async with _repo(instanz) as repo:
        got = await repo.flows.find_collections("", parent_id="wurzel", subject="Physik", limit=1)
    assert [h["id"] for h in got["hits"]] == ["u7"]
    assert got["total"] == 1 and got["total_is_lower_bound"] is False
    assert got["warnings"] == []


# --- API-3: die Untersammlungen werden gedeckelt --------------------------

class MitVielenUntersammlungen(Instanz):
    """Meldet mehr Untersammlungen, als sie ausliefert."""

    def __init__(self, geliefert: int, gesamt: int | None) -> None:
        super().__init__()
        self.geliefert, self.gesamt = geliefert, gesamt

    def __call__(self, request):
        if request.url.path.endswith("/children/collections"):
            self.anfragen.append(request)
            koerper = {"collections": [
                {"ref": {"id": f"unter-{i}"}, "title": f"Unter {i}",
                 "collection": {"scope": "MY"}} for i in range(self.geliefert)]}
            if self.gesamt is not None:
                koerper["pagination"] = {
                    "total": self.gesamt, "from": 0, "count": self.geliefert}
            return httpx.Response(200, json=koerper)
        return super().__call__(request)


async def test_untersammlungen_nennen_ihre_gesamtzahl():
    """Die Materialien tragen ``total_materials`` und ``returned_materials``,
    die Untersammlungen trugen nichts (Audit API-3) -- gedeckelt bei ``limit``,
    ohne dass der Aufrufer erfaehrt, ob es mehr gibt. Dieselbe Bauform, die
    MNT-4 an ``node.children.list()`` behoben hat: eine gekuerzte Liste sieht
    aus wie eine Sammlung mit weniger Kindern, als sie hat.

    Der Endpunkt liefert eine echte Gesamtzahl -- gemessen am 08.09.2026 gegen
    Staging: bei ``maxItems=1`` an einer Sammlung mit zwei Untersammlungen
    kommt **ein** Eintrag und ``total: 2``. (Der Zusatz, das sei nicht
    selbstverstaendlich, weil ``ngsearch`` mit ``pagination: null``
    antworte, stand hier bis zum 09.09.2026 und ist gemessen falsch.)
    """
    async with _repo(MitVielenUntersammlungen(geliefert=5, gesamt=12)) as repo:
        antwort = await repo.flows.collection_contents("c1", limit=5)
    assert antwort["total_collections"] == 12
    assert antwort["returned_collections"] == 5
    assert antwort["collections_truncated"] is True


async def test_untersammlungen_ohne_kappung_sind_nicht_gekuerzt():
    """Gegenprobe -- ein Kennzeichen, das immer wahr ist, sagt nichts."""
    async with _repo(MitVielenUntersammlungen(geliefert=2, gesamt=2)) as repo:
        antwort = await repo.flows.collection_contents("c1", limit=5)
    assert antwort["total_collections"] == 2
    assert antwort["collections_truncated"] is False


async def test_ohne_gesamtzahl_zaehlt_das_gelieferte():
    """Nennt der Endpunkt keine Zahl, ist die Zahl der Datensaetze die beste
    Auskunft -- und dann darf nichts als gekuerzt gelten, was niemand weiss."""
    async with _repo(MitVielenUntersammlungen(geliefert=2, gesamt=None)) as repo:
        antwort = await repo.flows.collection_contents("c1", limit=5)
    assert antwort["total_collections"] == 2
    assert antwort["collections_truncated"] is False


async def test_die_untersammlungen_werden_wirklich_gedeckelt():
    """Ohne diesen Test ist ``collections_truncated`` eine leere Zusage.

    Die drei Tests darueber pinnen die **Meldung** einer Kappung; die Kappung
    selbst hing an nichts. ``maxItems`` aus der Anfrage zu entfernen liess die
    ganze Suite gruen -- danach waere das Kennzeichen fuer immer ``False`` und
    der Satz in FLOWS und REFERENCE falsch (Pruefung 09.09.2026).
    """
    instanz = MitVielenUntersammlungen(geliefert=2, gesamt=9)
    async with _repo(instanz) as repo:
        await repo.flows.collection_contents("c1", limit=7)
    gefragt = next(r for r in instanz.anfragen
                   if r.url.path.endswith("/children/collections"))
    # ``limit + 1``: der eine zusaetzliche Datensatz beantwortet die
    # Kappungsfrage, ohne dass der Endpunkt eine Gesamtzahl nennen muss
    # (Pruefung 09.09.2026). Ausgeliefert werden weiterhin nur ``limit``.
    assert gefragt.url.params.get("maxItems") == "8", str(gefragt.url)


class MitBestand(Instanz):
    """Beachtet ``maxItems`` -- liefert also genau so viele wie ein Server.

    ``nennt_gesamtzahl=False`` ist die Antwortform ohne ``pagination``, fuer
    die ``page_total`` eine Vorgabe hat. Gemessen ist sie nicht -- alle drei
    Endpunkte, die diese Bibliothek auflistet, nennen eine Zahl (09.09.2026).
    Geprueft wird sie trotzdem: die Antwort darf nicht daran haengen.
    """

    def __init__(self, bestand: int, nennt_gesamtzahl: bool = False) -> None:
        super().__init__()
        self.bestand, self.nennt_gesamtzahl = bestand, nennt_gesamtzahl

    def __call__(self, request):
        if request.url.path.endswith("/children/collections"):
            self.anfragen.append(request)
            grenze = int(request.url.params.get("maxItems") or self.bestand)
            seite = [{"ref": {"id": f"unter-{i}"}, "title": f"Unter {i}",
                      "collection": {"scope": "MY"}}
                     for i in range(min(self.bestand, grenze))]
            koerper = {"collections": seite}
            if self.nennt_gesamtzahl:
                koerper["pagination"] = {"total": self.bestand, "from": 0,
                                         "count": len(seite)}
            return httpx.Response(200, json=koerper)
        return super().__call__(request)


async def test_ohne_gesamtzahl_wird_die_kappung_trotzdem_erkannt():
    """Der blinde Fleck des Kennzeichens (Pruefung 09.09.2026).

    ``collections_truncated`` las sich aus der genannten Gesamtzahl, und ohne
    eine galt die Zahl der Datensaetze als Gesamtzahl -- also war das
    Kennzeichen genau dann ``False``, wenn niemand etwas sagte. Bei neun
    Untersammlungen und ``limit=5`` kamen fuenf zurueck, ``total_collections:
    5`` und ``collections_truncated: False``: eine gekuerzte Liste, die aussieht
    wie eine vollstaendige -- genau das, wogegen API-3 das Kennzeichen
    eingefuehrt hat.

    Gefragt wird jetzt nach einem Datensatz mehr als ``limit``; kommt er an,
    ist gekuerzt worden. Dieselbe Bauform wie ``childobjects._ist_gekuerzt``.
    """
    async with _repo(MitBestand(bestand=9)) as repo:
        antwort = await repo.flows.collection_contents("c1", limit=5)
    assert antwort["returned_collections"] == 5
    assert antwort["collections_truncated"] is True
    assert len(antwort["collections"]) == 5, "der eine Datensatz mehr geht nicht raus"


async def test_genau_am_limit_ohne_gesamtzahl_ist_nicht_gekuerzt():
    """Gegenprobe: ein Kennzeichen, das immer wahr ist, sagt so wenig wie
    eines, das immer falsch ist. Genau ``limit`` Untersammlungen und keine
    genannte Zahl -- der zusaetzliche Datensatz kommt nicht, also ist es
    alles."""
    async with _repo(MitBestand(bestand=5)) as repo:
        antwort = await repo.flows.collection_contents("c1", limit=5)
    assert antwort["returned_collections"] == 5
    assert antwort["collections_truncated"] is False
    assert antwort["total_collections"] == 5


class MitMaterialbestand(Instanz):
    """Beachtet ``maxItems`` am Knoten-Endpunkt und nennt keine ``pagination``.

    Die Antwortform, die ``page_total`` fuer ``ngsearch`` ausdruecklich
    vorsieht -- hier fuer die Materialien einer Sammlung.
    """

    def __init__(self, bestand: int) -> None:
        super().__init__()
        self.bestand = bestand

    def __call__(self, request):
        pfad = request.url.path
        if pfad.endswith("/children") and not pfad.endswith("/children/collections"):
            self.anfragen.append(request)
            grenze = int(request.url.params.get("maxItems") or self.bestand)
            return httpx.Response(200, json={"nodes": [
                _knoten(f"m{i}", f"Material {i}")
                for i in range(min(self.bestand, grenze))]})
        return super().__call__(request)


async def test_ohne_gesamtzahl_ist_die_materialzahl_nicht_null():
    """``page_total`` gibt ohne ``pagination`` die Vorgabe zurueck, und die war
    hier **0** -- neben drei ausgelieferten Materialien (Pruefung 09.09.2026).

    Null Gesamtzahl bei drei Datensaetzen ist keine vorsichtige Angabe, es ist
    eine falsche: wer die beiden Zahlen vergleicht, liest daraus, dass es
    weniger gibt als er in der Hand haelt.
    """
    async with _repo(MitMaterialbestand(bestand=3)) as repo:
        antwort = await repo.flows.collection_contents("c1", limit=20)
    assert antwort["returned_materials"] == 3
    assert antwort["total_materials"] == 3


async def test_ohne_gesamtzahl_zeigt_die_materialzahl_die_kappung():
    """Und wenn gekuerzt wurde, muss man es an den zwei Zahlen sehen.

    Die Materialien tragen kein eigenes Kennzeichen; die Auskunft ist der
    Vergleich ``total_materials`` gegen ``returned_materials``. Damit der
    stimmt, wird ein Datensatz mehr als ``limit`` geholt: kommt er an, ist die
    Gesamtzahl mindestens einer ueber dem Gelieferten.
    """
    async with _repo(MitMaterialbestand(bestand=40)) as repo:
        antwort = await repo.flows.collection_contents("c1", limit=20)
    assert antwort["returned_materials"] == 20
    assert len(antwort["materials"]) == 20, "der eine mehr geht nicht raus"
    assert antwort["total_materials"] > antwort["returned_materials"]


async def test_die_materialien_werden_um_einen_datensatz_ueberfragt():
    """Woran die beiden Tests darueber haengen -- und ``skipCount`` bleibt der
    Versatz, nicht der Versatz plus eins."""
    instanz = MitMaterialbestand(bestand=40)
    async with _repo(instanz) as repo:
        await repo.flows.collection_contents("c1", limit=20, offset=10)
    gefragt = next(r for r in instanz.anfragen
                   if r.url.path.endswith("/children"))
    assert gefragt.url.params.get("maxItems") == "21", str(gefragt.url)
    assert gefragt.url.params.get("skipCount") == "10", str(gefragt.url)


async def test_der_versatz_zaehlt_zur_unteren_schranke():
    """Ohne genannte Gesamtzahl ist ``total_materials`` der Versatz **plus**
    das Gesehene -- die Seite faengt ja erst dort an.

    Ohne den Versatz waere die Schranke bei jedem ``offset`` zu klein, und wer
    blaettert, laese eine Sammlung, die schrumpft, je weiter er kommt. Die
    Mutationsprobe am 09.09.2026 zeigte, dass genau dieser Summand ungewacht
    war: ihn zu entfernen liess die ganze Datei gruen.
    """
    async with _repo(MitMaterialbestand(bestand=40)) as repo:
        antwort = await repo.flows.collection_contents("c1", limit=20, offset=10)
    assert antwort["returned_materials"] == 20
    assert antwort["total_materials"] == 31, "10 uebersprungen, 21 gesehen"
