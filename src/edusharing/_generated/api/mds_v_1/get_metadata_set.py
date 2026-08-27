from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.mds import Mds
from ...types import Response


def _get_kwargs(
    repository: str,
    metadataset: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/mds/v1/metadatasets/{repository}/{metadataset}".format(
            repository=quote(str(repository), safe=""),
            metadataset=quote(str(metadataset), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | Mds | None:
    if response.status_code == 200:
        response_200 = Mds.from_dict(response.json())

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
) -> Response[ErrorResponse | Mds]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    repository: str,
    metadataset: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[ErrorResponse | Mds]:
    """Get metadata set new.

     Get metadata set new.

    Args:
        repository (str):
        metadataset (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | Mds]
    """

    kwargs = _get_kwargs(
        repository=repository,
        metadataset=metadataset,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repository: str,
    metadataset: str,
    *,
    client: AuthenticatedClient | Client,
) -> ErrorResponse | Mds | None:
    """Get metadata set new.

     Get metadata set new.

    Args:
        repository (str):
        metadataset (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | Mds
    """

    return sync_detailed(
        repository=repository,
        metadataset=metadataset,
        client=client,
    ).parsed


async def asyncio_detailed(
    repository: str,
    metadataset: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[ErrorResponse | Mds]:
    """Get metadata set new.

     Get metadata set new.

    Args:
        repository (str):
        metadataset (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | Mds]
    """

    kwargs = _get_kwargs(
        repository=repository,
        metadataset=metadataset,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    metadataset: str,
    *,
    client: AuthenticatedClient | Client,
) -> ErrorResponse | Mds | None:
    """Get metadata set new.

     Get metadata set new.

    Args:
        repository (str):
        metadataset (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | Mds
    """

    return (
        await asyncio_detailed(
            repository=repository,
            metadataset=metadataset,
            client=client,
        )
    ).parsed
