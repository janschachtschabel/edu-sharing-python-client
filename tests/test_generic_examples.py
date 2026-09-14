"""Execute the new application examples against their HTTP boundary."""

import runpy
from pathlib import Path

from test_composed_flows import Backend as FlowBackend
from test_metadata_catalog import Backend as CatalogBackend

EXAMPLES = Path(__file__).resolve().parents[1] / "docs" / "examples"


async def test_generic_metadata_example_reuses_cached_values(capsys):
    example = runpy.run_path(str(EXAMPLES / "24_generic_metadata.py"))
    backend = CatalogBackend()
    async with backend.repo() as repo:
        snapshot = await example["inspect_metadata"](repo)
    assert len(backend.calls) == 2
    assert snapshot["entries"][0]["values"][0]["value"] == "urn:subject:one"
    assert "Restored entries: 1" in capsys.readouterr().out


async def test_preparation_context_example_performs_reads_and_preserves_status(capsys):
    example = runpy.run_path(str(EXAMPLES / "25_prepare_context.py"))
    backend = FlowBackend()
    async with backend.repo() as repo:
        result = await example["prepare_and_context"](
            repo, url="https://source.example/item", title="Space", collection_id="collection")
    assert result["prepared"]["ready_to_create"]
    assert result["context"]["stats"]["complete"] is False
    assert not any(r.method in ("PUT", "DELETE", "PATCH") for r in backend.calls)
    assert '"ready_to_create": true' in capsys.readouterr().out
