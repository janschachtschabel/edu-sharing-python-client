from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.json_object import JSONObject
from ...types import UNSET, Response, Unset


def _get_kwargs(
    repository: str,
    node: str,
    *,
    version: str | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["version"] = version

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/node/v1/nodes/{repository}/{node}/lrmi".format(
            repository=quote(str(repository), safe=""),
            node=quote(str(node), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | JSONObject | None:
    if response.status_code == 200:
        response_200 = JSONObject.from_dict(response.json())

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
) -> Response[ErrorResponse | JSONObject]:
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
    version: str | Unset = UNSET,
) -> Response[ErrorResponse | JSONObject]:
    """Get lrmi data.

     Get lrmi data of node.

    Args:
        repository (str):
        node (str):
        version (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | JSONObject]
    """

    kwargs = _get_kwargs(
        repository=repository,
        node=node,
        version=version,
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
    version: str | Unset = UNSET,
) -> ErrorResponse | JSONObject | None:
    """Get lrmi data.

     Get lrmi data of node.

    Args:
        repository (str):
        node (str):
        version (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | JSONObject
    """

    return sync_detailed(
        repository=repository,
        node=node,
        client=client,
        version=version,
    ).parsed


async def asyncio_detailed(
    repository: str,
    node: str,
    *,
    client: AuthenticatedClient | Client,
    version: str | Unset = UNSET,
) -> Response[ErrorResponse | JSONObject]:
    """Get lrmi data.

     Get lrmi data of node.

    Args:
        repository (str):
        node (str):
        version (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | JSONObject]
    """

    kwargs = _get_kwargs(
        repository=repository,
        node=node,
        version=version,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    node: str,
    *,
    client: AuthenticatedClient | Client,
    version: str | Unset = UNSET,
) -> ErrorResponse | JSONObject | None:
    """Get lrmi data.

     Get lrmi data of node.

    Args:
        repository (str):
        node (str):
        version (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | JSONObject
    """

    return (
        await asyncio_detailed(
            repository=repository,
            node=node,
            client=client,
            version=version,
        )
    ).parsed
