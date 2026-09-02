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
from edusharing._sync import LoopThread
from edusharing.errors import ConflictError, ValidationError

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

# Dasselbe fuer die Rechte: publish() liest zurueck und wuerde bei einer festen
# Antwort zu Recht einen stillen Verlust melden.
_ACL: list[dict] = []

# Und fuer die Kommentare, deren Anlegen ebenfalls zurueckliest.
_COMMENTS: list[dict] = []

# Der Workflow-Verlauf, aus demselben Grund.
_WORKFLOW: list[dict] = []

# Und die Vorschlaege, deren Entscheiden ebenfalls zurueckliest.
_SUGGESTIONS: list[dict] = []


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
    # Eng gefasst: /iam/v1/people/-home-/-me- ist die whoami-Route und gehoert
    # nicht hierher.
    if "/iam/v1/groups" in url or url.endswith("/memberships"):
        if url.endswith("/memberships"):
            return httpx.Response(200, json={"groups": []})
        if "/members" in url and method == "GET":
            return httpx.Response(200, json={"authorities": [],
                                             "pagination": {"total": 0}})
        if method in ("PUT", "DELETE"):
            return httpx.Response(200, content=b"")
        return httpx.Response(200, json={"group": {
            "authorityName": "GROUP_x", "authorityType": "GROUP",
            "groupName": "x", "profile": {"displayName": "X"}}})
    if url.endswith("/preview") or "/preview?" in url:
        return httpx.Response(200, json=_node_response())
    if url.endswith("/children/collections"):
        return httpx.Response(200, json={"collections": []})
    if url.endswith("/children") and method == "GET":
        return httpx.Response(200, json={
            "nodes": [_node_response()["node"]],
            "pagination": {"total": 1, "from": 0, "count": 1}})
    # Eng gefasst: das Einlegen einer Referenz ist auch ein PUT unter
    # /collection/v1/collections und hat einen leeren Body.
    if ("/collection/v1/collections" in url and method == "PUT"
            and "/references/" not in url):
        # Die Instanz setzt title, cm:title und cm:name. Hier genuegt, was
        # Node.title liest -- diese Datei prueft den Durchgriff, die Treue zum
        # Endpunkt steht in test_paging_preview.py.
        neuer = json.loads(request.content)["title"]
        _PROPS["cclom:title"] = [neuer]
        _PROPS["cm:title"] = [neuer]
        return httpx.Response(200, content=b"")
    if "/relation/v1" in url:
        if method == "GET":
            return httpx.Response(200, json={"relations": [{
                "type": "isPartOf",
                "fromNode": {"ref": {"id": NID}, "title": "Teil"},
                "toNode": {"ref": {"id": "reihe-1"}, "title": "Die Reihe"},
                "isAiGenerated": True,
                "evaluation": {"isApproved": False},
            }]})
        return httpx.Response(200, content=b"")
    if "/suggestions/v1" in url:
        if method == "GET":
            return httpx.Response(200, json={
                "nodeId": NID,
                "suggestions": {"ccm:taxonid": _SUGGESTIONS} if _SUGGESTIONS else {}})
        if method == "POST":
            _SUGGESTIONS.append({
                "id": "s-1", "propertyId": "ccm:taxonid", "value": "Biologie",
                "status": "PENDING", "description": "Weil",
                "createdBy": {"authorityName": "alice"}})
            return httpx.Response(200, json=[_SUGGESTIONS[-1]])
        # PATCH: die IDs stehen im Query, nicht im Body.
        for sid in request.url.params.get_list("id"):
            for v in _SUGGESTIONS:
                if v["id"] == sid:
                    v["status"] = request.url.params.get("status")
        return httpx.Response(200, json=[])
    if url.endswith("/workflow") or "/workflow?" in url:
        if method == "GET":
            return httpx.Response(200, json=_WORKFLOW)
        _WORKFLOW.append({
            "time": 1787913246139, "status": json.loads(request.content)["status"],
            "comment": "", "editor": {"authorityName": "alice"},
            "receiver": [{"authorityName": r["authorityName"]}
                         for r in json.loads(request.content)["receiver"]]})
        return httpx.Response(200, content=b"")
    if "/comment/v1" in url:
        if method == "GET":
            return httpx.Response(200, json={"comments": _COMMENTS})
        if method == "PUT":
            _COMMENTS.append({
                "ref": {"id": f"c-{len(_COMMENTS) + 1}"},
                "comment": request.content.decode("utf-8"),
                "created": 1787912255934,
                "creator": {"authorityName": "alice"}, "replyTo": None})
        elif method == "POST":
            cid = request.url.path.rsplit("/", 1)[-1]
            for c in _COMMENTS:
                if c["ref"]["id"] == cid:
                    c["comment"] = request.content.decode("utf-8")
        elif method == "DELETE":
            cid = request.url.path.rsplit("/", 1)[-1]
            _COMMENTS[:] = [c for c in _COMMENTS if c["ref"]["id"] != cid]
        return httpx.Response(200, content=b"")
    if "/rating/v1" in url:
        return httpx.Response(200, content=b"")
    if url.endswith("/parents") or "/parents?" in url:
        return httpx.Response(200, json={
            "nodes": [_node_response()["node"],
                      {"ref": {"id": "oben"}, "name": "ordner", "type": "ccm:map",
                       "properties": {"cclom:title": ["Ordner"]}}],
            "scope": "MY_FILES"})
    if "/usage/v1" in url:
        return httpx.Response(200, json=[{"collection": {
            "ref": {"id": "s-1"}, "name": "Sammlung", "type": "ccm:map",
            "properties": {"cclom:title": ["Sammlung"]}}}])
    if url.endswith("/permissions") or "/permissions?" in url:
        if method == "GET":
            return httpx.Response(200, json={"permissions": {
                "localPermissions": {"inherited": True, "permissions": _ACL},
                "inheritedPermissions": []}})
        _ACL[:] = json.loads(request.content)["permissions"]
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
    _ACL.clear()
    _COMMENTS.clear()
    _WORKFLOW.clear()
    _SUGGESTIONS.clear()
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


