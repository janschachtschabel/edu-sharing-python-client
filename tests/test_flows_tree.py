"""Der Sammlungsbaum: durchgehen, darin suchen, auszaehlen.

Drei Abläufe, die der MCP als ``browse_collection_tree``,
``search_wlo_within_collection`` und ``get_collection_stats`` anbietet. Alle
drei haben dasselbe Problem, und es ist kein technisches:

**Sammlungen bilden einen gerichteten Graphen, keinen Baum.** Eine
Untersammlung kann unter mehreren Elternteilen hängen. Wer nicht nach ID
entdoppelt, läuft im Kreis; wer die Verzweigung nicht deckelt, macht aus einem
Aufruf hundert.

Und: **eine Suche lässt sich nicht auf eine Sammlung eingrenzen.** Drei Mal
gemessen -- vom wlo-mcp-sc am 17.07.2026, hier am 27. und 28.08.2026 --
antwortet ``ngsearch`` mit ``virtual:primaryparent_nodeid`` als Kriterium mit
HTTP 400. Es wäre auch die falsche Antwort: eine Sammlung hält *Referenzen* auf
Knoten, deren eigenes Elternteil woanders liegt. Also wird gelaufen und lokal
verglichen -- und der Ablauf sagt, wenn er dabei abgeschnitten hat.
"""

import json

import httpx
import pytest

from edusharing import AsyncRepository
from edusharing.errors import AuthenticationError

REPO = "https://repo.test/edu-sharing"


def _sammlung(nid: str, titel: str) -> dict:
    return {"ref": {"id": nid}, "title": titel, "type": "ccm:map",
            "properties": {"cclom:title": [titel]}}


def _material(nid: str, titel: str, *, beschreibung: str = "",
              schlagworte: list[str] | None = None) -> dict:
    return {"ref": {"id": nid}, "title": titel, "type": "ccm:io",
            "properties": {"cclom:title": [titel],
                           "cclom:general_description": [beschreibung],
                           "cclom:general_keyword": schlagworte or []}}


class Instanz:
    """Ein Repositorium mit einem gerichteten Sammlungsgraphen.

    ``baum`` bildet Sammlung -> Untersammlungen ab, ``inhalt`` Sammlung ->
    Materialien.
    """

    def __init__(self, baum: dict[str, list[str]] | None = None,
                 inhalt: dict[str, list[dict]] | None = None,
                 titel: dict[str, str] | None = None) -> None:
        self.baum = baum if baum is not None else {
            "wurzel": ["a", "b"], "a": ["a1"], "b": [], "a1": []}
        self.inhalt = inhalt if inhalt is not None else {
            "wurzel": [_material("m0", "Ganz oben")],
            "a": [_material("m1", "Zellteilung")],
            "b": [_material("m2", "Photosynthese")],
            "a1": [_material("m3", "Mitose")],
        }
        self.titel = titel or {}
        self.anfragen: list[str] = []

    def handler(self, request: httpx.Request) -> httpx.Response:
        pfad = request.url.path
        self.anfragen.append(pfad)

        if pfad.endswith("/children/collections"):
            nid = pfad.split("/collections/-home-/")[1].split("/")[0]
            kinder = [_sammlung(k, self.titel.get(k, k.upper()))
                      for k in self.baum.get(nid, [])]
            return httpx.Response(200, json={"collections": kinder})

        if pfad.endswith("/children"):
            nid = pfad.split("/nodes/-home-/")[1].split("/")[0]
            material = self.inhalt.get(nid, [])
            ab = int(request.url.params.get("skipCount") or 0)
            wieviel = int(request.url.params.get("maxItems") or 20)
            return httpx.Response(200, json={
                "nodes": material[ab:ab + wieviel],
                "pagination": {"total": len(material), "from": ab,
                               "count": len(material[ab:ab + wieviel])}})

        return httpx.Response(200, json={"node": _sammlung("wurzel", "Wurzel")})

    def repo(self) -> AsyncRepository:
        return AsyncRepository(
            REPO, metadataset="mds_oeh", backoff_base=0.0,
            client=httpx.AsyncClient(transport=httpx.MockTransport(self.handler)))


# --- browse_tree ----------------------------------------------------------

