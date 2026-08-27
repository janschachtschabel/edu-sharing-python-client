"""Serienobjekte -- weitere Dokumente an einem Hauptdokument.

Ein Material kann zusaetzliche Dateien tragen: das Arbeitsblatt und sein
Loesungsblatt, ein Hauptdokument und seine Anhaenge. edu-sharing fuehrt die als
**Kindobjekte** unter dem Hauptknoten, und die Kombination, die das erzeugt, ist
nicht zu erraten.

Gemessen gegen Staging am 27.08.2026, nachdem der erste Versuch scheiterte:

    type=ccm:io_childobject              -> HTTP 500, der Typ existiert nicht
    type=ccm:io (ohne assocType)         -> HTTP 500, Integritaetsverletzung
    type=ccm:io + assocType=ccm:childio
        + aspects=ccm:io_childobject     -> angelegt

``ccm:io_childobject`` ist ein **Aspekt**, kein Typ -- daran scheiterte der
erste Anlauf. Der Weg stammt aus der Ideendatenbank, die ihn produktiv nutzt.
"""

import json

import httpx
import pytest

from edusharing import AsyncRepository
from edusharing.errors import EduSharingError, ValidationError

REPO = "https://repo.test/edu-sharing"
HAUPT = "haupt-1"

CHILD_ASPECT = "ccm:io_childobject"


def _kind(node_id: str, name: str, order: str | None, *, serie: bool = True) -> dict:
    props = {"cm:name": [name]}
    if order is not None:
        props["ccm:childobject_order"] = [order]
    return {
        "ref": {"id": node_id}, "name": name, "title": name, "type": "ccm:io",
        "aspects": [CHILD_ASPECT] if serie else ["cm:versionable"],
        "createdAt": f"2026-08-27T10:0{order or 9}:00Z",
        "content": {"hash": "-1"}, "properties": props,
    }


class Instanz:
    """Merkt sich, was angelegt wurde, und antwortet danach."""

    def __init__(self, kinder=None, upload_fehler: bool = False) -> None:
        self.anfragen: list[httpx.Request] = []
        self.kinder = list(kinder or [])
        self.upload_fehler = upload_fehler
        self.geloescht: list[str] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.anfragen.append(request)
        pfad, methode = request.url.path, request.method

        if methode == "POST" and pfad.rstrip("/").endswith("/children"):
            koerper = json.loads(request.content)
            name = (koerper.get("cm:name") or ["?"])[0]
            order = (koerper.get("ccm:childobject_order") or [None])[0]
            neu = _kind(f"kind-{len(self.kinder)}", name, order)
            self.kinder.append(neu)
            return httpx.Response(200, json={"node": neu})
        if methode == "POST" and "/content" in pfad:
            if self.upload_fehler:
                return httpx.Response(403, json={"error": "kein Zugriff"})
            return httpx.Response(200, json={"node": self.kinder[-1]})
        if methode == "GET" and pfad.endswith("/children"):
            return httpx.Response(200, json={
                "nodes": self.kinder,
                "pagination": {"total": len(self.kinder), "from": 0,
                               "count": len(self.kinder)}})
        if methode == "DELETE":
            self.geloescht.append(pfad.rstrip("/").split("/")[-1])
            return httpx.Response(200, content=b"")
        knoten_id = pfad.split("/-home-/")[1].split("/")[0] if "/-home-/" in pfad else HAUPT
        passend = next((k for k in self.kinder
                        if (k.get("ref") or {}).get("id") == knoten_id), None)
        return httpx.Response(200, json={"node": passend or _kind(HAUPT, "haupt.txt",
                                                                  None, serie=False)})


def _repo(instanz) -> AsyncRepository:
    return AsyncRepository(
        REPO, backoff_base=0.0,
        client=httpx.AsyncClient(transport=httpx.MockTransport(instanz)))


# --- Lesen ----------------------------------------------------------------

