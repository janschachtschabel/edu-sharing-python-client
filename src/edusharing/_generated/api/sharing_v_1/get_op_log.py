import datetime
from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.share_info_oplog import ShareInfoOplog
from ...types import UNSET, Response, Unset


def _get_kwargs(
    repository: str,
    *,
    op_log_id: int | Unset = UNSET,
    after: datetime.datetime | Unset = UNSET,
    until: datetime.datetime | Unset = UNSET,
    max_items: int | Unset = 500,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["opLogId"] = op_log_id

    json_after: str | Unset = UNSET
    if not isinstance(after, Unset):
        json_after = after.isoformat()
    params["after"] = json_after

    json_until: str | Unset = UNSET
    if not isinstance(until, Unset):
        json_until = until.isoformat()
    params["until"] = json_until

    params["maxItems"] = max_items

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/sharing/v1/share/{repository}/oplog".format(
            repository=quote(str(repository), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | list[ShareInfoOplog] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = ShareInfoOplog.from_dict(response_200_item_data)

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
) -> Response[ErrorResponse | list[ShareInfoOplog]]:
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
    op_log_id: int | Unset = UNSET,
    after: datetime.datetime | Unset = UNSET,
    until: datetime.datetime | Unset = UNSET,
    max_items: int | Unset = 500,
) -> Response[ErrorResponse | list[ShareInfoOplog]]:
    """Get the operation log of share info

    Args:
        repository (str):
        op_log_id (int | Unset):
        after (datetime.datetime | Unset):
        until (datetime.datetime | Unset):
        max_items (int | Unset):  Default: 500.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | list[ShareInfoOplog]]
    """

    kwargs = _get_kwargs(
        repository=repository,
        op_log_id=op_log_id,
        after=after,
        until=until,
        max_items=max_items,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repository: str,
    *,
    client: AuthenticatedClient | Client,
    op_log_id: int | Unset = UNSET,
    after: datetime.datetime | Unset = UNSET,
    until: datetime.datetime | Unset = UNSET,
    max_items: int | Unset = 500,
) -> ErrorResponse | list[ShareInfoOplog] | None:
    """Get the operation log of share info

    Args:
        repository (str):
        op_log_id (int | Unset):
        after (datetime.datetime | Unset):
        until (datetime.datetime | Unset):
        max_items (int | Unset):  Default: 500.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | list[ShareInfoOplog]
    """

    return sync_detailed(
        repository=repository,
        client=client,
        op_log_id=op_log_id,
        after=after,
        until=until,
        max_items=max_items,
    ).parsed


async def asyncio_detailed(
    repository: str,
    *,
    client: AuthenticatedClient | Client,
    op_log_id: int | Unset = UNSET,
    after: datetime.datetime | Unset = UNSET,
    until: datetime.datetime | Unset = UNSET,
    max_items: int | Unset = 500,
) -> Response[ErrorResponse | list[ShareInfoOplog]]:
    """Get the operation log of share info

    Args:
        repository (str):
        op_log_id (int | Unset):
        after (datetime.datetime | Unset):
        until (datetime.datetime | Unset):
        max_items (int | Unset):  Default: 500.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | list[ShareInfoOplog]]
    """

    kwargs = _get_kwargs(
        repository=repository,
        op_log_id=op_log_id,
        after=after,
        until=until,
        max_items=max_items,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    *,
    client: AuthenticatedClient | Client,
    op_log_id: int | Unset = UNSET,
    after: datetime.datetime | Unset = UNSET,
    until: datetime.datetime | Unset = UNSET,
    max_items: int | Unset = 500,
) -> ErrorResponse | list[ShareInfoOplog] | None:
    """Get the operation log of share info

    Args:
        repository (str):
        op_log_id (int | Unset):
        after (datetime.datetime | Unset):
        until (datetime.datetime | Unset):
        max_items (int | Unset):  Default: 500.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | list[ShareInfoOplog]
    """

    return (
        await asyncio_detailed(
            repository=repository,
            client=client,
            op_log_id=op_log_id,
            after=after,
            until=until,
            max_items=max_items,
        )
    ).parsed
