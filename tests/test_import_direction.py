"""Die Schichten zeigen in eine Richtung.

ARCHITECTURE zeichnet drei Schichten: die Ressourcen (``nodes``, ``skills``,
``search`` -- direkt unter ``edusharing/``), die Ablaeufe darueber
(``flows/``) und die Agentenbausteine zuoberst (``agent/``). Jede darf nach
unten greifen, keine nach oben.

Gemessen am 03.09.2026 stimmte das nicht: ``skills.py`` holte sich
``flows.fields`` und ``flows.ranking``, ``flows/text.py`` den ``cap_text`` aus
``agent/``. ``repo.skills`` liess sich damit ohne das ganze Ablaufpaket nicht
laden, und der Satz „Ablaeufe fuegen keine Faehigkeit hinzu" stimmte im Code
nicht mehr (Audit ARC-1). Nichts hat es gemeldet -- diese Datei tut es.
"""

import ast
from pathlib import Path

QUELLE = Path(__file__).resolve().parent.parent / "src" / "edusharing"

#: Die beiden Dateien, die nach oben greifen duerfen, und warum.
#: ``repository.py`` ist die Montagestelle -- sie verdrahtet die Schichten und
#: haengt ``repo.flows`` an; ``__init__.py`` ist die Paketoberflaeche, die die
#: oeffentlichen Namen aller Schichten nennt. Beide bauen nichts, sie reichen
#: durch.
MONTAGE = {"repository.py", "__init__.py"}

OBERE_SCHICHTEN = ("flows", "agent")


def _importe(pfad: Path) -> set[str]:
    """Jeder importierte Modulname, ausgedrueckt ab ``edusharing``."""
    paket = pfad.relative_to(QUELLE).parent.as_posix()
    teile = [] if paket in ("", ".") else paket.split("/")
    namen: set[str] = set()
    baum = ast.parse(pfad.read_text(encoding="utf-8"), filename=str(pfad))
    for knoten in ast.walk(baum):
        if isinstance(knoten, ast.ImportFrom):
            if knoten.level == 0:
                name = knoten.module or ""
                namen.add(name.removeprefix("edusharing.") if name.startswith(
                    "edusharing.") else name)
                continue
            wurzel = teile[: len(teile) - (knoten.level - 1)]
            namen.add(".".join([*wurzel, *(knoten.module or "").split(".")]).strip("."))
        elif isinstance(knoten, ast.Import):
            for alias in knoten.names:
                namen.add(alias.name.removeprefix("edusharing."))
    return namen


def _module(unterhalb: str = "") -> list[Path]:
    return [p for p in sorted(QUELLE.rglob("*.py"))
            if "_generated" not in p.parts
            and (unterhalb in p.relative_to(QUELLE).parts if unterhalb else True)]


def _verstoesse(pfade: list[Path], verboten: tuple[str, ...]) -> list[str]:
    gefunden = []
    for pfad in pfade:
        if pfad.name in MONTAGE:
            continue
        for name in sorted(_importe(pfad)):
            if name.split(".")[0] in verboten:
                gefunden.append(f"{pfad.relative_to(QUELLE).as_posix()} -> {name}")
    return gefunden


def test_die_ressourcenschicht_greift_nicht_nach_oben():
    """Kein Modul unter ``edusharing/`` -- ausser der Montagestelle -- darf
    ``flows`` oder ``agent`` importieren."""
    unten = [p for p in _module()
             if not set(p.relative_to(QUELLE).parts) & set(OBERE_SCHICHTEN)]
    assert _verstoesse(unten, OBERE_SCHICHTEN) == []


def test_kein_ablauf_importiert_den_agenten():
    """``flows/`` liegt unter ``agent/``. Ein Ablauf, der sich dort etwas
    holt, dreht die Richtung um."""
    assert _verstoesse(_module("flows"), ("agent",)) == []


def test_der_waechter_findet_einen_verstoss():
    """Ohne diesen Test waere ein Waechter, der versehentlich nichts mehr
    liest, gruen -- und damit wertlos."""
    assert _importe(QUELLE / "repository.py") >= {"flows"}
    assert _verstoesse([QUELLE / "flows" / "tree.py"], ("errors",)) == [
        "flows/tree.py -> errors"]
