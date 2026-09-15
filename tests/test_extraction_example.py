"""Run the URL-to-file example against the real client and a mocked HTTP service."""

import runpy
from pathlib import Path

import pytest
from test_extraction import Dienst, _oeffentlich

EXAMPLE = Path(__file__).resolve().parents[1] / "docs/examples/26_extract_page.py"


@pytest.mark.parametrize("method, output_format, content", [
    ("simple", "txt", "Ein Text mit Umlauten: äöü."),
    ("browser", "markdown", "# Ein Titel\n\n[Eine Quelle](https://example.org)"),
])
async def test_page_extraction_example_saves_the_requested_format(
    tmp_path, method, output_format, content,
):
    example = runpy.run_path(str(EXAMPLE))
    backend = Dienst(body={"text": content, "lang": "de", "status": 200})
    output = tmp_path / ("page.md" if output_format == "markdown" else "page.txt")
    async with backend.client(resolve=_oeffentlich) as service:
        result = await example["save_page"](
            service, "https://example.org", method=method,
            output_format=output_format, output=output,
        )
    assert output.read_text(encoding="utf-8") == content
    assert result.text == content
    assert backend.anfragen[0]["method"] == method
    assert backend.anfragen[0]["output_format"] == output_format


async def test_page_extraction_example_does_not_save_a_failure(tmp_path):
    example = runpy.run_path(str(EXAMPLE))
    backend = Dienst(status=424, body={"detail": {"error_message": "No text", "status": 404}})
    output = tmp_path / "page.md"
    async with backend.client(resolve=_oeffentlich) as service:
        result = await example["save_page"](
            service, "https://example.org", method="simple",
            output_format="markdown", output=output,
        )
    assert result.reason == "no_text"
    assert not output.exists()
