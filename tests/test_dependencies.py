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
