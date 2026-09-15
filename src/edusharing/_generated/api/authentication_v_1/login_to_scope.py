from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.login_credentials import LoginCredentials
from ...models.scope_login import ScopeLogin
from ...types import Response


def _get_kwargs(
    *,
    body: LoginCredentials,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/authentication/v1/loginToScope",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ScopeLogin | None:
    if response.status_code == 200:
        response_200 = ScopeLogin.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ScopeLogin]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: LoginCredentials,
) -> Response[ScopeLogin]:
    """Validates the Basic Auth Credentials and check if the session is a logged in user

     Use the Basic auth header field to transfer the credentials

    Args:
        body (LoginCredentials):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ScopeLogin]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: LoginCredentials,
) -> ScopeLogin | None:
    """Validates the Basic Auth Credentials and check if the session is a logged in user

     Use the Basic auth header field to transfer the credentials

    Args:
        body (LoginCredentials):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ScopeLogin
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: LoginCredentials,
) -> Response[ScopeLogin]:
    """Validates the Basic Auth Credentials and check if the session is a logged in user

     Use the Basic auth header field to transfer the credentials

    Args:
        body (LoginCredentials):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ScopeLogin]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: LoginCredentials,
) -> ScopeLogin | None:
    """Validates the Basic Auth Credentials and check if the session is a logged in user

     Use the Basic auth header field to transfer the credentials

    Args:
        body (LoginCredentials):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ScopeLogin
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
