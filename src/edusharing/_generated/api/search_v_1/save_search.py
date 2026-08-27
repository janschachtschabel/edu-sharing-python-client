from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.mds_query_criteria import MdsQueryCriteria
from ...models.node_entry import NodeEntry
from ...types import UNSET, Response, Unset


def _get_kwargs(
    repository: str,
    metadataset: str,
    query: str,
    *,
    body: list[MdsQueryCriteria],
    name: str,
    replace: bool | Unset = False,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["name"] = name

    params["replace"] = replace

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/search/v1/queries/{repository}/{metadataset}/{query}/save".format(
            repository=quote(str(repository), safe=""),
            metadataset=quote(str(metadataset), safe=""),
            query=quote(str(query), safe=""),
        ),
        "params": params,
    }

    _kwargs["json"] = []
    for body_item_data in body:
        body_item = body_item_data.to_dict()
        _kwargs["json"].append(body_item)

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | NodeEntry | None:
    if response.status_code == 200:
        response_200 = NodeEntry.from_dict(response.json())

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
) -> Response[ErrorResponse | NodeEntry]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    repository: str,
    metadataset: str,
    query: str,
    *,
    client: AuthenticatedClient | Client,
    body: list[MdsQueryCriteria],
    name: str,
    replace: bool | Unset = False,
) -> Response[ErrorResponse | NodeEntry]:
    """Save a search query.

     Save a search query.

    Args:
        repository (str):
        metadataset (str):
        query (str):
        name (str):
        replace (bool | Unset):  Default: False.
        body (list[MdsQueryCriteria]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | NodeEntry]
    """

    kwargs = _get_kwargs(
        repository=repository,
        metadataset=metadataset,
        query=query,
        body=body,
        name=name,
        replace=replace,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repository: str,
    metadataset: str,
    query: str,
    *,
    client: AuthenticatedClient | Client,
    body: list[MdsQueryCriteria],
    name: str,
    replace: bool | Unset = False,
) -> ErrorResponse | NodeEntry | None:
    """Save a search query.

     Save a search query.

    Args:
        repository (str):
        metadataset (str):
        query (str):
        name (str):
        replace (bool | Unset):  Default: False.
        body (list[MdsQueryCriteria]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | NodeEntry
    """

    return sync_detailed(
        repository=repository,
        metadataset=metadataset,
        query=query,
        client=client,
        body=body,
        name=name,
        replace=replace,
    ).parsed


async def asyncio_detailed(
    repository: str,
    metadataset: str,
    query: str,
    *,
    client: AuthenticatedClient | Client,
    body: list[MdsQueryCriteria],
    name: str,
    replace: bool | Unset = False,
) -> Response[ErrorResponse | NodeEntry]:
    """Save a search query.

     Save a search query.

    Args:
        repository (str):
        metadataset (str):
        query (str):
        name (str):
        replace (bool | Unset):  Default: False.
        body (list[MdsQueryCriteria]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | NodeEntry]
    """

    kwargs = _get_kwargs(
        repository=repository,
        metadataset=metadataset,
        query=query,
        body=body,
        name=name,
        replace=replace,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    metadataset: str,
    query: str,
    *,
    client: AuthenticatedClient | Client,
    body: list[MdsQueryCriteria],
    name: str,
    replace: bool | Unset = False,
) -> ErrorResponse | NodeEntry | None:
    """Save a search query.

     Save a search query.

    Args:
        repository (str):
        metadataset (str):
        query (str):
        name (str):
        replace (bool | Unset):  Default: False.
        body (list[MdsQueryCriteria]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | NodeEntry
    """

    return (
        await asyncio_detailed(
            repository=repository,
            metadataset=metadataset,
            query=query,
            client=client,
            body=body,
            name=name,
            replace=replace,
        )
    ).parsed
