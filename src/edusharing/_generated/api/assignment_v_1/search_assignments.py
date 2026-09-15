from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.assignment_search_result import AssignmentSearchResult
from ...models.error_response import ErrorResponse
from ...models.search_parameters import SearchParameters
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: SearchParameters | Unset = UNSET,
    max_items: int | Unset = 25,
    skip_count: int | Unset = 0,
    sort_properties: list[str] | Unset = UNSET,
    sort_ascending: list[bool] | Unset = UNSET,
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

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/assignment/v1/search",
        "params": params,
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> AssignmentSearchResult | ErrorResponse | None:
    if response.status_code == 200:
        response_200 = AssignmentSearchResult.from_dict(response.json())

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
) -> Response[AssignmentSearchResult | ErrorResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: SearchParameters | Unset = UNSET,
    max_items: int | Unset = 25,
    skip_count: int | Unset = 0,
    sort_properties: list[str] | Unset = UNSET,
    sort_ascending: list[bool] | Unset = UNSET,
) -> Response[AssignmentSearchResult | ErrorResponse]:
    """Search assignments

     Searches for assignments.

    Args:
        max_items (int | Unset):  Default: 25.
        skip_count (int | Unset):  Default: 0.
        sort_properties (list[str] | Unset):
        sort_ascending (list[bool] | Unset):
        body (SearchParameters | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AssignmentSearchResult | ErrorResponse]
    """

    kwargs = _get_kwargs(
        body=body,
        max_items=max_items,
        skip_count=skip_count,
        sort_properties=sort_properties,
        sort_ascending=sort_ascending,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: SearchParameters | Unset = UNSET,
    max_items: int | Unset = 25,
    skip_count: int | Unset = 0,
    sort_properties: list[str] | Unset = UNSET,
    sort_ascending: list[bool] | Unset = UNSET,
) -> AssignmentSearchResult | ErrorResponse | None:
    """Search assignments

     Searches for assignments.

    Args:
        max_items (int | Unset):  Default: 25.
        skip_count (int | Unset):  Default: 0.
        sort_properties (list[str] | Unset):
        sort_ascending (list[bool] | Unset):
        body (SearchParameters | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AssignmentSearchResult | ErrorResponse
    """

    return sync_detailed(
        client=client,
        body=body,
        max_items=max_items,
        skip_count=skip_count,
        sort_properties=sort_properties,
        sort_ascending=sort_ascending,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: SearchParameters | Unset = UNSET,
    max_items: int | Unset = 25,
    skip_count: int | Unset = 0,
    sort_properties: list[str] | Unset = UNSET,
    sort_ascending: list[bool] | Unset = UNSET,
) -> Response[AssignmentSearchResult | ErrorResponse]:
    """Search assignments

     Searches for assignments.

    Args:
        max_items (int | Unset):  Default: 25.
        skip_count (int | Unset):  Default: 0.
        sort_properties (list[str] | Unset):
        sort_ascending (list[bool] | Unset):
        body (SearchParameters | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AssignmentSearchResult | ErrorResponse]
    """

    kwargs = _get_kwargs(
        body=body,
        max_items=max_items,
        skip_count=skip_count,
        sort_properties=sort_properties,
        sort_ascending=sort_ascending,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: SearchParameters | Unset = UNSET,
    max_items: int | Unset = 25,
    skip_count: int | Unset = 0,
    sort_properties: list[str] | Unset = UNSET,
    sort_ascending: list[bool] | Unset = UNSET,
) -> AssignmentSearchResult | ErrorResponse | None:
    """Search assignments

     Searches for assignments.

    Args:
        max_items (int | Unset):  Default: 25.
        skip_count (int | Unset):  Default: 0.
        sort_properties (list[str] | Unset):
        sort_ascending (list[bool] | Unset):
        body (SearchParameters | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AssignmentSearchResult | ErrorResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            max_items=max_items,
            skip_count=skip_count,
            sort_properties=sort_properties,
            sort_ascending=sort_ascending,
        )
    ).parsed
