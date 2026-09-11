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

import inspect
import re
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType

import pytest
from test_docs_complete import _klassen_der_bibliothek

WURZEL = Path(__file__).resolve().parent.parent
SKILL = WURZEL / ".claude" / "skills" / "edu-sharing-python"


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
    """Zeichen fuer Zeichen -- sonst liest das Modell eine veraltete Referenz."""
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


def test_der_abgleich_vergleicht_wie_git(tmp_path):
    """CRLF gegen LF ist kein Unterschied -- fuer Git nicht, also auch hier nicht.

    ``.gitattributes`` legt ``eol=lf`` fest, aber ein Arbeitsbaum, der vor
    dieser Regel ausgecheckt wurde, behaelt CRLF (gemessen am 11.09.2026: 1172
    Dateien auf dem Rechner, auf dem der Skill entstand). Schreibt Git nach
    einem Pull nur die Quelle neu, stuende die Kopie byte-verschieden da,
    obwohl Git beide fuer gleich haelt -- ein roter Test ohne Befund.
    """
    abgleich = _abgleich()
    for name in ("REFERENCE.md", "REFERENCE.de.md", "FLOWS.md", "FLOWS.de.md"):
        (tmp_path / "docs" / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / "docs" / name).write_bytes(b"# Titel\r\nText\r\n")
    (tmp_path / "docs" / "examples").mkdir()
    abgleich.synchronisiere(tmp_path)
    kopie = tmp_path / ".claude" / "skills" / "edu-sharing-python" / "reference" / "FLOWS.md"
    assert kopie.read_bytes() == b"# Titel\nText\n", "die Kopie folgt eol=lf"
    assert abgleich.abweichungen(tmp_path) == []
    kopie.write_bytes(b"# Titel\nAnderer Text\n")
    assert abgleich.abweichungen(tmp_path) == [
        "veraltet: .claude/skills/edu-sharing-python/reference/FLOWS.md"]


# --- Die Vermittlungswache (Plan T3b) ---------------------------------------
#
# ``test_docs_complete`` fragt, ob jeder oeffentliche Name **vorkommt**.
# Gemessen am 11.09.2026 kam jeder vor -- und doch zeigte SKILL.md fuer 59 von
# 83 Aufrufformen mit Pflichtparametern nicht, was hineingehoert:
# ``set_property`` stand da, ``set_property(prop, value)`` nicht. Ein Modell,
# das nur den Namen kennt, raet die Argumente.
#
# Gezaehlt wird je Klasse, nicht je Name: ``delete`` gibt es an ``Comments``,
# ``Relations`` und ``Node`` mit drei verschiedenen Pflichtparametern. Die
# Huellen in ``_sync`` bleiben aussen vor -- sie spiegeln die asynchrone
# Oberflaeche Name fuer Name, wie ``test_docs_complete`` es festhaelt.

EINSTIEGE = ("SKILL.md", "SKILL.de.md")


def _pflichtparameter(klasse: type, name: str) -> tuple[tuple[str, ...], tuple[str, ...]] | None:
    """``(positionale, nur benannte)`` Parameter ohne Vorgabe -- ohne ``self``
    und ``cls``, ohne ``*args`` und ``**kwargs``. ``None`` fuer Properties und
    alles ohne Python-Rumpf."""
    roh = vars(klasse)[name]
    funktion = roh.__func__ if isinstance(roh, (classmethod, staticmethod)) else roh
    if not inspect.isfunction(funktion):
        return None
    parameter = list(inspect.signature(funktion).parameters.values())
    if not isinstance(roh, staticmethod):
        parameter = parameter[1:]
    ohne_vorgabe = [p for p in parameter if p.default is p.empty]
    return (tuple(p.name for p in ohne_vorgabe
                  if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)),
            tuple(p.name for p in ohne_vorgabe if p.kind is p.KEYWORD_ONLY))


