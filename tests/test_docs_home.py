"""Wohin die Dokumente jemanden schicken -- und ob es dieselbe Stelle ist.

Das Audit vom 20.09.2026 fand das Projekt auf zwei Repositorien verteilt: die
beiden READMEs liessen von ``openeduhub`` installieren, waehrend
``pyproject.toml``, ``SECURITY.md`` und der Skill auf
``janschachtschabel`` zeigten. Wer von dem einen installierte und dem anderen
eine Luecke meldete, meldete sie woanders hin (Audit DOC-20-2).

Und die READMEs druckten ``@v0.2.0`` fuer ein Repositorium ohne einen einzigen
Tag -- vier Befehle, die bei jedem scheitern, der sie ausfuehrt
(``git ls-remote --tags`` gemessen: leer; Audit DOC-20-1).

Gehalten wird hier nur, was jemandem sagt, was er *jetzt* tun soll:
Installationsbefehle, der Meldeweg, die Paketmetadaten. Die Geschichte --
Audits, Plaene, die Vergleichslinks des Changelogs -- zeigt weiter dorthin, wo
sie liegt; ein Link auf eine vergangene Pruefung ist keine Anweisung.
"""

import re
import tomllib
from pathlib import Path

WURZEL = Path(__file__).resolve().parents[1]

#: Das veroeffentlichte Repositorium. Entschieden am 20.09.2026.
HEIMAT = "openeduhub"

#: Dateien, die jemandem sagen, was zu tun ist.
ANWEISEND = [
    "README.md", "README.de.md", "SECURITY.md", "CONTRIBUTING.md",
    ".claude/skills/edu-sharing-python/SKILL.md",
    ".claude/skills/edu-sharing-python/SKILL.de.md",
]

_BESITZER = re.compile(r"github\.com/([A-Za-z0-9_.-]+)/edu-sharing-python-client")


def _zeilen(rel: str) -> list[tuple[int, str]]:
    text = (WURZEL / rel).read_text(encoding="utf-8")
    return list(enumerate(text.splitlines(), start=1))


def test_jeder_installationsbefehl_nennt_die_heimat():
    """``pip install`` und ``uv pip install`` holen von genau einer Stelle."""
    falsch = [
        f"{rel}:{nummer}: {zeile.strip()}"
        for rel in ANWEISEND for nummer, zeile in _zeilen(rel)
        if "pip install" in zeile and "edu-sharing-python-client" in zeile
        and (treffer := _BESITZER.search(zeile)) and treffer.group(1) != HEIMAT
    ]
    assert not falsch, "Installation von woanders:\n" + "\n".join(falsch)


def test_der_meldeweg_fuehrt_zur_heimat():
    """Eine Sicherheitsmeldung geht dorthin, wo die Bibliothek herkommt."""
    zeilen = [z for _, z in _zeilen("SECURITY.md") if "advisories/new" in z]
    assert zeilen, "SECURITY.md nennt keinen Meldeweg mehr"
    for zeile in zeilen:
        treffer = _BESITZER.search(zeile)
        assert treffer and treffer.group(1) == HEIMAT, zeile.strip()


def test_die_paketmetadaten_nennen_die_heimat():
    """Was ein Paketindex anzeigt, ist fuer viele der einzige Wegweiser."""
    daten = tomllib.loads((WURZEL / "pyproject.toml").read_text(encoding="utf-8"))
    urls = daten["project"]["urls"]
    assert urls, "pyproject.toml nennt keine Adressen mehr"
    for name, wert in urls.items():
        treffer = _BESITZER.search(wert)
        assert treffer and treffer.group(1) == HEIMAT, f"{name} = {wert}"


def test_die_paketmetadaten_nennen_den_autor():
    daten = tomllib.loads((WURZEL / "pyproject.toml").read_text(encoding="utf-8"))
    namen = [eintrag.get("name", "") for eintrag in daten["project"].get("authors", [])]
    assert any(name.strip() for name in namen), "pyproject.toml nennt keinen Autor"


def test_die_readmes_nennen_den_autor():
    """Beide Sprachen, damit die Nennung nicht an einer Fassung haengt."""
    for rel, ueberschrift in (("README.md", "## Author"), ("README.de.md", "## Autor")):
        text = (WURZEL / rel).read_text(encoding="utf-8")
        assert ueberschrift in text, f"{rel} hat keinen Autorenabschnitt"
        assert "Jan Schachtschabel" in text, rel


def test_keine_readme_verspricht_einen_tag_den_die_heimat_nicht_hat():
    """Die Gegenprobe zu DOC-20-1.

    ``git ls-remote --tags`` gegen openeduhub war am 20.09.2026 leer, also kann
    kein ``@v…`` dorthin zeigen. Sobald dort getaggt wird, faellt dieser Test
    als erster auf -- und sagt damit, dass der Abschnitt wieder geschrieben
    werden darf.
    """
    falsch = [
        f"{rel}:{nummer}: {zeile.strip()}"
        for rel in ANWEISEND for nummer, zeile in _zeilen(rel)
        if re.search(rf"github\.com/{HEIMAT}/edu-sharing-python-client@v", zeile)
    ]
    assert not falsch, ("ein Tag, den es dort nicht gibt:\n" + "\n".join(falsch))


def test_die_wache_erkennt_den_rueckfall():
    """Gegenprobe: genau die Zeilen, die das Audit fand, werden rot."""
    gefunden = _BESITZER.search(
        'python -m pip install "git+https://github.com/janschachtschabel/'
        'edu-sharing-python-client@main"')
    assert gefunden and gefunden.group(1) != HEIMAT
    assert re.search(rf"github\.com/{HEIMAT}/edu-sharing-python-client@v",
                     'uv pip install "git+https://github.com/openeduhub/'
                     'edu-sharing-python-client@v0.2.0"')
