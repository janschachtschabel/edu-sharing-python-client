import datetime
from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.user_node_activity import UserNodeActivity
from ...types import UNSET, Response, Unset


def _get_kwargs(
    repository: str,
    *,
    after: datetime.datetime,
    to: datetime.datetime | Unset = UNSET,
    max_items: int | Unset = 100,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_after = after.isoformat()
    params["after"] = json_after

    json_to: str | Unset = UNSET
    if not isinstance(to, Unset):
        json_to = to.isoformat()
    params["to"] = json_to

    params["maxItems"] = max_items

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/tracking/v1/tracking/{repository}/allUserNodeActivities".format(
            repository=quote(str(repository), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | list[UserNodeActivity] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = UserNodeActivity.from_dict(response_200_item_data)

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
) -> Response[ErrorResponse | list[UserNodeActivity]]:
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
    after: datetime.datetime,
    to: datetime.datetime | Unset = UNSET,
    max_items: int | Unset = 100,
) -> Response[ErrorResponse | list[UserNodeActivity]]:
    """Get all user activities

     Returns a paginated list of all user activities after a specific date

    Args:
        repository (str):
        after (datetime.datetime):
        to (datetime.datetime | Unset):
        max_items (int | Unset):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | list[UserNodeActivity]]
    """

    kwargs = _get_kwargs(
        repository=repository,
        after=after,
        to=to,
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
    after: datetime.datetime,
    to: datetime.datetime | Unset = UNSET,
    max_items: int | Unset = 100,
) -> ErrorResponse | list[UserNodeActivity] | None:
    """Get all user activities

     Returns a paginated list of all user activities after a specific date

    Args:
        repository (str):
        after (datetime.datetime):
        to (datetime.datetime | Unset):
        max_items (int | Unset):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | list[UserNodeActivity]
    """

    return sync_detailed(
        repository=repository,
        client=client,
        after=after,
        to=to,
        max_items=max_items,
    ).parsed


async def asyncio_detailed(
    repository: str,
    *,
    client: AuthenticatedClient | Client,
    after: datetime.datetime,
    to: datetime.datetime | Unset = UNSET,
    max_items: int | Unset = 100,
) -> Response[ErrorResponse | list[UserNodeActivity]]:
    """Get all user activities

     Returns a paginated list of all user activities after a specific date

    Args:
        repository (str):
        after (datetime.datetime):
        to (datetime.datetime | Unset):
        max_items (int | Unset):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | list[UserNodeActivity]]
    """

    kwargs = _get_kwargs(
        repository=repository,
        after=after,
        to=to,
        max_items=max_items,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    *,
    client: AuthenticatedClient | Client,
    after: datetime.datetime,
    to: datetime.datetime | Unset = UNSET,
    max_items: int | Unset = 100,
) -> ErrorResponse | list[UserNodeActivity] | None:
    """Get all user activities

     Returns a paginated list of all user activities after a specific date

    Args:
        repository (str):
        after (datetime.datetime):
        to (datetime.datetime | Unset):
        max_items (int | Unset):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | list[UserNodeActivity]
    """

    return (
        await asyncio_detailed(
            repository=repository,
            client=client,
            after=after,
            to=to,
            max_items=max_items,
        )
    ).parsed
