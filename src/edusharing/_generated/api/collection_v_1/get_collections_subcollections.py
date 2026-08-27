from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.collection_entries import CollectionEntries
from ...models.error_response import ErrorResponse
from ...models.get_collections_subcollections_scope import GetCollectionsSubcollectionsScope
from ...types import UNSET, Response, Unset


def _get_kwargs(
    repository: str,
    collection: str,
    *,
    scope: GetCollectionsSubcollectionsScope = GetCollectionsSubcollectionsScope.MY,
    fetch_counts: bool | Unset = True,
    max_items: int | Unset = 500,
    skip_count: int | Unset = 0,
    sort_properties: list[str] | Unset = UNSET,
    sort_ascending: list[bool] | Unset = UNSET,
    property_filter: list[str] | Unset = UNSET,
    resolve_inherited_access: bool | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_scope = scope.value
    params["scope"] = json_scope

    params["fetchCounts"] = fetch_counts

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

    json_property_filter: list[str] | Unset = UNSET
    if not isinstance(property_filter, Unset):
        json_property_filter = property_filter

    params["propertyFilter"] = json_property_filter

    params["resolveInheritedAccess"] = resolve_inherited_access

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/collection/v1/collections/{repository}/{collection}/children/collections".format(
            repository=quote(str(repository), safe=""),
            collection=quote(str(collection), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> CollectionEntries | ErrorResponse | None:
    if response.status_code == 200:
        response_200 = CollectionEntries.from_dict(response.json())

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
) -> Response[CollectionEntries | ErrorResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    repository: str,
    collection: str,
    *,
    client: AuthenticatedClient | Client,
    scope: GetCollectionsSubcollectionsScope = GetCollectionsSubcollectionsScope.MY,
    fetch_counts: bool | Unset = True,
    max_items: int | Unset = 500,
    skip_count: int | Unset = 0,
    sort_properties: list[str] | Unset = UNSET,
    sort_ascending: list[bool] | Unset = UNSET,
    property_filter: list[str] | Unset = UNSET,
    resolve_inherited_access: bool | Unset = UNSET,
) -> Response[CollectionEntries | ErrorResponse]:
    """Get child collections for collection (or root).

    Args:
        repository (str):
        collection (str):
        scope (GetCollectionsSubcollectionsScope):  Default: GetCollectionsSubcollectionsScope.MY.
        fetch_counts (bool | Unset):  Default: True.
        max_items (int | Unset):  Default: 500.
        skip_count (int | Unset):  Default: 0.
        sort_properties (list[str] | Unset):
        sort_ascending (list[bool] | Unset):
        property_filter (list[str] | Unset):
        resolve_inherited_access (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CollectionEntries | ErrorResponse]
    """

    kwargs = _get_kwargs(
        repository=repository,
        collection=collection,
        scope=scope,
        fetch_counts=fetch_counts,
        max_items=max_items,
        skip_count=skip_count,
        sort_properties=sort_properties,
        sort_ascending=sort_ascending,
        property_filter=property_filter,
        resolve_inherited_access=resolve_inherited_access,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repository: str,
    collection: str,
    *,
    client: AuthenticatedClient | Client,
    scope: GetCollectionsSubcollectionsScope = GetCollectionsSubcollectionsScope.MY,
    fetch_counts: bool | Unset = True,
    max_items: int | Unset = 500,
    skip_count: int | Unset = 0,
    sort_properties: list[str] | Unset = UNSET,
    sort_ascending: list[bool] | Unset = UNSET,
    property_filter: list[str] | Unset = UNSET,
    resolve_inherited_access: bool | Unset = UNSET,
) -> CollectionEntries | ErrorResponse | None:
    """Get child collections for collection (or root).

    Args:
        repository (str):
        collection (str):
        scope (GetCollectionsSubcollectionsScope):  Default: GetCollectionsSubcollectionsScope.MY.
        fetch_counts (bool | Unset):  Default: True.
        max_items (int | Unset):  Default: 500.
        skip_count (int | Unset):  Default: 0.
        sort_properties (list[str] | Unset):
        sort_ascending (list[bool] | Unset):
        property_filter (list[str] | Unset):
        resolve_inherited_access (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CollectionEntries | ErrorResponse
    """

    return sync_detailed(
        repository=repository,
        collection=collection,
        client=client,
        scope=scope,
        fetch_counts=fetch_counts,
        max_items=max_items,
        skip_count=skip_count,
        sort_properties=sort_properties,
        sort_ascending=sort_ascending,
        property_filter=property_filter,
        resolve_inherited_access=resolve_inherited_access,
    ).parsed


async def asyncio_detailed(
    repository: str,
    collection: str,
    *,
    client: AuthenticatedClient | Client,
    scope: GetCollectionsSubcollectionsScope = GetCollectionsSubcollectionsScope.MY,
    fetch_counts: bool | Unset = True,
    max_items: int | Unset = 500,
    skip_count: int | Unset = 0,
    sort_properties: list[str] | Unset = UNSET,
    sort_ascending: list[bool] | Unset = UNSET,
    property_filter: list[str] | Unset = UNSET,
    resolve_inherited_access: bool | Unset = UNSET,
) -> Response[CollectionEntries | ErrorResponse]:
    """Get child collections for collection (or root).

    Args:
        repository (str):
        collection (str):
        scope (GetCollectionsSubcollectionsScope):  Default: GetCollectionsSubcollectionsScope.MY.
        fetch_counts (bool | Unset):  Default: True.
        max_items (int | Unset):  Default: 500.
        skip_count (int | Unset):  Default: 0.
        sort_properties (list[str] | Unset):
        sort_ascending (list[bool] | Unset):
        property_filter (list[str] | Unset):
        resolve_inherited_access (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CollectionEntries | ErrorResponse]
    """

    kwargs = _get_kwargs(
        repository=repository,
        collection=collection,
        scope=scope,
        fetch_counts=fetch_counts,
        max_items=max_items,
        skip_count=skip_count,
        sort_properties=sort_properties,
        sort_ascending=sort_ascending,
        property_filter=property_filter,
        resolve_inherited_access=resolve_inherited_access,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    collection: str,
    *,
    client: AuthenticatedClient | Client,
    scope: GetCollectionsSubcollectionsScope = GetCollectionsSubcollectionsScope.MY,
    fetch_counts: bool | Unset = True,
    max_items: int | Unset = 500,
    skip_count: int | Unset = 0,
    sort_properties: list[str] | Unset = UNSET,
    sort_ascending: list[bool] | Unset = UNSET,
    property_filter: list[str] | Unset = UNSET,
    resolve_inherited_access: bool | Unset = UNSET,
) -> CollectionEntries | ErrorResponse | None:
    """Get child collections for collection (or root).

    Args:
        repository (str):
        collection (str):
        scope (GetCollectionsSubcollectionsScope):  Default: GetCollectionsSubcollectionsScope.MY.
        fetch_counts (bool | Unset):  Default: True.
        max_items (int | Unset):  Default: 500.
        skip_count (int | Unset):  Default: 0.
        sort_properties (list[str] | Unset):
        sort_ascending (list[bool] | Unset):
        property_filter (list[str] | Unset):
        resolve_inherited_access (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CollectionEntries | ErrorResponse
    """

    return (
        await asyncio_detailed(
            repository=repository,
            collection=collection,
            client=client,
            scope=scope,
            fetch_counts=fetch_counts,
            max_items=max_items,
            skip_count=skip_count,
            sort_properties=sort_properties,
            sort_ascending=sort_ascending,
            property_filter=property_filter,
            resolve_inherited_access=resolve_inherited_access,
        )
    ).parsed
