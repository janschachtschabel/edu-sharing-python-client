from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.scope_access import ScopeAccess
from ...types import UNSET, Response


def _get_kwargs(
    *,
    scope: str,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["scope"] = scope

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/authentication/v1/hasAccessToScope",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ScopeAccess | None:
    if response.status_code == 200:
        response_200 = ScopeAccess.from_dict(response.json())

        return response_200

    if response.status_code == 500:
        response_500 = ScopeAccess.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ScopeAccess]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    scope: str,
) -> Response[ScopeAccess]:
    """Returns true if the current user has access to the given scope

    Args:
        scope (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ScopeAccess]
    """

    kwargs = _get_kwargs(
        scope=scope,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    scope: str,
) -> ScopeAccess | None:
    """Returns true if the current user has access to the given scope

    Args:
        scope (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ScopeAccess
    """

    return sync_detailed(
        client=client,
        scope=scope,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    scope: str,
) -> Response[ScopeAccess]:
    """Returns true if the current user has access to the given scope

    Args:
        scope (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ScopeAccess]
    """

    kwargs = _get_kwargs(
        scope=scope,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    scope: str,
) -> ScopeAccess | None:
    """Returns true if the current user has access to the given scope

    Args:
        scope (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ScopeAccess
    """

    return (
        await asyncio_detailed(
            client=client,
            scope=scope,
        )
    ).parsed
