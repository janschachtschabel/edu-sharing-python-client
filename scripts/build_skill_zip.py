#!/usr/bin/env python3
"""Baut die ZIP des Skills fuer den Upload zu claude.ai.

claude.ai nimmt einen Skill als ZIP, deren Wurzel der Skill-Ordner ist, und
verlangt eine ``description`` von hoechstens 200 Zeichen (Hilfe-Artikel
12512198, abgerufen am 11.09.2026). Claude Code erlaubt 1536, die Plattform
1024: der Einstieg im Repositorium behaelt die lange Fassung mit ihren
Ausloesern, und die ZIP traegt deren **ersten Satz**. Alles andere ist der
Ordner, wie er im Repositorium liegt -- eine Quelle, nichts von Hand gepflegt.

Was dabei nicht geprueft ist, weil es niemand hier pruefen kann: der Upload
selbst. Die Hilfe nennt die Datei an einer Stelle ``skill.md``, die
Plattform-Doku ``SKILL.md``; die ZIP folgt der Plattform.

Aufruf::

    python scripts/build_skill_zip.py        # schreibt dist/edu-sharing-python.zip

``tests/test_skill_bundle.py`` prueft Wurzel, Inhalt, Beschreibung und dass
zwei Laeufe dieselben Bytes ergeben.
"""

from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / ".claude" / "skills" / "edu-sharing-python"
ZIEL = ROOT / "dist" / "edu-sharing-python.zip"

#: Die Grenze von claude.ai fuer die Beschreibung.
GRENZE = 200

#: Ein fester Zeitstempel fuer jeden Eintrag: sonst sieht jede ZIP neu aus,
#: auch wenn sich nichts geaendert hat. 1980 ist der frueheste, den ZIP kennt.
ZEITPUNKT = (1980, 1, 1, 0, 0, 0)

_BESCHREIBUNG = re.compile(r"^description: (.+)$", re.M)


def kurzbeschreibung(beschreibung: str) -> str:
    """Der erste Satz -- oder ein Fehler, wenn er die Grenze sprengt.

    Abschneiden hiesse, eine Beschreibung mitten im Wort auszuliefern, die
    ein Modell dann fuer die ganze haelt.
    """
    satz = beschreibung.split(". ", 1)[0].rstrip(".") + "."
    if len(satz) > GRENZE:
        raise ValueError(f"Der erste Satz der description hat {len(satz)} Zeichen, "
                         f"claude.ai nimmt hoechstens {GRENZE}: kuerzen in SKILL.md.")
    return satz


def mit_kurzbeschreibung(skill_md: str) -> str:
    """``SKILL.md`` mit dem ersten Satz als ``description`` -- sonst unveraendert."""
    treffer = _BESCHREIBUNG.search(skill_md)
    if treffer is None:
        raise ValueError("SKILL.md hat keine einzeilige description in der Frontmatter.")
    kurz = kurzbeschreibung(treffer.group(1))
    return skill_md[:treffer.start(1)] + kurz + skill_md[treffer.end(1):]


def dateien(skill: Path = SKILL) -> list[Path]:
    """Jede Datei des Skill-Ordners, ohne Bytecode -- sortiert nach dem Pfad als
    Text: Windows vergleicht ``Path`` ohne Gross- und Kleinschreibung, Linux
    mit, und dieselbe ZIP soll auf beiden dieselben Bytes haben."""
    return sorted((p for p in skill.rglob("*")
                   if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"),
                  key=lambda p: p.relative_to(skill).as_posix())


def baue(ziel: Path = ZIEL, skill: Path = SKILL) -> Path:
    """Schreibt die ZIP und gibt ihren Pfad zurueck.

    Zeilenenden werden LF, wie Git sie fuehrt (``.gitattributes``): ein
    Arbeitsbaum mit CRLF soll keine andere ZIP ergeben als einer mit LF.
    """
    ziel.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ziel, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for pfad in dateien(skill):
            inhalt = pfad.read_bytes().replace(b"\r\n", b"\n")
            if pfad == skill / "SKILL.md":
                inhalt = mit_kurzbeschreibung(inhalt.decode("utf-8")).encode("utf-8")
            eintrag = zipfile.ZipInfo(f"{skill.name}/{pfad.relative_to(skill).as_posix()}",
                                      date_time=ZEITPUNKT)
            eintrag.compress_type = zipfile.ZIP_DEFLATED
            eintrag.external_attr = 0o644 << 16
            z.writestr(eintrag, inhalt)
    return ziel


def main() -> int:
    try:
        ziel = baue()
    except ValueError as fehler:
        print(fehler, file=sys.stderr)
        return 1
    with zipfile.ZipFile(ziel) as z:
        anzahl = len(z.namelist())
    print(f"{ziel.relative_to(ROOT).as_posix()}: {anzahl} Dateien, {ziel.stat().st_size} Bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
