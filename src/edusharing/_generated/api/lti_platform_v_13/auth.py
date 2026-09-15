from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    scope: str,
    response_type: str,
    client_id: str | Unset = UNSET,
    login_hint: str,
    state: str,
    response_mode: str,
    nonce: str,
    prompt: str,
    lti_message_hint: str | Unset = UNSET,
    redirect_uri: str,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["scope"] = scope

    params["response_type"] = response_type

    params["client_id"] = client_id

    params["login_hint"] = login_hint

    params["state"] = state

    params["response_mode"] = response_mode

    params["nonce"] = nonce

    params["prompt"] = prompt

    params["lti_message_hint"] = lti_message_hint

    params["redirect_uri"] = redirect_uri

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/ltiplatform/v13/auth",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> str | None:
    if response.status_code == 200:
        response_200 = response.text
        return response_200

    if response.status_code == 400:
        response_400 = response.text
        return response_400

    if response.status_code == 401:
        response_401 = response.text
        return response_401

    if response.status_code == 403:
        response_403 = response.text
        return response_403

    if response.status_code == 404:
        response_404 = response.text
        return response_404

    if response.status_code == 500:
        response_500 = response.text
        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[str]:
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
    response_type: str,
    client_id: str | Unset = UNSET,
    login_hint: str,
    state: str,
    response_mode: str,
    nonce: str,
    prompt: str,
    lti_message_hint: str | Unset = UNSET,
    redirect_uri: str,
) -> Response[str]:
    """LTI Platform oidc endpoint. responds to a login authentication request

    Args:
        scope (str):
        response_type (str):
        client_id (str | Unset):
        login_hint (str):
        state (str):
        response_mode (str):
        nonce (str):
        prompt (str):
        lti_message_hint (str | Unset):
        redirect_uri (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[str]
    """

    kwargs = _get_kwargs(
        scope=scope,
        response_type=response_type,
        client_id=client_id,
        login_hint=login_hint,
        state=state,
        response_mode=response_mode,
        nonce=nonce,
        prompt=prompt,
        lti_message_hint=lti_message_hint,
        redirect_uri=redirect_uri,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    scope: str,
    response_type: str,
    client_id: str | Unset = UNSET,
    login_hint: str,
    state: str,
    response_mode: str,
    nonce: str,
    prompt: str,
    lti_message_hint: str | Unset = UNSET,
    redirect_uri: str,
) -> str | None:
    """LTI Platform oidc endpoint. responds to a login authentication request

    Args:
        scope (str):
        response_type (str):
        client_id (str | Unset):
        login_hint (str):
        state (str):
        response_mode (str):
        nonce (str):
        prompt (str):
        lti_message_hint (str | Unset):
        redirect_uri (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        str
    """

    return sync_detailed(
        client=client,
        scope=scope,
        response_type=response_type,
        client_id=client_id,
        login_hint=login_hint,
        state=state,
        response_mode=response_mode,
        nonce=nonce,
        prompt=prompt,
        lti_message_hint=lti_message_hint,
        redirect_uri=redirect_uri,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    scope: str,
    response_type: str,
    client_id: str | Unset = UNSET,
    login_hint: str,
    state: str,
    response_mode: str,
    nonce: str,
    prompt: str,
    lti_message_hint: str | Unset = UNSET,
    redirect_uri: str,
) -> Response[str]:
    """LTI Platform oidc endpoint. responds to a login authentication request

    Args:
        scope (str):
        response_type (str):
        client_id (str | Unset):
        login_hint (str):
        state (str):
        response_mode (str):
        nonce (str):
        prompt (str):
        lti_message_hint (str | Unset):
        redirect_uri (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[str]
    """

    kwargs = _get_kwargs(
        scope=scope,
        response_type=response_type,
        client_id=client_id,
        login_hint=login_hint,
        state=state,
        response_mode=response_mode,
        nonce=nonce,
        prompt=prompt,
        lti_message_hint=lti_message_hint,
        redirect_uri=redirect_uri,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    scope: str,
    response_type: str,
    client_id: str | Unset = UNSET,
    login_hint: str,
    state: str,
    response_mode: str,
    nonce: str,
    prompt: str,
    lti_message_hint: str | Unset = UNSET,
    redirect_uri: str,
) -> str | None:
    """LTI Platform oidc endpoint. responds to a login authentication request

    Args:
        scope (str):
        response_type (str):
        client_id (str | Unset):
        login_hint (str):
        state (str):
        response_mode (str):
        nonce (str):
        prompt (str):
        lti_message_hint (str | Unset):
        redirect_uri (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        str
    """

    return (
        await asyncio_detailed(
            client=client,
            scope=scope,
            response_type=response_type,
            client_id=client_id,
            login_hint=login_hint,
            state=state,
            response_mode=response_mode,
            nonce=nonce,
            prompt=prompt,
            lti_message_hint=lti_message_hint,
            redirect_uri=redirect_uri,
        )
    ).parsed
