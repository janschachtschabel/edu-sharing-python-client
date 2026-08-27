"""Die schreibenden Ablaeufe.

Zwei Dinge nehmen sie ab, die auf API-Ebene jedes Mal von Hand zu tun sind:

**Wo liegt mein Zeug.** Das Home-Verzeichnis steckt vier Ebenen tief in der
Antwort von whoami(). Ohne Ablauf gehoert dieser Griff in jedes Skript.

**Vokabular beim Schreiben.** Lesend loest die Suche "Biologie" zu ihrem URI
auf. Schreibend musste man den URI bisher kennen. Genau da faellt es schwerer
auf, wenn es fehlt: das Material wird angelegt, nur ohne Fach.
"""

import json

import httpx
import pytest

from edusharing import AsyncRepository
from edusharing.errors import EduSharingError

REPO = "https://repo.test/edu-sharing"
HOME = "home-folder-id"
NEU = "neuer-knoten"

FAECHER = {"values": [
    {"key": "http://w3id.org/openeduhub/vocabs/discipline/080", "displayString": "Biologie"},
    {"key": "http://w3id.org/openeduhub/vocabs/discipline/460", "displayString": "Physik"},
]}

ICH = {"person": {"authorityName": "alice", "userName": "alice", "profile": {},
                  "homeFolder": {"id": HOME}}}


class Instanz:
    """Ein Mock mit Gedaechtnis -- die Rueckleseprobe verlangt, dass ein
    Schreibvorgang sichtbar wird."""

    def __init__(self) -> None:
        self.knoten: dict[str, dict] = {}
        self.referenzen: list[tuple[str, str]] = []
        self.geloescht: list[str] = []
        self.anfragen: list[httpx.Request] = []

    def _antwort(self, node_id: str) -> dict:
        daten = self.knoten.setdefault(node_id, {"properties": {}})
        props = daten["properties"]
        return {"node": {
            "ref": {"id": node_id}, "type": "ccm:io", "access": ["Read", "Write"],
            "name": (props.get("cm:name") or [""])[0],
            "title": (props.get("cclom:title") or props.get("cm:title") or [""])[0],
            "content": {"hash": "-1"}, "properties": props,
        }}

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.anfragen.append(request)
        pfad, methode = request.url.path, request.method

        if "/values" in pfad:
            return httpx.Response(200, json=FAECHER)
        if "-me-" in pfad:
            return httpx.Response(200, json=ICH)
        if "/children" in pfad and methode == "POST" and "/collection" not in pfad:
            props = json.loads(request.content)
            self.knoten[NEU] = {"properties": dict(props)}
            return httpx.Response(200, json=self._antwort(NEU))
        if "/collection" in pfad and methode == "POST":
            self.knoten["sammlung-1"] = {"properties": {"cm:title": ["Sammlung"]}}
            return httpx.Response(200, json={"collection": {
                "ref": {"id": "sammlung-1"}, "title": "Sammlung",
                "collection": {"scope": "MY"}}})
        if "/references/" in pfad:
            teile = pfad.rstrip("/").split("/")
            self.referenzen.append((teile[-3], teile[-1]))
            return httpx.Response(200, content=b"")
        if methode == "PUT" and pfad.endswith("/metadata"):
            knoten_id = pfad.split("/-home-/")[1].split("/")[0]
            self.knoten.setdefault(knoten_id, {"properties": {}})["properties"].update(
                json.loads(request.content))
            return httpx.Response(200, json=self._antwort(knoten_id))
        if methode == "DELETE":
            self.geloescht.append(pfad.rstrip("/").split("/")[-1])
            return httpx.Response(200, content=b"")
        knoten_id = pfad.split("/-home-/")[1].split("/")[0] if "/-home-/" in pfad else NEU
        return httpx.Response(200, json=self._antwort(knoten_id))


def _repo(instanz: Instanz, **kwargs) -> AsyncRepository:
    return AsyncRepository(
        REPO, metadataset="mds_oeh", backoff_base=0.0,
        client=httpx.AsyncClient(transport=httpx.MockTransport(instanz)), **kwargs)