def _aufrufformen() -> dict[tuple[str, tuple[str, ...], tuple[str, ...]], list[str]]:
    """Jede Form ``(name, positionale, nur benannte)`` -> die Methoden, die sie haben.

    ``from_response(data)`` haben zehn Klassen; eine Zeile, die die Form
    zeigt, zeigt sie fuer alle.
    """
    formen: dict[tuple[str, tuple[str, ...], tuple[str, ...]], list[str]] = {}
    for klassenname, klasse in sorted(_klassen_der_bibliothek().items()):
        if klasse.__module__ == "edusharing._sync":
            continue
        for name in vars(klasse):
            if name.startswith("_"):
                continue
            pflicht = _pflichtparameter(klasse, name)
            if pflicht is not None:
                formen.setdefault((name, *pflicht), []).append(f"{klassenname}.{name}")
    return formen


def _argumente(text: str, start: int) -> list[str] | None:
    """Die Argumente ab ``start`` bis zur passenden Klammer, an den Kommas der
    obersten Ebene getrennt -- ``None``, wenn die Klammer nicht schliesst."""
    tiefe, teile, aktuell, zeichen_in = 0, [], [], ""
    for ch in text[start:start + 500]:
        if zeichen_in:
            aktuell.append(ch)
            zeichen_in = "" if ch == zeichen_in else zeichen_in
            continue
        if ch in "\"'":
            zeichen_in = ch
        elif ch in "([{":
            tiefe += 1
        elif ch in ")]}":
            if tiefe == 0:
                teile.append("".join(aktuell).strip())
                return [t for t in teile if t]
            tiefe -= 1
        elif ch == "," and tiefe == 0:
            teile.append("".join(aktuell).strip())
            aktuell = []
            continue
        aktuell.append(ch)
    return None


def _zeigt(text: str, name: str, positional: tuple[str, ...], benannt: tuple[str, ...]) -> bool:
    """Steht ``name(`` mit genau diesen Parameternamen da? Die positionalen in
    ihrer Reihenfolge vorn (``prop``, ``prop=…`` oder ``prop: str``), die nur
    benannten als ``k=…`` irgendwo in der Liste."""
    for treffer in re.finditer(rf"(?<![A-Za-z0-9_]){name}\(", text):
        teile = _argumente(text, treffer.end())
        if teile is None or len(teile) < len(positional):
            continue
        if not all(re.match(rf"{p}\b(?!\()", teile[i]) for i, p in enumerate(positional)):
            continue
        if all(any(re.match(rf"{k}\s*[=:]", t) for t in teile) for k in benannt):
            return True
    return False


@pytest.mark.xfail(strict=True, reason="gruen erst mit dem neuen Skill (Plan "
                   "2026-09-11-skill-umbau, T5/T6) -- dann faellt diese Markierung weg")
@pytest.mark.parametrize("datei", EINSTIEGE)
def test_der_einstieg_zeigt_jede_aufrufform_mit_ihren_pflichtparametern(datei: str):
    """Der Einstieg selbst, nicht die Referenz: das Modell liest ihn zuerst,
    und jede Datei, die es dafuer oeffnen muss, ist ein Schritt, den es
    auslassen kann."""
    text = (SKILL / datei).read_text(encoding="utf-8")
    fehlend = [f"{name}({', '.join([*positional, *(k + '=' for k in benannt)])})"
               f"  [{', '.join(methoden)}]"
               for (name, positional, benannt), methoden in sorted(_aufrufformen().items())
               if (positional or benannt) and not _zeigt(text, name, positional, benannt)]
    assert not fehlend, (f"{datei} zeigt {len(fehlend)} Aufrufformen nicht mit ihren "
                         "Pflichtparametern:\n  " + "\n  ".join(fehlend))


def test_die_vermittlungswache_sieht_falsche_und_fehlende_namen():
    """Gegenprobe: nur der Aufruf mit den echten Namen zaehlt."""
    assert _zeigt("| `node.set_property(prop, value, *, verify=True)` | `Node` |",
                  "set_property", ("prop", "value"), ())
    assert not _zeigt("`node.set_property(value)`", "set_property", ("prop", "value"), ())
    assert not _zeigt('`node.set_property("cclom:title", "x")`',
                      "set_property", ("prop", "value"), ())
    assert not _zeigt("`node.reset_property(prop, value)`", "set_property", ("prop", "value"), ())
    assert _zeigt("`templates.chat(configs, *, context_node_id=…)`",
                  "chat", ("configs",), ("context_node_id",))
    assert not _zeigt("`templates.chat(configs)`", "chat", ("configs",), ("context_node_id",))


