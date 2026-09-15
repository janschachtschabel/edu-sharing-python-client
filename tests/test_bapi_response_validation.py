"""Audit B02/B03: bad gateway data is an error, not a usable result."""

import re
from contextlib import asynccontextmanager

import httpx
import pytest

from edusharing.bapi import BapiTemplates, BildungsAPI
from edusharing.errors import EduSharingError


@asynccontextmanager
async def gateway(payload, *, template=False):
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(200, json=payload)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        options = dict(api_key="dummy-test-key", base_url="https://gateway.test",
                       client=client, max_retries=0)
        api = (BapiTemplates(metadataset="test-mds", **options) if template
               else BildungsAPI(**options))
        yield api, calls


@pytest.mark.parametrize("result", [{}, {"flagged": None}, {"flagged": "false"},
                                   {"flagged": 0}, {"flagged": []}])
async def test_moderation_requires_an_explicit_boolean_decision(result):
    async with gateway({"results": [result]}) as (api, calls):
        with pytest.raises(EduSharingError, match=r"/moderations.*flagged"):
            await api.moderate("text", model="test-model")
    assert len(calls) == 1


@pytest.mark.parametrize("flagged", [False, True])
async def test_an_explicit_moderation_decision_is_preserved(flagged):
    async with gateway({"results": [{"flagged": flagged}]}) as (api, _calls):
        answer = await api.moderate("text", model="test-model")
    assert answer.flagged is flagged


@pytest.mark.parametrize("method,payload,field", [
    ("chat", {"choices": [None]}, "choices[0]"),
    ("chat", {"choices": [{"message": "bad"}]}, "choices[0].message"),
    ("chat", {"choices": [{"message": {"content": 42}}]}, "content"),
    ("respond", {"incomplete_details": "bad"}, "incomplete_details"),
    ("respond", {"output": [{"content": [{"text": 42}]}]}, "text"),
    ("respond", {"output": [{"content": 42}]}, "content"),
    ("images", {"data": [None]}, "data[0]"),
    ("images", {"data": [{"url": 42}]}, "url"),
])
@pytest.mark.parametrize("template", [False, True])
async def test_bad_nested_answers_raise_library_errors(method, payload, field, template):
    async with gateway(payload, template=template) as (api, calls):
        args = (["test-config"],) if template else ("prompt",)
        kwargs = {"context_node_id": "node-1"} if template else {"model": "test-model"}
        with pytest.raises(EduSharingError, match=re.escape(field)):
            await getattr(api, method)(*args, **kwargs)
    assert len(calls) == 1


@pytest.mark.parametrize("payload", [
    {"data": [{"index": 1, "embedding": [0.2]}]},
    {"data": [{"index": 0, "embedding": [0.1]}, {"index": 0, "embedding": [0.2]}]},
    {"data": [{"index": -1, "embedding": [0.1]}, {"index": 1, "embedding": [0.2]}]},
    {"data": [{"embedding": [0.1]}, {"index": 1, "embedding": [0.2]}]},
    {"data": [{"index": False, "embedding": [0.1]}, {"index": 1, "embedding": [0.2]}]},
    {"data": [{"index": 0, "embedding": ["bad"]}, {"index": 1, "embedding": [0.2]}]},
    {"data": [{"index": 0, "embedding": [True]}, {"index": 1, "embedding": [0.2]}]},
    {"data": [{"index": 0}, {"index": 1, "embedding": [0.2]}]},
    {"data": [{"index": 0, "embedding": []}, {"index": 1, "embedding": [0.2]}]},
    {"data": [{"index": 0, "embedding": [0.1, 0.2]}, {"index": 1, "embedding": [0.2]}]},
])
async def test_incomplete_or_ambiguous_embeddings_are_not_paired_with_inputs(payload):
    async with gateway(payload) as (api, _calls):
        with pytest.raises(EduSharingError, match="/embeddings"):
            await api.embeddings(["Text A", "Text B"], model="test-model")


async def test_complete_embeddings_are_reordered_and_numbers_preserved():
    payload = {"data": [{"index": 1, "embedding": [0.2, 1]},
                        {"index": 0, "embedding": [0.1, 0]}]}
    async with gateway(payload) as (api, _calls):
        answer = await api.embeddings(["Text A", "Text B"], model="test-model")
    assert answer == [[0.1, 0], [0.2, 1]]


async def test_optional_response_fields_and_empty_image_results_stay_valid():
    async with gateway({"output": None, "incomplete_details": None}) as (api, _calls):
        answer = await api.respond("prompt", model="test-model")
        assert answer.text == answer.reason == ""
    async with gateway({"data": []}, template=True) as (api, _calls):
        assert await api.images(["test-config"], context_node_id="node-1") == []


async def test_validation_errors_do_not_repeat_payload_data():
    secret = "DUMMY_RESPONSE_SECRET"
    async with gateway({"choices": [{"message": secret}]}, template=True) as (api, _calls):
        with pytest.raises(EduSharingError) as error:
            await api.chat(["test-config"], context_node_id="node-1")
    assert secret not in str(error.value)
