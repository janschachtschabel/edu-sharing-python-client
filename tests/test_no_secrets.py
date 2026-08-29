"""Kein Zugangsdatum steht in einer versionierten Datei.

Am 29.08.2026 gefunden: das Staging-Passwort stand in ``tests/test_auth.py``
und in einem Audit-Dokument -- ausgerechnet in dem Test, der beweist, dass ein
Passwort nicht in eine Fehlermeldung gehoert. Es kam dorthin, weil es beim
Schreiben zur Hand war, und blieb, weil niemand danach suchte.

Dieser Test sucht. Er nimmt die Werte, die in der Umgebung stehen -- also die
echten -- und prueft, dass keiner davon in einer Datei des Arbeitsbaums
vorkommt. Ohne gesetzte Variablen (CI) hat er nichts zu tun und sagt das.

**Er meldet niemals einen Wert, nur einen Variablennamen.** Ein Waechter, der
das Geheimnis in seiner Fehlermeldung ausgibt, hat es selbst veroeffentlicht --
in die Testausgabe, in das CI-Protokoll, in den Modellkontext.
"""

import os
from pathlib import Path

import pytest

WURZEL = Path(__file__).resolve().parent.parent

#: Die Variablen, deren Werte Geheimnisse sind. Adressen stehen bewusst nicht
#: dabei: eine URL ist keins und darf in Beispielen stehen.
#:
#: ``EDU_SHARING_USER`` ebenfalls nicht. Ein Nutzername ist ein Bezeichner, kein
#: Geheimnis, und ein kurzer wie ``redaktion`` steckt in jedem zweiten deutschen
#: Satz -- ein Waechter, den man wegen Fehlalarmen abschaltet, ist keiner. Aus
#: dem Baum genommen wurde der echte Name am 29.08.2026 trotzdem: ein lebendes
#: Konto gehoert nicht als Beispielwert in eine veroeffentlichte Referenz.
GEHEIM = (
    "EDU_SHARING_PASSWORD",
    "B_API_KEY",
    "OPENAI_API_KEY",
    "ACADEMIC_CLOUD_API_KEY",
)

#: Was durchsucht wird. ``.git`` und ``.venv`` bleiben aussen vor: das eine ist
#: Geschichte, die dieser Test nicht aendern kann, das andere fremder Code.
ORDNER = ("src", "tests", "docs", "scripts", ".github", ".claude")
DATEIEN = ("README.md", "README.de.md", "CHANGELOG.md", "pyproject.toml",
           ".gitignore")

#: Zu kurze Werte treffen zufaellig: ein Nutzername wie ``ab`` steckt in jedem
#: zweiten Wort. Sechs Zeichen ist die Grenze, ab der ein Treffer etwas heisst.
#: (Der Wert selbst gehoert auch hier nicht hin -- die erste Fassung nannte
#: ihn als Beispiel und loeste diesen Test aus.)
MINDESTLAENGE = 6


def _versionierte_dateien() -> list[Path]:
    gefunden = [WURZEL / name for name in DATEIEN]
    for ordner in ORDNER:
        wurzel = WURZEL / ordner
        if wurzel.exists():
            gefunden.extend(p for p in wurzel.rglob("*")
                            if p.is_file() and "__pycache__" not in p.parts)
    return [p for p in gefunden if p.exists()]


def test_kein_gesetztes_geheimnis_steht_im_arbeitsbaum():
    """Was in der Umgebung steht, darf nicht auch in einer Datei stehen."""
    werte = {name: os.environ[name] for name in GEHEIM
             if len(os.environ.get(name, "")) >= MINDESTLAENGE}
    if not werte:
        pytest.skip("keine Zugangsdaten in der Umgebung -- nichts zu pruefen")

    treffer: list[str] = []
    for pfad in _versionierte_dateien():
        try:
            text = pfad.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue  # Binaerdatei oder gesperrt -- kein Ort fuer ein Passwort
        for name, wert in werte.items():
            if wert in text:
                # Nur der Name. Der Wert ist das, was hier nicht hin soll.
                treffer.append(f"{name} steht in {pfad.relative_to(WURZEL)}")

    assert not treffer, (
        "Zugangsdaten im Arbeitsbaum:\n  " + "\n  ".join(sorted(treffer))
        + "\n\nDen Wert entfernen und ersetzen, nicht den Test anpassen. "
          "Steht er schon in der Historie, hilft nur Rotieren oder Umschreiben."
    )
