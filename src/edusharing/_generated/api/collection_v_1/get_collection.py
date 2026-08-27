from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.collection_entry import CollectionEntry
from ...models.error_response import ErrorResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    repository: str,
    collection_id: str,
    *,
    track: bool | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["track"] = track

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/collection/v1/collections/{repository}/{collection_id}".format(
            repository=quote(str(repository), safe=""),
            collection_id=quote(str(collection_id), safe=""),
        ),
        "params": params,
    }

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
    collection_id: str,
    *,
    client: AuthenticatedClient | Client,
    track: bool | Unset = UNSET,
) -> Response[CollectionEntry | ErrorResponse]:
    """Get a collection.

     Get a collection.

    Args:
        repository (str):
        collection_id (str):
        track (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CollectionEntry | ErrorResponse]
    """

    kwargs = _get_kwargs(
        repository=repository,
        collection_id=collection_id,
        track=track,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repository: str,
    collection_id: str,
    *,
    client: AuthenticatedClient | Client,
    track: bool | Unset = UNSET,
) -> CollectionEntry | ErrorResponse | None:
    """Get a collection.

     Get a collection.

    Args:
        repository (str):
        collection_id (str):
        track (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CollectionEntry | ErrorResponse
    """

    return sync_detailed(
        repository=repository,
        collection_id=collection_id,
        client=client,
        track=track,
    ).parsed


async def asyncio_detailed(
    repository: str,
    collection_id: str,
    *,
    client: AuthenticatedClient | Client,
    track: bool | Unset = UNSET,
) -> Response[CollectionEntry | ErrorResponse]:
    """Get a collection.

     Get a collection.

    Args:
        repository (str):
        collection_id (str):
        track (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CollectionEntry | ErrorResponse]
    """

    kwargs = _get_kwargs(
        repository=repository,
        collection_id=collection_id,
        track=track,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    collection_id: str,
    *,
    client: AuthenticatedClient | Client,
    track: bool | Unset = UNSET,
) -> CollectionEntry | ErrorResponse | None:
    """Get a collection.

     Get a collection.

    Args:
        repository (str):
        collection_id (str):
        track (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CollectionEntry | ErrorResponse
    """

    return (
        await asyncio_detailed(
            repository=repository,
            collection_id=collection_id,
            client=client,
            track=track,
        )
    ).parsed
