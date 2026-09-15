"""Incremental gzip/deflate decoding with bounded output allocations."""

from __future__ import annotations

import zlib
from collections.abc import AsyncIterator, Iterator

import httpx

_CHUNK_SIZE = 64 * 1024
_MAX_ENCODINGS = 4


class _DecodeLimit(Exception):
    """An intermediate compressed layer exceeded the decoding budget."""


class _Inflater:
    def __init__(self, encoding: str, limit: int) -> None:
        self._decoder = zlib.decompressobj(16 + zlib.MAX_WBITS) if encoding == "gzip" else None
        self._prefix = b""
        self._probe: bytearray | None = None
        self._seen = False
        self._limit = limit + _CHUNK_SIZE
        self._chunk_size = min(_CHUNK_SIZE, limit + 1)
        self._received = 0

    def feed(self, data: bytes) -> Iterator[bytes]:
        self._seen |= bool(data)
        if self._decoder is None:
            # Two header bytes distinguish zlib-wrapped from raw deflate even
            # when the wire splits the header across separate chunks.
            needed = 2 - len(self._prefix)
            self._prefix += data[:needed]
            data = data[needed:]
            if len(self._prefix) < 2:
                return
            cmf, flg = self._prefix
            wrapped = cmf & 15 == 8 and (cmf * 256 + flg) % 31 == 0
            self._decoder = zlib.decompressobj(zlib.MAX_WBITS if wrapped else -zlib.MAX_WBITS)
            self._probe = bytearray() if wrapped else None
            data = self._prefix + data
            self._prefix = b""
        if self._probe is not None:
            # A zlib-looking prefix can also be raw deflate padding. Retain a
            # bounded prefix until the first output commits that interpretation.
            if len(self._probe) + len(data) <= _CHUNK_SIZE:
                self._probe.extend(data)
            else:
                self._probe = None
        try:
            yield from self._with_fallback(data)
        except zlib.error as exc:
            raise httpx.DecodingError("Invalid compressed response") from exc

    def _with_fallback(self, data: bytes) -> Iterator[bytes]:
        try:
            yield from self._inflate(data)
        except zlib.error:
            if self._probe is None:
                raise
            data, self._probe = bytes(self._probe), None
            self._decoder = zlib.decompressobj(-zlib.MAX_WBITS)
            yield from self._inflate(data)

    def _inflate(self, data: bytes) -> Iterator[bytes]:
        assert self._decoder is not None  # selected before any data is inflated
        while True:
            size = min(self._chunk_size, self._limit - self._received + 1)
            chunk = self._decoder.decompress(data, max_length=size)
            self._received += len(chunk)
            if self._received > self._limit:
                raise _DecodeLimit
            if chunk:
                self._probe = None
                yield chunk
            data = self._decoder.unconsumed_tail
            if not data and len(chunk) < size:
                break

    def finish(self) -> None:
        # decompress(..., max_length=...) drains bounded chunks in feed().
        # flush() would allocate without an upper limit again.
        if self._seen and (self._decoder is None or not self._decoder.eof):
            raise httpx.DecodingError("Incomplete compressed response")


def _through(data: bytes, decoders: list[_Inflater], index: int = 0) -> Iterator[bytes]:
    if index == len(decoders):
        yield data
    else:
        for chunk in decoders[index].feed(data):
            yield from _through(chunk, decoders, index + 1)


async def _decoded_chunks(response: httpx.Response, limit: int) -> AsyncIterator[bytes]:
    """Read raw wire bytes; no HTTPX decoder may allocate the complete body."""
    encodings = [
        part.strip().lower() for part in response.headers.get_list("content-encoding", True)
        if part.strip().lower() not in ("", "identity")
    ]
    if len(encodings) > _MAX_ENCODINGS or any(e not in ("gzip", "deflate") for e in encodings):
        raise httpx.DecodingError("Bounded downloads support gzip, deflate or identity encoding")
    if response.is_stream_consumed:
        # An injected already-buffered response was decoded by its owner.
        # We can enforce its size, but cannot undo allocations made there.
        yield response.content
        return
    decoders = [_Inflater(encoding, limit) for encoding in reversed(encodings)]
    async for raw in response.aiter_raw():
        if not decoders:
            yield raw
            continue
        for start in range(0, len(raw), _CHUNK_SIZE):
            part = bytes(memoryview(raw)[start:start + _CHUNK_SIZE])
            for chunk in _through(part, decoders):
                yield chunk
    for decoder in decoders:
        decoder.finish()
