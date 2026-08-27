"""Suchen, aufbereiten, ans Sprachmodell geben.

    B_API_KEY=... python docs/beispiele/04_ki_bausteine.py [Thema]

Zeigt den Bogen, fuer den ``edusharing.agent`` gedacht ist: aus einer Suche
wird ein Modellkontext, der die Fundstellen behaelt, Fremdinhalt kennzeichnet
und ein Budget einhaelt. Ohne den b-api-Schluessel laeuft alles ausser dem
letzten Schritt.

Nichts hiervon ist MCP-spezifisch -- ein MCP-Server waere ein duenner Adapter
darueber.
"""

import asyncio
import sys

# Die Windows-Konsole liefert sonst cp1252 und verstuemmelt Umlaute.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import os

from edusharing import AsyncRepository, EduSharingError
from edusharing.agent import as_result, as_untrusted, format_results, is_safe_url
from edusharing.bapi import BildungsAPI

REPO = "https://repository.staging.openeduhub.net"


async def main(thema: str) -> int:
    async with AsyncRepository(REPO, metadataset="mds_oeh") as repo:
        # 1. Suchen -- als Werkzeug-Ergebnis, damit ein Fehler nicht den
        #    ganzen Durchlauf beendet, sondern eine Auskunft wird.
        ergebnis = await as_result(
            repo.search(thema, fach="Biologie", limit=5),
            format=lambda r: format_results(r, max_chars=1500),
        )
        if not ergebnis:
            print(f"Suche fehlgeschlagen ({ergebnis.error_type}): {ergebnis.error}")
            return 1

        print("--- Was das Modell zu sehen bekaeme ---")
        print(ergebnis.text)

        treffer = ergebnis.data
        print(f"\n--- Fundstellen bleiben erhalten: {len(treffer.hits)} ---")
        for hit in treffer.hits:
            print(f"  {hit.id}  {hit.url}")

        # 2. Quell-URLs pruefen, bevor irgendetwas sie abruft.
        print("\n--- Quell-URLs geprueft (SSRF) ---")
        for hit in treffer.hits[:3]:
            quelle = hit.source_url
            if quelle:
                zeichen = "ok " if is_safe_url(quelle) else "GESPERRT"
                print(f"  {zeichen} {quelle[:70]}")

        if not treffer.hits:
            print("\nKeine Treffer -- ohne Material kein Modellkontext.")
            return 0

        # 3. Fremdtext gekennzeichnet in den Prompt.
        material = "\n\n".join(
            as_untrusted(h.description or h.title, label=f"Material {h.id}")
            for h in treffer.hits[:3]
        )

        if not os.environ.get("B_API_KEY"):
            print("\n(B_API_KEY nicht gesetzt -- der Modellaufruf entfaellt.)")
            print(f"Der Prompt waere {len(material)} Zeichen lang.")
            return 0

        async with BildungsAPI.from_env() as llm:
            antwort = await llm.chat(
                f"Fasse in einem Satz zusammen, worum es in diesen Materialien "
                f"geht:\n\n{material}",
                system="Du antwortest knapp und auf Deutsch.",
                max_tokens=200,
            )
            print(f"\n--- Antwort von {llm.last_model} ---")
            print(antwort.strip())

    return 0


if __name__ == "__main__":
    thema = sys.argv[1] if len(sys.argv) > 1 else "Photosynthese"
    try:
        raise SystemExit(asyncio.run(main(thema)))
    except EduSharingError as exc:
        print(f"Fehlgeschlagen: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
