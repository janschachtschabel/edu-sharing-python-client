"""Explicit metadata profiles are isolated and honored by public operations."""

import copy
import json
from dataclasses import asdict, replace

import httpx
import pytest

from edusharing import AsyncRepository, Repository
from edusharing.agent import plan_update
from edusharing.errors import ValidationError
from edusharing.flows.duplicates import find_by_url
from edusharing.ranking import score_hit

URL = "https://repo.example/edu-sharing"


def profile(prefix="acme"):
    from edusharing import MetadataProfile

    roles = {role: (f"{prefix}:{role}",) for role in (
        "title", "description", "url", "keywords")}
    return MetadataProfile(
        field_aliases={"subject": f"{prefix}:subject"},
        read_fields=roles, write_fields=roles, material_type=f"{prefix}:asset",
        fulltext_property=f"{prefix}:text", url_search_property=f"{prefix}:url",
    )


class Backend:
    def __init__(self):
        self.calls = []
        self.props = {"acme:title": ["Own title"], "acme:description": ["Own description"],
                      "acme:url": ["https://source.example/item"],
                      "acme:keywords": ["Optik"], "cclom:general_keyword": ["Old"]}

    def node(self):
        return {"ref": {"id": "item"}, "title": "Conventional DTO title",
                "name": (self.props.get("cm:name") or ["item"])[0],
                "type": "acme:asset", "properties": dict(self.props)}

    def handler(self, request):
        self.calls.append(request)
        path = request.url.path
        if "/search/" in path:
            return httpx.Response(200, json={"nodes": [self.node()],
                                           "pagination": {"total": 1}})
        if path.endswith("/children") and request.method == "POST":
            self.props = json.loads(request.content)
        if path.endswith("/metadata") and request.method == "PUT":
            self.props.update(json.loads(request.content))
        return httpx.Response(200, json={"node": self.node()})

    def repo(self, **kwargs):
        return AsyncRepository(URL, client=httpx.AsyncClient(
            transport=httpx.MockTransport(self.handler)), **kwargs)


async def test_custom_profile_writes_only_configured_roles_and_node_type():
    backend = Backend()
    async with backend.repo(metadata_profile=profile()) as repo:
        result = await repo.flows.add_material("Created", parent_id="parent")
        assert result["title"] == "Created"
    write = next(r for r in backend.calls if r.method == "POST")
    assert json.loads(write.content) == {"acme:title": ["Created"], "cm:name": ["Created"]}
    assert write.url.params["type"] == "acme:asset"


async def test_update_and_change_plan_use_the_same_profile():
    backend = Backend()
    async with backend.repo(metadata_profile=profile()) as repo:
        node = await repo.node("item")
        plan = await plan_update(node, title="New")
        assert plan.changes == {"acme:title": (["Own title"], ["New"])}
        await node.update(properties={"acme:title": ["Raw"]}, title="New")
    write = next(r for r in backend.calls if r.method == "PUT")
    assert json.loads(write.content) == {"acme:title": ["New"]}


async def test_node_search_describe_and_ranking_share_read_roles():
    backend = Backend()
    configured = profile()
    async with backend.repo(metadata_profile=configured) as repo:
        node = await repo.node("item")
        hit = (await repo.search("Optik")).hits[0]
        description = await repo.flows.describe("item")
    assert node.title == hit.title == description["title"] == "Own title"
    assert hit.description == description["description"] == "Own description"
    assert hit.source_url == description["source_url"] == "https://source.example/item"
    assert node.keywords == ["Optik"]
    assert score_hit(hit, "Optik", {}, metadata_profile=configured) > 0
    sent = next(r for r in backend.calls if "/search/" in r.url.path)
    assert json.loads(sent.content)["criteria"] == [
        {"property": "acme:text", "values": ["Optik"]}]


async def test_custom_keyword_merge_preserves_existing_values():
    backend = Backend()
    async with backend.repo(metadata_profile=profile()) as repo:
        node = await repo.node("item")
        await node.add_keywords("Licht")
    assert backend.props["acme:keywords"] == ["Optik", "Licht"]
    assert backend.props["cclom:general_keyword"] == ["Old"]


async def test_url_duplicate_lookup_uses_profile_property():
    backend = Backend()
    async with backend.repo(metadata_profile=profile()) as repo:
        found = await find_by_url(repo, "https://source.example/item")
    assert found["id"] == "item"
    sent = json.loads(backend.calls[0].content)["criteria"]
    assert sent == [{"property": "acme:url", "values": ["https://source.example/item"]}]


async def test_neutral_profile_rejects_unconfigured_write_roles_before_writing():
    from edusharing import MetadataProfile

    backend = Backend()
    async with backend.repo(metadata_profile=MetadataProfile()) as repo:
        with pytest.raises(ValidationError, match="title"):
            await repo.nodes.create("parent", name="item", title="No configured field")
        assert backend.calls == []
        await repo.flows.add_material(parent_id="parent", name="raw",
                                      properties={"foreign:title": ["Own"]})
    assert backend.props == {"foreign:title": ["Own"], "cm:name": ["raw"]}


