"""The decoded limit also bounds allocations while decompressing raw streams."""

import gzip
import tracemalloc
import zlib

import httpx
import pytest

from edusharing._http import _read_bounded_response
from edusharing.bapi import BildungsAPI
from edusharing.errors import ContentTooLargeError
from edusharing.transport import Transport


class Wire(httpx.AsyncByteStream):
    def __init__(self, parts):
        self.parts = parts

    async def __aiter__(self):
        for part in self.parts:
            yield part


def response(parts, encoding="gzip", status=200):
    return httpx.Response(status, stream=Wire(parts), headers={"content-encoding": encoding},
                          request=httpx.Request("GET", "https://repo.test/file"))


async def test_a_compressed_bomb_is_rejected_before_allocating_its_decoded_body():
    packed = gzip.compress(b"x" * (32 * 1024 * 1024))
    answer = response([packed])
    tracemalloc.start()
    try:
        with pytest.raises(ContentTooLargeError):
            await _read_bounded_response(answer, 1024, str(answer.url))
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
        await answer.aclose()
    assert peak < 2 * 1024 * 1024, f"allocated {peak} bytes for a 1 KiB limit"


@pytest.mark.parametrize("encoding, compress", [
    ("gzip", gzip.compress), ("deflate", zlib.compress),
    ("deflate", lambda data: zlib.compress(data, wbits=-zlib.MAX_WBITS)),
    ("gzip, deflate", lambda data: zlib.compress(gzip.compress(data))),
])
async def test_valid_compressed_data_survives_single_byte_wire_chunks(encoding, compress):
    data = b"A small, valid document.\n" * 20
    packed = compress(data)
    answer = response([packed[i:i + 1] for i in range(len(packed))], encoding)
    try:
        decoded = await _read_bounded_response(answer, len(data), str(answer.url))
        assert decoded.content == data
        assert "content-encoding" not in decoded.headers
    finally:
        await answer.aclose()


async def test_compressed_error_pages_also_have_bounded_allocations():
    packed = gzip.compress(b"x" * (32 * 1024 * 1024))
    answer = response([packed], status=403)
    tracemalloc.start()
    try:
        decoded = await _read_bounded_response(answer, 1024, str(answer.url))
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
        await answer.aclose()
    assert decoded.status_code == 403
    assert len(decoded.content) <= 64 * 1024
    assert peak < 2 * 1024 * 1024


@pytest.mark.parametrize("split", [False, True])
async def test_raw_deflate_may_start_with_a_valid_zlib_header(split):
    packed = bytes.fromhex("78 01 00 fe ff 61 01 00 00 ff ff")
    assert zlib.decompress(packed, wbits=-zlib.MAX_WBITS) == b"a"
    parts = [packed[i:i + 1] for i in range(len(packed))] if split else [packed]
    answer = response(parts, "deflate")
    assert (await _read_bounded_response(answer, 1, str(answer.url))).content == b"a"


@pytest.mark.parametrize("bapi", [False, True])
async def test_bounded_requests_negotiate_only_bounded_codecs(bapi):
    seen = []

    def handler(request):
        seen.append(request.headers["accept-encoding"])
        return httpx.Response(200, content=b"a")

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler),
                                headers={"accept-encoding": "gzip, deflate, br, zstd"}) as client:
        service = (BildungsAPI("test-key", base_url="https://gateway.test", client=client)
                   if bapi else Transport("https://repo.test/edu-sharing", client=client))
        async with service:
            if bapi:
                assert await service.call_bytes("audio/speech", {}, max_bytes=1) == b"a"
            else:
                assert await service.download("/file", max_bytes=1) == b"a"
        assert client.headers["accept-encoding"] == "gzip, deflate, br, zstd"
    assert seen == ["gzip, deflate"]
