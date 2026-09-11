"""Die Werte in den Codebeispielen -- nicht nur die Namen.

``test_docs_code`` prueft, ob ein Aufruf an die echte Signatur bindet. Ob der
**Wert** an einer Stelle stimmt, fragt es nicht. Das Review des Skills vom
11.09.2026 fand genau solche Stellen -- jede bindet, keine tut, was sie
verspricht:

* ``repo.search("Bruch", facets=["subject"])``: auf API-Ebene geht ``subject``
  ungemappt an den Server. Live: 400, *Widget subject was not found in the mds
  oeh*. Kurznamen uebersetzen nur die Schluesselwort-Filter von ``search`` und
  die Flows.
* ``repo.vocab.resolve_all("subject", "Biologie")``: dasselbe, ebenfalls 400.
* ``node.workflow.submit(…, "TO_BE_CHECKED")``: der Status gehoert zur Instanz,
  auf WLO ``100_tocheck``. Geraten wird er gespeichert und zurueckgelesen, also
  meldet nichts einen Fehler -- und das Material landet in keiner
  Warteschlange (README, *Workflow*).

Gelesen werden die ``python``-Bloecke der Dokumente, jeder Inline-Code, der als
Python parst -- ``SKILL.md`` hatte den ersten Fall im Fliesstext -- und die
Beispiele.
"""

import ast
import re
import textwrap

from test_docs_code import DOKUMENTE, WURZEL, _bloecke, _kette

_ZAUN = re.compile(r"```.*?```", re.S)
_INLINE = re.compile(r"`([^`\n]+)`")

#: Methoden, deren erstes Argument eine Eigenschaft ist. ``get`` fehlt mit
#: Absicht: ``hit.get("description")`` am Flow-Ergebnis ist ein ``dict``.
_EIGENSCHAFT_ZUERST = {"labels", "get_all", "set_property", "propose",
                       "values", "suggest", "resolve", "resolve_all"}

#: Der Einreichungsstatus, den WLO kennt -- gemessen in
#: ``tests/test_live_write.py``, erklaert im README unter *Workflow*. Ein
#: anderer Wert in der Doku ist geraten.
GEMESSENER_STATUS = "100_tocheck"


def _schnipsel(rel: str) -> list[str]:
    """Jeder Code in einer Datei, den jemand kopieren koennte."""
    pfad = WURZEL / rel
    if pfad.suffix == ".py":
        return [pfad.read_text(encoding="utf-8")]
    gefunden = [quelle for _, quelle in _bloecke(rel)]
    fliesstext = _ZAUN.sub("", pfad.read_text(encoding="utf-8"))
    gefunden += [s for s in _INLINE.findall(fliesstext) if "(" in s]
    return gefunden


def _eigenschaft(knoten: ast.AST) -> str | None:
    """Der Text eines Zeichenketten-Literals, das keine Eigenschaft ist."""
    if isinstance(knoten, ast.Constant) and isinstance(knoten.value, str) \
            and ":" not in knoten.value:
        return knoten.value
    return None


