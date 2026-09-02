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
from edusharing.placement import collections_of

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


async def test_placement_kostet_drei_anfragen_eine_je_frage():
    """Der Knoten, der Weg nach oben, die Sammlungen -- je einmal.

    Bis zum 02.09.2026 waren es zwei: parents liefert den Knoten mit. Seither
    wird er vorab gelesen, weil eine Listing-ID eine Referenz ist und die
    Sammlungen fuer das ORIGINAL zu erfragen sind (siehe unten). Was weiterhin
    nicht passiert: ein Nachlesen je gefundener Sammlung -- die usage-Antwort
    traegt jede vollstaendig."""
    instanz = Instanz()
    async with instanz.repo() as repo:
        await repo.flows.placement(NID)
    pfade = [r.url.path for r in instanz.anfragen]
    assert len(pfade) == 3, pfade
    assert sum(p.endswith("/metadata") for p in pfade) == 1


async def test_placement_nennt_den_titel_des_knotens():
    """Aus der parents-Antwort, in der er als erster steht -- deshalb kostet
    die Auskunft keine eigene Anfrage."""
    instanz = Instanz()
    async with instanz.repo() as repo:
        ergebnis = await repo.flows.placement(NID)
    assert ergebnis["title"] == "Mein Titel"


# --- Wenn eine der beiden Haelften nicht antwortet (Audit A3) -------------

async def test_ein_verweigerter_weg_nach_oben_kostet_nicht_die_sammlungen():
    """Gemessen am 28.08.2026 gegen Staging: ``/parents`` antwortet fuer
    **fremdes** Material mit 500 AccessDeniedException, waehrend derselbe
    Endpunkt bei einem eigenen Knoten ein sauberes 403 liefert. Fremdes
    Material ist das, was eine Suche liefert -- und ``placement`` warf damit
    bei **18 von 20** Materialtreffern, obwohl die Sammlungshaelfte jedes Mal
    antwortete. Von 58 solchen Knoten haetten 48 eine brauchbare Antwort
    geliefert, 4 davon mit echten Sammlungszugehoerigkeiten.

    Jeder andere Teilausfall in dieser Bibliothek wird berichtet statt
    geworfen: ``describe_many`` ueberlebt tote Knoten, ``collections.find``
    ueberlebt einen ausgefallenen Weg. ``placement`` war der Ausreisser.
    """
    instanz = Instanz(eltern_fehler=403)
    async with instanz.repo() as repo:
        ergebnis = await repo.flows.placement(NID)
    assert [s["id"] for s in ergebnis["collections"]] == ["s-1", "s-2"]
    assert ergebnis["path"] == []
    assert ergebnis["failed"] == [
        {"part": "path", "reason": ergebnis["failed"][0]["reason"]}]
    assert "PermissionDeniedError" in ergebnis["failed"][0]["reason"]
    json.dumps(ergebnis)


async def test_verweigerte_sammlungen_kosten_nicht_den_weg_nach_oben():
    """Die Gegenrichtung: ``/usage/v1/.../collections`` antwortet gemessen mit
    500 fuer eine ID, fuer die der Knotenendpunkt 404 sagt."""
    instanz = Instanz()
    urspruenglich = instanz.handler

    def handler(request: httpx.Request) -> httpx.Response:
        if "/usage/v1" in request.url.path:
            instanz.anfragen.append(request)
            return httpx.Response(500, json={
                "error": "java.lang.Exception", "message": "Node does not exist"})
        return urspruenglich(request)

    instanz.handler = handler
    async with instanz.repo() as repo:
        ergebnis = await repo.flows.placement(NID)
    assert [s["title"] for s in ergebnis["path"]] == ["Oberordner", "Unterordner"]
    assert ergebnis["collections"] == []
    assert ergebnis["failed"][0]["part"] == "collections"
    assert "NotFoundError" in ergebnis["failed"][0]["reason"]


async def test_faellt_beides_aus_wird_geworfen():
    """Nichts zu berichten ist kein Teilergebnis. Ein leeres ``placement`` waere
    die Behauptung, der Knoten liege nirgends -- ``collections.find`` zieht
    dieselbe Grenze."""
    instanz = Instanz(eltern_fehler=403)
    urspruenglich = instanz.handler

    def handler(request: httpx.Request) -> httpx.Response:
        if "/usage/v1" in request.url.path:
            instanz.anfragen.append(request)
            return httpx.Response(403, json={
                "error": "DAOSecurityException", "message": "nein"})
        return urspruenglich(request)

    instanz.handler = handler
    async with instanz.repo() as repo:
        with pytest.raises(PermissionDeniedError):
            await repo.flows.placement(NID)


async def test_ohne_ausfall_bleibt_failed_leer():
    """Gegenprobe: das neue Feld darf im Normalfall nicht stoeren."""
    instanz = Instanz()
    async with instanz.repo() as repo:
        ergebnis = await repo.flows.placement(NID)
    assert ergebnis["failed"] == []


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


