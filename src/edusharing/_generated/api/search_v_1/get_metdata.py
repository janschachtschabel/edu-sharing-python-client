from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.node_entries import NodeEntries
from ...types import UNSET, Response, Unset


def _get_kwargs(
    repository: str,
    *,
    node_ids: list[str] | Unset = UNSET,
    property_filter: list[str] | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_node_ids: list[str] | Unset = UNSET
    if not isinstance(node_ids, Unset):
        json_node_ids = node_ids

    params["nodeIds"] = json_node_ids

    json_property_filter: list[str] | Unset = UNSET
    if not isinstance(property_filter, Unset):
        json_property_filter = property_filter

    params["propertyFilter"] = json_property_filter

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/search/v1/metadata/{repository}".format(
            repository=quote(str(repository), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | NodeEntries | None:
    if response.status_code == 200:
        response_200 = NodeEntries.from_dict(response.json())

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
) -> Response[ErrorResponse | NodeEntries]:
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
    node_ids: list[str] | Unset = UNSET,
    property_filter: list[str] | Unset = UNSET,
) -> Response[ErrorResponse | NodeEntries]:
    """get nodes with metadata and collections

    Args:
        repository (str):
        node_ids (list[str] | Unset):
        property_filter (list[str] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | NodeEntries]
    """

    kwargs = _get_kwargs(
        repository=repository,
        node_ids=node_ids,
        property_filter=property_filter,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repository: str,
    *,
    client: AuthenticatedClient | Client,
    node_ids: list[str] | Unset = UNSET,
    property_filter: list[str] | Unset = UNSET,
) -> ErrorResponse | NodeEntries | None:
    """get nodes with metadata and collections

    Args:
        repository (str):
        node_ids (list[str] | Unset):
        property_filter (list[str] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | NodeEntries
    """

    return sync_detailed(
        repository=repository,
        client=client,
        node_ids=node_ids,
        property_filter=property_filter,
    ).parsed


async def asyncio_detailed(
    repository: str,
    *,
    client: AuthenticatedClient | Client,
    node_ids: list[str] | Unset = UNSET,
    property_filter: list[str] | Unset = UNSET,
) -> Response[ErrorResponse | NodeEntries]:
    """get nodes with metadata and collections

    Args:
        repository (str):
        node_ids (list[str] | Unset):
        property_filter (list[str] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | NodeEntries]
    """

    kwargs = _get_kwargs(
        repository=repository,
        node_ids=node_ids,
        property_filter=property_filter,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    *,
    client: AuthenticatedClient | Client,
    node_ids: list[str] | Unset = UNSET,
    property_filter: list[str] | Unset = UNSET,
) -> ErrorResponse | NodeEntries | None:
    """get nodes with metadata and collections

    Args:
        repository (str):
        node_ids (list[str] | Unset):
        property_filter (list[str] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | NodeEntries
    """

    return (
        await asyncio_detailed(
            repository=repository,
            client=client,
            node_ids=node_ids,
            property_filter=property_filter,
        )
    ).parsed