def test_die_synchrone_fassade_spiegelt_die_vorgaben():
    """Review C6: Flows.find_collections(text="") hatte blockierend keine
    Vorgabe. Jede Methode der Fassade braucht ein Spiegelbild; wo es dieselben
    Parameter nennt, muessen die Vorgaben gleich sein, und was es nicht nennt,
    muss ueber **kwargs erreichbar bleiben."""
    from edusharing._sync import SyncFlows
    from edusharing.flows import Flows

    fehler = []
    for name, fn in inspect.getmembers(Flows, inspect.isfunction):
        if name.startswith("_"):
            continue
        spiegel = getattr(SyncFlows, name, None)
        if spiegel is None:
            fehler.append(f"{name}: fehlt in SyncFlows")
            continue
        a = {n: p for n, p in inspect.signature(fn).parameters.items() if n != "self"}
        b = {n: p for n, p in inspect.signature(spiegel).parameters.items() if n != "self"}
        offen = any(p.kind is inspect.Parameter.VAR_KEYWORD for p in b.values())
        for n, p in a.items():
            if p.kind is inspect.Parameter.VAR_KEYWORD:
                continue
            if n in b and b[n].default != p.default:
                fehler.append(f"{name}({n}): Vorgabe {b[n].default!r} statt {p.default!r}")
            elif n not in b and not offen:
                fehler.append(f"{name}({n}): fehlt im Spiegel")
    assert not fehler, "\n".join(fehler)


def test_skills_synchron(repo):
    """SyncSkills stand in keinem Test -- genau die Klasse, fuer die diese
    Datei da ist."""
    from edusharing._sync import SyncSkills

    assert isinstance(repo.skills, SyncSkills)
    for name in ("search", "get", "registry", "pick"):
        assert not inspect.iscoroutinefunction(getattr(repo.skills, name)), name
    registry = _kein_coroutine(repo.skills.registry("coll-1"))
    assert registry.reason == "no_registry"


