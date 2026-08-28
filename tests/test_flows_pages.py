"""Kuratierte Seiten als Ablauf: ausgeben und finden.

Die beiden Abläufe, die der MCP als ``get_topic_page_content`` und
``search_wlo_topic_pages`` anbietet -- nur ohne die WLO-Annahme, dass eine
solche Seite „Themenseite" heißt.

Zwei gemessene Dinge bestimmen ihre Form (Staging, 28.08.2026):

* **Auf ``ccm:page_config_ref`` lässt sich nicht filtern** -- HTTP 400, das
  Widget steht nicht in der MDS. Eine Seite wird also aus der *Antwort*
  erkannt. Weil die Sammlungssuche jetzt Eigenschaften mitliefert, kostet das
  eine Anfrage statt 1 + n.
* **Weg B der Sammlungssuche hat eine feste Projektion** und bleibt
  eigenschaftslos. Treffer, die nur er fand, lassen sich nicht beurteilen --
  darum meldet ``find_pages``, wie viele es überhaupt beurteilen konnte.

Die gespeicherten Suchen der Widgets werden **nicht ausgeführt**. Sie tragen
``virtual:``-Felder, die die MDS nicht kennt; was ohne Raten geht, ist die
feste Liste ``sortedNodeIds``.
"""

import json

import httpx
import pytest

from edusharing import AsyncRepository

REPO = "https://repo.test/edu-sharing"

SAMMLUNG = "col-1"
ORDNER = "folder-1"
V1 = "var-1"
V2 = "var-2"
WIDGET_LISTE = "w-liste"
WIDGET_SUCHE = "w-suche"


def _ref(node_id: str) -> str:
    return f"workspace://SpacesStore/{node_id}"


def _node(nid: str, *, titel: str = "", typ: str = "ccm:map",
          props: dict | None = None) -> dict:
    eigen = {"cclom:title": [titel or nid], "cm:name": [titel or nid]}
    eigen.update(props or {})
    return {"ref": {"id": nid}, "type": typ, "title": titel or nid,
            "name": titel or nid, "properties": eigen, "access": ["Read"]}


def _variante(nid: str, titel: str, lanes: list[dict]) -> dict:
    return _node(nid, titel=titel, props={
        "ccm:page_variant_config": [json.dumps({"structure": {"swimlanes": lanes}})],
        "ccm:page_variant_is_template": ["false"]})


LANES_A = [
    {"heading": "Uebersicht", "type": "container", "grid": [
        {"item": "wlo-collection-chips", "nodeId": _ref(WIDGET_LISTE)}]},
    {"heading": "Neues", "type": "container", "grid": [
        {"item": "wlo-content-teaser", "nodeId": _ref(WIDGET_SUCHE)},
        {"item": "wlo-editorial-members"}]},
]
LANES_B = [{"heading": "Nur eine", "type": "container", "grid": [
    {"item": "wlo-content-teaser", "nodeId": _ref(WIDGET_LISTE)}]}]


