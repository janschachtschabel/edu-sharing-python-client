from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.export_by_lucene_response_200_item import ExportByLuceneResponse200Item
from ...models.export_by_lucene_store import ExportByLuceneStore
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    query: str | Unset = '@cm\\:name:\\"*\\"',
    sort_properties: list[str] | Unset = UNSET,
    sort_ascending: list[bool] | Unset = UNSET,
    properties: list[str] | Unset = UNSET,
    store: ExportByLuceneStore | Unset = UNSET,
    authority_scope: list[str] | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["query"] = query

    json_sort_properties: list[str] | Unset = UNSET
    if not isinstance(sort_properties, Unset):
        json_sort_properties = sort_properties

    params["sortProperties"] = json_sort_properties

    json_sort_ascending: list[bool] | Unset = UNSET
    if not isinstance(sort_ascending, Unset):
        json_sort_ascending = sort_ascending

    params["sortAscending"] = json_sort_ascending

    json_properties: list[str] | Unset = UNSET
    if not isinstance(properties, Unset):
        json_properties = properties

    params["properties"] = json_properties

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
        "url": "/admin/v1/lucene/export",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | list[ExportByLuceneResponse200Item] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = ExportByLuceneResponse200Item.from_dict(response_200_item_data)

            response_200.append(response_200_item)

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
) -> Response[ErrorResponse | list[ExportByLuceneResponse200Item]]:
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
    sort_properties: list[str] | Unset = UNSET,
    sort_ascending: list[bool] | Unset = UNSET,
    properties: list[str] | Unset = UNSET,
    store: ExportByLuceneStore | Unset = UNSET,
    authority_scope: list[str] | Unset = UNSET,
) -> Response[ErrorResponse | list[ExportByLuceneResponse200Item]]:
    r"""Search for custom lucene query and choose specific properties to load

     e.g. @cm\:name:\"*\"

    Args:
        query (str | Unset):  Default: '@cm\\:name:\\"*\\"'.
        sort_properties (list[str] | Unset):
        sort_ascending (list[bool] | Unset):
        properties (list[str] | Unset):
        store (ExportByLuceneStore | Unset):
        authority_scope (list[str] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | list[ExportByLuceneResponse200Item]]
    """

    kwargs = _get_kwargs(
        query=query,
        sort_properties=sort_properties,
        sort_ascending=sort_ascending,
        properties=properties,
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
    sort_properties: list[str] | Unset = UNSET,
    sort_ascending: list[bool] | Unset = UNSET,
    properties: list[str] | Unset = UNSET,
    store: ExportByLuceneStore | Unset = UNSET,
    authority_scope: list[str] | Unset = UNSET,
) -> ErrorResponse | list[ExportByLuceneResponse200Item] | None:
    r"""Search for custom lucene query and choose specific properties to load

     e.g. @cm\:name:\"*\"

    Args:
        query (str | Unset):  Default: '@cm\\:name:\\"*\\"'.
        sort_properties (list[str] | Unset):
        sort_ascending (list[bool] | Unset):
        properties (list[str] | Unset):
        store (ExportByLuceneStore | Unset):
        authority_scope (list[str] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | list[ExportByLuceneResponse200Item]
    """

    return sync_detailed(
        client=client,
        query=query,
        sort_properties=sort_properties,
        sort_ascending=sort_ascending,
        properties=properties,
        store=store,
        authority_scope=authority_scope,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    query: str | Unset = '@cm\\:name:\\"*\\"',
    sort_properties: list[str] | Unset = UNSET,
    sort_ascending: list[bool] | Unset = UNSET,
    properties: list[str] | Unset = UNSET,
    store: ExportByLuceneStore | Unset = UNSET,
    authority_scope: list[str] | Unset = UNSET,
) -> Response[ErrorResponse | list[ExportByLuceneResponse200Item]]:
    r"""Search for custom lucene query and choose specific properties to load

     e.g. @cm\:name:\"*\"

    Args:
        query (str | Unset):  Default: '@cm\\:name:\\"*\\"'.
        sort_properties (list[str] | Unset):
        sort_ascending (list[bool] | Unset):
        properties (list[str] | Unset):
        store (ExportByLuceneStore | Unset):
        authority_scope (list[str] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | list[ExportByLuceneResponse200Item]]
    """

    kwargs = _get_kwargs(
        query=query,
        sort_properties=sort_properties,
        sort_ascending=sort_ascending,
        properties=properties,
        store=store,
        authority_scope=authority_scope,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    query: str | Unset = '@cm\\:name:\\"*\\"',
    sort_properties: list[str] | Unset = UNSET,
    sort_ascending: list[bool] | Unset = UNSET,
    properties: list[str] | Unset = UNSET,
    store: ExportByLuceneStore | Unset = UNSET,
    authority_scope: list[str] | Unset = UNSET,
) -> ErrorResponse | list[ExportByLuceneResponse200Item] | None:
    r"""Search for custom lucene query and choose specific properties to load

     e.g. @cm\:name:\"*\"

    Args:
        query (str | Unset):  Default: '@cm\\:name:\\"*\\"'.
        sort_properties (list[str] | Unset):
        sort_ascending (list[bool] | Unset):
        properties (list[str] | Unset):
        store (ExportByLuceneStore | Unset):
        authority_scope (list[str] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | list[ExportByLuceneResponse200Item]
    """

    return (
        await asyncio_detailed(
            client=client,
            query=query,
            sort_properties=sort_properties,
            sort_ascending=sort_ascending,
            properties=properties,
            store=store,
            authority_scope=authority_scope,
        )
    ).parsed
