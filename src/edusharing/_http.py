"""Bounded HTTP response reading shared by repository and b-api downloads."""

import httpx

from .errors import ContentTooLargeError

_ERROR_PAGE_LIMIT = 64 * 1024


def _check_size(size: int, max_bytes: int, url: str) -> None:
    if size > max_bytes:
        raise ContentTooLargeError(
            f"The file is larger than max_bytes={max_bytes}: {size} bytes "
            "(announced, or received so far). Raise the limit only if this "
            "response size is expected.", url=url)


async def _read_bounded_response(
    response: httpx.Response, max_bytes: int, url: str,
) -> httpx.Response:
    """Read decoded bytes, retaining a bounded error page for error mapping.

    The caller owns the response context and closes it on every exit path.
    """
    success = response.status_code < 300
    # Content-Length describes wire bytes; with compression only the decoded
    # count can be compared with the caller's limit (audit F05).
    announced = response.headers.get("content-length", "")
    if (success and "content-encoding" not in response.headers
            and announced.isascii() and announced.isdigit()):
        _check_size(int(announced), max_bytes, url)
    chunks: list[bytes] = []
    received = 0
    async for chunk in response.aiter_bytes():
        received += len(chunk)
        if success:
            _check_size(received, max_bytes, url)
        elif received > _ERROR_PAGE_LIMIT:
            break
        chunks.append(chunk)
    # HTTPX has decoded these bytes already. Keeping the encoding header would
    # make the rebuilt response decompress them a second time (audit F05).
    headers = httpx.Headers(response.headers)
    headers.pop("content-encoding", None)
    headers.pop("content-length", None)
    return httpx.Response(
        response.status_code, headers=headers,
        content=b"".join(chunks), request=response.request)
