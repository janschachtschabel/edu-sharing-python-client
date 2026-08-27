from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.authority_entries import AuthorityEntries
from ...models.error_response import ErrorResponse
from ...types import Response


def _get_kwargs(
    repository: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/iam/v1/authorities/{repository}/recent".format(
            repository=quote(str(repository), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> AuthorityEntries | ErrorResponse | None:
    if response.status_code == 200:
        response_200 = AuthorityEntries.from_dict(response.json())

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
) -> Response[AuthorityEntries | ErrorResponse]:
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
) -> Response[AuthorityEntries | ErrorResponse]:
    """Get recently invited authorities.

     Get the authorities the current user has recently invited.

    Args:
        repository (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AuthorityEntries | ErrorResponse]
    """

    kwargs = _get_kwargs(
        repository=repository,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repository: str,
    *,
    client: AuthenticatedClient | Client,
) -> AuthorityEntries | ErrorResponse | None:
    """Get recently invited authorities.

     Get the authorities the current user has recently invited.

    Args:
        repository (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AuthorityEntries | ErrorResponse
    """

    return sync_detailed(
        repository=repository,
        client=client,
    ).parsed


async def asyncio_detailed(
    repository: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[AuthorityEntries | ErrorResponse]:
    """Get recently invited authorities.

     Get the authorities the current user has recently invited.

    Args:
        repository (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AuthorityEntries | ErrorResponse]
    """

    kwargs = _get_kwargs(
        repository=repository,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    *,
    client: AuthenticatedClient | Client,
) -> AuthorityEntries | ErrorResponse | None:
    """Get recently invited authorities.

     Get the authorities the current user has recently invited.

    Args:
        repository (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AuthorityEntries | ErrorResponse
    """

    return (
        await asyncio_detailed(
            repository=repository,
            client=client,
        )
    ).parsed
