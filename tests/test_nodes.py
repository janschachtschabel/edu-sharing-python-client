"""Knoten lesen, anlegen, aendern -- mit Rueckleseprobe.

Gemessen gegen edu-sharing 11.0 (Staging, 27.08.2026), an einem Wegwerf-Knoten:

    PUT /metadata, Property im MDS          200  gespeichert
    PUT /metadata, Property NICHT im MDS    200  NICHT gespeichert
    POST /property, dieselbe Property       200  gespeichert
    PUT /metadata, erfundenes Feld          200  NICHT gespeichert

Zweimal HTTP 200 fuer etwas, das nicht passiert ist. Ein Statuscode ist hier
also kein Persistenzbeweis, und ohne Rueckleseprobe meldet eine Anwendung
Erfolg fuer verlorene Daten.
"""

import json

import httpx
import pytest

from edusharing.errors import SilentDropError
from edusharing.nodes import Node, Nodes
from edusharing.transport import Transport

REPO = "https://repository.staging.openeduhub.net/edu-sharing"
NID = "c2eac649-8e3d-4ed2-aac6-498e3d7ed2d9"


def _node_antwort(properties: dict) -> dict:
    return {"node": {
        "ref": {"id": NID, "repo": "local"},
        "name": "material.txt",
        "title": (properties.get("cclom:title") or [""])[0],
        "type": "ccm:io",
        "access": ["Read", "Write", "Delete"],
        "properties": properties,
    }}


class Server:
    """Ein Knoten im Speicher, der sich verhaelt wie edu-sharing.

    ``stumm`` nennt die Properties, die bei ``PUT /metadata`` verworfen werden
    -- so wie das Repositorium alles verwirft, was der Metadatensatz nicht
    kennt.
    """

    def __init__(self, properties: dict | None = None, stumm: tuple[str, ...] = ()):
        self.props = dict(properties or {"cclom:title": ["Alt"]})
        self.stumm = stumm
        self.aufrufe: list[httpx.Request] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.aufrufe.append(request)
        pfad, methode = request.url.path, request.method

        if methode == "GET" and pfad.endswith("/metadata"):
            return httpx.Response(200, json=_node_antwort(self.props))

        if methode == "PUT" and pfad.endswith("/metadata"):
            for k, v in json.loads(request.content).items():
                if k not in self.stumm:          # stille Verwerfung nachbilden
                    self.props[k] = v
            return httpx.Response(200, json=_node_antwort(self.props))

        if methode == "POST" and pfad.endswith("/property"):
            prop = request.url.params.get("property")
            wert = json.loads(request.content)
            if wert is None:
                self.props.pop(prop, None)
            else:
                self.props[prop] = wert          # umgeht die MDS-Filterung
            return httpx.Response(200, content=b"")

        if methode == "POST" and pfad.endswith("/children"):
            self.props.update(json.loads(request.content))
            return httpx.Response(200, json=_node_antwort(self.props))

        if methode == "DELETE":
            return httpx.Response(200, content=b"")

        return httpx.Response(404, json={"error": "x", "message": f"{methode} {pfad}"})


def _nodes(server: Server) -> Nodes:
    transport = Transport(
        REPO, client=httpx.AsyncClient(transport=httpx.MockTransport(server)),
        backoff_base=0.0,
    )
    return Nodes(transport)


# --- Lesen ----------------------------------------------------------------

async def test_knoten_laden():
    node = await _nodes(Server()).get(NID)
    assert isinstance(node, Node)
    assert node.id == NID
    assert node.title == "Alt"
    assert node.url == f"{REPO}/components/render/{NID}"


async def test_geladener_knoten_kennt_seine_rechte():
    """Vor einem Schreibvorgang laesst sich damit pruefen, ob er ueberhaupt
    erlaubt ist -- statt ein stilles Nichts als Erfolg zu lesen."""
    node = await _nodes(Server()).get(NID)
    assert node.can_write is True
    assert "Delete" in node.access


async def test_properties_sind_erreichbar():
    node = await _nodes(Server({"cclom:title": ["Alt"], "ccm:wwwurl": ["https://x.test"]})).get(NID)
    assert node.get("ccm:wwwurl") == "https://x.test"
    assert node.get_all("ccm:wwwurl") == ["https://x.test"]
    assert node.get("gibtsnicht") is None


# --- Schreiben mit Rueckleseprobe -----------------------------------------

async def test_update_speichert_und_liest_zurueck():
    server = Server()
    node = await _nodes(server).get(NID)
    aktualisiert = await node.update(title="Neu")
    assert aktualisiert.title == "Neu"
    assert any(r.method == "PUT" for r in server.aufrufe)


