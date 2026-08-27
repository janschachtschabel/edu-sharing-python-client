from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.abstract_entries import AbstractEntries
from ...models.error_response import ErrorResponse
from ...models.get_collections_proposals_status import GetCollectionsProposalsStatus
from ...types import UNSET, Response


def _get_kwargs(
    repository: str,
    collection: str,
    *,
    status: GetCollectionsProposalsStatus,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_status = status.value
    params["status"] = json_status

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/collection/v1/collections/{repository}/{collection}/children/proposals".format(
            repository=quote(str(repository), safe=""),
            collection=quote(str(collection), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> AbstractEntries | ErrorResponse | None:
    if response.status_code == 200:
        response_200 = AbstractEntries.from_dict(response.json())

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
) -> Response[AbstractEntries | ErrorResponse]:
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
    status: GetCollectionsProposalsStatus,
) -> Response[AbstractEntries | ErrorResponse]:
    """Get proposed objects for collection (requires edit permissions on collection).

    Args:
        repository (str):
        collection (str):
        status (GetCollectionsProposalsStatus):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AbstractEntries | ErrorResponse]
    """

    kwargs = _get_kwargs(
        repository=repository,
        collection=collection,
        status=status,
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
    status: GetCollectionsProposalsStatus,
) -> AbstractEntries | ErrorResponse | None:
    """Get proposed objects for collection (requires edit permissions on collection).

    Args:
        repository (str):
        collection (str):
        status (GetCollectionsProposalsStatus):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AbstractEntries | ErrorResponse
    """

    return sync_detailed(
        repository=repository,
        collection=collection,
        client=client,
        status=status,
    ).parsed


async def asyncio_detailed(
    repository: str,
    collection: str,
    *,
    client: AuthenticatedClient | Client,
    status: GetCollectionsProposalsStatus,
) -> Response[AbstractEntries | ErrorResponse]:
    """Get proposed objects for collection (requires edit permissions on collection).

    Args:
        repository (str):
        collection (str):
        status (GetCollectionsProposalsStatus):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AbstractEntries | ErrorResponse]
    """

    kwargs = _get_kwargs(
        repository=repository,
        collection=collection,
        status=status,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    collection: str,
    *,
    client: AuthenticatedClient | Client,
    status: GetCollectionsProposalsStatus,
) -> AbstractEntries | ErrorResponse | None:
    """Get proposed objects for collection (requires edit permissions on collection).

    Args:
        repository (str):
        collection (str):
        status (GetCollectionsProposalsStatus):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AbstractEntries | ErrorResponse
    """

    return (
        await asyncio_detailed(
            repository=repository,
            collection=collection,
            client=client,
            status=status,
        )
    ).parsed