async def test_der_baum_kommt_verschachtelt():
    instanz = Instanz()
    async with instanz.repo() as repo:
        baum = await repo.flows.browse_tree("wurzel", depth=2)
    assert baum["id"] == "wurzel"
    assert [k["id"] for k in baum["collections"]] == ["a", "b"]
    assert [k["id"] for k in baum["collections"][0]["collections"]] == ["a1"]


async def test_die_tiefe_wird_eingehalten():
    """Sonst laeuft ein Aufruf durch den ganzen Bestand."""
    instanz = Instanz()
    async with instanz.repo() as repo:
        baum = await repo.flows.browse_tree("wurzel", depth=1)
    assert [k["id"] for k in baum["collections"]] == ["a", "b"]
    assert baum["collections"][0]["collections"] == []


async def test_ein_kreis_laeuft_nicht_endlos():
    """Sammlungen bilden einen Graphen: a haengt unter b und b unter a ist
    erlaubt. Ohne Entdopplung nach ID laeuft der Ablauf bis zum Abbruch."""
    instanz = Instanz(baum={"wurzel": ["a"], "a": ["b"], "b": ["a"]},
                      inhalt={})
    async with instanz.repo() as repo:
        baum = await repo.flows.browse_tree("wurzel", depth=5)
    assert baum["collections"][0]["id"] == "a"
    assert baum["collections"][0]["collections"][0]["id"] == "b"
    # a taucht nicht ein zweites Mal auf.
    assert baum["collections"][0]["collections"][0]["collections"] == []


async def test_dieselbe_untersammlung_unter_zwei_eltern():
    """Ein DAG, kein Kreis. Beim zweiten Mal wird nicht noch einmal geoeffnet."""
    instanz = Instanz(baum={"wurzel": ["a", "b"], "a": ["geteilt"],
                            "b": ["geteilt"], "geteilt": []},
                      inhalt={})
    async with instanz.repo() as repo:
        await repo.flows.browse_tree("wurzel", depth=3)
    geoeffnet = [p for p in instanz.anfragen
                 if p.endswith("/children/collections") and "geteilt" in p]
    assert len(geoeffnet) == 1, "eine Sammlung wird einmal geoeffnet"


async def test_der_deckel_wird_gemeldet():
    """Still abzuschneiden liest sich wie Vollstaendigkeit."""
    instanz = Instanz(baum={"wurzel": [f"k{i}" for i in range(10)],
                            **{f"k{i}": [] for i in range(10)}},
                      inhalt={})
    async with instanz.repo() as repo:
        baum = await repo.flows.browse_tree("wurzel", depth=2, max_collections=4)
    assert baum["truncated"] is True
    assert baum["opened"] <= 4


async def test_ohne_deckel_kein_hinweis():
    instanz = Instanz()
    async with instanz.repo() as repo:
        baum = await repo.flows.browse_tree("wurzel", depth=3)
    assert baum["truncated"] is False


async def test_der_baum_kostet_eine_anfrage_je_sammlung():
    """Nur die Untersammlungen, nicht die Materialien -- das ist die Frage,
    die dieser Ablauf beantwortet, und es halbiert die Kosten."""
    instanz = Instanz()
    async with instanz.repo() as repo:
        await repo.flows.browse_tree("wurzel", depth=3)
    assert all(p.endswith("/children/collections") for p in instanz.anfragen)
    assert len(instanz.anfragen) == 4, instanz.anfragen


async def test_der_baum_ist_json():
    instanz = Instanz()
    async with instanz.repo() as repo:
        json.dumps(await repo.flows.browse_tree("wurzel"))


# --- search_in_collection -------------------------------------------------

async def test_suche_in_der_sammlung_findet_im_titel():
    instanz = Instanz()
    async with instanz.repo() as repo:
        ergebnis = await repo.flows.search_in_collection("wurzel", "zellteilung")
    assert [h["id"] for h in ergebnis["hits"]] == ["m1"]


async def test_die_suche_geht_in_die_tiefe():
    instanz = Instanz()
    async with instanz.repo() as repo:
        ergebnis = await repo.flows.search_in_collection("wurzel", "mitose",
                                                         depth=3)
    assert [h["id"] for h in ergebnis["hits"]] == ["m3"]


async def test_gross_und_kleinschreibung_ist_gleich():
    instanz = Instanz()
    async with instanz.repo() as repo:
        ergebnis = await repo.flows.search_in_collection("wurzel", "ZELLTEILUNG")
    assert [h["id"] for h in ergebnis["hits"]] == ["m1"]


