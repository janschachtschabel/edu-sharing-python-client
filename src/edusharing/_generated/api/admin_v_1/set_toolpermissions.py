from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.set_toolpermissions_body import SetToolpermissionsBody
from ...models.set_toolpermissions_response_200 import SetToolpermissionsResponse200
from ...types import UNSET, Response, Unset


def _get_kwargs(
    authority: str,
    *,
    body: SetToolpermissionsBody | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/admin/v1/toolpermissions/{authority}".format(
            authority=quote(str(authority), safe=""),
        ),
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | SetToolpermissionsResponse200 | None:
    if response.status_code == 200:
        response_200 = SetToolpermissionsResponse200.from_dict(response.json())

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
) -> Response[ErrorResponse | SetToolpermissionsResponse200]:
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
    body: SetToolpermissionsBody | Unset = UNSET,
) -> Response[ErrorResponse | SetToolpermissionsResponse200]:
    """set toolpermissions for an authority

     If a toolpermission has status UNDEFINED, it will remove explicit permissions for the authority

    Args:
        authority (str):
        body (SetToolpermissionsBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | SetToolpermissionsResponse200]
    """

    kwargs = _get_kwargs(
        authority=authority,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    authority: str,
    *,
    client: AuthenticatedClient | Client,
    body: SetToolpermissionsBody | Unset = UNSET,
) -> ErrorResponse | SetToolpermissionsResponse200 | None:
    """set toolpermissions for an authority

     If a toolpermission has status UNDEFINED, it will remove explicit permissions for the authority

    Args:
        authority (str):
        body (SetToolpermissionsBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | SetToolpermissionsResponse200
    """

    return sync_detailed(
        authority=authority,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    authority: str,
    *,
    client: AuthenticatedClient | Client,
    body: SetToolpermissionsBody | Unset = UNSET,
) -> Response[ErrorResponse | SetToolpermissionsResponse200]:
    """set toolpermissions for an authority

     If a toolpermission has status UNDEFINED, it will remove explicit permissions for the authority

    Args:
        authority (str):
        body (SetToolpermissionsBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | SetToolpermissionsResponse200]
    """

    kwargs = _get_kwargs(
        authority=authority,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    authority: str,
    *,
    client: AuthenticatedClient | Client,
    body: SetToolpermissionsBody | Unset = UNSET,
) -> ErrorResponse | SetToolpermissionsResponse200 | None:
    """set toolpermissions for an authority

     If a toolpermission has status UNDEFINED, it will remove explicit permissions for the authority

    Args:
        authority (str):
        body (SetToolpermissionsBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | SetToolpermissionsResponse200
    """

    return (
        await asyncio_detailed(
            authority=authority,
            client=client,
            body=body,
        )
    ).parsed
