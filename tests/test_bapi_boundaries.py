"""Follow-up audit: typed service boundaries and safe retry decisions."""

import json
from contextlib import asynccontextmanager

import httpx
import pytest

from edusharing.bapi import BildungsAPI
from edusharing.bapi.models import Model, rank_among, rank_models
from edusharing.errors import EduSharingError, RateLimitedError, ServerError


@asynccontextmanager
async def gateway(handler, **kwargs):
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        async with BildungsAPI("test-key", base_url="https://gateway.test", client=client,
                                max_retries=2, backoff_base=0, **kwargs) as api:
            yield api


@pytest.mark.parametrize("binary", [False, True])
async def test_uncertain_generic_write_is_not_sent_again(binary):
    calls = []

    def handler(request):
        calls.append(request)
        raise httpx.ReadTimeout("reply lost", request=request)

    async with gateway(handler) as api:
        method = api.call_bytes if binary else api.call
        with pytest.raises(EduSharingError, match="may have"):
            await method("batches", {"input_file_id": "file-1"})
    assert len(calls) == 1


async def test_generic_write_does_not_repeat_a_server_failure():
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(503, json={"error": "after storage"})

    async with gateway(handler) as api:
        with pytest.raises(ServerError):
            await api.call("fine_tuning/jobs", {})
    assert len(calls) == 1


async def test_connect_failure_before_sending_still_retries():
    calls = []

    def handler(request):
        calls.append(request)
        if len(calls) == 1:
            raise httpx.ConnectError("not connected", request=request)
        return httpx.Response(200, json={"id": "one-job"})

    async with gateway(handler) as api:
        assert await api.call("batches", {}) == {"id": "one-job"}
    assert len(calls) == 2


async def test_repeatable_generic_call_can_explicitly_opt_into_retries():
    calls = []

    def handler(request):
        calls.append(request)
        if len(calls) == 1:
            raise httpx.ReadTimeout("reply lost", request=request)
        return httpx.Response(200, json={"text": "answer"})

    async with gateway(handler) as api:
        assert await api.call("completions", {}, idempotent=True) == {"text": "answer"}
    assert len(calls) == 2


@pytest.mark.parametrize("bad", [[], {"choices": [None]}])
async def test_auto_selection_validates_the_answer_before_accepting_a_model(bad):
    tried = []

    def handler(request):
        if request.url.path.endswith("/models"):
            return httpx.Response(200, json={"data": [{"id": "a", "demand": 0},
                                                       {"id": "b", "demand": 1}]})
        tried.append(json.loads(request.content)["model"])
        return httpx.Response(200, json=bad if tried[-1] == "a" else
                              {"choices": [{"message": {"content": "valid"}}]})

    async with gateway(handler) as api:
        assert await api.chat("question") == "valid"
        assert api.last_model == "b"
    assert tried == ["a", "b"]


async def test_auto_selection_does_not_bypass_retry_after_on_the_same_key():
    tried = []

    def handler(request):
        if request.url.path.endswith("/models"):
            return httpx.Response(200, json={"data": [{"id": "a", "demand": 0},
                                                       {"id": "b", "demand": 1}]})
        tried.append(json.loads(request.content)["model"])
        return httpx.Response(429, headers={"retry-after": "3600"})

    async with gateway(handler) as api:
        with pytest.raises(RateLimitedError) as error:
            await api.chat("question")
        assert api.last_model is None
    assert tried == ["a"]
    assert error.value.status == 429 and error.value.retry_after == 3600


@pytest.mark.parametrize("payload", [[], None, "invalid"])
async def test_typed_responses_reject_non_objects(payload):
    async with gateway(lambda request: httpx.Response(
        200, content=json.dumps(payload).encode(), headers={"content-type": "application/json"}
    )) as api:
        with pytest.raises(EduSharingError):
            await api.respond("question", model="test-model")


@pytest.mark.parametrize("payload", [{"data": [None]}, {"data": "invalid"}, "invalid"])
async def test_invalid_model_lists_raise_library_errors(payload):
    async with gateway(lambda request: httpx.Response(200, json=payload)) as api:
        with pytest.raises(EduSharingError):
            await api.models()


@pytest.mark.parametrize("among", [None, ["unknown", "measured"]])
def test_unknown_demand_is_last_even_above_99(among):
    models = [Model("unknown"), Model("measured", demand=100)]
    ranked = rank_models(models) if among is None else rank_among(models, among)
    assert [m.id for m in ranked] == ["measured", "unknown"]
