from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.mediacenter import Mediacenter
from ...models.profile import Profile
from ...types import UNSET, Response, Unset


def _get_kwargs(
    repository: str,
    mediacenter: str,
    *,
    body: Profile | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/mediacenter/v1/mediacenter/{repository}/{mediacenter}".format(
            repository=quote(str(repository), safe=""),
            mediacenter=quote(str(mediacenter), safe=""),
        ),
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | Mediacenter | None:
    if response.status_code == 200:
        response_200 = Mediacenter.from_dict(response.json())

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

    if response.status_code == 409:
        response_409 = ErrorResponse.from_dict(response.json())

        return response_409

    if response.status_code == 500:
        response_500 = ErrorResponse.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ErrorResponse | Mediacenter]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    repository: str,
    mediacenter: str,
    *,
    client: AuthenticatedClient | Client,
    body: Profile | Unset = UNSET,
) -> Response[ErrorResponse | Mediacenter]:
    """edit a mediacenter in repository.

    Args:
        repository (str):
        mediacenter (str):
        body (Profile | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | Mediacenter]
    """

    kwargs = _get_kwargs(
        repository=repository,
        mediacenter=mediacenter,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repository: str,
    mediacenter: str,
    *,
    client: AuthenticatedClient | Client,
    body: Profile | Unset = UNSET,
) -> ErrorResponse | Mediacenter | None:
    """edit a mediacenter in repository.

    Args:
        repository (str):
        mediacenter (str):
        body (Profile | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | Mediacenter
    """

    return sync_detailed(
        repository=repository,
        mediacenter=mediacenter,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    repository: str,
    mediacenter: str,
    *,
    client: AuthenticatedClient | Client,
    body: Profile | Unset = UNSET,
) -> Response[ErrorResponse | Mediacenter]:
    """edit a mediacenter in repository.

    Args:
        repository (str):
        mediacenter (str):
        body (Profile | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | Mediacenter]
    """

    kwargs = _get_kwargs(
        repository=repository,
        mediacenter=mediacenter,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    mediacenter: str,
    *,
    client: AuthenticatedClient | Client,
    body: Profile | Unset = UNSET,
) -> ErrorResponse | Mediacenter | None:
    """edit a mediacenter in repository.

    Args:
        repository (str):
        mediacenter (str):
        body (Profile | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | Mediacenter
    """

    return (
        await asyncio_detailed(
            repository=repository,
            mediacenter=mediacenter,
            client=client,
            body=body,
        )
    ).parsed
