"""Der synchrone Durchgriff -- vollstaendig.

Diese Datei existiert wegen zweier echter Fehler, die genau hier steckten und
beide erst beim Benutzen auffielen:

* ``Repository`` hatte kein ``raw``. Wer nur den synchronen Zugang benutzte,
  sass fest, sobald etwas gebraucht wurde, das die Bibliothek nicht abdeckt.
* ``SyncNode.content`` gab ein Objekt mit **asynchronen** Methoden zurueck. Der
  Aufruf lieferte eine Coroutine, tat nichts und meldete nichts.

Beide Male war die Ursache dieselbe: eine neue asynchrone Flaeche kam dazu, und
der synchrone Durchgriff wurde vergessen. Kein Test hat das gefangen, weil der
synchrone Weg nur stichprobenhaft geprueft war.

Diese Datei prueft deshalb **jede** synchrone Methode daraufhin, dass sie ein
Ergebnis liefert und keine Coroutine. Der Nachweis ist billig und faengt genau
die Sorte Fehler, die zweimal durchgerutscht ist.
"""

import inspect
import json

import httpx
import pytest

from edusharing import Repository

REPO = "https://repo.test/edu-sharing"
NID = "node-1"

NODE = {"node": {
    "ref": {"id": NID}, "name": "material.txt", "title": "Titel", "type": "ccm:io",
    "access": ["Read", "Write"], "mimetype": "text/plain",
    "downloadUrl": f"{REPO}/eduservlet/download?node={NID}",
    "content": {"hash": "-123"},
    "properties": {"cclom:title": ["Titel"], "cclom:general_keyword": ["Fremd"]},
}}
COLLECTION = {"collection": {"ref": {"id": "coll-1"}, "title": "Sammlung",
                             "collection": {"scope": "MY"}}}
VOCAB = {"values": [{"key": "http://vocab.test/080", "displayString": "Biologie"}]}
SEARCH = {"nodes": [], "pagination": {"total": 0, "from": 0, "count": 0}}
MDS = {"metadatasets": [{"id": "mds", "name": "Contentbuffet"}]}
ABOUT = {"version": {"repository": "11.0", "major": 1, "minor": 1}}
ME = {"person": {"authorityName": "alice", "userName": "alice", "profile": {}}}


# Der Knoten lebt im Modulzustand: die Rueckleseprobe verlangt, dass ein
# Schreibvorgang sichtbar wird -- ein Handler mit fester Antwort wuerde sie zu
# Recht ausloesen.
_PROPS: dict[str, list[str]] = {}


def _node_response() -> dict:
    node = dict(NODE["node"])
    node["properties"] = dict(NODE["node"]["properties"]) | _PROPS
    node["title"] = (node["properties"].get("cclom:title") or [""])[0]
    return {"node": node}


def _handler(request: httpx.Request) -> httpx.Response:
    url, method = str(request.url), request.method
    ist_anlegen = (method == "POST" and request.url.path.endswith("/children")
                   and "/collection" not in request.url.path)
    if ist_anlegen:
        # Wie die Instanz: die Antwort des Anlegens traegt den gespeicherten
        # Stand. Ein Mock mit fester Antwort loest die Rueckleseprobe zu Recht
        # aus.
        _PROPS.update(json.loads(request.content))
        return httpx.Response(200, json=_node_response())
    if method == "PUT" and url.endswith("/metadata"):
        _PROPS.update(json.loads(request.content))
        return httpx.Response(200, json=_node_response())
    if method == "POST" and "/property" in url:
        prop = request.url.params.get("property")
        wert = json.loads(request.content)
        if wert is None:
            _PROPS.pop(prop, None)
        else:
            _PROPS[prop] = wert
        return httpx.Response(200, content=b"")
    if "eduservlet/download" in url:
        return httpx.Response(200, content=b"Dateiinhalt")
    if url.endswith("/textContent") or "/textContent?" in url:
        return httpx.Response(200, json={"text": "Volltext"})
    if "/mds/v1/metadatasets/-home-" in url and "/values" not in url:
        return httpx.Response(200, json=MDS)
    if "/values" in url:
        return httpx.Response(200, json=VOCAB)
    if "/_about" in url:
        return httpx.Response(200, json=ABOUT)
    if "-me-" in url:
        return httpx.Response(200, json=ME)
    if "/collection/v1/collections" in url and method == "POST":
        return httpx.Response(200, json=COLLECTION)
    if "/references/" in url:
        return httpx.Response(200, content=b"")
    if "/collection/v1/collections" in url:
        return httpx.Response(200, json={"collections": [], "pagination": None})
    if "/ngsearch" in url or "/collections" in url:
        return httpx.Response(200, json=SEARCH)
    if method == "DELETE":
        return httpx.Response(200, content=b"")
    return httpx.Response(200, json=_node_response())


