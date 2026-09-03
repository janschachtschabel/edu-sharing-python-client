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


def test_der_waechter_liest_auch_einen_umgebrochenen_code_span():
    """Ein Span, der ueber eine Zeile laeuft, zerriss die Zuordnung.

    Gefunden am 31.08.2026 in README.md: ``answers `500\nAccessDeniedException`.
    The library translates that to `PermissionDeniedError``` -- das Muster
    konnte den ersten Span nicht fassen, paarte dessen schliessende Backtick
    mit der oeffnenden des naechsten und hielt die Prosa dazwischen fuer Code.

    Zwei Fehlerrichtungen, und die zweite ist die schlimmere: ein Name, der nur
    im Fliesstext steht, haette als dokumentiert gegolten.
    """
    text = ("answers `500\nAccessDeniedException`. The library translates that "
            "to `PermissionDeniedError` -- as a server error")

    gefunden = _in_code_geschrieben(text)
    assert "AccessDeniedException" in gefunden, "der umgebrochene Span fehlt"
    assert "PermissionDeniedError" in gefunden, "der Span dahinter fehlt"
    # Und die Prosa zwischen den beiden gilt weiterhin nicht als Code:
    assert "translates" not in gefunden, "Fliesstext als Code gezaehlt"


# --- Erklaert der Skill die ganze Bibliothek? ------------------------------
#
# Die Waechter oben pruefen den Skill auf Ablaeufe und ``node.*``-Aufrufe.
# Beides war lueckenlos -- und trotzdem fehlten am 31.08.2026 drei ganze
# Bereiche: die Vokabular-API (nur der Ablauf war genannt, nicht
# ``repo.vocab.resolve_all``, die Korrektur fuer mehrdeutige Labels), die
# Instanz-Auskunft, und ``repo.people`` stand als blosser Stern da.
#
# Der Skill ist eine Wegweisertabelle, keine Referenz -- aber ein Wegweiser,
# der eine Tuer nicht nennt, fuehrt niemanden hindurch. Eine KI hat im
# Normalfall nur ihn geladen, nicht das Repositorium.

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
# Dieser Test haelt das fest, denn eine Wegweisertabelle, die eine neue
# Funktion verschweigt, laesst die KI sie von Hand nachbauen. Wer die
# Oberflaeche erweitert, erweitert beide Sprachfassungen des Skills mit.


@pytest.mark.parametrize("name", sorted(SKILLS))
def test_der_skill_nennt_jeden_oeffentlichen_namen(name):
    """Alles aus ``__all__`` steht im Skill -- in beiden Sprachfassungen."""
    namen = oeffentliche_namen()
    geschrieben = _in_code_geschrieben(SKILLS[name].read_text(encoding="utf-8"))
    fehlend = sorted(n for n in namen if n not in geschrieben)
    assert not fehlend, (
        f"{name} nennt {len(fehlend)} von {len(namen)} oeffentlichen Namen "
        f"nicht:\n  " + "\n  ".join(f"{n}  ({namen[n]})" for n in fehlend))


# --- Und stimmen die dokumentierten Signaturen? ---------------------------
#
# ``repo.resolve(url_or_id)`` stand in beiden Referenzen und versprach "die
# Knoten-ID hinter einer Render-URL". Die Methode heisst so, tut aber etwas
# anderes: ``resolve(prop, label)`` uebersetzt ein Label in einen Vokabular-
# wert. Die Faehigkeit aus der Zeile gab es nie. Kein Waechter bemerkte es --
# Namen wurden geprueft, Signaturen nicht.
#
# Positionelle Argumente werden nach Name UND Reihenfolge geprueft, denn ein
# Leser schreibt sie irgendwann als Schluesselwort. Schluesselwortargumente
# duerfen alles sein, wenn die Methode ``**kwargs`` hat.

_AUFRUF = re.compile(r"repo\.((?:flows\.)?[a-z_]+)\(")
_BEZEICHNER = re.compile(r"[a-z_][a-z_0-9]*")
_FLOW_MODULE = ("find", "collections", "describe", "contents", "curate", "tree",
                "pages", "text", "suggest", "skills", "rerank", "duplicates")


