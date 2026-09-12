"""Jeder oeffentliche Name steht in beiden Referenzen.

Die Frage "ist alles dokumentiert?" war bisher nur zu beantworten, indem jemand
sie von Hand nachzaehlt -- und die Antwort galt bis zum naechsten Commit. Am
29.08.2026 ergab so ein Durchgang elf oeffentliche Namen, die in keiner Datei
vorkamen: ``repo.remove_from_collection``, ``node.remove_keywords``,
``collections.remove``, ``vocab.suggest``, ``BildungsAPI.models``,
``TextExtraction.ping``, ``MetadataAgent.schemas``, ``ChangePlan``,
``format_hit``, ``check_url``.

Dieser Test macht daraus eine Wache. Als "oeffentlich" gilt, was ein Modul in
``__all__`` nennt -- jedes Modul der Handschicht hat eines -- samt der
oeffentlichen Methoden der so genannten Klassen. Als "dokumentiert" gilt, was
in ``docs/REFERENCE.md`` **und** ``docs/REFERENCE.de.md`` in Code-Schreibweise
vorkommt. Beide, denn eine nur halb uebersetzte Referenz ist fuer die eine
Haelfte der Leserschaft keine.

Hier steht die Frage nach der **Vollstaendigkeit**: jeder oeffentliche Name,
jeder Ablauf, jede Tuer, jedes Feld einer Klasse, und dasselbe fuer das
Skill-Buendel. Ob das Behauptete auch **stimmt** -- ein Feld in einer
Tabellenzeile, ein Variablenname, ein Verweis, die versprochene Ergebnisform,
die Parameter eines dokumentierten Aufrufs -- fragt ``test_docs_claims``, das
die geteilten Helfer von hier holt.
"""

import ast
import re
from pathlib import Path

import pytest

WURZEL = Path(__file__).resolve().parent.parent
QUELLE = WURZEL / "src" / "edusharing"
REFERENZEN = {
    "REFERENCE.md": WURZEL / "docs" / "REFERENCE.md",
    "REFERENCE.de.md": WURZEL / "docs" / "REFERENCE.de.md",
}

#: ``_sync`` spiegelt die asynchrone Oberflaeche Name fuer Name. Die Referenz
#: sagt das einmal, statt jeden Eintrag zweimal zu fuehren.
NICHT_GEPRUEFT = {"_sync.py"}


def _aus_all(baum: ast.Module) -> set[str]:
    for knoten in baum.body:
        if isinstance(knoten, ast.Assign) and any(
                getattr(ziel, "id", "") == "__all__" for ziel in knoten.targets):
            return {e.value for e in knoten.value.elts
                    if isinstance(e, ast.Constant) and isinstance(e.value, str)}
    return set()