# --- Vokabular und Auskuenfte --------------------------------------------

def test_resolve_synchron(repo):
    """War ungetestet -- der einzige synchrone Weg ins Vokabular."""
    assert _kein_coroutine(repo.resolve("ccm:taxonid", "Biologie")) == \
        "http://vocab.test/080"


def test_resolve_all_synchron(repo):
    """Ein Label kann zu zwei Vokabularen gehoeren.

    ``resolve`` liefert davon nur das erste. Blockierend gab es keinen Weg zur
    ganzen Menge -- die Suche loeste sie intern auf, aber wer sie sehen wollte,
    brauchte ``AsyncRepository``.
    """
    assert _kein_coroutine(repo.resolve_all("ccm:taxonid", "Biologie")) == \
        ["http://vocab.test/080"]


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


def test_der_schleifenfaden_darf_doppelt_geschlossen_werden():
    """``Repository.close()`` faengt den zweiten Aufruf selbst ab und erreicht
    die Sicherung im Faden nie -- die Zusage im Docstring von
    ``LoopThread.close`` war damit unbelegt. Ohne sie wirft der zweite Aufruf,
    weil die Schleife schon zu ist.
    """
    faden = LoopThread()
    faden.close()
    faden.close()          # genau das, was ohne die Sicherung wirft


def test_repr_der_durchgereichten_schichten(repo):
    """Ein ``__repr__`` ist die einzige Methode, die beim Debuggen aufgerufen
    wird, wenn sowieso etwas schiefsteht. Fuer Knoten und Repository wird das
    hier schon geprueft; Transport und Ablaeufe fehlten."""
    assert REPO in repr(repo.raw)
    assert "Flows" in repr(repo.flows)


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


def test_seiten_ablaeufe_synchron(repo):
    """Sechstes Mal dieselbe Falle."""
    seite = _kein_coroutine(repo.flows.page(NID))
    assert seite["collection"]["id"] == NID
    assert seite["swimlanes"] == [], "der gemockte Knoten traegt keine Seite"
    assert _kein_coroutine(repo.flows.find_pages("Optik"))["hits"] == []


def test_serienobjekte_synchron(repo):
    """Fuenftes Mal dieselbe Falle: neue asynchrone Flaeche am Node, Durchgriff
    vergessen, Aufruf liefert stumm eine Coroutine."""
    kinder = repo.node(NID).children
    assert "ChildObjects" in repr(kinder)
    assert not inspect.iscoroutinefunction(kinder.list)
    assert _kein_coroutine(kinder.list()) == []
    assert _kein_coroutine(repo.flows.child_objects(NID))["count"] == 0

    # add() macht zwei Anfragen und gibt einen Knoten zurueck -- ohne
    # Durchgriff bekaeme der Aufrufer eine Coroutine statt des Kindes, und der
    # Anhang entstuende nie.
    kind = _kein_coroutine(
        kinder.add(b"Anhang", filename="anhang.txt", mimetype="text/plain"))
    assert kind.id == NID, "der Mock gibt denselben Knoten zurueck"
    # Der zurueckgegebene Knoten muss selbst synchron sein, sonst verschiebt
    # sich die Falle nur eine Ebene tiefer.
    assert not inspect.iscoroutinefunction(kind.delete)