def test_profiles_are_deeply_immutable_and_repositories_are_isolated():
    from edusharing import MetadataProfile

    roles = {"title": ["acme:title"]}
    configured = MetadataProfile(write_fields=roles)
    roles["title"].append("other:title")
    assert configured.write_fields["title"] == ("acme:title",)
    with pytest.raises(TypeError):
        configured.write_fields["title"] = ("other:title",)
    first = Backend()
    second = Backend()
    with Repository(URL, metadata_profile=profile(), client=httpx.AsyncClient(
            transport=httpx.MockTransport(first.handler))) as a:
        with Repository(URL, metadata_profile=profile("other"), field_aliases={},
                        client=httpx.AsyncClient(
                            transport=httpx.MockTransport(second.handler))) as b:
            assert a.metadata_profile.write_fields["title"] == ("acme:title",)
            assert b.metadata_profile.write_fields["title"] == ("other:title",)
            assert b.searcher.field_aliases == {}


def test_compatibility_profile_falls_back_past_an_empty_first_field():
    from edusharing import WLO_METADATA_PROFILE

    props = {"cclom:title": [""], "cm:title": ["Fallback"],
             "cclom:general_description": [""], "cm:description": ["Description"]}
    assert WLO_METADATA_PROFILE.title({"name": "filename", "properties": props}) == "Fallback"
    assert WLO_METADATA_PROFILE.value(props, "description") == "Description"


async def test_collection_subtree_search_matches_profile_title():
    from edusharing import MetadataProfile

    configured = MetadataProfile(read_fields={"title": ("acme:title",)})

    def handler(request):
        children = ([{"ref": {"id": "child"}, "title": "Conventional title",
                      "properties": {"acme:title": ["Optik"]}}]
                    if request.url.path.endswith("/root/children/collections") else [])
        return httpx.Response(200, json={"collections": children,
                                        "pagination": {"total": len(children)}})

    async with AsyncRepository(URL, metadata_profile=configured,
            client=httpx.AsyncClient(transport=httpx.MockTransport(handler))) as repo:
        got = await repo.flows.find_collections("Optik", parent_id="root")
    assert [hit["id"] for hit in got["hits"]] == ["child"]
    assert got["hits"][0]["title"] == "Optik"


async def test_collection_update_verifies_rest_fields_not_profile_projection():
    from edusharing import MetadataProfile

    configured = MetadataProfile(read_fields={"title": ("acme:title",)})
    state = {"title": "Old DTO", "properties": {
        "cm:title": ["Old DTO"], "acme:title": ["Custom title"]}}

    def handler(request):
        if request.method == "PUT":
            sent = json.loads(request.content)
            state["title"] = sent["title"]
            state["properties"].update(sent["properties"])
            return httpx.Response(200)
        return httpx.Response(200, json={"node": {
            "ref": {"id": "collection"}, **state}})

    async with AsyncRepository(URL, metadata_profile=configured,
            client=httpx.AsyncClient(transport=httpx.MockTransport(handler))) as repo:
        updated = await repo.collections.update("collection", title="New title")
    assert updated.raw["title"] == "New title"
    assert updated.get_all("cm:title") == ["New title"]
    assert updated.get_all("acme:title") == ["Custom title"]


async def test_profiled_hits_remain_copyable_and_json_dataclasses():
    backend = Backend()
    async with backend.repo(metadata_profile=profile()) as repo:
        result = await repo.search("Optik")
    json.dumps(asdict(result))
    hit = result.hits[0]
    assert copy.deepcopy(hit).title == "Own title"
    assert score_hit(replace(hit, title="Other"), "Optik", {}) > 0


def test_sync_neutral_material_can_be_created_without_a_title_role():
    from edusharing import MetadataProfile

    backend = Backend()
    with Repository(URL, metadata_profile=MetadataProfile(), client=httpx.AsyncClient(
            transport=httpx.MockTransport(backend.handler))) as repo:
        result = repo.flows.add_material(name="raw", properties={"acme:title": ["Raw"]},
                                         parent_id="parent")
    assert result["created"]
    write = next(r for r in backend.calls if r.method == "POST")
    assert json.loads(write.content) == {"cm:name": ["raw"], "acme:title": ["Raw"]}


async def test_keyword_proposal_merges_the_configured_write_field():
    from test_flows_suggest import NID, REPO, Instanz, _vorschlag

    from edusharing import MetadataProfile

    backend = Instanz([_vorschlag("s1", "acme:tags", "new")])
    backend.props.update({"acme:tags": ["existing"], "acme:display_tags": ["display"]})
    configured = MetadataProfile(read_fields={"keywords": ["acme:display_tags"]},
                                 write_fields={"keywords": ["acme:tags"]})
    async with AsyncRepository(REPO, metadata_profile=configured, client=httpx.AsyncClient(
            transport=httpx.MockTransport(backend.handler))) as repo:
        result = await repo.flows.accept_suggestion(NID, "s1")
    assert result["applied"]
    assert backend.props["acme:tags"] == ["existing", "new"]
    assert backend.props["acme:display_tags"] == ["display"]
