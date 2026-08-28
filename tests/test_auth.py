"""Zugangsdaten.

Zwei Dinge muessen hier stimmen, und beide sind Sicherheitsfragen: dass ein
Bearer-Token nicht stillschweigend wirkungslos durchgereicht wird, und dass ein
Passwort nicht versehentlich in einem Log oder Traceback landet.
"""

import base64

import pytest

from edusharing.auth import ANONYMOUS, BasicCredential, Credential, credential_from
from edusharing.errors import EduSharingError


def test_anonym_sendet_keinen_auth_header():
    assert ANONYMOUS.headers() == {}
    assert ANONYMOUS.is_anonymous is True


def test_basic_erzeugt_den_korrekten_header():
    cred = BasicCredential("alice", "geheim")
    erwartet = base64.b64encode(b"alice:geheim").decode("ascii")
    assert cred.headers() == {"Authorization": f"Basic {erwartet}"}
    assert cred.is_anonymous is False


def test_umlaute_im_passwort_werden_utf8_kodiert():
    """Deutsche Passwoerter enthalten Umlaute. Die Kodierung muss festgelegt
    sein, sonst haengt der Login von der Plattform-Locale ab."""
    cred = BasicCredential("mueller", "Paßwortä")
    kopf = cred.headers()["Authorization"]
    roh = base64.b64decode(kopf.removeprefix("Basic "))
    assert roh == "mueller:Paßwortä".encode()


# --- Das Passwort darf nirgends auftauchen --------------------------------

def test_repr_zeigt_das_passwort_nicht():
    """repr() landet in Tracebacks, Log-Zeilen und Debugger-Ansichten."""
    cred = BasicCredential("alice", "streng-geheim-123")
    assert "streng-geheim-123" not in repr(cred)


def test_str_zeigt_das_passwort_nicht():
    cred = BasicCredential("alice", "streng-geheim-123")
    assert "streng-geheim-123" not in str(cred)


def test_repr_nennt_den_benutzernamen():
    """Ohne jede Auskunft waere die Fehlersuche unmoeglich -- der Benutzername
    ist kein Geheimnis, das Passwort schon."""
    assert "alice" in repr(BasicCredential("alice", "x"))


# --- Die Bearer-Falle -----------------------------------------------------

def test_bearer_wird_abgelehnt():
    """edu-sharing deklariert nur basicAuth und cookieAuth. Ein Bearer-Header
    wird IGNORIERT, nicht abgelehnt: die Anfrage sieht dann authentifiziert aus,
    laeuft aber als Gast. Stillschweigend als Gast zu arbeiten ist schlimmer als
    ein Fehler beim Start."""
    with pytest.raises(EduSharingError, match="Bearer"):
        credential_from("Bearer eyJhbGciOiJIUzI1NiJ9.abc")


def test_bearer_meldung_nennt_die_alternative():
    with pytest.raises(EduSharingError) as info:
        credential_from("Bearer abc")
    assert "Basic" in str(info.value)


def test_bearer_token_steht_nicht_in_der_meldung():
    """Ein Token ist ein Geheimnis, auch ein hier nutzloses."""
    with pytest.raises(EduSharingError) as info:
        credential_from("Bearer eyJhbGciOiJIUzI1NiJ9.streng-geheim")
    assert "streng-geheim" not in str(info.value)


# --- credential_from ------------------------------------------------------

def test_none_ergibt_anonym():
    assert credential_from(None) is ANONYMOUS


def test_tupel_ergibt_basic():
    cred = credential_from(("alice", "geheim"))
    assert isinstance(cred, BasicCredential)
    assert cred.headers()["Authorization"].startswith("Basic ")


def test_fertiger_basic_header_wird_uebernommen():
    """Wer den Header schon hat -- etwa aus einer weitergereichten Anfrage --
    soll ihn nicht erst zerlegen muessen."""
    roh = base64.b64encode(b"alice:geheim").decode("ascii")
    cred = credential_from(f"Basic {roh}")
    assert cred.headers() == {"Authorization": f"Basic {roh}"}


