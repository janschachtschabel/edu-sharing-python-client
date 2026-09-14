"""Binary provider answers use the same routing/error boundary as JSON calls."""

import gzip
import json

import httpx
import pytest

from edusharing.bapi import BildungsAPI
from edusharing.errors import ContentTooLargeError, PermissionDeniedError, ValidationError


class Chunks(httpx.AsyncByteStream):
    def __init__(self, parts):
        self.parts = parts
        self.read = 0
        self.closed = False

    async def __aiter__(self):
        for part in self.parts:
            self.read += 1
            yield part

    async def aclose(self):
        self.closed = True


def api_for(client, **kwargs):
    return BildungsAPI("dummy-test-key", base_url="https://gateway.test", client=client,
                       max_retries=1, backoff_base=0, **kwargs)


async def test_speech_returns_bytes_with_correct_route_body_and_key():
    seen = []
    audio = b"ID3\x04\x00binary audio"
    body = {"model": "tts-1", "input": "Hello", "voice": "alloy"}

    def handler(request):
        seen.append(request)
        return httpx.Response(200, content=audio, headers={"content-type": "audio/mpeg"})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        async with api_for(client) as api:
            assert await api.call_bytes("audio/speech", body, provider="openai") == audio
        assert not client.is_closed
    assert len(seen) == 1
    assert seen[0].url.path == "/api/v1/llm/openai/audio/speech"
    assert seen[0].headers["x-api-key"] == "dummy-test-key"
    assert seen[0].headers["accept"] == "*/*"
    assert json.loads(seen[0].content) == body


async def test_binary_call_keeps_typed_json_errors():
    def handler(request):
        return httpx.Response(403, json={"error": {"message": "Denied"}})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(PermissionDeniedError, match="Denied"):
            await api_for(client).call_bytes("audio/speech", {}, max_bytes=10)


@pytest.mark.parametrize("route", ["../admin", "/audio/speech", "audio/speech?x=1"])
async def test_binary_route_is_rejected_before_sending(route):
    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(200, content=b"")

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(ValidationError):
            await api_for(client).call_bytes(route, {})
    assert seen == []


async def test_binary_limit_stops_reading_and_closes_the_stream():
    stream = Chunks([b"123", b"456", b"never read"])
    async with httpx.AsyncClient(transport=httpx.MockTransport(
            lambda request: httpx.Response(200, stream=stream))) as client:
        with pytest.raises(ContentTooLargeError):
            await api_for(client).call_bytes("audio/speech", {}, max_bytes=5)
    assert stream.read == 2
    assert stream.closed


async def test_compressed_binary_answer_is_decoded_once_with_a_decoded_size_limit():
    audio = b"A" * 1000
    packed = gzip.compress(audio)
    streams = []

    def handler(request):
        stream = Chunks([packed])
        streams.append(stream)
        return httpx.Response(200, stream=stream, headers={
            "content-encoding": "gzip", "content-length": str(len(packed))})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        api = api_for(client)
        assert await api.call_bytes("audio/speech", {}, max_bytes=len(audio)) == audio
        with pytest.raises(ContentTooLargeError):
            await api.call_bytes("audio/speech", {}, max_bytes=50)
    assert all(stream.closed for stream in streams)


async def test_binary_call_retries_rate_limits_using_the_existing_policy():
    seen = []

    def handler(request):
        seen.append(request)
        if len(seen) == 1:
            return httpx.Response(429, json={"message": "wait"}, headers={"retry-after": "0"})
        return httpx.Response(200, content=b"audio")

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        assert await api_for(client).call_bytes("audio/speech", {}, max_bytes=5) == b"audio"
    assert len(seen) == 2


async def test_binary_empty_answer_and_zero_limit_are_valid():
    async with httpx.AsyncClient(transport=httpx.MockTransport(
            lambda request: httpx.Response(200, content=b""))) as client:
        assert await api_for(client).call_bytes("audio/speech", {}, max_bytes=0) == b""
