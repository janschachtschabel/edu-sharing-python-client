from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.logger_config_result import LoggerConfigResult
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    filters: list[str] | Unset = UNSET,
    only_config: bool | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_filters: list[str] | Unset = UNSET
    if not isinstance(filters, Unset):
        json_filters = filters

    params["filters"] = json_filters

    params["onlyConfig"] = only_config

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/admin/v1/log/config",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | LoggerConfigResult | None:
    if response.status_code == 200:
        response_200 = LoggerConfigResult.from_dict(response.json())

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

    if response.status_code == 409:
        response_409 = ErrorResponse.from_dict(response.json())

        return response_409

    if response.status_code == 500:
        response_500 = ErrorResponse.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ErrorResponse | LoggerConfigResult]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    filters: list[str] | Unset = UNSET,
    only_config: bool | Unset = UNSET,
) -> Response[ErrorResponse | LoggerConfigResult]:
    """get the logger config

    Args:
        filters (list[str] | Unset):
        only_config (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | LoggerConfigResult]
    """

    kwargs = _get_kwargs(
        filters=filters,
        only_config=only_config,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    filters: list[str] | Unset = UNSET,
    only_config: bool | Unset = UNSET,
) -> ErrorResponse | LoggerConfigResult | None:
    """get the logger config

    Args:
        filters (list[str] | Unset):
        only_config (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | LoggerConfigResult
    """

    return sync_detailed(
        client=client,
        filters=filters,
        only_config=only_config,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    filters: list[str] | Unset = UNSET,
    only_config: bool | Unset = UNSET,
) -> Response[ErrorResponse | LoggerConfigResult]:
    """get the logger config

    Args:
        filters (list[str] | Unset):
        only_config (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | LoggerConfigResult]
    """

    kwargs = _get_kwargs(
        filters=filters,
        only_config=only_config,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    filters: list[str] | Unset = UNSET,
    only_config: bool | Unset = UNSET,
) -> ErrorResponse | LoggerConfigResult | None:
    """get the logger config

    Args:
        filters (list[str] | Unset):
        only_config (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | LoggerConfigResult
    """

    return (
        await asyncio_detailed(
            client=client,
            filters=filters,
            only_config=only_config,
        )
    ).parsed
