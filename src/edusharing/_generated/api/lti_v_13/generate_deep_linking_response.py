from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.node_lti_deep_link import NodeLTIDeepLink
from ...types import UNSET, Response


def _get_kwargs(
    *,
    node_ids: list[str],
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_node_ids = node_ids

    params["nodeIds"] = json_node_ids

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/lti/v13/generateDeepLinkingResponse",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | NodeLTIDeepLink | None:
    if response.status_code == 200:
        response_200 = NodeLTIDeepLink.from_dict(response.json())

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
) -> Response[ErrorResponse | NodeLTIDeepLink]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    node_ids: list[str],
) -> Response[ErrorResponse | NodeLTIDeepLink]:
    """generate DeepLinkingResponse

    Args:
        node_ids (list[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | NodeLTIDeepLink]
    """

    kwargs = _get_kwargs(
        node_ids=node_ids,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    node_ids: list[str],
) -> ErrorResponse | NodeLTIDeepLink | None:
    """generate DeepLinkingResponse

    Args:
        node_ids (list[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | NodeLTIDeepLink
    """

    return sync_detailed(
        client=client,
        node_ids=node_ids,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    node_ids: list[str],
) -> Response[ErrorResponse | NodeLTIDeepLink]:
    """generate DeepLinkingResponse

    Args:
        node_ids (list[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | NodeLTIDeepLink]
    """

    kwargs = _get_kwargs(
        node_ids=node_ids,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    node_ids: list[str],
) -> ErrorResponse | NodeLTIDeepLink | None:
    """generate DeepLinkingResponse

    Args:
        node_ids (list[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | NodeLTIDeepLink
    """

    return (
        await asyncio_detailed(
            client=client,
            node_ids=node_ids,
        )
    ).parsed
