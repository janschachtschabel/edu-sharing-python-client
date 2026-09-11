"""Der Skill traegt auch ausserhalb dieses Repositoriums.

Wer ``.claude/skills/edu-sharing-python`` nutzt, kopiert den Ordner -- nach
``~/.claude/skills/``, nach ``~/.agents/skills/`` oder als ZIP zu claude.ai.
Bis zum 11.09.2026 verwies der Skill fuer jede Einzelheit nach
``../../../docs/REFERENCE.md``; ausserhalb des Repositoriums zeigt das ins
Leere, und ein Modell raet dann die Signaturen.

Deshalb liegen die Nachschlagewerke **im** Skill-Ordner, unter ``reference/``:
Kopien von REFERENCE, FLOWS (je beide Sprachen) und aller Beispiele.
Kopien, nicht Neufassungen -- eine Quelle je Inhalt. ``scripts/sync_skill.py``
stellt sie her; dieser Test verlangt, dass sie gleich sind.
"""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType

WURZEL = Path(__file__).resolve().parent.parent


def _abgleich() -> ModuleType:
    """``scripts/sync_skill.py``, ohne es auszufuehren.

    Die Wache haengt an derselben Abbildung, die das Skript benutzt -- eine
    zweite Liste hier waere eine, die auseinanderlaeuft.
    """
    spec = spec_from_file_location("sync_skill", WURZEL / "scripts" / "sync_skill.py")
    assert spec is not None and spec.loader is not None
    modul = module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


def test_die_nachschlagedateien_sind_kopien_der_doku():
    """Byte fuer Byte -- sonst liest das Modell eine veraltete Referenz."""
    abweichend = _abgleich().abweichungen(WURZEL)
    assert not abweichend, (
        "Der Skill-Ordner weicht von docs/ ab -- `python scripts/sync_skill.py` "
        "behebt es:\n  " + "\n  ".join(abweichend))


def test_die_abbildung_nimmt_mit_was_der_plan_verlangt():
    """Die Abbildung selbst gegen die Anforderung: beide Sprachen von REFERENCE
    und FLOWS, und jedes Beispiel. Fehlte eine Datei in der Abbildung, waeren
    Skript und Wache sich einig -- und beide falsch."""
    quellen = {q.relative_to(WURZEL).as_posix() for q, _ in _abgleich().paare(WURZEL)}
    verlangt = {"docs/REFERENCE.md", "docs/REFERENCE.de.md",
                "docs/FLOWS.md", "docs/FLOWS.de.md"}
    verlangt |= {p.relative_to(WURZEL).as_posix()
                 for p in (WURZEL / "docs" / "examples").glob("*.py")}
    assert verlangt <= quellen, f"nicht in der Abbildung: {sorted(verlangt - quellen)}"


def test_die_kopien_behalten_ihre_namen():
    """``FLOWS.md`` verweist auf ``examples/05_flow_search.py``. Das bleibt nur
    gueltig, wenn die Kopie unter demselben relativen Namen liegt."""
    for quelle, kopie in _abgleich().paare(WURZEL):
        von_docs = quelle.relative_to(WURZEL / "docs").as_posix()
        im_skill = kopie.relative_to(
            WURZEL / ".claude" / "skills" / "edu-sharing-python" / "reference").as_posix()
        assert von_docs == im_skill


def test_der_abgleich_sieht_jede_abweichung(tmp_path):
    """Gegenprobe: fehlend, veraltet und verwaist fallen auf -- und das
    Skript behebt alle drei."""
    abgleich = _abgleich()
    for name in ("REFERENCE.md", "REFERENCE.de.md", "FLOWS.md", "FLOWS.de.md"):
        (tmp_path / "docs" / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / "docs" / name).write_text(f"# {name}\n", encoding="utf-8")
    (tmp_path / "docs" / "examples").mkdir()
    (tmp_path / "docs" / "examples" / "01_a.py").write_text("print(1)\n", encoding="utf-8")

    assert "fehlt: .claude/skills/edu-sharing-python/reference/FLOWS.md" in (
        abgleich.abweichungen(tmp_path))
    abgleich.synchronisiere(tmp_path)
    assert abgleich.abweichungen(tmp_path) == []

    ziel = tmp_path / ".claude" / "skills" / "edu-sharing-python" / "reference"
    (ziel / "FLOWS.md").write_text("# von Hand geaendert\n", encoding="utf-8")
    (ziel / "examples" / "99_alt.py").write_text("print(99)\n", encoding="utf-8")
    assert abgleich.abweichungen(tmp_path) == [
        "veraltet: .claude/skills/edu-sharing-python/reference/FLOWS.md",
        "verwaist: .claude/skills/edu-sharing-python/reference/examples/99_alt.py",
    ]
    abgleich.synchronisiere(tmp_path)
    assert abgleich.abweichungen(tmp_path) == []
    assert not (ziel / "examples" / "99_alt.py").exists()
