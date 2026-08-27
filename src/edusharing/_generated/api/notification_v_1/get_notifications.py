from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_notifications_status_item import GetNotificationsStatusItem
from ...models.notification_response_page import NotificationResponsePage
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    receiver_id: str | Unset = "-me-",
    status: list[GetNotificationsStatusItem] | Unset = UNSET,
    page: int | Unset = 0,
    size: int | Unset = 25,
    sort: list[str] | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["receiverId"] = receiver_id

    json_status: list[str] | Unset = UNSET
    if not isinstance(status, Unset):
        json_status = []
        for status_item_data in status:
            status_item = status_item_data.value
            json_status.append(status_item)

    params["status"] = json_status

    params["page"] = page

    params["size"] = size

    json_sort: list[str] | Unset = UNSET
    if not isinstance(sort, Unset):
        json_sort = sort

    params["sort"] = json_sort

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/notification/v1/notifications",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> NotificationResponsePage | None:
    if response.status_code == 200:
        response_200 = NotificationResponsePage.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[NotificationResponsePage]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    receiver_id: str | Unset = "-me-",
    status: list[GetNotificationsStatusItem] | Unset = UNSET,
    page: int | Unset = 0,
    size: int | Unset = 25,
    sort: list[str] | Unset = UNSET,
) -> Response[NotificationResponsePage]:
    """Retrieve stored notification, filtered by receiver and status

    Args:
        receiver_id (str | Unset):  Default: '-me-'.
        status (list[GetNotificationsStatusItem] | Unset):
        page (int | Unset):  Default: 0.
        size (int | Unset):  Default: 25.
        sort (list[str] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[NotificationResponsePage]
    """

    kwargs = _get_kwargs(
        receiver_id=receiver_id,
        status=status,
        page=page,
        size=size,
        sort=sort,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    receiver_id: str | Unset = "-me-",
    status: list[GetNotificationsStatusItem] | Unset = UNSET,
    page: int | Unset = 0,
    size: int | Unset = 25,
    sort: list[str] | Unset = UNSET,
) -> NotificationResponsePage | None:
    """Retrieve stored notification, filtered by receiver and status

    Args:
        receiver_id (str | Unset):  Default: '-me-'.
        status (list[GetNotificationsStatusItem] | Unset):
        page (int | Unset):  Default: 0.
        size (int | Unset):  Default: 25.
        sort (list[str] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        NotificationResponsePage
    """

    return sync_detailed(
        client=client,
        receiver_id=receiver_id,
        status=status,
        page=page,
        size=size,
        sort=sort,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    receiver_id: str | Unset = "-me-",
    status: list[GetNotificationsStatusItem] | Unset = UNSET,
    page: int | Unset = 0,
    size: int | Unset = 25,
    sort: list[str] | Unset = UNSET,
) -> Response[NotificationResponsePage]:
    """Retrieve stored notification, filtered by receiver and status

    Args:
        receiver_id (str | Unset):  Default: '-me-'.
        status (list[GetNotificationsStatusItem] | Unset):
        page (int | Unset):  Default: 0.
        size (int | Unset):  Default: 25.
        sort (list[str] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[NotificationResponsePage]
    """

    kwargs = _get_kwargs(
        receiver_id=receiver_id,
        status=status,
        page=page,
        size=size,
        sort=sort,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    receiver_id: str | Unset = "-me-",
    status: list[GetNotificationsStatusItem] | Unset = UNSET,
    page: int | Unset = 0,
    size: int | Unset = 25,
    sort: list[str] | Unset = UNSET,
) -> NotificationResponsePage | None:
    """Retrieve stored notification, filtered by receiver and status

    Args:
        receiver_id (str | Unset):  Default: '-me-'.
        status (list[GetNotificationsStatusItem] | Unset):
        page (int | Unset):  Default: 0.
        size (int | Unset):  Default: 25.
        sort (list[str] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        NotificationResponsePage
    """

    return (
        await asyncio_detailed(
            client=client,
            receiver_id=receiver_id,
            status=status,
            page=page,
            size=size,
            sort=sort,
        )
    ).parsed
