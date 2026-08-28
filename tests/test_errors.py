"""Fehler-Mapping.

Die Erwartungen stammen aus Messungen gegen edu-sharing 11.0 (Staging,
27.08.2026), nicht aus der Implementierung. Jeder Testfall nennt die Messung,
die ihn begruendet.
"""

import pytest

from edusharing.errors import (
    AuthenticationError,
    ConflictError,
    EduSharingError,
    NotFoundError,
    PermissionDeniedError,
    ServerError,
    ValidationError,
    error_from_response,
)

URL = "https://repo.example.test/edu-sharing/rest/node/v1/nodes/-home-/x/metadata"


def _body(error_class: str, message: str) -> str:
    """Die Antwortform von edu-sharing: error / message / stacktrace."""
    import json

    return json.dumps({
        "error": error_class,
        "message": message,
        "stacktrace": "\njava.lang.Exception: ...\n\tat org.edu_sharing.Intern(Foo.java:1)\n",
    })


# --- Status-Mapping -------------------------------------------------------

def test_401_ohne_body_ist_authentifizierungsfehler():
    """Gemessen: falsche Zugangsdaten -> 401 mit LEEREM Body (kein JSON).

    Der Parser darf daran nicht scheitern.
    """
    exc = error_from_response(401, URL, "")
    assert isinstance(exc, AuthenticationError)


def test_404_ist_nicht_gefunden():
    """Gemessen: unbekannte Node-ID -> 404 DAOMissingException."""
    exc = error_from_response(
        404, URL, _body("org.edu_sharing.restservices.DAOMissingException",
                        "InvalidNodeRefException: Node does not exist"))
    assert isinstance(exc, NotFoundError)


def test_403_ist_rechteproblem():
    """Gemessen: comments lesen ohne Comment-Permission -> 403 DAOSecurityException."""
    exc = error_from_response(
        403, URL, _body("org.edu_sharing.restservices.DAOSecurityException",
                        "InsufficientPermissionException: No permission"))
    assert isinstance(exc, PermissionDeniedError)


def test_400_ist_validierungsfehler():
    """Gemessen: unbekanntes Kriterium in ngsearch -> 400 DAOValidationException."""
    exc = error_from_response(
        400, URL, _body("org.edu_sharing.restservices.DAOValidationException",
                        "Could not find parameter virtual:parent_recursive"))
    assert isinstance(exc, ValidationError)


def test_409_ist_konflikt():
    """Aus der Praxis: addReference auf eine bereits vorhandene Referenz."""
    exc = error_from_response(
        409, URL, _body("org.edu_sharing.restservices.DAODuplicateNodeNameException",
                        "DuplicateChildNodeNameException"))
    assert isinstance(exc, ConflictError)


def test_echter_500_bleibt_serverfehler():
    exc = error_from_response(
        500, URL, _body("java.lang.NullPointerException", "Cannot invoke NodeRef.getId()"))
    assert isinstance(exc, ServerError)
    assert not isinstance(exc, AuthenticationError)


# --- Der Kernfall: fehlende Auth kommt als 500 ----------------------------

def test_500_not_allowed_for_guest_ist_authentifizierungsfehler():
    """Gemessen: GET /iam/v1/people/-home-/-me-/preferences ohne Auth
    antwortet mit **HTTP 500**, nicht 401:

        {"error": "java.lang.Exception", "message": "Not allowed for guest user"}

    Wer nur den Status liest, meldet einen Serverfehler und empfiehlt einen
    Wiederholungsversuch -- dabei fehlt schlicht die Anmeldung. Ein Retry
    darauf ist zwecklos und belastet das Repositorium.
    """
    exc = error_from_response(
        500, URL, _body("java.lang.Exception", "Not allowed for guest user"))
    assert isinstance(exc, AuthenticationError)


