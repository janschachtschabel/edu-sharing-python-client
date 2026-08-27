"""Fehlertypen und die Zuordnung einer HTTP-Antwort zu einem davon.

edu-sharing antwortet im Fehlerfall mit drei Feldern::

    {"error": "org.edu_sharing.restservices.DAOMissingException",
     "message": "InvalidNodeRefException: Node does not exist: ...",
     "stacktrace": "\\njava.lang.Exception: ...\\n\\tat org.edu_sharing...."}

``error`` traegt den Java-Klassennamen und ist die praezisere Kategorie -- der
HTTP-Status allein reicht nicht, wie ``ServerError`` unten zeigt.

Der ``stacktrace`` bleibt als Attribut erreichbar, taucht aber nie in ``str()``
auf: er enthaelt interne Klassenpfade und Zeilennummern, die in einer Meldung
nichts zu suchen haben, die eine Anwendung ihren Nutzenden zeigt.
"""

from __future__ import annotations

import json

__all__ = [
    "EduSharingError",
    "TransportError",
    "AuthenticationError",
    "PermissionDeniedError",
    "NotFoundError",
    "ValidationError",
    "ConflictError",
    "ServerError",
    "error_from_response",
]


class EduSharingError(Exception):
    """Basis aller Fehler dieser Bibliothek.

    Wer nicht unterscheiden will, faengt diesen Typ.

    Attribute:
        status: HTTP-Statuscode, oder ``None`` wenn die Anfrage den Server
            nie erreicht hat (siehe ``TransportError``).
        url: die angefragte URL.
        error_class: der Java-Klassenname aus dem Feld ``error``, sofern die
            Antwort JSON war.
        stacktrace: der Java-Stacktrace. Nur zum Debuggen -- nicht anzeigen.
    """

    def __init__(
        self,
        message: str,
        *,
        status: int | None = None,
        url: str | None = None,
        error_class: str | None = None,
        stacktrace: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.url = url
        self.error_class = error_class
        self.stacktrace = stacktrace


class TransportError(EduSharingError):
    """Die Anfrage hat den Server nie erreicht: Timeout, DNS, TLS, Verbindung.

    Abgegrenzt von ``ServerError``, weil der Unterschied fuer den Aufrufer
    zaehlt: hier ist unklar, ob etwas passiert ist. Ein Schreibvorgang, der in
    einen Timeout laeuft, kann trotzdem ausgefuehrt worden sein.
    """


class AuthenticationError(EduSharingError):
    """Nicht angemeldet, oder die Zugangsdaten stimmen nicht.

    Auf WLO-Instanzen gemessen: falsche Zugangsdaten geben ``401`` auf JEDEM
    Endpunkt -- es gibt keinen Rueckfall auf "nur oeffentlich lesen". Ein
    Tippfehler im Passwort legt damit die ganze Anwendung lahm, statt sie
    eingeschraenkt weiterlaufen zu lassen.
    """


class PermissionDeniedError(EduSharingError):
    """Angemeldet, aber ohne das noetige Recht.

    edu-sharing hat zwei Rechte-Ebenen: die ACL am Knoten und die
    Tool-Permissions am Konto. Beide landen hier.
    """


class NotFoundError(EduSharingError):
    """Der Knoten, die Sammlung oder der Endpunkt existiert nicht."""


class ValidationError(EduSharingError):
    """Das Repositorium hat die Anfrage abgelehnt (``DAOValidationException``).

    Typisch: ein Suchkriterium, das die angesprochene Query nicht kennt.
    """


class ConflictError(EduSharingError):
    """Der Vorgang kollidiert mit dem vorhandenen Zustand.

    Typisch: ein Name, den es unter demselben Elternknoten schon gibt.
    """


class ServerError(EduSharingError):
    """Ein echter Fehler auf der Gegenseite.

    Nur die 5xx, die nach Pruefung KEINE verkleidete Auth- oder Rechtefrage
    sind -- siehe ``error_from_response``.
    """


# Ein Gast auf einem geschuetzten Endpunkt bekommt HTTP 500, nicht 401.
# Gemessen an GET /iam/v1/people/-home-/-me-/preferences ohne Zugangsdaten:
#   500  {"error": "java.lang.Exception", "message": "Not allowed for guest user"}
# Der Status ist damit irrefuehrend, und die Verwechslung ist teuer: als
# ServerError wuerde der Transport es wiederholen -- dreimal dieselbe Anfrage,
# die nie gelingen kann, weil nur die Anmeldung fehlt.
_GUEST_HINT = "not allowed for guest"

# Dieselbe Verkleidung fuer Rechte: /rating/v1/ratings/.../history antwortet
# mit 500 NotAnAdminException.
_ADMIN_HINT = "notanadmin"


def _parse_body(body: str) -> tuple[str | None, str, str | None]:
    """Zerlege den Antwortkoerper in (error_class, message, stacktrace).

    Faellt auf ``(None, "", None)`` zurueck, wenn der Koerper kein JSON ist:
    ein 401 kommt leer, und ein Reverse-Proxy antwortet mit HTML.
    """
    if not body:
        return None, "", None
    try:
        data = json.loads(body)
    except (ValueError, TypeError):
        return None, "", None
    if not isinstance(data, dict):
        return None, "", None
    return (
        data.get("error") or None,
        str(data.get("message") or ""),
        data.get("stacktrace") or None,
    )


def _short(error_class: str | None) -> str:
    """``org.edu_sharing.restservices.DAOMissingException`` -> ``DAOMissingException``."""
    return error_class.rsplit(".", 1)[-1] if error_class else ""


def error_from_response(status: int, url: str, body: str) -> EduSharingError:
    """Baue aus einer Fehlerantwort den passenden Fehlertyp.

    Der HTTP-Status ist der erste Hinweis, aber nicht der letzte: bei 5xx
    entscheidet der Inhalt, ob wirklich der Server kaputt ist oder ob nur die
    Anmeldung beziehungsweise ein Recht fehlt.
    """
    error_class, message, stacktrace = _parse_body(body)

    if status >= 500:
        lowered = message.lower()
        if _GUEST_HINT in lowered:
            cls: type[EduSharingError] = AuthenticationError
        elif _ADMIN_HINT in (error_class or "").lower():
            cls = PermissionDeniedError
        else:
            cls = ServerError
    else:
        cls = {
            400: ValidationError,
            401: AuthenticationError,
            403: PermissionDeniedError,
            404: NotFoundError,
            409: ConflictError,
        }.get(status, EduSharingError)

    parts = [f"HTTP {status}"]
    if error_class:
        parts.append(_short(error_class))
    text = " ".join(parts)
    if message:
        text = f"{text}: {message}"

    return cls(
        text,
        status=status,
        url=url,
        error_class=error_class,
        stacktrace=stacktrace,
    )