def test_beziehungen_synchron(repo):
    """``repo.relations`` war die einzige durchgereichte Schicht ohne Test --
    gemessen, nicht vermutet: vor diesem Test war ``SyncRelations`` in der
    Abdeckung von ``_sync.py`` zu 100 % unbelegt, jede der vier Methoden.
    """
    beziehungen = repo.relations
    assert "Relations" in repr(beziehungen)

    gefunden = _kein_coroutine(beziehungen.of(NID))
    assert [(b.type, b.to_id) for b in gefunden] == [("isPartOf", "reihe-1")]
    # Die zwei Flaggen, die aus einem Vorschlag noch keine Tatsache machen.
    assert gefunden[0].ai_generated and not gefunden[0].approved

    # create/delete/approve geben None -- ein vergessener Durchgriff gaebe
    # stattdessen eine Coroutine zurueck, und die Beziehung entstuende nie.
    for aufruf in (
        lambda: beziehungen.create(NID, "isPartOf", "reihe-1", ai_generated=True),
        lambda: beziehungen.approve(NID, "isPartOf", "reihe-1"),
        lambda: beziehungen.delete(NID, "isPartOf", "reihe-1"),
    ):
        assert _kein_coroutine(aufruf()) is None

    # Und der Ablauf darueber, der dieselbe Antwort auf die Sicht des
    # gefragten Knotens umrechnet.
    ablauf = _kein_coroutine(repo.flows.relations(NID))
    assert ablauf["count"] == 1
    assert ablauf["relations"][0]["id"] == "reihe-1"


def test_beziehungen_pruefen_vor_dem_senden(repo):
    """Die Pruefung sitzt in ``Relations``; der Durchgriff darf sie nicht
    verschlucken -- sonst schlaegt erst die Instanz mit einem nackten 400 zu."""
    with pytest.raises(ValidationError):
        repo.relations.create(NID, "hasPart", "reihe-1")   # nur lesbarer Typ
    with pytest.raises(ValidationError):
        repo.relations.create(NID, "isPartOf", NID)        # auf sich selbst


def test_seite_gibt_ein_synchrones_objekt(repo):
    """Ohne Durchgriff waere ``node.page.render(...)`` eine nicht abgewartete
    Coroutine -- und die aendert, was jeder Besucher einer oeffentlichen Seite
    sieht: naemlich nichts, still."""
    node = repo.node(NID)
    assert not inspect.iscoroutinefunction(node.page.get)
    assert not inspect.iscoroutinefunction(node.page.render)
    assert NID in repr(node.page)
    # Der gemockte Knoten traegt kein ccm:page_config_ref -- der Normalfall.
    assert _kein_coroutine(node.page.get()) is None
    with pytest.raises(ConflictError):
        node.page.render("egal")


def test_rechte_geben_ein_synchrones_objekt(repo):
    """Derselbe Fall wie seinerzeit bei ``content``: eine neue asynchrone
    Flaeche, und der Durchgriff fehlt. Dann liefert der Aufruf eine Coroutine,
    tut nichts und meldet nichts -- bei Rechten hiesse das, einen Knoten fuer
    veroeffentlicht zu halten, der es nicht ist."""
    node = repo.node(NID)
    rechte = _kein_coroutine(node.permissions.get())
    assert rechte.inherits is True
    assert not rechte.is_public


def test_veroeffentlichen_synchron(repo):
    node = repo.node(NID)
    assert _kein_coroutine(node.permissions.publish()) is True
    assert _kein_coroutine(node.permissions.get()).is_public
    assert _kein_coroutine(node.permissions.unpublish()) is True
    assert not _kein_coroutine(node.permissions.get()).is_public


def test_rechte_geben_und_nehmen_synchron(repo):
    node = repo.node(NID)
    assert _kein_coroutine(node.permissions.grant("alice", "Coordinator")) is True
    assert _kein_coroutine(node.permissions.revoke("alice")) is True
    assert "node-1" in repr(node.permissions)


def test_herkunft_synchron(repo):
    """Zwei neue asynchrone Methoden am Knoten -- ohne Durchgriff liefern sie
    eine Coroutine und der Aufrufer sieht eine leere Auskunft, die keine ist."""
    node = repo.node(NID)
    eltern = _kein_coroutine(node.parents())
    assert [n.id for n in eltern] == ["oben"]
    sammlungen = _kein_coroutine(node.collections())
    assert [s.id for s in sammlungen] == ["s-1"]


