from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.statistics_global import StatisticsGlobal
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    group: str | Unset = UNSET,
    sub_group: list[str] | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["group"] = group

    json_sub_group: list[str] | Unset = UNSET
    if not isinstance(sub_group, Unset):
        json_sub_group = sub_group

    params["subGroup"] = json_sub_group

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/statistic/v1/public",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | StatisticsGlobal | None:
    if response.status_code == 200:
        response_200 = StatisticsGlobal.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = ErrorResponse.from_dict(response.json())

        return response_401

    if response.status_code == 500:
        response_500 = ErrorResponse.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ErrorResponse | StatisticsGlobal]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    group: str | Unset = UNSET,
    sub_group: list[str] | Unset = UNSET,
) -> Response[ErrorResponse | StatisticsGlobal]:
    """Get stats.

     Get global statistics for this repository.

    Args:
        group (str | Unset):
        sub_group (list[str] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | StatisticsGlobal]
    """

    kwargs = _get_kwargs(
        group=group,
        sub_group=sub_group,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    group: str | Unset = UNSET,
    sub_group: list[str] | Unset = UNSET,
) -> ErrorResponse | StatisticsGlobal | None:
    """Get stats.

     Get global statistics for this repository.

    Args:
        group (str | Unset):
        sub_group (list[str] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | StatisticsGlobal
    """

    return sync_detailed(
        client=client,
        group=group,
        sub_group=sub_group,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    group: str | Unset = UNSET,
    sub_group: list[str] | Unset = UNSET,
) -> Response[ErrorResponse | StatisticsGlobal]:
    """Get stats.

     Get global statistics for this repository.

    Args:
        group (str | Unset):
        sub_group (list[str] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | StatisticsGlobal]
    """

    kwargs = _get_kwargs(
        group=group,
        sub_group=sub_group,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    group: str | Unset = UNSET,
    sub_group: list[str] | Unset = UNSET,
) -> ErrorResponse | StatisticsGlobal | None:
    """Get stats.

     Get global statistics for this repository.

    Args:
        group (str | Unset):
        sub_group (list[str] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | StatisticsGlobal
    """

    return (
        await asyncio_detailed(
            client=client,
            group=group,
            sub_group=sub_group,
        )
    ).parsed
