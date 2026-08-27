from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.node_usage import NodeUsage
from ...types import UNSET, Response, Unset


def _get_kwargs(
    repository_id: str,
    node_id: str,
    *,
    from_: int | Unset = UNSET,
    to: int | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["from"] = from_

    params["to"] = to

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/usage/v1/usages/repository/{repository_id}/{node_id}".format(
            repository_id=quote(str(repository_id), safe=""),
            node_id=quote(str(node_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | list[NodeUsage] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = NodeUsage.from_dict(response_200_item_data)

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
) -> Response[ErrorResponse | list[NodeUsage]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    repository_id: str,
    node_id: str,
    *,
    client: AuthenticatedClient | Client,
    from_: int | Unset = UNSET,
    to: int | Unset = UNSET,
) -> Response[ErrorResponse | list[NodeUsage]]:
    """
    Args:
        repository_id (str):
        node_id (str):
        from_ (int | Unset):
        to (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | list[NodeUsage]]
    """

    kwargs = _get_kwargs(
        repository_id=repository_id,
        node_id=node_id,
        from_=from_,
        to=to,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repository_id: str,
    node_id: str,
    *,
    client: AuthenticatedClient | Client,
    from_: int | Unset = UNSET,
    to: int | Unset = UNSET,
) -> ErrorResponse | list[NodeUsage] | None:
    """
    Args:
        repository_id (str):
        node_id (str):
        from_ (int | Unset):
        to (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | list[NodeUsage]
    """

    return sync_detailed(
        repository_id=repository_id,
        node_id=node_id,
        client=client,
        from_=from_,
        to=to,
    ).parsed


async def asyncio_detailed(
    repository_id: str,
    node_id: str,
    *,
    client: AuthenticatedClient | Client,
    from_: int | Unset = UNSET,
    to: int | Unset = UNSET,
) -> Response[ErrorResponse | list[NodeUsage]]:
    """
    Args:
        repository_id (str):
        node_id (str):
        from_ (int | Unset):
        to (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | list[NodeUsage]]
    """

    kwargs = _get_kwargs(
        repository_id=repository_id,
        node_id=node_id,
        from_=from_,
        to=to,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository_id: str,
    node_id: str,
    *,
    client: AuthenticatedClient | Client,
    from_: int | Unset = UNSET,
    to: int | Unset = UNSET,
) -> ErrorResponse | list[NodeUsage] | None:
    """
    Args:
        repository_id (str):
        node_id (str):
        from_ (int | Unset):
        to (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | list[NodeUsage]
    """

    return (
        await asyncio_detailed(
            repository_id=repository_id,
            node_id=node_id,
            client=client,
            from_=from_,
            to=to,
        )
    ).parsed
