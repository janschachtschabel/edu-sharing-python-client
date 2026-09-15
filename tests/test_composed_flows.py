"""Composed workflows keep identity, partial states and read budgets explicit."""

import json
from dataclasses import replace

import httpx
import pytest
from test_metadata_profile import URL, profile
from test_permissions import _ace, _antwort

from edusharing import AsyncRepository
from edusharing.errors import ValidationError


class Backend:
    def __init__(self, *, placement_status=200, duplicate=False):
        self.calls = []
        self.placement_status = placement_status
        self.duplicate = duplicate

    def handler(self, request):
        self.calls.append(request)
        path = request.url.path
        if "/references/" in path:
            if request.method == "DELETE":
                return httpx.Response(200, json={})
            return httpx.Response(self.placement_status, json={"node": {
                "ref": {"id": "new-reference"}, "originalId": "original"}})
        if path.endswith("/values"):
            return httpx.Response(200, json={"values": [
                {"key": "urn:one", "displayString": "Space"},
                {"key": "urn:two", "displayString": "Space"}]})
        if "/mds/" in path:
            return httpx.Response(200, json={"widgets": [
                {"id": "acme:title", "isRequired": "mandatory"},
                {"id": "acme:rights", "isRequired": "mandatoryForPublish"}]})
        if "/search/" in path:
            nodes = [{"ref": {"id": "existing"}, "properties": {
                "acme:url": ["https://source.example/item"]}}] if self.duplicate else []
            return httpx.Response(200, json={"nodes": nodes, "pagination": {"total": len(nodes)}})
        if path.endswith("/children/collections"):
            return httpx.Response(200, json={"collections": [], "pagination": {"total": 0}})
        if path.endswith("/children"):
            return httpx.Response(200, json={"nodes": [{"ref": {"id": "ref"},
                "originalId": "original", "properties": {
                    "acme:subject": ["urn:one"], "acme:subject_DISPLAYNAME": ["Space"]}}],
                "pagination": {"total": 8}})
        return httpx.Response(200, json={"node": {"ref": {"id": "input"},
            "originalId": "original" if "/input/" in path else None,
            "properties": {"acme:title": ["Own collection"], "acme:context": ["Teaching notes"]}}})

    def repo(self):
        return AsyncRepository(URL, metadata_profile=replace(profile(),
            compendium_property="acme:context"), max_retries=0,
            client=httpx.AsyncClient(transport=httpx.MockTransport(self.handler)))


async def test_place_uses_original_and_returns_writer_reference_without_index_read():
    backend = Backend()
    async with backend.repo() as repo:
        result = await repo.flows.place_material("input", "target", remove_from="old")
    assert result["original_id"] == "original"
    assert result["reference_id"] == "new-reference"
    assert result["placed"] and result["created"]
    assert result["removed_from"] == "old"
    writes = [r for r in backend.calls if r.method != "GET"]
    assert [r.method for r in writes] == ["PUT", "DELETE"]
    assert writes[0].url.path.endswith("/target/references/original")
    assert writes[1].url.path.endswith("/old/references/original")
    assert not any("/children" in r.url.path for r in backend.calls)


async def test_failed_placement_never_removes_the_old_one():
    backend = Backend(placement_status=403)
    async with backend.repo() as repo:
        result = await repo.flows.place_material("input", "target", remove_from="old")
    assert not result["placed"]
    assert result["failed"][0]["step"] == "place"
    assert not any(r.method == "DELETE" for r in backend.calls)


async def test_existing_placement_is_success_with_unknown_reference_id():
    backend = Backend(placement_status=409)
    async with backend.repo() as repo:
        result = await repo.flows.place_material("input", "target")
    assert result["placed"] and not result["created"]
    assert result["reference_id"] is None


async def test_same_source_and_destination_is_rejected_before_requests():
    backend = Backend()
    async with backend.repo() as repo:
        with pytest.raises(ValidationError):
            await repo.flows.place_material("input", "target", remove_from="target")
    assert backend.calls == []


