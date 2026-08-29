"""Verknuepfungen zwischen Knoten auf gleicher Ebene.

edu-sharing 11.0 hat dafuer eine eigene API (``/relation/v1``), die weder der
wlo-mcp-sc noch diese Bibliothek bisher nutzte. Sie ist der Weg, eine Reihe zu
modellieren: die Teile zeigen mit ``isPartOf`` auf die Reihe, Geschwister mit
``references`` aufeinander.

Alles hier gemessen gegen Staging am 27.08.2026:

* Die Umkehrung wird automatisch gefuehrt. Wer ``isPartOf`` von Teil zu Reihe
  anlegt, sieht an der Reihe ``hasPart`` -- ohne sie zweimal zu setzen.
* Die API kennt ``isAiGenerated`` und eine Freigabe (``approve``). Sie ist fuer
  maschinell erzeugte Verknuepfungen gebaut, was fuer die Zielgruppe dieser
  Bibliothek zaehlt: eine KI darf vorschlagen, ein Mensch bestaetigt.
"""

import json

import httpx
import pytest

from edusharing import AsyncRepository
from edusharing.errors import SilentDropError, ValidationError
from edusharing.relations import RELATION_TYPES, Relation

REPO = "https://repo.test/edu-sharing"


def _knoten(node_id: str, titel: str) -> dict:
    return {"ref": {"id": node_id}, "title": titel, "type": "ccm:io",
            "properties": {"cclom:title": [titel]}}


# Gemessene Antwortform von GET /relation/v1/-home-/{node}
ANTWORT = [
    {
        "fromNode": _knoten("teil-1", "Teil 1"),
        "toNode": _knoten("reihe", "Die Reihe"),
        "type": "isPartOf",
        "reverseType": None,
        "aiGenerated": False,
        "isAiGenerated": False,
        "evaluation": {"isApproved": False, "approvedBy": None, "approved": False},
        "metadata": {},
        "createdAt": "2026-08-27T10:00:00Z",
        "createdBy": {"userName": "alice"},
    },
    {
        "fromNode": _knoten("teil-1", "Teil 1"),
        "toNode": _knoten("teil-2", "Teil 2"),
        "type": "references",
        "reverseType": None,
        "aiGenerated": True,
        "isAiGenerated": True,
        "evaluation": {"isApproved": True, "approved": True},
        "metadata": {"quelle": "modell"},
        "createdAt": "2026-08-27T10:01:00Z",
        "createdBy": {"userName": "dienst"},
    },
]


class Instanz:
    def __init__(self, antwort=None) -> None:
        self.anfragen: list[httpx.Request] = []
        self.antwort = ANTWORT if antwort is None else antwort

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.anfragen.append(request)
        if request.url.path.startswith("/edu-sharing/rest/relation/"):
            if request.method == "GET":
                return httpx.Response(200, json=self.antwort)
            return httpx.Response(200, content=b"")
        return httpx.Response(200, json={"node": _knoten("teil-1", "Teil 1")})


def _repo(instanz) -> AsyncRepository:
    return AsyncRepository(
        REPO, backoff_base=0.0,
        client=httpx.AsyncClient(transport=httpx.MockTransport(instanz)))


# --- Lesen ----------------------------------------------------------------

async def test_relationen_eines_knotens_lesen():
    instanz = Instanz()
    async with _repo(instanz) as repo:
        relationen = await repo.relations.of("teil-1")

    assert len(relationen) == 2
    erste = relationen[0]
    assert erste.type == "isPartOf"
    assert erste.from_id == "teil-1"
    assert erste.to_id == "reihe"
    assert erste.to_title == "Die Reihe"
    assert erste.ai_generated is False
    assert erste.approved is False


async def test_maschinell_erzeugte_relation_ist_erkennbar():
    """Der Grund, warum das Feld hier auftaucht: eine KI darf vorschlagen, und
    wer die Vorschlaege sichtet, muss sie von gepflegten unterscheiden koennen."""
    instanz = Instanz()
    async with _repo(instanz) as repo:
        relationen = await repo.relations.of("teil-1")
    maschinell = [r for r in relationen if r.ai_generated]
    assert len(maschinell) == 1
    assert maschinell[0].approved is True


async def test_relation_traegt_die_gegenrichtung():
    """Aus Sicht des anderen Knotens heisst dieselbe Verknuepfung anders --
    gemessen: isPartOf erscheint dort als hasPart."""
    assert Relation.opposite_of("isPartOf") == "hasPart"
    assert Relation.opposite_of("hasPart") == "isPartOf"
    assert Relation.opposite_of("references") == "references"
    assert Relation.opposite_of("gibtsnicht") is None


async def test_leere_antwort_ist_kein_fehler():
    instanz = Instanz(antwort=[])
    async with _repo(instanz) as repo:
        assert await repo.relations.of("einsam") == []


