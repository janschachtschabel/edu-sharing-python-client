from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.search_by_property_combine_mode import SearchByPropertyCombineMode
from ...models.search_by_property_content_type import SearchByPropertyContentType
from ...models.search_result_node import SearchResultNode
from ...types import UNSET, Response, Unset


def _get_kwargs(
    repository: str,
    *,
    content_type: SearchByPropertyContentType | Unset = UNSET,
    combine_mode: SearchByPropertyCombineMode | Unset = UNSET,
    property_: list[str] | Unset = UNSET,
    value: list[str] | Unset = UNSET,
    comparator: list[str] | Unset = UNSET,
    max_items: int | Unset = 10,
    skip_count: int | Unset = 0,
    sort_properties: list[str] | Unset = UNSET,
    sort_ascending: list[bool] | Unset = UNSET,
    property_filter: list[str] | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_content_type: str | Unset = UNSET
    if not isinstance(content_type, Unset):
        json_content_type = content_type.value

    params["contentType"] = json_content_type

    json_combine_mode: str | Unset = UNSET
    if not isinstance(combine_mode, Unset):
        json_combine_mode = combine_mode.value

    params["combineMode"] = json_combine_mode

    json_property_: list[str] | Unset = UNSET
    if not isinstance(property_, Unset):
        json_property_ = property_

    params["property"] = json_property_

    json_value: list[str] | Unset = UNSET
    if not isinstance(value, Unset):
        json_value = value

    params["value"] = json_value

    json_comparator: list[str] | Unset = UNSET
    if not isinstance(comparator, Unset):
        json_comparator = comparator

    params["comparator"] = json_comparator

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

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/search/v1/custom/{repository}".format(
            repository=quote(str(repository), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | SearchResultNode | None:
    if response.status_code == 200:
        response_200 = SearchResultNode.from_dict(response.json())

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
) -> Response[ErrorResponse | SearchResultNode]:
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
    content_type: SearchByPropertyContentType | Unset = UNSET,
    combine_mode: SearchByPropertyCombineMode | Unset = UNSET,
    property_: list[str] | Unset = UNSET,
    value: list[str] | Unset = UNSET,
    comparator: list[str] | Unset = UNSET,
    max_items: int | Unset = 10,
    skip_count: int | Unset = 0,
    sort_properties: list[str] | Unset = UNSET,
    sort_ascending: list[bool] | Unset = UNSET,
    property_filter: list[str] | Unset = UNSET,
) -> Response[ErrorResponse | SearchResultNode]:
    """Search for custom properties with custom values

     e.g. property=cm:name, value:*Test*

    Args:
        repository (str):
        content_type (SearchByPropertyContentType | Unset):
        combine_mode (SearchByPropertyCombineMode | Unset):
        property_ (list[str] | Unset):
        value (list[str] | Unset):
        comparator (list[str] | Unset):
        max_items (int | Unset):  Default: 10.
        skip_count (int | Unset):  Default: 0.
        sort_properties (list[str] | Unset):
        sort_ascending (list[bool] | Unset):
        property_filter (list[str] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | SearchResultNode]
    """

    kwargs = _get_kwargs(
        repository=repository,
        content_type=content_type,
        combine_mode=combine_mode,
        property_=property_,
        value=value,
        comparator=comparator,
        max_items=max_items,
        skip_count=skip_count,
        sort_properties=sort_properties,
        sort_ascending=sort_ascending,
        property_filter=property_filter,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repository: str,
    *,
    client: AuthenticatedClient | Client,
    content_type: SearchByPropertyContentType | Unset = UNSET,
    combine_mode: SearchByPropertyCombineMode | Unset = UNSET,
    property_: list[str] | Unset = UNSET,
    value: list[str] | Unset = UNSET,
    comparator: list[str] | Unset = UNSET,
    max_items: int | Unset = 10,
    skip_count: int | Unset = 0,
    sort_properties: list[str] | Unset = UNSET,
    sort_ascending: list[bool] | Unset = UNSET,
    property_filter: list[str] | Unset = UNSET,
) -> ErrorResponse | SearchResultNode | None:
    """Search for custom properties with custom values

     e.g. property=cm:name, value:*Test*

    Args:
        repository (str):
        content_type (SearchByPropertyContentType | Unset):
        combine_mode (SearchByPropertyCombineMode | Unset):
        property_ (list[str] | Unset):
        value (list[str] | Unset):
        comparator (list[str] | Unset):
        max_items (int | Unset):  Default: 10.
        skip_count (int | Unset):  Default: 0.
        sort_properties (list[str] | Unset):
        sort_ascending (list[bool] | Unset):
        property_filter (list[str] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | SearchResultNode
    """

    return sync_detailed(
        repository=repository,
        client=client,
        content_type=content_type,
        combine_mode=combine_mode,
        property_=property_,
        value=value,
        comparator=comparator,
        max_items=max_items,
        skip_count=skip_count,
        sort_properties=sort_properties,
        sort_ascending=sort_ascending,
        property_filter=property_filter,
    ).parsed


