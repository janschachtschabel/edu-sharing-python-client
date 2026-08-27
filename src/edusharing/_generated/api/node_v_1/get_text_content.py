from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.node_text import NodeText
from ...types import UNSET, Response, Unset


def _get_kwargs(
    repository: str,
    node: str,
    *,
    force_update: bool | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["forceUpdate"] = force_update

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/node/v1/nodes/{repository}/{node}/textContent".format(
            repository=quote(str(repository), safe=""),
            node=quote(str(node), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | NodeText | None:
    if response.status_code == 200:
        response_200 = NodeText.from_dict(response.json())

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
) -> Response[ErrorResponse | NodeText]:
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
    force_update: bool | Unset = UNSET,
) -> Response[ErrorResponse | NodeText]:
    """Get the plain text content of a node.

     Returns the extracted plain text for a ccm:io node. The result is cached in ccm:fulltext_content
    after the first extraction.

    For file nodes, the text is extracted from the binary content via the local transform service.
    For link nodes (ccm:wwwurl set), text is fetched from the URL via the BAPI text-extraction proxy. If
    extraction fails, null is returned.

    Args:
        repository (str):
        node (str):
        force_update (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | NodeText]
    """

    kwargs = _get_kwargs(
        repository=repository,
        node=node,
        force_update=force_update,
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
    force_update: bool | Unset = UNSET,
) -> ErrorResponse | NodeText | None:
    """Get the plain text content of a node.

     Returns the extracted plain text for a ccm:io node. The result is cached in ccm:fulltext_content
    after the first extraction.

    For file nodes, the text is extracted from the binary content via the local transform service.
    For link nodes (ccm:wwwurl set), text is fetched from the URL via the BAPI text-extraction proxy. If
    extraction fails, null is returned.

    Args:
        repository (str):
        node (str):
        force_update (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | NodeText
    """

    return sync_detailed(
        repository=repository,
        node=node,
        client=client,
        force_update=force_update,
    ).parsed


async def asyncio_detailed(
    repository: str,
    node: str,
    *,
    client: AuthenticatedClient | Client,
    force_update: bool | Unset = UNSET,
) -> Response[ErrorResponse | NodeText]:
    """Get the plain text content of a node.

     Returns the extracted plain text for a ccm:io node. The result is cached in ccm:fulltext_content
    after the first extraction.

    For file nodes, the text is extracted from the binary content via the local transform service.
    For link nodes (ccm:wwwurl set), text is fetched from the URL via the BAPI text-extraction proxy. If
    extraction fails, null is returned.

    Args:
        repository (str):
        node (str):
        force_update (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | NodeText]
    """

    kwargs = _get_kwargs(
        repository=repository,
        node=node,
        force_update=force_update,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    node: str,
    *,
    client: AuthenticatedClient | Client,
    force_update: bool | Unset = UNSET,
) -> ErrorResponse | NodeText | None:
    """Get the plain text content of a node.

     Returns the extracted plain text for a ccm:io node. The result is cached in ccm:fulltext_content
    after the first extraction.

    For file nodes, the text is extracted from the binary content via the local transform service.
    For link nodes (ccm:wwwurl set), text is fetched from the URL via the BAPI text-extraction proxy. If
    extraction fails, null is returned.

    Args:
        repository (str):
        node (str):
        force_update (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | NodeText
    """

    return (
        await asyncio_detailed(
            repository=repository,
            node=node,
            client=client,
            force_update=force_update,
        )
    ).parsed
