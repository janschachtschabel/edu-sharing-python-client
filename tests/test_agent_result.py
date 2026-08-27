"""Fehler als Ergebnis statt als Ausnahme.

Ein Werkzeug, das ein Sprachmodell aufruft, muss auch im Fehlerfall etwas
zurueckgeben, mit dem das Modell weiterarbeiten kann. Eine durchgereichte
Ausnahme beendet stattdessen den Durchlauf -- und das Modell erfaehrt nie,
dass bloss ein Filter unbekannt war.

Aufgefangen werden ausschliesslich Fehler dieser Bibliothek. Ein TypeError im
eigenen Code ist ein Programmierfehler und muss laut bleiben.
"""

import pytest

from edusharing.agent.result import ToolResult, as_result
from edusharing.errors import NotFoundError, ValidationError


async def test_erfolg_traegt_das_ergebnis():
    async def arbeit():
        return {"a": 1}

    ergebnis = await as_result(arbeit())
    assert ergebnis.ok is True
    assert ergebnis.data == {"a": 1}
    assert ergebnis.error is None


async def test_bibliotheksfehler_wird_zum_ergebnis():
    async def arbeit():
        raise NotFoundError("HTTP 404 DAOMissingException: Node does not exist")

    ergebnis = await as_result(arbeit())
    assert ergebnis.ok is False
    assert "Node does not exist" in ergebnis.error
    assert ergebnis.data is None


async def test_fehlerart_bleibt_erkennbar():
    """Damit ein Werkzeug unterscheiden kann, ob es sich lohnt, anders zu
    fragen -- oder ob die Anmeldung fehlt."""
    async def arbeit():
        raise ValidationError("Unbekanntes Suchfeld")

    ergebnis = await as_result(arbeit())
    assert ergebnis.error_type == "ValidationError"


async def test_programmierfehler_schlagen_durch():
    """Ein TypeError im eigenen Code ist kein Ergebnis, sondern ein Defekt.
    Ihn in einen freundlichen Text zu verwandeln versteckt ihn."""
    async def arbeit():
        raise TypeError("falscher Typ")

    with pytest.raises(TypeError):
        await as_result(arbeit())


async def test_kein_stacktrace_im_fehlertext():
    """Der Text geht in einen Modellkontext und moeglicherweise in eine
    Oberflaeche -- interne Klassenpfade haben dort nichts zu suchen."""
    async def arbeit():
        raise NotFoundError(
            "HTTP 404: weg",
            stacktrace="\njava.lang.Exception\n\tat org.edu_sharing.Intern(F.java:1)")

    ergebnis = await as_result(arbeit())
    assert "org.edu_sharing.Intern" not in ergebnis.error
    assert "\tat " not in ergebnis.error


async def test_text_ist_immer_gefuellt():
    """Ein Werkzeug braucht in jedem Fall etwas Ausgebbares."""
    async def gut():
        return 42

    async def schlecht():
        raise NotFoundError("weg")

    assert (await as_result(gut())).text
    assert (await as_result(schlecht())).text


async def test_eigener_formatierer():
    async def arbeit():
        return ["a", "b"]

    ergebnis = await as_result(arbeit(), format=lambda d: f"{len(d)} Eintraege")
    assert ergebnis.text == "2 Eintraege"


def test_ergebnis_ist_bool_auswertbar():
    assert bool(ToolResult(ok=True, text="x"))
    assert not bool(ToolResult(ok=False, text="x", error="y"))