class Instanz:
    def __init__(self, *, seiten_ref: str | None = _ref(ORDNER),
                 page_config: str | None = None,
                 treffer: list[dict] | None = None) -> None:
        self.page_config = page_config if page_config is not None else json.dumps(
            {"variants": [_ref(V1), _ref(V2)]})
        self.seiten_ref = seiten_ref
        self.treffer = treffer
        self.gelesen: list[str] = []
        self.varianten = [_variante(V1, "Variante A", LANES_A),
                          _variante(V2, "Variante B", LANES_B)]
        self.widgets = {
            WIDGET_LISTE: _node(WIDGET_LISTE, titel="WIDGET_liste", props={
                "ccm:widget_config": [json.dumps({
                    "description": "Die Struktur des Themas",
                    "sortedNodeIds": ["mat-1", "mat-2"]})]}),
            WIDGET_SUCHE: _node(WIDGET_SUCHE, titel="WIDGET_suche", props={
                "ccm:widget_config": [json.dumps({
                    "description": "Neue Inhalte",
                    "searchText": "Optik",
                    "propertyFilters": {"virtual:editorial_license": ["oer"]}})]}),
        }

    def handler(self, request: httpx.Request) -> httpx.Response:
        pfad, url = request.url.path, str(request.url)
        if "/search/v1/queries/" in url:
            return httpx.Response(200, json={
                "nodes": self.treffer or [],
                "pagination": {"total": len(self.treffer or []), "from": 0}})
        if "/collection/v1/collections/-home-/search" in url:
            return httpx.Response(200, json={"collections": []})
        if pfad.endswith("/children"):
            return httpx.Response(200, json={
                "nodes": self.varianten,
                "pagination": {"total": len(self.varianten), "from": 0}})
        if pfad.endswith("/metadata"):
            nid = pfad.rsplit("/", 2)[-2]
            self.gelesen.append(nid)
            if nid == ORDNER:
                props = ({"ccm:page_config": [self.page_config]}
                         if self.page_config is not None else {})
                return httpx.Response(200, json={
                    "node": _node(ORDNER, titel=f"PAGE_{ORDNER}", props=props)})
            for variante in self.varianten:
                if variante["ref"]["id"] == nid:
                    return httpx.Response(200, json={"node": variante})
            if nid in self.widgets:
                return httpx.Response(200, json={"node": self.widgets[nid]})
            if nid != SAMMLUNG:
                return httpx.Response(404, json={
                    "error": "DAOMissingException", "message": "node does not exist"})
            props = ({"ccm:page_config_ref": [self.seiten_ref]}
                     if self.seiten_ref is not None else {})
            return httpx.Response(200, json={
                "node": _node(SAMMLUNG, titel="Deutsch", props=props)})
        return httpx.Response(404, json={"error": "x", "message": "nicht gemockt"})

    def repo(self) -> AsyncRepository:
        return AsyncRepository(
            REPO, backoff_base=0.0, metadataset="mds_oeh",
            client=httpx.AsyncClient(transport=httpx.MockTransport(self.handler)))


# --- page -----------------------------------------------------------------

async def test_gerenderte_variante_wird_ausgegeben():
    async with Instanz().repo() as repo:
        seite = await repo.flows.page(SAMMLUNG)
    assert seite["collection"]["id"] == SAMMLUNG
    assert seite["collection"]["title"] == "Deutsch"
    assert seite["folder_id"] == ORDNER
    assert seite["rendered"]["id"] == V1
    assert seite["rendered"]["by_position"] is True
    assert [ln["heading"] for ln in seite["swimlanes"]] == ["Uebersicht", "Neues"]
    assert seite["reason"] == ""


async def test_alle_varianten_werden_genannt():
    """Auch die, die gerade nicht rendert -- sonst weiss ein Aufrufer nicht,
    worauf er ueberhaupt umstellen koennte."""
    async with Instanz().repo() as repo:
        seite = await repo.flows.page(SAMMLUNG)
    assert [v["id"] for v in seite["variants"]] == [V1, V2]
    assert seite["variants"][0]["is_template"] is False
    assert seite["variants"][0]["readable"] is True


async def test_bestimmte_variante_waehlen():
    async with Instanz().repo() as repo:
        seite = await repo.flows.page(SAMMLUNG, variant=V2)
    assert seite["rendered"]["id"] == V2
    assert [ln["heading"] for ln in seite["swimlanes"]] == ["Nur eine"]


async def test_unbekannte_variante_wird_benannt():
    async with Instanz().repo() as repo:
        seite = await repo.flows.page(SAMMLUNG, variant="gibtesnicht")
    assert seite["swimlanes"] == []
    assert "gibtesnicht" in seite["reason"]
    assert [v["id"] for v in seite["variants"]] == [V1, V2], (
        "die vorhandenen Varianten gehoeren in die Antwort, sonst raet der Aufrufer")


async def test_sammlung_ohne_seite_ist_kein_fehler():
    """Die meisten Sammlungen haben keine. Eine Ausnahme daraus zu machen
    hiesse, den Normalfall zum Stoerfall zu erklaeren."""
    async with Instanz(seiten_ref=None).repo() as repo:
        seite = await repo.flows.page(SAMMLUNG)
    assert seite["swimlanes"] == []
    assert seite["variants"] == []
    assert seite["folder_id"] == ""
    assert "ccm:page_config_ref" in seite["reason"]