async def test_update_prueft_wirklich_zurueck():
    """Die Probe muss ein echter GET nach dem Schreiben sein -- die Antwort des
    PUT selbst zu glauben hiesse, dem Server bei der Frage zu trauen, die er
    gerade falsch beantwortet."""
    server = Server()
    node = await _nodes(server).get(NID)
    server.aufrufe.clear()
    await node.update(title="Neu")
    folge = [r.method for r in server.aufrufe]
    assert folge.index("PUT") < folge.index("GET"), "GET muss nach dem PUT kommen"


async def test_stiller_verlust_wird_zum_fehler():
    """Der Kernfall: HTTP 200, Wert nach der Rueckleseprobe abwesend."""
    server = Server(stumm=("ccm:oeh_collection_compendium_text",))
    node = await _nodes(server).get(NID)
    with pytest.raises(SilentDropError) as info:
        await node.update(properties={"ccm:oeh_collection_compendium_text": "Text"})
    assert "ccm:oeh_collection_compendium_text" in str(info.value)


async def test_fehler_nennt_den_ausweg():
    """Wer hier strandet, soll nicht raten muessen: set_property umgeht die
    Filterung des Metadatensatzes."""
    server = Server(stumm=("ccm:foo",))
    node = await _nodes(server).get(NID)
    with pytest.raises(SilentDropError) as info:
        await node.update(properties={"ccm:foo": "x"})
    assert "set_property" in str(info.value)


async def test_fehler_kennt_die_betroffenen_felder():
    server = Server(stumm=("ccm:foo", "ccm:bar"))
    node = await _nodes(server).get(NID)
    with pytest.raises(SilentDropError) as info:
        await node.update(properties={"ccm:foo": "x", "ccm:bar": "y", "cclom:title": "ok"})
    assert set(info.value.dropped) == {"ccm:foo", "ccm:bar"}


async def test_teilerfolg_bleibt_erhalten():
    """Was durchkam, bleibt geschrieben -- edu-sharing kann nicht zurueckrollen.
    Der Fehler meldet den Verlust, taeuscht aber keinen Rollback vor."""
    server = Server(stumm=("ccm:foo",))
    node = await _nodes(server).get(NID)
    with pytest.raises(SilentDropError):
        await node.update(properties={"ccm:foo": "x", "cclom:title": "Durchgekommen"})
    assert server.props["cclom:title"] == ["Durchgekommen"]


async def test_verify_abschaltbar():
    """Bei einem Stapellauf ueber viele Knoten verdoppelt die Probe die
    Aufrufe. Wer das abwaegt, darf sie abschalten -- bewusst, nicht by default."""
    server = Server(stumm=("ccm:foo",))
    node = await _nodes(server).get(NID)
    await node.update(properties={"ccm:foo": "x"}, verify=False)
    assert not any(r.method == "GET" for r in server.aufrufe[1:])


# --- Der Direktweg --------------------------------------------------------

async def test_set_property_umgeht_die_filterung():
    server = Server(stumm=("ccm:foo",))
    node = await _nodes(server).get(NID)
    aktualisiert = await node.set_property("ccm:foo", "x")
    assert aktualisiert.get("ccm:foo") == "x"


async def test_set_property_prueft_ebenfalls_zurueck():
    """Auch dieser Weg kann scheitern -- etwa mangels Schreibrecht."""
    class Verweigert(Server):
        def __call__(self, request):
            if request.method == "POST" and request.url.path.endswith("/property"):
                self.aufrufe.append(request)
                return httpx.Response(200, content=b"")   # tut nur so
            return super().__call__(request)

    node = await _nodes(Verweigert()).get(NID)
    with pytest.raises(SilentDropError):
        await node.set_property("ccm:foo", "x")


async def test_set_property_kann_loeschen():
    server = Server({"cclom:title": ["Alt"], "ccm:foo": ["weg damit"]})
    node = await _nodes(server).get(NID)
    aktualisiert = await node.set_property("ccm:foo", None)
    assert aktualisiert.get("ccm:foo") is None


# --- Feld-Aliase ----------------------------------------------------------

async def test_titel_wird_in_beide_namensraeume_geschrieben():
    """Gemessen im WLO-Umfeld: die Oberflaeche rendert cm:title und
    cclom:title unterschiedlich. Nur eines zu setzen fuehrt dazu, dass die
    Anzeige etwas anderes zeigt als die Anwendung geschrieben hat."""
    server = Server()
    node = await _nodes(server).get(NID)
    await node.update(title="Neu")
    assert server.props["cm:title"] == ["Neu"]
    assert server.props["cclom:title"] == ["Neu"]


async def test_beschreibung_ebenfalls_doppelt():
    server = Server()
    node = await _nodes(server).get(NID)
    await node.update(description="Text")
    assert server.props["cm:description"] == ["Text"]
    assert server.props["cclom:general_description"] == ["Text"]


