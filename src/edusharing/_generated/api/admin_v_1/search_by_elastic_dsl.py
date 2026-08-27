from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.search_result_elastic import SearchResultElastic
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    dsl: str | Unset = UNSET,
    index: str | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["dsl"] = dsl

    params["index"] = index

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/admin/v1/elastic",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | SearchResultElastic | None:
    if response.status_code == 200:
        response_200 = SearchResultElastic.from_dict(response.json())

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
) -> Response[ErrorResponse | SearchResultElastic]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    dsl: str | Unset = UNSET,
    index: str | Unset = UNSET,
) -> Response[ErrorResponse | SearchResultElastic]:
    """Search for custom elastic DSL query

    Args:
        dsl (str | Unset):
        index (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | SearchResultElastic]
    """

    kwargs = _get_kwargs(
        dsl=dsl,
        index=index,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    dsl: str | Unset = UNSET,
    index: str | Unset = UNSET,
) -> ErrorResponse | SearchResultElastic | None:
    """Search for custom elastic DSL query

    Args:
        dsl (str | Unset):
        index (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | SearchResultElastic
    """

    return sync_detailed(
        client=client,
        dsl=dsl,
        index=index,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    dsl: str | Unset = UNSET,
    index: str | Unset = UNSET,
) -> Response[ErrorResponse | SearchResultElastic]:
    """Search for custom elastic DSL query

    Args:
        dsl (str | Unset):
        index (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | SearchResultElastic]
    """

    kwargs = _get_kwargs(
        dsl=dsl,
        index=index,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    dsl: str | Unset = UNSET,
    index: str | Unset = UNSET,
) -> ErrorResponse | SearchResultElastic | None:
    """Search for custom elastic DSL query

    Args:
        dsl (str | Unset):
        index (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | SearchResultElastic
    """

    return (
        await asyncio_detailed(
            client=client,
            dsl=dsl,
            index=index,
        )
    ).parsed
