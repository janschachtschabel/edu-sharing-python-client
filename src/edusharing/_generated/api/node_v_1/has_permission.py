from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...types import Response


def _get_kwargs(
    repository: str,
    node: str,
    user: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/node/v1/nodes/{repository}/{node}/permissions/{user}".format(
            repository=quote(str(repository), safe=""),
            node=quote(str(node), safe=""),
            user=quote(str(user), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | list[str] | None:
    if response.status_code == 200:
        response_200 = cast(list[str], response.json())

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
) -> Response[ErrorResponse | list[str]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    repository: str,
    node: str,
    user: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[ErrorResponse | list[str]]:
    """Which permissions has user/group for node.

     Check for actual permissions (also when user is in groups) for a specific node

    Args:
        repository (str):
        node (str):
        user (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | list[str]]
    """

    kwargs = _get_kwargs(
        repository=repository,
        node=node,
        user=user,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repository: str,
    node: str,
    user: str,
    *,
    client: AuthenticatedClient | Client,
) -> ErrorResponse | list[str] | None:
    """Which permissions has user/group for node.

     Check for actual permissions (also when user is in groups) for a specific node

    Args:
        repository (str):
        node (str):
        user (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | list[str]
    """

    return sync_detailed(
        repository=repository,
        node=node,
        user=user,
        client=client,
    ).parsed


async def asyncio_detailed(
    repository: str,
    node: str,
    user: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[ErrorResponse | list[str]]:
    """Which permissions has user/group for node.

     Check for actual permissions (also when user is in groups) for a specific node

    Args:
        repository (str):
        node (str):
        user (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | list[str]]
    """

    kwargs = _get_kwargs(
        repository=repository,
        node=node,
        user=user,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    node: str,
    user: str,
    *,
    client: AuthenticatedClient | Client,
) -> ErrorResponse | list[str] | None:
    """Which permissions has user/group for node.

     Check for actual permissions (also when user is in groups) for a specific node

    Args:
        repository (str):
        node (str):
        user (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | list[str]
    """

    return (
        await asyncio_detailed(
            repository=repository,
            node=node,
            user=user,
            client=client,
        )
    ).parsed
