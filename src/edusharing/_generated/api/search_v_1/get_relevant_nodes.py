from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.search_result_node import SearchResultNode
from ...types import UNSET, Response, Unset


def _get_kwargs(
    repository: str,
    *,
    property_filter: list[str] | Unset = UNSET,
    max_items: int | Unset = 10,
    skip_count: int | Unset = 0,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_property_filter: list[str] | Unset = UNSET
    if not isinstance(property_filter, Unset):
        json_property_filter = property_filter

    params["propertyFilter"] = json_property_filter

    params["maxItems"] = max_items

    params["skipCount"] = skip_count

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/search/v1/relevant/{repository}".format(
            repository=quote(str(repository), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | SearchResultNode | None:
    if response.status_code == 200:
        response_200 = SearchResultNode.from_dict(response.json())

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
) -> Response[ErrorResponse | SearchResultNode]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    repository: str,
    *,
    client: AuthenticatedClient | Client,
    property_filter: list[str] | Unset = UNSET,
    max_items: int | Unset = 10,
    skip_count: int | Unset = 0,
) -> Response[ErrorResponse | SearchResultNode]:
    """Get relevant nodes for the current user

    Args:
        repository (str):
        property_filter (list[str] | Unset):
        max_items (int | Unset):  Default: 10.
        skip_count (int | Unset):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | SearchResultNode]
    """

    kwargs = _get_kwargs(
        repository=repository,
        property_filter=property_filter,
        max_items=max_items,
        skip_count=skip_count,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repository: str,
    *,
    client: AuthenticatedClient | Client,
    property_filter: list[str] | Unset = UNSET,
    max_items: int | Unset = 10,
    skip_count: int | Unset = 0,
) -> ErrorResponse | SearchResultNode | None:
    """Get relevant nodes for the current user

    Args:
        repository (str):
        property_filter (list[str] | Unset):
        max_items (int | Unset):  Default: 10.
        skip_count (int | Unset):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | SearchResultNode
    """

    return sync_detailed(
        repository=repository,
        client=client,
        property_filter=property_filter,
        max_items=max_items,
        skip_count=skip_count,
    ).parsed


async def asyncio_detailed(
    repository: str,
    *,
    client: AuthenticatedClient | Client,
    property_filter: list[str] | Unset = UNSET,
    max_items: int | Unset = 10,
    skip_count: int | Unset = 0,
) -> Response[ErrorResponse | SearchResultNode]:
    """Get relevant nodes for the current user

    Args:
        repository (str):
        property_filter (list[str] | Unset):
        max_items (int | Unset):  Default: 10.
        skip_count (int | Unset):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | SearchResultNode]
    """

    kwargs = _get_kwargs(
        repository=repository,
        property_filter=property_filter,
        max_items=max_items,
        skip_count=skip_count,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    *,
    client: AuthenticatedClient | Client,
    property_filter: list[str] | Unset = UNSET,
    max_items: int | Unset = 10,
    skip_count: int | Unset = 0,
) -> ErrorResponse | SearchResultNode | None:
    """Get relevant nodes for the current user

    Args:
        repository (str):
        property_filter (list[str] | Unset):
        max_items (int | Unset):  Default: 10.
        skip_count (int | Unset):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | SearchResultNode
    """

    return (
        await asyncio_detailed(
            repository=repository,
            client=client,
            property_filter=property_filter,
            max_items=max_items,
            skip_count=skip_count,
        )
    ).parsed
