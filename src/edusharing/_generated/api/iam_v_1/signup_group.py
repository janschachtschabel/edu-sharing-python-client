from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.signup_group_response_200 import SignupGroupResponse200
from ...types import UNSET, Response, Unset


def _get_kwargs(
    repository: str,
    group: str,
    *,
    password: str | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["password"] = password

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/iam/v1/groups/{repository}/{group}/signup".format(
            repository=quote(str(repository), safe=""),
            group=quote(str(group), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | SignupGroupResponse200 | None:
    if response.status_code == 200:
        response_200 = SignupGroupResponse200(response.json())

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
) -> Response[ErrorResponse | SignupGroupResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    repository: str,
    group: str,
    *,
    client: AuthenticatedClient | Client,
    password: str | Unset = UNSET,
) -> Response[ErrorResponse | SignupGroupResponse200]:
    """let the current user signup to the given group

    Args:
        repository (str):
        group (str):
        password (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | SignupGroupResponse200]
    """

    kwargs = _get_kwargs(
        repository=repository,
        group=group,
        password=password,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repository: str,
    group: str,
    *,
    client: AuthenticatedClient | Client,
    password: str | Unset = UNSET,
) -> ErrorResponse | SignupGroupResponse200 | None:
    """let the current user signup to the given group

    Args:
        repository (str):
        group (str):
        password (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | SignupGroupResponse200
    """

    return sync_detailed(
        repository=repository,
        group=group,
        client=client,
        password=password,
    ).parsed


async def asyncio_detailed(
    repository: str,
    group: str,
    *,
    client: AuthenticatedClient | Client,
    password: str | Unset = UNSET,
) -> Response[ErrorResponse | SignupGroupResponse200]:
    """let the current user signup to the given group

    Args:
        repository (str):
        group (str):
        password (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | SignupGroupResponse200]
    """

    kwargs = _get_kwargs(
        repository=repository,
        group=group,
        password=password,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    group: str,
    *,
    client: AuthenticatedClient | Client,
    password: str | Unset = UNSET,
) -> ErrorResponse | SignupGroupResponse200 | None:
    """let the current user signup to the given group

    Args:
        repository (str):
        group (str):
        password (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | SignupGroupResponse200
    """

    return (
        await asyncio_detailed(
            repository=repository,
            group=group,
            client=client,
            password=password,
        )
    ).parsed
