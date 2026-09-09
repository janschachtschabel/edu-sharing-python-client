"""Vier Schichten, fuenf Vertraege: HTTP-Antwort bis blockierender Zugang.

Die Zweitpruefung vom 09.09.2026 verlangt in Abschnitt 7 „wenige gezielte
Integrationstests" der Form **HTTP-Antwort -> Modell -> oeffentlicher Flow ->
synchroner Wrapper** und nennt als Abnahmekriterium der Reihe B woertlich:
„ACL-, Referenz-, Quellen- und Vollstaendigkeitsinformationen bleiben bis zur
oeffentlichen Oberflaeche korrekt".

Warum das nicht schon dastand: ``test_sync_surface.py`` geht zwar alle vier
Schichten, prueft aber die **Form** -- „ist das Ergebnis keine Coroutine".
Gemessen am 09.09.2026 kam keiner der in dieser Runde reparierten Werte --
``facet_meta``, ``source_url``, ``variants_total``, das ausgeschlossene
Original -- irgendwo durch den synchronen Zugang hindurch vor. Genau dort
sitzen aber die Fehler dieser Runde: nicht in der Schicht, die einen Wert
liest, sondern in der, die ihn weiterreicht.

Deshalb je ein Durchgang pro genannter Art, jeder mit einer Gegenprobe oder
einem zweiten Wert daneben, damit keiner gruen bleiben kann, weil die Antwort
leer ist. Jede Wache ist mutiert worden: die Reparatur im Quelltext
zurueckgedreht, der Test rot gesehen.

Ein Handler fuer alle fuenf. Ein Repositorium beantwortet auch nicht je Frage
aus einer anderen Welt, und ein gemeinsamer Knoten deckt auf, wenn zwei
Ablaeufe dieselbe Antwort verschieden lesen.
"""

import contextlib
import json

import httpx
import pytest

from edusharing import Repository
from edusharing.errors import SilentDropError

REPO = "https://repo.test/edu-sharing"

REF = "ref-1"            # Eine Sammlungsreferenz -- der uebliche Ausgangspunkt
ORIGINAL = "original-1"  # ... und ihr Original, ein anderer Datensatz
ANDERES = "b"
SAMMLUNG = "col-1"
ORDNER = "folder-1"
SEITE = "https://beispiel.test/arbeitsblatt"

FACH = "http://w3id.org/openeduhub/vocabs/discipline/080"
STUFE = "http://w3id.org/openeduhub/vocabs/educationalContext/sekundarstufe_1"

VOKABULAR = {
    "ccm:taxonid": [{"key": FACH, "displayString": "Biologie"}],
    "ccm:educationalcontext": [{"key": STUFE, "displayString": "Sekundarstufe I"}],
}


def _ref(node_id: str) -> str:
    return f"workspace://SpacesStore/{node_id}"


def _material(nid: str, titel: str, *, url: str | None = None,
              original: str | None = None) -> dict:
    eigenschaften: dict[str, list[str]] = {
        "cclom:title": [titel],
        "ccm:taxonid": [FACH],
        "ccm:taxonid_DISPLAYNAME": ["Biologie"],
        "ccm:educationalcontext": [STUFE],
        "ccm:educationalcontext_DISPLAYNAME": ["Sekundarstufe I"],
    }
    if url:
        eigenschaften["ccm:wwwurl"] = [url]
    knoten = {"ref": {"id": nid}, "title": titel, "type": "ccm:io",
              "mimetype": "text/html", "content": {"hash": None},
              "properties": eigenschaften}
    if original:
        knoten["originalId"] = original
    return knoten


def _ordnerknoten(nid: str, *, props: dict | None = None) -> dict:
    eigen = {"cclom:title": [nid], "cm:name": [nid]}
    eigen.update(props or {})
    return {"ref": {"id": nid}, "type": "ccm:map", "title": nid, "name": nid,
            "properties": eigen, "access": ["Read"]}


def _variante(nid: str) -> dict:
    return _ordnerknoten(nid, props={
        "ccm:page_variant_config": [json.dumps({"structure": {"swimlanes": [
            # Ohne ``nodeId`` -- diese Datei fragt nach der Variantenliste, und
            # eine Widget-Aufloesung daneben waere eine zweite Ursache fuer
            # ``truncated``.
            {"heading": "Eine", "type": "container",
             "grid": [{"item": "wlo-editorial-members"}]}]}})],
        "ccm:page_variant_is_template": ["false"]})


def _ace(name: str, *rechte: str, typ: str = "USER") -> dict:
    return {"authority": {"authorityName": name, "authorityType": typ},
            "permissions": list(rechte), "editable": True}


# 51 Varianten: eine mehr, als der Ablauf mit ``maxItems=50`` holt. Der Default
# liegt auf der letzten und ist damit gerade nicht dabei -- das ist der Fall,
# den R04 gemessen hat.
VARIANTEN = [f"v{i}" for i in range(51)]

VARIANTENZAHL = len(VARIANTEN)
GEHOLT = 50


