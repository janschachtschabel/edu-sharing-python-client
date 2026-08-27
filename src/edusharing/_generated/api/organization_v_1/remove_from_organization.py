from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.organization_user_deprovisioning import OrganizationUserDeprovisioning
from ...types import UNSET, Response, Unset


def _get_kwargs(
    repository: str,
    organization: str,
    member: str,
    *,
    body: OrganizationUserDeprovisioning | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/organization/v1/organizations/{repository}/{organization}/member/{member}".format(
            repository=quote(str(repository), safe=""),
            organization=quote(str(organization), safe=""),
            member=quote(str(member), safe=""),
        ),
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | ErrorResponse | None:
    if response.status_code == 200:
        response_200 = cast(Any, None)
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
) -> Response[Any | ErrorResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    repository: str,
    organization: str,
    member: str,
    *,
    client: AuthenticatedClient | Client,
    body: OrganizationUserDeprovisioning | Unset = UNSET,
) -> Response[Any | ErrorResponse]:
    """Remove member from organization.

     Remove member from organization. Requires at least admin permissions for the organization. For mode
    assign, full admin rights are required

    Args:
        repository (str):
        organization (str):
        member (str):
        body (OrganizationUserDeprovisioning | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ErrorResponse]
    """

    kwargs = _get_kwargs(
        repository=repository,
        organization=organization,
        member=member,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repository: str,
    organization: str,
    member: str,
    *,
    client: AuthenticatedClient | Client,
    body: OrganizationUserDeprovisioning | Unset = UNSET,
) -> Any | ErrorResponse | None:
    """Remove member from organization.

     Remove member from organization. Requires at least admin permissions for the organization. For mode
    assign, full admin rights are required

    Args:
        repository (str):
        organization (str):
        member (str):
        body (OrganizationUserDeprovisioning | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ErrorResponse
    """

    return sync_detailed(
        repository=repository,
        organization=organization,
        member=member,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    repository: str,
    organization: str,
    member: str,
    *,
    client: AuthenticatedClient | Client,
    body: OrganizationUserDeprovisioning | Unset = UNSET,
) -> Response[Any | ErrorResponse]:
    """Remove member from organization.

     Remove member from organization. Requires at least admin permissions for the organization. For mode
    assign, full admin rights are required

    Args:
        repository (str):
        organization (str):
        member (str):
        body (OrganizationUserDeprovisioning | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ErrorResponse]
    """

    kwargs = _get_kwargs(
        repository=repository,
        organization=organization,
        member=member,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    organization: str,
    member: str,
    *,
    client: AuthenticatedClient | Client,
    body: OrganizationUserDeprovisioning | Unset = UNSET,
) -> Any | ErrorResponse | None:
    """Remove member from organization.

     Remove member from organization. Requires at least admin permissions for the organization. For mode
    assign, full admin rights are required

    Args:
        repository (str):
        organization (str):
        member (str):
        body (OrganizationUserDeprovisioning | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ErrorResponse
    """

    return (
        await asyncio_detailed(
            repository=repository,
            organization=organization,
            member=member,
            client=client,
            body=body,
        )
    ).parsed
