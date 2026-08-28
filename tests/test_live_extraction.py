"""Tests gegen den echten Textextraktionsdienst.

    EDU_SHARING_TEXT_EXTRACTION_URL=https://... uv run pytest -m live

Beantworten, was ein Mock nicht kann: hat der Dienst noch dieselbe Form? Er
gehoert nicht zu edu-sharing und wird unabhaengig davon deployt -- am
28.08.2026 lief auf Staging Version ``c766f2e5``.

Alle Ziele hier sind oeffentliche Seiten. Nichts wird geschrieben.
"""

import os

import pytest

from edusharing import AsyncRepository
from edusharing.errors import NotFoundError
from edusharing.extraction import TextExtraction

pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(
        not os.environ.get(TextExtraction.ENV_BASE_URL),
        reason=f"{TextExtraction.ENV_BASE_URL} nicht gesetzt",
    ),
]


@pytest.fixture
async def dienst():
    async with TextExtraction.from_env() as client:
        yield client


async def test_der_dienst_meldet_sich(dienst):
    zustand = await dienst.ping()
    assert zustand.get("status") == "ok", f"unerwartete Antwort: {zustand}"
    assert zustand.get("version"), "keine Version gemeldet"


async def test_eine_oeffentliche_seite_liefert_text(dienst):
    ergebnis = await dienst.text_of("https://wirlernenonline.de/")
    assert ergebnis.reason == "", f"kein Text: {ergebnis.detail}"
    assert ergebnis.text.strip()
    assert ergebnis.status == 200, "Status der Zielseite"
    assert ergebnis.lang, "keine Sprache erkannt"
    assert ergebnis.char_count == len(ergebnis.text)


async def test_kuerzen_wirkt_am_echten_dienst(dienst):
    ergebnis = await dienst.text_of("https://wirlernenonline.de/", max_chars=200)
    if ergebnis.reason:
        pytest.skip(f"die Seite lieferte keinen Text: {ergebnis.detail}")
    assert len(ergebnis.text) <= 200
    assert ergebnis.truncated == (ergebnis.char_count > 200)


async def test_eine_download_url_des_repositoriums_scheitert(dienst):
    """Gemessen am 28.08.2026 (und vom MCP am 28.07.2026): der Dienst kann
    nicht lesen, was das Repositorium selbst hostet -- 424. Dafuer bleibt
    ``node.content.text()`` zustaendig. Wer das nicht weiss, sucht den Fehler
    bei sich."""
    if not os.environ.get("EDU_SHARING_URL"):
        pytest.skip("EDU_SHARING_URL nicht gesetzt")
    # Die Treffer werden DURCHGEGANGEN: der Suchindex haelt Knoten, die es im
    # Speicher nicht mehr gibt -- gemessen 4 von 25. Den ersten zu nehmen macht
    # den Test von einem Zustand abhaengig, den er nicht prueft.
    download = ""
    async with AsyncRepository.from_env(metadataset="mds_oeh") as repo:
        treffer = await repo.search("Photosynthese", limit=8)
        assert treffer.hits, "kein Material zum Pruefen gefunden"
        for hit in treffer.hits:
            try:
                knoten = await repo.nodes.get(hit.id)
            except NotFoundError:
                continue
            download = knoten.raw.get("downloadUrl") or ""
            if download:
                break
    if not download:
        pytest.skip("kein abrufbarer Knoten mit downloadUrl gefunden")

    ergebnis = await dienst.text_of(download)
    assert ergebnis.reason == "no_text"
    assert ergebnis.text == ""


async def test_ein_privater_host_wird_gar_nicht_erst_gesendet(dienst):
    """Der Dienst antwortet darauf zwar mit 424 -- aber das ist sein Netz und
    seine Version. Verlassen wird sich diese Bibliothek darauf nicht."""
    ergebnis = await dienst.text_of("http://169.254.169.254/latest/meta-data/")
    assert ergebnis.reason == "private_host"
