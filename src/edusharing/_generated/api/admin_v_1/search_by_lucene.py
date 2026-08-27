from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.search_by_lucene_store import SearchByLuceneStore
from ...models.search_result import SearchResult
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    query: str | Unset = '@cm\\:name:\\"*\\"',
    max_items: int | Unset = 10,
    skip_count: int | Unset = 0,
    sort_properties: list[str] | Unset = UNSET,
    sort_ascending: list[bool] | Unset = UNSET,
    property_filter: list[str] | Unset = UNSET,
    store: SearchByLuceneStore | Unset = UNSET,
    authority_scope: list[str] | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["query"] = query

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

    json_store: str | Unset = UNSET
    if not isinstance(store, Unset):
        json_store = store.value

    params["store"] = json_store

    json_authority_scope: list[str] | Unset = UNSET
    if not isinstance(authority_scope, Unset):
        json_authority_scope = authority_scope

    params["authorityScope"] = json_authority_scope

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/admin/v1/lucene",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | SearchResult | None:
    if response.status_code == 200:
        response_200 = SearchResult.from_dict(response.json())

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
) -> Response[ErrorResponse | SearchResult]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    query: str | Unset = '@cm\\:name:\\"*\\"',
    max_items: int | Unset = 10,
    skip_count: int | Unset = 0,
    sort_properties: list[str] | Unset = UNSET,
    sort_ascending: list[bool] | Unset = UNSET,
    property_filter: list[str] | Unset = UNSET,
    store: SearchByLuceneStore | Unset = UNSET,
    authority_scope: list[str] | Unset = UNSET,
) -> Response[ErrorResponse | SearchResult]:
    r"""Search for custom lucene query

     e.g. @cm\:name:\"*\"

    Args:
        query (str | Unset):  Default: '@cm\\:name:\\"*\\"'.
        max_items (int | Unset):  Default: 10.
        skip_count (int | Unset):  Default: 0.
        sort_properties (list[str] | Unset):
        sort_ascending (list[bool] | Unset):
        property_filter (list[str] | Unset):
        store (SearchByLuceneStore | Unset):
        authority_scope (list[str] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | SearchResult]
    """

    kwargs = _get_kwargs(
        query=query,
        max_items=max_items,
        skip_count=skip_count,
        sort_properties=sort_properties,
        sort_ascending=sort_ascending,
        property_filter=property_filter,
        store=store,
        authority_scope=authority_scope,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    query: str | Unset = '@cm\\:name:\\"*\\"',
    max_items: int | Unset = 10,
    skip_count: int | Unset = 0,
    sort_properties: list[str] | Unset = UNSET,
    sort_ascending: list[bool] | Unset = UNSET,
    property_filter: list[str] | Unset = UNSET,
    store: SearchByLuceneStore | Unset = UNSET,
    authority_scope: list[str] | Unset = UNSET,
) -> ErrorResponse | SearchResult | None:
    r"""Search for custom lucene query

     e.g. @cm\:name:\"*\"

    Args:
        query (str | Unset):  Default: '@cm\\:name:\\"*\\"'.
        max_items (int | Unset):  Default: 10.
        skip_count (int | Unset):  Default: 0.
        sort_properties (list[str] | Unset):
        sort_ascending (list[bool] | Unset):
        property_filter (list[str] | Unset):
        store (SearchByLuceneStore | Unset):
        authority_scope (list[str] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | SearchResult
    """

    return sync_detailed(
        client=client,
        query=query,
        max_items=max_items,
        skip_count=skip_count,
        sort_properties=sort_properties,
        sort_ascending=sort_ascending,
        property_filter=property_filter,
        store=store,
        authority_scope=authority_scope,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    query: str | Unset = '@cm\\:name:\\"*\\"',
    max_items: int | Unset = 10,
    skip_count: int | Unset = 0,
    sort_properties: list[str] | Unset = UNSET,
    sort_ascending: list[bool] | Unset = UNSET,
    property_filter: list[str] | Unset = UNSET,
    store: SearchByLuceneStore | Unset = UNSET,
    authority_scope: list[str] | Unset = UNSET,
) -> Response[ErrorResponse | SearchResult]:
    r"""Search for custom lucene query

     e.g. @cm\:name:\"*\"

    Args:
        query (str | Unset):  Default: '@cm\\:name:\\"*\\"'.
        max_items (int | Unset):  Default: 10.
        skip_count (int | Unset):  Default: 0.
        sort_properties (list[str] | Unset):
        sort_ascending (list[bool] | Unset):
        property_filter (list[str] | Unset):
        store (SearchByLuceneStore | Unset):
        authority_scope (list[str] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | SearchResult]
    """

    kwargs = _get_kwargs(
        query=query,
        max_items=max_items,
        skip_count=skip_count,
        sort_properties=sort_properties,
        sort_ascending=sort_ascending,
        property_filter=property_filter,
        store=store,
        authority_scope=authority_scope,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    query: str | Unset = '@cm\\:name:\\"*\\"',
    max_items: int | Unset = 10,
    skip_count: int | Unset = 0,
    sort_properties: list[str] | Unset = UNSET,
    sort_ascending: list[bool] | Unset = UNSET,
    property_filter: list[str] | Unset = UNSET,
    store: SearchByLuceneStore | Unset = UNSET,
    authority_scope: list[str] | Unset = UNSET,
) -> ErrorResponse | SearchResult | None:
    r"""Search for custom lucene query

     e.g. @cm\:name:\"*\"

    Args:
        query (str | Unset):  Default: '@cm\\:name:\\"*\\"'.
        max_items (int | Unset):  Default: 10.
        skip_count (int | Unset):  Default: 0.
        sort_properties (list[str] | Unset):
        sort_ascending (list[bool] | Unset):
        property_filter (list[str] | Unset):
        store (SearchByLuceneStore | Unset):
        authority_scope (list[str] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | SearchResult
    """

    return (
        await asyncio_detailed(
            client=client,
            query=query,
            max_items=max_items,
            skip_count=skip_count,
            sort_properties=sort_properties,
            sort_ascending=sort_ascending,
            property_filter=property_filter,
            store=store,
            authority_scope=authority_scope,
        )
    ).parsed
