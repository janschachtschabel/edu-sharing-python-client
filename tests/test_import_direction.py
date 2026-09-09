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
import textwrap
from pathlib import Path

QUELLE = Path(__file__).resolve().parent.parent / "src" / "edusharing"

#: Die beiden Dateien, die nach oben greifen duerfen, und warum.
#: ``repository.py`` ist die Montagestelle -- sie verdrahtet die Schichten und
#: haengt ``repo.flows`` an; ``__init__.py`` ist die Paketoberflaeche, die die
#: oeffentlichen Namen aller Schichten nennt. Beide bauen nichts, sie reichen
#: durch.
MONTAGE = {"repository.py", "__init__.py"}  # relativ zu ``edusharing/``

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
            pfad = [*wurzel, *(knoten.module or "").split(".")]
            namen.add(".".join(pfad).strip("."))
            # ``from . import flows`` nennt sein Ziel im Alias, nicht im
            # Modul. Ohne diese Zeile war genau die Form unsichtbar, die
            # ``nodes.py`` verwendet (``from . import nodes_write, placement,
            # ratings``) -- ein Modul haette sich so ``flows`` holen koennen,
            # ohne dass die Wache anschlaegt (Review 08.09.2026).
            for alias in knoten.names:
                namen.add(".".join([*pfad, alias.name]).strip("."))
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
        # Der Pfad, nicht der Dateiname: sonst waeren auch
        # ``flows/__init__.py`` und ``agent/__init__.py`` von allem befreit.
        if pfad.relative_to(QUELLE).as_posix() in MONTAGE:
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
    # Die Form, die der Waechter frueher uebersah.
    assert "placement" in _importe(QUELLE / "nodes.py")
    # Enthalten, nicht gleich: seit der Waechter auch die Aliasse liest,
    # meldet er zusaetzlich ``errors.EduSharingError`` -- beide Angaben sind
    # richtig, und der Test soll nicht an ihrer Zahl haengen.
    assert "flows/tree.py -> errors" in _verstoesse(
        [QUELLE / "flows" / "tree.py"], ("errors",))


# --- Importe in Funktionsruempfen (Audit ARC-3) --------------------------

#: Ein Import im Rumpf einer Funktion haelt einen Zyklus offen, statt ihn
#: aufzuloesen: die beiden Module brauchen einander weiterhin, nur nicht mehr
#: beim Laden. Wer eines davon liest, sieht seine Abhaengigkeiten nicht mehr
#: im Kopf der Datei stehen.
#:
#: Am 03.09.2026 gab es fuenf davon, vier mal ``from .nodes import Node``
#: (Audit ARC-3). ``Nodes.wrap`` hat sie abgeloest -- die Fabrik gab es
#: implizit schon, ``Nodes`` baute an vier Stellen selbst ``Node(data, self)``.
#:
#: Was hier steht, ist eine bewusste Ausnahme mit Begruendung, kein Rueckstand.
#: Der Schluessel nennt auch die **Funktion**: die Begruendung gilt fuer eine
#: Stelle, und ohne den Namen erlaubte der Eintrag jeden Rumpfimport dieses
#: Moduls irgendwo in dieser Datei -- nachgewiesen an ``Skills._summary``
#: (Pruefung 09.09.2026).
#:
#: Der Name ist der **blanke** Funktionsname, nicht der qualifizierte. Wer
#: den Import aus ``Skills.registry`` entfernt, laesst den Eintrag verwaisen
#: -- und ``test_die_ausnahmen_gibt_es_noch`` faengt genau das. Nur eine
#: absichtlich gleichnamige Funktion auf Modulebene erbte ihn; dafuer
#: braeuchte es den qualifizierten Namen, und diesen Fall muesste jemand
#: herstellen wollen (Pruefung 09.09.2026, gemessen und angenommen).
ERLAUBT = {
    # ``skills_registry`` braucht ``skills`` fuer die Konventionen, und
    # ``Skills.registry`` braucht ``load_registry``. Den Rumpf zu verschieben
    # und zurueckzuexportieren -- der Vorschlag des Berichts -- taeuschte den
    # Zyklus nur an eine andere Stelle: die beiden Module bleiben zwei Haelften
    # einer Sache, und ein Import im Rumpf sagt das ehrlicher als ein Re-Export.
    ("skills.py", "registry", "skills_registry"),
}


