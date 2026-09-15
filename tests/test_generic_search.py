"""Foreign metadata values keep their identity through public search flows."""

import json

import httpx
import pytest

from edusharing import AsyncRepository
from edusharing.errors import ValidationError

URL = "https://repo.example/edu-sharing"


def repository(calls, *, seed=None):
    def handler(request):
        calls.append(request)
        if request.url.path.endswith("/values"):
            label = "Space" if request.headers.get("locale") == "en_EN" else "Weltraum"
            return httpx.Response(200, json={"values": [
                {"key": "urn:subject:one", "displayString": label},
                {"key": "urn:subject:two", "displayString": label},
            ]})
        if "/search/" in request.url.path:
            return httpx.Response(200, json={"nodes": [], "pagination": {"total": 0}})
        return httpx.Response(200, json={"node": {
            "ref": {"id": "seed"}, "title": "Seed", "type": "ccm:io",
            "properties": seed or {},
        }})

    return AsyncRepository(
        URL, metadataset="custom", field_aliases={"subject": "acme:subject"},
        client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    )


def criteria(calls):
    return [json.loads(r.content)["criteria"] for r in calls if "/search/" in r.url.path]


@pytest.mark.parametrize("rerank", [False, True])
async def test_flow_forwards_locale_and_explicit_raw_values(rerank):
    calls = []
    async with repository(calls) as repo:
        result = await repo.flows.search(
            "Space exploration", subject="Space", locale="en_EN", rerank=rerank,
            raw_filters={"acme:identifier": ["ITEM-42"]},
        )
    assert result["unresolved"] == []
    assert criteria(calls)
    for sent in criteria(calls):
        assert {"property": "acme:identifier", "values": ["ITEM-42"]} in sent
        assert {"property": "acme:subject", "values": [
            "urn:subject:one", "urn:subject:two"]} in sent
    assert all(r.headers.get("locale") == "en_EN" for r in calls)


async def test_raw_filter_does_not_load_a_vocabulary():
    calls = []
    async with repository(calls) as repo:
        await repo.search(raw_filters={"acme:identifier": "ITEM-42"})
    assert len(calls) == 1
    assert criteria(calls) == [[{"property": "acme:identifier", "values": ["ITEM-42"]}]]


async def test_conflicting_raw_and_label_filters_fail_before_requests():
    calls = []
    async with repository(calls) as repo:
        with pytest.raises(ValidationError, match="both"):
            await repo.search(subject="Space", raw_filters={"acme:subject": "raw"})
    assert calls == []


@pytest.mark.parametrize("rerank", [False, True])
async def test_strict_unresolved_never_runs_a_broader_search(rerank):
    calls = []
    async with repository(calls) as repo:
        with pytest.raises(ValidationError, match="Unresolved"):
            await repo.flows.search("Optik", subject="Unknown", strict=True, rerank=rerank)
    assert criteria(calls) == []


async def test_mixed_search_rejects_conflicting_filters_before_either_bucket():
    calls = []
    async with repository(calls) as repo:
        with pytest.raises(ValidationError, match="both"):
            await repo.flows.search_all("Optik", subject="Space",
                                        raw_filters={"acme:subject": "stored"})
    assert calls == []


@pytest.mark.parametrize("display", ["", "Weltraum", "Unknown old label"])
async def test_related_uses_stored_identity_without_re_resolving_its_label(display):
    calls = []
    seed = {"acme:subject": ["urn:subject:one"]}
    if display:
        seed["acme:subject_DISPLAYNAME"] = [display]
    async with repository(calls, seed=seed) as repo:
        result = await repo.flows.related("seed", on=["subject"])
    assert criteria(calls) == [[{"property": "acme:subject", "values": ["urn:subject:one"]}]]
    assert not any(r.url.path.endswith("/values") for r in calls)
    assert result["based_on_values"] == {"subject": ["urn:subject:one"]}


async def test_vocabulary_flow_exposes_identifiers_beside_duplicate_labels():
    async with repository([]) as repo:
        result = await repo.flows.vocabulary("subject")
    assert result["values"] == ["Weltraum", "Weltraum"]
    assert result["entries"] == [
        {"value": "urn:subject:one", "label": "Weltraum"},
        {"value": "urn:subject:two", "label": "Weltraum"},
    ]


async def test_describe_preserves_values_when_labels_are_missing_or_incomplete():
    seed = {"acme:subject": ["urn:subject:one", "CODE_B"],
            "acme:subject_DISPLAYNAME": ["Only one label"]}
    async with repository([], seed=seed) as repo:
        result = await repo.flows.describe("seed")
    assert result["value_fields"]["subject"] == [
        {"value": "urn:subject:one", "label": None},
        {"value": "CODE_B", "label": None},
    ]
