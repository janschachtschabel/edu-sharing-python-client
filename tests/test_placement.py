"""Wo ein Knoten liegt -- und wer ihn kuratiert hat.

Zwei Fragen, zwei Endpunkte, beide bisher nur ueber ``repo.raw`` erreichbar:

* ``GET /node/v1/nodes/-home-/{id}/parents`` -- der Weg nach oben.
* ``GET /usage/v1/usages/node/{id}/collections`` -- die Sammlungen, die eine
  Referenz auf den Knoten halten. Das ist nicht dasselbe: eine Sammlung
  verweist auf Knoten, deren Elternteil ganz woanders liegt.

Gemessen gegen Staging am 28.08.2026 in einem eigens angelegten Ordner:

* ``parents`` liefert den Knoten **selbst** als ersten Eintrag, danach die
  Vorfahren, der naechste zuerst. Wer das nicht abzieht, zaehlt ihn als seinen
  eigenen Vorfahren.
* ``fullPath=true`` endet fuer ein gewoehnliches Konto mit **HTTP 403** -- der
  vollstaendige Weg fuehrt durch Bereiche, die es nicht lesen darf. Ohne den
  Parameter reicht die Antwort bis zur Grenze des Erlaubten und nennt sie in
  ``scope``.
* Ohne ``propertyFilter=-all-`` kommen die Vorfahren mit **leeren**
  ``properties`` zurueck -- Namen ja, Titel nein.
* ``usages`` antwortet mit einer **Liste**, nicht mit einem Objekt, und jeder
  Eintrag traegt unter ``collection`` einen vollstaendigen Knoten.
"""

import json

import httpx
import pytest

from edusharing import AsyncRepository
from edusharing.errors import PermissionDeniedError

REPO = "https://repo.test/edu-sharing"
NID = "k-1"


def _knoten(node_id: str, name: str, titel: str, typ: str = "ccm:map") -> dict:
    return {"ref": {"id": node_id, "repo": "local"}, "name": name, "type": typ,
            "title": titel, "isPublic": False,
            "properties": {"cm:name": [name], "cclom:title": [titel]}}


# Die gemessene Antwortform: der Knoten selbst zuerst, dann aufwaerts.
ELTERN = {"nodes": [
    _knoten(NID, "k.txt", "Mein Titel", typ="ccm:io"),
    _knoten("unter", "unterordner", "Unterordner"),
    _knoten("oben", "oberordner", "Oberordner"),
], "pagination": None, "scope": "MY_FILES"}

# Und die von usages: eine Liste, jeder Eintrag mit vollem Knoten.
NUTZUNGEN = [
    {"nodeId": "ref-1", "parentNodeId": NID, "type": "DIRECT",
     "collection": _knoten("s-1", "Sammlung A", "Sammlung A")},
    {"nodeId": "ref-2", "parentNodeId": NID, "type": "DIRECT",
     "collection": _knoten("s-2", "Sammlung B", "Sammlung B")},
]


class Instanz:
    def __init__(self, *, eltern: dict | None = None,
                 nutzungen: list | None = None,
                 eltern_fehler: int | None = None) -> None:
        self.eltern = ELTERN if eltern is None else eltern
        self.nutzungen = NUTZUNGEN if nutzungen is None else nutzungen
        self.eltern_fehler = eltern_fehler
        self.anfragen: list[httpx.Request] = []

    def handler(self, request: httpx.Request) -> httpx.Response:
        self.anfragen.append(request)
        pfad = request.url.path
        if pfad.endswith("/parents"):
            if self.eltern_fehler:
                return httpx.Response(self.eltern_fehler, json={
                    "error": "DAOSecurityException", "message": "Zugriff verweigert"})
            return httpx.Response(200, json=self.eltern)
        if "/usage/v1" in pfad:
            return httpx.Response(200, json=self.nutzungen)
        return httpx.Response(200, json={"node": _knoten(NID, "k.txt", "Mein Titel",
                                                         typ="ccm:io")})

    def repo(self) -> AsyncRepository:
        return AsyncRepository(
            REPO, metadataset="mds_oeh", backoff_base=0.0,
            client=httpx.AsyncClient(transport=httpx.MockTransport(self.handler)))

    def params(self, teil: str) -> dict:
        for r in self.anfragen:
            if teil in r.url.path:
                return dict(r.url.params)
        raise AssertionError(f"keine Anfrage an {teil}")


