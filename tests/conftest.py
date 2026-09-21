"""Was ein Schreiblauf nicht liegenlassen darf.

Jeder Schreibtest legt seinen Wegwerf-Ordner selbst an und loescht ihn im
``finally``, endgueltig statt in den Papierkorb. Was keiner von ihnen kann,
ist zu beweisen, dass das geklappt hat:

* ``_wegwerfen`` faengt je Objekt und **meldet** statt zu werfen -- sonst
  ersetzte eine Ausnahme im ``finally`` den Fehler, den der Test gerade
  gefunden hat (Audit TST-3). Gemeldet heisst aber: es steht in der Ausgabe
  und sonst nirgends, und niemand liest die Ausgabe eines gruenen Laufs.
* Ein Unterprozess, den die Zeitgrenze abschiesst, hat gar kein ``finally``
  mehr. ``test_live_examples`` sagt das selbst ueber seine schreibenden
  Beispiele: der Wegwerf-Ordner bleibt dann stehen, selbst angelegt, aber
  eben liegengeblieben.

Also wird am Ende des Laufs einmal nachgesehen. **Nicht als Test:** die
Reihenfolge ist zufaellig, und ein Test mitten im Lauf saehe den
Wegwerf-Ordner eines gerade laufenden anderen und meldete ihn als Spur.

Gesucht wird ausschliesslich, was diese Suite selbst anlegt -- der Praefix
``pytest-``. Fremde Bestaende werden weder angefasst noch gemeldet, und
geloescht wird hier gar nichts: eine Spur ist ein Befund, den jemand ansehen
soll, kein Muell, den ein Hook still wegraeumt.
"""

import asyncio
import os
from collections.abc import Callable

import pytest

from edusharing import AsyncRepository

#: Woran diese Suite ihre eigenen Objekte erkennt. Jede Fixture, die etwas
#: anlegt, benennt es so.
PRAEFIX = "pytest-"

#: Eine Seite der Kinderliste. Die Vorgabe der Bibliothek ist 50; hier wird
#: ohnehin geblaettert, die Zahl bestimmt nur, wie viele Anfragen es werden.
_SEITE = 100


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Nach dem Lauf: liegt noch etwas von uns auf der Instanz?"""
    if not _war_ein_schreiblauf(session):
        return

    sag = _ausgabe(session)
    try:
        spuren = asyncio.run(_spuren())
    except Exception as fehler:
        # Nicht den Lauf faellen: sein Ergebnis steht. Aber auch nicht
        # verschweigen -- ungeprueft ist nicht dasselbe wie sauber.
        sag(f"Aufraeumkontrolle nicht durchgefuehrt: "
            f"{type(fehler).__name__}: {fehler}", yellow=True)
        return

    if not spuren:
        sag("Aufraeumkontrolle: keine Spur geblieben.", green=True)
        return

    sag(f"Aufraeumkontrolle: {len(spuren)} Objekt(e) der Suite liegen noch "
        "auf der Instanz:", red=True)
    for spur in spuren:
        sag(f"  {spur}", red=True)
    session.exitstatus = pytest.ExitCode.TESTS_FAILED


def _ausgabe(session: pytest.Session) -> Callable[..., None]:
    """Schreiben, das auch ohne ``-s`` ankommt.

    Gemessen: ``write_line`` aus diesem Hook heraus verschwindet, solange die
    Ausgabe-Erfassung laeuft -- mit ``-s`` stand die Zeile da, ohne ``-s``
    nicht. Der Capture-Manager kann fuer die Dauer der Zeile beiseitetreten;
    das ist der vorgesehene Weg, und ohne ihn haette diese Wache einen Befund,
    den niemand zu sehen bekommt.
    """
    bericht = session.config.pluginmanager.get_plugin("terminalreporter")
    erfassung = session.config.pluginmanager.get_plugin("capturemanager")

    def sag(zeile: str, **farbe: bool) -> None:
        if bericht is None:
            return
        if erfassung is None:
            bericht.write_line(zeile, **farbe)
            return
        with erfassung.global_and_fixture_disabled():
            bericht.write_line(zeile, **farbe)

    return sag


def _war_ein_schreiblauf(session: pytest.Session) -> bool:
    """Nur nach ``-m write`` und nur mit Zugangsdaten.

    Ohne Anmeldung gibt es nichts anzulegen und nichts nachzusehen; ohne die
    Marke hat kein Test geschrieben, und eine Anfrage an die Instanz waere
    eine, die der Offline-Lauf nicht machen darf.
    """
    ausdruck = str(session.config.getoption("-m", default="") or "")
    if "write" not in ausdruck or "not write" in ausdruck:
        return False
    return bool(os.environ.get("EDU_SHARING_URL")
                and os.environ.get("EDU_SHARING_USER"))


async def _spuren() -> list[str]:
    """Die Objekte mit unserem Praefix -- im Home und unter den Sammlungen."""
    async with AsyncRepository.from_env(metadataset="mds_oeh") as repo:
        return await _im_home(repo) + await _in_sammlungen(repo)


async def _im_home(repo: AsyncRepository) -> list[str]:
    """Alles im Home-Verzeichnis, seitenweise.

    ``nodes.children()`` und nicht ``node.children.list()``: das zweite gibt
    die **Anhaenge** eines Materials zurueck, gefiltert auf
    ``ccm:io_childobject``. Eine Wegwerf-Datei im Home ist keiner. Mit der
    falschen Liste meldete diese Kontrolle "keine Spur", waehrend die Spur
    danebenlag -- gemessen am 21.09.2026 mit einer absichtlich gelegten.

    Und seitenweise, weil eine Seite 50 traegt: ein Wegwerf-Ordner auf Seite
    zwei waere sonst genau das, was unbemerkt liegenbleibt.
    """
    wer = await repo.whoami()
    home = ((wer.raw.get("person") or {}).get("homeFolder") or {}).get("id")
    if not home:
        return []

    gefunden: list[str] = []
    offset = 0
    while True:
        seite = await repo.nodes.children(home, limit=_SEITE, offset=offset)
        gefunden += [f"{kind.type} {kind.name} ({kind.id})" for kind in seite.nodes
                     if kind.name.startswith(PRAEFIX)]
        offset += len(seite.nodes)
        if not seite.nodes or offset >= seite.total:
            return gefunden


async def _in_sammlungen(repo: AsyncRepository) -> list[str]:
    """Sammlungen liegen nicht im Home -- eine Wegwerf-Sammlung faende die
    Home-Liste also nie."""
    treffer = await repo.collections.find(PRAEFIX.rstrip("-"))
    return [f"Sammlung {hit.title} ({hit.id})" for hit in treffer
            if hit.title.startswith(PRAEFIX)]
