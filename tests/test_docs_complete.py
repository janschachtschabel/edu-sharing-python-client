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
    return gefunden


def _in_code_geschrieben(text: str) -> set[str]:
    """Alle Bezeichner, die in einer Code-Zaun oder Inline-Code stehen.

    Nur dort: ein Name, der bloss im Fliesstext auftaucht, ist erwaehnt, nicht
    dokumentiert -- und ``delete`` als deutsches Wort gibt es ohnehin nicht.
    """
    stuecke = re.findall(r"```.*?```", text, re.S) + re.findall(r"`[^`\n]+`", text)
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


# --- Und stimmen die genannten Felder? ------------------------------------
#
# Der Test oben prueft, dass ein Name vorkommt -- nicht, dass er richtig ist.
# Beim Schreiben der Referenz am 29.08.2026 waren sechs Behauptungen falsch:
# ``Identity.is_guest`` (heisst ``is_anonymous``), ``Identity.groups`` (gibt es
# nicht), ``About.version`` (heisst ``repository_version``),
# ``FacetValue.label`` (gibt es nicht), ``Member.authority`` (heisst ``name``)
# und ``ExtractedText.method`` (gibt es nicht). Alle sechs standen in einer
# Tabellenzeile der Form ``| `Klasse` | `feld`, `feld` |``.

#: Eine Tabellenzeile, ganz gleich was in Spalte 1 steht.
_ZEILE = re.compile(r"^\|(.+?)\|(.+)\|\s*$", re.M)
#: Der Klassenname, entweder allein in Spalte 1 oder am Anfang von Spalte 2.
_KLASSE = re.compile(r"^\s*`([A-Z][A-Za-z0-9_]*)`")
_FELD = re.compile(r"`([a-z_][a-z0-9_]*)`")


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


def _hat(klasse: type, feld: str) -> bool:
    import dataclasses
    if hasattr(klasse, feld):
        return True
    if dataclasses.is_dataclass(klasse):
        return feld in {f.name for f in dataclasses.fields(klasse)}
    return feld in getattr(klasse, "__annotations__", {})


def test_jedes_genannte_feld_gibt_es_wirklich():
    """Eine Zeile ``| `Klasse` | `feld` |`` behauptet etwas Pruefbares.

    Ausgenommen sind Namen, die anderswo als oeffentliche Funktion existieren
    -- ``| `UnsafeUrlError` | `check_url` hat abgelehnt |`` nennt keinen
    Feldnamen, sondern verweist.

    **Grenze:** geprueft werden Tabellenzeilen, nicht Code-Bloecke. Ein
    ``got.method`` in einem Beispiel faellt hier nicht auf -- dafuer muesste
    der Test wissen, welche Klasse hinter ``got`` steht. Die Ausgaben in den
    Code-Bloecken wurden am 29.08.2026 von Hand gegen die Feldlisten der
    Datenklassen geprueft.
    """
    klassen = _klassen_der_bibliothek()
    anderswo = set(oeffentliche_namen())
    falsch: list[str] = []
    for datei, pfad in REFERENZEN.items():
        for links, rechts in _ZEILE.findall(pfad.read_text(encoding="utf-8")):
            # Die Klasse steht entweder allein links (``| `Facet` | `values` |``)
            # oder rechts am Anfang (``| `repo.about()` | `About` -- `version` |``).
            treffer = _KLASSE.match(links.strip()) or _KLASSE.match(rechts.strip())
            name = treffer.group(1) if treffer else ""
            klasse = klassen.get(name)
            if klasse is None:
                continue
            rest = rechts if _KLASSE.match(links.strip()) else rechts.split("`", 3)[-1]
            for feld in _FELD.findall(rest):
                if feld not in anderswo and not _hat(klasse, feld):
                    falsch.append(f"{datei}: {name}.{feld} gibt es nicht")

    assert not falsch, "\n  " + "\n  ".join(falsch)


