from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.update_notification_status_by_receiver_id_new_status import (
    UpdateNotificationStatusByReceiverIdNewStatus,
)
from ...models.update_notification_status_by_receiver_id_old_status_item import (
    UpdateNotificationStatusByReceiverIdOldStatusItem,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    receiver_id: str | Unset = UNSET,
    old_status: list[UpdateNotificationStatusByReceiverIdOldStatusItem] | Unset = UNSET,
    new_status: UpdateNotificationStatusByReceiverIdNewStatus
    | Unset = UpdateNotificationStatusByReceiverIdNewStatus.READ,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["receiverId"] = receiver_id

    json_old_status: list[str] | Unset = UNSET
    if not isinstance(old_status, Unset):
        json_old_status = []
        for old_status_item_data in old_status:
            old_status_item = old_status_item_data.value
            json_old_status.append(old_status_item)

    params["oldStatus"] = json_old_status

    json_new_status: str | Unset = UNSET
    if not isinstance(new_status, Unset):
        json_new_status = new_status.value

    params["newStatus"] = json_new_status

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/notification/v1/notifications/receiver/status",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | None:
    if response.status_code == 200:
        return None

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    receiver_id: str | Unset = UNSET,
    old_status: list[UpdateNotificationStatusByReceiverIdOldStatusItem] | Unset = UNSET,
    new_status: UpdateNotificationStatusByReceiverIdNewStatus
    | Unset = UpdateNotificationStatusByReceiverIdNewStatus.READ,
) -> Response[Any]:
    """Endpoint to update the notification status

    Args:
        receiver_id (str | Unset):
        old_status (list[UpdateNotificationStatusByReceiverIdOldStatusItem] | Unset):
        new_status (UpdateNotificationStatusByReceiverIdNewStatus | Unset):  Default:
            UpdateNotificationStatusByReceiverIdNewStatus.READ.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        receiver_id=receiver_id,
        old_status=old_status,
        new_status=new_status,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    receiver_id: str | Unset = UNSET,
    old_status: list[UpdateNotificationStatusByReceiverIdOldStatusItem] | Unset = UNSET,
    new_status: UpdateNotificationStatusByReceiverIdNewStatus
    | Unset = UpdateNotificationStatusByReceiverIdNewStatus.READ,
) -> Response[Any]:
    """Endpoint to update the notification status

    Args:
        receiver_id (str | Unset):
        old_status (list[UpdateNotificationStatusByReceiverIdOldStatusItem] | Unset):
        new_status (UpdateNotificationStatusByReceiverIdNewStatus | Unset):  Default:
            UpdateNotificationStatusByReceiverIdNewStatus.READ.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        receiver_id=receiver_id,
        old_status=old_status,
        new_status=new_status,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
