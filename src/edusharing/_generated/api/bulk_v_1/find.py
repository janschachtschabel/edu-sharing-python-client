from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.bulk_run import BulkRun
from ...models.error_response import ErrorResponse
from ...models.find_filter_by_sate import FindFilterBySate
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    replicationsource: str,
    filter_by_sate: FindFilterBySate | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["replicationsource"] = replicationsource

    json_filter_by_sate: str | Unset = UNSET
    if not isinstance(filter_by_sate, Unset):
        json_filter_by_sate = filter_by_sate.value

    params["filterBySate"] = json_filter_by_sate

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/bulk/v1/runs",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | list[BulkRun] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = BulkRun.from_dict(response_200_item_data)

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
) -> Response[ErrorResponse | list[BulkRun]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    replicationsource: str,
    filter_by_sate: FindFilterBySate | Unset = UNSET,
) -> Response[ErrorResponse | list[BulkRun]]:
    """get imports from new runs

     Gets a list of runs from this crawler (by day) and info about the state of this run

    Args:
        replicationsource (str):
        filter_by_sate (FindFilterBySate | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | list[BulkRun]]
    """

    kwargs = _get_kwargs(
        replicationsource=replicationsource,
        filter_by_sate=filter_by_sate,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    replicationsource: str,
    filter_by_sate: FindFilterBySate | Unset = UNSET,
) -> ErrorResponse | list[BulkRun] | None:
    """get imports from new runs

     Gets a list of runs from this crawler (by day) and info about the state of this run

    Args:
        replicationsource (str):
        filter_by_sate (FindFilterBySate | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | list[BulkRun]
    """

    return sync_detailed(
        client=client,
        replicationsource=replicationsource,
        filter_by_sate=filter_by_sate,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    replicationsource: str,
    filter_by_sate: FindFilterBySate | Unset = UNSET,
) -> Response[ErrorResponse | list[BulkRun]]:
    """get imports from new runs

     Gets a list of runs from this crawler (by day) and info about the state of this run

    Args:
        replicationsource (str):
        filter_by_sate (FindFilterBySate | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | list[BulkRun]]
    """

    kwargs = _get_kwargs(
        replicationsource=replicationsource,
        filter_by_sate=filter_by_sate,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    replicationsource: str,
    filter_by_sate: FindFilterBySate | Unset = UNSET,
) -> ErrorResponse | list[BulkRun] | None:
    """get imports from new runs

     Gets a list of runs from this crawler (by day) and info about the state of this run

    Args:
        replicationsource (str):
        filter_by_sate (FindFilterBySate | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | list[BulkRun]
    """

    return (
        await asyncio_detailed(
            client=client,
            replicationsource=replicationsource,
            filter_by_sate=filter_by_sate,
        )
    ).parsed
