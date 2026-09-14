"""Audit follow-up: preserve failures, warnings and per-client state."""

from contextlib import asynccontextmanager

import httpx
import pytest

from edusharing import AsyncRepository
from edusharing.errors import ConflictError
from edusharing.search import STANDARD_FIELD_ALIASES

BASE = "https://repo.test/edu-sharing"


@asynccontextmanager
async def repository(handler, **kwargs):
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        async with AsyncRepository(BASE, client=client, max_retries=0, **kwargs) as repo:
            yield repo


async def test_initial_metadata_failure_is_a_text_flow_result():
    def handler(request):
        assert request.url.path.endswith("/metadata")
        return httpx.Response(503, json={"message": "temporarily unavailable"})

    async with repository(handler) as repo:
        got = await repo.flows.text("n")
    assert got["reason"] == "repository_failed"
    assert "ServerError" in got["detail"] and "503" in got["detail"]
    assert got["source"] == "none" and got["text"] == ""


@pytest.mark.parametrize("combined", [False, True])
async def test_page_discovery_keeps_collection_search_warnings(combined):
    def handler(request):
        if "/search/v1/queries/" in request.url.path:
            if "collection" in request.url.path:
                return httpx.Response(403, json={"message": "collection query denied"})
            return httpx.Response(200, json={"nodes": [], "pagination": {"total": 0}})
        if request.url.path.endswith("/search"):
            return httpx.Response(200, json={"collections": []})
        raise AssertionError(str(request.url))

    async with repository(handler) as repo:
        got = ((await repo.flows.search_all("Optik", include_pages=True))["pages"]
               if combined else await repo.flows.find_pages("Optik"))
    assert got["warnings"]
    assert "403" in " ".join(got["warnings"])


async def test_field_aliases_belong_to_one_repository():
    original = dict(STANDARD_FIELD_ALIASES)
    async with repository(lambda request: httpx.Response(200)) as first:
        async with repository(lambda request: httpx.Response(200)) as second:
            try:
                first.searcher.field_aliases["subject"] = "custom:subject"
                assert second.searcher.field_aliases == original
                assert STANDARD_FIELD_ALIASES == original
            finally:
                STANDARD_FIELD_ALIASES.clear()
                STANDARD_FIELD_ALIASES.update(original)


async def test_injected_field_aliases_are_copied():
    aliases = {"subject": "custom:subject"}
    async with repository(lambda request: httpx.Response(200), field_aliases=aliases) as repo:
        aliases["subject"] = "changed:subject"
        assert repo.searcher.field_aliases["subject"] == "custom:subject"


async def test_unpublish_checks_fresh_inherited_access_even_after_a_noop():
    reads, writes = [], []

    def handler(request):
        if request.url.path.endswith("/metadata"):
            return httpx.Response(200, json={"node": {"ref": {"id": "n"}}})
        assert request.url.path.endswith("/permissions")
        if request.method != "GET":
            writes.append(request)
            return httpx.Response(200)
        reads.append(request)
        inherited = [{"authority": {"authorityName": "GROUP_EVERYONE",
                                     "authorityType": "EVERYONE"},
                      "permissions": ["Consumer"]}] if len(reads) >= 2 else []
        return httpx.Response(200, json={"permissions": {
            "localPermissions": {"inherited": True, "permissions": []},
            "inheritedPermissions": inherited}})

    async with repository(handler) as repo:
        node = await repo.node("n")
        with pytest.raises(ConflictError) as error:
            await node.permissions.unpublish()
    assert len(reads) == 2 and writes == []
    assert "public" in str(error.value)
    assert "removed" not in str(error.value)
