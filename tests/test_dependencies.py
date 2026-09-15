"""Was das Paket verlangt, benutzt es auch.

Am 03.09.2026 nannte ``pyproject.toml`` vier Laufzeit-Abhaengigkeiten, von
denen zwei nirgends importiert waren: ``python-dateutil`` und
``typing-extensions``. Die generierte Schicht liest Daten mit
``datetime.fromisoformat``, und ``six`` kam nur als Anhaengsel von dateutil
mit. Jede unbenutzte Abhaengigkeit ist Gewicht, Angriffsflaeche und Pflege
fuer nichts (Audit DEP-1).

Die Wache liest, was das Paket verlangt, und sucht den Import dazu. Sie faengt
den umgekehrten Fall nicht -- ein Import ohne Eintrag faellt beim Installieren
in einer frischen Umgebung auf, und dafuer ist die CI da.
"""

import ast
import hashlib
import tomllib
from pathlib import Path

import pytest

WURZEL = Path(__file__).resolve().parent.parent
QUELLE = WURZEL / "src" / "edusharing"

#: Wie ein Paket auf PyPI heisst und wie es sich importiert, ist nicht
#: dasselbe -- und manches Paket bringt zwei Namen mit. Nur die Faelle, die
#: hier vorkommen.
_MODULNAME = {
    "python-dateutil": {"dateutil"},
    "typing-extensions": {"typing_extensions"},
    "attrs": {"attrs", "attr"},
}


def _verlangt() -> list[str]:
    """Die Laufzeit-Abhaengigkeiten, ohne ihre Versionsgrenzen."""
    daten = tomllib.loads((WURZEL / "pyproject.toml").read_text(encoding="utf-8"))
    namen = []
    for eintrag in daten["project"]["dependencies"]:
        name = eintrag.split(";")[0]
        for trenner in (">=", "==", "~=", ">", "<", "!=", "["):
            name = name.split(trenner)[0]
        namen.append(name.strip())
    return namen


def _importierte_wurzeln() -> set[str]:
    """Jedes Modul, das irgendwo unter ``src/`` importiert wird -- oberste
    Ebene, denn ``from attr import define`` verlangt ``attrs``."""
    gefunden: set[str] = set()
    for pfad in QUELLE.rglob("*.py"):
        baum = ast.parse(pfad.read_text(encoding="utf-8"), filename=str(pfad))
        for knoten in ast.walk(baum):
            if isinstance(knoten, ast.Import):
                gefunden.update(a.name.split(".")[0] for a in knoten.names)
            elif isinstance(knoten, ast.ImportFrom) and knoten.level == 0:
                gefunden.add((knoten.module or "").split(".")[0])
    return gefunden


@pytest.mark.parametrize("paket", _verlangt())
def test_jede_verlangte_abhaengigkeit_wird_auch_importiert(paket):
    importiert = _importierte_wurzeln()
    moegliche = _MODULNAME.get(paket, {paket.replace("-", "_")})
    assert moegliche & importiert, (
        f"{paket} steht in pyproject.toml, wird aber unter src/ nirgends "
        f"importiert (gesucht: {sorted(moegliche)}). Gewicht und "
        "Angriffsflaeche fuer nichts -- entweder benutzen oder streichen."
    )


def test_die_wache_findet_ein_phantom():
    """Ohne diesen Test waere eine Wache, die die Namen nicht mehr aufloest,
    gruen und wertlos."""
    # Ohne diese Zeile waere eine leere Liste kein Fehlschlag, sondern ein
    # uebersprungener Test -- die Wache waere still statt rot.
    assert _verlangt(), "keine Laufzeit-Abhaengigkeit gelesen"
    assert "httpx" in _importierte_wurzeln()
    assert "gibtsnicht" not in _importierte_wurzeln()


# --- Herkunft der generierten Schicht --------------------------------------


def test_die_generierte_schicht_sagt_woraus_sie_entstand():
    """1131 Dateien, 141k Zeilen -- und bis zum Audit stand nirgends, welcher
    Generator und welche Spec sie erzeugt haben. Wer neu erzeugt, bekommt dann
    einen Diff, in dem sich Spec-Aenderung und Generator-Aenderung nicht
    trennen lassen (Audit DEP-2)."""
    notiz = (WURZEL / "src" / "edusharing" / "_generated" / "GENERATED.md")
    assert notiz.exists(), "die Herkunftsnotiz fehlt -- scripts/generate_client.py schreibt sie"
    text = notiz.read_text(encoding="utf-8")

    lock = tomllib.loads((WURZEL / "uv.lock").read_text(encoding="utf-8"))
    version = next(p["version"] for p in lock["package"]
                   if p["name"] == "openapi-python-client")
    assert f"openapi-python-client` {version}" in text, (
        "die Notiz nennt eine andere Generator-Fassung als uv.lock")

    spec = WURZEL / "openapi" / "edu-sharing-11.0.json"
    digest = hashlib.sha256(spec.read_bytes()).hexdigest()
    assert digest in text, (
        "die Notiz nennt einen anderen Spec-Hash als die eingecheckte Spec -- "
        "entweder ist die Schicht aelter als die Spec oder umgekehrt")