@pytest.fixture
def repo():
    _PROPS.clear()
    r = Repository(
        REPO, client=httpx.AsyncClient(transport=httpx.MockTransport(_handler)))
    try:
        yield r
    finally:
        r.close()


def _kein_coroutine(wert):
    """Der Kern dieser Datei: ein vergessener Durchgriff liefert genau das."""
    assert not inspect.iscoroutine(wert), (
        f"{wert!r} ist eine Coroutine -- der synchrone Durchgriff fehlt"
    )
    return wert


# --- Knoten ---------------------------------------------------------------

def test_node_und_update(repo):
    node = _kein_coroutine(repo.node(NID))
    assert node.id == NID
    _kein_coroutine(node.update(title="Neu"))


def test_set_property(repo):
    node = repo.node(NID)
    _kein_coroutine(node.set_property("ccm:foo", "x", verify=False))


def test_schlagworte_synchron(repo):
    """War ungetestet -- add_keywords/remove_keywords geben SyncNode zurueck."""
    node = repo.node(NID)
    ergaenzt = _kein_coroutine(node.add_keywords("Neu"))
    assert not inspect.iscoroutine(ergaenzt)
    _kein_coroutine(ergaenzt.remove_keywords("Neu"))


def test_delete_synchron(repo):
    _kein_coroutine(repo.node(NID).delete())


def test_create_node_synchron(repo):
    node = _kein_coroutine(repo.create_node("parent", name="neu.txt"))
    assert node.id == NID


def test_node_repr_ohne_absturz(repo):
    assert NID in repr(repo.node(NID))


# --- Dateien --------------------------------------------------------------

def test_content_gibt_synchrones_objekt(repo):
    """Der zweite gefundene Fehler: content gab asynchrone Methoden zurueck."""
    content = repo.node(NID).content
    assert not inspect.iscoroutinefunction(content.download)
    assert not inspect.iscoroutinefunction(content.upload)
    assert not inspect.iscoroutinefunction(content.text)


def test_download_synchron(repo):
    assert _kein_coroutine(repo.node(NID).content.download()) == b"Dateiinhalt"


def test_upload_synchron(repo):
    node = _kein_coroutine(
        repo.node(NID).content.upload(b"x", filename="x.txt", mimetype="text/plain"))
    assert node.id == NID


def test_textinhalt_synchron(repo):
    assert _kein_coroutine(repo.node(NID).content.text()) == "Volltext"


def test_content_reicht_lesende_eigenschaften_durch(repo):
    content = repo.node(NID).content
    assert content.mimetype == "text/plain"
    assert content.has_content is True
    assert "node-1" in repr(content)


# --- Sammlungen -----------------------------------------------------------

def test_create_collection_synchron(repo):
    coll = _kein_coroutine(repo.create_collection("Meine Sammlung"))
    assert coll.id == "coll-1"


def test_add_und_remove_synchron(repo):
    assert _kein_coroutine(repo.add_to_collection("coll-1", NID)) is True
    _kein_coroutine(repo.remove_from_collection("coll-1", NID))


def test_find_collections_synchron(repo):
    assert _kein_coroutine(repo.find_collections("Optik")) is not None


# --- Vokabular und Auskuenfte --------------------------------------------

def test_resolve_synchron(repo):
    """War ungetestet -- der einzige synchrone Weg ins Vokabular."""
    assert _kein_coroutine(repo.resolve("ccm:taxonid", "Biologie")) == \
        "http://vocab.test/080"


def test_search_synchron(repo):
    assert _kein_coroutine(repo.search("x")) is not None


