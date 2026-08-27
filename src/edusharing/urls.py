"""Aus einer Adresse, wie Menschen sie weitergeben, eine belastbare Basis-URL.

Betreibende nennen ihr Repositorium mal als blanke Domain, mal mit ``/edu-sharing``,
mal mit dem ``/rest`` aus der API-Dokumentation dahinter. Alle diese Formen meinen
dasselbe, also duerfen sie alle funktionieren.

Zwei Formen meinen es NICHT und werden abgelehnt statt stillschweigend geraten:
ein Deep-Link auf eine Seite und ein doppeltes ``/edu-sharing``. Beide fuehren
sonst dazu, dass jeder einzelne Aufruf mit 404 endet, ohne dass irgendwo stuende,
warum.
"""

from __future__ import annotations

import re

from .errors import EduSharingError

__all__ = ["normalize_repository_url", "rest_base"]

_APP_SEGMENT = "/edu-sharing"


def normalize_repository_url(raw: str) -> str:
    """Normalisiere eine Repository-Adresse zu ``<schema>://<host>[/pfad]/edu-sharing``.

    Das Ergebnis ist die Frontend-Basis, nicht die REST-Basis: aus ihr leiten
    sich sowohl ``/rest/...`` als auch die Ansichts-URLs ``/components/...`` ab.

    Raises:
        EduSharingError: bei leerer Eingabe, einem Deep-Link oder einem
            doppelten ``/edu-sharing``.
    """
    url = (raw or "").strip()
    if not url:
        raise EduSharingError(
            "Keine Repository-URL angegeben. Erwartet wird etwas wie "
            "'https://repository.staging.openeduhub.net'."
        )

    url = url.rstrip("/")
    # Das /rest haengen wir selbst an; wer es mitliefert, bekaeme sonst /rest/rest.
    url = re.sub(r"/rest$", "", url, flags=re.IGNORECASE).rstrip("/")

    if not re.match(r"^https?://", url, flags=re.IGNORECASE):
        url = f"https://{url}"

    if re.search(r"/components(/|$)", url, flags=re.IGNORECASE):
        raise EduSharingError(
            f"Die URL zeigt auf eine Seite, nicht auf das Repositorium: {raw!r}. "
            "Erwartet wird die Basis, also alles bis einschliesslich '/edu-sharing'."
        )

    # Lookahead statt Gruppe, damit "/edu-sharing/edu-sharing" als zwei Treffer zaehlt.
    count = len(re.findall(r"/edu-sharing(?=/|$)", url, flags=re.IGNORECASE))
    if count > 1:
        raise EduSharingError(
            f"Die URL enthaelt '/edu-sharing' mehrfach: {raw!r}."
        )
    if count == 0:
        url += _APP_SEGMENT

    return url


def rest_base(repository_url: str) -> str:
    """Die REST-Wurzel zu einer normalisierten Repository-URL."""
    return f"{repository_url}/rest"