def _aufrufe(text: str, muster: re.Pattern[str] = _AUFRUF):
    """Jeder dokumentierte ``repo.x(...)`` / ``repo.flows.x(...)`` -- inline oder
    in einem ```-Block -- mit seinem rohen Argumenttext. Klammern werden
    gezaehlt, damit ein mehrzeiliger Aufruf ganz bleibt; Kommentare am
    Zeilenende fallen weg. Mit ``muster`` liest es auch ``Klasse(...)``."""
    for m in muster.finditer(text):
        tiefe, i = 1, m.end()
        while i < len(text) and tiefe:
            tiefe += (text[i] == "(") - (text[i] == ")")
            i += 1
        if tiefe:
            continue
        yield m.group(1), re.sub(r"#[^\n]*", "", text[m.end():i - 1])


def _argumente(roh: str) -> list[str]:
    """Am Komma auf Tiefe null getrennt -- eine Liste, ein Dict oder ein Komma
    in einem String bleiben ganz."""
    teile: list[str] = []
    aktuell: list[str] = []
    tiefe = 0
    anfuehrung: str | None = None
    for c in roh:
        if anfuehrung:
            if c == anfuehrung:
                anfuehrung = None
        elif c in "'\"":
            anfuehrung = c
        elif c in "([{":
            tiefe += 1
        elif c in ")]}":
            tiefe -= 1
        if c == "," and tiefe == 0 and not anfuehrung:
            teile.append("".join(aktuell))
            aktuell = []
        else:
            aktuell.append(c)
    teile.append("".join(aktuell))
    return [s.strip() for s in teile if s.strip()]


def _funktion_hinter(name: str):
    """Die Ablauf-Funktion, an die eine ``**kwargs``-Fassadenmethode weiterreicht."""
    import importlib
    import inspect
    for modul in _FLOW_MODULE:
        fn = getattr(importlib.import_module(f"edusharing.flows.{modul}"), name, None)
        if inspect.isfunction(fn):
            return fn
    return None


def _positionelle(ziel) -> list[str]:
    import inspect
    erlaubt = (inspect.Parameter.POSITIONAL_ONLY,
               inspect.Parameter.POSITIONAL_OR_KEYWORD)
    return [n for n, p in inspect.signature(ziel).parameters.items()
            if n != "self" and p.kind in erlaubt]


_PLATZHALTER = object()


def _bindet_nicht(ziel, roh: str, wer: str, *, implizit: int) -> list[str]:
    """Der Aufruf `wer(roh)` gegen ``inspect.signature(ziel).bind_partial``.

    Der Namensvergleich sieht nur Bezeichner: ``folder.id, title=...`` und
    ``"Mappe", [a, b]`` warfen beim Abschreiben TypeError, ohne dass er es
    bemerkte (Audit DOC-1, 03.09.2026). Platzhalter statt Werte; ``implizit``
    zaehlt ``self`` oder das ``repo`` einer Ablauf-Funktion; ``bind_partial``,
    weil eine Tabellenzeile wie ``BildungsAPI(models_cache_seconds=0)`` nur
    einen Knopf zeigt und die Pflichtargumente bewusst weglaesst."""
    import inspect
    positional: list[object] = [_PLATZHALTER] * implizit
    schluessel: dict[str, object] = {}
    for stueck in _argumente(roh):
        if stueck in ("…", "..."):
            continue                        # "und mehr" -- kein Wert
        if stueck.startswith("*"):
            return []                       # entpackt: statisch nicht pruefbar
        name = stueck.split("=", 1)[0].strip()
        if "=" in stueck and _BEZEICHNER.fullmatch(name):
            schluessel[name] = _PLATZHALTER
        else:
            positional.append(_PLATZHALTER)
    try:
        inspect.signature(ziel).bind_partial(*positional, **schluessel)
    except TypeError as fehler:
        return [f"{wer}({' '.join(roh.split())}) bindet nicht: {fehler}"]
    return []


def _repo_ziel(methode: str):
    """Die Methode hinter ``repo.x`` oder ``repo.flows.x`` -- seit dem
    02.09.2026 auch die Fassade, deren 57 dokumentierte Aufrufe dem Waechter
    bis dahin entgingen."""
    from edusharing import AsyncRepository, Repository
    from edusharing.flows import Flows
    if methode.startswith("flows."):
        return getattr(Flows, methode[len("flows."):], None)
    return getattr(Repository, methode, None) or getattr(AsyncRepository, methode, None)


