from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.status_mode import StatusMode
from ...types import UNSET, Response, Unset


def _get_kwargs(
    mode: StatusMode,
    *,
    timeout_seconds: int | Unset = 10,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["timeoutSeconds"] = timeout_seconds

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/_about/status/{mode}".format(
            mode=quote(str(mode), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | str | None:
    if response.status_code == 200:
        response_200 = cast(str, response.json())
        return response_200

    if response.status_code == 400:
        response_400 = ErrorResponse.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = ErrorResponse.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = ErrorResponse.from_dict(response.json())

        return response_403

    if response.status_code == 404:
        response_404 = ErrorResponse.from_dict(response.json())

        return response_404

    if response.status_code == 500:
        response_500 = ErrorResponse.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ErrorResponse | str]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    mode: StatusMode,
    *,
    client: AuthenticatedClient | Client,
    timeout_seconds: int | Unset = 10,
) -> Response[ErrorResponse | str]:
    """status of repo services

     returns http status 200 when ok

    Args:
        mode (StatusMode):
        timeout_seconds (int | Unset):  Default: 10.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | str]
    """

    kwargs = _get_kwargs(
        mode=mode,
        timeout_seconds=timeout_seconds,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    mode: StatusMode,
    *,
    client: AuthenticatedClient | Client,
    timeout_seconds: int | Unset = 10,
) -> ErrorResponse | str | None:
    """status of repo services

     returns http status 200 when ok

    Args:
        mode (StatusMode):
        timeout_seconds (int | Unset):  Default: 10.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | str
    """

    return sync_detailed(
        mode=mode,
        client=client,
        timeout_seconds=timeout_seconds,
    ).parsed


async def asyncio_detailed(
    mode: StatusMode,
    *,
    client: AuthenticatedClient | Client,
    timeout_seconds: int | Unset = 10,
) -> Response[ErrorResponse | str]:
    """status of repo services

     returns http status 200 when ok

    Args:
        mode (StatusMode):
        timeout_seconds (int | Unset):  Default: 10.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | str]
    """

    kwargs = _get_kwargs(
        mode=mode,
        timeout_seconds=timeout_seconds,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    mode: StatusMode,
    *,
    client: AuthenticatedClient | Client,
    timeout_seconds: int | Unset = 10,
) -> ErrorResponse | str | None:
    """status of repo services

     returns http status 200 when ok

    Args:
        mode (StatusMode):
        timeout_seconds (int | Unset):  Default: 10.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | str
    """

    return (
        await asyncio_detailed(
            mode=mode,
            client=client,
            timeout_seconds=timeout_seconds,
        )
    ).parsed
