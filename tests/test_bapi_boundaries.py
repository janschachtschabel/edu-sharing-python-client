"""Follow-up audit: typed service boundaries and safe retry decisions."""

import json
from contextlib import asynccontextmanager

import httpx
import pytest

from edusharing.bapi import BildungsAPI
from edusharing.bapi.models import Model, rank_among, rank_models
from edusharing.errors import (
    EduSharingError,
    RateLimitedError,
    ServerError,
    ValidationError,
)


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


# --- What the candidate loop may swallow, and what it may not -------------
#
# A candidate that does not answer is the loop's business. A request this
# caller's own arguments cannot produce is not: no model refused it, because
# none was ever asked.


def _listing(*ids):
    """A gateway whose /models lists these ids and answers everything else."""
    def handler(request):
        if request.url.path.endswith("/models"):
            return httpx.Response(200, json={
                "data": [{"id": mid, "demand": n} for n, mid in enumerate(ids)]})
        handler.asked.append(json.loads(request.content)["model"])
        return httpx.Response(200, json={"choices": [{"message": {"content": "ok"}}]})
    handler.asked = []
    return handler


async def test_an_effort_one_candidate_can_take_picks_that_candidate():
    """Skipping is the right answer, and this pins it.

    Whoever passes ``reasoning_effort=`` without a model has asked for the
    effort, not for a particular model. A candidate that cannot take it is the
    wrong candidate -- so the library moves on, and the wish is honoured by
    whoever answers. ``gemma`` ranks first here (demand 0) and is passed over.
    """
    handler = _listing("gemma-4-31b-it", "gpt-5.6-luna")
    async with gateway(handler) as api:
        assert await api.chat("question", reasoning_effort="high") == "ok"
        assert api.last_model == "gpt-5.6-luna"
    assert handler.asked == ["gpt-5.6-luna"], handler.asked


async def test_an_effort_no_candidate_can_take_is_the_callers_error():
    """When nobody can take it, it was never about availability.

    Measured before the fix: this raised ``EduSharingError: None of the models
    tried answered`` -- while **nothing had been sent**, so nothing had failed
    to answer. The same call with an explicit model has always raised
    ``ValidationError``, so the type depended on whether a model was named,
    for an error that is purely about the arguments. Someone catching
    ``ValidationError`` caught nothing and read a message about the gateway.
    """
    handler = _listing("gemma-4-31b-it", "qwen3.6-35b-a3b")
    async with gateway(handler) as api:
        with pytest.raises(ValidationError) as error:
            await api.chat("question", reasoning_effort="high")
    assert handler.asked == [], "nothing was sent, so nothing failed to answer"
    assert "reasoning_effort" in str(error.value), error.value


async def test_one_refusal_beside_one_real_failure_is_still_a_failure():
    """The boundary where the two error types part.

    If any candidate was actually asked and answered badly, the call is not
    purely about the arguments any more -- the gateway had its say. The
    generic error names both, the refusal and the answer, so whoever reads it
    can tell which was which.
    """
    def handler(request):
        if request.url.path.endswith("/models"):
            return httpx.Response(200, json={"data": [
                {"id": "gemma-4-31b-it", "demand": 0},
                {"id": "gpt-5.6-luna", "demand": 1}]})
        return httpx.Response(503, json={"error": "upstream busy"})

    async with gateway(handler) as api:
        with pytest.raises(EduSharingError) as error:
            await api.chat("question", reasoning_effort="high")
    meldung = str(error.value)
    assert "None of the models tried answered" in meldung
    assert "gemma-4-31b-it" in meldung and "gpt-5.6-luna" in meldung, meldung
    assert not isinstance(error.value, ValidationError), "one of them did answer"


async def test_respond_keeps_the_error_type_it_documents():
    """``respond`` gained the model policy on 2026-09-21 and inherited this
    with it -- before that it required a model and always raised
    ``ValidationError``. Its docstring still promises one."""
    def handler(request):
        if request.url.path.endswith("/models"):
            return httpx.Response(200, json={"data": [{"id": "gemma-4-31b-it", "demand": 0}]})
        raise AssertionError("no request should be sent")

    async with gateway(handler) as api:
        with pytest.raises(ValidationError):
            await api.respond("question", reasoning_effort="high")


async def test_a_named_model_is_recorded_only_once_its_answer_was_read():
    """``last_model`` says who the answer came from -- so an answer that could
    not be read leaves it alone.

    The automatic branch has always validated first (the test above), and the
    reference states that rule. The named branch did too, until the model
    policy moved to ``choice`` on 2026-09-21 and the two fell out of step.
    """
    def handler(request):
        if request.url.path.endswith("/models"):
            return httpx.Response(200, json={"data": [{"id": "a", "demand": 0}]})
        return httpx.Response(200, json={"choices": [None]})

    async with gateway(handler) as api:
        with pytest.raises(EduSharingError, match="choices"):
            await api.chat("question", model="named")
        assert api.last_model is None, "nothing readable came back, so nobody answered"


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