def test_jeder_dokumentierte_repository_aufruf_nennt_echte_parameter():
    """``repo.x(a, b=…)`` muss es geben, und a muss so heissen."""
    import inspect

    falsch: list[str] = []
    for datei in BEHAUPTEND:
        pfad = WURZEL / datei
        if not pfad.exists():
            continue
        for methode, roh in _aufrufe(pfad.read_text(encoding="utf-8")):
            ziel = _repo_ziel(methode)
            if ziel is None:
                falsch.append(f"{datei}: repo.{methode}() gibt es nicht")
                continue
            parameter = inspect.signature(ziel).parameters
            offen = any(p.kind is inspect.Parameter.VAR_KEYWORD
                        for p in parameter.values())
            if offen and methode.startswith("flows."):
                # A facade that forwards ``**kwargs`` documents nothing itself:
                # the function behind it is what a keyword is checked against.
                hinter = _funktion_hinter(methode[len("flows."):])
                if hinter is not None:
                    ziel = hinter
                    parameter = inspect.signature(ziel).parameters
                    offen = any(p.kind is inspect.Parameter.VAR_KEYWORD
                                for p in parameter.values())
            positionell = _positionelle(ziel)
            if positionell[:1] == ["repo"]:
                positionell = positionell[1:]   # the function behind a facade takes repo first
            stelle = 0
            for stueck in _argumente(roh):
                if "=" in stueck:
                    name = stueck.split("=")[0].strip()
                    if (_BEZEICHNER.fullmatch(name) and name not in parameter
                            and not offen):
                        falsch.append(
                            f"{datei}: repo.{methode}() hat kein Argument {name!r}")
                    continue
                if _BEZEICHNER.fullmatch(stueck):
                    echt = positionell[stelle] if stelle < len(positionell) else None
                    if echt != stueck:
                        falsch.append(
                            f"{datei}: repo.{methode}() nennt an Stelle {stelle + 1} "
                            f"{stueck!r}, die Methode nennt es {echt!r}")
                stelle += 1
            erste = next(iter(parameter), None)
            falsch.extend(_bindet_nicht(ziel, roh, f"{datei}: repo.{methode}",
                                        implizit=int(erste in ("self", "repo"))))

    assert not falsch, "\n  " + "\n  ".join(falsch)


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


# --- Und die freien Funktionen? --------------------------------------------
#
# ``ancestry_of(repo, node_id)`` stand in der Referenz, die Funktion nahm ein
# ``Nodes``-Objekt. Der Waechter darueber prueft nur ``repo.x(...)``-Zeilen --
# so kam es durch. Dieselbe Pruefung fuer jede Zeile `name(a, b=...)`, deren
# Name eine oeffentliche freie Funktion ist: positionelle Argumente nach Name
# und Reihenfolge, Schluesselwoerter gegen die Parameterliste.

_FREIER_AUFRUF = re.compile(r"`([a-z_][a-z_0-9]*)\(([^`)]*)\)`")


def _freie_funktion(name: str):
    """Die oeffentliche Funktion dieses Namens, oder None fuer alles andere."""
    import importlib
    import inspect
    herkunft = oeffentliche_namen().get(name)
    if not herkunft or ":" in herkunft:        # Felder und Methoden: andere Waechter
        return None
    modul = "edusharing." + herkunft.replace("\\", "/")[:-3].replace("/", ".")
    try:
        ziel = getattr(importlib.import_module(modul), name, None)
    except Exception:  # ein Modul, das nicht laedt, faellt anderswo auf
        return None
    return ziel if inspect.isfunction(ziel) else None


def _argumente_pruefen(ziel, roh: str, wer: str) -> list[str]:
    """Die Beschwerden ueber `wer(roh)` gegen die echte Signatur von ``ziel``."""
    import inspect
    parameter = inspect.signature(ziel).parameters
    offen = any(p.kind is inspect.Parameter.VAR_KEYWORD for p in parameter.values())
    positionell = _positionelle(ziel)
    falsch: list[str] = []
    stelle = 0
    for stueck in (s.strip() for s in roh.split(",") if s.strip()):
        if "=" in stueck:
            name = stueck.split("=")[0].strip()
            if _BEZEICHNER.fullmatch(name) and name not in parameter and not offen:
                falsch.append(f"{wer}() hat kein Argument {name!r}")
            continue
        if _BEZEICHNER.fullmatch(stueck):
            echt = positionell[stelle] if stelle < len(positionell) else None
            if echt != stueck:
                falsch.append(f"{wer}() nennt an Stelle {stelle + 1} {stueck!r}, "
                              f"die Funktion nennt es {echt!r}")
        stelle += 1
    falsch.extend(_bindet_nicht(ziel, roh, wer, implizit=0))
    return falsch


