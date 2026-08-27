from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    app_id: str,
    parent_id: str,
    node_id: str | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["appId"] = app_id

    params["parentId"] = parent_id

    params["nodeId"] = node_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/ltiplatform/v13/generateLoginInitiationForm",
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
    app_id: str,
    parent_id: str,
    node_id: str | Unset = UNSET,
) -> Response[str]:
    """generate a form used for Initiating Login from a Third Party. Use thes endpoint when starting a lti
    deeplink flow.

    Args:
        app_id (str):
        parent_id (str):
        node_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[str]
    """

    kwargs = _get_kwargs(
        app_id=app_id,
        parent_id=parent_id,
        node_id=node_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    app_id: str,
    parent_id: str,
    node_id: str | Unset = UNSET,
) -> str | None:
    """generate a form used for Initiating Login from a Third Party. Use thes endpoint when starting a lti
    deeplink flow.

    Args:
        app_id (str):
        parent_id (str):
        node_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        str
    """

    return sync_detailed(
        client=client,
        app_id=app_id,
        parent_id=parent_id,
        node_id=node_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    app_id: str,
    parent_id: str,
    node_id: str | Unset = UNSET,
) -> Response[str]:
    """generate a form used for Initiating Login from a Third Party. Use thes endpoint when starting a lti
    deeplink flow.

    Args:
        app_id (str):
        parent_id (str):
        node_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[str]
    """

    kwargs = _get_kwargs(
        app_id=app_id,
        parent_id=parent_id,
        node_id=node_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    app_id: str,
    parent_id: str,
    node_id: str | Unset = UNSET,
) -> str | None:
    """generate a form used for Initiating Login from a Third Party. Use thes endpoint when starting a lti
    deeplink flow.

    Args:
        app_id (str):
        parent_id (str):
        node_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        str
    """

    return (
        await asyncio_detailed(
            client=client,
            app_id=app_id,
            parent_id=parent_id,
            node_id=node_id,
        )
    ).parsed