def test_credential_wird_unveraendert_durchgereicht():
    cred = BasicCredential("alice", "geheim")
    assert credential_from(cred) is cred


def test_unbekannte_form_wird_abgelehnt():
    with pytest.raises(EduSharingError):
        credential_from(12345)


def test_ein_passwort_im_falschen_slot_steht_nicht_in_der_meldung():
    """Audit A5. Der Schutz galt nur fuer Bearer-Token: die Meldung schnitt am
    ersten Leerzeichen ab, und ein Passwort hat keins. ``auth="PASSWORT-ENTFERNT"``
    -- die wahrscheinlichste Art, in diesen Zweig zu geraten -- landete damit
    woertlich in der Ausnahme und von dort in Traceback, Log und Modellkontext.
    ``BasicCredential.__repr__`` verhindert genau das an der Nachbartuer.
    """
    with pytest.raises(EduSharingError) as info:
        credential_from("PASSWORT-ENTFERNT")
    assert "PASSWORT-ENTFERNT" not in str(info.value)


def test_ein_eigenes_credential_wird_angenommen():
    """Audit A4. ``Credential`` ist ein ``runtime_checkable`` Protocol und wird
    aus dem Paket exportiert -- die Bibliothek wirbt damit als Erweiterungs-
    punkt. ``credential_from`` liess aber nur die zwei mitgelieferten Klassen
    zu, womit der Fall, fuer den das Modul geschrieben ist (ein Dienst mit
    vielen Nutzern, weitergereichte Sitzung), nicht bedienbar war.
    """
    class SitzungsCredential:
        def headers(self) -> dict[str, str]:
            return {"Cookie": "JSESSIONID=abc"}

        @property
        def is_anonymous(self) -> bool:
            return False

    eigenes = SitzungsCredential()
    assert isinstance(eigenes, Credential), "das Protocol sagt ja"
    assert credential_from(eigenes) is eigenes, "die Bibliothek muss auch ja sagen"


def test_ein_string_geht_weiter_den_string_weg():
    """Gegenprobe zu A4: ``str`` erfuellt das Protocol nicht, aber die Pruefung
    darf den Bearer-Zweig auch nicht ueberholen."""
    with pytest.raises(EduSharingError) as info:
        credential_from("Bearer abc")
    assert "Bearer" in str(info.value)


# --- from_env -------------------------------------------------------------

def test_from_env_liest_benutzer_und_passwort(monkeypatch):
    monkeypatch.setenv("EDU_SHARING_USER", "alice")
    monkeypatch.setenv("EDU_SHARING_PASSWORD", "geheim")
    cred = BasicCredential.from_env()
    assert cred is not None
    assert cred.headers() == {
        "Authorization": "Basic " + base64.b64encode(b"alice:geheim").decode("ascii")
    }


def test_from_env_ohne_variablen_ergibt_none(monkeypatch):
    """Kein Zugangsdaten-Paar in der Umgebung heisst anonym, nicht Absturz --
    oeffentliches Lesen ist ein gueltiger Betriebsfall."""
    monkeypatch.delenv("EDU_SHARING_USER", raising=False)
    monkeypatch.delenv("EDU_SHARING_PASSWORD", raising=False)
    assert BasicCredential.from_env() is None


def test_from_env_mit_halbem_paar_wird_abgelehnt(monkeypatch):
    """Benutzername ohne Passwort ist ein Konfigurationsfehler. Anonym
    weiterzulaufen wuerde ihn verschleiern -- und gemessen gibt edu-sharing
    auf falsche Zugangsdaten ueberall 401, nicht eingeschraenkten Zugriff."""
    monkeypatch.setenv("EDU_SHARING_USER", "alice")
    monkeypatch.delenv("EDU_SHARING_PASSWORD", raising=False)
    with pytest.raises(EduSharingError):
        BasicCredential.from_env()
