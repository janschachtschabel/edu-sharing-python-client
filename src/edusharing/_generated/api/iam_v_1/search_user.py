from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.search_user_status import SearchUserStatus
from ...models.user_entries import UserEntries
from ...types import UNSET, Response, Unset


def _get_kwargs(
    repository: str,
    *,
    pattern: str,
    global_: bool | Unset = True,
    status: SearchUserStatus | Unset = UNSET,
    max_items: int | Unset = 10,
    skip_count: int | Unset = 0,
    sort_properties: list[str] | Unset = UNSET,
    sort_ascending: list[bool] | Unset = UNSET,
    resolve_organisations: bool | Unset = True,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["pattern"] = pattern

    params["global"] = global_

    json_status: str | Unset = UNSET
    if not isinstance(status, Unset):
        json_status = status.value

    params["status"] = json_status

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

    params["resolveOrganisations"] = resolve_organisations

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/iam/v1/people/{repository}".format(
            repository=quote(str(repository), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | UserEntries | None:
    if response.status_code == 200:
        response_200 = UserEntries.from_dict(response.json())

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
) -> Response[ErrorResponse | UserEntries]:
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
    pattern: str,
    global_: bool | Unset = True,
    status: SearchUserStatus | Unset = UNSET,
    max_items: int | Unset = 10,
    skip_count: int | Unset = 0,
    sort_properties: list[str] | Unset = UNSET,
    sort_ascending: list[bool] | Unset = UNSET,
    resolve_organisations: bool | Unset = True,
) -> Response[ErrorResponse | UserEntries]:
    """Search users.

     Search users. (admin rights are required.)

    Args:
        repository (str):
        pattern (str):
        global_ (bool | Unset):  Default: True.
        status (SearchUserStatus | Unset):
        max_items (int | Unset):  Default: 10.
        skip_count (int | Unset):  Default: 0.
        sort_properties (list[str] | Unset):
        sort_ascending (list[bool] | Unset):
        resolve_organisations (bool | Unset):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | UserEntries]
    """

    kwargs = _get_kwargs(
        repository=repository,
        pattern=pattern,
        global_=global_,
        status=status,
        max_items=max_items,
        skip_count=skip_count,
        sort_properties=sort_properties,
        sort_ascending=sort_ascending,
        resolve_organisations=resolve_organisations,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repository: str,
    *,
    client: AuthenticatedClient | Client,
    pattern: str,
    global_: bool | Unset = True,
    status: SearchUserStatus | Unset = UNSET,
    max_items: int | Unset = 10,
    skip_count: int | Unset = 0,
    sort_properties: list[str] | Unset = UNSET,
    sort_ascending: list[bool] | Unset = UNSET,
    resolve_organisations: bool | Unset = True,
) -> ErrorResponse | UserEntries | None:
    """Search users.

     Search users. (admin rights are required.)

    Args:
        repository (str):
        pattern (str):
        global_ (bool | Unset):  Default: True.
        status (SearchUserStatus | Unset):
        max_items (int | Unset):  Default: 10.
        skip_count (int | Unset):  Default: 0.
        sort_properties (list[str] | Unset):
        sort_ascending (list[bool] | Unset):
        resolve_organisations (bool | Unset):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | UserEntries
    """

    return sync_detailed(
        repository=repository,
        client=client,
        pattern=pattern,
        global_=global_,
        status=status,
        max_items=max_items,
        skip_count=skip_count,
        sort_properties=sort_properties,
        sort_ascending=sort_ascending,
        resolve_organisations=resolve_organisations,
    ).parsed


async def asyncio_detailed(
    repository: str,
    *,
    client: AuthenticatedClient | Client,
    pattern: str,
    global_: bool | Unset = True,
    status: SearchUserStatus | Unset = UNSET,
    max_items: int | Unset = 10,
    skip_count: int | Unset = 0,
    sort_properties: list[str] | Unset = UNSET,
    sort_ascending: list[bool] | Unset = UNSET,
    resolve_organisations: bool | Unset = True,
) -> Response[ErrorResponse | UserEntries]:
    """Search users.

     Search users. (admin rights are required.)

    Args:
        repository (str):
        pattern (str):
        global_ (bool | Unset):  Default: True.
        status (SearchUserStatus | Unset):
        max_items (int | Unset):  Default: 10.
        skip_count (int | Unset):  Default: 0.
        sort_properties (list[str] | Unset):
        sort_ascending (list[bool] | Unset):
        resolve_organisations (bool | Unset):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | UserEntries]
    """

    kwargs = _get_kwargs(
        repository=repository,
        pattern=pattern,
        global_=global_,
        status=status,
        max_items=max_items,
        skip_count=skip_count,
        sort_properties=sort_properties,
        sort_ascending=sort_ascending,
        resolve_organisations=resolve_organisations,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    *,
    client: AuthenticatedClient | Client,
    pattern: str,
    global_: bool | Unset = True,
    status: SearchUserStatus | Unset = UNSET,
    max_items: int | Unset = 10,
    skip_count: int | Unset = 0,
    sort_properties: list[str] | Unset = UNSET,
    sort_ascending: list[bool] | Unset = UNSET,
    resolve_organisations: bool | Unset = True,
) -> ErrorResponse | UserEntries | None:
    """Search users.

     Search users. (admin rights are required.)

    Args:
        repository (str):
        pattern (str):
        global_ (bool | Unset):  Default: True.
        status (SearchUserStatus | Unset):
        max_items (int | Unset):  Default: 10.
        skip_count (int | Unset):  Default: 0.
        sort_properties (list[str] | Unset):
        sort_ascending (list[bool] | Unset):
        resolve_organisations (bool | Unset):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | UserEntries
    """

    return (
        await asyncio_detailed(
            repository=repository,
            client=client,
            pattern=pattern,
            global_=global_,
            status=status,
            max_items=max_items,
            skip_count=skip_count,
            sort_properties=sort_properties,
            sort_ascending=sort_ascending,
            resolve_organisations=resolve_organisations,
        )
    ).parsed