# --- Und stimmen die Variablennamen? --------------------------------------
#
# ``TEXT_EXTRACTION_URL`` stand in der Referenz und im Skill; die Variable
# heisst ``EDU_SHARING_TEXT_EXTRACTION_URL``. Wer den falschen Namen setzt,
# bekommt kein Fehlverhalten, sondern eine Verweigerung ohne erkennbaren
# Grund -- ``from_env()`` sagt nur, dass die Variable fehlt.

#: Alles, was nach Konfiguration aussieht. Eng gefasst, damit ``CONSUMER``,
#: ``GROUP_lehrer`` oder ``TO_BE_CHECKED`` nicht mitgezaehlt werden.
_UMGEBUNG = re.compile(
    r"`((?:EDU_SHARING|B_API|METADATA_AGENT)_[A-Z0-9_]+"
    r"|[A-Z][A-Z0-9_]*_(?:URL|KEY|TOKEN|PASSWORD))`")

#: Jede Datei, die Namen behauptet. Der Skill gehoert dazu: er nennt sie in
#: einer Tabelle, und ein Skill mit falschen Namen ist schlimmer als keiner.
BEHAUPTEND = [
    "README.md", "README.de.md",
    "docs/REFERENCE.md", "docs/REFERENCE.de.md",
    "docs/FLOWS.md", "docs/FLOWS.de.md",
    "docs/ARCHITECTURE.md", "docs/ARCHITECTURE.de.md",
    ".claude/skills/edu-sharing-python/SKILL.md",
    ".claude/skills/edu-sharing-python/SKILL.de.md",
]


def test_jeder_genannte_variablenname_kommt_im_code_vor():
    """Ein Name, den niemand liest, ist eine Anleitung ins Leere.

    Als Beleg zaehlt ein Vorkommen in ``src/`` oder in einem Beispiel -- die
    Beispiele lesen eigene Variablen (``EDU_SHARING_MDS``), die die Bibliothek
    selbst nicht kennt.
    """
    belegt = "\n".join(
        p.read_text(encoding="utf-8")
        for ordner in (QUELLE, WURZEL / "docs" / "examples")
        for p in sorted(ordner.rglob("*.py"))
        if "_generated" not in p.parts
    )
    erfunden: list[str] = []
    for datei in BEHAUPTEND:
        pfad = WURZEL / datei
        if not pfad.exists():
            continue
        for name in sorted(set(_UMGEBUNG.findall(pfad.read_text(encoding="utf-8")))):
            if f'"{name}"' not in belegt and f"'{name}'" not in belegt:
                erfunden.append(f"{datei}: {name}")

    assert not erfunden, "\n  " + "\n  ".join(erfunden)


# --- Der Skill ------------------------------------------------------------
#
# ``.claude/skills/edu-sharing-python/SKILL.md`` ist eine Wegweisertabelle fuer
# ein Modell: "diese Aufgabe -> dieser Aufruf". Ein Wegweiser, der auf einen
# Aufruf zeigt, den es nicht gibt, ist schlimmer als keiner -- das Modell
# schreibt den Code trotzdem. Und ein Wegweiser, der einen Ablauf auslaesst,
# laesst das Modell ihn von Hand nachbauen.

#: Beide Sprachfassungen. Die deutsche ist keine Zierde -- sie steht denselben
#: Lesern gegenueber und wuerde ohne Waechter als erste veralten.
SKILLS = {
    name: WURZEL / ".claude" / "skills" / "edu-sharing-python" / name
    for name in ("SKILL.md", "SKILL.de.md")
}


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


# --- Und zeigen die Verweise irgendwohin? ---------------------------------

#: Jede Datei mit Verweisen, die stimmen muessen. Die Audits stehen nicht
#: dabei: sie sind Momentaufnahmen und werden nicht mitgepflegt.
VERWEISEND = [*BEHAUPTEND, "CHANGELOG.md"]

_LINK = re.compile(r"]\(([^)#][^)]*)\)")