async def test_beschreibung_und_fachlabel_zaehlen_mit():
    """Verglichen wird, was der serialisierte Treffer traegt: Titel,
    Beschreibung und die aufgeloesten Feldwerte. Schlagworte stehen nicht
    darin -- fuer Volltext ueber den ganzen Bestand gibt es flows.search."""
    mit_fach = _material("m2", "Auch ohne")
    mit_fach["properties"]["ccm:taxonid_DISPLAYNAME"] = ["Osmose-Kunde"]
    instanz = Instanz(
        baum={"wurzel": []},
        inhalt={"wurzel": [
            _material("m1", "Ohne", beschreibung="handelt von Osmose"),
            mit_fach,
            _material("m3", "Nichts davon")]})
    async with instanz.repo() as repo:
        ergebnis = await repo.flows.search_in_collection("wurzel", "osmose")
    assert {h["id"] for h in ergebnis["hits"]} == {"m1", "m2"}


async def test_die_suche_sagt_wo_sie_gesucht_hat():
    """Ein leeres Ergebnis aus einer abgeschnittenen Suche ist kein 'gibt es
    nicht'."""
    instanz = Instanz()
    async with instanz.repo() as repo:
        ergebnis = await repo.flows.search_in_collection(
            "wurzel", "gibtesnicht", depth=3)
    assert ergebnis["hits"] == []
    assert ergebnis["searched"] == 4
    assert ergebnis["truncated"] is False


async def test_der_deckel_begrenzt_auch_die_suche():
    """Der Baum listet Kinder, die er nicht geoeffnet hat -- sie kommen mit der
    Antwort des Elternteils. Material aus allen zu lesen kostete zwei Anfragen
    je Sammlung und liefe am gesetzten Deckel vorbei."""
    instanz = Instanz(baum={"wurzel": [f"k{i}" for i in range(10)],
                            **{f"k{i}": [] for i in range(10)}},
                      inhalt={f"k{i}": [_material(f"m{i}", "Zelle")]
                              for i in range(10)})
    async with instanz.repo() as repo:
        ergebnis = await repo.flows.search_in_collection(
            "wurzel", "zelle", depth=2, max_collections=3)
    assert ergebnis["searched"] == 3
    assert ergebnis["truncated"] is True


async def test_die_suche_meldet_das_abschneiden():
    instanz = Instanz(baum={"wurzel": [f"k{i}" for i in range(10)],
                            **{f"k{i}": [] for i in range(10)}},
                      inhalt={f"k{i}": [_material(f"m{i}", "Zelle")]
                              for i in range(10)})
    async with instanz.repo() as repo:
        ergebnis = await repo.flows.search_in_collection(
            "wurzel", "zelle", depth=2, max_collections=3)
    assert ergebnis["truncated"] is True
    assert len(ergebnis["hits"]) < 10


async def test_eine_leere_anfrage_wird_abgelehnt():
    instanz = Instanz()
    async with instanz.repo() as repo:
        with pytest.raises(ValueError, match="query"):
            await repo.flows.search_in_collection("wurzel", "  ")
    assert instanz.anfragen == []


# --- collection_stats -----------------------------------------------------

async def test_die_zahlen_kommen_aus_der_pagination():
    instanz = Instanz(
        baum={"wurzel": ["a", "b"]},
        inhalt={"wurzel": [_material(f"m{i}", f"M{i}") for i in range(7)]})
    async with instanz.repo() as repo:
        zahlen = await repo.flows.collection_stats("wurzel")
    assert zahlen["materials"] == 7
    assert zahlen["collections"] == 2


async def test_die_aufschluesselung_zaehlt_die_felder_aus():
    instanz = Instanz(
        baum={"wurzel": []},
        inhalt={"wurzel": [
            {"ref": {"id": "m1"}, "type": "ccm:io", "title": "Eins",
             "properties": {"cclom:title": ["Eins"],
                            "ccm:taxonid_DISPLAYNAME": ["Biologie"]}},
            {"ref": {"id": "m2"}, "type": "ccm:io", "title": "Zwei",
             "properties": {"cclom:title": ["Zwei"],
                            "ccm:taxonid_DISPLAYNAME": ["Biologie"]}},
            {"ref": {"id": "m3"}, "type": "ccm:io", "title": "Drei",
             "properties": {"cclom:title": ["Drei"],
                            "ccm:taxonid_DISPLAYNAME": ["Chemie"]}}]})
    async with instanz.repo() as repo:
        zahlen = await repo.flows.collection_stats("wurzel")
    assert zahlen["by"]["subject"] == {"Biologie": 2, "Chemie": 1}


