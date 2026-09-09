"""URL-Pruefung vor dem Abruf.

Ein Dienst, der Inhalte aus einem Repositorium an ein Sprachmodell weitergibt,
holt frueher oder spaeter eine URL, die aus Fremddaten stammt -- ``ccm:wwwurl``
eines beliebigen Datensatzes etwa. Zeigt die auf ``localhost`` oder in ein
internes Netz, wird der eigene Dienst zum Werkzeug (SSRF).
"""

import pytest

from edusharing.agent.safety import UnsafeUrlError, check_url, is_safe_url


@pytest.mark.parametrize("url", [
    "https://beispiel.test/material",
    "http://beispiel.test/material",
    # Die Form einer echten Render-Adresse; die Instanz darin ist frei
    # erfunden, geprueft wird Schema und Host.
    "https://repositorium.example.test/edu-sharing/components/render/abc",
    "https://xn--bcher-kva.example/seite",          # Punycode
])
def test_oeffentliche_adressen_sind_erlaubt(url):
    assert is_safe_url(url) is True


# --- Schemata --------------------------------------------------------------

@pytest.mark.parametrize("url", [
    "file:///etc/passwd",
    "gopher://beispiel.test/",
    "data:text/html,<script>alert(1)</script>",
    "ftp://beispiel.test/datei",
    "javascript:alert(1)",
])
def test_nur_http_und_https(url):
    """Alles andere ist entweder kein Netzabruf oder ein bekannter Umweg."""
    assert is_safe_url(url) is False


# --- Private Adressen ------------------------------------------------------

@pytest.mark.parametrize("url", [
    "http://127.0.0.1/admin",
    "http://localhost:8080/admin",
    "http://LOCALHOST/admin",
    "http://10.0.0.5/",
    "http://172.16.0.1/",
    "http://172.31.255.254/",
    "http://192.168.1.1/",
    "http://[::1]/",
    "http://[fc00::1]/",
])
def test_private_und_lokale_adressen_sind_gesperrt(url):
    assert is_safe_url(url) is False


def test_link_local_metadaten_endpunkt_ist_gesperrt():
    """169.254.169.254 ist der Metadaten-Dienst der meisten Cloud-Anbieter --
    das lohnendste einzelne Ziel eines SSRF-Angriffs."""
    assert is_safe_url("http://169.254.169.254/latest/meta-data/") is False


@pytest.mark.parametrize("url", [
    "http://172.15.0.1/",        # knapp unterhalb des privaten Bereichs
    "http://172.32.0.1/",        # knapp oberhalb
    "http://11.0.0.1/",
])
def test_benachbarte_oeffentliche_bereiche_bleiben_erlaubt(url):
    """Der private 172er-Block reicht nur von 16 bis 31 -- wer breiter sperrt,
    macht oeffentliche Adressen unerreichbar."""
    assert is_safe_url(url) is True


@pytest.mark.parametrize("name", [
    "http://meinserver.local/",
    "http://dienst.internal/",
    "http://irgendwas.localhost/",
])
def test_interne_namensraeume_sind_gesperrt(name):
    assert is_safe_url(name) is False


# --- Bereiche, die die Aufzaehlung uebersah (Audit A6) --------------------

@pytest.mark.parametrize("url", [
    "http://100.64.0.1/",        # CGNAT, RFC 6598
    "http://100.127.255.254/",   # oberes Ende desselben Blocks
    "http://[64:ff9b::1]/",      # NAT64, RFC 6052
])
def test_weitere_nicht_routbare_bereiche_sind_gesperrt(url):
    """Zwei Pruefungen lagen in dieser Bibliothek nebeneinander und antworteten
    verschieden. Die Aufzaehlung hier liess **CGNAT** durch -- Adressen, die in
    Provider- und Firmennetzen alltaeglich sind. ``not is_global`` in
    ``extraction`` fing die, liess dafuer **NAT64** durch. Jede hatte ein Loch,
    das die andere nicht hatte; jetzt gelten beide Regelsaetze.
    """
    assert is_safe_url(url) is False