async def test_nur_serienobjekte_werden_gelistet():
    """Unter einem Hauptknoten haengen auch andere Kinder -- Versionen etwa.
    Ohne die Filterung auf den Aspekt kaemen die als Anhaenge zurueck."""
    instanz = Instanz(kinder=[
        _kind("a", "anhang.txt", "0"),
        _kind("version", "alte-fassung.txt", None, serie=False),
    ])
    async with _repo(instanz) as repo:
        node = await repo.node(HAUPT)
        kinder = await node.children.list()
    assert [k.name for k in kinder] == ["anhang.txt"]


async def test_reihenfolge_folgt_dem_ordnungsfeld():
    instanz = Instanz(kinder=[
        _kind("c", "drittens.txt", "2"),
        _kind("a", "erstens.txt", "0"),
        _kind("b", "zweitens.txt", "1"),
    ])
    async with _repo(instanz) as repo:
        kinder = await (await repo.node(HAUPT)).children.list()
    assert [k.name for k in kinder] == ["erstens.txt", "zweitens.txt", "drittens.txt"]


async def test_ohne_ordnungsfeld_ans_ende_und_dann_nach_alter():
    """Ein Kind ohne Ordnungsangabe darf nicht zufaellig vorn landen."""
    instanz = Instanz(kinder=[
        _kind("ohne", "ohne-order.txt", None),
        _kind("mit", "mit-order.txt", "0"),
    ])
    async with _repo(instanz) as repo:
        kinder = await (await repo.node(HAUPT)).children.list()
    assert [k.name for k in kinder] == ["mit-order.txt", "ohne-order.txt"]


async def test_keine_kinder_ist_kein_fehler():
    async with _repo(Instanz()) as repo:
        assert await (await repo.node(HAUPT)).children.list() == []


# --- Anlegen --------------------------------------------------------------

async def test_anlegen_setzt_aspekt_und_assoziation():
    """Die Kombination ist der ganze Punkt: ccm:io_childobject ist ein ASPEKT,
    kein Typ. Als Typ gesetzt antwortet die Instanz mit HTTP 500."""
    instanz = Instanz()
    async with _repo(instanz) as repo:
        node = await repo.node(HAUPT)
        await node.children.add(b"Inhalt", filename="anhang.txt",
                                mimetype="text/plain")

    angelegt = next(r for r in instanz.anfragen
                    if r.method == "POST" and r.url.path.rstrip("/").endswith("/children"))
    assert angelegt.url.params.get("type") == "ccm:io"
    assert angelegt.url.params.get("assocType") == "ccm:childio"
    assert angelegt.url.params.get("aspects") == CHILD_ASPECT


async def test_anlegen_haengt_hinten_an():
    """Ohne eigene Angabe bekommt das neue Kind die naechste freie Nummer --
    sonst konkurrieren zwei Anhaenge um dieselbe Position."""
    instanz = Instanz(kinder=[_kind("a", "erstens.txt", "0"),
                              _kind("b", "zweitens.txt", "1")])
    async with _repo(instanz) as repo:
        node = await repo.node(HAUPT)
        await node.children.add(b"x", filename="drittens.txt", mimetype="text/plain")

    angelegt = next(r for r in instanz.anfragen
                    if r.method == "POST" and r.url.path.rstrip("/").endswith("/children"))
    assert json.loads(angelegt.content)["ccm:childobject_order"] == ["2"]


async def test_eigene_reihenfolge_wird_uebernommen():
    instanz = Instanz()
    async with _repo(instanz) as repo:
        node = await repo.node(HAUPT)
        await node.children.add(b"x", filename="a.txt", mimetype="text/plain", order=7)
    angelegt = next(r for r in instanz.anfragen
                    if r.method == "POST" and r.url.path.rstrip("/").endswith("/children"))
    assert json.loads(angelegt.content)["ccm:childobject_order"] == ["7"]


