from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.register_exists import RegisterExists
from ...types import Response


def _get_kwargs(
    mail: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/register/v1/exists/{mail}".format(
            mail=quote(str(mail), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | RegisterExists | None:
    if response.status_code == 200:
        response_200 = RegisterExists.from_dict(response.json())

        return response_200

    if response.status_code == 500:
        response_500 = ErrorResponse.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ErrorResponse | RegisterExists]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    mail: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[ErrorResponse | RegisterExists]:
    """Check if the given mail is already successfully registered

    Args:
        mail (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | RegisterExists]
    """

    kwargs = _get_kwargs(
        mail=mail,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    mail: str,
    *,
    client: AuthenticatedClient | Client,
) -> ErrorResponse | RegisterExists | None:
    """Check if the given mail is already successfully registered

    Args:
        mail (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | RegisterExists
    """

    return sync_detailed(
        mail=mail,
        client=client,
    ).parsed


async def asyncio_detailed(
    mail: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[ErrorResponse | RegisterExists]:
    """Check if the given mail is already successfully registered

    Args:
        mail (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | RegisterExists]
    """

    kwargs = _get_kwargs(
        mail=mail,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    mail: str,
    *,
    client: AuthenticatedClient | Client,
) -> ErrorResponse | RegisterExists | None:
    """Check if the given mail is already successfully registered

    Args:
        mail (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | RegisterExists
    """

    return (
        await asyncio_detailed(
            mail=mail,
            client=client,
        )
    ).parsed