# --- Die Referenz-Falle ---------------------------------------------------
#
# Gemessen gegen Staging am 02.09.2026, Sammlung "Ungleichungen": das erste
# Material im Listing traegt ``ccm:collection_io_reference`` und
# ``originalId``. ``/usage/v1/usages/node/{id}/collections`` kennt nur das
# Original -- fuer die Listing-ID antwortet es 200 mit leerer Liste:
#
#     collections_of(Listing-ID) = 0     collections_of(Original) = 2
#
# Die Bibliothek sagte damit "in keiner Sammlung" fuer ein Material, das in
# zweien liegt. Kein Fehler, kein Hinweis. Darum wird IMMER ueber das Original
# gefragt, und wer den Knoten schon hat, uebergibt es, statt ihn erneut zu lesen.

REF_ID, ORIG_ID = "r-1", "o-1"


def _referenz() -> dict:
    data = _knoten(REF_ID, "k.txt", "Mein Titel", typ="ccm:io")
    data["originalId"] = ORIG_ID
    data["aspects"] = ["ccm:collection_io_reference"]
    data["properties"]["ccm:original"] = [ORIG_ID]
    return data


class Referenz(Instanz):
    """Eine Referenz ``r-1`` auf das Original ``o-1``; usage antwortet nur dem Original."""

    def handler(self, request: httpx.Request) -> httpx.Response:
        self.anfragen.append(request)
        pfad = request.url.path
        if pfad.endswith("/metadata"):
            original = _knoten(ORIG_ID, "k.txt", "Mein Titel", typ="ccm:io")
            data = _referenz() if f"/{REF_ID}/" in pfad else original
            return httpx.Response(200, json={"node": data})
        if pfad.endswith("/parents"):
            return httpx.Response(200, json={"nodes": [_referenz(), _knoten("oben", "o", "Oben")],
                                             "pagination": None, "scope": "MY_FILES"})
        if "/usage/v1" in pfad:
            wen = pfad.split("/usages/node/")[1].split("/")[0]
            return httpx.Response(200, json=NUTZUNGEN if wen == ORIG_ID else [])
        raise AssertionError(f"unerwartet: {request.method} {pfad}")

    def usage_pfad(self) -> str:
        return next(a.url.path for a in self.anfragen if "/usage/v1" in a.url.path)

    def metadata_abrufe(self) -> int:
        return sum(1 for a in self.anfragen if a.url.path.endswith("/metadata"))


async def test_collections_of_fragt_das_original_einer_referenz():
    instanz = Referenz()
    async with instanz.repo() as repo:
        sammlungen = await collections_of(repo.nodes, REF_ID)
    assert [s.id for s in sammlungen] == ["s-1", "s-2"]
    assert instanz.usage_pfad().endswith(f"/usages/node/{ORIG_ID}/collections")


async def test_collections_of_nimmt_auch_das_repositorium():
    """Jede andere freie Funktion nimmt ``repo``; diese nahm ``Nodes`` -- und
    die Referenz dokumentierte ``repo``. Beides gilt jetzt."""
    instanz = Referenz()
    async with instanz.repo() as repo:
        assert len(await collections_of(repo, REF_ID)) == 2


async def test_mit_bekanntem_original_wird_der_knoten_nicht_gelesen():
    instanz = Referenz()
    async with instanz.repo() as repo:
        await collections_of(repo.nodes, REF_ID, original_id=ORIG_ID)
    assert instanz.metadata_abrufe() == 0
    assert instanz.usage_pfad().endswith(f"/usages/node/{ORIG_ID}/collections")


async def test_node_collections_uebergibt_sein_eigenes_original():
    """Der Knoten liegt schon vor -- ein zweiter Abruf waere eine Anfrage fuer nichts."""
    instanz = Referenz()
    async with instanz.repo() as repo:
        knoten = await repo.node(REF_ID)
        vorher = len(instanz.anfragen)
        sammlungen = await knoten.collections()
    assert [s.id for s in sammlungen] == ["s-1", "s-2"]
    assert len(instanz.anfragen) == vorher + 1


async def test_placement_liest_einmal_und_nennt_das_original():
    instanz = Referenz()
    async with instanz.repo() as repo:
        lage = await repo.flows.placement(REF_ID)
    assert lage["id"] == REF_ID
    assert lage["original_id"] == ORIG_ID
    assert [c["id"] for c in lage["collections"]] == ["s-1", "s-2"]
    assert instanz.usage_pfad().endswith(f"/usages/node/{ORIG_ID}/collections")
    assert instanz.metadata_abrufe() == 1


async def test_placement_eines_originals_nennt_kein_original():
    instanz = Referenz()
    async with instanz.repo() as repo:
        lage = await repo.flows.placement(ORIG_ID)
    assert lage["original_id"] is None
    assert instanz.usage_pfad().endswith(f"/usages/node/{ORIG_ID}/collections")