# --- Schreiben ------------------------------------------------------------

async def test_relation_anlegen():
    instanz = Instanz()
    async with _repo(instanz) as repo:
        await repo.relations.create("teil-1", "isPartOf", "reihe")

    post = next(r for r in instanz.anfragen if r.method == "POST")
    koerper = json.loads(post.content)
    assert koerper == {"fromNode": "teil-1", "toNode": "reihe",
                       "type": "isPartOf", "isAiGenerated": False}


async def test_maschinelle_relation_wird_als_solche_angelegt():
    instanz = Instanz()
    async with _repo(instanz) as repo:
        await repo.relations.create("a", "references", "b", ai_generated=True)
    koerper = json.loads(next(r for r in instanz.anfragen if r.method == "POST").content)
    assert koerper["isAiGenerated"] is True


@pytest.mark.parametrize("typ", ["hasPart", "isBasisFor", "gibtsnicht", ""])
async def test_nicht_setzbare_typen_werden_abgelehnt(typ):
    """Nur sieben der zwoelf Typen lassen sich setzen; die uebrigen entstehen
    als Gegenrichtung von selbst. Wer hasPart zu setzen versucht, bekommt sonst
    einen HTTP 400 ohne erkennbaren Grund."""
    instanz = Instanz()
    async with _repo(instanz) as repo:
        with pytest.raises(ValidationError) as fehler:
            await repo.relations.create("a", typ, "b")
    assert "isPartOf" in str(fehler.value), "die Meldung muss die erlaubten nennen"


@pytest.mark.parametrize("von,nach", [("", "b"), ("a", ""), ("", "")])
async def test_fehlende_ids_werden_abgelehnt(von, nach):
    """Eine leere ID erzeugt einen doppelten Schraegstrich und damit einen
    voellig anderen Pfad."""
    instanz = Instanz()
    async with _repo(instanz) as repo:
        with pytest.raises(ValidationError):
            await repo.relations.create(von, "references", nach)
    assert not instanz.anfragen, "es darf nichts abgesetzt worden sein"


async def test_metadaten_werden_mitgeschickt():
    """Freitext an der Verknuepfung -- etwa, welches Modell sie vorschlug.

    Die Instanz hier speichert es; auf einer, die es verwirft, wirft
    ``create`` seit dem 28.08.2026 einen SilentDropError -- siehe
    ``test_verworfene_metadaten_werden_gemeldet``.
    """
    gespeichert = [dict(ANTWORT[0], fromNode=_knoten("a", "A"),
                        toNode=_knoten("b", "B"), type="references",
                        metadata={"modell": "opus", "score": 0.9})]
    instanz = Instanz(antwort=gespeichert)
    async with _repo(instanz) as repo:
        await repo.relations.create("a", "references", "b",
                                    metadata={"modell": "opus", "score": 0.9})
    koerper = json.loads(next(r for r in instanz.anfragen if r.method == "POST").content)
    assert koerper["metadata"] == {"modell": "opus", "score": 0.9}


async def test_lesbare_darstellung():
    """repr taucht in Fehlermeldungen und Protokollen auf."""
    from edusharing.relations import Relations
    instanz = Instanz()
    async with _repo(instanz) as repo:
        assert repo.url in repr(repo.relations)
        relation = (await repo.relations.of("teil-1"))[0]
    assert "teil-1" in repr(relation)
    assert "isPartOf" in repr(relation)
    assert isinstance(repo.relations, Relations)


async def test_ein_knoten_kann_sich_nicht_selbst_referenzieren():
    instanz = Instanz()
    async with _repo(instanz) as repo:
        with pytest.raises(ValidationError):
            await repo.relations.create("a", "references", "a")


async def test_relation_loeschen():
    instanz = Instanz()
    async with _repo(instanz) as repo:
        await repo.relations.delete("teil-1", "references", "teil-2")
    entfernt = next(r for r in instanz.anfragen if r.method == "DELETE")
    assert entfernt.url.path.endswith("/relation/v1/-home-/teil-1/references/teil-2")


async def test_ids_werden_im_pfad_kodiert():
    """Dieselbe Regel wie ueberall sonst (Audit F1): ein Bezeichner darf den
    Pfad nicht verlassen.

    Geprueft wird ``raw_path``, nicht ``path``: httpx dekodiert in ``path`` die
    Prozentzeichen wieder, sodass ein kodierter Schraegstrich dort wie ein
    echter aussieht. Was tatsaechlich ueber die Leitung geht, steht in
    ``raw_path`` -- und nur das entscheidet, was der Server als Segment sieht.

    Zwei Punkte sind uebrigens ein gueltiges Zeichen in einer ID. Gefaehrlich
    ist allein der Schraegstrich, der ein zusaetzliches Segment erzeugt.
    """
    instanz = Instanz()
    async with _repo(instanz) as repo:
        await repo.relations.delete("../admin", "references", "b/c")

    entfernt = next(r for r in instanz.anfragen if r.method == "DELETE")
    gesendet = entfernt.url.raw_path.decode()
    segmente = gesendet.strip("/").split("/")
    assert segmente[:5] == ["edu-sharing", "rest", "relation", "v1", "-home-"]
    assert len(segmente) == 8, f"die ID hat den Pfad zerlegt: {gesendet}"
    assert "%2F" in gesendet, "der Schraegstrich muss kodiert sein"


