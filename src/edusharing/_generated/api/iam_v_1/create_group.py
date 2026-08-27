from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.group import Group
from ...models.group_profile import GroupProfile
from ...types import UNSET, Response, Unset


def _get_kwargs(
    repository: str,
    group: str,
    *,
    body: GroupProfile,
    parent: str | Unset = UNSET,
    return_result: bool | Unset = True,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["parent"] = parent

    params["returnResult"] = return_result

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/iam/v1/groups/{repository}/{group}".format(
            repository=quote(str(repository), safe=""),
            group=quote(str(group), safe=""),
        ),
        "params": params,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | Group | None:
    if response.status_code == 200:
        response_200 = Group.from_dict(response.json())

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
) -> Response[ErrorResponse | Group]:
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
    body: GroupProfile,
    parent: str | Unset = UNSET,
    return_result: bool | Unset = True,
) -> Response[ErrorResponse | Group]:
    """Create a new group.

     Create a new group. (admin rights are required.)

    Args:
        repository (str):
        group (str):
        parent (str | Unset):
        return_result (bool | Unset):  Default: True.
        body (GroupProfile):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | Group]
    """

    kwargs = _get_kwargs(
        repository=repository,
        group=group,
        body=body,
        parent=parent,
        return_result=return_result,
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
    body: GroupProfile,
    parent: str | Unset = UNSET,
    return_result: bool | Unset = True,
) -> ErrorResponse | Group | None:
    """Create a new group.

     Create a new group. (admin rights are required.)

    Args:
        repository (str):
        group (str):
        parent (str | Unset):
        return_result (bool | Unset):  Default: True.
        body (GroupProfile):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | Group
    """

    return sync_detailed(
        repository=repository,
        group=group,
        client=client,
        body=body,
        parent=parent,
        return_result=return_result,
    ).parsed


async def asyncio_detailed(
    repository: str,
    group: str,
    *,
    client: AuthenticatedClient | Client,
    body: GroupProfile,
    parent: str | Unset = UNSET,
    return_result: bool | Unset = True,
) -> Response[ErrorResponse | Group]:
    """Create a new group.

     Create a new group. (admin rights are required.)

    Args:
        repository (str):
        group (str):
        parent (str | Unset):
        return_result (bool | Unset):  Default: True.
        body (GroupProfile):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | Group]
    """

    kwargs = _get_kwargs(
        repository=repository,
        group=group,
        body=body,
        parent=parent,
        return_result=return_result,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    group: str,
    *,
    client: AuthenticatedClient | Client,
    body: GroupProfile,
    parent: str | Unset = UNSET,
    return_result: bool | Unset = True,
) -> ErrorResponse | Group | None:
    """Create a new group.

     Create a new group. (admin rights are required.)

    Args:
        repository (str):
        group (str):
        parent (str | Unset):
        return_result (bool | Unset):  Default: True.
        body (GroupProfile):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | Group
    """

    return (
        await asyncio_detailed(
            repository=repository,
            group=group,
            client=client,
            body=body,
            parent=parent,
            return_result=return_result,
        )
    ).parsed