async def test_die_datei_wird_hochgeladen():
    instanz = Instanz()
    async with _repo(instanz) as repo:
        node = await repo.node(HAUPT)
        kind = await node.children.add(b"Der Inhalt", filename="a.txt",
                                       mimetype="text/plain")
    assert kind.id
    assert any("/content" in r.url.path for r in instanz.anfragen), \
        "ohne Datei ist das Kind ein leerer Rumpf"


async def test_scheiternder_upload_hinterlaesst_keinen_rumpf():
    """Aus der Ideendatenbank uebernommen: ein Kindknoten ohne Inhalt ist
    Datenmuell. Anlegen und Hochladen sind zwei Aufrufe, und der zweite kann
    fuer sich scheitern."""
    instanz = Instanz(upload_fehler=True)
    async with _repo(instanz) as repo:
        node = await repo.node(HAUPT)
        with pytest.raises(EduSharingError):
            await node.children.add(b"x", filename="a.txt", mimetype="text/plain")
    assert instanz.geloescht, "der Rumpf blieb stehen"


async def test_ein_fehlschlagendes_aufraeumen_verdeckt_nicht_den_grund():
    """Wenn schon der Upload scheitert und danach auch das Aufraeumen, ist die
    Upload-Meldung die, die der Aufrufer braucht. Der Rumpf bleibt dann stehen
    -- unschoen, aber besser als eine Fehlermeldung ueber das Aufraeumen."""
    class OhneLoeschen(Instanz):
        def __call__(self, request):
            if request.method == "DELETE":
                self.anfragen.append(request)
                return httpx.Response(403, json={"error": "auch das nicht"})
            return super().__call__(request)

    instanz = OhneLoeschen(upload_fehler=True)
    async with _repo(instanz) as repo:
        node = await repo.node(HAUPT)
        with pytest.raises(EduSharingError) as fehler:
            await node.children.add(b"x", filename="a.txt", mimetype="text/plain")
    assert "403" in str(fehler.value)
    assert any(r.method == "DELETE" for r in instanz.anfragen), (
        "das Aufraeumen wurde gar nicht erst versucht")


async def test_ein_kind_ohne_id_ist_ein_fehler():
    """Ohne ID laesst sich nichts hochladen und nichts wieder aufraeumen."""
    class OhneId(Instanz):
        def __call__(self, request):
            pfad = request.url.path.rstrip("/")
            if request.method == "POST" and pfad.endswith("/children"):
                self.anfragen.append(request)
                return httpx.Response(200, json={"node": {"ref": {}}})
            return super().__call__(request)

    instanz = OhneId()
    async with _repo(instanz) as repo:
        node = await repo.node(HAUPT)
        with pytest.raises(EduSharingError):
            await node.children.add(b"x", filename="a.txt", mimetype="text/plain")


async def test_lesbare_darstellung():
    """repr taucht in Fehlermeldungen und Protokollen auf."""
    async with _repo(Instanz()) as repo:
        node = await repo.node(HAUPT)
        assert HAUPT in repr(node.children)


async def test_leerer_dateiname_wird_abgelehnt():
    instanz = Instanz()
    async with _repo(instanz) as repo:
        node = await repo.node(HAUPT)
        with pytest.raises(ValidationError):
            await node.children.add(b"x", filename="  ", mimetype="text/plain")
    assert not instanz.anfragen or all(r.method == "GET" for r in instanz.anfragen)


# --- Ablauf-Ebene ---------------------------------------------------------

async def test_flow_liefert_die_serienobjekte_als_json():
    instanz = Instanz(kinder=[_kind("a", "loesung.pdf", "0")])
    async with _repo(instanz) as repo:
        ergebnis = await repo.flows.child_objects(HAUPT)
    assert ergebnis["id"] == HAUPT
    assert ergebnis["count"] == 1
    assert ergebnis["children"][0]["name"] == "loesung.pdf"
    assert ergebnis["children"][0]["order"] == 0
    json.dumps(ergebnis)