async def test_context_reads_contents_once_and_exposes_sample_limits():
    backend = Backend()
    async with backend.repo() as repo:
        result = await repo.flows.collection_context("collection", limit=2)
    assert len(backend.calls) == 3
    assert result["collection"]["title"] == "Own collection"
    assert result["compendium"]["text"] == "Teaching notes"
    assert result["stats"]["sampled"] == 1
    assert result["stats"]["materials"] == 8
    assert result["stats"]["complete"] is False
    assert result["stats"]["by"]["subject"] == {"Space": 1}
    assert result["contents"]["materials"][0]["value_fields"]["subject"][0]["value"] == "urn:one"
    json.dumps(result)


async def test_prepare_returns_raw_draft_and_never_writes():
    backend = Backend()
    async with backend.repo() as repo:
        result = await repo.flows.prepare_material(
            "https://source.example/item", title="Space", labels={"subject": "urn:one"})
    assert result["ready_to_create"]
    assert result["draft"] == {"name": "Space", "url": "https://source.example/item",
                               "properties": {
        "acme:title": ["Space"], "acme:url": ["https://source.example/item"],
        "acme:subject": ["urn:one"]}}
    assert result["validation"]["missing_for_publish"] == ["acme:rights"]
    assert result["duplicate"]["status"] == "absent"
    assert all(r.method == "GET" or (r.method == "POST" and (
        "/search/" in r.url.path or r.url.path.endswith("/values"))) for r in backend.calls)
    json.dumps(result)


async def test_prepare_reports_ambiguity_and_missing_required_fields():
    backend = Backend()
    async with backend.repo() as repo:
        result = await repo.flows.prepare_material(
            "https://source.example/item", name="draft", labels={"subject": "Space"})
    assert not result["ready_to_create"]
    assert result["unresolved"][0]["candidates"] == ["urn:one", "urn:two"]
    assert "acme:subject" not in result["draft"]["properties"]
    assert result["validation"]["missing"] == ["acme:title"]


async def test_prepare_names_existing_record_instead_of_claiming_create_ready():
    backend = Backend(duplicate=True)
    async with backend.repo() as repo:
        result = await repo.flows.prepare_material("https://source.example/item", title="Space")
    assert not result["ready_to_create"]
    assert result["duplicate"]["status"] == "exists"
    assert result["duplicate"]["node"]["id"] == "existing"


async def test_already_public_material_can_move_without_a_second_acl_write():
    backend = Backend()
    original_handler = backend.handler

    def handler(request):
        if request.url.path.endswith("/permissions"):
            backend.calls.append(request)
            return httpx.Response(200, json=_antwort(
                own=[_ace("GROUP_EVERYONE", "Consumer", typ="GROUP")]))
        return original_handler(request)

    backend.handler = handler
    async with backend.repo() as repo:
        result = await repo.flows.place_material("input", "target", publish=True, remove_from="old")
    assert result["public"] is True
    assert result["failed"] == []
    assert result["removed_from"] == "old"
    assert not any(r.method == "POST" for r in backend.calls)


@pytest.mark.parametrize("failed_step", ["publish", "remove"])
async def test_partial_placement_failure_keeps_new_reference_identity(failed_step):
    backend = Backend()
    original_handler = backend.handler

    def handler(request):
        if request.url.path.endswith("/permissions") or request.method == "DELETE":
            backend.calls.append(request)
            return httpx.Response(403, json={"error": "refused"})
        return original_handler(request)

    backend.handler = handler
    async with backend.repo() as repo:
        result = await repo.flows.place_material(
            "input", "target", publish=failed_step == "publish", remove_from="old")
    assert result["placed"]
    assert result["reference_id"] == "new-reference"
    assert result["removed_from"] is None
    assert result["failed"][0]["step"] == failed_step
    if failed_step == "publish":
        assert not any(r.method == "DELETE" for r in backend.calls)