async def asyncio_detailed(
    repository: str,
    *,
    client: AuthenticatedClient | Client,
    content_type: SearchByPropertyContentType | Unset = UNSET,
    combine_mode: SearchByPropertyCombineMode | Unset = UNSET,
    property_: list[str] | Unset = UNSET,
    value: list[str] | Unset = UNSET,
    comparator: list[str] | Unset = UNSET,
    max_items: int | Unset = 10,
    skip_count: int | Unset = 0,
    sort_properties: list[str] | Unset = UNSET,
    sort_ascending: list[bool] | Unset = UNSET,
    property_filter: list[str] | Unset = UNSET,
) -> Response[ErrorResponse | SearchResultNode]:
    """Search for custom properties with custom values

     e.g. property=cm:name, value:*Test*

    Args:
        repository (str):
        content_type (SearchByPropertyContentType | Unset):
        combine_mode (SearchByPropertyCombineMode | Unset):
        property_ (list[str] | Unset):
        value (list[str] | Unset):
        comparator (list[str] | Unset):
        max_items (int | Unset):  Default: 10.
        skip_count (int | Unset):  Default: 0.
        sort_properties (list[str] | Unset):
        sort_ascending (list[bool] | Unset):
        property_filter (list[str] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | SearchResultNode]
    """

    kwargs = _get_kwargs(
        repository=repository,
        content_type=content_type,
        combine_mode=combine_mode,
        property_=property_,
        value=value,
        comparator=comparator,
        max_items=max_items,
        skip_count=skip_count,
        sort_properties=sort_properties,
        sort_ascending=sort_ascending,
        property_filter=property_filter,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    *,
    client: AuthenticatedClient | Client,
    content_type: SearchByPropertyContentType | Unset = UNSET,
    combine_mode: SearchByPropertyCombineMode | Unset = UNSET,
    property_: list[str] | Unset = UNSET,
    value: list[str] | Unset = UNSET,
    comparator: list[str] | Unset = UNSET,
    max_items: int | Unset = 10,
    skip_count: int | Unset = 0,
    sort_properties: list[str] | Unset = UNSET,
    sort_ascending: list[bool] | Unset = UNSET,
    property_filter: list[str] | Unset = UNSET,
) -> ErrorResponse | SearchResultNode | None:
    """Search for custom properties with custom values

     e.g. property=cm:name, value:*Test*

    Args:
        repository (str):
        content_type (SearchByPropertyContentType | Unset):
        combine_mode (SearchByPropertyCombineMode | Unset):
        property_ (list[str] | Unset):
        value (list[str] | Unset):
        comparator (list[str] | Unset):
        max_items (int | Unset):  Default: 10.
        skip_count (int | Unset):  Default: 0.
        sort_properties (list[str] | Unset):
        sort_ascending (list[bool] | Unset):
        property_filter (list[str] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | SearchResultNode
    """

    return (
        await asyncio_detailed(
            repository=repository,
            client=client,
            content_type=content_type,
            combine_mode=combine_mode,
            property_=property_,
            value=value,
            comparator=comparator,
            max_items=max_items,
            skip_count=skip_count,
            sort_properties=sort_properties,
            sort_ascending=sort_ascending,
            property_filter=property_filter,
        )
    ).parsed
