from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.notification_event_dto import NotificationEventDTO
from ...models.update_notification_status_status import UpdateNotificationStatusStatus
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    id: str | Unset = UNSET,
    status: UpdateNotificationStatusStatus | Unset = UpdateNotificationStatusStatus.READ,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["id"] = id

    json_status: str | Unset = UNSET
    if not isinstance(status, Unset):
        json_status = status.value

    params["status"] = json_status

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/notification/v1/notifications/status",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> NotificationEventDTO | None:
    if response.status_code == 200:
        response_200 = NotificationEventDTO.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[NotificationEventDTO]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    id: str | Unset = UNSET,
    status: UpdateNotificationStatusStatus | Unset = UpdateNotificationStatusStatus.READ,
) -> Response[NotificationEventDTO]:
    """Endpoint to update the notification status

    Args:
        id (str | Unset):
        status (UpdateNotificationStatusStatus | Unset):  Default:
            UpdateNotificationStatusStatus.READ.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[NotificationEventDTO]
    """

    kwargs = _get_kwargs(
        id=id,
        status=status,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    id: str | Unset = UNSET,
    status: UpdateNotificationStatusStatus | Unset = UpdateNotificationStatusStatus.READ,
) -> NotificationEventDTO | None:
    """Endpoint to update the notification status

    Args:
        id (str | Unset):
        status (UpdateNotificationStatusStatus | Unset):  Default:
            UpdateNotificationStatusStatus.READ.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        NotificationEventDTO
    """

    return sync_detailed(
        client=client,
        id=id,
        status=status,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    id: str | Unset = UNSET,
    status: UpdateNotificationStatusStatus | Unset = UpdateNotificationStatusStatus.READ,
) -> Response[NotificationEventDTO]:
    """Endpoint to update the notification status

    Args:
        id (str | Unset):
        status (UpdateNotificationStatusStatus | Unset):  Default:
            UpdateNotificationStatusStatus.READ.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[NotificationEventDTO]
    """

    kwargs = _get_kwargs(
        id=id,
        status=status,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    id: str | Unset = UNSET,
    status: UpdateNotificationStatusStatus | Unset = UpdateNotificationStatusStatus.READ,
) -> NotificationEventDTO | None:
    """Endpoint to update the notification status

    Args:
        id (str | Unset):
        status (UpdateNotificationStatusStatus | Unset):  Default:
            UpdateNotificationStatusStatus.READ.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        NotificationEventDTO
    """

    return (
        await asyncio_detailed(
            client=client,
            id=id,
            status=status,
        )
    ).parsed
