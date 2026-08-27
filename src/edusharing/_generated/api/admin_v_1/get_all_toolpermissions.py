from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.get_all_toolpermissions_response_200 import GetAllToolpermissionsResponse200
from ...types import Response


def _get_kwargs(
    authority: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/admin/v1/toolpermissions/{authority}".format(
            authority=quote(str(authority), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | GetAllToolpermissionsResponse200 | None:
    if response.status_code == 200:
        response_200 = GetAllToolpermissionsResponse200.from_dict(response.json())

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
) -> Response[ErrorResponse | GetAllToolpermissionsResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    authority: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[ErrorResponse | GetAllToolpermissionsResponse200]:
    """get all toolpermissions for an authority

     Returns explicit (rights set for this authority) + effective (resulting rights for this authority)
    toolpermission

    Args:
        authority (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | GetAllToolpermissionsResponse200]
    """

    kwargs = _get_kwargs(
        authority=authority,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    authority: str,
    *,
    client: AuthenticatedClient | Client,
) -> ErrorResponse | GetAllToolpermissionsResponse200 | None:
    """get all toolpermissions for an authority

     Returns explicit (rights set for this authority) + effective (resulting rights for this authority)
    toolpermission

    Args:
        authority (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | GetAllToolpermissionsResponse200
    """

    return sync_detailed(
        authority=authority,
        client=client,
    ).parsed


async def asyncio_detailed(
    authority: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[ErrorResponse | GetAllToolpermissionsResponse200]:
    """get all toolpermissions for an authority

     Returns explicit (rights set for this authority) + effective (resulting rights for this authority)
    toolpermission

    Args:
        authority (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | GetAllToolpermissionsResponse200]
    """

    kwargs = _get_kwargs(
        authority=authority,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    authority: str,
    *,
    client: AuthenticatedClient | Client,
) -> ErrorResponse | GetAllToolpermissionsResponse200 | None:
    """get all toolpermissions for an authority

     Returns explicit (rights set for this authority) + effective (resulting rights for this authority)
    toolpermission

    Args:
        authority (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | GetAllToolpermissionsResponse200
    """

    return (
        await asyncio_detailed(
            authority=authority,
            client=client,
        )
    ).parsed
