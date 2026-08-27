from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.change_preview_body import ChangePreviewBody
from ...models.error_response import ErrorResponse
from ...models.node_entry import NodeEntry
from ...types import UNSET, Response, Unset


def _get_kwargs(
    repository: str,
    node: str,
    *,
    body: ChangePreviewBody | Unset = UNSET,
    mimetype: str,
    create_version: bool | Unset = True,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["mimetype"] = mimetype

    params["createVersion"] = create_version

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/node/v1/nodes/{repository}/{node}/preview".format(
            repository=quote(str(repository), safe=""),
            node=quote(str(node), safe=""),
        ),
        "params": params,
    }

    if not isinstance(body, Unset):
        _kwargs["files"] = body.to_multipart()

    headers["Content-Type"] = "multipart/form-data; boundary=+++"

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
    repository: str,
    node: str,
    *,
    client: AuthenticatedClient | Client,
    body: ChangePreviewBody | Unset = UNSET,
    mimetype: str,
    create_version: bool | Unset = True,
) -> Response[ErrorResponse | NodeEntry]:
    """Change preview of node.

     Change preview of node.

    Args:
        repository (str):
        node (str):
        mimetype (str):
        create_version (bool | Unset):  Default: True.
        body (ChangePreviewBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | NodeEntry]
    """

    kwargs = _get_kwargs(
        repository=repository,
        node=node,
        body=body,
        mimetype=mimetype,
        create_version=create_version,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repository: str,
    node: str,
    *,
    client: AuthenticatedClient | Client,
    body: ChangePreviewBody | Unset = UNSET,
    mimetype: str,
    create_version: bool | Unset = True,
) -> ErrorResponse | NodeEntry | None:
    """Change preview of node.

     Change preview of node.

    Args:
        repository (str):
        node (str):
        mimetype (str):
        create_version (bool | Unset):  Default: True.
        body (ChangePreviewBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | NodeEntry
    """

    return sync_detailed(
        repository=repository,
        node=node,
        client=client,
        body=body,
        mimetype=mimetype,
        create_version=create_version,
    ).parsed


async def asyncio_detailed(
    repository: str,
    node: str,
    *,
    client: AuthenticatedClient | Client,
    body: ChangePreviewBody | Unset = UNSET,
    mimetype: str,
    create_version: bool | Unset = True,
) -> Response[ErrorResponse | NodeEntry]:
    """Change preview of node.

     Change preview of node.

    Args:
        repository (str):
        node (str):
        mimetype (str):
        create_version (bool | Unset):  Default: True.
        body (ChangePreviewBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | NodeEntry]
    """

    kwargs = _get_kwargs(
        repository=repository,
        node=node,
        body=body,
        mimetype=mimetype,
        create_version=create_version,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    node: str,
    *,
    client: AuthenticatedClient | Client,
    body: ChangePreviewBody | Unset = UNSET,
    mimetype: str,
    create_version: bool | Unset = True,
) -> ErrorResponse | NodeEntry | None:
    """Change preview of node.

     Change preview of node.

    Args:
        repository (str):
        node (str):
        mimetype (str):
        create_version (bool | Unset):  Default: True.
        body (ChangePreviewBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | NodeEntry
    """

    return (
        await asyncio_detailed(
            repository=repository,
            node=node,
            client=client,
            body=body,
            mimetype=mimetype,
            create_version=create_version,
        )
    ).parsed
