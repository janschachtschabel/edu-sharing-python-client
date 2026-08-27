"""Normalisierung der Repository-URL.

Die behandelten Eingabeformen sind keine erfundenen Randfaelle: es sind die
Formen, in denen Betreibende ihre Repository-Adresse tatsaechlich weitergeben
-- mal die blanke Domain, mal ein aus der REST-Doku kopierter Pfad.
"""

import pytest

from edusharing.errors import EduSharingError
from edusharing.urls import normalize_repository_url, path_segment, rest_base

HOST = "https://repository.staging.openeduhub.net"
FULL = f"{HOST}/edu-sharing"


@pytest.mark.parametrize("eingabe", [
    HOST,                                   # blanke Domain
    f"{HOST}/",                             # mit Schraegstrich
    FULL,                                   # schon vollstaendig
    f"{FULL}/",
    f"{FULL}//",                            # mehrfacher Schraegstrich
    f"{FULL}/rest",                         # aus der REST-Doku kopiert
    f"{FULL}/rest/",
    f"  {FULL}  ",                          # aus der Zwischenablage
    "repository.staging.openeduhub.net",    # ohne Protokoll
])
def test_alle_schreibweisen_ergeben_dieselbe_basis(eingabe):
    assert normalize_repository_url(eingabe) == FULL


def test_http_bleibt_http():
    """Lokale und interne Instanzen laufen ohne TLS. Ein erzwungenes Upgrade
    auf https wuerde sie unerreichbar machen."""
    assert normalize_repository_url("http://localhost:8080") == "http://localhost:8080/edu-sharing"


def test_pfad_unterhalb_von_edu_sharing_bleibt_erhalten():
    """Manche Instanzen liegen nicht auf der Wurzel."""
    assert normalize_repository_url("https://host.test/repo/edu-sharing") == \
        "https://host.test/repo/edu-sharing"


def test_rest_basis_wird_angehaengt():
    assert rest_base(FULL) == f"{FULL}/rest"


# --- Eingaben, die ein Konfigurationsfehler sind --------------------------

def test_leere_eingabe_wird_abgelehnt():
    """Sonst richtet sich die Anwendung stillschweigend gegen "https:///edu-sharing"."""
    with pytest.raises(EduSharingError):
        normalize_repository_url("")


def test_nur_leerzeichen_wird_abgelehnt():
    with pytest.raises(EduSharingError):
        normalize_repository_url("   ")


def test_deep_link_wird_abgelehnt():
    """Ein aus dem Browser kopierter Link auf eine Seite, nicht auf das
    Repositorium. Ohne Pruefung wuerde jeder Aufruf mit 404 enden, und die
    Ursache stuende nirgends."""
    with pytest.raises(EduSharingError, match="components"):
        normalize_repository_url(f"{FULL}/components/render/abc-123")


def test_doppeltes_edu_sharing_wird_abgelehnt():
    with pytest.raises(EduSharingError, match="edu-sharing"):
        normalize_repository_url(f"{FULL}/edu-sharing")


# --- Pfadsegmente ---------------------------------------------------------
#
# Diese Gruppe existiert wegen eines Audit-Befundes (F1, 27.08.2026): Bezeichner
# wurden unkodiert per f-String in Pfade gesetzt. Nachgewiesen war, dass eine
# node_id von "../../../admin/v1/applications" einen anderen Endpunkt erreicht
# und "abc?admin=1" das angehaengte "/metadata" verschluckt.
#
# Der Fall ist keine Theorie: in einem MCP-Server kommt die node_id aus dem
# Sprachmodell und damit aus Fremddaten.

def test_pfadsegment_kodiert_schraegstrich():
    """Ein Segment darf niemals eine Pfadgrenze ueberschreiten."""
    assert path_segment("a/b") == "a%2Fb"


def test_pfadsegment_kodiert_punkte_und_trenner():
    assert path_segment("../../admin") == "..%2F..%2Fadmin"
    assert path_segment("abc?admin=1") == "abc%3Fadmin%3D1"
    assert path_segment("abc#frag") == "abc%23frag"


def test_pfadsegment_laesst_harmlose_ids_unveraendert():
    """Gegenprobe: echte edu-sharing-IDs sind UUIDs und duerfen sich nicht
    aendern -- sonst bricht die Kodierung den Normalbetrieb."""
    uuid = "8f3c1e42-9b7a-4d21-bc55-0e6a1f2d3c47"
    assert path_segment(uuid) == uuid
    assert path_segment("-home-") == "-home-"
    assert path_segment("mds_oeh") == "mds_oeh"


def test_pfadsegment_kodiert_umlaute():
    assert path_segment("Bücher") == "B%C3%BCcher"


def test_pfadsegment_lehnt_leeres_ab():
    """Ein leeres Segment erzeugt einen doppelten Schraegstrich und damit einen
    voellig anderen Pfad."""
    with pytest.raises(EduSharingError):
        path_segment("")
