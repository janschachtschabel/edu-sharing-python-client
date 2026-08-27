"""Verbinden und nachsehen, womit man es zu tun hat.

    python docs/beispiele/01_verbinden.py
    python docs/beispiele/01_verbinden.py https://mein-repositorium.example/edu-sharing

Laeuft ohne Zugangsdaten. Mit ``EDU_SHARING_USER`` und ``EDU_SHARING_PASSWORD``
in der Umgebung meldet sich das Beispiel an und zeigt den Unterschied.
"""

import sys

from edusharing import BasicCredential, EduSharingError, Repository

STANDARD = "https://repository.staging.openeduhub.net"


def main(url: str) -> int:
    with Repository(url, auth=BasicCredential.from_env()) as repo:
        print(f"Repositorium: {repo.url}\n")

        # Was ist das fuer eine Instanz? Die Antwort entscheidet, was eine
        # Anwendung voraussetzen darf -- statt es zu raten.
        about = repo.about()
        print(f"  edu-sharing   {about.repository_version}")
        print(f"  Renderdienst  {about.renderservice_version}")
        print(f"  API           {about.api_version}")
        print(f"  Dienste       {len(about.services)}")
        if about.plugins:
            print(f"  Plugins       {', '.join(about.plugins)}")

        # Als wer laufe ich hier? Ohne diese Frage merkt eine Anwendung nicht,
        # dass sie als Gast arbeitet -- und stolpert spaeter an einer Stelle,
        # die mit der Ursache nichts zu tun hat.
        wer = repo.whoami()
        print()
        if wer.is_anonymous:
            print("  Angemeldet als: niemand (anonymer Zugriff)")
            print("  Fuer Schreibzugriff EDU_SHARING_USER und EDU_SHARING_PASSWORD setzen.")
        else:
            print(f"  Angemeldet als: {wer.display_name} ({wer.authority})")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else STANDARD))
    except EduSharingError as exc:
        # Fehler dieser Bibliothek sind erklaerte Fehler -- sie brauchen keinen
        # Traceback, um verstanden zu werden.
        print(f"Fehlgeschlagen: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