async def test_unknown_duplicate_and_schema_are_not_readiness():
    backend = Backend()
    original_handler = backend.handler

    def handler(request):
        if "/search/" in request.url.path or "/mds/" in request.url.path:
            backend.calls.append(request)
            return httpx.Response(404, json={"error": "not found"})
        return original_handler(request)

    backend.handler = handler
    async with backend.repo() as repo:
        result = await repo.flows.prepare_material("https://source.example/item", title="Space")
    assert result["duplicate"]["status"] == "unknown"
    assert result["validation"]["checked"] is False
    assert not result["ready_to_create"]


async def test_prepared_draft_preserves_duplicate_policy_at_creation():
    from edusharing.errors import ConflictError

    backend = Backend()
    async with backend.repo() as repo:
        prepared = await repo.flows.prepare_material("https://source.example/item", title="Space")
        backend.duplicate = True
        with pytest.raises(ConflictError):
            await repo.flows.add_material(
                **prepared["draft"], parent_id="parent", if_exists="raise")
    assert not any(r.url.path.endswith("/parent/children") for r in backend.calls)


@pytest.mark.parametrize("partial", ["truncated", "ignored"])
async def test_incomplete_duplicate_check_reports_unknown(partial):
    backend = Backend()
    original_handler = backend.handler

    def handler(request):
        if "/search/" in request.url.path:
            backend.calls.append(request)
            return httpx.Response(200, json={"nodes": [],
                "pagination": {"total": 1 if partial == "truncated" else 0},
                "ignored": ["acme:url"] if partial == "ignored" else []})
        return original_handler(request)

    backend.handler = handler
    async with backend.repo() as repo:
        result = await repo.flows.prepare_material("https://source.example/item", title="Space")
    assert result["duplicate"]["status"] == "unknown"
    assert not result["ready_to_create"]


async def test_context_forwards_custom_registry_conventions():
    from edusharing.skills import WLO_SKILLS

    backend = Backend()
    original_handler = backend.handler

    def handler(request):
        if request.url.path.endswith("/children"):
            backend.calls.append(request)
            return httpx.Response(200, json={"nodes": [{"ref": {"id": "registry"},
                "mimetype": "text/markdown", "downloadUrl": URL + "/registry.md",
                "properties": {"acme:kind": ["urn:registry"], "acme:title": ["Rules"]}}],
                "pagination": {"total": 1}})
        if request.url.path.endswith("/registry.md"):
            backend.calls.append(request)
            return httpx.Response(200, text="# Approved skills\n\nNo entries yet.")
        return original_handler(request)

    backend.handler = handler
    conventions = replace(WLO_SKILLS, type_property="acme:kind", registry_type="urn:registry")
    async with backend.repo() as repo:
        result = await repo.flows.collection_context(
            "collection", include_registry=True, registry_conventions=conventions)
    assert result["registry"]["registry_id"] == "registry"


@pytest.mark.parametrize("missing", ["read_role", "projection"])
async def test_duplicate_check_cannot_prove_absence_without_readable_urls(missing):
    backend = Backend(duplicate=True)
    configured = profile()
    original_handler = backend.handler
    if missing == "read_role":
        configured = replace(configured, read_fields={"title": ("acme:title",)})

    def handler(request):
        response = original_handler(request)
        if missing == "projection" and "/search/" in request.url.path:
            return httpx.Response(200, json={"nodes": [{"ref": {"id": "existing"}}],
                                           "pagination": {"total": 1}})
        return response

    async with AsyncRepository(URL, metadata_profile=configured, max_retries=0,
            client=httpx.AsyncClient(transport=httpx.MockTransport(handler))) as repo:
        result = await repo.flows.prepare_material("https://source.example/item", title="Space")
    assert result["duplicate"]["status"] == "unknown"
    assert not result["ready_to_create"]