# --- Identity.home_folder -------------------------------------------------

async def test_identity_kennt_das_home_verzeichnis():
    """Es lag vier Ebenen tief in raw. Wer dorthin schreiben will, hat den
    Griff bisher selbst gebaut."""
    instanz = Instanz()
    async with _repo(instanz) as repo:
        wer = await repo.whoami()
    assert wer.home_folder == HOME


# --- add_material ---------------------------------------------------------

async def test_material_anlegen_ohne_ort_landet_im_home_verzeichnis():
    instanz = Instanz()
    async with _repo(instanz) as repo:
        ergebnis = await repo.flows.add_material("Feuerspuren")
    assert ergebnis["id"] == NEU
    assert ergebnis["parent_id"] == HOME
    json.dumps(ergebnis)


async def test_material_anlegen_loest_vokabular_auf():
    """Der eigentliche Gewinn: subject="Biologie" statt des URI."""
    instanz = Instanz()
    async with _repo(instanz) as repo:
        await repo.flows.add_material("Feuerspuren", subject="Biologie")
    geschrieben = instanz.knoten[NEU]["properties"]
    assert geschrieben["ccm:taxonid"] == [
        "http://w3id.org/openeduhub/vocabs/discipline/080"]


async def test_unaufloesbarer_wert_wird_gemeldet_nicht_verschwiegen():
    """Schreibend wiegt das schwerer als lesend: das Material entsteht, nur
    ohne das Feld -- und sieht vollstaendig aus."""
    instanz = Instanz()
    async with _repo(instanz) as repo:
        ergebnis = await repo.flows.add_material("Feuerspuren", subject="Gibtsnicht")
    assert ergebnis["unresolved"], "der Wert fiel weg, ohne dass es jemand erfaehrt"
    assert ergebnis["unresolved"][0]["field"] == "subject"
    assert "ccm:taxonid" not in instanz.knoten[NEU]["properties"]


async def test_material_bekommt_titel_und_link():
    instanz = Instanz()
    async with _repo(instanz) as repo:
        await repo.flows.add_material(
            "Feuerspuren", url="https://beispiel.test/m",
            description="Beschreibung", keywords=["Feuer", "Satellit"])
    props = instanz.knoten[NEU]["properties"]
    assert props["cclom:title"] == ["Feuerspuren"]
    assert props["ccm:wwwurl"] == ["https://beispiel.test/m"]
    assert props["cclom:general_keyword"] == ["Feuer", "Satellit"]


async def test_material_kann_direkt_in_eine_sammlung():
    """Sonst sind es zwei Aufrufe, und der zweite wird vergessen."""
    instanz = Instanz()
    async with _repo(instanz) as repo:
        ergebnis = await repo.flows.add_material(
            "Feuerspuren", collection_id="sammlung-1")
    assert ("sammlung-1", NEU) in instanz.referenzen
    assert ergebnis["collection"]["id"] == "sammlung-1"


async def test_leerer_titel_wird_abgelehnt():
    instanz = Instanz()
    async with _repo(instanz) as repo:
        with pytest.raises(EduSharingError):
            await repo.flows.add_material("   ")


# --- build_collection -----------------------------------------------------

async def test_sammlung_anlegen_und_fuellen_in_einem_aufruf():
    instanz = Instanz()
    async with _repo(instanz) as repo:
        ergebnis = await repo.flows.build_collection(
            "Meine Sammlung", node_ids=["a", "b"])
    assert ergebnis["id"] == "sammlung-1"
    assert ergebnis["added"] == ["a", "b"]
    assert ergebnis["failed"] == []
    json.dumps(ergebnis)