@pytest.mark.parametrize("url", [
    "http://2130706433/",        # 127.0.0.1 als Dezimalzahl
    "http://0177.0.0.1/",        # oktal
    "http://0x7f000001/",        # hexadezimal
    "http://127.1/",             # verkuerzt
])
def test_andere_schreibweisen_einer_ip_sind_gesperrt(url):
    """Audit A7. ``ipaddress.ip_address`` kennt nur die punktierte Form; jede
    andere Schreibweise fiel als "das ist ein Name" durch und wurde
    durchgelassen. Ob sie beim Abruf wirklich auf 127.0.0.1 landet, haengt am
    Resolver -- auf Windows nicht, auf anderen Plattformen ungeprueft. Die
    Sperre kostet nichts: ein Hostname, dessen letztes Label nur aus Ziffern
    besteht, ist nach RFC 1123 keiner.
    """
    assert is_safe_url(url) is False


@pytest.mark.parametrize("url", [
    "https://example.com/",
    "https://sub.domain.example.org/pfad",
    "https://xn--bcher-kva.example/",   # Punycode
    "https://host123.example.net/",     # Ziffern im Namen, aber nicht im Label
])
def test_gewoehnliche_namen_bleiben_erlaubt(url):
    """Gegenprobe zu A7: die Sperre darf keinen echten Hostnamen treffen."""
    assert is_safe_url(url) is True


# --- Grenzfaelle -----------------------------------------------------------

@pytest.mark.parametrize("url", ["", "   ", "kein-url", "https://", "http:///pfad"])
def test_unbrauchbare_eingaben_gelten_als_unsicher(url):
    """Im Zweifel nicht abrufen."""
    assert is_safe_url(url) is False


def test_zugangsdaten_in_der_url_sind_gesperrt():
    """http://user:pass@host ist ein bekannter Weg, Pruefungen zu verwirren --
    manche Parser lesen den Host anders als der spaetere Abruf."""
    assert is_safe_url("http://harmlos.test@127.0.0.1/") is False


# --- check_url -------------------------------------------------------------

def test_check_url_laesst_sichere_adressen_durch():
    assert check_url("https://beispiel.test/x") == "https://beispiel.test/x"


def test_check_url_wirft_bei_unsicherer_adresse():
    with pytest.raises(UnsafeUrlError):
        check_url("http://127.0.0.1/admin")


def test_meldung_nennt_die_adresse_und_den_grund():
    with pytest.raises(UnsafeUrlError) as info:
        check_url("http://127.0.0.1/admin")
    text = str(info.value)
    assert "127.0.0.1" in text
    assert "local" in text.lower() or "private" in text.lower()


# --- F06 (Fremdpruefung 09.09.2026): das Passwort in der Absage ------------
#
# ``check_url`` lehnt eine Adresse mit eingebetteten Zugangsdaten ab -- und
# setzte die vollstaendige Adresse mit ``{url!r}`` in die Meldung. Gemessen am
# 09.09.2026 stand ``DUMMY_PASSWORD`` in der Ausnahme. Der Abruf war
# verhindert, das Geheimnis trotzdem unterwegs: in Protokollen und in jedem
# Agentenergebnis, das die Meldung weiterreicht.
#
# ``mask_userinfo`` gibt es seit SEC-1 zwei Module weiter, und
# ``refuse_userinfo`` benutzt es laengst.

GEHEIM = "https://alice:DUMMY_PASSWORD@example.test/datei"


def test_die_absage_wiederholt_das_passwort_nicht():
    with pytest.raises(UnsafeUrlError) as fehler:
        check_url(GEHEIM)
    assert "DUMMY_PASSWORD" not in str(fehler.value)
    assert "alice" not in str(fehler.value)


def test_die_absage_bleibt_trotzdem_lesbar():
    """Die Gegenprobe: maskieren heisst nicht schweigen. Wer die Meldung liest,
    muss sehen, welche Adresse gemeint war und warum sie abgelehnt wurde --
    sonst ist der naechste Schritt Raten."""
    with pytest.raises(UnsafeUrlError) as fehler:
        check_url(GEHEIM)
    meldung = str(fehler.value)
    assert "example.test" in meldung
    assert "***@" in meldung
    assert "credentials" in meldung.lower()


def test_ein_agentenergebnis_traegt_es_ebenso_wenig():
    """Der Weg, auf dem die Meldung wirklich hinausgeht."""
    import asyncio

    from edusharing.agent.result import as_result

    async def holen() -> str:
        return check_url(GEHEIM)

    ergebnis = asyncio.run(as_result(holen()))
    assert ergebnis.ok is False
    assert "DUMMY_PASSWORD" not in f"{ergebnis.text} {ergebnis.error}"
