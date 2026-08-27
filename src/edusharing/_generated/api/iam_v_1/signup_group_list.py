from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.user import User
from ...types import Response


def _get_kwargs(
    repository: str,
    group: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/iam/v1/groups/{repository}/{group}/signup/list".format(
            repository=quote(str(repository), safe=""),
            group=quote(str(group), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | list[User] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = User.from_dict(response_200_item_data)

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
) -> Response[ErrorResponse | list[User]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    repository: str,
    group: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[ErrorResponse | list[User]]:
    """list pending users that want to join this group

     Requires admin rights or org administrator on this group

    Args:
        repository (str):
        group (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | list[User]]
    """

    kwargs = _get_kwargs(
        repository=repository,
        group=group,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repository: str,
    group: str,
    *,
    client: AuthenticatedClient | Client,
) -> ErrorResponse | list[User] | None:
    """list pending users that want to join this group

     Requires admin rights or org administrator on this group

    Args:
        repository (str):
        group (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | list[User]
    """

    return sync_detailed(
        repository=repository,
        group=group,
        client=client,
    ).parsed


async def asyncio_detailed(
    repository: str,
    group: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[ErrorResponse | list[User]]:
    """list pending users that want to join this group

     Requires admin rights or org administrator on this group

    Args:
        repository (str):
        group (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | list[User]]
    """

    kwargs = _get_kwargs(
        repository=repository,
        group=group,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    group: str,
    *,
    client: AuthenticatedClient | Client,
) -> ErrorResponse | list[User] | None:
    """list pending users that want to join this group

     Requires admin rights or org administrator on this group

    Args:
        repository (str):
        group (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | list[User]
    """

    return (
        await asyncio_detailed(
            repository=repository,
            group=group,
            client=client,
        )
    ).parsed