async def test_unbekannter_alias_wird_abgelehnt():
    node = await _nodes(Server()).get(NID)
    with pytest.raises(Exception, match="voelligNeu"):
        await node.update(voelligNeu="x")


async def test_werte_werden_zu_listen():
    """edu-sharing erwartet jede Property als Liste, auch einzelne Werte."""
    server = Server()
    node = await _nodes(server).get(NID)
    await node.update(properties={"ccm:wwwurl": "https://x.test"})
    assert server.props["ccm:wwwurl"] == ["https://x.test"]


# --- Anlegen und Loeschen -------------------------------------------------

async def test_knoten_anlegen():
    server = Server()
    node = await _nodes(server).create("parent-1", name="neu.txt", title="Frisch")
    assert node.id == NID
    erzeugung = next(r for r in server.aufrufe if r.url.path.endswith("/children"))
    assert "parent-1" in str(erzeugung.url)
    assert erzeugung.url.params.get("type") == "ccm:io"


async def test_anlegen_ohne_namen_wird_abgelehnt():
    """cm:name ist der Schluessel im Elternknoten -- ohne ihn ist das Ergebnis
    vom Server abhaengig statt vorhersagbar."""
    with pytest.raises(Exception, match="name"):
        await _nodes(Server()).create("parent-1", name="")


async def test_loeschen_landet_per_vorgabe_im_papierkorb():
    """recycle=true ist der Schalter fuer Wiederherstellbarkeit und wird
    deshalb immer explizit gesetzt, nie dem Server ueberlassen."""
    server = Server()
    node = await _nodes(server).get(NID)
    await node.delete()
    loeschung = next(r for r in server.aufrufe if r.method == "DELETE")
    assert loeschung.url.params.get("recycle") == "true"


async def test_endgueltiges_loeschen_muss_verlangt_werden():
    server = Server()
    node = await _nodes(server).get(NID)
    await node.delete(recycle=False)
    loeschung = next(r for r in server.aufrufe if r.method == "DELETE")
    assert loeschung.url.params.get("recycle") == "false"


# --- Der synchrone Zugang -------------------------------------------------

def test_synchroner_knoten_blockiert_statt_zu_awaiten():
    """Wer Repository benutzt, soll node.update() ohne await schreiben koennen
    -- sonst ist der synchrone Zugang beim Schreiben eine Sackgasse."""
    from edusharing import Repository

    server = Server()
    with Repository(
        REPO, client=httpx.AsyncClient(transport=httpx.MockTransport(server)),
    ) as repo:
        node = repo.node(NID)
        assert node.title == "Alt"
        aktualisiert = node.update(title="Neu")
        assert aktualisiert.title == "Neu"


def test_synchroner_knoten_meldet_stillen_verlust():
    from edusharing import Repository

    server = Server(stumm=("ccm:foo",))
    with Repository(
        REPO, client=httpx.AsyncClient(transport=httpx.MockTransport(server)),
    ) as repo:
        with pytest.raises(SilentDropError):
            repo.node(NID).update(properties={"ccm:foo": "x"})


def test_synchron_anlegen_und_loeschen():
    from edusharing import Repository

    server = Server()
    with Repository(
        REPO, client=httpx.AsyncClient(transport=httpx.MockTransport(server)),
    ) as repo:
        node = repo.create_node("parent-1", name="neu.txt")
        assert node.id == NID
        node.delete()
        assert any(r.method == "DELETE" for r in server.aufrufe)


# --- Schlagworte: eine geteilte Liste -------------------------------------

async def test_schlagworte_werden_gelesen():
    server = Server({"cclom:general_keyword": ["Weimar", "Klassik"]})
    node = await _nodes(server).get(NID)
    assert node.keywords == ["Weimar", "Klassik"]


async def test_hinzufuegen_erhaelt_fremde_eintraege():
    """cclom:general_keyword pflegen mehrere Beteiligte gemeinsam. Wer die
    Liste setzt statt ergaenzt, loescht die Arbeit anderer -- lautlos."""
    server = Server({"cclom:general_keyword": ["Fremd", "Auch fremd"]})
    node = await _nodes(server).get(NID)
    aktualisiert = await node.add_keywords("Meins")
    assert aktualisiert.keywords == ["Fremd", "Auch fremd", "Meins"]


async def test_hinzufuegen_dupliziert_nicht():
    server = Server({"cclom:general_keyword": ["Weimar"]})
    node = await _nodes(server).get(NID)
    aktualisiert = await node.add_keywords("Weimar", "Klassik")
    assert aktualisiert.keywords == ["Weimar", "Klassik"]


