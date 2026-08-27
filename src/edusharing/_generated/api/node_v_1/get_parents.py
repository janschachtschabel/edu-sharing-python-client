from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.parent_entries import ParentEntries
from ...types import UNSET, Response, Unset


def _get_kwargs(
    repository: str,
    node: str,
    *,
    property_filter: list[str] | Unset = UNSET,
    full_path: bool | Unset = UNSET,
    ignore_access_error: bool | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_property_filter: list[str] | Unset = UNSET
    if not isinstance(property_filter, Unset):
        json_property_filter = property_filter

    params["propertyFilter"] = json_property_filter

    params["fullPath"] = full_path

    params["ignoreAccessError"] = ignore_access_error

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/node/v1/nodes/{repository}/{node}/parents".format(
            repository=quote(str(repository), safe=""),
            node=quote(str(node), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | ParentEntries | None:
    if response.status_code == 200:
        response_200 = ParentEntries.from_dict(response.json())

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
) -> Response[ErrorResponse | ParentEntries]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    repository: str,
    node: str,
    *,
    client: AuthenticatedClient | Client,
    property_filter: list[str] | Unset = UNSET,
    full_path: bool | Unset = UNSET,
    ignore_access_error: bool | Unset = UNSET,
) -> Response[ErrorResponse | ParentEntries]:
    """Get parents of node.

     Get all parents metadata + own metadata of node. Index 0 is always the current node

    Args:
        repository (str):
        node (str):
        property_filter (list[str] | Unset):
        full_path (bool | Unset):
        ignore_access_error (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | ParentEntries]
    """

    kwargs = _get_kwargs(
        repository=repository,
        node=node,
        property_filter=property_filter,
        full_path=full_path,
        ignore_access_error=ignore_access_error,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repository: str,
    node: str,
    *,
    client: AuthenticatedClient | Client,
    property_filter: list[str] | Unset = UNSET,
    full_path: bool | Unset = UNSET,
    ignore_access_error: bool | Unset = UNSET,
) -> ErrorResponse | ParentEntries | None:
    """Get parents of node.

     Get all parents metadata + own metadata of node. Index 0 is always the current node

    Args:
        repository (str):
        node (str):
        property_filter (list[str] | Unset):
        full_path (bool | Unset):
        ignore_access_error (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | ParentEntries
    """

    return sync_detailed(
        repository=repository,
        node=node,
        client=client,
        property_filter=property_filter,
        full_path=full_path,
        ignore_access_error=ignore_access_error,
    ).parsed


async def asyncio_detailed(
    repository: str,
    node: str,
    *,
    client: AuthenticatedClient | Client,
    property_filter: list[str] | Unset = UNSET,
    full_path: bool | Unset = UNSET,
    ignore_access_error: bool | Unset = UNSET,
) -> Response[ErrorResponse | ParentEntries]:
    """Get parents of node.

     Get all parents metadata + own metadata of node. Index 0 is always the current node

    Args:
        repository (str):
        node (str):
        property_filter (list[str] | Unset):
        full_path (bool | Unset):
        ignore_access_error (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | ParentEntries]
    """

    kwargs = _get_kwargs(
        repository=repository,
        node=node,
        property_filter=property_filter,
        full_path=full_path,
        ignore_access_error=ignore_access_error,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    node: str,
    *,
    client: AuthenticatedClient | Client,
    property_filter: list[str] | Unset = UNSET,
    full_path: bool | Unset = UNSET,
    ignore_access_error: bool | Unset = UNSET,
) -> ErrorResponse | ParentEntries | None:
    """Get parents of node.

     Get all parents metadata + own metadata of node. Index 0 is always the current node

    Args:
        repository (str):
        node (str):
        property_filter (list[str] | Unset):
        full_path (bool | Unset):
        ignore_access_error (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | ParentEntries
    """

    return (
        await asyncio_detailed(
            repository=repository,
            node=node,
            client=client,
            property_filter=property_filter,
            full_path=full_path,
            ignore_access_error=ignore_access_error,
        )
    ).parsed
