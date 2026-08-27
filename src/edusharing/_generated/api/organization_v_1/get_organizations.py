from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.organization_entries import OrganizationEntries
from ...types import UNSET, Response, Unset


def _get_kwargs(
    repository: str,
    *,
    pattern: str | Unset = UNSET,
    max_items: int | Unset = 10,
    skip_count: int | Unset = 0,
    sort_properties: list[str] | Unset = UNSET,
    sort_ascending: list[bool] | Unset = UNSET,
    only_memberships: bool | Unset = True,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["pattern"] = pattern

    params["maxItems"] = max_items

    params["skipCount"] = skip_count

    json_sort_properties: list[str] | Unset = UNSET
    if not isinstance(sort_properties, Unset):
        json_sort_properties = sort_properties

    params["sortProperties"] = json_sort_properties

    json_sort_ascending: list[bool] | Unset = UNSET
    if not isinstance(sort_ascending, Unset):
        json_sort_ascending = sort_ascending

    params["sortAscending"] = json_sort_ascending

    params["onlyMemberships"] = only_memberships

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/organization/v1/organizations/{repository}".format(
            repository=quote(str(repository), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | OrganizationEntries | None:
    if response.status_code == 200:
        response_200 = OrganizationEntries.from_dict(response.json())

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
) -> Response[ErrorResponse | OrganizationEntries]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    repository: str,
    *,
    client: AuthenticatedClient | Client,
    pattern: str | Unset = UNSET,
    max_items: int | Unset = 10,
    skip_count: int | Unset = 0,
    sort_properties: list[str] | Unset = UNSET,
    sort_ascending: list[bool] | Unset = UNSET,
    only_memberships: bool | Unset = True,
) -> Response[ErrorResponse | OrganizationEntries]:
    """Get organizations of repository.

     Get organizations of repository the current user is member. May returns an empty list.

    Args:
        repository (str):
        pattern (str | Unset):
        max_items (int | Unset):  Default: 10.
        skip_count (int | Unset):  Default: 0.
        sort_properties (list[str] | Unset):
        sort_ascending (list[bool] | Unset):
        only_memberships (bool | Unset):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | OrganizationEntries]
    """

    kwargs = _get_kwargs(
        repository=repository,
        pattern=pattern,
        max_items=max_items,
        skip_count=skip_count,
        sort_properties=sort_properties,
        sort_ascending=sort_ascending,
        only_memberships=only_memberships,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repository: str,
    *,
    client: AuthenticatedClient | Client,
    pattern: str | Unset = UNSET,
    max_items: int | Unset = 10,
    skip_count: int | Unset = 0,
    sort_properties: list[str] | Unset = UNSET,
    sort_ascending: list[bool] | Unset = UNSET,
    only_memberships: bool | Unset = True,
) -> ErrorResponse | OrganizationEntries | None:
    """Get organizations of repository.

     Get organizations of repository the current user is member. May returns an empty list.

    Args:
        repository (str):
        pattern (str | Unset):
        max_items (int | Unset):  Default: 10.
        skip_count (int | Unset):  Default: 0.
        sort_properties (list[str] | Unset):
        sort_ascending (list[bool] | Unset):
        only_memberships (bool | Unset):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | OrganizationEntries
    """

    return sync_detailed(
        repository=repository,
        client=client,
        pattern=pattern,
        max_items=max_items,
        skip_count=skip_count,
        sort_properties=sort_properties,
        sort_ascending=sort_ascending,
        only_memberships=only_memberships,
    ).parsed


async def asyncio_detailed(
    repository: str,
    *,
    client: AuthenticatedClient | Client,
    pattern: str | Unset = UNSET,
    max_items: int | Unset = 10,
    skip_count: int | Unset = 0,
    sort_properties: list[str] | Unset = UNSET,
    sort_ascending: list[bool] | Unset = UNSET,
    only_memberships: bool | Unset = True,
) -> Response[ErrorResponse | OrganizationEntries]:
    """Get organizations of repository.

     Get organizations of repository the current user is member. May returns an empty list.

    Args:
        repository (str):
        pattern (str | Unset):
        max_items (int | Unset):  Default: 10.
        skip_count (int | Unset):  Default: 0.
        sort_properties (list[str] | Unset):
        sort_ascending (list[bool] | Unset):
        only_memberships (bool | Unset):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | OrganizationEntries]
    """

    kwargs = _get_kwargs(
        repository=repository,
        pattern=pattern,
        max_items=max_items,
        skip_count=skip_count,
        sort_properties=sort_properties,
        sort_ascending=sort_ascending,
        only_memberships=only_memberships,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    *,
    client: AuthenticatedClient | Client,
    pattern: str | Unset = UNSET,
    max_items: int | Unset = 10,
    skip_count: int | Unset = 0,
    sort_properties: list[str] | Unset = UNSET,
    sort_ascending: list[bool] | Unset = UNSET,
    only_memberships: bool | Unset = True,
) -> ErrorResponse | OrganizationEntries | None:
    """Get organizations of repository.

     Get organizations of repository the current user is member. May returns an empty list.

    Args:
        repository (str):
        pattern (str | Unset):
        max_items (int | Unset):  Default: 10.
        skip_count (int | Unset):  Default: 0.
        sort_properties (list[str] | Unset):
        sort_ascending (list[bool] | Unset):
        only_memberships (bool | Unset):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | OrganizationEntries
    """

    return (
        await asyncio_detailed(
            repository=repository,
            client=client,
            pattern=pattern,
            max_items=max_items,
            skip_count=skip_count,
            sort_properties=sort_properties,
            sort_ascending=sort_ascending,
            only_memberships=only_memberships,
        )
    ).parsed
