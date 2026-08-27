from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.group import Group
from ...types import Response


def _get_kwargs(
    repository: str,
    mediacenter: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/mediacenter/v1/mediacenter/{repository}/{mediacenter}/manages".format(
            repository=quote(str(repository), safe=""),
            mediacenter=quote(str(mediacenter), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | list[Group] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = Group.from_dict(response_200_item_data)

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
) -> Response[ErrorResponse | list[Group]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    repository: str,
    mediacenter: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[ErrorResponse | list[Group]]:
    """get groups that are managed by the given mediacenter

    Args:
        repository (str):
        mediacenter (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | list[Group]]
    """

    kwargs = _get_kwargs(
        repository=repository,
        mediacenter=mediacenter,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repository: str,
    mediacenter: str,
    *,
    client: AuthenticatedClient | Client,
) -> ErrorResponse | list[Group] | None:
    """get groups that are managed by the given mediacenter

    Args:
        repository (str):
        mediacenter (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | list[Group]
    """

    return sync_detailed(
        repository=repository,
        mediacenter=mediacenter,
        client=client,
    ).parsed


async def asyncio_detailed(
    repository: str,
    mediacenter: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[ErrorResponse | list[Group]]:
    """get groups that are managed by the given mediacenter

    Args:
        repository (str):
        mediacenter (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | list[Group]]
    """

    kwargs = _get_kwargs(
        repository=repository,
        mediacenter=mediacenter,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    mediacenter: str,
    *,
    client: AuthenticatedClient | Client,
) -> ErrorResponse | list[Group] | None:
    """get groups that are managed by the given mediacenter

    Args:
        repository (str):
        mediacenter (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | list[Group]
    """

    return (
        await asyncio_detailed(
            repository=repository,
            mediacenter=mediacenter,
            client=client,
        )
    ).parsed