def test_jeder_dokumentierte_freie_aufruf_nennt_echte_parameter():
    """`name(a, b=...)` in jeder behauptenden Datei -- mit den echten Namen."""
    falsch: list[str] = []
    for datei in BEHAUPTEND:
        pfad = WURZEL / datei
        if not pfad.exists():
            continue
        for name, roh in _FREIER_AUFRUF.findall(pfad.read_text(encoding="utf-8")):
            ziel = _freie_funktion(name)
            if ziel is None:
                continue
            falsch.extend(f"{datei}: {f}" for f in _argumente_pruefen(ziel, roh, name))
    assert not falsch, "\n  " + "\n  ".join(sorted(set(falsch)))


_KONSTRUKTOR = re.compile(r"(?<!\w)([A-Z][A-Za-z0-9_]*)\(")


def _konstruktor(name: str, klassen: dict[str, type]):
    """``__init__`` der oeffentlichen Klasse -- fuer ``Repository`` der von
    ``AsyncRepository``, an den die blockierende Huelle alles weiterreicht."""
    from edusharing import AsyncRepository
    klasse = {"Repository": AsyncRepository}.get(name) or klassen.get(name)
    return None if klasse is None else klasse.__init__


def test_jeder_dokumentierte_konstruktor_bindet():
    """`Repository(url, credential=...)` und `BildungsAPI(url, key)` standen in
    den Tabellen des Skills, `Repository(url, credential=cred)` in seinem
    Beispiel (Audit DOC-2, 03.09.2026) -- TypeError beim Abschreiben, und
    kein Waechter las Konstruktoren."""
    klassen = _klassen_der_bibliothek()
    falsch: list[str] = []
    for datei in BEHAUPTEND:
        pfad = WURZEL / datei
        if not pfad.exists():
            continue
        for name, roh in _aufrufe(pfad.read_text(encoding="utf-8"), _KONSTRUKTOR):
            ziel = _konstruktor(name, klassen)
            if ziel is None:
                continue
            falsch.extend(_bindet_nicht(ziel, roh, f"{datei}: {name}", implizit=1))
    assert not falsch, "\n  " + "\n  ".join(sorted(set(falsch)))


def test_der_waechter_bindet_platzhalter_an_die_signatur():
    """Die vier Aufrufe des Audits, nachgestellt -- und ihre richtigen Formen."""
    from edusharing.flows.curate import add_material, build_collection
    klassen = _klassen_der_bibliothek()
    repository = _konstruktor("Repository", klassen)
    bapi = _konstruktor("BildungsAPI", klassen)

    def klemmt(ziel, roh: str) -> bool:
        return bool(_bindet_nicht(ziel, roh, "x", implizit=1))

    assert klemmt(add_material, 'folder.id, title="x"')          # title doppelt
    assert klemmt(build_collection, '"Mappe", [a, b]')           # node_ids ist keyword-only
    assert klemmt(repository, "url, credential=c")               # heisst auth
    assert klemmt(bapi, "url, key")                              # base_url ist keyword-only
    assert not klemmt(add_material, 'title="x", parent_id=folder.id')
    assert not klemmt(build_collection, '"Mappe", node_ids=[a, b]')
    assert not klemmt(repository, "url, auth=c")
    assert not klemmt(bapi, "key, base_url=url")
    assert not klemmt(bapi, "models_cache_seconds=0")            # nur ein Knopf gezeigt
    assert not klemmt(build_collection, "title, node_ids=[…], …")  # "und mehr"
    assert not klemmt(bapi, "*args")                             # entpackt: nicht pruefbar


def test_der_waechter_liest_auch_zaeune_und_zaehlt_klammern():
    """Bis zum Abend des 02.09.2026 sah der Signatur-Waechter nur `repo.x(...)`
    in Backticks -- 160 Aufrufe in ```-Bloecken, die Leser abschreiben, nicht."""
    text = ('x\n```python\nawait repo.flows.find_collections(\n    "Physik, Optik",   # 1\n'
            '    parent_id="w", properties=["a", "b"],\n)\n```\n`repo.node(node_id)`')
    aufrufe = list(_aufrufe(text))
    assert [a[0] for a in aufrufe] == ["flows.find_collections", "node"]
    assert _argumente(aufrufe[0][1]) == ['"Physik, Optik"', 'parent_id="w"',
                                         'properties=["a", "b"]']
    assert _argumente(aufrufe[1][1]) == ["node_id"]
