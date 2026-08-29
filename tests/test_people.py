"""Gruppen und Mitgliedschaften.

Die Frage, die dahintersteht, ist immer dieselbe: **wer darf hier moderieren.**
Die Ideendatenbank beantwortet sie ueber diese drei Endpunkte.

Gemessen gegen Staging am 28.08.2026 mit einem gewoehnlichen Konto -- ohne
Administratorrechte:

* ``GET /iam/v1/people/-home-/-me-/memberships`` → ``{"groups": [...]}``. Je
  Gruppe stehen ``authorityName`` (``GROUP_ORG_AI-Skills``), ``groupName``
  (``ORG_AI-Skills``), ``signupMethod`` und ein ``profile`` mit
  ``displayName`` und ``groupType``.
* ``GET /iam/v1/groups/-home-/{g}`` → die Gruppe **in einer Huelle**:
  ``{"group": {...}}``.
* ``GET /iam/v1/groups/-home-/{g}/members`` → **500 AccessDeniedException**
  („User does not have permissions to manage this group"). Mitglieder sieht
  nur, wer die Gruppe verwaltet -- das ist ein Rechteproblem, kein Serverfehler,
  und wird als solches uebersetzt.
* ``POST /iam/v1/groups/-home-/{name}`` → **403**. Dieses Konto darf keine
  Gruppen anlegen.

**Was daraus folgt.** Die Form der Mitgliederliste und das Verhalten der
schreibenden Operationen konnten mit diesem Konto **nicht live geprueft**
werden. Beides ist hier gegen die gemessene Anfrageform und gegen das
OpenAPI-Modell getestet -- Methode, Pfad, Body, Antwortform. Dass die Instanz
sie annimmt, bleibt unbelegt. Die Docstrings sagen das ebenfalls.
"""

import httpx
import pytest

from edusharing import AsyncRepository
from edusharing.errors import PermissionDeniedError
from edusharing.people import Group, Member

REPO = "https://repo.test/edu-sharing"


def _gruppe(name: str, *, anzeige: str = "Anzeige", typ: str | None = "EDITORIAL",
            signup: str | None = "simple") -> dict:
    """Die gemessene Form einer Gruppe."""
    return {
        "authorityName": name,
        "authorityType": "GROUP",
        "groupName": name.removeprefix("GROUP_"),
        "signupMethod": signup,
        "profile": {"displayName": anzeige, "groupType": typ,
                    "groupEmail": None, "scopeType": None,
                    "customAttributes": None},
        "ref": {"repo": "local", "id": "g-1"},
        "organizations": None,
        "properties": {"ccm:group_signup_method": [signup] if signup else []},
    }


class Instanz:
    def __init__(self, *, gruppen: list[dict] | None = None,
                 mitglieder: list[dict] | None = None,
                 mitglieder_fehler: bool = False) -> None:
        self.gruppen = gruppen if gruppen is not None else [
            _gruppe("GROUP_ORG_AI-Skills", anzeige="AI-Compliance")]
        self.mitglieder = mitglieder if mitglieder is not None else [
            {"authorityName": "alice", "authorityType": "USER"},
            {"authorityName": "GROUP_unter", "authorityType": "GROUP"},
        ]
        self.mitglieder_fehler = mitglieder_fehler
        self.anfragen: list[httpx.Request] = []

    def handler(self, request: httpx.Request) -> httpx.Response:
        self.anfragen.append(request)
        pfad = request.url.path
        if pfad.endswith("/memberships"):
            return httpx.Response(200, json={"groups": self.gruppen})
        if "/members" in pfad:
            if self.mitglieder_fehler:
                # Gemessene Verkleidung: ein Rechteproblem als 500.
                return httpx.Response(500, json={
                    "error": "org.alfresco.repo.security.permissions."
                             "AccessDeniedException",
                    "message": "User does not have permissions to manage this group"})
            if request.method in ("PUT", "DELETE"):
                return httpx.Response(200, content=b"")
            return httpx.Response(200, json={
                "authorities": self.mitglieder,
                "pagination": {"total": len(self.mitglieder), "from": 0,
                               "count": len(self.mitglieder)}})
        if "/iam/v1/groups/" in pfad:
            name = pfad.rsplit("/", 1)[-1]
            if request.method == "POST":
                self.gruppen.append(_gruppe(name, anzeige="Neu", signup=None))
                return httpx.Response(200, json={"group": self.gruppen[-1]})
            if request.method == "DELETE":
                self.gruppen = [g for g in self.gruppen
                                if g["authorityName"] != name]
                return httpx.Response(200, content=b"")
            for g in self.gruppen:
                if g["authorityName"] == name:
                    return httpx.Response(200, json={"group": g})
            return httpx.Response(404, json={
                "error": "org.edu_sharing.restservices.DAOMissingException",
                "message": f"Group does not exist: {name}"})
        return httpx.Response(200, json={})

    def repo(self) -> AsyncRepository:
        return AsyncRepository(
            REPO, backoff_base=0.0,
            client=httpx.AsyncClient(transport=httpx.MockTransport(self.handler)))

    def letzte(self, methode: str) -> httpx.Request:
        for r in reversed(self.anfragen):
            if r.method == methode:
                return r
        raise AssertionError(f"keine {methode}-Anfrage")


