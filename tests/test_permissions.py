"""Wer darf was mit einem Knoten -- und wer darf ihn ueberhaupt sehen.

Ohne diesen Teil legt die Bibliothek Material an, das ausser dem Anleger
niemand lesen kann, und meldet Erfolg. Die Ideendatenbank hat den Grund
aufgeschrieben: edu-sharing veroeffentlicht ein Original **nicht**, wenn es als
Referenz in eine oeffentliche Sammlung gehaengt wird.

Alles hier gemessen gegen Staging am 28.08.2026, in einem eigens angelegten
Wegwerf-Ordner:

* Der ``POST`` **ersetzt** die lokale ACL. Wer nur ein Recht ergaenzen will,
  muss selbst zusammenfuehren -- sonst loescht er die uebrigen Eintraege.
* Ein **GROUP_-Name ohne Gruppe dahinter** wird still verworfen: HTTP 200,
  und danach steht nichts da. Ein **Benutzername** wird dagegen gar nicht
  geprueft -- ein Eintrag fuer ein Konto, das es nicht gibt, wird gespeichert
  und berechtigt niemanden.
* Ein unbekannter **Rechtename** ist dagegen laut -- HTTP 500
  ``Can not find Quatschrecht``.
* Ein Knoten ist oeffentlich, wenn sein **Elternteil** es ist. Das Recht steht
  dann unter ``inheritedPermissions``, die lokale ACL bleibt leer.
* Die lokale ACL zu leeren nimmt das **nicht** zurueck. Nur ``inherited=false``
  tut das -- und schneidet dabei jedes geerbte Recht ab, nicht nur dieses.
* Der ``POST`` antwortet mit **leerem Body**. Es gibt nichts zu pruefen ausser
  einem zweiten Lesen.
"""

import json

import httpx
import pytest

from edusharing import AsyncRepository
from edusharing.errors import ConflictError, SilentDropError
from edusharing.permissions import CONSUMER, EVERYONE, Ace, Permissions

REPO = "https://repo.test/edu-sharing"


def _ace(name: str, *rechte: str, typ: str = "USER") -> dict:
    return {"authority": {"authorityName": name, "authorityType": typ},
            "permissions": list(rechte), "editable": True}


def _antwort(*, inherits: bool = True, own: list[dict] | None = None,
             inherited: list[dict] | None = None) -> dict:
    """Die gemessene Form von GET /node/v1/nodes/-home-/{id}/permissions."""
    return {"permissions": {
        "localPermissions": {"inherited": inherits, "permissions": own or []},
        "inheritedPermissions": inherited if inherited is not None
        else [_ace("ROLE_OWNER", "All", typ="OWNER")],
    }}