# --- Der Umfang des Quellpakets (Audit OPS-5) ------------------------------
#
# Ohne einen eigenen Abschnitt nimmt hatchling alles, was unter Versionskontrolle
# steht. Gemessen am 08.09.2026: 1318 Dateien, 1,2 MB -- darunter `.claude/`
# (Werkzeugkonfiguration), `.github/`, `uv.lock` und die 1,3 MB grosse
# Spezifikation, die nur zum Regenerieren gebraucht wird.

def _sdist_abschnitt() -> dict:
    text = (WURZEL / "pyproject.toml").read_text(encoding="utf-8")
    return tomllib.loads(text)["tool"]["hatch"]["build"]["targets"]["sdist"]


def test_das_quellpaket_zaehlt_auf_was_es_mitnimmt():
    """Eine Positivliste, keine Ausschlussliste.

    Eine Ausschlussliste veraltet bei jedem neuen Ordner: was dazukommt, ist
    ausgeliefert, bis jemand daran denkt. Eine Einschlussliste ist die
    Definition und kann nicht unvollstaendig werden -- sie kann nur zu wenig
    mitnehmen, und das faellt beim ersten Installieren auf.
    """
    abschnitt = _sdist_abschnitt()
    assert "include" in abschnitt, (
        "ohne `include` nimmt hatchling alles, was git kennt")
    assert "exclude" not in abschnitt, (
        "eine Ausschlussliste veraltet mit jedem neuen Ordner")


def test_das_quellpaket_traegt_das_paket_und_seine_lizenz():
    """Das Minimum, ohne das die Auslieferung falsch waere."""
    include = _sdist_abschnitt()["include"]
    for pflicht in ("src/edusharing", "LICENSE", "README.md", "pyproject.toml"):
        assert any(e.rstrip("/") == pflicht for e in include), f"{pflicht} fehlt"


def test_jeder_genannte_pfad_existiert():
    """Ein Eintrag, der ins Leere zeigt, nimmt still nichts mit -- und ein
    leeres Quellpaket faellt erst dem auf, der es installiert."""
    fehlend = [e for e in _sdist_abschnitt()["include"]
               if not (WURZEL / e.rstrip("/")).exists()]
    assert not fehlend, f"im include, aber nicht im Baum: {fehlend}"


def test_die_suite_gehoert_nicht_ins_quellpaket():
    """Sie prueft das *Repositorium*, nicht das Paket.

    ``test_docs_*`` liest ``docs/`` und die READMEs, ``test_dependencies``
    liest ``uv.lock`` und die Spezifikation, ``test_no_secrets`` durchsucht
    ``.github/`` und ``.claude/``. Fehlen die, laufen die Wachen nicht rot --
    ``rglob`` auf einem Ordner, den es nicht gibt, liefert einfach nichts.
    Eine Suite, die im Quellpaket aus dem falschen Grund gruen ist, verspricht
    eine Pruefbarkeit, die es dort nicht gibt.
    """
    include = _sdist_abschnitt()["include"]
    assert not any(e.rstrip("/") == "tests" for e in include)


#: Was das Quellpaket mitnimmt -- die Entscheidung aus OPS-5, hier zum
#: Nachschlagen. Wer sie aendert, aendert diesen Satz mit und denkt dabei
#: nach: die Wachen darunter halten sonst nur den Boden, und das Wiederaufnehmen
#: von ``openapi/`` -- den 1,3 MB, um die es ging -- faellt niemandem auf
#: (Pruefung 08.09.2026).
UMFANG = {
    "src/edusharing", "pyproject.toml", "LICENSE",
    "README.md", "README.de.md", "CHANGELOG.md", "SECURITY.md",
}


def test_das_quellpaket_nimmt_nichts_mit_das_niemand_beschlossen_hat():
    """Die Decke, nicht der Boden.

    Eine Positivliste kann nicht *unvollstaendig* werden -- das ist ihr Vorzug
    --, aber sie kann wachsen, ohne dass jemand hinsieht. Diese Wache ist die
    zweite Unterschrift.
    """
    dazu = sorted({e.rstrip("/") for e in _sdist_abschnitt()["include"]} - UMFANG)
    assert not dazu, (
        f"im Quellpaket, aber nicht in UMFANG: {dazu}. Wenn das so gewollt ist, "
        "gehoert es dort eingetragen -- mit dem Grund.")