# --- Lesen ----------------------------------------------------------------

async def test_eigene_mitgliedschaften():
    instanz = Instanz()
    async with instanz.repo() as repo:
        gruppen = await repo.people.memberships()
    assert [g.name for g in gruppen] == ["GROUP_ORG_AI-Skills"]
    assert gruppen[0].display_name == "AI-Compliance"
    assert gruppen[0].short_name == "ORG_AI-Skills"
    assert gruppen[0].type == "EDITORIAL"
    assert gruppen[0].signup == "simple"


async def test_ohne_mitgliedschaft_eine_leere_liste():
    instanz = Instanz(gruppen=[])
    async with instanz.repo() as repo:
        assert await repo.people.memberships() == []


async def test_eine_gruppe_kommt_aus_der_huelle():
    """Der Endpunkt antwortet mit {"group": {...}} -- wer die Huelle nicht
    auspackt, bekommt ein Objekt ohne Namen."""
    instanz = Instanz()
    async with instanz.repo() as repo:
        gruppe = await repo.people.group("GROUP_ORG_AI-Skills")
    assert gruppe.name == "GROUP_ORG_AI-Skills"
    assert gruppe.display_name == "AI-Compliance"


async def test_eine_unbekannte_gruppe_wird_gemeldet():
    from edusharing.errors import NotFoundError
    instanz = Instanz()
    async with instanz.repo() as repo:
        with pytest.raises(NotFoundError):
            await repo.people.group("GROUP_gibtesnicht")


async def test_mitglieder_trennen_menschen_von_untergruppen():
    """Eine Untergruppe als Person zu behandeln waere bei der Frage „wer darf
    moderieren" ein Fehler mit Folgen."""
    instanz = Instanz()
    async with instanz.repo() as repo:
        mitglieder = await repo.people.members("GROUP_ORG_AI-Skills")
    assert mitglieder == [Member(name="alice", is_group=False),
                          Member(name="GROUP_unter", is_group=True)]


async def test_die_mitgliederliste_holt_mehr_als_zehn():
    """Der Endpunkt setzt maxItems still auf 10 -- eine Gruppe mit fuenfzig
    Mitgliedern kaeme dann als Gruppe mit zehn zurueck."""
    instanz = Instanz()
    async with instanz.repo() as repo:
        await repo.people.members("GROUP_ORG_AI-Skills")
    assert int(instanz.letzte("GET").url.params["maxItems"]) >= 100


async def test_fehlende_verwaltungsrechte_sind_ein_rechteproblem():
    """Gemessen kommt das als 500 AccessDeniedException. Als Serverfehler
    wuerde der Transport es dreimal wiederholen."""
    instanz = Instanz(mitglieder_fehler=True)
    async with instanz.repo() as repo:
        with pytest.raises(PermissionDeniedError):
            await repo.people.members("GROUP_ORG_AI-Skills")


