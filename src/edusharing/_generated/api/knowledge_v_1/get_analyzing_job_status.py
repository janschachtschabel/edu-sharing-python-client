from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.job_entry import JobEntry
from ...types import Response


def _get_kwargs(
    job: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/knowledge/v1/analyze/jobs/{job}".format(
            job=quote(str(job), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | JobEntry | None:
    if response.status_code == 200:
        response_200 = JobEntry.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = cast(Any, None)
        return response_401

    if response.status_code == 403:
        response_403 = cast(Any, None)
        return response_403

    if response.status_code == 404:
        response_404 = cast(Any, None)
        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | JobEntry]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    job: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Any | JobEntry]:
    """Get analyzing job status.

     Get analyzing job status.

    Args:
        job (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | JobEntry]
    """

    kwargs = _get_kwargs(
        job=job,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    job: str,
    *,
    client: AuthenticatedClient | Client,
) -> Any | JobEntry | None:
    """Get analyzing job status.

     Get analyzing job status.

    Args:
        job (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | JobEntry
    """

    return sync_detailed(
        job=job,
        client=client,
    ).parsed


async def asyncio_detailed(
    job: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Any | JobEntry]:
    """Get analyzing job status.

     Get analyzing job status.

    Args:
        job (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | JobEntry]
    """

    kwargs = _get_kwargs(
        job=job,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    job: str,
    *,
    client: AuthenticatedClient | Client,
) -> Any | JobEntry | None:
    """Get analyzing job status.

     Get analyzing job status.

    Args:
        job (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | JobEntry
    """

    return (
        await asyncio_detailed(
            job=job,
            client=client,
        )
    ).parsed