async def test_die_stichprobe_wird_genannt():
    """Ausgezaehlt wird ueber die tatsaechlich geholten Kinder. Wer nicht
    weiss, dass es eine Stichprobe war, haelt sie fuer die Gesamtheit."""
    instanz = Instanz(
        baum={"wurzel": []},
        inhalt={"wurzel": [_material(f"m{i}", f"M{i}") for i in range(50)]})
    async with instanz.repo() as repo:
        zahlen = await repo.flows.collection_stats("wurzel", sample=10)
    assert zahlen["materials"] == 50
    assert zahlen["sampled"] == 10
    assert zahlen["complete"] is False


async def test_eine_kleine_sammlung_ist_vollstaendig_ausgezaehlt():
    instanz = Instanz(
        baum={"wurzel": []},
        inhalt={"wurzel": [_material(f"m{i}", f"M{i}") for i in range(3)]})
    async with instanz.repo() as repo:
        zahlen = await repo.flows.collection_stats("wurzel", sample=10)
    assert zahlen["sampled"] == 3
    assert zahlen["complete"] is True


async def test_die_zahlen_sind_json():
    instanz = Instanz()
    async with instanz.repo() as repo:
        json.dumps(await repo.flows.collection_stats("wurzel"))


async def test_die_zahlen_kosten_zwei_anfragen():
    instanz = Instanz()
    async with instanz.repo() as repo:
        await repo.flows.collection_stats("wurzel")
    assert len(instanz.anfragen) == 2, instanz.anfragen


async def test_eine_unlesbare_untersammlung_kostet_nicht_die_ganze_suche():
    """Audit A10. ``browse_tree`` findet Untersammlungen in der Antwort ihrer
    Eltern -- darunter also auch solche, die das Konto nie geoeffnet hat und
    deren Rechte es nicht kennt. Ein 403 unter fuenfundzwanzig machte aus einer
    Teilantwort gar keine.

    Dieselbe Grenze wie ueberall sonst: gemeldet statt geworfen, und die Zahl
    steht neben ``truncated`` -- das Modul argumentiert selbst, stilles
    Abschneiden lese sich wie Vollstaendigkeit.
    """
    instanz = Instanz()
    urspruenglich = instanz.handler

    def handler(request: httpx.Request) -> httpx.Response:
        pfad = request.url.path
        if pfad.endswith("/children") and "/nodes/-home-/b/" in pfad:
            instanz.anfragen.append(pfad)
            return httpx.Response(403, json={
                "error": "DAOSecurityException", "message": "nicht fuer dich"})
        return urspruenglich(request)

    instanz.handler = handler
    async with instanz.repo() as repo:
        ergebnis = await repo.flows.search_in_collection("wurzel", "zellteilung")
    assert [h["id"] for h in ergebnis["hits"]] == ["m1"], "der Rest wurde gesucht"
    assert ergebnis["unreadable"] == 1
    json.dumps(ergebnis)


async def test_ohne_ausfall_ist_unreadable_null():
    instanz = Instanz()
    async with instanz.repo() as repo:
        ergebnis = await repo.flows.search_in_collection("wurzel", "zellteilung")
    assert ergebnis["unreadable"] == 0
    assert ergebnis["failed"] == []


# --- Audit COR-2 (03.09.2026): "unreadable" war ein Sammelbecken -----------

def _verweigert(instanz: Instanz, sammlungen: tuple[str, ...], status: int) -> None:
    """Das Material-Listing der genannten Sammlungen antwortet mit ``status``."""
    urspruenglich = instanz.handler

    def handler(request: httpx.Request) -> httpx.Response:
        pfad = request.url.path
        if pfad.endswith("/children") and any(
            f"/nodes/-home-/{s}/" in pfad for s in sammlungen
        ):
            instanz.anfragen.append(pfad)
            return httpx.Response(status, json={
                "error": "DAOSecurityException", "message": "nicht fuer dich"})
        return urspruenglich(request)

    instanz.handler = handler