async def test_knoten_ids_sind_flach_und_entdoppelt():
    async with Instanz().repo() as repo:
        seite = await repo.flows.page(SAMMLUNG)
    assert seite["node_ids"] == [WIDGET_LISTE, WIDGET_SUCHE]


async def test_element_ohne_knoten_bleibt_in_der_linie():
    async with Instanz().repo() as repo:
        seite = await repo.flows.page(SAMMLUNG)
    zweite = seite["swimlanes"][1]["items"]
    assert [it["widget"] for it in zweite] == ["wlo-content-teaser", "wlo-editorial-members"]
    assert zweite[1]["node_id"] is None


async def test_ohne_aufloesen_wird_kein_widget_gelesen():
    instanz = Instanz()
    async with instanz.repo() as repo:
        seite = await repo.flows.page(SAMMLUNG)
    assert seite["resolved"] is False
    assert WIDGET_LISTE not in instanz.gelesen
    assert all("node_ids" not in it for ln in seite["swimlanes"] for it in ln["items"])


# --- page(resolve_widgets=True) -------------------------------------------

async def test_feste_liste_wird_aufgeloest():
    async with Instanz().repo() as repo:
        seite = await repo.flows.page(SAMMLUNG, resolve_widgets=True)
    erstes = seite["swimlanes"][0]["items"][0]
    assert erstes["description"] == "Die Struktur des Themas"
    assert erstes["node_ids"] == ["mat-1", "mat-2"]
    assert "search" not in erstes
    assert seite["resolved"] is True


async def test_gespeicherte_suche_wird_genannt_nicht_ausgefuehrt():
    """Die Filter tragen virtual:-Felder, die die MDS nicht kennt. Sie
    auszufuehren hiesse raten; sie zu nennen laesst den Aufrufer entscheiden."""
    async with Instanz().repo() as repo:
        seite = await repo.flows.page(SAMMLUNG, resolve_widgets=True)
    suche = seite["swimlanes"][1]["items"][0]
    assert suche["search"] == {"text": "Optik",
                               "filters": {"virtual:editorial_license": ["oer"]}}
    assert "node_ids" not in suche


async def test_widget_wird_einmal_gelesen():
    """Dasselbe Widget kann in mehreren Linien stehen."""
    instanz = Instanz(page_config=json.dumps({"variants": [_ref(V2), _ref(V1)]}))
    async with instanz.repo() as repo:
        await repo.flows.page(SAMMLUNG, variant=V1, resolve_widgets=True)
    assert instanz.gelesen.count(WIDGET_LISTE) == 1


async def test_deckel_wird_gemeldet():
    instanz = Instanz()
    async with instanz.repo() as repo:
        seite = await repo.flows.page(SAMMLUNG, resolve_widgets=True, max_widgets=1)
    assert seite["truncated"] is True
    assert instanz.gelesen.count(WIDGET_SUCHE) == 0
    assert "node_ids" in seite["swimlanes"][0]["items"][0]
    assert "description" not in seite["swimlanes"][1]["items"][0]


async def test_verschwundenes_widget_bricht_die_seite_nicht():
    """Ein Index, der seine Knoten ueberlebt, ist hier der Normalfall."""
    instanz = Instanz()
    instanz.widgets.pop(WIDGET_SUCHE)
    async with instanz.repo() as repo:
        seite = await repo.flows.page(SAMMLUNG, resolve_widgets=True)
    assert seite["swimlanes"][0]["items"][0]["node_ids"] == ["mat-1", "mat-2"]
    assert "unreachable" in seite["swimlanes"][1]["items"][0]