class Instanz:
    """Ein Repositorium fuer alle fuenf Vertraege.

    Der Ausgangsknoten ``ref-1`` ist eine Referenz auf ``original-1``, traegt
    eine verlinkte Seite und hat Repository-Text. Die Suche liefert sein
    Original, ein anderes Material und eine gekuerzte Facette. Die Sammlung
    ``col-1`` zeigt auf einen Seitenordner mit 51 Varianten.
    """

    def __init__(self, *, eigene: list[dict] | None = None,
                 taub: bool = False, rest: int = 30) -> None:
        self.text = "Ein Text im Repositorium."
        self.rest = rest
        self.inherits = True
        self.eigene = list(eigene or [])
        # ``taub`` bildet den gemessenen Server nach, der nur die zuletzt
        # genannte Autoritaet behaelt und dabei die Vererbung abschaltet (R03).
        self.taub = taub
        self.geschrieben: list[dict] = []
        self.knoten = {
            REF: _material(REF, "Zellteilung", url=SEITE, original=ORIGINAL),
            ORIGINAL: _material(ORIGINAL, "Zellteilung"),
            ANDERES: _material(ANDERES, "Photosynthese"),
        }

    # --- Antworten ---------------------------------------------------------

    def _rechte(self) -> dict:
        return {"permissions": {
            "localPermissions": {"inherited": self.inherits,
                                 "permissions": self.eigene},
            "inheritedPermissions": [_ace("ROLE_OWNER", "All", typ="OWNER")]}}

    def _suchtreffer(self) -> dict:
        nodes = [self.knoten[ORIGINAL], self.knoten[ANDERES]]
        return {
            "nodes": nodes,
            "pagination": {"total": 211, "from": 0, "count": len(nodes)},
            "facets": [{
                "property": "ccm:taxonid",
                "values": [{"value": "Biologie", "count": 70}],
                # Der Server hat 30 weitere Werte, die er nicht ausgibt.
                "sumOtherDocCount": self.rest,
            }],
        }

    def handler(self, request: httpx.Request) -> httpx.Response:
        pfad, url = request.url.path, str(request.url)

        if pfad.endswith("/permissions"):
            if request.method == "GET":
                return httpx.Response(200, json=self._rechte())
            koerper = json.loads(request.content)
            self.geschrieben.append(koerper)
            if self.taub:
                self.inherits = False
                self.eigene = koerper["permissions"][-1:]
            else:
                self.inherits = koerper["inherited"]
                self.eigene = list(koerper["permissions"])
            return httpx.Response(200, content=b"")

        if pfad.endswith("/textContent"):
            return httpx.Response(200, json={"text": self.text})

        if "/values" in pfad:
            # Die Property steht im Rumpf, nicht im Pfad.
            prop = json.loads(request.content)["valueParameters"]["property"]
            return httpx.Response(200, json={"values": VOKABULAR.get(prop, [])})

        if "/collection/v1/collections/-home-/search" in url:
            return httpx.Response(200, json={"collections": []})

        if "/search/v1" in pfad:
            return httpx.Response(200, json=self._suchtreffer())

        if pfad.endswith("/children"):
            wieviel = int(request.url.params.get("maxItems") or 20)
            teil = [_variante(n) for n in VARIANTEN[:wieviel]]
            return httpx.Response(200, json={
                "nodes": teil,
                "pagination": {"total": VARIANTENZAHL, "from": 0,
                               "count": len(teil)}})

        if pfad.endswith("/metadata"):
            nid = pfad.rsplit("/", 2)[-2]
            if nid in self.knoten:
                return httpx.Response(200, json={"node": self.knoten[nid]})
            if nid == SAMMLUNG:
                return httpx.Response(200, json={"node": _ordnerknoten(
                    SAMMLUNG, props={"ccm:page_config_ref": [_ref(ORDNER)]})})
            if nid == ORDNER:
                return httpx.Response(200, json={"node": _ordnerknoten(
                    ORDNER, props={"ccm:page_config": [json.dumps({
                        "variants": [_ref(n) for n in VARIANTEN],
                        "default": _ref(VARIANTEN[-1])})]})})
            if nid in VARIANTEN:
                return httpx.Response(200, json={"node": _variante(nid)})
            return httpx.Response(404, json={
                "error": "DAOMissingException", "message": f"kein Knoten: {nid}"})

        raise AssertionError(f"nicht gemockt: {request.method} {url}")


@contextlib.contextmanager
def _repo(instanz: Instanz):
    """Der blockierende Zugang -- derselbe, den ein Notizbuch benutzt."""
    verbindung = Repository(
        REPO, metadataset="mds_oeh", backoff_base=0.0,
        client=httpx.AsyncClient(transport=httpx.MockTransport(instanz.handler)))
    try:
        yield verbindung
    finally:
        verbindung.close()


# --- ACL --------------------------------------------------------------------

