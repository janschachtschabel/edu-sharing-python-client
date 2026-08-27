from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.node_entry import NodeEntry
from ...types import UNSET, Response, Unset


def _get_kwargs(
    repository: str,
    collection: str,
    node: str,
    *,
    source_repo: str | Unset = UNSET,
    allow_duplicate: bool | Unset = False,
    as_proposal: bool | Unset = False,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["sourceRepo"] = source_repo

    params["allowDuplicate"] = allow_duplicate

    params["asProposal"] = as_proposal

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/collection/v1/collections/{repository}/{collection}/references/{node}".format(
            repository=quote(str(repository), safe=""),
            collection=quote(str(collection), safe=""),
            node=quote(str(node), safe=""),
        ),
        "params": params,
    }

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

    if response.status_code == 409:
        response_409 = ErrorResponse.from_dict(response.json())

        return response_409

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
    collection: str,
    node: str,
    *,
    client: AuthenticatedClient | Client,
    source_repo: str | Unset = UNSET,
    allow_duplicate: bool | Unset = False,
    as_proposal: bool | Unset = False,
) -> Response[ErrorResponse | NodeEntry]:
    """Add a node to a collection.

     Add a node to a collection.

    Args:
        repository (str):
        collection (str):
        node (str):
        source_repo (str | Unset):
        allow_duplicate (bool | Unset):  Default: False.
        as_proposal (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | NodeEntry]
    """

    kwargs = _get_kwargs(
        repository=repository,
        collection=collection,
        node=node,
        source_repo=source_repo,
        allow_duplicate=allow_duplicate,
        as_proposal=as_proposal,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repository: str,
    collection: str,
    node: str,
    *,
    client: AuthenticatedClient | Client,
    source_repo: str | Unset = UNSET,
    allow_duplicate: bool | Unset = False,
    as_proposal: bool | Unset = False,
) -> ErrorResponse | NodeEntry | None:
    """Add a node to a collection.

     Add a node to a collection.

    Args:
        repository (str):
        collection (str):
        node (str):
        source_repo (str | Unset):
        allow_duplicate (bool | Unset):  Default: False.
        as_proposal (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | NodeEntry
    """

    return sync_detailed(
        repository=repository,
        collection=collection,
        node=node,
        client=client,
        source_repo=source_repo,
        allow_duplicate=allow_duplicate,
        as_proposal=as_proposal,
    ).parsed


async def asyncio_detailed(
    repository: str,
    collection: str,
    node: str,
    *,
    client: AuthenticatedClient | Client,
    source_repo: str | Unset = UNSET,
    allow_duplicate: bool | Unset = False,
    as_proposal: bool | Unset = False,
) -> Response[ErrorResponse | NodeEntry]:
    """Add a node to a collection.

     Add a node to a collection.

    Args:
        repository (str):
        collection (str):
        node (str):
        source_repo (str | Unset):
        allow_duplicate (bool | Unset):  Default: False.
        as_proposal (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | NodeEntry]
    """

    kwargs = _get_kwargs(
        repository=repository,
        collection=collection,
        node=node,
        source_repo=source_repo,
        allow_duplicate=allow_duplicate,
        as_proposal=as_proposal,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    collection: str,
    node: str,
    *,
    client: AuthenticatedClient | Client,
    source_repo: str | Unset = UNSET,
    allow_duplicate: bool | Unset = False,
    as_proposal: bool | Unset = False,
) -> ErrorResponse | NodeEntry | None:
    """Add a node to a collection.

     Add a node to a collection.

    Args:
        repository (str):
        collection (str):
        node (str):
        source_repo (str | Unset):
        allow_duplicate (bool | Unset):  Default: False.
        as_proposal (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | NodeEntry
    """

    return (
        await asyncio_detailed(
            repository=repository,
            collection=collection,
            node=node,
            client=client,
            source_repo=source_repo,
            allow_duplicate=allow_duplicate,
            as_proposal=as_proposal,
        )
    ).parsed
