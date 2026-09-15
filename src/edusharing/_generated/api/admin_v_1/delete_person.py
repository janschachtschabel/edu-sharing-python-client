from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.person_delete_options import PersonDeleteOptions
from ...models.person_report import PersonReport
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: PersonDeleteOptions | Unset = UNSET,
    username: list[str],
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    json_username = username

    params["username"] = json_username

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/admin/v1/deletePersons",
        "params": params,
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | PersonReport | None:
    if response.status_code == 200:
        response_200 = PersonReport.from_dict(response.json())

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
) -> Response[ErrorResponse | PersonReport]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: PersonDeleteOptions | Unset = UNSET,
    username: list[str],
) -> Response[ErrorResponse | PersonReport]:
    r"""delete persons

     delete the given persons. Their status must be set to \"todelete\"

    Args:
        username (list[str]):
        body (PersonDeleteOptions | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | PersonReport]
    """

    kwargs = _get_kwargs(
        body=body,
        username=username,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: PersonDeleteOptions | Unset = UNSET,
    username: list[str],
) -> ErrorResponse | PersonReport | None:
    r"""delete persons

     delete the given persons. Their status must be set to \"todelete\"

    Args:
        username (list[str]):
        body (PersonDeleteOptions | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | PersonReport
    """

    return sync_detailed(
        client=client,
        body=body,
        username=username,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: PersonDeleteOptions | Unset = UNSET,
    username: list[str],
) -> Response[ErrorResponse | PersonReport]:
    r"""delete persons

     delete the given persons. Their status must be set to \"todelete\"

    Args:
        username (list[str]):
        body (PersonDeleteOptions | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | PersonReport]
    """

    kwargs = _get_kwargs(
        body=body,
        username=username,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: PersonDeleteOptions | Unset = UNSET,
    username: list[str],
) -> ErrorResponse | PersonReport | None:
    r"""delete persons

     delete the given persons. Their status must be set to \"todelete\"

    Args:
        username (list[str]):
        body (PersonDeleteOptions | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | PersonReport
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            username=username,
        )
    ).parsed
