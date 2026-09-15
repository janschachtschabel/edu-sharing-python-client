"""Die eine Wiederholungs-Regel.

Drei Schleifen beantworteten dieselbe Frage auf drei Arten: der Transport
wiederholte nach Fehlertyp, die beiden Nachbardienste nach Statuscode, und
alle drei warteten exakt ``base * 2^n``. Unter einer acht Wege breiten
Schranke ist das eine Herde -- acht Aufrufe treffen denselben 503 und kommen
in derselben Millisekunde zurueck (Audit ARC-2).

Geprueft wird hier die Regel selbst: der Statussatz, der Backoff mit Jitter
und ``Retry-After`` in beiden Schreibweisen, die RFC 9110 erlaubt.
"""

from datetime import UTC, datetime, timedelta
from email.utils import format_datetime

import pytest

from edusharing import retry
from edusharing.errors import EduSharingError
from edusharing.retry import RETRYABLE_STATUS, RetryPolicy, parse_retry_after


@pytest.fixture
def wuerfel(monkeypatch):
    """Der Zufall wird gestellt: ``wuerfel(0.5)`` laesst ``random()`` 0.5 sagen."""

    def stellen(wert: float) -> None:
        monkeypatch.setattr(retry, "random", lambda: wert)

    return stellen


# --- Der Statussatz --------------------------------------------------------


def test_der_statussatz_ist_der_gemessene():
    """Vier Serverfehler und der 429. 404 fehlt mit Absicht: 'Das ist kein
    Chat-Modell' wird beim vierten Versuch nicht wahrer."""
    assert RETRYABLE_STATUS == frozenset({429, 500, 502, 503, 504})
    assert 404 not in RETRYABLE_STATUS
    assert 400 not in RETRYABLE_STATUS


# --- Backoff mit Jitter ----------------------------------------------------


def test_die_wartezeit_waechst_exponentiell(wuerfel):
    wuerfel(1.0)
    regel = RetryPolicy(backoff_base=0.5)
    assert [regel.delay(n) for n in (1, 2, 3)] == [0.5, 1.0, 2.0]


def test_der_jitter_streut_die_herde(wuerfel):
    """Ohne Jitter kaeme jeder Aufruf einer Fan-out-Welle in derselben
    Millisekunde zurueck. Gestreut wird nach unten, nie ueber den vollen
    Schritt hinaus -- die Kurve bleibt, die Gleichzeitigkeit geht."""
    regel = RetryPolicy(backoff_base=0.5)
    wuerfel(0.0)
    frueh = regel.delay(3)
    wuerfel(1.0)
    spaet = regel.delay(3)
    assert frueh == pytest.approx(1.0)
    assert spaet == pytest.approx(2.0)
    assert frueh < spaet


def test_ohne_backoff_wird_nicht_gewartet(wuerfel):
    """``backoff_base=0`` heisst 0 -- der Jitter darf daraus nichts machen,
    sonst warten die Tests der ganzen Suite ploetzlich doch."""
    wuerfel(1.0)
    assert RetryPolicy(backoff_base=0.0).delay(4) == 0.0


# --- Retry-After -----------------------------------------------------------


def test_retry_after_in_sekunden_wird_gelesen():
    assert parse_retry_after("12") == 12.0


def test_retry_after_als_datum_wird_gelesen():
    """RFC 9110 erlaubt beide Schreibweisen. Ein Dienst, der ein Datum
    schickt, wird sonst wie einer ohne Angabe behandelt."""
    gleich = datetime.now(UTC) + timedelta(seconds=30)
    gelesen = parse_retry_after(format_datetime(gleich, usegmt=True))
    assert gelesen is not None
    assert 25 <= gelesen <= 31


def test_ein_datum_in_der_vergangenheit_heisst_sofort():
    vorbei = datetime.now(UTC) - timedelta(seconds=60)
    assert parse_retry_after(format_datetime(vorbei, usegmt=True)) == 0.0


@pytest.mark.parametrize("wert", [None, "", "  ", "bald", "-5", "12,5", "NaN"])
def test_unlesbares_retry_after_gilt_als_nicht_gesagt(wert):
    """Lieber nach eigener Kurve warten als auf eine Zahl bauen, die keine
    ist. Ein negativer Wert ist keine Wartezeit."""
    assert parse_retry_after(wert) is None


def test_retry_after_wird_beachtet_und_nie_unterschritten(wuerfel):
    """Der Dienst hat eine Zahl genannt -- frueher als gesagt wiederzukommen
    ist genau das, was der 429 verhindern soll. Der Jitter darf nur addieren."""
    wuerfel(0.0)
    assert RetryPolicy(backoff_base=0.5).delay(1, retry_after=10.0) == 10.0
    wuerfel(1.0)
    assert RetryPolicy(backoff_base=0.5).delay(1, retry_after=10.0) == 10.5


def test_eine_zu_lange_wartezeit_wird_nicht_abgewartet(wuerfel):
    """Eine Stunde in einem Bibliotheksaufruf zu schlafen ist keine
    Wiederholung, sondern ein Aufhaenger. ``None`` heisst: nicht warten,
    den Fehler dem Aufrufer geben -- der kann einplanen."""
    wuerfel(0.0)
    regel = RetryPolicy(backoff_base=0.5, max_retry_after=60.0)
    assert regel.delay(1, retry_after=3600.0) is None
    assert regel.delay(1, retry_after=60.0) == 60.0


def test_die_grenzen_werden_beim_bauen_geprueft():
    with pytest.raises(EduSharingError, match="max_retries"):
        RetryPolicy(max_retries=-1)
    with pytest.raises(EduSharingError, match="backoff_base"):
        RetryPolicy(backoff_base=-0.5)
    with pytest.raises(EduSharingError, match="max_retry_after"):
        RetryPolicy(max_retry_after=-1.0)