# --- Schreiben ------------------------------------------------------------
#
# Live nicht verifizierbar: das Testkonto bekommt 403. Geprueft wird die
# Anfrageform gegen das gemessene Modell.

async def test_gruppe_anlegen_schickt_ein_profil():
    instanz = Instanz(gruppen=[])
    async with instanz.repo() as repo:
        neu = await repo.people.create_group("GROUP_test", display_name="Test")
    post = instanz.letzte("POST")
    assert post.url.path.endswith("/iam/v1/groups/-home-/GROUP_test")
    import json
    assert json.loads(post.content)["displayName"] == "Test"
    assert neu.name == "GROUP_test"


async def test_ohne_anzeigenamen_steht_der_name_da():
    """Ein Profil ohne displayName ergaebe eine namenlose Gruppe in jeder
    Oberflaeche."""
    instanz = Instanz(gruppen=[])
    async with instanz.repo() as repo:
        await repo.people.create_group("GROUP_test")
    import json
    assert json.loads(instanz.letzte("POST").content)["displayName"] == "GROUP_test"


async def test_ein_elternteil_wird_als_parameter_geschickt():
    instanz = Instanz(gruppen=[])
    async with instanz.repo() as repo:
        await repo.people.create_group("GROUP_test", parent="GROUP_oben")
    assert instanz.letzte("POST").url.params["parent"] == "GROUP_oben"


async def test_mitglied_hinzufuegen_adressiert_es_im_pfad():
    instanz = Instanz()
    async with instanz.repo() as repo:
        await repo.people.add_member("GROUP_ORG_AI-Skills", "alice")
    put = instanz.letzte("PUT")
    assert put.url.path.endswith("/GROUP_ORG_AI-Skills/members/alice")


async def test_mitglied_entfernen_ebenso():
    instanz = Instanz()
    async with instanz.repo() as repo:
        await repo.people.remove_member("GROUP_ORG_AI-Skills", "alice")
    assert instanz.letzte("DELETE").url.path.endswith(
        "/GROUP_ORG_AI-Skills/members/alice")


async def test_gruppe_loeschen():
    instanz = Instanz()
    async with instanz.repo() as repo:
        await repo.people.delete_group("GROUP_ORG_AI-Skills")
        assert await repo.people.memberships() == []


async def test_sonderzeichen_im_gruppennamen_werden_kodiert():
    """Ein Gruppenname mit Schraegstrich wuerde sonst einen anderen Pfad
    adressieren -- derselbe Grund wie bei jeder anderen ID."""
    instanz = Instanz()
    async with instanz.repo() as repo:
        await repo.people.add_member("GROUP_a/b", "alice")
    assert "GROUP_a%2Fb" in instanz.letzte("PUT").url.raw_path.decode()


# --- Form -----------------------------------------------------------------

def test_group_ist_unveraenderlich():
    g = Group(name="GROUP_x", short_name="x", display_name="X",
              type=None, signup=None, raw={})
    with pytest.raises(AttributeError):
        g.name = "y"  # type: ignore[misc]


def test_group_repr_nennt_namen_und_anzeige():
    g = Group(name="GROUP_x", short_name="x", display_name="Die Gruppe",
              type=None, signup=None, raw={})
    assert repr(g) == "Group('GROUP_x', 'Die Gruppe')"


def test_member_repr():
    assert repr(Member(name="alice", is_group=False)) == "Member('alice')"
    assert repr(Member(name="GROUP_x", is_group=True)) == "Member('GROUP_x', Gruppe)"


async def test_der_gruppentyp_wird_mitgeschickt():
    import json
    instanz = Instanz(gruppen=[])
    async with instanz.repo() as repo:
        await repo.people.create_group("GROUP_test", type="EDITORIAL")
    assert json.loads(instanz.letzte("POST").content)["groupType"] == "EDITORIAL"


async def test_people_repr_nennt_die_instanz():
    instanz = Instanz()
    async with instanz.repo() as repo:
        assert REPO in repr(repo.people)