def test_about_whoami_metadatasets_synchron(repo):
    assert _kein_coroutine(repo.about()).repository_version == "11.0"
    assert _kein_coroutine(repo.whoami()).authority == "alice"
    assert len(_kein_coroutine(repo.metadatasets())) == 1


def test_raw_synchron(repo):
    """Der erste gefundene Fehler: raw fehlte am synchronen Zugang ganz."""
    assert _kein_coroutine(repo.raw.json("GET", "/_about")) is not None
    assert _kein_coroutine(repo.raw.request("GET", "/_about")).status_code == 200


# --- Durchgereichte Schichten ---------------------------------------------

def test_schichten_sind_erreichbar(repo):
    """searcher, collections, nodes und vocab geben die asynchronen Objekte --
    absichtlich, fuer Zugriff auf ihre Einstellungen."""
    assert repo.searcher.metadataset == repo.metadataset
    assert repo.collections.metadataset == repo.metadataset
    assert repo.nodes.repository_url == repo.url
    assert repo.vocab.metadataset == repo.metadataset


def test_repr_und_url(repo):
    assert repo.url in repr(repo)


def test_mehrfaches_schliessen_ist_erlaubt(repo):
    """close() steht typischerweise in einem finally und wird zusaetzlich vom
    Kontextmanager gerufen."""
    repo.close()
    repo.close()


def test_json_durchgriff_sendet_korrekt(repo):
    """Gegenprobe, dass der Durchgriff nicht nur nicht abstuerzt, sondern die
    Anfrage wirklich absetzt."""
    antwort = repo.raw.request(
        "PUT", f"/node/v1/nodes/-home-/{NID}/metadata", json={"cclom:title": ["X"]})
    assert antwort.status_code == 200
    assert json.loads(antwort.request.content) == {"cclom:title": ["X"]}


# --- Ablaeufe -------------------------------------------------------------

def test_flows_sind_synchron_erreichbar(repo):
    """Dieselbe Falle wie bei SyncNode.content: eine neue asynchrone Flaeche
    kommt dazu, der synchrone Durchgriff wird vergessen, und der Aufruf liefert
    stumm eine Coroutine."""
    ergebnis = _kein_coroutine(repo.flows.search("Physik"))
    assert isinstance(ergebnis, dict)
    assert "hits" in ergebnis


def test_flows_vokabular_und_describe_synchron(repo):
    assert _kein_coroutine(repo.flows.vocabulary("subject"))["property"] == "ccm:taxonid"
    assert _kein_coroutine(repo.flows.describe(NID))["id"] == NID


def test_schreibende_flows_synchron(repo):
    """Auch die schreibenden Ablaeufe muessen durchgreifen -- eine Coroutine,
    die niemand erwartet, legt hier gar nichts an und meldet auch nichts."""
    angelegt = _kein_coroutine(repo.flows.add_material("Titel", parent_id="parent"))
    assert angelegt["id"] == NID

    sammlung = _kein_coroutine(repo.flows.build_collection("Sammlung", node_ids=[NID]))
    assert sammlung["id"] == "coll-1"

    geloescht = _kein_coroutine(repo.flows.delete(NID))
    assert geloescht["recycled"] is True


def test_neue_flows_synchron(repo):
    """Dieselbe Falle, viertes Mal: neue asynchrone Flaeche, Durchgriff
    vergessen, Aufruf liefert stumm eine Coroutine."""
    assert _kein_coroutine(repo.flows.find_collections("Optik"))["hits"] is not None
    assert _kein_coroutine(repo.flows.collection_contents("coll-1"))["id"] == "coll-1"
    assert _kein_coroutine(repo.flows.update_material(NID, title="Neu"))["id"] == NID


def test_serienobjekte_synchron(repo):
    """Fuenftes Mal dieselbe Falle: neue asynchrone Flaeche am Node, Durchgriff
    vergessen, Aufruf liefert stumm eine Coroutine."""
    kinder = repo.node(NID).children
    assert not inspect.iscoroutinefunction(kinder.list)
    assert _kein_coroutine(kinder.list()) == []
    assert _kein_coroutine(repo.flows.child_objects(NID))["count"] == 0
