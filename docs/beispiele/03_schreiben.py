"""Schreiben mit Rueckleseprobe -- und was ohne sie passiert.

    EDU_SHARING_USER=... EDU_SHARING_PASSWORD=... python docs/beispiele/03_schreiben.py

Legt einen eigenen Wegwerf-Ordner an, arbeitet ausschliesslich darin und
entfernt ihn am Ende wieder. Es wird nichts angefasst, was schon da war.

Vorgefuehrt wird der Befund, um den herum diese Bibliothek gebaut ist:
edu-sharing antwortet auf verlorene Schreibvorgaenge mit HTTP 200.
"""

import sys
import uuid

# Die Windows-Konsole liefert sonst cp1252 und verstuemmelt Umlaute.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from edusharing import EduSharingError, Repository, SilentDropError

# Diese Property kennt der Metadatensatz mds_oeh nicht -- ueber sie laesst sich
# der stille Verlust zeigen.
NICHT_IM_MDS = "ccm:oeh_collection_compendium_text"


def main() -> int:
    with Repository.from_env(metadataset="mds_oeh") as repo:
        wer = repo.whoami()
        if wer.is_anonymous:
            print("Ohne Anmeldung laesst sich nichts schreiben. Bitte "
                  "EDU_SHARING_USER und EDU_SHARING_PASSWORD setzen.", file=sys.stderr)
            return 1
        print(f"Angemeldet als {wer.display_name} ({wer.authority})\n")

        home = ((wer.raw.get("person") or {}).get("homeFolder") or {}).get("id")
        ordner = repo.create_node(
            home, name=f"beispiel-{uuid.uuid4().hex[:8]}", type="cm:folder",
            titel="Wegwerf-Ordner des Beispiels")
        print(f"Wegwerf-Ordner angelegt: {ordner.name}")

        try:
            node = repo.create_node(ordner.id, name="material.txt", titel="Erster Titel")
            print(f"  Knoten:  {node.url}")

            # 1. Eine Property, die der Metadatensatz kennt.
            node = node.update(titel="Geaenderter Titel",
                               beschreibung="Von der Bibliothek geschrieben")
            print(f"  Titel:   {node.get('cclom:title')}")

            # 2. Eine, die er nicht kennt -- der Server meldet 200 und speichert nichts.
            try:
                node.update(properties={NICHT_IM_MDS: "Dieser Text geht verloren"})
                print("  ! Kein Fehler -- das waere ueberraschend.")
            except SilentDropError as verlust:
                print(f"  Erkannt: {', '.join(verlust.dropped)} kam nicht an")
                print("           (der Server hatte 200 gemeldet)")

            # 3. Der Direktweg umgeht die Filterung -- bewusst, nicht automatisch.
            node = node.set_property(NICHT_IM_MDS, "Auf dem Direktweg gespeichert")
            print(f"  Direkt:  {node.get(NICHT_IM_MDS)}")

            # 4. Schlagworte ergaenzen, nicht ersetzen: die Liste ist geteilt.
            node = node.update(properties={"cclom:general_keyword": ["Von jemand anderem"]})
            node = node.add_keywords("Weimar (Ort)")
            print(f"  Schlagworte: {node.keywords}")

            # 5. Eine Datei anhaengen und zurueckholen.
            inhalt = "Ein Beispieltext mit Umlauten: Größe, Übung.\n".encode()
            node = node.content.upload(inhalt, filename="material.txt",
                                       mimetype="text/plain")
            zurueck = node.content.download()
            print(f"  Datei:   {node.content.size} Bytes, identisch: {zurueck == inhalt}")

        finally:
            ordner.delete()
            print("\nWegwerf-Ordner entfernt -- der Bestand ist wie vorgefunden.")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except EduSharingError as exc:
        print(f"Fehlgeschlagen: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
