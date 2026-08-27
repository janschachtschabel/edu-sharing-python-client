from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.node_entry import NodeEntry
from ...types import Response


def _get_kwargs(
    repository: str,
    node: str,
    from_: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/node/v1/nodes/{repository}/{node}/metadata/copy/{from_}".format(
            repository=quote(str(repository), safe=""),
            node=quote(str(node), safe=""),
            from_=quote(str(from_), safe=""),
        ),
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
    node: str,
    from_: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[ErrorResponse | NodeEntry]:
    """Copy metadata from another node.

     Copies all common metadata from one note to another. Current user needs write access to the target
    node and read access to the source node.

    Args:
        repository (str):
        node (str):
        from_ (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | NodeEntry]
    """

    kwargs = _get_kwargs(
        repository=repository,
        node=node,
        from_=from_,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repository: str,
    node: str,
    from_: str,
    *,
    client: AuthenticatedClient | Client,
) -> ErrorResponse | NodeEntry | None:
    """Copy metadata from another node.

     Copies all common metadata from one note to another. Current user needs write access to the target
    node and read access to the source node.

    Args:
        repository (str):
        node (str):
        from_ (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | NodeEntry
    """

    return sync_detailed(
        repository=repository,
        node=node,
        from_=from_,
        client=client,
    ).parsed


async def asyncio_detailed(
    repository: str,
    node: str,
    from_: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[ErrorResponse | NodeEntry]:
    """Copy metadata from another node.

     Copies all common metadata from one note to another. Current user needs write access to the target
    node and read access to the source node.

    Args:
        repository (str):
        node (str):
        from_ (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | NodeEntry]
    """

    kwargs = _get_kwargs(
        repository=repository,
        node=node,
        from_=from_,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    node: str,
    from_: str,
    *,
    client: AuthenticatedClient | Client,
) -> ErrorResponse | NodeEntry | None:
    """Copy metadata from another node.

     Copies all common metadata from one note to another. Current user needs write access to the target
    node and read access to the source node.

    Args:
        repository (str):
        node (str):
        from_ (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | NodeEntry
    """

    return (
        await asyncio_detailed(
            repository=repository,
            node=node,
            from_=from_,
            client=client,
        )
    ).parsed
