from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.sharing_info import SharingInfo
from ...types import UNSET, Response, Unset


def _get_kwargs(
    repository: str,
    node: str,
    share: str,
    *,
    password: str | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["password"] = password

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/sharing/v1/sharing/{repository}/{node}/{share}".format(
            repository=quote(str(repository), safe=""),
            node=quote(str(node), safe=""),
            share=quote(str(share), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | SharingInfo | None:
    if response.status_code == 200:
        response_200 = SharingInfo.from_dict(response.json())

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
) -> Response[ErrorResponse | SharingInfo]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    repository: str,
    node: str,
    share: str,
    *,
    client: AuthenticatedClient | Client,
    password: str | Unset = UNSET,
) -> Response[ErrorResponse | SharingInfo]:
    """Get general info of a share.

    Args:
        repository (str):
        node (str):
        share (str):
        password (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | SharingInfo]
    """

    kwargs = _get_kwargs(
        repository=repository,
        node=node,
        share=share,
        password=password,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repository: str,
    node: str,
    share: str,
    *,
    client: AuthenticatedClient | Client,
    password: str | Unset = UNSET,
) -> ErrorResponse | SharingInfo | None:
    """Get general info of a share.

    Args:
        repository (str):
        node (str):
        share (str):
        password (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | SharingInfo
    """

    return sync_detailed(
        repository=repository,
        node=node,
        share=share,
        client=client,
        password=password,
    ).parsed


async def asyncio_detailed(
    repository: str,
    node: str,
    share: str,
    *,
    client: AuthenticatedClient | Client,
    password: str | Unset = UNSET,
) -> Response[ErrorResponse | SharingInfo]:
    """Get general info of a share.

    Args:
        repository (str):
        node (str):
        share (str):
        password (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | SharingInfo]
    """

    kwargs = _get_kwargs(
        repository=repository,
        node=node,
        share=share,
        password=password,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    node: str,
    share: str,
    *,
    client: AuthenticatedClient | Client,
    password: str | Unset = UNSET,
) -> ErrorResponse | SharingInfo | None:
    """Get general info of a share.

    Args:
        repository (str):
        node (str):
        share (str):
        password (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | SharingInfo
    """

    return (
        await asyncio_detailed(
            repository=repository,
            node=node,
            share=share,
            client=client,
            password=password,
        )
    ).parsed