def _eigener_rumpf(fn: ast.AST) -> list[ast.AST]:
    """Die Knoten im **eigenen** Rumpf, ohne verschachtelte Funktionen.

    ``ast.walk`` stiege in die mit ab -- und weil jede von ihnen vom
    aeusseren Rundgang selbst gefunden wird, kaeme derselbe Import zweimal:
    einmal der Funktion zugeschrieben, in deren Rumpf er gar nicht steht.
    Eine Ausnahme fuer so eine Stelle braeuchte dann zwei Eintraege in
    ``ERLAUBT``, einen davon unwahr (Pruefung 09.09.2026).

    Eine verschachtelte **Klasse** wird betreten: ihre Methoden sind selbst
    Funktionen und fallen hier heraus, ein Import in ihrem Klassenrumpf
    steht aber im Rumpf dieser Funktion.
    """
    gefunden: list[ast.AST] = []
    stapel = list(ast.iter_child_nodes(fn))
    while stapel:
        knoten = stapel.pop()
        if isinstance(knoten, ast.FunctionDef | ast.AsyncFunctionDef):
            continue
        gefunden.append(knoten)
        stapel.extend(ast.iter_child_nodes(knoten))
    return gefunden


def _rumpfimporte_aus(baum: ast.AST, datei: str) -> list[tuple[str, int, str, str]]:
    """Jeder Import, der im Rumpf einer Funktion steht, aus einem Baum."""
    gefunden = []
    for knoten in ast.walk(baum):
        if not isinstance(knoten, ast.FunctionDef | ast.AsyncFunctionDef):
            continue
        for innen in _eigener_rumpf(knoten):
            if isinstance(innen, ast.ImportFrom):
                gefunden.append((datei, innen.lineno, knoten.name,
                                 innen.module or ""))
            elif isinstance(innen, ast.Import):
                gefunden.append((datei, innen.lineno, knoten.name,
                                 innen.names[0].name))
    # Nach Zeile, damit die Verstossmeldung in Lesereihenfolge steht --
    # der Abstieg oben nimmt den Stapel von hinten.
    return sorted(gefunden, key=lambda e: e[1])


def _rumpfimporte() -> list[tuple[str, int, str, str]]:
    """Dasselbe ueber den ganzen Quellordner."""
    gefunden = []
    for pfad in sorted(QUELLE.rglob("*.py")):
        if "_generated" in pfad.parts:
            continue
        baum = ast.parse(pfad.read_text(encoding="utf-8"), filename=str(pfad))
        gefunden.extend(
            _rumpfimporte_aus(baum, pfad.relative_to(QUELLE).as_posix()))
    return gefunden


def test_kein_modul_importiert_im_funktionsrumpf():
    """Was ein Modul braucht, steht in seinem Kopf."""
    verstoesse = [
        f"{datei}:{zeile} in {funktion}() -- from {modul}"
        for datei, zeile, funktion, modul in _rumpfimporte()
        if (datei, funktion, modul) not in ERLAUBT
    ]
    assert not verstoesse, (
        "Import im Funktionsrumpf -- entweder aufloesen oder in ERLAUBT "
        "eintragen, mit dem Grund:\n  " + "\n  ".join(verstoesse))


def test_die_ausnahmen_gibt_es_noch():
    """Eine Ausnahme fuer etwas, das es nicht mehr gibt, ist eine Karteileiche
    -- und die naechste Person haelt sie fuer eine Regel."""
    tatsaechlich = {(d, f, m) for d, _, f, m in _rumpfimporte()}
    verwaist = sorted(ERLAUBT - tatsaechlich)
    assert not verwaist, f"in ERLAUBT, aber nicht mehr im Code: {verwaist}"


def test_ein_verschachtelter_import_wird_einmal_gemeldet():
    """Gegenprobe am Waechter selbst.

    ``ast.walk`` steigt in verschachtelte Funktionen ab, und weil die vom
    aeusseren Rundgang selbst gefunden werden, kam derselbe Import **zweimal**
    -- einmal ``aussen()`` zugeschrieben, in dessen Rumpf er nicht steht. Der
    Waechter wurde davon nicht loechrig, nur ungenau: eine Ausnahme fuer eine
    verschachtelte Stelle braeuchte zwei Eintraege in ``ERLAUBT``, einen davon
    unwahr (Pruefung 09.09.2026).
    """
    quelle = textwrap.dedent("""
        def aussen():
            def innen():
                from x import y
                return y
            return innen
    """)
    gefunden = _rumpfimporte_aus(ast.parse(quelle), "probe.py")
    assert [(f, m) for _, _, f, m in gefunden] == [("innen", "x")], gefunden