def test_placement_synchron(repo):
    ergebnis = _kein_coroutine(repo.flows.placement(NID))
    assert ergebnis["path"] == [{"id": "oben", "title": "Ordner", "type": "ccm:map"}]
    assert ergebnis["scope"] == "MY_FILES"


def test_search_all_synchron(repo):
    ergebnis = _kein_coroutine(repo.flows.search_all("Zelle"))
    assert "materials" in ergebnis and "collections" in ergebnis
    assert ergebnis["collections"]["filters_ignored"] == []


def test_bewertung_synchron(repo):
    """rating ist eine reine Eigenschaft und geht durch __getattr__; rate und
    unrate sind asynchron und brauchen den Durchgriff."""
    node = repo.node(NID)
    assert node.rating is None
    _kein_coroutine(node.rate(4, "gut"))
    _kein_coroutine(node.unrate())


def test_kommentare_synchron(repo):
    node = repo.node(NID)
    assert _kein_coroutine(node.comments.list()) == []
    neu = _kein_coroutine(node.comments.add("Erster"))
    _kein_coroutine(node.comments.edit(neu.id, "Zweiter"))
    _kein_coroutine(node.comments.delete(neu.id))
    assert NID in repr(node.comments)


def test_people_synchron(repo):
    """Der ganze people-Zugang ist neu und asynchron -- ohne Durchgriff liefert
    jede Methode eine Coroutine."""
    leute = repo.people
    assert _kein_coroutine(leute.memberships()) == []
    assert "Sync" in repr(leute)
    _kein_coroutine(leute.group("GROUP_x"))
    _kein_coroutine(leute.members("GROUP_x"))
    _kein_coroutine(leute.create_group("GROUP_neu"))
    _kein_coroutine(leute.add_member("GROUP_x", "alice"))
    _kein_coroutine(leute.remove_member("GROUP_x", "alice"))
    _kein_coroutine(leute.delete_group("GROUP_neu"))


def test_vorschlaege_synchron(repo):
    node = repo.node(NID)
    assert _kein_coroutine(node.suggestions.list()) == []
    neu = _kein_coroutine(node.suggestions.propose("ccm:taxonid", "Biologie", "Weil"))
    _kein_coroutine(node.suggestions.decide([neu.id]))
    assert NID in repr(node.suggestions)


def test_workflow_synchron(repo):
    node = repo.node(NID)
    assert _kein_coroutine(node.workflow.history()) == []
    schritt = _kein_coroutine(node.workflow.submit("bob", "100_tocheck"))
    assert schritt.status == "100_tocheck"
    assert NID in repr(node.workflow)


def test_vorschaubild_synchron(repo):
    node = repo.node(NID)
    assert node.preview_url is None
    _kein_coroutine(node.content.set_preview(b"\x89PNG"))
    _kein_coroutine(node.content.delete_preview())


def test_blaettern_synchron(repo):
    seite = _kein_coroutine(repo.children(NID, limit=2))
    assert seite.total >= 0
    for n in seite.nodes:
        assert not inspect.iscoroutinefunction(n.update)


def test_sammlung_aendern_synchron(repo):
    assert _kein_coroutine(repo.update_collection("coll-1", title="Neu"))


def test_die_fuenf_neuen_ablaeufe_synchron(repo):
    """Fuenf neue asynchrone Flaechen auf einmal -- ohne Durchgriff liefert
    jede eine Coroutine, die nichts tut und nichts meldet."""
    assert _kein_coroutine(repo.flows.describe_many([NID]))["found"] == 1
    _kein_coroutine(repo.flows.related(NID))
    _kein_coroutine(repo.flows.browse_tree("coll-1", depth=1))
    _kein_coroutine(repo.flows.search_in_collection("coll-1", "x", depth=1))
    _kein_coroutine(repo.flows.collection_stats("coll-1"))
