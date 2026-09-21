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

#: Ein Installationsbefehl, der einen Tag der Heimat festnagelt.
_MIT_TAG = re.compile(
    rf"github\.com/{HEIMAT}/edu-sharing-python-client@v([0-9][0-9A-Za-z.\-]*)")

#: Etwas, das wie eine Versionsangabe aussieht. **Nicht** nur ``X.Y.Z``: die
#: erste Fassung verlangte genau drei Zahlen und war damit fuer ``0.4.0rc1``
#: oder ``0.4.0b2`` **unerfuellbar** -- das Muster fand dort gar nichts, also
#: haette kein Wortlaut der Tabellenzeile den Test gruen bekommen, und die
#: Meldung haette "gar keine Version" gesagt statt "diese Form kenne ich
#: nicht". Eine Wache, die an einer gueltigen Versionsnummer haengenbleibt,
#: kostet genau in dem Moment eine Stunde, in dem jemand veroeffentlicht.
_WIE_EINE_VERSION = re.compile(r"\b[0-9]+\.[0-9]+(?:[0-9A-Za-z.]*[0-9A-Za-z])?")


def _version() -> str:
    """Die Version, die das Projekt gerade traegt -- aus ``pyproject.toml``.

    Nicht ueber ``edusharing.__version__``: das liest die Paketdaten der
    installierten Fassung und haengt nach einer Erhoehung genau so lange
    hinterher, bis jemand neu synchronisiert -- der Test wuerde dann gruen
    bleiben, obwohl die Doku bereits falsch ist.
    """
    daten = tomllib.loads((WURZEL / "pyproject.toml").read_text(encoding="utf-8"))
    return str(daten["project"]["version"])


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
    """Die Gegenprobe zu DOC-20-1 -- seit dem 21.09.2026 andersherum.

    Bis dahin war ``git ls-remote --tags`` gegen openeduhub leer, und jedes
    ``@v…`` zeigte ins Nichts; der Test verbot sie deshalb alle. Seither liegen
    dort Tags, und der Release-Ablauf am Ende der README legt jede weitere
    Version ebenfalls dort ab. Ein ``@v…`` darf also stehen -- aber nur das der
    laufenden Version.

    Denn die Zeile, die eine Versionserhoehung ueberlebt, ist die eigentliche
    Falle: sie zeigt auf einen Tag, den es gibt, und schickt trotzdem jeden
    Leser auf einen alten Stand. Ein Linter findet das nie, und dem Schreiber
    der Erhoehung faellt es nicht auf, weil nichts rot wird.
    """
    version = _version()
    falsch = [
        f"{rel}:{nummer}: {zeile.strip()}"
        for rel in ANWEISEND for nummer, zeile in _zeilen(rel)
        for treffer in _MIT_TAG.finditer(zeile)
        if treffer.group(1) != version
    ]
    assert not falsch, (
        f"ein Tag, der nicht {version} ist:\n" + "\n".join(falsch))


def test_die_gestuetzte_fassung_ist_die_laufende():
    """Wer installiert, was die README nennt, muss sich in SECURITY.md finden.

    Das Audit fand ``0.1.x`` als gestuetzte Linie, waehrend das Projekt 0.3.0
    trug -- "die Fassung, zu deren Installation man auffordert, steht nicht in
    ihrer eigenen Stuetzungstabelle" (DOC-20-2). Am 21.09.2026 stand dort
    ``0.3.0`` bei Version 0.3.4: derselbe Verfall, einen Schritt weiter.

    Das ist dieselbe Falle wie der ueberlebende ``@v…``-Tag eine Wache weiter
    oben. Die Zahl sieht richtig aus, niemand rechnet sie nach, und wer eine
    Luecke meldet, liest eine Tabelle, die ihm sagt, seine Fassung werde nicht
    gestuetzt -- obwohl sie die einzige ist, die es gibt.
    """
    version = _version()
    gestuetzt = [f"{nummer}: {zeile.strip()}"
                 for nummer, zeile in _zeilen("SECURITY.md") if "\u2705" in zeile]
    assert gestuetzt, "SECURITY.md nennt keine gestuetzte Fassung mehr"
    genannt = {treffer for zeile in gestuetzt
               for treffer in _WIE_EINE_VERSION.findall(zeile)}
    assert genannt == {version}, (
        f"gestuetzt genannt: {sorted(genannt) or 'gar keine Version'}, "
        f"laufend ist {version}\n  " + "\n  ".join(gestuetzt))


def test_die_wache_erkennt_den_rueckfall():
    """Gegenprobe: das falsche Repositorium bleibt falsch, und ein Tag aus
    einer frueheren Version wird als solcher erkannt."""
    gefunden = _BESITZER.search(
        'python -m pip install "git+https://github.com/janschachtschabel/'
        'edu-sharing-python-client@main"')
    assert gefunden and gefunden.group(1) != HEIMAT

    veraltet = _MIT_TAG.search(
        'uv pip install "git+https://github.com/openeduhub/'
        'edu-sharing-python-client@v0.2.0"')
    assert veraltet and veraltet.group(1) == "0.2.0" != _version()

    # Und die Stuetzungstabelle: eine Zeile ohne Zahl ist so falsch wie eine
    # mit der falschen -- sonst genuegte es, die Zahl wegzulassen.
    assert _WIE_EINE_VERSION.findall("| `main` (0.3.0) | \u2705 |") == ["0.3.0"]
    assert _WIE_EINE_VERSION.findall("| `main` | \u2705 |") == []

    # Eine Vorabversion ist eine Version. Ohne diese beiden Zeilen war die
    # Wache fuer sie unerfuellbar, und nichts sagte es.
    assert _WIE_EINE_VERSION.findall("| `main` (0.4.0rc1) | \u2705 |") == ["0.4.0rc1"]
    assert _WIE_EINE_VERSION.findall("| `main` (0.4.0.post1) | \u2705 |") == ["0.4.0.post1"]
    # Und ein Punkt am Satzende gehoert nicht zur Nummer.
    assert _WIE_EINE_VERSION.findall("die Fassung 0.3.4.") == ["0.3.4"]
