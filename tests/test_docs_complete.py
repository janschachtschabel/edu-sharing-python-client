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
        for knoten in baum.body:
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
