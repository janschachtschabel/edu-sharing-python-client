from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.get_assocs_direction import GetAssocsDirection
from ...models.node_entries import NodeEntries
from ...types import UNSET, Response, Unset


def _get_kwargs(
    repository: str,
    node: str,
    *,
    max_items: int | Unset = 500,
    skip_count: int | Unset = 0,
    sort_properties: list[str] | Unset = UNSET,
    sort_ascending: list[bool] | Unset = UNSET,
    direction: GetAssocsDirection,
    assoc_name: str | Unset = UNSET,
    property_filter: list[str] | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["maxItems"] = max_items

    params["skipCount"] = skip_count

    json_sort_properties: list[str] | Unset = UNSET
    if not isinstance(sort_properties, Unset):
        json_sort_properties = sort_properties

    params["sortProperties"] = json_sort_properties

    json_sort_ascending: list[bool] | Unset = UNSET
    if not isinstance(sort_ascending, Unset):
        json_sort_ascending = sort_ascending

    params["sortAscending"] = json_sort_ascending

    json_direction = direction.value
    params["direction"] = json_direction

    params["assocName"] = assoc_name

    json_property_filter: list[str] | Unset = UNSET
    if not isinstance(property_filter, Unset):
        json_property_filter = property_filter

    params["propertyFilter"] = json_property_filter

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/node/v1/nodes/{repository}/{node}/assocs".format(
            repository=quote(str(repository), safe=""),
            node=quote(str(node), safe=""),
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
    node: str,
    *,
    client: AuthenticatedClient | Client,
    max_items: int | Unset = 500,
    skip_count: int | Unset = 0,
    sort_properties: list[str] | Unset = UNSET,
    sort_ascending: list[bool] | Unset = UNSET,
    direction: GetAssocsDirection,
    assoc_name: str | Unset = UNSET,
    property_filter: list[str] | Unset = UNSET,
) -> Response[ErrorResponse | NodeEntries]:
    """Get related nodes.

     Get nodes related based on an assoc.

    Args:
        repository (str):
        node (str):
        max_items (int | Unset):  Default: 500.
        skip_count (int | Unset):  Default: 0.
        sort_properties (list[str] | Unset):
        sort_ascending (list[bool] | Unset):
        direction (GetAssocsDirection):
        assoc_name (str | Unset):
        property_filter (list[str] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | NodeEntries]
    """

    kwargs = _get_kwargs(
        repository=repository,
        node=node,
        max_items=max_items,
        skip_count=skip_count,
        sort_properties=sort_properties,
        sort_ascending=sort_ascending,
        direction=direction,
        assoc_name=assoc_name,
        property_filter=property_filter,
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
    max_items: int | Unset = 500,
    skip_count: int | Unset = 0,
    sort_properties: list[str] | Unset = UNSET,
    sort_ascending: list[bool] | Unset = UNSET,
    direction: GetAssocsDirection,
    assoc_name: str | Unset = UNSET,
    property_filter: list[str] | Unset = UNSET,
) -> ErrorResponse | NodeEntries | None:
    """Get related nodes.

     Get nodes related based on an assoc.

    Args:
        repository (str):
        node (str):
        max_items (int | Unset):  Default: 500.
        skip_count (int | Unset):  Default: 0.
        sort_properties (list[str] | Unset):
        sort_ascending (list[bool] | Unset):
        direction (GetAssocsDirection):
        assoc_name (str | Unset):
        property_filter (list[str] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | NodeEntries
    """

    return sync_detailed(
        repository=repository,
        node=node,
        client=client,
        max_items=max_items,
        skip_count=skip_count,
        sort_properties=sort_properties,
        sort_ascending=sort_ascending,
        direction=direction,
        assoc_name=assoc_name,
        property_filter=property_filter,
    ).parsed


async def asyncio_detailed(
    repository: str,
    node: str,
    *,
    client: AuthenticatedClient | Client,
    max_items: int | Unset = 500,
    skip_count: int | Unset = 0,
    sort_properties: list[str] | Unset = UNSET,
    sort_ascending: list[bool] | Unset = UNSET,
    direction: GetAssocsDirection,
    assoc_name: str | Unset = UNSET,
    property_filter: list[str] | Unset = UNSET,
) -> Response[ErrorResponse | NodeEntries]:
    """Get related nodes.

     Get nodes related based on an assoc.

    Args:
        repository (str):
        node (str):
        max_items (int | Unset):  Default: 500.
        skip_count (int | Unset):  Default: 0.
        sort_properties (list[str] | Unset):
        sort_ascending (list[bool] | Unset):
        direction (GetAssocsDirection):
        assoc_name (str | Unset):
        property_filter (list[str] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | NodeEntries]
    """

    kwargs = _get_kwargs(
        repository=repository,
        node=node,
        max_items=max_items,
        skip_count=skip_count,
        sort_properties=sort_properties,
        sort_ascending=sort_ascending,
        direction=direction,
        assoc_name=assoc_name,
        property_filter=property_filter,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    node: str,
    *,
    client: AuthenticatedClient | Client,
    max_items: int | Unset = 500,
    skip_count: int | Unset = 0,
    sort_properties: list[str] | Unset = UNSET,
    sort_ascending: list[bool] | Unset = UNSET,
    direction: GetAssocsDirection,
    assoc_name: str | Unset = UNSET,
    property_filter: list[str] | Unset = UNSET,
) -> ErrorResponse | NodeEntries | None:
    """Get related nodes.

     Get nodes related based on an assoc.

    Args:
        repository (str):
        node (str):
        max_items (int | Unset):  Default: 500.
        skip_count (int | Unset):  Default: 0.
        sort_properties (list[str] | Unset):
        sort_ascending (list[bool] | Unset):
        direction (GetAssocsDirection):
        assoc_name (str | Unset):
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
            node=node,
            client=client,
            max_items=max_items,
            skip_count=skip_count,
            sort_properties=sort_properties,
            sort_ascending=sort_ascending,
            direction=direction,
            assoc_name=assoc_name,
            property_filter=property_filter,
        )
    ).parsed
