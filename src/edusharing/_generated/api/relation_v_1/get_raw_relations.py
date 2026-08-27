from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.relation_data import RelationData
from ...types import Response


def _get_kwargs(
    repository: str,
    node: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/relation/v1/{repository}/{node}/raw".format(
            repository=quote(str(repository), safe=""),
            node=quote(str(node), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | list[RelationData] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = RelationData.from_dict(response_200_item_data)

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
) -> Response[ErrorResponse | list[RelationData]]:
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
) -> Response[ErrorResponse | list[RelationData]]:
    """get all relation of the node without resolving node details

     Returns all relations of the node.

    Args:
        repository (str):
        node (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | list[RelationData]]
    """

    kwargs = _get_kwargs(
        repository=repository,
        node=node,
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
) -> ErrorResponse | list[RelationData] | None:
    """get all relation of the node without resolving node details

     Returns all relations of the node.

    Args:
        repository (str):
        node (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | list[RelationData]
    """

    return sync_detailed(
        repository=repository,
        node=node,
        client=client,
    ).parsed


async def asyncio_detailed(
    repository: str,
    node: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[ErrorResponse | list[RelationData]]:
    """get all relation of the node without resolving node details

     Returns all relations of the node.

    Args:
        repository (str):
        node (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | list[RelationData]]
    """

    kwargs = _get_kwargs(
        repository=repository,
        node=node,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    node: str,
    *,
    client: AuthenticatedClient | Client,
) -> ErrorResponse | list[RelationData] | None:
    """get all relation of the node without resolving node details

     Returns all relations of the node.

    Args:
        repository (str):
        node (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | list[RelationData]
    """

    return (
        await asyncio_detailed(
            repository=repository,
            node=node,
            client=client,
        )
    ).parsed