def _verstoesse(quelle: str) -> list[str]:
    """Kurznamen an Eigenschaftspositionen, und ein geratener Status."""
    try:
        baum = ast.parse(textwrap.dedent(quelle))
    except SyntaxError:
        return []                # sagt test_docs_code, oder es ist kein Code
    gefunden = []
    for aufruf in ast.walk(baum):
        if not isinstance(aufruf, ast.Call):
            continue
        kette = _kette(aufruf.func) or []
        name = kette[-1] if kette else ""
        ueber_flows = "flows" in kette
        for wort in aufruf.keywords:
            werte: list[ast.AST] = []
            if wort.arg == "facets" and not ueber_flows and isinstance(
                    wort.value, (ast.List, ast.Tuple)):
                werte = list(wort.value.elts)
            elif wort.arg in ("filters", "properties") and isinstance(wort.value, ast.Dict):
                werte = [k for k in wort.value.keys if k is not None]
            elif wort.arg == "properties" and isinstance(wort.value, (ast.List, ast.Tuple)):
                werte = list(wort.value.elts)
            for wert in werte:
                if (kurz := _eigenschaft(wert)) is not None:
                    gefunden.append(f"{name}({wort.arg}=...{kurz!r}...): ein "
                                    "Kurzname, wo die Eigenschaft stehen muss")
        if name in _EIGENSCHAFT_ZUERST and not ueber_flows and aufruf.args:
            if (kurz := _eigenschaft(aufruf.args[0])) is not None:
                gefunden.append(f"{name}({kurz!r}, ...): ein Kurzname, wo die "
                                "Eigenschaft stehen muss")
        if kette[-2:] == ["workflow", "submit"]:
            status = aufruf.args[1] if len(aufruf.args) > 1 else next(
                (w.value for w in aufruf.keywords if w.arg == "status"), None)
            if isinstance(status, ast.Constant) and status.value != GEMESSENER_STATUS:
                gefunden.append(f"workflow.submit(..., {status.value!r}): nicht der "
                                f"gemessene Status {GEMESSENER_STATUS!r}")
    return gefunden


def _dateien() -> list[str]:
    beispiele = sorted((WURZEL / "docs" / "examples").glob("*.py"))
    return DOKUMENTE + [p.relative_to(WURZEL).as_posix() for p in beispiele]


def test_eigenschaftspositionen_tragen_den_vollen_namen():
    """Ein Kurzname dort, wo die Bibliothek ihn nicht uebersetzt, ist ein 400.

    Kurznamen gelten als Schluesselwort bei ``search``, ``update`` und
    ``create_node`` und ueberall in ``repo.flows`` -- dort auch in ``facets``.
    Nicht in ``filters``, nicht in ``properties``, nicht in ``facets`` auf
    API-Ebene, nicht als Eigenschaft von ``vocab``, ``resolve``, ``labels``,
    ``get_all``, ``set_property`` oder ``propose``.
    """
    falsch = [f"{rel}: {befund}"
              for rel in _dateien() for quelle in _schnipsel(rel)
              for befund in _verstoesse(quelle)]
    assert not falsch, "\n".join(falsch)


def test_der_waechter_sieht_kurznamen_und_status():
    """Gegenprobe: jede der drei Stellen aus dem Review wird rot, ihr
    Gegenstueck gruen -- und der Flow darf, was die API-Ebene nicht darf."""
    rot = [
        'repo.search("Bruch", facets=["subject"])',
        'repo.searcher.search(text, filters={"subject": "Physik"})',
        'await repo.vocab.resolve_all("subject", "Biologie")',
        'node.update(properties={"subject": [uri]})',
        'node.labels("subject")',
        'node.workflow.submit("GROUP_redaktion", "TO_BE_CHECKED")',
        'node.workflow.submit("GROUP_redaktion", status="TO_BE_CHECKED")',
    ]
    gruen = [
        'repo.search("Bruch", facets=["ccm:taxonid"])',
        'repo.flows.search("Bruch", facets=["subject"])',
        'repo.search("Bruch", subject="Mathematik")',
        'await repo.vocab.resolve_all("ccm:taxonid", "Biologie")',
        'node.labels("ccm:taxonid")',
        'hit.get("description")',
        'repo.flows.vocabulary("subject")',
        'node.workflow.submit("GROUP_redaktion", "100_tocheck")',
    ]
    for quelle in rot:
        assert _verstoesse(quelle), quelle
    for quelle in gruen:
        assert not _verstoesse(quelle), quelle


def test_der_waechter_liest_auch_inline_code():
    """``SKILL.md`` hatte ``facets=["subject"]`` im Fliesstext, nicht im Block."""
    text = 'Sonst: `repo.searcher.search(t, facets=["subject"])`. Und `nicht(` Code.'
    spans = [s for s in _INLINE.findall(text) if "(" in s]
    assert [b for s in spans for b in _verstoesse(s)]
