"""Kein Bezeichner darf ungeprueft in einen URL-Pfad.

Entscheidung E8 sagt, dass Bezeichner an genau einer Stelle prozentkodiert
werden (``urls.path_segment``). Zweimal ist trotzdem eine Stelle entstanden,
die das nicht tat:

* 27.08.2026 -- eine Knoten-ID ``../../../admin/v1/applications`` erreichte
  einen anderen Endpunkt, ``abc?admin=1`` schluckte das angehaengte
  ``/metadata``.
* 29.08.2026 -- ``bapi.call("../../administration/account")`` verliess
  ``/api/v1/llm/{provider}/`` und erreichte die Administrations-API, mitsamt
  X-API-KEY. ``path_segment`` lag auf dem Anbieter, nicht auf der Route, in
  derselben f-String-Zeile.

Beide Male fand es eine Durchsicht, nicht ein Test. Dieser hier ist der
Waechter: er liest den Syntaxbaum jedes Moduls der Handschicht und verlangt fuer
jeden Platzhalter in einem **als Anfragepfad uebergebenen** f-String einen
Nachweis. Er braucht kein Netz und laeuft in der Vorgabe-Suite mit.

**Das Kriterium ist die Verwendung, nicht die Form.** Eine erste Fassung fragte
"enthaelt der f-String einen Schraegstrich" und meldete 33 Stellen, von denen
rund 31 Fehlermeldungen waren, die zufaellig einen Pfad nennen. Ein Waechter,
den man wegen Fehlalarmen abschaltet, ist keiner. Gesucht wird deshalb der
f-String, der einer Anfragemethode uebergeben wird -- dort und nur dort
adressiert er etwas.
"""

import ast
from pathlib import Path

QUELLE = Path(__file__).resolve().parent.parent / "src" / "edusharing"

#: Die Methoden, deren Argument ein Pfad ist. ``json``/``request`` sind die Wege
#: durch ``Transport``, ``_request``/``_json`` die der drei Dienst-Clients, die
#: HTTP-Verben die direkten httpx-Aufrufe. ``_request`` fehlte zuerst -- und
#: damit sah der Waechter ausgerechnet die Stelle nicht, die am 29.08. brach.
ANFRAGE = {"json", "request", "_json", "_request",
           "get", "post", "put", "delete", "patch"}

#: Funktionen, die einen Wert als Pfadbestandteil pruefen, statt ihn zu
#: kodieren. ``path_segment`` kann nicht ueberall greifen: eine Route wie
#: ``images/generations`` braucht ihren Schraegstrich, also prueft
#: ``_check_route`` sie Segment fuer Segment.
PRUEFER = {"_check_route"}

#: Attribute, die eine konfigurierte Basisadresse tragen -- vom Aufrufer beim
#: Verbinden gesetzt und dort geprueft, nicht pro Anfrage uebergeben.
BASEN = {"base_url", "rest_url", "repository_url", "url"}


def _aus_path_segment(baum: ast.AST) -> set[str]:
    """Namen, die in diesem Modul aus ``path_segment(...)`` stammen.

    ``segment = path_segment(collection_id)`` und zwei Zeilen spaeter
    ``f"/node/v1/nodes/-home-/{segment}/children"`` ist geschuetzt.
    """
    sicher: set[str] = set()
    for knoten in ast.walk(baum):
        if not isinstance(knoten, ast.Assign):
            continue
        wert = knoten.value
        if (isinstance(wert, ast.Call) and isinstance(wert.func, ast.Name)
                and wert.func.id == "path_segment"):
            sicher.update(z.id for z in knoten.targets if isinstance(z, ast.Name))
    return sicher


def _geprueft(baum: ast.AST) -> set[str]:
    """Namen, die einem Pruefer uebergeben wurden, etwa ``_check_route(route)``."""
    return {
        argument.id
        for knoten in ast.walk(baum)
        if isinstance(knoten, ast.Call) and isinstance(knoten.func, ast.Name)
        and knoten.func.id in PRUEFER
        for argument in knoten.args
        if isinstance(argument, ast.Name)
    }


def _belegt(ausdruck: ast.expr, belegt_im_modul: set[str]) -> bool:
    """Ob dieser Platzhalter nachweislich unbedenklich ist."""
    if (isinstance(ausdruck, ast.Call) and isinstance(ausdruck.func, ast.Name)
            and ausdruck.func.id == "path_segment"):
        return True
    if isinstance(ausdruck, ast.Name):
        # GROSSSCHREIBUNG heisst Modulkonstante -- kein fremder Wert.
        return ausdruck.id.isupper() or ausdruck.id in belegt_im_modul
    if isinstance(ausdruck, ast.Attribute) and ausdruck.attr in BASEN:
        return True
    return False