def test_die_aufrufformen_sind_die_gemessenen():
    """Woran die Wache haengt: je Klasse gezaehlt, die Huellen der blockierenden
    Fassade aussen vor. Die Form von ``set_property`` und die drei von
    ``delete`` muessen darunter sein -- sonst zaehlt die Wache etwas anderes
    als gemessen."""
    formen = _aufrufformen()
    assert ("set_property", ("prop", "value"), ()) in formen
    assert ("delete", ("comment_id",), ()) in formen
    assert ("delete", ("from_node", "relation_type", "to_node"), ()) in formen
    assert ("delete", (), ()) in formen
    assert not any(m.startswith("Sync") for ms in formen.values() for m in ms)


def _buendel(sprache: str) -> str:
    """Einstieg und Nachschlagedateien einer Sprache."""
    einstieg = SKILL / ("SKILL.de.md" if sprache == "de" else "SKILL.md")
    nachschlag = [p for p in sorted((SKILL / "reference").glob("*.md"))
                  if p.name.endswith(".de.md") == (sprache == "de")]
    return "\n".join(p.read_text(encoding="utf-8") for p in [einstieg, *nachschlag])


def _zeigt_ergebnis(text: str, name: str) -> bool:
    """``name(`` in einer Tabellenzeile mit einer zweiten Spalte -- die sagt,
    was zurueckkommt -- oder in einem Python-Beispiel."""
    aufruf = re.compile(rf"(?<![A-Za-z0-9_]){name}\(")
    for zeile in text.splitlines():
        if zeile.startswith("|") and aufruf.search(zeile):
            zellen = [z.strip() for z in zeile.strip().strip("|").split("|")]
            if sum(bool(z) for z in zellen) >= 2:
                return True
    return any(aufruf.search(block)
               for block in re.findall(r"```(?:python|py)\n(.*?)```", text, re.S))


def test_die_ergebniswache_sieht_eine_zeile_ohne_ergebnis():
    """Gegenprobe: der Name allein, oder eine Zeile ohne zweite Spalte, zaehlt nicht."""
    assert _zeigt_ergebnis("| `repo.whoami()` | `Identity` |", "whoami")
    assert _zeigt_ergebnis("```python\nme = await repo.whoami()\n```", "whoami")
    assert not _zeigt_ergebnis("| `repo.whoami()` | |", "whoami")
    assert not _zeigt_ergebnis("Mit `repo.whoami()` fragt man nach sich selbst.", "whoami")
    # Gemessen am 11.09.2026: 35 Formen -- 58 Methoden, von denen viele sich
    # eine teilen (``list()``, ``get()``, ``aclose()``).
    ohne = [f for f in _aufrufformen() if not f[1] and not f[2]]
    assert len(ohne) > 30, f"nur {len(ohne)} Formen ohne Pflichtparameter -- zaehlt die Wache?"


@pytest.mark.parametrize("sprache", ["en", "de"])
def test_jeder_aufruf_ohne_pflichtparameter_zeigt_was_zurueckkommt(sprache: str):
    """``whoami()`` braucht nichts -- aber wer es ruft, muss wissen, was
    zurueckkommt. Im Buendel, nicht zwingend im Einstieg: dort steht die
    Tabelle, hier genuegt die Referenz."""
    text = _buendel(sprache)
    fehlend = [f"{name}()  [{', '.join(methoden)}]"
               for (name, positional, benannt), methoden in sorted(_aufrufformen().items())
               if not positional and not benannt and not _zeigt_ergebnis(text, name)]
    assert not fehlend, (f"Buendel ({sprache}) zeigt fuer {len(fehlend)} Aufrufe nicht, was "
                         "zurueckkommt:\n  " + "\n  ".join(fehlend))