async def test_fehlgeschlagenes_einlegen_wird_benannt():
    """Teilerfolg ist der Normalfall. Ein Ablauf, der ihn verschweigt, meldet
    Erfolg fuer etwas, das nur halb passiert ist."""
    instanz = Instanz()

    def handler(request):
        if "/references/" in request.url.path and request.url.path.endswith("/kaputt"):
            return httpx.Response(403, json={"error": "kein Zugriff"})
        return instanz(request)

    async with AsyncRepository(
        REPO, metadataset="mds_oeh", backoff_base=0.0,
        client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    ) as repo:
        ergebnis = await repo.flows.build_collection("S", node_ids=["gut", "kaputt"])
    assert ergebnis["added"] == ["gut"]
    assert len(ergebnis["failed"]) == 1
    assert ergebnis["failed"][0]["id"] == "kaputt"
    assert "reason" in ergebnis["failed"][0]


# --- delete ---------------------------------------------------------------

async def test_loeschen_sagt_was_geloescht_wurde():
    """Ein blosses "erledigt" laesst den Aufrufer im Ungewissen, ob er das
    Richtige erwischt hat -- und ein Sprachmodell bestaetigt dann irgendetwas."""
    instanz = Instanz()
    instanz.knoten["abc"] = {"properties": {"cclom:title": ["Feuerspuren"]}}
    async with _repo(instanz) as repo:
        ergebnis = await repo.flows.delete("abc")
    assert ergebnis["id"] == "abc"
    assert ergebnis["title"] == "Feuerspuren"
    assert ergebnis["recycled"] is True
    assert "abc" in instanz.geloescht


async def test_loeschen_geht_standardmaessig_in_den_papierkorb():
    """Die Vorgabe ist die umkehrbare Variante. Wer endgueltig loeschen will,
    muss es hinschreiben."""
    instanz = Instanz()
    instanz.knoten["abc"] = {"properties": {"cclom:title": ["Weg"]}}
    async with _repo(instanz) as repo:
        await repo.flows.delete("abc")
    loeschung = [r for r in instanz.anfragen if r.method == "DELETE"][-1]
    assert loeschung.url.params.get("recycle") == "true"


async def test_ein_uri_wird_unveraendert_durchgereicht():
    """Wer den URI schon kennt, soll ihn benutzen duerfen. Durch den Resolver
    geschickt wuerde er als unaufloesbar gemeldet -- obwohl er richtig ist."""
    instanz = Instanz()
    uri = "http://w3id.org/openeduhub/vocabs/discipline/460"
    async with _repo(instanz) as repo:
        ergebnis = await repo.flows.add_material("Titel", subject=uri)
    assert not ergebnis["unresolved"]
    assert instanz.knoten[NEU]["properties"]["ccm:taxonid"] == [uri]


async def test_ohne_home_verzeichnis_wird_der_grund_genannt():
    """Ein Gastkonto hat keines. Ohne diese Meldung endet der Aufruf in einem
    404 auf eine leere Eltern-ID, und niemand weiss warum."""
    instanz = Instanz()

    def ohne_home(request):
        if "-me-" in request.url.path:
            return httpx.Response(200, json={"person": {
                "authorityName": "GUEST", "userName": "guest", "profile": {}}})
        return instanz(request)

    async with AsyncRepository(
        REPO, metadataset="mds_oeh", backoff_base=0.0,
        client=httpx.AsyncClient(transport=httpx.MockTransport(ohne_home)),
    ) as repo:
        with pytest.raises(EduSharingError) as fehler:
            await repo.flows.add_material("Titel")
    assert "parent_id" in str(fehler.value), "die Meldung muss den Ausweg nennen"


async def test_sammlungsparameter_kommen_richtig_an():
    """parent heisst auf der API-Ebene parent, nicht parent_id -- ein
    vertauschter Name faellt sonst erst im Betrieb auf."""
    instanz = Instanz()
    async with _repo(instanz) as repo:
        await repo.flows.build_collection(
            "S", description="Text", parent_id="eltern-1", scope="PUBLIC")
    post = next(r for r in instanz.anfragen
                if r.method == "POST" and "/collection" in r.url.path)
    body = json.loads(post.content)
    assert body["collection"]["scope"] == "PUBLIC"
    assert body["collection"]["description"] == "Text"
    assert post.url.path.endswith("/-home-/eltern-1/children")