# --- Der Weg nach oben ----------------------------------------------------

async def test_der_knoten_selbst_zaehlt_nicht_als_eigener_vorfahre():
    """Gemessen steht er als erster in der Antwort. Ihn stehen zu lassen hiesse,
    jeden Brotkrumenpfad um einen falschen Schritt zu verlaengern."""
    instanz = Instanz()
    async with instanz.repo() as repo:
        knoten = await repo.node(NID)
        eltern = await knoten.parents()
    assert [n.id for n in eltern] == ["unter", "oben"]


async def test_die_reihenfolge_bleibt_wie_die_antwort_sie_gibt():
    """Der naechste zuerst -- so heisst die Methode auch. Wer von oben nach
    unten anzeigen will, dreht um; der Ablauf tut genau das."""
    instanz = Instanz()
    async with instanz.repo() as repo:
        knoten = await repo.node(NID)
        eltern = await knoten.parents()
    assert [n.title for n in eltern] == ["Unterordner", "Oberordner"]


async def test_eigenschaften_werden_mitgelesen():
    """Ohne propertyFilter kommen die Vorfahren mit leeren properties zurueck --
    gemessen. Ein Pfad ohne Titel ist als Brotkrume unbrauchbar."""
    instanz = Instanz()
    async with instanz.repo() as repo:
        knoten = await repo.node(NID)
        await knoten.parents()
    assert instanz.params("/parents")["propertyFilter"] == "-all-"


async def test_der_volle_pfad_wird_nicht_verlangt():
    """fullPath=true endet fuer ein gewoehnliches Konto mit 403 -- gemessen.
    Ihn ungefragt zu verlangen hiesse, die Methode fuer die Mehrheit der
    Konten unbrauchbar zu machen."""
    instanz = Instanz()
    async with instanz.repo() as repo:
        knoten = await repo.node(NID)
        await knoten.parents()
    assert instanz.params("/parents").get("fullPath") in (None, "false")


async def test_ein_knoten_ganz_oben_hat_keine_vorfahren():
    instanz = Instanz(eltern={"nodes": [_knoten(NID, "k.txt", "Titel", typ="ccm:io")],
                              "scope": "MY_FILES"})
    async with instanz.repo() as repo:
        knoten = await repo.node(NID)
        assert await knoten.parents() == []


async def test_ein_403_wird_durchgereicht():
    """Nicht zu leeren Vorfahren verschlucken: kein Weg nach oben und ein
    verweigerter Weg nach oben sind verschiedene Auskuenfte."""
    instanz = Instanz(eltern_fehler=403)
    async with instanz.repo() as repo:
        knoten = await repo.node(NID)
        with pytest.raises(PermissionDeniedError):
            await knoten.parents()


# --- Die Sammlungen -------------------------------------------------------

async def test_sammlungen_die_den_knoten_halten():
    instanz = Instanz()
    async with instanz.repo() as repo:
        knoten = await repo.node(NID)
        sammlungen = await knoten.collections()
    assert [s.id for s in sammlungen] == ["s-1", "s-2"]
    assert [s.title for s in sammlungen] == ["Sammlung A", "Sammlung B"]


async def test_ohne_sammlung_eine_leere_liste():
    instanz = Instanz(nutzungen=[])
    async with instanz.repo() as repo:
        knoten = await repo.node(NID)
        assert await knoten.collections() == []


async def test_ein_eintrag_ohne_sammlung_wird_uebergangen():
    """Die Antwort ist eine Nutzungsliste, keine Sammlungsliste -- ein Eintrag
    ohne collection-Block waere sonst ein Knoten ohne ID."""
    instanz = Instanz(nutzungen=[{"nodeId": "ref-1", "collection": None},
                                 NUTZUNGEN[0]])
    async with instanz.repo() as repo:
        knoten = await repo.node(NID)
        assert [s.id for s in await knoten.collections()] == ["s-1"]