@pytest.mark.parametrize("wert, erwartet", [
    (None, "keins"),
    ("not json at all", "not valid JSON"),
    ("[1, 2]", "not an object"),
])
async def test_kaputtes_widget_wird_gemeldet_nicht_geworfen(wert, erwartet):
    """Auch das Widget-Dokument validiert niemand."""
    instanz = Instanz()
    if wert is None:
        instanz.widgets[WIDGET_LISTE] = _node(WIDGET_LISTE, titel="ohne Konfig")
    else:
        instanz.widgets[WIDGET_LISTE] = _node(
            WIDGET_LISTE, props={"ccm:widget_config": [wert]})
    async with instanz.repo() as repo:
        seite = await repo.flows.page(SAMMLUNG, resolve_widgets=True)
    erstes = seite["swimlanes"][0]["items"][0]
    if erwartet == "keins":
        assert "unreadable" not in erstes and "node_ids" not in erstes
    else:
        assert erwartet in erstes["unreadable"]


async def test_seite_ohne_varianten_sagt_das():
    instanz = Instanz()
    instanz.varianten = []
    async with instanz.repo() as repo:
        seite = await repo.flows.page(SAMMLUNG)
    assert seite["rendered"] is None
    assert "nothing to render" in seite["reason"]
    assert seite["folder_id"] == ORDNER, (
        "der Ordner existiert -- nur leer; das ist etwas anderes als keine Seite")


@pytest.mark.parametrize("deckel", [0, -3])
async def test_unsinniger_deckel_wird_abgelehnt(deckel):
    async with Instanz().repo() as repo:
        with pytest.raises(ValueError, match="resolve_widgets"):
            await repo.flows.page(SAMMLUNG, max_widgets=deckel)


# --- find_pages -----------------------------------------------------------

async def test_seiten_werden_am_treffer_erkannt():
    treffer = [
        _node("a", titel="Ohne Seite"),
        _node("b", titel="Mit Seite", props={"ccm:page_config_ref": [_ref("f-b")]}),
    ]
    async with Instanz(treffer=treffer).repo() as repo:
        gefunden = await repo.flows.find_pages("Deutsch")
    assert [h["id"] for h in gefunden["hits"]] == ["b"]
    assert gefunden["hits"][0]["folder_id"] == "f-b"
    assert gefunden["hits"][0]["title"] == "Mit Seite"


async def test_beurteilbare_treffer_werden_gezaehlt():
    """Weg B liefert keine Eigenschaften. Ohne diese Zahl liest sich "keine
    Seite gefunden" wie eine Aussage ueber die Instanz, obwohl es eine ueber
    die Projektion war."""
    treffer = [_node("a", titel="Mit Projektion"),
               {"ref": {"id": "b"}, "title": "Ohne Projektion", "properties": {}}]
    async with Instanz(treffer=treffer).repo() as repo:
        gefunden = await repo.flows.find_pages("Deutsch")
    assert gefunden["checked"] == 1
    assert gefunden["hits"] == []
    assert "1" in gefunden["reason"]


async def test_gesamtzahl_ist_als_untergrenze_gekennzeichnet():
    """Die Sammlungssuche fragt zwei Routen und fuehrt sie zusammen; eine von
    ihnen meldet gar keine Gesamtzahl. 876 heisst also "mindestens 876"."""
    treffer = [_node("a", titel="Ohne Seite")]
    async with Instanz(treffer=treffer).repo() as repo:
        gefunden = await repo.flows.find_pages("Deutsch")
    assert gefunden["total_is_lower_bound"] is True


async def test_ohne_treffer_bleibt_die_antwort_still():
    async with Instanz(treffer=[]).repo() as repo:
        gefunden = await repo.flows.find_pages("gibtesnicht")
    assert gefunden["hits"] == []
    assert gefunden["checked"] == 0
    assert gefunden["query"] == "gibtesnicht"


async def test_alle_treffer_beurteilbar_ergibt_keinen_hinweis():
    treffer = [_node("b", titel="Mit Seite",
                     props={"ccm:page_config_ref": [_ref("f-b")]})]
    async with Instanz(treffer=treffer).repo() as repo:
        gefunden = await repo.flows.find_pages("Deutsch")
    assert gefunden["reason"] == ""


@pytest.mark.parametrize("limit", [0, -1])
async def test_unsinniges_limit_wird_abgelehnt(limit):
    async with Instanz().repo() as repo:
        with pytest.raises(ValueError):
            await repo.flows.find_pages("x", limit=limit)
