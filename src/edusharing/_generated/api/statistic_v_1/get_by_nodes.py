import datetime
from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.get_by_nodes_content_type import GetByNodesContentType
from ...models.tracking_node import TrackingNode
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: list[str] | Unset = UNSET,
    date_from: datetime.datetime,
    date_to: datetime.datetime,
    max_results: int,
    published: bool | Unset = UNSET,
    content_type: GetByNodesContentType | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    json_date_from = date_from.isoformat()
    params["dateFrom"] = json_date_from

    json_date_to = date_to.isoformat()
    params["dateTo"] = json_date_to

    params["maxResults"] = max_results

    params["published"] = published

    json_content_type: str | Unset = UNSET
    if not isinstance(content_type, Unset):
        json_content_type = content_type.value

    params["contentType"] = json_content_type

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/statistic/v1/statistics/nodes/range",
        "params": params,
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | list[TrackingNode] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = TrackingNode.from_dict(response_200_item_data)

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

    if response.status_code == 500:
        response_500 = ErrorResponse.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ErrorResponse | list[TrackingNode]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: list[str] | Unset = UNSET,
    date_from: datetime.datetime,
    date_to: datetime.datetime,
    max_results: int,
    published: bool | Unset = UNSET,
    content_type: GetByNodesContentType | Unset = UNSET,
) -> Response[ErrorResponse | list[TrackingNode]]:
    """get statistics for node actions for the given nodes

     requires toolpermission TOOLPERMISSION_SELECTIVE_STATISTICS_NODES

    Args:
        date_from (datetime.datetime):
        date_to (datetime.datetime):
        max_results (int):
        published (bool | Unset):
        content_type (GetByNodesContentType | Unset):
        body (list[str] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | list[TrackingNode]]
    """

    kwargs = _get_kwargs(
        body=body,
        date_from=date_from,
        date_to=date_to,
        max_results=max_results,
        published=published,
        content_type=content_type,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: list[str] | Unset = UNSET,
    date_from: datetime.datetime,
    date_to: datetime.datetime,
    max_results: int,
    published: bool | Unset = UNSET,
    content_type: GetByNodesContentType | Unset = UNSET,
) -> ErrorResponse | list[TrackingNode] | None:
    """get statistics for node actions for the given nodes

     requires toolpermission TOOLPERMISSION_SELECTIVE_STATISTICS_NODES

    Args:
        date_from (datetime.datetime):
        date_to (datetime.datetime):
        max_results (int):
        published (bool | Unset):
        content_type (GetByNodesContentType | Unset):
        body (list[str] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | list[TrackingNode]
    """

    return sync_detailed(
        client=client,
        body=body,
        date_from=date_from,
        date_to=date_to,
        max_results=max_results,
        published=published,
        content_type=content_type,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: list[str] | Unset = UNSET,
    date_from: datetime.datetime,
    date_to: datetime.datetime,
    max_results: int,
    published: bool | Unset = UNSET,
    content_type: GetByNodesContentType | Unset = UNSET,
) -> Response[ErrorResponse | list[TrackingNode]]:
    """get statistics for node actions for the given nodes

     requires toolpermission TOOLPERMISSION_SELECTIVE_STATISTICS_NODES

    Args:
        date_from (datetime.datetime):
        date_to (datetime.datetime):
        max_results (int):
        published (bool | Unset):
        content_type (GetByNodesContentType | Unset):
        body (list[str] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | list[TrackingNode]]
    """

    kwargs = _get_kwargs(
        body=body,
        date_from=date_from,
        date_to=date_to,
        max_results=max_results,
        published=published,
        content_type=content_type,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: list[str] | Unset = UNSET,
    date_from: datetime.datetime,
    date_to: datetime.datetime,
    max_results: int,
    published: bool | Unset = UNSET,
    content_type: GetByNodesContentType | Unset = UNSET,
) -> ErrorResponse | list[TrackingNode] | None:
    """get statistics for node actions for the given nodes

     requires toolpermission TOOLPERMISSION_SELECTIVE_STATISTICS_NODES

    Args:
        date_from (datetime.datetime):
        date_to (datetime.datetime):
        max_results (int):
        published (bool | Unset):
        content_type (GetByNodesContentType | Unset):
        body (list[str] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | list[TrackingNode]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            date_from=date_from,
            date_to=date_to,
            max_results=max_results,
            published=published,
            content_type=content_type,
        )
    ).parsed
