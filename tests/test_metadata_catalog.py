"""Catalog loading and vocabulary reuse across process lifetimes."""

import asyncio
import copy
import json

import httpx
import pytest

from edusharing import AsyncRepository, Repository
from edusharing.errors import ValidationError

URL = "https://repo.example/edu-sharing"


class Backend:
    def __init__(self):
        self.calls = []
        self.active = 0
        self.peak = 0
        self.schema = {"id": "custom", "name": "Custom metadata", "widgets": [
            {"id": "acme:title", "caption": "Title", "isRequired": "mandatory"},
            {"id": "acme:subject", "type": "multivalue", "hasValues": True},
        ], "groups": [], "views": [], "lists": [], "sorts": []}

    async def handler(self, request):
        self.calls.append(request)
        self.active += 1
        self.peak = max(self.peak, self.active)
        await asyncio.sleep(0)
        self.active -= 1
        if request.url.path.endswith("/values"):
            return httpx.Response(200, json={"values": [
                {"key": "urn:subject:one", "displayString": "Space"}]})
        return httpx.Response(200, json=copy.deepcopy(self.schema))

    def repo(self, *, sync=False, **kwargs):
        cls = Repository if sync else AsyncRepository
        return cls(URL, metadataset="custom", client=httpx.AsyncClient(
            transport=httpx.MockTransport(self.handler)), **kwargs)


async def test_catalog_coalesces_loads_and_returns_independent_data():
    backend = Backend()
    async with backend.repo() as repo:
        results = await asyncio.gather(*(repo.metadata.load(locale="en_EN") for _ in range(8)))
        assert len(backend.calls) == 1
        results[0]["widgets"].clear()
        assert len((await repo.metadata.load(locale="en_EN"))["widgets"]) == 2
        fields = await repo.metadata.fields(locale="en_EN")
        assert [f["id"] for f in fields] == ["acme:title", "acme:subject"]
        assert "filterable" not in fields[0]
        assert all(r.headers.get("locale") == "en_EN" for r in backend.calls)


async def test_catalog_refresh_and_clear_reload_actual_definition():
    backend = Backend()
    async with backend.repo() as repo:
        await repo.metadata.load()
        backend.schema["name"] = "Changed"
        assert (await repo.metadata.load())["name"] == "Custom metadata"
        assert (await repo.metadata.load(refresh=True))["name"] == "Changed"
        repo.metadata.clear_cache()
        await repo.metadata.load()
        assert len(backend.calls) == 3


async def test_preload_is_bounded_and_reverse_lookup_uses_the_cache():
    backend = Backend()
    async with backend.repo() as repo:
        loaded = await repo.vocab.preload([f"acme:field{i}" for i in range(7)],
                                          locale="en_EN", concurrency=2)
        assert len(loaded) == 7
        assert backend.peak <= 2
        assert await repo.vocab.label("acme:field0", "urn:subject:one", locale="en_EN") == "Space"
        assert len(backend.calls) == 7


async def test_snapshot_roundtrip_is_json_and_loads_without_network():
    source, target = Backend(), Backend()
    async with source.repo() as repo:
        await repo.vocab.values("acme:subject", locale="en_EN")
        snapshot = json.loads(json.dumps(repo.vocab.snapshot(scope="public")))
    async with target.repo() as repo:
        assert repo.vocab.restore(snapshot, scope="public") == 1
        snapshot["entries"][0]["values"].clear()
        found = await repo.vocab.resolve("acme:subject", "Space", locale="en_EN")
        assert found == "urn:subject:one"
        assert target.calls == []


@pytest.mark.parametrize("change", ["scope", "metadataset", "query", "repository"])
async def test_snapshot_rejects_another_context_before_changing_the_cache(change):
    backend = Backend()
    async with backend.repo() as repo:
        await repo.vocab.values("acme:subject")
        snapshot = repo.vocab.snapshot(scope="public")
        snapshot["context"][change] = "different"
        with pytest.raises(ValidationError, match="context"):
            repo.vocab.restore(snapshot, scope="public")
        assert len(await repo.vocab.values("acme:subject")) == 1
        assert len(backend.calls) == 1


async def test_restore_does_not_make_expired_values_fresh():
    backend = Backend()
    async with backend.repo() as repo:
        await repo.vocab.values("acme:subject")
        snapshot = repo.vocab.snapshot(scope="public")
        snapshot["entries"][0]["loaded_at"] -= 7200
        repo.vocab.clear_cache()
        assert repo.vocab.restore(snapshot, scope="public") == 0
        await repo.vocab.values("acme:subject")
        assert len(backend.calls) == 2


async def test_malformed_snapshot_does_not_partially_fill_cache():
    backend = Backend()
    async with backend.repo() as repo:
        await repo.vocab.values("acme:subject")
        snapshot = repo.vocab.snapshot(scope="public")
        broken = copy.deepcopy(snapshot["entries"][0])
        broken["property"] = "other"
        broken["values"] = [{"value": ["not a string"], "label": "Invalid"}]
        snapshot["entries"].append(broken)
        repo.vocab.clear_cache()
        with pytest.raises(ValidationError):
            repo.vocab.restore(snapshot, scope="public")
        assert repo.vocab.snapshot(scope="public")["entries"] == []


def test_catalog_and_preload_are_synchronous_through_repository():
    backend = Backend()
    with backend.repo(sync=True) as repo:
        assert repo.metadata.load()["id"] == "custom"
        assert len(repo.metadata.fields()) == 2
        assert repo.vocab.preload(["acme:subject"])["acme:subject"][0].label == "Space"
        assert repo.vocab.label("acme:subject", "urn:subject:one") == "Space"
