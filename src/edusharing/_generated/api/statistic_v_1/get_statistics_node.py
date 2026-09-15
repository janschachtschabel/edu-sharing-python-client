from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.get_statistics_node_body import GetStatisticsNodeBody
from ...models.get_statistics_node_grouping import GetStatisticsNodeGrouping
from ...models.tracking_node import TrackingNode
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: GetStatisticsNodeBody | Unset = UNSET,
    grouping: GetStatisticsNodeGrouping,
    date_from: int,
    date_to: int,
    mediacenter: str | Unset = UNSET,
    additional_fields: list[str] | Unset = UNSET,
    group_field: list[str] | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    json_grouping = grouping.value
    params["grouping"] = json_grouping

    params["dateFrom"] = date_from

    params["dateTo"] = date_to

    params["mediacenter"] = mediacenter

    json_additional_fields: list[str] | Unset = UNSET
    if not isinstance(additional_fields, Unset):
        json_additional_fields = additional_fields

    params["additionalFields"] = json_additional_fields

    json_group_field: list[str] | Unset = UNSET
    if not isinstance(group_field, Unset):
        json_group_field = group_field

    params["groupField"] = json_group_field

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/statistic/v1/statistics/nodes",
        "params": params,
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

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
    body: GetStatisticsNodeBody | Unset = UNSET,
    grouping: GetStatisticsNodeGrouping,
    date_from: int,
    date_to: int,
    mediacenter: str | Unset = UNSET,
    additional_fields: list[str] | Unset = UNSET,
    group_field: list[str] | Unset = UNSET,
) -> Response[ErrorResponse | list[TrackingNode]]:
    """get statistics for node actions

     requires either toolpermission TOOLPERMISSION_GLOBAL_STATISTICS_NODES for global stats or to be
    admin of the requested mediacenter

    Args:
        grouping (GetStatisticsNodeGrouping):
        date_from (int):
        date_to (int):
        mediacenter (str | Unset):
        additional_fields (list[str] | Unset):
        group_field (list[str] | Unset):
        body (GetStatisticsNodeBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | list[TrackingNode]]
    """

    kwargs = _get_kwargs(
        body=body,
        grouping=grouping,
        date_from=date_from,
        date_to=date_to,
        mediacenter=mediacenter,
        additional_fields=additional_fields,
        group_field=group_field,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: GetStatisticsNodeBody | Unset = UNSET,
    grouping: GetStatisticsNodeGrouping,
    date_from: int,
    date_to: int,
    mediacenter: str | Unset = UNSET,
    additional_fields: list[str] | Unset = UNSET,
    group_field: list[str] | Unset = UNSET,
) -> ErrorResponse | list[TrackingNode] | None:
    """get statistics for node actions

     requires either toolpermission TOOLPERMISSION_GLOBAL_STATISTICS_NODES for global stats or to be
    admin of the requested mediacenter

    Args:
        grouping (GetStatisticsNodeGrouping):
        date_from (int):
        date_to (int):
        mediacenter (str | Unset):
        additional_fields (list[str] | Unset):
        group_field (list[str] | Unset):
        body (GetStatisticsNodeBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | list[TrackingNode]
    """

    return sync_detailed(
        client=client,
        body=body,
        grouping=grouping,
        date_from=date_from,
        date_to=date_to,
        mediacenter=mediacenter,
        additional_fields=additional_fields,
        group_field=group_field,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: GetStatisticsNodeBody | Unset = UNSET,
    grouping: GetStatisticsNodeGrouping,
    date_from: int,
    date_to: int,
    mediacenter: str | Unset = UNSET,
    additional_fields: list[str] | Unset = UNSET,
    group_field: list[str] | Unset = UNSET,
) -> Response[ErrorResponse | list[TrackingNode]]:
    """get statistics for node actions

     requires either toolpermission TOOLPERMISSION_GLOBAL_STATISTICS_NODES for global stats or to be
    admin of the requested mediacenter

    Args:
        grouping (GetStatisticsNodeGrouping):
        date_from (int):
        date_to (int):
        mediacenter (str | Unset):
        additional_fields (list[str] | Unset):
        group_field (list[str] | Unset):
        body (GetStatisticsNodeBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | list[TrackingNode]]
    """

    kwargs = _get_kwargs(
        body=body,
        grouping=grouping,
        date_from=date_from,
        date_to=date_to,
        mediacenter=mediacenter,
        additional_fields=additional_fields,
        group_field=group_field,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: GetStatisticsNodeBody | Unset = UNSET,
    grouping: GetStatisticsNodeGrouping,
    date_from: int,
    date_to: int,
    mediacenter: str | Unset = UNSET,
    additional_fields: list[str] | Unset = UNSET,
    group_field: list[str] | Unset = UNSET,
) -> ErrorResponse | list[TrackingNode] | None:
    """get statistics for node actions

     requires either toolpermission TOOLPERMISSION_GLOBAL_STATISTICS_NODES for global stats or to be
    admin of the requested mediacenter

    Args:
        grouping (GetStatisticsNodeGrouping):
        date_from (int):
        date_to (int):
        mediacenter (str | Unset):
        additional_fields (list[str] | Unset):
        group_field (list[str] | Unset):
        body (GetStatisticsNodeBody | Unset):

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
            grouping=grouping,
            date_from=date_from,
            date_to=date_to,
            mediacenter=mediacenter,
            additional_fields=additional_fields,
            group_field=group_field,
        )
    ).parsed
