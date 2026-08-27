from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.contributor_data import ContributorData
from ...models.error_response import ErrorResponse
from ...models.update_contributor_request import UpdateContributorRequest
from ...types import UNSET, Response, Unset


def _get_kwargs(
    repository: str,
    id: int,
    *,
    body: UpdateContributorRequest | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/contributor/v1/{repository}/{id}".format(
            repository=quote(str(repository), safe=""),
            id=quote(str(id), safe=""),
        ),
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ContributorData | ErrorResponse | None:
    if response.status_code == 200:
        response_200 = ContributorData.from_dict(response.json())

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
) -> Response[ContributorData | ErrorResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    repository: str,
    id: int,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateContributorRequest | Unset = UNSET,
) -> Response[ContributorData | ErrorResponse]:
    """update a managed contributor

     Updates a contributor. With applyToExisting=true the change is propagated to all media carrying this
    contributor. Requires the TOOLPERMISSION_MANAGE_CONTRIBUTORS toolpermission.

    Args:
        repository (str):
        id (int):
        body (UpdateContributorRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ContributorData | ErrorResponse]
    """

    kwargs = _get_kwargs(
        repository=repository,
        id=id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repository: str,
    id: int,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateContributorRequest | Unset = UNSET,
) -> ContributorData | ErrorResponse | None:
    """update a managed contributor

     Updates a contributor. With applyToExisting=true the change is propagated to all media carrying this
    contributor. Requires the TOOLPERMISSION_MANAGE_CONTRIBUTORS toolpermission.

    Args:
        repository (str):
        id (int):
        body (UpdateContributorRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ContributorData | ErrorResponse
    """

    return sync_detailed(
        repository=repository,
        id=id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    repository: str,
    id: int,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateContributorRequest | Unset = UNSET,
) -> Response[ContributorData | ErrorResponse]:
    """update a managed contributor

     Updates a contributor. With applyToExisting=true the change is propagated to all media carrying this
    contributor. Requires the TOOLPERMISSION_MANAGE_CONTRIBUTORS toolpermission.

    Args:
        repository (str):
        id (int):
        body (UpdateContributorRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ContributorData | ErrorResponse]
    """

    kwargs = _get_kwargs(
        repository=repository,
        id=id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    id: int,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateContributorRequest | Unset = UNSET,
) -> ContributorData | ErrorResponse | None:
    """update a managed contributor

     Updates a contributor. With applyToExisting=true the change is propagated to all media carrying this
    contributor. Requires the TOOLPERMISSION_MANAGE_CONTRIBUTORS toolpermission.

    Args:
        repository (str):
        id (int):
        body (UpdateContributorRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ContributorData | ErrorResponse
    """

    return (
        await asyncio_detailed(
            repository=repository,
            id=id,
            client=client,
            body=body,
        )
    ).parsed