def test_jeder_verweis_zeigt_auf_eine_datei_die_es_gibt():
    """Ein toter Verweis ist die stillste Form von veralteter Doku.

    Umbenennen oder verschieben faellt sonst erst auf, wenn jemand klickt --
    und in einer Referenz mit 85 Verweisen klickt niemand alle durch.
    """
    kaputt: list[str] = []
    for datei in VERWEISEND:
        pfad = WURZEL / datei
        if not pfad.exists():
            continue
        for ziel in _LINK.findall(pfad.read_text(encoding="utf-8")):
            if ziel.startswith(("http://", "https://", "mailto:")):
                continue
            if not (pfad.parent / ziel.split("#")[0]).resolve().exists():
                kaputt.append(f"{datei} -> {ziel}")

    assert not kaputt, "\n  " + "\n  ".join(kaputt)


# --- Und stimmt die versprochene Ergebnisform? -----------------------------
#
# Ein Ablauf beschreibt seine Rueckgabe als ``{a, b, c}``. Wer einen Schluessel
# nicht nennt, laesst ihn niemanden lesen -- und ausgerechnet die
# ungenannten waren die wichtigen: ``placement.failed`` sagt, dass der Weg nach
# oben verweigert wurde, und ohne ihn liest sich ein leerer ``path`` als "der
# Knoten liegt nirgends" statt "Sie duerfen nicht sehen, wo er liegt". Am
# 31.08.2026 ist genau das einem Pruefskript passiert, das die Bibliothek
# benutzen sollte.

ABLAEUFE = WURZEL / "src" / "edusharing" / "flows"
_VERSPROCHEN = re.compile(r"``\{([a-z_,\s]+)\}``")


def _letzte_woertliche_rueckgabe(funktion: ast.AST) -> set[str] | None:
    """Die Schluessel des zurueckgegebenen dict-Literals, falls es eins gibt."""
    gefunden = None
    for knoten in ast.walk(funktion):
        if isinstance(knoten, ast.Return) and isinstance(knoten.value, ast.Dict):
            gefunden = {s.value for s in knoten.value.keys
                        if isinstance(s, ast.Constant) and isinstance(s.value, str)}
    return gefunden


def test_jeder_ablauf_nennt_jeden_schluessel_den_er_liefert():
    """Was zurueckkommt, steht im Docstring -- vollstaendig.

    Geprueft wird nur, wo die Funktion ein dict-Literal zurueckgibt. Wo sie
    einen Helfer ruft (``result_as_dict``), kann das hier nichts sagen, und das
    zu behaupten waere schlimmer als die Luecke.
    """
    fehlend: list[str] = []
    for pfad in sorted(ABLAEUFE.glob("*.py")):
        baum = ast.parse(pfad.read_text(encoding="utf-8"), filename=str(pfad))
        for knoten in baum.body:
            if not isinstance(knoten, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            treffer = _VERSPROCHEN.search(ast.get_docstring(knoten) or "")
            echte = _letzte_woertliche_rueckgabe(knoten)
            if not treffer or echte is None:
                continue
            genannt = {s.strip() for s in treffer.group(1).split(",") if s.strip()}
            offen = sorted(echte - genannt)
            if offen:
                fehlend.append(f"{pfad.name}:{knoten.name} liefert auch {offen}")

    assert not fehlend, "\n  " + "\n  ".join(fehlend)


def test_der_waechter_sieht_auch_zuweisungen_in_einem_try_block():
    """Sonst hat er einen blinden Fleck, und der ist am 31.08.2026 aufgefallen.

    ``__version__`` wird in einem ``try``/``except`` zugewiesen -- fuer den
    Fall, dass das Paket gar nicht installiert ist. Der Waechter las nur
    ``baum.body`` und sah die Zuweisung deshalb nicht; der Eintrag in der
    Referenz musste von Hand geschrieben werden, und ein naechster Name an
    derselben Stelle waere still durchgerutscht.
    """
    assert "__version__" in oeffentliche_namen()
