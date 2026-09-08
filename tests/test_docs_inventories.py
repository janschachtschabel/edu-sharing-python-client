"""Jedes Verzeichnis in der Dokumentation zaehlt auf, was es wirklich gibt.

``test_docs_complete.py`` fragt: *steht jeder oeffentliche Name irgendwo?*
Hier steht die andere Frage: *stimmen die Listen?* Eine Aufzaehlung veraltet
anders als ein fehlender Name -- sie bleibt lesbar, plausibel und vollstaendig
aussehend, waehrend hinter ihr etwas dazugekommen ist.

Genau das war passiert (Audit DOC-5): die README zaehlte am 03.09.2026
"Twenty flows" auf, ``Flows`` hatte 26; die Beispieltabelle endete bei
``20_provider_load.py``, obwohl ``21_skills.py`` seit dem 02.09.2026 im Ordner
lag und in keinem Verzeichnis stand. Beides faellt niemandem auf, der die Liste
nur liest.

Deshalb gehoeren die Zahlen den Waechtern und nicht der Prosa: die Dokumente
nennen **keine** Anzahl mehr, sie zaehlen auf -- und hier wird gezaehlt.
"""

import re
from pathlib import Path

import pytest

WURZEL = Path(__file__).resolve().parent.parent
BEISPIELE = WURZEL / "docs" / "examples"


def ablaeufe() -> set[str]:
    """Die oeffentlichen Ablaeufe, aus der Klasse gelesen statt gezaehlt."""
    from edusharing.flows import Flows

    return {n for n in dir(Flows) if not n.startswith("_")}


# --- Das Kapitelverzeichnis in FLOWS ---------------------------------------

FLUSSDATEIEN = {
    "FLOWS.md": WURZEL / "docs" / "FLOWS.md",
    "FLOWS.de.md": WURZEL / "docs" / "FLOWS.de.md",
}

#: ``## `name` `` -- jeder Ablauf hat in FLOWS ein eigenes Kapitel.
_KAPITEL = re.compile(r"^## `([a-z_]+)", re.M)


@pytest.mark.parametrize("name", sorted(FLUSSDATEIEN))
def test_flows_hat_ein_kapitel_je_ablauf(name):
    """FLOWS ist das gueltige Verzeichnis -- also muss es vollstaendig sein."""
    pfad = FLUSSDATEIEN[name]
    assert pfad.exists(), f"{name} fehlt"
    kapitel = set(_KAPITEL.findall(pfad.read_text(encoding="utf-8")))
    echte = ablaeufe()

    fehlend = sorted(echte - kapitel)
    assert not fehlend, f"{name}: kein Kapitel fuer {fehlend}"

    erfunden = sorted(kapitel - echte)
    assert not erfunden, f"{name}: Kapitel fuer Ablaeufe, die es nicht gibt: {erfunden}"


# --- Die Aufzaehlung in der README -----------------------------------------
#
# Die README nennt die Ablaeufe in einem Satz. Der Satz beginnt mit einer festen
# Wendung, damit diese Wache ihn findet: wer sie umschreibt, faellt hier auf und
# nicht erst dem Leser.

READMES = {
    "README.md": (WURZEL / "README.md", "Every flow:"),
    "README.de.md": (WURZEL / "README.de.md", "Alle Abläufe:"),
}

_SPANNE = re.compile(r"`([a-z_]+)`")


@pytest.mark.parametrize("name", sorted(READMES))
def test_die_readme_zaehlt_jeden_ablauf_auf(name):
    """Die Aufzaehlung nennt jeden Ablauf und erfindet keinen."""
    pfad, anfang = READMES[name]
    text = pfad.read_text(encoding="utf-8")
    beginn = text.find(anfang)
    assert beginn != -1, (
        f"{name}: die Aufzaehlung faengt nicht mehr mit {anfang!r} an. "
        "Entweder die Wendung wiederherstellen oder diese Wache mitfuehren.")
    ende = text.find("\n\n", beginn)
    genannt = set(_SPANNE.findall(text[beginn:ende]))
    echte = ablaeufe()

    fehlend = sorted(echte - genannt)
    assert not fehlend, (
        f"{name}: {len(fehlend)} von {len(echte)} Ablaeufen fehlen in der "
        f"Aufzaehlung: {fehlend}")

    erfunden = sorted(genannt - echte)
    assert not erfunden, f"{name}: aufgezaehlt, aber kein Ablauf: {erfunden}"


# --- Das Beispielverzeichnis ------------------------------------------------

