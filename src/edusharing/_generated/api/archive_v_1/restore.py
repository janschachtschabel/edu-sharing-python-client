from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.restore_results import RestoreResults
from ...types import UNSET, Response, Unset


def _get_kwargs(
    repository: str,
    *,
    archived_node_ids: list[str],
    target: str | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_archived_node_ids = archived_node_ids

    params["archivedNodeIds"] = json_archived_node_ids

    params["target"] = target

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/archive/v1/restore/{repository}".format(
            repository=quote(str(repository), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | RestoreResults | None:
    if response.status_code == 200:
        response_200 = RestoreResults.from_dict(response.json())

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
) -> Response[ErrorResponse | RestoreResults]:
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
    archived_node_ids: list[str],
    target: str | Unset = UNSET,
) -> Response[ErrorResponse | RestoreResults]:
    """restore archived nodes.

     restores archived nodes. restoreStatus can have the following values: FALLBACK_PARENT_NOT_EXISTS,
    FALLBACK_PARENT_NO_PERMISSION, DUPLICATENAME, FINE

    Args:
        repository (str):
        archived_node_ids (list[str]):
        target (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | RestoreResults]
    """

    kwargs = _get_kwargs(
        repository=repository,
        archived_node_ids=archived_node_ids,
        target=target,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repository: str,
    *,
    client: AuthenticatedClient | Client,
    archived_node_ids: list[str],
    target: str | Unset = UNSET,
) -> ErrorResponse | RestoreResults | None:
    """restore archived nodes.

     restores archived nodes. restoreStatus can have the following values: FALLBACK_PARENT_NOT_EXISTS,
    FALLBACK_PARENT_NO_PERMISSION, DUPLICATENAME, FINE

    Args:
        repository (str):
        archived_node_ids (list[str]):
        target (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | RestoreResults
    """

    return sync_detailed(
        repository=repository,
        client=client,
        archived_node_ids=archived_node_ids,
        target=target,
    ).parsed


async def asyncio_detailed(
    repository: str,
    *,
    client: AuthenticatedClient | Client,
    archived_node_ids: list[str],
    target: str | Unset = UNSET,
) -> Response[ErrorResponse | RestoreResults]:
    """restore archived nodes.

     restores archived nodes. restoreStatus can have the following values: FALLBACK_PARENT_NOT_EXISTS,
    FALLBACK_PARENT_NO_PERMISSION, DUPLICATENAME, FINE

    Args:
        repository (str):
        archived_node_ids (list[str]):
        target (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | RestoreResults]
    """

    kwargs = _get_kwargs(
        repository=repository,
        archived_node_ids=archived_node_ids,
        target=target,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    *,
    client: AuthenticatedClient | Client,
    archived_node_ids: list[str],
    target: str | Unset = UNSET,
) -> ErrorResponse | RestoreResults | None:
    """restore archived nodes.

     restores archived nodes. restoreStatus can have the following values: FALLBACK_PARENT_NOT_EXISTS,
    FALLBACK_PARENT_NO_PERMISSION, DUPLICATENAME, FINE

    Args:
        repository (str):
        archived_node_ids (list[str]):
        target (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | RestoreResults
    """

    return (
        await asyncio_detailed(
            repository=repository,
            client=client,
            archived_node_ids=archived_node_ids,
            target=target,
        )
    ).parsed
