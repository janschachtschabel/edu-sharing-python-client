"""Pruefen, ob eine URL abgerufen werden darf.

Ein Dienst, der Repositoriums-Inhalte an ein Sprachmodell weiterreicht, holt
frueher oder spaeter eine URL, die aus Fremddaten stammt: ``ccm:wwwurl`` eines
beliebigen Datensatzes, ein Link aus einem Beschreibungstext. Zeigt die auf
``localhost`` oder in ein internes Netz, ruft der Dienst sie mit **seinen**
Netzrechten ab -- und wird zum Werkzeug (Server-Side Request Forgery).

Geprueft wird ohne Netzzugriff: Schema, Form, und bei IP-Literalen der Bereich.
Die Bereichspruefung nutzt ``ipaddress`` aus der Standardbibliothek statt
selbstgebauter Praefixvergleiche -- die sind die uebliche Fehlerquelle
(``172.16.0.0/12`` reicht nur bis ``172.31``, nicht bis ``172.255``).

**Grenze, die eine Anwendung kennen muss:** ein *Name* wird hier nicht
aufgeloest. ``interner-dienst.example.com`` kann auf ``10.0.0.5`` zeigen und
kommt trotzdem durch. Wer das ausschliessen muss, prueft die Adresse nach der
Aufloesung erneut oder setzt einen ausgehenden Proxy davor. Eine Aufloesung an
dieser Stelle waere ohnehin nur Scheinsicherheit: zwischen Pruefung und Abruf
kann sich die Antwort aendern (DNS-Rebinding).
"""

from __future__ import annotations

import ipaddress
from urllib.parse import urlsplit

from ..errors import EduSharingError

__all__ = ["UnsafeUrlError", "is_safe_url", "check_url"]

ERLAUBTE_SCHEMATA = frozenset({"http", "https"})

#: Namen und Endungen, die per Konvention nicht ins oeffentliche Netz zeigen.
#: Ein IP-Literal faengt bereits die Bereichspruefung ab; das hier greift fuer
#: Namen, die gar nicht erst aufgeloest werden sollen.
GESPERRTE_NAMEN = frozenset({"localhost"})
GESPERRTE_ENDUNGEN = (".local", ".internal", ".localhost", ".home.arpa")


class UnsafeUrlError(EduSharingError):
    """Die URL darf nicht abgerufen werden."""


def _grund(url: str) -> str | None:
    """Der Grund, warum ``url`` nicht abgerufen werden darf -- oder ``None``."""
    if not url or not url.strip():
        return "leere Adresse"

    try:
        teile = urlsplit(url.strip())
    except ValueError as exc:
        return f"nicht lesbar ({exc})"

    if teile.scheme.lower() not in ERLAUBTE_SCHEMATA:
        return f"Schema {teile.scheme or '(keines)'!r} -- erlaubt sind nur http und https"

    # Zugangsdaten in der URL sind ein bekannter Weg, Pruefungen zu verwirren:
    # manche Parser lesen den Host anders als der spaetere Abruf.
    if "@" in teile.netloc:
        return "die Adresse enthaelt Zugangsdaten (user:pass@host)"

    try:
        host = teile.hostname
    except ValueError as exc:
        return f"Host nicht lesbar ({exc})"
    if not host:
        return "kein Host"

    host = host.lower().rstrip(".")
    if host in GESPERRTE_NAMEN or host.endswith(GESPERRTE_ENDUNGEN):
        return f"{host!r} ist ein lokaler Name"

    try:
        adresse = ipaddress.ip_address(host)
    except ValueError:
        # Kein IP-Literal, sondern ein Name -- siehe Modul-Docstring.
        return None

    if adresse.is_loopback:
        return f"{host} ist eine lokale Adresse (Loopback)"
    if adresse.is_link_local:
        # 169.254.169.254 ist der Metadaten-Dienst der meisten Cloud-Anbieter
        # und damit das lohnendste einzelne Ziel eines SSRF-Angriffs.
        return f"{host} ist eine Link-Local-Adresse"
    if adresse.is_private or adresse.is_reserved or adresse.is_multicast:
        return f"{host} ist eine private oder reservierte Adresse"
    return None


def is_safe_url(url: str) -> bool:
    """Ob ``url`` abgerufen werden darf.

    Im Zweifel ``False``: eine unlesbare Adresse gilt als unsicher.
    """
    return _grund(url) is None


def check_url(url: str) -> str:
    """Gib ``url`` zurueck, wenn sie abgerufen werden darf.

    Raises:
        UnsafeUrlError: sonst, mit dem Grund in der Meldung.
    """
    grund = _grund(url)
    if grund is not None:
        raise UnsafeUrlError(f"Adresse nicht abrufbar: {url!r} -- {grund}.")
    return url