class Instanz:
    """Ein Repositorium, dessen ACL sich merkt, was geschrieben wurde."""

    def __init__(self, *, inherits: bool = True, own: list[dict] | None = None,
                 inherited: list[dict] | None = None,
                 taub: bool = False) -> None:
        self.inherits = inherits
        self.own = list(own or [])
        self.inherited = inherited if inherited is not None else [
            _ace("ROLE_OWNER", "All", typ="OWNER")]
        # taub=True bildet den gemessenen stillen Verlust nach: 200, nichts
        # gespeichert.
        self.taub = taub
        self.geschrieben: list[dict] = []

    def handler(self, request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/permissions"):
            if request.method == "GET":
                return httpx.Response(200, json=_antwort(
                    inherits=self.inherits, own=self.own, inherited=self.inherited))
            koerper = json.loads(request.content)
            self.geschrieben.append(koerper)
            if not self.taub:
                self.inherits = koerper["inherited"]
                self.own = list(koerper["permissions"])
            return httpx.Response(200, content=b"")
        return httpx.Response(
                200, json={"node": {"ref": {"id": "n1"}, "type": "ccm:io"}})

    def repo(self) -> AsyncRepository:
        return AsyncRepository(
            REPO, backoff_base=0.0,
            client=httpx.AsyncClient(transport=httpx.MockTransport(self.handler)))


# --- Lesen ----------------------------------------------------------------

async def test_liest_eigene_und_geerbte_rechte():
    instanz = Instanz(own=[_ace("alice", "Coordinator")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        rechte = await knoten.permissions.get()
    assert [a.authority for a in rechte.own] == ["alice"]
    assert [a.authority for a in rechte.inherited] == ["ROLE_OWNER"]
    assert rechte.inherits is True


async def test_oeffentlich_durch_eigenes_recht():
    instanz = Instanz(own=[_ace(EVERYONE, CONSUMER, typ="EVERYONE")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        rechte = await knoten.permissions.get()
    assert rechte.is_public


async def test_oeffentlich_durch_vererbung():
    """Gemessen: liegt der Knoten in einem oeffentlichen Ordner, bleibt seine
    lokale ACL leer und das Recht steht unter den geerbten. Wer nur die lokale
    ansieht, haelt einen fuer alle lesbaren Knoten fuer privat."""
    instanz = Instanz(own=[], inherited=[
        _ace("ROLE_OWNER", "All", typ="OWNER"),
        _ace(EVERYONE, CONSUMER, typ="EVERYONE")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        rechte = await knoten.permissions.get()
    assert rechte.own == ()
    assert rechte.is_public


async def test_nicht_oeffentlich():
    instanz = Instanz(own=[_ace("alice", "Coordinator")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        rechte = await knoten.permissions.get()
    assert not rechte.is_public


async def test_geerbtes_recht_zaehlt_nicht_wenn_die_vererbung_aus_ist():
    """inherited=false schneidet die geerbte Liste ab -- gemessen kam sie danach
    leer zurueck. Bildet die Antwort sie trotzdem ab, darf sie nicht zaehlen."""
    instanz = Instanz(inherits=False, own=[], inherited=[
        _ace(EVERYONE, CONSUMER, typ="EVERYONE")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        rechte = await knoten.permissions.get()
    assert not rechte.is_public


async def test_allows_fragt_beide_listen():
    instanz = Instanz(own=[_ace("alice", "Coordinator")],
                      inherited=[_ace("bob", "Consumer")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        rechte = await knoten.permissions.get()
    assert rechte.allows("alice", "Coordinator")
    assert rechte.allows("bob", "Consumer")
    assert not rechte.allows("alice", "Consumer")
    assert not rechte.allows("carol", "Consumer")


# --- Schreiben ------------------------------------------------------------

async def test_grant_behaelt_die_uebrigen_eintraege():
    """Der wichtigste Test der Datei. Der POST ersetzt die lokale ACL -- wer
    nicht zusammenfuehrt, loescht beim Veroeffentlichen die Rechte anderer."""
    instanz = Instanz(own=[_ace("alice", "Coordinator")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        await knoten.permissions.grant("bob", CONSUMER)
    gesendet = {a["authority"]["authorityName"]
                for a in instanz.geschrieben[-1]["permissions"]}
    assert gesendet == {"alice", "bob"}


async def test_grant_behaelt_die_vererbung_bei():
    instanz = Instanz(inherits=True)
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        await knoten.permissions.grant("bob", CONSUMER)
    assert instanz.geschrieben[-1]["inherited"] is True


async def test_grant_ergaenzt_ein_recht_bei_bestehender_autoritaet():
    instanz = Instanz(own=[_ace("alice", "Consumer")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        await knoten.permissions.grant("alice", "Coordinator")
    eintrag = instanz.geschrieben[-1]["permissions"][0]
    assert sorted(eintrag["permissions"]) == ["Consumer", "Coordinator"]


async def test_grant_schreibt_nicht_wenn_das_recht_schon_steht():
    instanz = Instanz(own=[_ace("alice", "Consumer")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        geaendert = await knoten.permissions.grant("alice", CONSUMER)
    assert geaendert is False
    assert instanz.geschrieben == []


async def test_revoke_nimmt_nur_das_genannte_recht():
    instanz = Instanz(own=[_ace("alice", "Consumer", "Coordinator")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        await knoten.permissions.revoke("alice", "Coordinator")
    eintrag = instanz.geschrieben[-1]["permissions"][0]
    assert eintrag["permissions"] == ["Consumer"]


async def test_revoke_ohne_recht_entfernt_die_ganze_autoritaet():
    instanz = Instanz(own=[_ace("alice", "Consumer"), _ace("bob", "Consumer")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        await knoten.permissions.revoke("alice")
    uebrig = [a["authority"]["authorityName"]
              for a in instanz.geschrieben[-1]["permissions"]]
    assert uebrig == ["bob"]


async def test_revoke_laesst_einen_leeren_eintrag_nicht_stehen():
    instanz = Instanz(own=[_ace("alice", "Consumer")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        await knoten.permissions.revoke("alice", "Consumer")
    assert instanz.geschrieben[-1]["permissions"] == []


async def test_revoke_schreibt_nicht_wenn_nichts_zu_nehmen_ist():
    instanz = Instanz(own=[_ace("alice", "Consumer")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        geaendert = await knoten.permissions.revoke("bob", "Consumer")
    assert geaendert is False
    assert instanz.geschrieben == []


async def test_stiller_verlust_wird_gemeldet():
    """Gemessen: ein GROUP_-Name ohne Gruppe dahinter kommt mit HTTP 200 zurueck
    und steht danach nicht da. Genau der Fall, fuer den diese Bibliothek
    zurueckliest."""
    instanz = Instanz(taub=True)
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        with pytest.raises(SilentDropError) as fehler:
            await knoten.permissions.grant("GROUP_gibtesnicht", CONSUMER)
    assert "GROUP_gibtesnicht" in fehler.value.dropped


# --- Veroeffentlichen -----------------------------------------------------

async def test_publish_setzt_den_richtigen_autoritaetstyp():
    """GROUP_EVERYONE traegt den Typ EVERYONE, nicht GROUP -- der Name faengt
    mit GROUP_ an und verleitet zum falschen. Das Repositorium normalisiert den
    Typ zwar selbst (gemessen), aber was gesendet wird, soll stimmen."""
    instanz = Instanz()
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        await knoten.permissions.publish()
    eintrag = instanz.geschrieben[-1]["permissions"][-1]
    assert eintrag["authority"] == {"authorityName": EVERYONE,
                                    "authorityType": "EVERYONE"}
    assert eintrag["permissions"] == [CONSUMER]


async def test_publish_ist_wiederholbar():
    instanz = Instanz(own=[_ace(EVERYONE, CONSUMER, typ="EVERYONE")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        geaendert = await knoten.permissions.publish()
    assert geaendert is False
    assert instanz.geschrieben == []


async def test_publish_schreibt_nicht_wenn_schon_geerbt_oeffentlich():
    """Ein zweites Recht neben dem geerbten waere Rauschen -- und es spaeter zu
    entfernen wuerde nichts bewirken."""
    instanz = Instanz(inherited=[_ace(EVERYONE, CONSUMER, typ="EVERYONE")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        geaendert = await knoten.permissions.publish()
    assert geaendert is False
    assert instanz.geschrieben == []


async def test_unpublish_nimmt_das_eigene_recht_zurueck():
    instanz = Instanz(own=[_ace("alice", "Coordinator"),
                           _ace(EVERYONE, CONSUMER, typ="EVERYONE")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        geaendert = await knoten.permissions.unpublish()
    assert geaendert is True
    uebrig = [a["authority"]["authorityName"]
              for a in instanz.geschrieben[-1]["permissions"]]
    assert uebrig == ["alice"]


async def test_unpublish_ist_wiederholbar():
    instanz = Instanz(own=[])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        geaendert = await knoten.permissions.unpublish()
    assert geaendert is False


async def test_unpublish_meldet_wenn_die_vererbung_oeffentlich_haelt():
    """Gemessen: die lokale ACL zu leeren nimmt nichts zurueck, solange das
    Elternteil oeffentlich ist. ``False`` zurueckzugeben hiesse behaupten, der
    Knoten sei jetzt privat -- er ist es nicht."""
    instanz = Instanz(own=[], inherited=[_ace(EVERYONE, CONSUMER, typ="EVERYONE")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        with pytest.raises(ConflictError) as fehler:
            await knoten.permissions.unpublish()
    assert "geerbt" in str(fehler.value).lower() or "inherit" in str(fehler.value).lower()


# --- Formen ---------------------------------------------------------------

def test_ace_leitet_den_typ_aus_dem_namen_ab():
    assert Ace.for_authority(EVERYONE, CONSUMER).authority_type == "EVERYONE"
    assert Ace.for_authority("GROUP_lehrer", CONSUMER).authority_type == "GROUP"
    assert Ace.for_authority("ROLE_OWNER", "All").authority_type == "OWNER"
    assert Ace.for_authority("alice", CONSUMER).authority_type == "USER"


def test_ace_typ_laesst_sich_ueberschreiben():
    gesetzt = Ace.for_authority("x", CONSUMER, authority_type="GROUP")
    assert gesetzt.authority_type == "GROUP"


def test_permissions_ist_unveraenderlich():
    rechte = Permissions.from_response(_antwort())
    with pytest.raises(AttributeError):
        rechte.inherits = False  # type: ignore[misc]


async def test_revoke_schreibt_nicht_wenn_die_autoritaet_das_recht_nicht_hat():
    """Sie steht in der Liste, aber mit anderen Rechten. Ein Schreibvorgang
    waere ein Leerlauf, der wie eine Aenderung aussieht."""
    instanz = Instanz(own=[_ace("alice", "Coordinator")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        geaendert = await knoten.permissions.revoke("alice", CONSUMER)
    assert geaendert is False
    assert instanz.geschrieben == []


async def test_grant_ohne_recht_ist_ein_fehler():
    """Ein Aufruf ohne Recht kann nichts bewirken. Still nichts zu tun hiesse,
    einen Tippfehler als Erfolg zu melden."""
    instanz = Instanz()
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        with pytest.raises(ValueError, match="at least one permission"):
            await knoten.permissions.grant("alice")
    assert instanz.geschrieben == []


async def test_reprs_nennen_das_wesentliche():
    instanz = Instanz(own=[_ace(EVERYONE, CONSUMER, typ="EVERYONE")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        assert "n1" in repr(knoten.permissions)
        rechte = await knoten.permissions.get()
    assert "public=True" in repr(rechte)
    assert repr(rechte.own[0]) == f"Ace('{EVERYONE}', {CONSUMER})"