def _splisst_einen_pfad(f_string: ast.JoinedStr) -> bool:
    """Ob ein Bezeichner ZWISCHEN Pfadbestandteile gesetzt wird.

    ``f"{self.base_url}{path}"`` haengt eine fertige Adresse an eine Basis und
    baut nichts zusammen -- dort gibt es nichts zu kodieren. Erst ein literaler
    Schraegstrich neben dem Platzhalter macht ihn zu einem Pfadbestandteil, der
    ausbrechen koennte.
    """
    return any("/" in teil.value for teil in f_string.values
               if isinstance(teil, ast.Constant) and isinstance(teil.value, str))


def _pfad_argumente(baum: ast.AST):
    """Jeder f-String, der einer Anfragemethode als Pfad uebergeben wird."""
    for knoten in ast.walk(baum):
        if not isinstance(knoten, ast.Call):
            continue
        name = knoten.func.attr if isinstance(knoten.func, ast.Attribute) else None
        if name not in ANFRAGE:
            continue
        for argument in knoten.args:
            if isinstance(argument, ast.JoinedStr) and _splisst_einen_pfad(argument):
                yield argument


def _verstoesse() -> list[str]:
    gefunden: list[str] = []
    for pfad in sorted(QUELLE.rglob("*.py")):
        if "_generated" in pfad.parts:
            continue
        baum = ast.parse(pfad.read_text(encoding="utf-8"), filename=str(pfad))
        sicher = _aus_path_segment(baum) | _geprueft(baum)
        for f_string in _pfad_argumente(baum):
            for teil in f_string.values:
                if isinstance(teil, ast.FormattedValue) and not _belegt(teil.value, sicher):
                    gefunden.append(
                        f"{pfad.name}:{teil.lineno}  {{{ast.unparse(teil.value)}}}")
    return gefunden


def test_jeder_platzhalter_in_einem_anfragepfad_ist_belegt():
    """Jeder Platzhalter geht durch path_segment, ist eine Konstante oder eine
    konfigurierte Basisadresse.

    Faellt dieser Test fuer eine neue Stelle, ist die Frage nicht "wie bringe
    ich ihn zum Schweigen", sondern: kann der Wert von aussen kommen? Wenn ja --
    und unter einem MCP kommt er vom Modell -- gehoert er durch
    ``path_segment``. Kann er es nachweislich nicht, gehoert der Nachweis in
    ``_belegt``, nicht ein Ausnahmeeintrag hierher.
    """
    verstoesse = _verstoesse()
    assert not verstoesse, (
        f"{len(verstoesse)} ungeprueft in einen Anfragepfad interpoliert:\n  "
        + "\n  ".join(verstoesse)
    )


def test_der_waechter_sieht_ueberhaupt_etwas():
    """Gegenprobe: ein Waechter, der nichts findet, beweist nichts.

    Geprueft wird beides -- dass ein blanker Name auffaellt und dass er nach
    ``path_segment`` nicht mehr auffaellt. Ohne das ginge ein zu grosszuegiges
    ``_belegt`` als "alles sauber" durch.
    """
    schlecht = ast.parse(
        'await t.json("GET", f"/node/v1/nodes/-home-/{node_id}/metadata")')
    assert len(list(_pfad_argumente(schlecht))) == 1, "der f-String wurde nicht gesehen"
    platz = next(t for t in next(_pfad_argumente(schlecht)).values
                 if isinstance(t, ast.FormattedValue))
    assert not _belegt(platz.value, set()), "ein blanker Name gilt als belegt"

    gut = ast.parse(
        'await t.json("GET", f"/node/v1/nodes/-home-/{path_segment(node_id)}/metadata")')
    platz = next(t for t in next(_pfad_argumente(gut)).values
                 if isinstance(t, ast.FormattedValue))
    assert _belegt(platz.value, set())


def test_der_waechter_meldet_keine_fehlermeldungen():
    """Ein f-String mit einem Schraegstrich ist noch kein Pfad.

    Die erste Fassung dieses Waechters fragte nur nach dem Schraegstrich und
    meldete 33 Stellen, davon rund 31 Fehlermeldungen wie
    ``f"{url!r} is not usable -- try https://example.org"``.
    """
    text = ast.parse('raise EduSharingError(f"{value!r} is not a path like /a/b")')
    assert not list(_pfad_argumente(text))

    # Und ein dict.get, das zufaellig 'get' heisst:
    dict_get = ast.parse('properties.get(f"{prop}_DISPLAYNAME")')
    assert not list(_pfad_argumente(dict_get))

    # Und eine Basis plus fertigem Pfad -- da wird nichts eingesplisst:
    basis = ast.parse('await self._client.get(f"{self.base_url}{path}")')
    assert not list(_pfad_argumente(basis))
