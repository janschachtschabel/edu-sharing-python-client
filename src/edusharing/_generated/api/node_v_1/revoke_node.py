from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.node import Node
from ...models.revoke_details import RevokeDetails
from ...types import Response


def _get_kwargs(
    repository: str,
    node: str,
    *,
    body: RevokeDetails,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/node/v1/nodes/{repository}/{node}/publish/revoke".format(
            repository=quote(str(repository), safe=""),
            node=quote(str(node), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | Node | None:
    if response.status_code == 200:
        response_200 = Node.from_dict(response.json())

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
) -> Response[ErrorResponse | Node]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    repository: str,
    node: str,
    *,
    client: AuthenticatedClient | Client,
    body: RevokeDetails,
) -> Response[ErrorResponse | Node]:
    """Revoke published copy or regular node

     Revoke a previously published copy or a regular. The content of this copy will be irrevocable
    removed, only the metadata will remain

    Args:
        repository (str):
        node (str):
        body (RevokeDetails):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | Node]
    """

    kwargs = _get_kwargs(
        repository=repository,
        node=node,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repository: str,
    node: str,
    *,
    client: AuthenticatedClient | Client,
    body: RevokeDetails,
) -> ErrorResponse | Node | None:
    """Revoke published copy or regular node

     Revoke a previously published copy or a regular. The content of this copy will be irrevocable
    removed, only the metadata will remain

    Args:
        repository (str):
        node (str):
        body (RevokeDetails):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | Node
    """

    return sync_detailed(
        repository=repository,
        node=node,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    repository: str,
    node: str,
    *,
    client: AuthenticatedClient | Client,
    body: RevokeDetails,
) -> Response[ErrorResponse | Node]:
    """Revoke published copy or regular node

     Revoke a previously published copy or a regular. The content of this copy will be irrevocable
    removed, only the metadata will remain

    Args:
        repository (str):
        node (str):
        body (RevokeDetails):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | Node]
    """

    kwargs = _get_kwargs(
        repository=repository,
        node=node,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    node: str,
    *,
    client: AuthenticatedClient | Client,
    body: RevokeDetails,
) -> ErrorResponse | Node | None:
    """Revoke published copy or regular node

     Revoke a previously published copy or a regular. The content of this copy will be irrevocable
    removed, only the metadata will remain

    Args:
        repository (str):
        node (str):
        body (RevokeDetails):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | Node
    """

    return (
        await asyncio_detailed(
            repository=repository,
            node=node,
            client=client,
            body=body,
        )
    ).parsed
