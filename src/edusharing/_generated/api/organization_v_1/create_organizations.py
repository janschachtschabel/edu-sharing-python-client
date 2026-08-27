from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.organization import Organization
from ...types import UNSET, Response, Unset


def _get_kwargs(
    repository: str,
    organization: str,
    *,
    eduscope: str | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["eduscope"] = eduscope

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/organization/v1/organizations/{repository}/{organization}".format(
            repository=quote(str(repository), safe=""),
            organization=quote(str(organization), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | Organization | None:
    if response.status_code == 200:
        response_200 = Organization.from_dict(response.json())

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
) -> Response[ErrorResponse | Organization]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    repository: str,
    organization: str,
    *,
    client: AuthenticatedClient | Client,
    eduscope: str | Unset = UNSET,
) -> Response[ErrorResponse | Organization]:
    """create organization in repository.

     create organization in repository.

    Args:
        repository (str):
        organization (str):
        eduscope (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | Organization]
    """

    kwargs = _get_kwargs(
        repository=repository,
        organization=organization,
        eduscope=eduscope,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repository: str,
    organization: str,
    *,
    client: AuthenticatedClient | Client,
    eduscope: str | Unset = UNSET,
) -> ErrorResponse | Organization | None:
    """create organization in repository.

     create organization in repository.

    Args:
        repository (str):
        organization (str):
        eduscope (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | Organization
    """

    return sync_detailed(
        repository=repository,
        organization=organization,
        client=client,
        eduscope=eduscope,
    ).parsed


async def asyncio_detailed(
    repository: str,
    organization: str,
    *,
    client: AuthenticatedClient | Client,
    eduscope: str | Unset = UNSET,
) -> Response[ErrorResponse | Organization]:
    """create organization in repository.

     create organization in repository.

    Args:
        repository (str):
        organization (str):
        eduscope (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | Organization]
    """

    kwargs = _get_kwargs(
        repository=repository,
        organization=organization,
        eduscope=eduscope,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    organization: str,
    *,
    client: AuthenticatedClient | Client,
    eduscope: str | Unset = UNSET,
) -> ErrorResponse | Organization | None:
    """create organization in repository.

     create organization in repository.

    Args:
        repository (str):
        organization (str):
        eduscope (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | Organization
    """

    return (
        await asyncio_detailed(
            repository=repository,
            organization=organization,
            client=client,
            eduscope=eduscope,
        )
    ).parsed
