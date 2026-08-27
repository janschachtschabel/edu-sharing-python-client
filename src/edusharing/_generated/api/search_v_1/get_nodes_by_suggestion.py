from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.get_nodes_by_suggestion_content_type import GetNodesBySuggestionContentType
from ...models.get_nodes_by_suggestion_status_item import GetNodesBySuggestionStatusItem
from ...models.get_nodes_by_suggestion_type_item import GetNodesBySuggestionTypeItem
from ...models.search_parameters import SearchParameters
from ...models.search_result_suggestion import SearchResultSuggestion
from ...types import UNSET, Response, Unset


def _get_kwargs(
    repository: str,
    *,
    body: SearchParameters | Unset = UNSET,
    status: list[GetNodesBySuggestionStatusItem] | Unset = UNSET,
    type_: list[GetNodesBySuggestionTypeItem] | Unset = UNSET,
    content_type: GetNodesBySuggestionContentType | Unset = UNSET,
    max_items: int | Unset = 25,
    skip_count: int | Unset = 0,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    json_status: list[str] | Unset = UNSET
    if not isinstance(status, Unset):
        json_status = []
        for status_item_data in status:
            status_item = status_item_data.value
            json_status.append(status_item)

    params["status"] = json_status

    json_type_: list[str] | Unset = UNSET
    if not isinstance(type_, Unset):
        json_type_ = []
        for type_item_data in type_:
            type_item = type_item_data.value
            json_type_.append(type_item)

    params["type"] = json_type_

    json_content_type: str | Unset = UNSET
    if not isinstance(content_type, Unset):
        json_content_type = content_type.value

    params["contentType"] = json_content_type

    params["maxItems"] = max_items

    params["skipCount"] = skip_count

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/search/v1/suggestions/{repository}".format(
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
) -> ErrorResponse | SearchResultSuggestion | None:
    if response.status_code == 200:
        response_200 = SearchResultSuggestion.from_dict(response.json())

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
) -> Response[ErrorResponse | SearchResultSuggestion]:
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
    status: list[GetNodesBySuggestionStatusItem] | Unset = UNSET,
    type_: list[GetNodesBySuggestionTypeItem] | Unset = UNSET,
    content_type: GetNodesBySuggestionContentType | Unset = UNSET,
    max_items: int | Unset = 25,
    skip_count: int | Unset = 0,
) -> Response[ErrorResponse | SearchResultSuggestion]:
    """Get nodes that have suggestions (requires write permissions on the individual nodes)

    Args:
        repository (str):
        status (list[GetNodesBySuggestionStatusItem] | Unset):
        type_ (list[GetNodesBySuggestionTypeItem] | Unset):
        content_type (GetNodesBySuggestionContentType | Unset):
        max_items (int | Unset):  Default: 25.
        skip_count (int | Unset):  Default: 0.
        body (SearchParameters | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | SearchResultSuggestion]
    """

    kwargs = _get_kwargs(
        repository=repository,
        body=body,
        status=status,
        type_=type_,
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
    status: list[GetNodesBySuggestionStatusItem] | Unset = UNSET,
    type_: list[GetNodesBySuggestionTypeItem] | Unset = UNSET,
    content_type: GetNodesBySuggestionContentType | Unset = UNSET,
    max_items: int | Unset = 25,
    skip_count: int | Unset = 0,
) -> ErrorResponse | SearchResultSuggestion | None:
    """Get nodes that have suggestions (requires write permissions on the individual nodes)

    Args:
        repository (str):
        status (list[GetNodesBySuggestionStatusItem] | Unset):
        type_ (list[GetNodesBySuggestionTypeItem] | Unset):
        content_type (GetNodesBySuggestionContentType | Unset):
        max_items (int | Unset):  Default: 25.
        skip_count (int | Unset):  Default: 0.
        body (SearchParameters | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | SearchResultSuggestion
    """

    return sync_detailed(
        repository=repository,
        client=client,
        body=body,
        status=status,
        type_=type_,
        content_type=content_type,
        max_items=max_items,
        skip_count=skip_count,
    ).parsed


async def asyncio_detailed(
    repository: str,
    *,
    client: AuthenticatedClient | Client,
    body: SearchParameters | Unset = UNSET,
    status: list[GetNodesBySuggestionStatusItem] | Unset = UNSET,
    type_: list[GetNodesBySuggestionTypeItem] | Unset = UNSET,
    content_type: GetNodesBySuggestionContentType | Unset = UNSET,
    max_items: int | Unset = 25,
    skip_count: int | Unset = 0,
) -> Response[ErrorResponse | SearchResultSuggestion]:
    """Get nodes that have suggestions (requires write permissions on the individual nodes)

    Args:
        repository (str):
        status (list[GetNodesBySuggestionStatusItem] | Unset):
        type_ (list[GetNodesBySuggestionTypeItem] | Unset):
        content_type (GetNodesBySuggestionContentType | Unset):
        max_items (int | Unset):  Default: 25.
        skip_count (int | Unset):  Default: 0.
        body (SearchParameters | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | SearchResultSuggestion]
    """

    kwargs = _get_kwargs(
        repository=repository,
        body=body,
        status=status,
        type_=type_,
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
    status: list[GetNodesBySuggestionStatusItem] | Unset = UNSET,
    type_: list[GetNodesBySuggestionTypeItem] | Unset = UNSET,
    content_type: GetNodesBySuggestionContentType | Unset = UNSET,
    max_items: int | Unset = 25,
    skip_count: int | Unset = 0,
) -> ErrorResponse | SearchResultSuggestion | None:
    """Get nodes that have suggestions (requires write permissions on the individual nodes)

    Args:
        repository (str):
        status (list[GetNodesBySuggestionStatusItem] | Unset):
        type_ (list[GetNodesBySuggestionTypeItem] | Unset):
        content_type (GetNodesBySuggestionContentType | Unset):
        max_items (int | Unset):  Default: 25.
        skip_count (int | Unset):  Default: 0.
        body (SearchParameters | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | SearchResultSuggestion
    """

    return (
        await asyncio_detailed(
            repository=repository,
            client=client,
            body=body,
            status=status,
            type_=type_,
            content_type=content_type,
            max_items=max_items,
            skip_count=skip_count,
        )
    ).parsed
