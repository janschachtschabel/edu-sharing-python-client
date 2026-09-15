#!/usr/bin/env python3
"""Haelt die Nachschlagedateien im Skill-Ordner gleich mit ``docs/``.

Der Skill ``.claude/skills/edu-sharing-python`` soll auch ausserhalb dieses
Repositoriums tragen -- kopiert nach ``~/.claude/skills/``, nach
``~/.agents/skills/`` oder als ZIP hochgeladen. Verweise nach ``../../../docs``
sind dort tot. Deshalb liegen unter ``reference/`` Kopien von REFERENCE und
FLOWS (je beide Sprachen) und aller Beispiele, inhaltsgleich (Zeilenenden
zaehlen wie fuer Git, siehe ``_inhalt``): eine Quelle je Inhalt. Die
Verweise zwischen ihnen bleiben gueltig, weil jede Kopie ihren relativen
Namen behaelt (``FLOWS.md`` -> ``examples/05_flow_search.py``).

Was nur der Skill hat -- ``SKILL.md``, ``SKILL.de.md``, die Fallen unter
``reference/TRAPS*.md`` --, fasst dieses Skript nicht an.

Aufruf::

    python scripts/sync_skill.py           # kopiert, entfernt verwaiste Beispiele
    python scripts/sync_skill.py --check   # meldet Abweichungen, Exit 1

``tests/test_skill_bundle.py`` verlangt die Gleichheit.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NACHSCHLAG = Path(".claude") / "skills" / "edu-sharing-python" / "reference"

#: Die Dokumente, die mitkommen. Beide Sprachen: der Skill ist zweisprachig.
DOKUMENTE = ("REFERENCE.md", "REFERENCE.de.md", "FLOWS.md", "FLOWS.de.md")


def paare(root: Path = ROOT) -> list[tuple[Path, Path]]:
    """``(Quelle, Kopie)`` fuer jede Datei, die in den Skill-Ordner gehoert."""
    docs, ziel = root / "docs", root / NACHSCHLAG
    gefunden = [(docs / name, ziel / name) for name in DOKUMENTE]
    gefunden += [(p, ziel / "examples" / p.name)
                 for p in sorted((docs / "examples").glob("*.py"))]
    return gefunden


def _verwaist(root: Path) -> list[Path]:
    """Beispiele im Skill-Ordner, die es in ``docs/examples`` nicht mehr gibt."""
    erwartet = {kopie for _, kopie in paare(root)}
    return sorted(p for p in (root / NACHSCHLAG / "examples").glob("*.py")
                  if p not in erwartet)


def _anzeige(pfad: Path, root: Path) -> str:
    return pfad.relative_to(root).as_posix()


def _inhalt(pfad: Path) -> bytes:
    """Der Inhalt, wie Git ihn sieht: ``.gitattributes`` legt ``eol=lf`` fest.

    Ein Arbeitsbaum, der vor dieser Regel ausgecheckt wurde, behaelt CRLF.
    Byte fuer Byte verglichen, meldete der Abgleich dort einen Unterschied,
    den Git nicht kennt.
    """
    return pfad.read_bytes().replace(b"\r\n", b"\n")


def abweichungen(root: Path = ROOT) -> list[str]:
    """Jede Kopie, die fehlt, veraltet oder verwaist ist -- leer, wenn alles gleich ist."""
    gefunden = []
    for quelle, kopie in paare(root):
        if not kopie.exists():
            gefunden.append(f"fehlt: {_anzeige(kopie, root)}")
        elif _inhalt(kopie) != _inhalt(quelle):
            gefunden.append(f"veraltet: {_anzeige(kopie, root)}")
    gefunden += [f"verwaist: {_anzeige(p, root)}" for p in _verwaist(root)]
    return gefunden


def synchronisiere(root: Path = ROOT) -> list[str]:
    """Stellt die Gleichheit her und sagt, was sich dafuer geaendert hat."""
    geaendert = []
    for quelle, kopie in paare(root):
        daten = _inhalt(quelle)
        if kopie.exists() and _inhalt(kopie) == daten:
            continue
        kopie.parent.mkdir(parents=True, exist_ok=True)
        kopie.write_bytes(daten)
        geaendert.append(f"kopiert: {_anzeige(kopie, root)}")
    for pfad in _verwaist(root):
        pfad.unlink()
        geaendert.append(f"entfernt: {_anzeige(pfad, root)}")
    return geaendert


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true",
                        help="nur pruefen; Exit 1, wenn eine Kopie abweicht")
    if parser.parse_args(argv).check:
        gefunden = abweichungen()
        for zeile in gefunden:
            print(zeile)
        if gefunden:
            print("-> python scripts/sync_skill.py behebt es")
        return 1 if gefunden else 0
    for zeile in synchronisiere() or ["alles gleich"]:
        print(zeile)
    return 0


if __name__ == "__main__":
    sys.exit(main())