async def test_failed_nennt_die_verweigerte_sammlung_mit_grund():
    """Eine Zahl sagt nicht, *welche* Sammlung sich verweigert hat und warum.
    Wer nachsehen will, braucht die id und den Fehlertyp."""
    instanz = Instanz()
    _verweigert(instanz, ("b",), 403)
    async with instanz.repo() as repo:
        ergebnis = await repo.flows.search_in_collection("wurzel", "zellteilung")
    assert ergebnis["unreadable"] == 1
    assert [f["id"] for f in ergebnis["failed"]] == ["b"]
    assert ergebnis["failed"][0]["reason"].startswith("PermissionDeniedError")
    json.dumps(ergebnis)


async def test_scheitern_alle_listen_wirft_der_erste_fehler():
    """Mit falschem Passwort sagt jedes Listing 401 -- und die Antwort war
    "hits: [], unreadable: 4": eine Teilantwort ohne Teil. Nichts gelesen ist
    keine Antwort, sondern der Fehler."""
    instanz = Instanz()
    _verweigert(instanz, ("wurzel", "a", "b", "a1"), 401)
    async with instanz.repo() as repo:
        with pytest.raises(AuthenticationError):
            await repo.flows.search_in_collection("wurzel", "zellteilung")


async def test_ein_programmfehler_wird_nicht_zu_unreadable(monkeypatch):
    """``gather(return_exceptions=True)`` faengt alles -- auch einen TypeError
    aus dieser Bibliothek. Der ist kein "verweigert", der ist ein Fehler."""
    import edusharing.flows.tree as tree
    echt = tree.collection_contents

    async def kaputt(repo, collection_id, **kwargs):
        if collection_id == "b":
            raise RuntimeError("kaputt")
        return await echt(repo, collection_id, **kwargs)

    monkeypatch.setattr(tree, "collection_contents", kaputt)
    instanz = Instanz()
    async with instanz.repo() as repo:
        with pytest.raises(RuntimeError, match="kaputt"):
            await repo.flows.search_in_collection("wurzel", "zellteilung")


async def test_die_zaehler_teilen_die_stichprobe_nicht_auf():
    """Ein Feld ist mehrwertig -- live gemessen trugen 15 Materialien zusammen
    25 Stufenangaben. Wer die Zaehler als Aufteilung liest, rechnet falsch."""
    zwei_stufen = {"ref": {"id": "m1"}, "type": "ccm:io", "title": "Eins",
                   "properties": {"cclom:title": ["Eins"],
                                  "ccm:educationalcontext_DISPLAYNAME":
                                      ["Primarstufe", "Sekundarstufe I"]}}
    instanz = Instanz(baum={"wurzel": []}, inhalt={"wurzel": [zwei_stufen]})
    async with instanz.repo() as repo:
        zahlen = await repo.flows.collection_stats("wurzel")
    assert zahlen["sampled"] == 1
    assert sum(zahlen["by"]["level"].values()) == 2


# --- Zweite Runde (Review 02.09.2026, abends) ------------------------------

async def test_der_baum_traegt_keine_rohdaten():
    """Der Gang haelt jeden Datensatz (fuer find_collections); browse_tree gibt
    id, title, collections zurueck -- sonst nichts, auf jeder Ebene."""
    instanz = Instanz()
    async with instanz.repo() as repo:
        baum = await repo.flows.browse_tree("wurzel")

    def pruefe(eintraege):
        for e in eintraege:
            assert set(e) == {"id", "title", "collections"}, e
            pruefe(e["collections"])

    assert baum["collections"]
    pruefe(baum["collections"])


class MehrAlsEineSeite(Instanz):
    def handler(self, request: httpx.Request) -> httpx.Response:
        antwort = super().handler(request)
        if request.url.path.endswith("/children/collections"):
            data = antwort.json()
            data["pagination"] = {"total": 120, "from": 0, "count": len(data["collections"])}
            return httpx.Response(200, json=data)
        return antwort


async def test_mehr_untersammlungen_als_eine_seite_sind_abgeschnitten():
    instanz = MehrAlsEineSeite()
    async with instanz.repo() as repo:
        baum = await repo.flows.browse_tree("wurzel")
        suche = await repo.flows.search_in_collection("wurzel", "Zellteilung")
    assert baum["truncated"] is True
    assert suche["truncated"] is True