def oeffentliche_namen() -> dict[str, str]:
    """Jeder oeffentliche Name, und woher er stammt."""
    gefunden: dict[str, str] = {}
    for pfad in sorted(QUELLE.rglob("*.py")):
        if "_generated" in pfad.parts or pfad.name in NICHT_GEPRUEFT:
            continue
        baum = ast.parse(pfad.read_text(encoding="utf-8"), filename=str(pfad))
        exportiert = _aus_all(baum)
        herkunft = pfad.relative_to(QUELLE).as_posix()
        # Auch die Rumpfe von try/except auf oberster Ebene: ``__version__``
        # wird dort zugewiesen, fuer den Fall ohne Installation. Wer nur
        # ``baum.body`` liest, hat genau dort einen blinden Fleck.
        oberste: list[ast.stmt] = []
        for knoten in baum.body:
            oberste.append(knoten)
            if isinstance(knoten, ast.Try):
                oberste.extend(knoten.body)
                for behandler in knoten.handlers:
                    oberste.extend(behandler.body)
        for knoten in oberste:
            if isinstance(knoten, ast.ClassDef) and knoten.name in exportiert:
                gefunden.setdefault(knoten.name, herkunft)
                for eintrag in knoten.body:
                    if (isinstance(eintrag, (ast.FunctionDef, ast.AsyncFunctionDef))
                            and not eintrag.name.startswith("_")):
                        gefunden.setdefault(
                            eintrag.name, f"{herkunft}:{knoten.name}")
            elif (isinstance(knoten, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and knoten.name in exportiert):
                gefunden.setdefault(knoten.name, herkunft)
            elif isinstance(knoten, ast.Assign):
                for ziel in knoten.targets:
                    name = getattr(ziel, "id", "")
                    if name and name != "__all__" and name in exportiert:
                        gefunden.setdefault(name, herkunft)
            # Eine Konstante mit Annotation (``X: tuple[str, ...] = (...)``) ist
            # ein ``AnnAssign`` und rutschte bis zum 11.09.2026 durch: so blieb
            # ``RELATION_TYPES`` undokumentiert, und mit ihm die Frage, welche
            # Beziehungen es ueberhaupt anzulegen gibt.
            elif isinstance(knoten, ast.AnnAssign):
                name = getattr(knoten.target, "id", "")
                if name and name in exportiert:
                    gefunden.setdefault(name, herkunft)
    return gefunden


def _in_code_geschrieben(text: str) -> set[str]:
    """Alle Bezeichner, die in einer Code-Zaun oder Inline-Code stehen.

    Nur dort: ein Name, der bloss im Fliesstext auftaucht, ist erwaehnt, nicht
    dokumentiert -- und ``delete`` als deutsches Wort gibt es ohnehin nicht.

    Die Zaeune kommen zuerst heraus, sonst paart das Inline-Muster deren
    Backticks mit denen echter Spans. Und ein Inline-Span darf umbrechen: ein
    Umbruch mittendrin gehoert der Zeilenbreite, nicht der Bedeutung.
    """
    zaeune = re.findall(r"```.*?```", text, re.S)
    ohne_zaeune = re.sub(r"```.*?```", "", text, flags=re.S)
    stuecke = zaeune + re.findall(r"`[^`]+`", ohne_zaeune, re.S)
    return {w for stueck in stuecke
            for w in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", stueck)}


def test_jeder_oeffentliche_name_steht_in_beiden_referenzen():
    """Wer die Oberflaeche erweitert, erweitert die Referenz -- in beiden Sprachen.

    Faellt dieser Test fuer einen neuen Namen, ist die Frage nicht "wie trage
    ich ihn nach", sondern zuerst: gehoert er ueberhaupt in ``__all__``? Ein
    Helfer, den nur die Bibliothek selbst ruft, gehoert dort nicht hin. Wenn er
    hingehoert, gehoert er auch in die Referenz.
    """
    namen = oeffentliche_namen()
    fehlend: dict[str, list[str]] = {}
    for datei, pfad in REFERENZEN.items():
        assert pfad.exists(), f"{datei} fehlt"
        geschrieben = _in_code_geschrieben(pfad.read_text(encoding="utf-8"))
        offen = sorted(n for n in namen if n not in geschrieben)
        if offen:
            fehlend[datei] = offen

    assert not fehlend, "\n".join(
        f"{datei}: {len(offen)} von {len(namen)} nicht dokumentiert:\n  "
        + "\n  ".join(f"{n}  ({namen[n]})" for n in offen)
        for datei, offen in fehlend.items()
    )


def test_der_waechter_sieht_nur_code_nicht_fliesstext():
    """Gegenprobe: ein Name im Fliesstext gilt nicht als dokumentiert.

    Sonst genuegte es, ihn irgendwo zu erwaehnen, und die Referenz waere ein
    Stichwortverzeichnis statt einer Anleitung.
    """
    assert _in_code_geschrieben("Der Aufruf remove_keywords loescht sie.") == set()
    assert "remove_keywords" in _in_code_geschrieben(
        "Der Aufruf `node.remove_keywords(...)` loescht sie.")
    assert "remove_keywords" in _in_code_geschrieben(
        "```python\nawait node.remove_keywords(['alt'])\n```")


def _klassen_der_bibliothek() -> dict[str, type]:
    """Jede oeffentliche Klasse, ueber ihren Namen erreichbar."""
    import importlib
    gefunden: dict[str, type] = {}
    for pfad in sorted(QUELLE.rglob("*.py")):
        if "_generated" in pfad.parts or pfad.name == "__init__.py":
            continue
        modul = "edusharing." + pfad.relative_to(QUELLE).with_suffix("").as_posix(
            ).replace("/", ".")
        try:
            geladen = importlib.import_module(modul)
        except Exception:  # ein Modul, das nicht laedt, faellt anderswo auf
            continue
        for name in getattr(geladen, "__all__", []):
            wert = getattr(geladen, name, None)
            if isinstance(wert, type):
                gefunden.setdefault(name, wert)
    return gefunden


BEHAUPTEND = [
    "README.md", "README.de.md",
    "docs/REFERENCE.md", "docs/REFERENCE.de.md",
    "docs/FLOWS.md", "docs/FLOWS.de.md",
    "docs/ARCHITECTURE.md", "docs/ARCHITECTURE.de.md",
    ".claude/skills/edu-sharing-python/SKILL.md",
    ".claude/skills/edu-sharing-python/SKILL.de.md",
    ".claude/skills/edu-sharing-python/reference/TRAPS.md",
    ".claude/skills/edu-sharing-python/reference/TRAPS.de.md",
]


# --- Der Skill ------------------------------------------------------------
#
# ``.claude/skills/edu-sharing-python/SKILL.md`` ist der Einstieg eines Modells
# in die Bibliothek: Rezepte und jeder Aufruf mit seinen Parametern (seit dem
# 11.09.2026; vorher eine Wegweisertabelle "diese Aufgabe -> dieser Aufruf").
# Ein Einstieg, der auf einen Aufruf zeigt, den es nicht gibt, ist schlimmer
# als keiner -- das Modell schreibt den Code trotzdem. Und einer, der einen
# Ablauf auslaesst, laesst das Modell ihn von Hand nachbauen.

#: Beide Sprachfassungen. Die deutsche ist keine Zierde -- sie steht denselben
#: Lesern gegenueber und wuerde ohne Waechter als erste veralten.
SKILLS = {
    name: WURZEL / ".claude" / "skills" / "edu-sharing-python" / name
    for name in ("SKILL.md", "SKILL.de.md")
}


def buendel(name: str) -> str:
    """Ein Einstieg und die Nachschlagedateien derselben Sprache unter ``reference/``.

    Seit dem 11.09.2026 traegt der Skill-Ordner die Referenz selbst mit. Was
    ein Modell dort findet, hat es -- auch ausserhalb dieses Repositoriums.
    """
    einstieg = SKILLS[name]
    deutsch = name.endswith(".de.md")
    nachschlag = [p for p in sorted((einstieg.parent / "reference").glob("*.md"))
                  if p.name.endswith(".de.md") == deutsch]
    return "\n".join(p.read_text(encoding="utf-8") for p in [einstieg, *nachschlag])


@pytest.mark.parametrize("name", sorted(SKILLS))
def test_der_skill_kennt_jeden_ablauf_und_erfindet_keinen(name):
    """Alle Ablaeufe, und nur echte -- in jeder Sprachfassung."""
    from edusharing.flows import Flows

    pfad = SKILLS[name]
    assert pfad.exists(), f"{name} fehlt"
    genannt = set(re.findall(r"repo\.flows\.([a-z_]+)",
                             pfad.read_text(encoding="utf-8")))
    echte = {n for n in dir(Flows) if not n.startswith("_")}

    erfunden = sorted(genannt - echte)
    assert not erfunden, f"{name} nennt Ablaeufe, die es nicht gibt: {erfunden}"

    fehlend = sorted(echte - genannt)
    assert not fehlend, (
        f"{name}: {len(fehlend)} von {len(echte)} Ablaeufen fehlen: {fehlend}")


@pytest.mark.parametrize("name", sorted(SKILLS))
def test_der_skill_erfindet_keine_aufrufe_am_knoten(name):
    """``node.<zubehoer>`` und ``node.<methode>()`` muss es geben."""
    from edusharing.nodes import Node

    pfad = SKILLS[name]
    assert pfad.exists(), f"{name} fehlt"
    text = pfad.read_text(encoding="utf-8")
    genannt = (set(re.findall(r"node\.([a-z_]+)\.[a-z_]+", text))
               | set(re.findall(r"\bnode\.([a-z_]+)\(", text)))
    erfunden = sorted(n for n in genannt if not hasattr(Node, n))
    assert not erfunden, f"{name} nennt am Knoten: {erfunden}"


# --- Erklaert der Skill die ganze Bibliothek? ------------------------------
#
# Die Waechter oben pruefen den Skill auf Ablaeufe und ``node.*``-Aufrufe.
# Beides war lueckenlos -- und trotzdem fehlten am 31.08.2026 drei ganze
# Bereiche: die Vokabular-API (nur der Ablauf war genannt, nicht
# ``repo.vocab.resolve_all``, die Korrektur fuer mehrdeutige Labels), die
# Instanz-Auskunft, und ``repo.people`` stand als blosser Stern da.
#
# Der Einstieg ist keine Referenz -- die liegt daneben in ``reference/`` --,
# aber einer, der eine Tuer nicht nennt, fuehrt niemanden hindurch. Eine KI
# liest ihn zuerst, oft als einziges.

#: Zeilen der dreispaltigen Zugriffstabelle: ``| `repo.vocab` | `Vocabulary` | ... |``
_ZUGRIFF = re.compile(r"^\|\s*`(repo|node)\.([a-z_]+)`\s*\|\s*`[A-Z]\w*`\s*\|", re.M)


def zugriffswege() -> set[str]:
    """Die Tueren in die Bibliothek, aus der Referenz abgeleitet.

    Nicht von Hand gepflegt: eine Liste im Test veraltet, sobald ein Zugriff
    dazukommt. Die Referenz nennt sie ohnehin, und dass SIE vollstaendig ist,
    prueft der Test darueber.
    """
    text = REFERENZEN["REFERENCE.md"].read_text(encoding="utf-8")
    return {f"{objekt}.{attribut}" for objekt, attribut in _ZUGRIFF.findall(text)}


@pytest.mark.parametrize("name", sorted(SKILLS))
def test_der_skill_nennt_jede_tuer_in_die_bibliothek(name):
    """Jeder Zugriffsweg kommt im Skill vor -- sonst ist der Bereich unsichtbar."""
    wege = zugriffswege()
    assert len(wege) >= 12, f"die Zugriffstabelle wurde nicht erkannt: {wege}"

    text = SKILLS[name].read_text(encoding="utf-8")
    fehlend = sorted(w for w in wege if w not in text)
    assert not fehlend, (
        f"{name} nennt {len(fehlend)} von {len(wege)} Zugriffswegen nicht: "
        f"{', '.join(fehlend)}")


# Der Test darueber prueft die Tueren -- jeden Zugriffsweg. Er sagt nichts
# darueber, was man tut, wenn man hindurch ist: ``repo.nodes`` stand darin,
# ``repo.create_node`` nicht, obwohl acht Beispiele damit anfangen.
#
# Das schaerfere Mass ist ableitbar statt gepflegt: Was eine lauffaehige
# Anwendung in diesem Repositorium benutzt, muss der Skill nennen. Kommt ein
# Beispiel dazu, waechst das Mass mit -- ohne dass jemand eine Liste pflegt.

BEISPIELE = WURZEL / "docs" / "examples"


def namen_der_beispiele() -> dict[str, str]:
    """Jeder oeffentliche Name, den ein Beispiel benutzt, und wo zuerst."""
    namen = oeffentliche_namen()
    benutzt: dict[str, str] = {}
    for pfad in sorted(BEISPIELE.glob("*.py")):
        for knoten in ast.walk(ast.parse(pfad.read_text(encoding="utf-8"))):
            if isinstance(knoten, ast.Name):
                wort = knoten.id
            elif isinstance(knoten, ast.Attribute):
                wort = knoten.attr
            elif isinstance(knoten, ast.alias):
                wort = knoten.name
            else:
                continue
            if wort in namen:
                benutzt.setdefault(wort, pfad.name)
    return benutzt


@pytest.mark.parametrize("name", sorted(SKILLS))
def test_der_skill_nennt_was_die_beispiele_benutzen(name):
    """Was eine echte Anwendung braucht, darf der Wegweiser nicht verschweigen."""
    benutzt = namen_der_beispiele()
    assert len(benutzt) >= 60, (
        f"die Beispiele wurden nicht gelesen: nur {len(benutzt)} Namen gefunden")

    geschrieben = _in_code_geschrieben(SKILLS[name].read_text(encoding="utf-8"))
    fehlend = sorted(n for n in benutzt if n not in geschrieben)
    assert not fehlend, (
        f"{name} nennt {len(fehlend)} von {len(benutzt)} Namen nicht, die "
        f"Beispiele benutzen:\n  "
        + "\n  ".join(f"{n}  ({benutzt[n]})" for n in fehlend))


def test_der_waechter_wuerde_einen_fehlenden_namen_bemerken():
    """Sonst prueft der Test darueber nichts.

    Kein Sonderweg: derselbe Vergleich, nur gegen einen Text, in dem ein Name
    fehlt, den die Beispiele benutzen.
    """
    benutzt = namen_der_beispiele()
    assert "create_node" in benutzt, "das Mass selbst ist kaputt"

    ohne = SKILLS["SKILL.md"].read_text(encoding="utf-8").replace(
        "create_node", "xxx")
    geschrieben = _in_code_geschrieben(ohne)
    assert "create_node" not in geschrieben


# Das Mass darueber -- "was ein Beispiel benutzt" -- ist die Untergrenze. Der
# Skill ist inzwischen darueber hinaus: er nennt jeden oeffentlichen Namen.
# Dieser Test haelt das fest, denn ein Skill, der eine neue Funktion
# verschweigt, laesst die KI sie von Hand nachbauen. Wer die
# Oberflaeche erweitert, erweitert beide Sprachfassungen des Skills mit.
#
# Seit dem 11.09.2026 gilt das fuer das Buendel, nicht fuer den Einstieg
# allein: 370 Namen samt Feldern und Konstanten passen nicht in einen
# Einstieg unter 500 Zeilen, und die Referenz liegt jetzt im Skill-Ordner.
# Die Tueren, die Ablaeufe und die Namen der Beispiele bleiben Sache des
# Einstiegs -- die Tests darueber.


@pytest.mark.parametrize("name", sorted(SKILLS))
def test_der_skill_nennt_jeden_oeffentlichen_namen(name):
    """Alles aus ``__all__`` steht im Skill-Buendel -- in beiden Sprachfassungen."""
    namen = oeffentliche_namen()
    geschrieben = _in_code_geschrieben(buendel(name))
    fehlend = sorted(n for n in namen if n not in geschrieben)
    assert not fehlend, (
        f"{name} nennt {len(fehlend)} von {len(namen)} oeffentlichen Namen "
        f"nicht:\n  " + "\n  ".join(f"{n}  ({namen[n]})" for n in fehlend))


# --- Und stehen die Felder der Objekte drin? ------------------------------
#
# ``test_jeder_oeffentliche_name_steht_in_beiden_referenzen`` misst gegen
# ``__all__`` -- also gegen Klassen und Funktionen, nicht gegen die Felder,
# die eine Klasse traegt. Darum fehlten ``Swimlane.heading``, ``Group.signup``,
# ``Relation.created_by`` und 36 weitere in der Referenz, obwohl sie als
# vollstaendig galt. Wer ein Objekt zurueckbekommt, muss nachlesen koennen,
# was darauf ist; sonst raet er, und Raten erfindet Feldnamen.


def felder_der_klassen() -> dict[str, list[str]]:
    """Jedes oeffentliche Feld jeder oeffentlichen Klasse."""
    gefunden: dict[str, list[str]] = {}
    for name, klasse in sorted(_klassen_der_bibliothek().items()):
        felder = set(getattr(klasse, "__annotations__", {}))
        felder |= {n for n, wert in vars(klasse).items() if isinstance(wert, property)}
        offen = sorted(f for f in felder if not f.startswith("_"))
        if offen:
            gefunden[name] = offen
    return gefunden


@pytest.mark.parametrize("datei", sorted(REFERENZEN))
def test_jedes_feld_jeder_klasse_steht_in_der_referenz(datei):
    """Wer ein Objekt zurueckgibt, dokumentiert, was darauf ist."""
    felder = felder_der_klassen()
    assert len(felder) >= 25, f"die Klassen wurden nicht gefunden: {len(felder)}"

    geschrieben = _in_code_geschrieben(REFERENZEN[datei].read_text(encoding="utf-8"))
    fehlend = [(kl, [f for f in fs if f not in geschrieben])
               for kl, fs in felder.items()]
    fehlend = [(kl, fs) for kl, fs in fehlend if fs]
    anzahl = sum(len(fs) for _, fs in fehlend)
    assert not fehlend, (
        f"{datei}: {anzahl} Felder aus {len(fehlend)} Klassen fehlen:\n  "
        + "\n  ".join(f"{kl}: {', '.join(fs)}" for kl, fs in fehlend))


