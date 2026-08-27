from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.dynamic_registration_tokens import DynamicRegistrationTokens
from ...types import UNSET, Response


def _get_kwargs(
    *,
    generate: bool = False,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["generate"] = generate

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/lti/v13/registration/url",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> DynamicRegistrationTokens | str | None:
    if response.status_code == 200:
        response_200 = DynamicRegistrationTokens.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = cast(str, response.json())
        return response_400

    if response.status_code == 401:
        response_401 = cast(str, response.json())
        return response_401

    if response.status_code == 403:
        response_403 = cast(str, response.json())
        return response_403

    if response.status_code == 404:
        response_404 = cast(str, response.json())
        return response_404

    if response.status_code == 500:
        response_500 = cast(str, response.json())
        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[DynamicRegistrationTokens | str]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    generate: bool = False,
) -> Response[DynamicRegistrationTokens | str]:
    """LTI Dynamic Registration - generates url for platform

    Args:
        generate (bool):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DynamicRegistrationTokens | str]
    """

    kwargs = _get_kwargs(
        generate=generate,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    generate: bool = False,
) -> DynamicRegistrationTokens | str | None:
    """LTI Dynamic Registration - generates url for platform

    Args:
        generate (bool):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DynamicRegistrationTokens | str
    """

    return sync_detailed(
        client=client,
        generate=generate,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    generate: bool = False,
) -> Response[DynamicRegistrationTokens | str]:
    """LTI Dynamic Registration - generates url for platform

    Args:
        generate (bool):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DynamicRegistrationTokens | str]
    """

    kwargs = _get_kwargs(
        generate=generate,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    generate: bool = False,
) -> DynamicRegistrationTokens | str | None:
    """LTI Dynamic Registration - generates url for platform

    Args:
        generate (bool):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DynamicRegistrationTokens | str
    """

    return (
        await asyncio_detailed(
            client=client,
            generate=generate,
        )
    ).parsed
