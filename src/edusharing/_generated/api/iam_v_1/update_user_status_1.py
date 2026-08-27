from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.update_user_status_1_status import UpdateUserStatus1Status
from ...types import UNSET, Response


def _get_kwargs(
    repository: str,
    status: UpdateUserStatus1Status,
    *,
    body: list[str],
    notify: bool = True,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["notify"] = notify

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/iam/v1/people/{repository}/status/{status}".format(
            repository=quote(str(repository), safe=""),
            status=quote(str(status), safe=""),
        ),
        "params": params,
    }

    _kwargs["json"] = body

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
    repository: str,
    status: UpdateUserStatus1Status,
    *,
    client: AuthenticatedClient | Client,
    body: list[str],
    notify: bool = True,
) -> Response[Any | ErrorResponse]:
    """update the status of multiple users.

     update the status of multiple users. (admin rights are required.) The whole list is processed within
    a single transaction, i.e. if one user fails, the status of no user is changed. At most 1000 users
    are accepted per request, at most 100 if notify is enabled, since the notification mails are sent
    synchronously, one per user. Larger requests are rejected with 400. A batch size of 100 (20 with
    notify enabled) is recommended.

    Args:
        repository (str):
        status (UpdateUserStatus1Status):
        notify (bool):  Default: True.
        body (list[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ErrorResponse]
    """

    kwargs = _get_kwargs(
        repository=repository,
        status=status,
        body=body,
        notify=notify,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repository: str,
    status: UpdateUserStatus1Status,
    *,
    client: AuthenticatedClient | Client,
    body: list[str],
    notify: bool = True,
) -> Any | ErrorResponse | None:
    """update the status of multiple users.

     update the status of multiple users. (admin rights are required.) The whole list is processed within
    a single transaction, i.e. if one user fails, the status of no user is changed. At most 1000 users
    are accepted per request, at most 100 if notify is enabled, since the notification mails are sent
    synchronously, one per user. Larger requests are rejected with 400. A batch size of 100 (20 with
    notify enabled) is recommended.

    Args:
        repository (str):
        status (UpdateUserStatus1Status):
        notify (bool):  Default: True.
        body (list[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ErrorResponse
    """

    return sync_detailed(
        repository=repository,
        status=status,
        client=client,
        body=body,
        notify=notify,
    ).parsed


async def asyncio_detailed(
    repository: str,
    status: UpdateUserStatus1Status,
    *,
    client: AuthenticatedClient | Client,
    body: list[str],
    notify: bool = True,
) -> Response[Any | ErrorResponse]:
    """update the status of multiple users.

     update the status of multiple users. (admin rights are required.) The whole list is processed within
    a single transaction, i.e. if one user fails, the status of no user is changed. At most 1000 users
    are accepted per request, at most 100 if notify is enabled, since the notification mails are sent
    synchronously, one per user. Larger requests are rejected with 400. A batch size of 100 (20 with
    notify enabled) is recommended.

    Args:
        repository (str):
        status (UpdateUserStatus1Status):
        notify (bool):  Default: True.
        body (list[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ErrorResponse]
    """

    kwargs = _get_kwargs(
        repository=repository,
        status=status,
        body=body,
        notify=notify,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    status: UpdateUserStatus1Status,
    *,
    client: AuthenticatedClient | Client,
    body: list[str],
    notify: bool = True,
) -> Any | ErrorResponse | None:
    """update the status of multiple users.

     update the status of multiple users. (admin rights are required.) The whole list is processed within
    a single transaction, i.e. if one user fails, the status of no user is changed. At most 1000 users
    are accepted per request, at most 100 if notify is enabled, since the notification mails are sent
    synchronously, one per user. Larger requests are rejected with 400. A batch size of 100 (20 with
    notify enabled) is recommended.

    Args:
        repository (str):
        status (UpdateUserStatus1Status):
        notify (bool):  Default: True.
        body (list[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ErrorResponse
    """

    return (
        await asyncio_detailed(
            repository=repository,
            status=status,
            client=client,
            body=body,
            notify=notify,
        )
    ).parsed