def test_500_node_does_not_exist_ist_ein_verstecktes_404():
    """Gemessen am 28.08.2026: /usage/v1/usages/node/{id}/collections antwortet
    fuer einen Knoten, den es nicht gibt, mit **500** -- waehrend der
    Knotenendpunkt fuer dieselbe ID ordentlich 404 sagt.

    Der Unterschied ist teuer: als Serverfehler wiederholt der Transport die
    Anfrage dreimal, und der Aufrufer, der NotFoundError abfaengt, sieht sie
    nicht. Der Suchindex haelt auf Staging Knoten, die es nicht mehr gibt --
    gemessen 4 von 25 -- also ist das kein Randfall."""
    fehler = error_from_response(
        500, URL, _body("org.edu_sharing.restservices.DAOException",
                        "org.edu_sharing.service.usage.UsageException: Node does "
                        "not exist: workspace://SpacesStore/1f71f84a"))
    assert isinstance(fehler, NotFoundError)


def test_ein_500_mit_anderem_daoexception_bleibt_serverfehler():
    """Die Gegenprobe: nicht jede DAOException ist ein fehlender Knoten."""
    fehler = error_from_response(
        500, URL, _body("org.edu_sharing.restservices.DAOException",
                        "java.lang.UnsupportedOperationException: Can not find "
                        "Quatschrecht"))
    assert isinstance(fehler, ServerError)


def test_500_access_is_denied_ist_ein_rechteproblem():
    """Gemessen am 28.08.2026: /node/v1/nodes/-home-/{id}/parents antwortet fuer
    fremdes Material mit **500 AccessDeniedException**, waehrend derselbe
    Endpunkt am eigenen Knoten ordentlich 403 sagt.

    Dieselbe teure Verwechslung wie beim Gastzugang: als Serverfehler wiederholt
    der Transport die Anfrage dreimal, obwohl sie nie gelingen kann."""
    fehler = error_from_response(
        500, URL, _body("org.alfresco.repo.security.permissions.AccessDeniedException",
                        "Access is denied."))
    assert isinstance(fehler, PermissionDeniedError)


def test_500_not_an_admin_ist_rechteproblem():
    """Gemessen (Skill wlo-edu-sharing-api): /rating/v1/ratings/.../history
    antwortet 500 NotAnAdminException. Auch das ist kein Serverfehler."""
    exc = error_from_response(
        500, URL, _body("org.edu_sharing.restservices.NotAnAdminException", "not an admin"))
    assert isinstance(exc, PermissionDeniedError)


# --- Was die Fehlermeldung zeigen darf ------------------------------------

def test_meldung_enthaelt_keinen_stacktrace():
    """edu-sharing liefert den vollen Java-Stacktrace mit internen Pfaden mit.
    Der gehoert nicht in die Meldung, die eine Anwendung anzeigt."""
    exc = error_from_response(
        404, URL, _body("org.edu_sharing.restservices.DAOMissingException", "Node does not exist"))
    text = str(exc)
    assert "org.edu_sharing.Intern" not in text
    assert "\tat " not in text


def test_meldung_nennt_status_und_ursache():
    exc = error_from_response(
        404, URL, _body("org.edu_sharing.restservices.DAOMissingException", "Node does not exist"))
    text = str(exc)
    assert "404" in text
    assert "Node does not exist" in text
    # Der Java-Klassenname ist die praezisere Kategorie -- er gehoert in die Meldung.
    assert "DAOMissingException" in text


def test_stacktrace_bleibt_zum_debuggen_erreichbar():
    exc = error_from_response(
        404, URL, _body("org.edu_sharing.restservices.DAOMissingException", "Node does not exist"))
    assert exc.stacktrace is not None
    assert "org.edu_sharing.Intern" in exc.stacktrace


def test_nicht_json_body_stuerzt_nicht_ab():
    """Manche Fehler kommen als HTML (Reverse-Proxy) oder leer zurueck."""
    exc = error_from_response(502, URL, "<html><body>error code: 522</body></html>")
    assert isinstance(exc, ServerError)
    assert exc.error_class is None


def test_attribute_sind_gesetzt():
    exc = error_from_response(
        400, URL, _body("org.edu_sharing.restservices.DAOValidationException", "kaputt"))
    assert exc.status == 400
    assert exc.url == URL
    assert exc.error_class == "org.edu_sharing.restservices.DAOValidationException"


@pytest.mark.parametrize("status", [400, 401, 403, 404, 409, 500, 502])
def test_alles_erbt_von_edusharingerror(status):
    """Ein Aufrufer kann pauschal EduSharingError fangen."""
    assert isinstance(error_from_response(status, URL, ""), EduSharingError)
