from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.collection_entry import CollectionEntry
from ...models.error_response import ErrorResponse
from ...models.node import Node
from ...types import Response


def _get_kwargs(
    repository: str,
    collection: str,
    *,
    body: Node,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/collection/v1/collections/{repository}/{collection}/children".format(
            repository=quote(str(repository), safe=""),
            collection=quote(str(collection), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> CollectionEntry | ErrorResponse | None:
    if response.status_code == 200:
        response_200 = CollectionEntry.from_dict(response.json())

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
) -> Response[CollectionEntry | ErrorResponse]:
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
    body: Node,
) -> Response[CollectionEntry | ErrorResponse]:
    """Create a new collection.

     Create a new collection.

    Args:
        repository (str):
        collection (str):
        body (Node):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CollectionEntry | ErrorResponse]
    """

    kwargs = _get_kwargs(
        repository=repository,
        collection=collection,
        body=body,
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
    body: Node,
) -> CollectionEntry | ErrorResponse | None:
    """Create a new collection.

     Create a new collection.

    Args:
        repository (str):
        collection (str):
        body (Node):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CollectionEntry | ErrorResponse
    """

    return sync_detailed(
        repository=repository,
        collection=collection,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    repository: str,
    collection: str,
    *,
    client: AuthenticatedClient | Client,
    body: Node,
) -> Response[CollectionEntry | ErrorResponse]:
    """Create a new collection.

     Create a new collection.

    Args:
        repository (str):
        collection (str):
        body (Node):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CollectionEntry | ErrorResponse]
    """

    kwargs = _get_kwargs(
        repository=repository,
        collection=collection,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    collection: str,
    *,
    client: AuthenticatedClient | Client,
    body: Node,
) -> CollectionEntry | ErrorResponse | None:
    """Create a new collection.

     Create a new collection.

    Args:
        repository (str):
        collection (str):
        body (Node):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CollectionEntry | ErrorResponse
    """

    return (
        await asyncio_detailed(
            repository=repository,
            collection=collection,
            client=client,
            body=body,
        )
    ).parsed
