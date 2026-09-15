from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: list[list[str]] | Unset = UNSET,
    date_from: int,
    date_to: int,
    mediacenter: str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["dateFrom"] = date_from

    params["dateTo"] = date_to

    params["mediacenter"] = mediacenter

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/statistic/v1/statistics/nodes/complete",
        "params": params,
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = []
        for body_item_data in body:
            body_item = body_item_data

            _kwargs["json"].append(body_item)

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | ErrorResponse | None:
    if response.status_code == 200:
        response_200 = cast(Any, None)
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
) -> Response[Any | ErrorResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: list[list[str]] | Unset = UNSET,
    date_from: int,
    date_to: int,
    mediacenter: str | Unset = UNSET,
) -> Response[Any | ErrorResponse]:
    """Schedules a asynchronous job to retrieve statistics for all node actions. The result will be added
    to your inbox in form of an csv.

     requires either toolpermission TOOLPERMISSION_GLOBAL_STATISTICS_NODES for global stats or to be
    admin of the requested mediacenter

    Args:
        date_from (int):
        date_to (int):
        mediacenter (str | Unset):
        body (list[list[str]] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ErrorResponse]
    """

    kwargs = _get_kwargs(
        body=body,
        date_from=date_from,
        date_to=date_to,
        mediacenter=mediacenter,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: list[list[str]] | Unset = UNSET,
    date_from: int,
    date_to: int,
    mediacenter: str | Unset = UNSET,
) -> Any | ErrorResponse | None:
    """Schedules a asynchronous job to retrieve statistics for all node actions. The result will be added
    to your inbox in form of an csv.

     requires either toolpermission TOOLPERMISSION_GLOBAL_STATISTICS_NODES for global stats or to be
    admin of the requested mediacenter

    Args:
        date_from (int):
        date_to (int):
        mediacenter (str | Unset):
        body (list[list[str]] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ErrorResponse
    """

    return sync_detailed(
        client=client,
        body=body,
        date_from=date_from,
        date_to=date_to,
        mediacenter=mediacenter,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: list[list[str]] | Unset = UNSET,
    date_from: int,
    date_to: int,
    mediacenter: str | Unset = UNSET,
) -> Response[Any | ErrorResponse]:
    """Schedules a asynchronous job to retrieve statistics for all node actions. The result will be added
    to your inbox in form of an csv.

     requires either toolpermission TOOLPERMISSION_GLOBAL_STATISTICS_NODES for global stats or to be
    admin of the requested mediacenter

    Args:
        date_from (int):
        date_to (int):
        mediacenter (str | Unset):
        body (list[list[str]] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ErrorResponse]
    """

    kwargs = _get_kwargs(
        body=body,
        date_from=date_from,
        date_to=date_to,
        mediacenter=mediacenter,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: list[list[str]] | Unset = UNSET,
    date_from: int,
    date_to: int,
    mediacenter: str | Unset = UNSET,
) -> Any | ErrorResponse | None:
    """Schedules a asynchronous job to retrieve statistics for all node actions. The result will be added
    to your inbox in form of an csv.

     requires either toolpermission TOOLPERMISSION_GLOBAL_STATISTICS_NODES for global stats or to be
    admin of the requested mediacenter

    Args:
        date_from (int):
        date_to (int):
        mediacenter (str | Unset):
        body (list[list[str]] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ErrorResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            date_from=date_from,
            date_to=date_to,
            mediacenter=mediacenter,
        )
    ).parsed
