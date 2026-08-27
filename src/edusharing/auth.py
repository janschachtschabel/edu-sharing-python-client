"""Zugangsdaten -- wer eine Anfrage stellt.

Eigenes Modul, weil hier eine Sicherheitsgrenze liegt und eine Sicherheitsgrenze
am Dateinamen auffindbar sein sollte. Zwei Eigenschaften traegt sie:

**Zugangsdaten sind Werte, kein globaler Zustand.** Jede Anfrage bekommt ihre
mitgegeben. Ein Dienst, der viele Nutzende bedient -- ein MCP-Server etwa --
kann sonst nicht sauber trennen, wer gerade fragt.

**Bearer-Token werden abgelehnt.** Die OpenAPI-Spezifikation von edu-sharing
deklariert genau zwei Verfahren, ``basicAuth`` und ``cookieAuth``. Ein
``Authorization: Bearer ...`` wird vom Server **ignoriert, nicht abgelehnt**:
die Anfrage sieht authentifiziert aus und laeuft als Gast. Wer damit schreibt,
bekommt 500 "Not allowed for guest user" an einer Stelle, die nichts mit dem
eigentlichen Problem zu tun hat.
"""

from __future__ import annotations

import base64
import os
from typing import Protocol, runtime_checkable

from .errors import EduSharingError

__all__ = ["Credential", "AnonymousCredential", "ANONYMOUS", "BasicCredential",
           "credential_from"]

ENV_USER = "EDU_SHARING_USER"
ENV_PASSWORD = "EDU_SHARING_PASSWORD"


@runtime_checkable
class Credential(Protocol):
    """Was der Transport von Zugangsdaten braucht."""

    def headers(self) -> dict[str, str]:
        """Die Kopfzeilen, die an das Repositorium gehen."""
        ...

    @property
    def is_anonymous(self) -> bool:
        """Ob ohne Anmeldung gearbeitet wird."""
        ...


class AnonymousCredential:
    """Kein Login. Gueltiger Betriebsfall -- vieles ist oeffentlich lesbar."""

    def headers(self) -> dict[str, str]:
        return {}

    @property
    def is_anonymous(self) -> bool:
        return True

    def __repr__(self) -> str:
        return "AnonymousCredential()"


ANONYMOUS: Credential = AnonymousCredential()


class BasicCredential:
    """Benutzername und Passwort nach RFC 7617.

    Das Passwort taucht weder in ``repr`` noch in ``str`` auf: beide landen in
    Tracebacks und Log-Zeilen.
    """

    __slots__ = ("_username", "_header")

    def __init__(self, username: str, password: str) -> None:
        self._username = username
        # UTF-8 festgelegt, nicht der Plattform ueberlassen: sonst haengt ein
        # Login mit Umlaut davon ab, auf welchem System der Client laeuft.
        raw = f"{username}:{password}".encode("utf-8")
        self._header = "Basic " + base64.b64encode(raw).decode("ascii")

    @classmethod
    def from_raw_header(cls, header: str) -> "BasicCredential":
        """Uebernimm einen fertigen ``Basic ...``-Header, ohne ihn zu zerlegen.

        Fuer Faelle, in denen die Zugangsdaten aus einer weitergereichten
        Anfrage stammen und im Klartext gar nicht vorliegen.
        """
        obj = cls.__new__(cls)
        object.__setattr__(obj, "_username", "<aus Header>")
        object.__setattr__(obj, "_header", header)
        return obj

    @classmethod
    def from_env(cls) -> "BasicCredential | None":
        """Lies ``EDU_SHARING_USER`` / ``EDU_SHARING_PASSWORD``.

        Returns:
            ``None``, wenn beide fehlen -- dann wird anonym gearbeitet.

        Raises:
            EduSharingError: wenn nur eines von beiden gesetzt ist. Anonym
                weiterzulaufen wuerde den Konfigurationsfehler verschleiern,
                und gemessen antwortet edu-sharing auf falsche Zugangsdaten
                ueberall mit 401 statt mit eingeschraenktem Zugriff.
        """
        user = os.environ.get(ENV_USER)
        password = os.environ.get(ENV_PASSWORD)
        if not user and not password:
            return None
        if not user or not password:
            fehlt = ENV_PASSWORD if user else ENV_USER
            raise EduSharingError(
                f"Unvollstaendige Zugangsdaten: {fehlt} fehlt. "
                f"Entweder {ENV_USER} und {ENV_PASSWORD} beide setzen oder beide weglassen."
            )
        return cls(user, password)

    def headers(self) -> dict[str, str]:
        return {"Authorization": self._header}

    @property
    def is_anonymous(self) -> bool:
        return False

    @property
    def username(self) -> str:
        return self._username

    def __repr__(self) -> str:
        return f"BasicCredential(username={self._username!r}, password=<verborgen>)"

    __str__ = __repr__


def credential_from(value: object) -> Credential:
    """Mache aus dem, was ein Aufrufer uebergibt, Zugangsdaten.

    Angenommen werden: ``None`` (anonym), ein ``(benutzer, passwort)``-Paar, ein
    fertiger ``Basic ...``-Header und ein bereits gebautes ``Credential``.

    Raises:
        EduSharingError: bei einem Bearer-Token oder einer unbekannten Form.
    """
    if value is None:
        return ANONYMOUS
    if isinstance(value, (AnonymousCredential, BasicCredential)):
        return value
    if isinstance(value, tuple) and len(value) == 2:
        user, password = value
        return BasicCredential(str(user), str(password))
    if isinstance(value, str):
        # Der Token selbst darf nicht in die Meldung -- er ist ein Geheimnis,
        # auch wenn er hier nutzlos ist.
        if value.lower().startswith("bearer "):
            raise EduSharingError(
                "Bearer-Token werden von edu-sharing nicht unterstuetzt. Die API "
                "kennt nur Basic-Auth und Session-Cookies, und sie IGNORIERT einen "
                "Bearer-Header, statt ihn abzulehnen -- die Anfrage liefe dann "
                "unbemerkt als Gast. Bitte Benutzername und Passwort uebergeben: "
                "Repository(url, auth=(benutzer, passwort))."
            )
        if value.lower().startswith("basic "):
            return BasicCredential.from_raw_header(value)
        raise EduSharingError(
            f"Unbekannte Form von Zugangsdaten: {value.split(' ', 1)[0]!r}. "
            "Erwartet wird ein (benutzer, passwort)-Paar oder ein 'Basic ...'-Header."
        )
    raise EduSharingError(
        f"Zugangsdaten koennen nicht aus {type(value).__name__} gebildet werden. "
        "Erwartet wird None, ein (benutzer, passwort)-Paar oder ein 'Basic ...'-Header."
    )
