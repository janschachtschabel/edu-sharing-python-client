from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.get_recent_user_events_content_type import GetRecentUserEventsContentType
from ...models.get_recent_user_events_event_type_item import GetRecentUserEventsEventTypeItem
from ...models.search_parameters import SearchParameters
from ...models.search_result_event import SearchResultEvent
from ...types import UNSET, Response, Unset


def _get_kwargs(
    repository: str,
    *,
    body: SearchParameters | Unset = UNSET,
    event_type: list[GetRecentUserEventsEventTypeItem] | Unset = UNSET,
    content_type: GetRecentUserEventsContentType | Unset = UNSET,
    max_items: int | Unset = 25,
    skip_count: int | Unset = 0,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    json_event_type: list[str] | Unset = UNSET
    if not isinstance(event_type, Unset):
        json_event_type = []
        for event_type_item_data in event_type:
            event_type_item = event_type_item_data.value
            json_event_type.append(event_type_item)

    params["eventType"] = json_event_type

    json_content_type: str | Unset = UNSET
    if not isinstance(content_type, Unset):
        json_content_type = content_type.value

    params["contentType"] = json_content_type

    params["maxItems"] = max_items

    params["skipCount"] = skip_count

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/search/v1/user/recent/{repository}".format(
            repository=quote(str(repository), safe=""),
        ),
        "params": params,
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | SearchResultEvent | None:
    if response.status_code == 200:
        response_200 = SearchResultEvent.from_dict(response.json())

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
) -> Response[ErrorResponse | SearchResultEvent]:
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
    body: SearchParameters | Unset = UNSET,
    event_type: list[GetRecentUserEventsEventTypeItem] | Unset = UNSET,
    content_type: GetRecentUserEventsContentType | Unset = UNSET,
    max_items: int | Unset = 25,
    skip_count: int | Unset = 0,
) -> Response[ErrorResponse | SearchResultEvent]:
    """Get nodes with recent events for current user

    Args:
        repository (str):
        event_type (list[GetRecentUserEventsEventTypeItem] | Unset):
        content_type (GetRecentUserEventsContentType | Unset):
        max_items (int | Unset):  Default: 25.
        skip_count (int | Unset):  Default: 0.
        body (SearchParameters | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | SearchResultEvent]
    """

    kwargs = _get_kwargs(
        repository=repository,
        body=body,
        event_type=event_type,
        content_type=content_type,
        max_items=max_items,
        skip_count=skip_count,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repository: str,
    *,
    client: AuthenticatedClient | Client,
    body: SearchParameters | Unset = UNSET,
    event_type: list[GetRecentUserEventsEventTypeItem] | Unset = UNSET,
    content_type: GetRecentUserEventsContentType | Unset = UNSET,
    max_items: int | Unset = 25,
    skip_count: int | Unset = 0,
) -> ErrorResponse | SearchResultEvent | None:
    """Get nodes with recent events for current user

    Args:
        repository (str):
        event_type (list[GetRecentUserEventsEventTypeItem] | Unset):
        content_type (GetRecentUserEventsContentType | Unset):
        max_items (int | Unset):  Default: 25.
        skip_count (int | Unset):  Default: 0.
        body (SearchParameters | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | SearchResultEvent
    """

    return sync_detailed(
        repository=repository,
        client=client,
        body=body,
        event_type=event_type,
        content_type=content_type,
        max_items=max_items,
        skip_count=skip_count,
    ).parsed


async def asyncio_detailed(
    repository: str,
    *,
    client: AuthenticatedClient | Client,
    body: SearchParameters | Unset = UNSET,
    event_type: list[GetRecentUserEventsEventTypeItem] | Unset = UNSET,
    content_type: GetRecentUserEventsContentType | Unset = UNSET,
    max_items: int | Unset = 25,
    skip_count: int | Unset = 0,
) -> Response[ErrorResponse | SearchResultEvent]:
    """Get nodes with recent events for current user

    Args:
        repository (str):
        event_type (list[GetRecentUserEventsEventTypeItem] | Unset):
        content_type (GetRecentUserEventsContentType | Unset):
        max_items (int | Unset):  Default: 25.
        skip_count (int | Unset):  Default: 0.
        body (SearchParameters | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | SearchResultEvent]
    """

    kwargs = _get_kwargs(
        repository=repository,
        body=body,
        event_type=event_type,
        content_type=content_type,
        max_items=max_items,
        skip_count=skip_count,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    *,
    client: AuthenticatedClient | Client,
    body: SearchParameters | Unset = UNSET,
    event_type: list[GetRecentUserEventsEventTypeItem] | Unset = UNSET,
    content_type: GetRecentUserEventsContentType | Unset = UNSET,
    max_items: int | Unset = 25,
    skip_count: int | Unset = 0,
) -> ErrorResponse | SearchResultEvent | None:
    """Get nodes with recent events for current user

    Args:
        repository (str):
        event_type (list[GetRecentUserEventsEventTypeItem] | Unset):
        content_type (GetRecentUserEventsContentType | Unset):
        max_items (int | Unset):  Default: 25.
        skip_count (int | Unset):  Default: 0.
        body (SearchParameters | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | SearchResultEvent
    """

    return (
        await asyncio_detailed(
            repository=repository,
            client=client,
            body=body,
            event_type=event_type,
            content_type=content_type,
            max_items=max_items,
            skip_count=skip_count,
        )
    ).parsed