def test_acl_ein_stiller_verlust_erreicht_den_blockierenden_aufrufer():
    """R03 durch alle vier Schichten.

    Der Server nimmt nur den neuen Eintrag und schaltet die Vererbung ab. Der
    Vergleich passiert tief im asynchronen Teil; hier steht die Frage, ob der
    Aufrufer davon erfaehrt, der nie ein ``await`` schreibt. Ein Ablauf, der
    eine Ausnahme ueber die Schleifengrenze verliert, meldet stattdessen
    Erfolg -- und das ist bei Rechten der teuerste Fehler ueberhaupt.
    """
    instanz = Instanz(eigene=[_ace("alice", "Coordinator")], taub=True)
    with _repo(instanz) as repo, pytest.raises(SilentDropError) as fehler:
        repo.node(REF).permissions.grant("bob", "Consumer")

    assert "alice" in str(fehler.value)
    assert "inherit" in str(fehler.value).lower()
    assert instanz.geschrieben, "geschrieben wurde bereits"


def test_acl_ein_gelungener_grant_meldet_weiterhin_wahr():
    """Die Gegenprobe. Ohne sie waere die Wache oben auch gruen, wenn der
    synchrone Zugang jeden Grant ablehnt."""
    instanz = Instanz(eigene=[_ace("alice", "Coordinator")])
    with _repo(instanz) as repo:
        assert repo.node(REF).permissions.grant("bob", "Consumer") is True
        rechte = repo.node(REF).permissions.get()

    assert sorted(a.authority for a in rechte.own) == ["alice", "bob"]
    assert rechte.inherits is True


# --- Referenz ---------------------------------------------------------------

def test_referenz_das_eigene_original_faellt_heraus():
    """R08 durch alle vier Schichten.

    Ausgangspunkt ist eine Referenz, ihr Original steht im Suchergebnis. Ein
    „Aehnliches"-Streifen unter einer Sammlungsansicht empfiehlt sonst genau
    das Material, das der Nutzer gerade ansieht -- unter anderer ID, also
    ohne dass es jemandem als Wiederholung auffaellt.
    """
    with _repo(Instanz()) as repo:
        ergebnis = repo.flows.related(REF)

    assert [h["id"] for h in ergebnis["hits"]] == [ANDERES]


# --- Quellen ----------------------------------------------------------------

def test_quellen_der_repository_text_traegt_die_quell_url():
    """R07 durch alle vier Schichten.

    ``source_url`` wurde erst nach dem fruehen Rueckgabepfad gesetzt und fehlte
    damit im haeufigsten Fall. Eine Quellenangabe, die nur auf dem seltenen Weg
    ankommt, ist fuer eine Zitatliste keine.
    """
    with _repo(Instanz()) as repo:
        antwort = repo.flows.text(REF)

    assert antwort["source"] == "repository"
    assert antwort["source_url"] == SEITE
    assert antwort["text"] == "Ein Text im Repositorium."


# --- Vollstaendigkeit -------------------------------------------------------

def test_vollstaendigkeit_die_facetten_restanzahl_kommt_an():
    """R06 durch alle vier Schichten.

    Die Werteliste bleibt, wo sie war -- die Restanzahl steht daneben. Beide
    Karten werden geprueft: eine Filterleiste, die nur ``facets`` liest, haelt
    eine gekuerzte Liste sonst fuer vollstaendig.
    """
    with _repo(Instanz(rest=30)) as repo:
        antwort = repo.flows.search("Zellteilung", facets=["subject"])

    assert antwort["facets"]["subject"] == [{"value": "Biologie", "count": 70}]
    assert antwort["facet_meta"]["subject"] == {"other_count": 30, "truncated": True}


def test_vollstaendigkeit_eine_ganze_facette_sagt_es_ebenso():
    """Die Gegenprobe: ``other_count=0`` muss durch den synchronen Zugang
    darstellbar bleiben. Sonst heisst „kein Wert" einmal vollstaendig und
    einmal nicht gefragt."""
    with _repo(Instanz(rest=0)) as repo:
        antwort = repo.flows.search("Zellteilung", facets=["subject"])

    assert antwort["facet_meta"]["subject"] == {"other_count": 0, "truncated": False}


def test_vollstaendigkeit_die_gekuerzte_variantenliste_kommt_an():
    """R04 durch alle vier Schichten.

    51 Varianten, der Default liegt auf der letzten und ist damit nicht in den
    geholten 50. ``rendered=None`` hiess frueher „der Ordner hat keine
    Varianten"; mit der Kuerzung heisst es „noch nicht geladen". Ohne
    ``truncated_by`` und ``variants_total`` kann der Aufrufer die beiden nicht
    auseinanderhalten -- und meldet die Seite als leer.
    """
    with _repo(Instanz()) as repo:
        seite = repo.flows.page(SAMMLUNG)

    assert seite["truncated"] is True
    assert seite["truncated_by"] == ["variants"]
    assert seite["variants_total"] == VARIANTENZAHL
    assert len(seite["variants"]) == GEHOLT
