"""Suchen mit Labels statt URIs -- und ohne die Instanz vorauszusetzen.

    python docs/beispiele/02_suchen.py
    python docs/beispiele/02_suchen.py Photosynthese

Zeigt den Punkt, um den es dieser Bibliothek geht: dieselben drei Zeilen laufen
gegen jeden Metadatensatz, weil Filterwerte zur Laufzeit gegen *diese* Instanz
aufgeloest werden.
"""

import sys

# Die Windows-Konsole liefert sonst cp1252 und verstuemmelt Umlaute. Betrifft
# nur die Ausgabe dieses Beispiels -- die Bibliothek arbeitet durchgehend in
# UTF-8 und fasst stdout nicht an.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from edusharing import EduSharingError, Repository

STANDARD = "https://repository.staging.openeduhub.net"


def main(thema: str) -> int:
    with Repository(STANDARD, metadataset="mds_oeh") as repo:
        # Welche Metadatensaetze gibt es ueberhaupt? Die Wahl aendert, was
        # filterbar ist und was gefunden wird.
        print("Metadatensaetze dieser Instanz:")
        for satz in repo.metadatasets():
            marke = " <- benutzt" if satz.id == repo.metadataset else ""
            print(f"  {satz.id:<24} {satz.name}{marke}")

        # 'Biologie' ist ein Label. Auf die URI, die DIESE Instanz dafuer
        # fuehrt, uebersetzt die Bibliothek selbst.
        print(f"\nSuche: {thema!r}, eingegrenzt auf das Fach Biologie")
        ergebnis = repo.search(thema, fach="Biologie", limit=5,
                               facets=["ccm:educationalcontext"])

        # Konnte ein Filter nicht aufgeloest werden, ist das Ergebnis breiter
        # als angefragt -- das gehoert gesagt, nicht verschwiegen.
        for offen in ergebnis.unresolved:
            print(f"  ! {offen}")

        print(f"  {ergebnis.total} Treffer insgesamt, die ersten {len(ergebnis.hits)}:")
        for treffer in ergebnis.hits:
            faecher = ", ".join(treffer.labels("ccm:taxonid")) or "-"
            print(f"    {treffer.title}")
            print(f"      {faecher} | {treffer.url}")

        if ergebnis.facets:
            facette = ergebnis.facets[0]
            print(f"\n  Verteilung nach {facette.property}:")
            for wert in facette.values[:5]:
                print(f"    {wert.count:>5}x  {wert.value.rsplit('/', 1)[-1]}")
            if facette.truncated:
                print(f"    (gekuerzt -- {facette.other_count} weitere)")

        # Sammlungen brauchen beide Wege: bei manchen Suchwoertern haben sie
        # keinen einzigen Treffer gemeinsam.
        print(f"\nSammlungen zu {thema!r}:")
        sammlungen = repo.find_collections(thema, limit=5)
        for warnung in sammlungen.warnings:
            print(f"  ! {warnung}")
        for treffer in sammlungen.hits:
            print(f"    {treffer.title} -- {treffer.url}")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "Photosynthese"))
    except EduSharingError as exc:
        print(f"Fehlgeschlagen: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