async def test_freigeben():
    instanz = Instanz()
    async with _repo(instanz) as repo:
        await repo.relations.approve("a", "references", "b")
    post = [r for r in instanz.anfragen if r.method == "POST"][-1]
    assert post.url.path.endswith("/a/references/b/approve")


# --- Die bekannten Typen --------------------------------------------------

def test_die_setzbaren_typen_sind_benannt():
    """Damit niemand raten muss, und damit die Fehlermeldung sie nennen kann."""
    assert "isPartOf" in RELATION_TYPES
    assert "references" in RELATION_TYPES
    assert "hasPart" not in RELATION_TYPES, "entsteht als Gegenrichtung"
    assert len(RELATION_TYPES) == 7


# --- Ablauf-Ebene ---------------------------------------------------------

async def test_flow_nennt_jeweils_den_anderen_knoten():
    """Wer nach den Relationen von "teil-1" fragt, will wissen, WOMIT er
    verknuepft ist -- nicht seine eigene ID zweimal."""
    instanz = Instanz()
    async with _repo(instanz) as repo:
        ergebnis = await repo.flows.relations("teil-1")

    assert ergebnis["count"] == 2
    ziele = {(r["type"], r["title"]) for r in ergebnis["relations"]}
    assert ziele == {("isPartOf", "Die Reihe"), ("references", "Teil 2")}
    json.dumps(ergebnis)


async def test_flow_meldet_maschinelle_und_bestaetigte_verknuepfungen():
    instanz = Instanz()
    async with _repo(instanz) as repo:
        ergebnis = await repo.flows.relations("teil-1")
    vorschlag = next(r for r in ergebnis["relations"] if r["ai_generated"])
    assert vorschlag["approved"] is True


async def test_verworfene_metadaten_werden_gemeldet():
    """edu-sharing 11.0 nimmt metadata an und speichert es nicht.

    Gemessen am 28.08.2026 gegen die Staging, dreimal und zuletzt direkt am
    Endpunkt an der Bibliothek vorbei -- nur Strings, mit isEvaluated, und
    verschachtelt. Jedes Mal HTTP 200, jedes Mal ``metadata: {}`` zurueck.
    Die Spezifikation gibt fuer CreateRelationRequest.metadata ein freies
    Objekt vor, die Bibliothek schickt also das Richtige.

    Genau der Fall, fuer den es SilentDropError gibt: ein Aufrufer, der eine
    Begruendung an die Verknuepfung haengt, muss erfahren, dass sie nicht
    ankam. Die Probe kostet eine zusaetzliche Anfrage und faellt nur an, wenn
    ueberhaupt metadata mitgegeben wurde -- dieselbe Abwaegung wie bei
    ``Node.update``.
    """
    verworfen = [dict(ANTWORT[0], fromNode=_knoten("a", "A"),
                      toNode=_knoten("b", "B"), type="references",
                      metadata={})]
    instanz = Instanz(antwort=verworfen)
    async with _repo(instanz) as repo:
        with pytest.raises(SilentDropError) as fehler:
            await repo.relations.create("a", "references", "b",
                                        metadata={"grund": "Probe"})
    assert "metadata" in str(fehler.value)


async def test_angekommene_metadaten_sind_kein_fehler():
    """Auf einer Instanz, die sie speichert, darf nichts geworfen werden --
    die Probe liest zurueck und urteilt danach, nicht nach der Version."""
    behalten = [dict(ANTWORT[0], fromNode=_knoten("a", "A"),
                     toNode=_knoten("b", "B"), type="references",
                     metadata={"grund": "Probe"})]
    async with _repo(Instanz(antwort=behalten)) as repo:
        await repo.relations.create("a", "references", "b",
                                    metadata={"grund": "Probe"})


async def test_ohne_metadaten_wird_nicht_zurueckgelesen():
    """Kein Aufwand, wo nichts zu pruefen ist."""
    instanz = Instanz()
    async with _repo(instanz) as repo:
        await repo.relations.create("a", "references", "b")
    gelesen = [r for r in instanz.anfragen
               if r.method == "GET" and "/relation/" in r.url.path]
    assert not gelesen, f"unnoetige Rueckleseprobe: {[r.url.path for r in gelesen]}"
