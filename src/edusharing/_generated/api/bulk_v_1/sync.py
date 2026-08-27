from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.node_entry import NodeEntry
from ...models.sync_body import SyncBody
from ...types import UNSET, Response, Unset


def _get_kwargs(
    group: str,
    *,
    body: SyncBody,
    match: list[str],
    group_by: list[str] | Unset = UNSET,
    type_: str,
    aspects: list[str] | Unset = UNSET,
    resolve_node: bool | Unset = True,
    reset_version: bool | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    json_match = match

    params["match"] = json_match

    json_group_by: list[str] | Unset = UNSET
    if not isinstance(group_by, Unset):
        json_group_by = group_by

    params["groupBy"] = json_group_by

    params["type"] = type_

    json_aspects: list[str] | Unset = UNSET
    if not isinstance(aspects, Unset):
        json_aspects = aspects

    params["aspects"] = json_aspects

    params["resolveNode"] = resolve_node

    params["resetVersion"] = reset_version

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/bulk/v1/sync/{group}".format(
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
) -> ErrorResponse | NodeEntry | None:
    if response.status_code == 200:
        response_200 = NodeEntry.from_dict(response.json())

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
) -> Response[ErrorResponse | NodeEntry]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    group: str,
    *,
    client: AuthenticatedClient | Client,
    body: SyncBody,
    match: list[str],
    group_by: list[str] | Unset = UNSET,
    type_: str,
    aspects: list[str] | Unset = UNSET,
    resolve_node: bool | Unset = True,
    reset_version: bool | Unset = UNSET,
) -> Response[ErrorResponse | NodeEntry]:
    r"""Create or update a given node

     Depending on the given \"match\" properties either a new node will be created or the existing one
    will be updated

    Args:
        group (str):
        match (list[str]):
        group_by (list[str] | Unset):
        type_ (str):
        aspects (list[str] | Unset):
        resolve_node (bool | Unset):  Default: True.
        reset_version (bool | Unset):
        body (SyncBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | NodeEntry]
    """

    kwargs = _get_kwargs(
        group=group,
        body=body,
        match=match,
        group_by=group_by,
        type_=type_,
        aspects=aspects,
        resolve_node=resolve_node,
        reset_version=reset_version,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    group: str,
    *,
    client: AuthenticatedClient | Client,
    body: SyncBody,
    match: list[str],
    group_by: list[str] | Unset = UNSET,
    type_: str,
    aspects: list[str] | Unset = UNSET,
    resolve_node: bool | Unset = True,
    reset_version: bool | Unset = UNSET,
) -> ErrorResponse | NodeEntry | None:
    r"""Create or update a given node

     Depending on the given \"match\" properties either a new node will be created or the existing one
    will be updated

    Args:
        group (str):
        match (list[str]):
        group_by (list[str] | Unset):
        type_ (str):
        aspects (list[str] | Unset):
        resolve_node (bool | Unset):  Default: True.
        reset_version (bool | Unset):
        body (SyncBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | NodeEntry
    """

    return sync_detailed(
        group=group,
        client=client,
        body=body,
        match=match,
        group_by=group_by,
        type_=type_,
        aspects=aspects,
        resolve_node=resolve_node,
        reset_version=reset_version,
    ).parsed


async def asyncio_detailed(
    group: str,
    *,
    client: AuthenticatedClient | Client,
    body: SyncBody,
    match: list[str],
    group_by: list[str] | Unset = UNSET,
    type_: str,
    aspects: list[str] | Unset = UNSET,
    resolve_node: bool | Unset = True,
    reset_version: bool | Unset = UNSET,
) -> Response[ErrorResponse | NodeEntry]:
    r"""Create or update a given node

     Depending on the given \"match\" properties either a new node will be created or the existing one
    will be updated

    Args:
        group (str):
        match (list[str]):
        group_by (list[str] | Unset):
        type_ (str):
        aspects (list[str] | Unset):
        resolve_node (bool | Unset):  Default: True.
        reset_version (bool | Unset):
        body (SyncBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | NodeEntry]
    """

    kwargs = _get_kwargs(
        group=group,
        body=body,
        match=match,
        group_by=group_by,
        type_=type_,
        aspects=aspects,
        resolve_node=resolve_node,
        reset_version=reset_version,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    group: str,
    *,
    client: AuthenticatedClient | Client,
    body: SyncBody,
    match: list[str],
    group_by: list[str] | Unset = UNSET,
    type_: str,
    aspects: list[str] | Unset = UNSET,
    resolve_node: bool | Unset = True,
    reset_version: bool | Unset = UNSET,
) -> ErrorResponse | NodeEntry | None:
    r"""Create or update a given node

     Depending on the given \"match\" properties either a new node will be created or the existing one
    will be updated

    Args:
        group (str):
        match (list[str]):
        group_by (list[str] | Unset):
        type_ (str):
        aspects (list[str] | Unset):
        resolve_node (bool | Unset):  Default: True.
        reset_version (bool | Unset):
        body (SyncBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | NodeEntry
    """

    return (
        await asyncio_detailed(
            group=group,
            client=client,
            body=body,
            match=match,
            group_by=group_by,
            type_=type_,
            aspects=aspects,
            resolve_node=resolve_node,
            reset_version=reset_version,
        )
    ).parsed
