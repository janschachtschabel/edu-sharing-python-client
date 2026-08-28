"""Was ``from edusharing import ...`` hergibt.

Die Liste ``__all__`` ist von Hand nach Themen gruppiert und kommentiert, nicht
alphabetisch -- deshalb ist ``RUF022`` in pyproject.toml abgeschaltet. Damit
sieht ruff sie ueberhaupt nicht mehr an, und ein Tippfehler darin faellt erst
auf, wenn jemand den Namen importiert. Diese Datei schliesst die Luecke.
"""

import edusharing


def test_jeder_oeffentliche_name_ist_auch_da():
    """``__all__`` verspricht nichts, was das Modul nicht hat.

    Ein Name, den ``__all__`` nennt und der fehlt, laesst ``import *``
    fehlschlagen und ist sonst unsichtbar.
    """
    fehlend = [name for name in edusharing.__all__ if not hasattr(edusharing, name)]
    assert not fehlend, f"in __all__ genannt, aber nicht vorhanden: {fehlend}"


def test_kein_name_steht_doppelt():
    """Eine handgruppierte Liste laedt zum Kopieren ein."""
    doppelt = sorted({n for n in edusharing.__all__
                      if edusharing.__all__.count(n) > 1})
    assert not doppelt, f"mehrfach in __all__: {doppelt}"