async def test_sammlungen_sind_vollwertige_knoten():
    """Der usage-Eintrag traegt den ganzen Knoten -- gemessen mit properties,
    Titel und isPublic. Also braucht niemand sie einzeln nachzulesen."""
    instanz = Instanz()
    async with instanz.repo() as repo:
        knoten = await repo.node(NID)
        erste = (await knoten.collections())[0]
    assert erste.get("cclom:title") == "Sammlung A"
    assert erste.is_public is False
    assert len(instanz.anfragen) == 2, "keine Nachlese je Sammlung"


# --- Der Ablauf -----------------------------------------------------------

async def test_placement_beantwortet_beide_fragen_in_einem_aufruf():
    instanz = Instanz()
    async with instanz.repo() as repo:
        ergebnis = await repo.flows.placement(NID)
    assert [s["id"] for s in ergebnis["collections"]] == ["s-1", "s-2"]
    assert ergebnis["id"] == NID
    json.dumps(ergebnis)


async def test_der_pfad_laeuft_von_oben_nach_unten():
    """Anders als ``node.parents()``, das die Antwort des Endpunkts spiegelt.
    Ein Brotkrumenpfad wird von oben gelesen, und der Ablauf ist die Schicht,
    die fuer die Anzeige da ist."""
    instanz = Instanz()
    async with instanz.repo() as repo:
        ergebnis = await repo.flows.placement(NID)
    assert [s["title"] for s in ergebnis["path"]] == ["Oberordner", "Unterordner"]


async def test_placement_kostet_zwei_anfragen():
    """Beide Endpunkte, parallel. Ein dritter Aufruf waere das Nachlesen des
    Knotens -- den fragt der Ablauf nicht, weil parents ihn schon mitliefert."""
    instanz = Instanz()
    async with instanz.repo() as repo:
        await repo.flows.placement(NID)
    assert len(instanz.anfragen) == 2, [r.url.path for r in instanz.anfragen]


async def test_placement_nennt_den_titel_des_knotens():
    """Aus der parents-Antwort, in der er als erster steht -- deshalb kostet
    die Auskunft keine eigene Anfrage."""
    instanz = Instanz()
    async with instanz.repo() as repo:
        ergebnis = await repo.flows.placement(NID)
    assert ergebnis["title"] == "Mein Titel"


# --- Wie weit die Antwort reicht ------------------------------------------

async def test_der_scope_wird_durchgereicht():
    """Der Pfad endet an der Grenze des Erlaubten, und scope benennt sie.
    Ohne die Angabe geht ein abgeschnittener Pfad als vollstaendiger durch."""
    instanz = Instanz()
    async with instanz.repo() as repo:
        ergebnis = await repo.flows.placement(NID)
    assert ergebnis["scope"] == "MY_FILES"


async def test_eine_leere_antwort_hat_keinen_titel():
    """Statt auf einen Knoten zuzugreifen, den die Antwort nicht enthaelt."""
    instanz = Instanz(eltern={"nodes": [], "scope": ""})
    async with instanz.repo() as repo:
        ergebnis = await repo.flows.placement(NID)
    assert ergebnis["title"] is None
    assert ergebnis["path"] == []


async def test_ein_pfadschritt_faellt_auf_den_namen_zurueck():
    """Ordner tragen oft keinen Titel -- gemessen ueberschreibt edu-sharing
    cm:title beim Anlegen mit cm:name. Ein leerer Brotkrumen waere die Folge."""
    ohne_titel = {"ref": {"id": "unter"}, "name": "unterordner", "type": "ccm:map",
                  "properties": {"cm:name": ["unterordner"]}}
    instanz = Instanz(eltern={"nodes": [
        _knoten(NID, "k.txt", "Mein Titel", typ="ccm:io"), ohne_titel],
        "scope": "MY_FILES"})
    async with instanz.repo() as repo:
        ergebnis = await repo.flows.placement(NID)
    assert ergebnis["path"][0]["title"] == "unterordner"


async def test_ancestry_repr_nennt_das_wesentliche():
    from edusharing.placement import ancestry_of
    instanz = Instanz()
    async with instanz.repo() as repo:
        herkunft = await ancestry_of(repo.nodes, NID)
    assert repr(herkunft) == "Ancestry(parents=2, scope='MY_FILES')"
