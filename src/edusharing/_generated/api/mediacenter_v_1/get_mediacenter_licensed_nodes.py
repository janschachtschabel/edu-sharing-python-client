from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.group import Group
from ...models.search_parameters import SearchParameters
from ...types import UNSET, Response, Unset


def _get_kwargs(
    repository: str,
    mediacenter: str,
    *,
    body: SearchParameters,
    max_items: int | Unset = 10,
    skip_count: int | Unset = 0,
    sort_properties: list[str] | Unset = UNSET,
    sort_ascending: list[bool] | Unset = UNSET,
    property_filter: list[str] | Unset = UNSET,
    searchword: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

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

    json_property_filter: list[str] | Unset = UNSET
    if not isinstance(property_filter, Unset):
        json_property_filter = property_filter

    params["propertyFilter"] = json_property_filter

    params["searchword"] = searchword

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/mediacenter/v1/mediacenter/{repository}/{mediacenter}/licenses".format(
            repository=quote(str(repository), safe=""),
            mediacenter=quote(str(mediacenter), safe=""),
        ),
        "params": params,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | list[Group] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = Group.from_dict(response_200_item_data)

            response_200.append(response_200_item)

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
) -> Response[ErrorResponse | list[Group]]:
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
    body: SearchParameters,
    max_items: int | Unset = 10,
    skip_count: int | Unset = 0,
    sort_properties: list[str] | Unset = UNSET,
    sort_ascending: list[bool] | Unset = UNSET,
    property_filter: list[str] | Unset = UNSET,
    searchword: str,
) -> Response[ErrorResponse | list[Group]]:
    """get nodes that are licensed by the given mediacenter

    Args:
        repository (str):
        mediacenter (str):
        max_items (int | Unset):  Default: 10.
        skip_count (int | Unset):  Default: 0.
        sort_properties (list[str] | Unset):
        sort_ascending (list[bool] | Unset):
        property_filter (list[str] | Unset):
        searchword (str):
        body (SearchParameters):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | list[Group]]
    """

    kwargs = _get_kwargs(
        repository=repository,
        mediacenter=mediacenter,
        body=body,
        max_items=max_items,
        skip_count=skip_count,
        sort_properties=sort_properties,
        sort_ascending=sort_ascending,
        property_filter=property_filter,
        searchword=searchword,
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
    body: SearchParameters,
    max_items: int | Unset = 10,
    skip_count: int | Unset = 0,
    sort_properties: list[str] | Unset = UNSET,
    sort_ascending: list[bool] | Unset = UNSET,
    property_filter: list[str] | Unset = UNSET,
    searchword: str,
) -> ErrorResponse | list[Group] | None:
    """get nodes that are licensed by the given mediacenter

    Args:
        repository (str):
        mediacenter (str):
        max_items (int | Unset):  Default: 10.
        skip_count (int | Unset):  Default: 0.
        sort_properties (list[str] | Unset):
        sort_ascending (list[bool] | Unset):
        property_filter (list[str] | Unset):
        searchword (str):
        body (SearchParameters):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | list[Group]
    """

    return sync_detailed(
        repository=repository,
        mediacenter=mediacenter,
        client=client,
        body=body,
        max_items=max_items,
        skip_count=skip_count,
        sort_properties=sort_properties,
        sort_ascending=sort_ascending,
        property_filter=property_filter,
        searchword=searchword,
    ).parsed


async def asyncio_detailed(
    repository: str,
    mediacenter: str,
    *,
    client: AuthenticatedClient | Client,
    body: SearchParameters,
    max_items: int | Unset = 10,
    skip_count: int | Unset = 0,
    sort_properties: list[str] | Unset = UNSET,
    sort_ascending: list[bool] | Unset = UNSET,
    property_filter: list[str] | Unset = UNSET,
    searchword: str,
) -> Response[ErrorResponse | list[Group]]:
    """get nodes that are licensed by the given mediacenter

    Args:
        repository (str):
        mediacenter (str):
        max_items (int | Unset):  Default: 10.
        skip_count (int | Unset):  Default: 0.
        sort_properties (list[str] | Unset):
        sort_ascending (list[bool] | Unset):
        property_filter (list[str] | Unset):
        searchword (str):
        body (SearchParameters):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | list[Group]]
    """

    kwargs = _get_kwargs(
        repository=repository,
        mediacenter=mediacenter,
        body=body,
        max_items=max_items,
        skip_count=skip_count,
        sort_properties=sort_properties,
        sort_ascending=sort_ascending,
        property_filter=property_filter,
        searchword=searchword,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    mediacenter: str,
    *,
    client: AuthenticatedClient | Client,
    body: SearchParameters,
    max_items: int | Unset = 10,
    skip_count: int | Unset = 0,
    sort_properties: list[str] | Unset = UNSET,
    sort_ascending: list[bool] | Unset = UNSET,
    property_filter: list[str] | Unset = UNSET,
    searchword: str,
) -> ErrorResponse | list[Group] | None:
    """get nodes that are licensed by the given mediacenter

    Args:
        repository (str):
        mediacenter (str):
        max_items (int | Unset):  Default: 10.
        skip_count (int | Unset):  Default: 0.
        sort_properties (list[str] | Unset):
        sort_ascending (list[bool] | Unset):
        property_filter (list[str] | Unset):
        searchword (str):
        body (SearchParameters):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | list[Group]
    """

    return (
        await asyncio_detailed(
            repository=repository,
            mediacenter=mediacenter,
            client=client,
            body=body,
            max_items=max_items,
            skip_count=skip_count,
            sort_properties=sort_properties,
            sort_ascending=sort_ascending,
            property_filter=property_filter,
            searchword=searchword,
        )
    ).parsed