_VERWEIS = re.compile(r"docs/examples/([0-9]{2}_[a-z_]+\.py)")


@pytest.mark.parametrize("name", sorted(READMES))
def test_jedes_beispiel_steht_in_der_readme(name):
    """Ein Beispiel, das in keiner Tabelle steht, findet niemand.

    Der umgekehrte Weg -- zeigt jeder Verweis auf eine Datei, die es gibt --
    steht in ``test_docs_complete.py``. Beide Richtungen zusammen halten das
    Verzeichnis deckungsgleich mit dem Ordner.
    """
    pfad, _ = READMES[name]
    verzeichnet = set(_VERWEIS.findall(pfad.read_text(encoding="utf-8")))
    vorhanden = {p.name for p in BEISPIELE.glob("*.py")}

    fehlend = sorted(vorhanden - verzeichnet)
    assert not fehlend, f"{name}: nicht verzeichnet: {fehlend}"


# --- Das Modulverzeichnis ---------------------------------------------------

ARCHITEKTUR = {
    "ARCHITECTURE.md": WURZEL / "docs" / "ARCHITECTURE.md",
    "ARCHITECTURE.de.md": WURZEL / "docs" / "ARCHITECTURE.de.md",
}
QUELLE = WURZEL / "src" / "edusharing"


def module() -> list[str]:
    """Jedes Modul der Handschicht, als Pfad ab ``edusharing/``."""
    return [p.relative_to(QUELLE).as_posix()
            for p in sorted(QUELLE.rglob("*.py"))
            if "_generated" not in p.parts and p.name != "__init__.py"]


@pytest.mark.parametrize("name", sorted(ARCHITEKTUR))
def test_jedes_modul_kommt_im_architekturnachweis_vor(name):
    """Ein Teilsystem, das im Nachweis fehlt, gibt es fuer den Leser nicht.

    Am 03.09.2026 kam das Wort "skills" in ARCHITECTURE ueberhaupt nicht vor,
    obwohl vier Module es tragen -- rund 13 % der Schicht, ohne einen Satz
    darueber, warum es sie gibt (Audit DOC-3). Zehn Module waren so unsichtbar.

    Es genuegt, dass der Name faellt: als Pfad, als Dateiname oder in
    Code-Schreibweise. Diese Wache verlangt keinen eigenen Absatz je Modul --
    sie verlangt, dass keines vergessen wird.
    """
    text = ARCHITEKTUR[name].read_text(encoding="utf-8")
    fehlend = [
        m for m in module()
        if m not in text and Path(m).name not in text and f"`{Path(m).stem}`" not in text
    ]
    assert not fehlend, (
        f"{name}: {len(fehlend)} von {len(module())} Modulen kommen nicht vor:\n  "
        + "\n  ".join(fehlend))


# --- Die Warnstellen --------------------------------------------------------

_WARNT = re.compile(r"\blogger\.warning\(")


def warnende_module() -> list[str]:
    """Jedes Modul, das mindestens einmal ``logger.warning`` ruft."""
    return [p.relative_to(QUELLE).as_posix()
            for p in sorted(QUELLE.rglob("*.py"))
            if "_generated" not in p.parts
            and _WARNT.search(p.read_text(encoding="utf-8"))]


@pytest.mark.parametrize("name", sorted(READMES))
def test_jedes_warnende_modul_steht_in_der_readme(name):
    """WARNING ist die Ausnahme vom Schweigen -- also gehoert sie aufgezaehlt.

    Die README zaehlte "vier Stellen" auf, es waren fuenf, als der Audit sie
    zaehlte (DOC-7), und sieben, als diese Wache entstand: dazugekommen waren
    die abgewiesene Adressschreibweise aus SEC-3 und die Hintergrundschleife,
    die nicht anhaelt, aus COR-4. Beide sind fuer den Aufrufer die einzige
    Nachricht ueber etwas, das sonst niemand bemerkt.

    Gezaehlt werden **Module**, nicht Aufrufe: die drei Hostverweigerungen des
    Extraktionsdienstes sind ein Absatz wert, nicht drei. Eine Anzahl steht in
    der README deshalb nicht mehr -- eine Zahl, die niemand nachrechnet, wird
    falsch, ohne dass sie aufhoert, ueberzeugend auszusehen.
    """
    pfad, _ = READMES[name]
    text = pfad.read_text(encoding="utf-8")
    fehlend = [m for m in warnende_module() if m not in text]
    assert not fehlend, (
        f"{name}: diese Module warnen, werden aber nicht genannt: {fehlend}")
