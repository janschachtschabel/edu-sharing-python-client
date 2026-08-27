from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...types import Response


def _get_kwargs(
    repository: str,
    group: str,
    *,
    body: list[str],
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/iam/v1/groups/{repository}/{group}/members".format(
            repository=quote(str(repository), safe=""),
            group=quote(str(group), safe=""),
        ),
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

    if response.status_code == 409:
        response_409 = ErrorResponse.from_dict(response.json())

        return response_409

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
    group: str,
    *,
    client: AuthenticatedClient | Client,
    body: list[str],
) -> Response[Any | ErrorResponse]:
    """Add members to the group.

     Add members to the group. (admin rights are required.) The whole list is processed within a single
    transaction, i.e. if one member fails, no member is added. At most 1000 members are accepted per
    request, larger requests are rejected with 400. A batch size of 100 is recommended. Batches must not
    be sent in parallel for the same group, since all of them write to the same group node and would
    only run into transaction retries.

    Args:
        repository (str):
        group (str):
        body (list[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ErrorResponse]
    """

    kwargs = _get_kwargs(
        repository=repository,
        group=group,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repository: str,
    group: str,
    *,
    client: AuthenticatedClient | Client,
    body: list[str],
) -> Any | ErrorResponse | None:
    """Add members to the group.

     Add members to the group. (admin rights are required.) The whole list is processed within a single
    transaction, i.e. if one member fails, no member is added. At most 1000 members are accepted per
    request, larger requests are rejected with 400. A batch size of 100 is recommended. Batches must not
    be sent in parallel for the same group, since all of them write to the same group node and would
    only run into transaction retries.

    Args:
        repository (str):
        group (str):
        body (list[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ErrorResponse
    """

    return sync_detailed(
        repository=repository,
        group=group,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    repository: str,
    group: str,
    *,
    client: AuthenticatedClient | Client,
    body: list[str],
) -> Response[Any | ErrorResponse]:
    """Add members to the group.

     Add members to the group. (admin rights are required.) The whole list is processed within a single
    transaction, i.e. if one member fails, no member is added. At most 1000 members are accepted per
    request, larger requests are rejected with 400. A batch size of 100 is recommended. Batches must not
    be sent in parallel for the same group, since all of them write to the same group node and would
    only run into transaction retries.

    Args:
        repository (str):
        group (str):
        body (list[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ErrorResponse]
    """

    kwargs = _get_kwargs(
        repository=repository,
        group=group,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    group: str,
    *,
    client: AuthenticatedClient | Client,
    body: list[str],
) -> Any | ErrorResponse | None:
    """Add members to the group.

     Add members to the group. (admin rights are required.) The whole list is processed within a single
    transaction, i.e. if one member fails, no member is added. At most 1000 members are accepted per
    request, larger requests are rejected with 400. A batch size of 100 is recommended. Batches must not
    be sent in parallel for the same group, since all of them write to the same group node and would
    only run into transaction retries.

    Args:
        repository (str):
        group (str):
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
            group=group,
            client=client,
            body=body,
        )
    ).parsed