async def test_hinzufuegen_liest_vorher_frisch():
    """Das Node-Objekt kann veraltet sein. Auf seinem Stand zu mergen wuerde
    alles ueberschreiben, was seit dem Laden dazugekommen ist."""
    server = Server({"cclom:general_keyword": ["Alt"]})
    node = await _nodes(server).get(NID)
    server.props["cclom:general_keyword"] = ["Alt", "Inzwischen dazugekommen"]
    aktualisiert = await node.add_keywords("Meins")
    assert "Inzwischen dazugekommen" in aktualisiert.keywords


async def test_entfernen_laesst_andere_stehen():
    server = Server({"cclom:general_keyword": ["Fremd", "Meins"]})
    node = await _nodes(server).get(NID)
    aktualisiert = await node.remove_keywords("Meins")
    assert aktualisiert.keywords == ["Fremd"]


async def test_entfernen_eines_unbekannten_ist_kein_fehler():
    server = Server({"cclom:general_keyword": ["Fremd"]})
    node = await _nodes(server).get(NID)
    aktualisiert = await node.remove_keywords("gibtsnicht")
    assert aktualisiert.keywords == ["Fremd"]


async def test_hinzufuegen_ohne_argumente_schreibt_nicht():
    """Ein leerer Aufruf darf keinen Schreibvorgang ausloesen."""
    server = Server({"cclom:general_keyword": ["Fremd"]})
    node = await _nodes(server).get(NID)
    server.aufrufe.clear()
    await node.add_keywords()
    assert not any(r.method == "PUT" for r in server.aufrufe)


# --- Dateien --------------------------------------------------------------

async def test_datei_hochladen():
    """mimetype ist Pflicht -- die Spec deklariert ihn als required, und ohne
    ihn kann das Repositorium den Inhalt nicht einordnen."""
    hochgeladen = []

    class MitDatei(Server):
        def __call__(self, request):
            if request.method == "POST" and request.url.path.endswith("/content"):
                hochgeladen.append(request)
                return httpx.Response(200, json=_node_antwort(self.props))
            return super().__call__(request)

    node = await _nodes(MitDatei()).get(NID)
    await node.content.upload(b"Hallo", filename="probe.txt", mimetype="text/plain")
    assert hochgeladen
    assert hochgeladen[0].url.params.get("mimetype") == "text/plain"


async def test_upload_ohne_mimetype_wird_abgelehnt():
    node = await _nodes(Server()).get(NID)
    with pytest.raises(Exception, match="mimetype"):
        await node.content.upload(b"x", filename="p.txt", mimetype="")


async def test_download_nutzt_die_downloadurl_des_knotens():
    """Es gibt kein GET auf .../content -- gemessen antwortet es mit 405.
    Der Weg fuehrt ueber die downloadUrl aus den Metadaten."""
    geholt = []

    class MitDownload(Server):
        def __call__(self, request):
            if "eduservlet/download" in str(request.url):
                geholt.append(request)
                return httpx.Response(200, content=b"Dateiinhalt")
            return super().__call__(request)

    server = MitDownload()
    node = await _nodes(server).get(NID)
    node._data["downloadUrl"] = f"{REPO}/eduservlet/download?node={NID}"
    node._data["content"] = {"hash": "-1222810457"}     # gemessene Form
    assert await node.content.download() == b"Dateiinhalt"
    assert geholt


async def test_download_ohne_datei_meldet_das_klar():
    """Ein Knoten ohne Datei darf keinen leeren Bytestring vortaeuschen.

    Die Pruefung geht ueber den Hash, nicht ueber downloadUrl: gemessen ist
    downloadUrl IMMER gesetzt, und ein Knoten ohne Inhalt liefert daran 200
    mit null Bytes. Der Hash dagegen ist nur ohne Inhalt None -- bei einer
    0-Byte-Datei ist er gesetzt.
    """
    node = await _nodes(Server()).get(NID)
    node._data["downloadUrl"] = f"{REPO}/eduservlet/download?node={NID}"
    node._data["content"] = {"hash": None}
    assert node.content.has_content is False
    with pytest.raises(Exception, match="carries no file"):
        await node.content.download()


async def test_leere_datei_gilt_als_inhalt():
    """Die Unterscheidung, die den Hash noetig macht: eine 0-Byte-Datei ist
    ein Inhalt, ein Knoten ohne Datei nicht -- beide haben cclom:size None."""
    node = await _nodes(Server()).get(NID)
    node._data["content"] = {"hash": "-190212752"}     # gemessen bei b""
    assert node.content.has_content is True


async def test_textinhalt_wird_ausgepackt():
    """textContent antwortet mit {"text": ...} -- der Rumpf ist JSON, nicht
    der Text selbst."""
    class MitText(Server):
        def __call__(self, request):
            if request.url.path.endswith("/textContent"):
                return httpx.Response(200, json={"text": "Der extrahierte Text"})
            return super().__call__(request)

    node = await _nodes(MitText()).get(NID)
    assert await node.content.text() == "Der extrahierte Text"
