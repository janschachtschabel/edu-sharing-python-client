from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.change_metadata_with_versioning_body import ChangeMetadataWithVersioningBody
from ...models.error_response import ErrorResponse
from ...models.node_entry import NodeEntry
from ...types import UNSET, Response, Unset


def _get_kwargs(
    repository: str,
    node: str,
    *,
    body: ChangeMetadataWithVersioningBody,
    version_comment: str,
    obey_mds: bool | Unset = True,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["versionComment"] = version_comment

    params["obeyMds"] = obey_mds

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/node/v1/nodes/{repository}/{node}/metadata".format(
            repository=quote(str(repository), safe=""),
            node=quote(str(node), safe=""),
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
    body: ChangeMetadataWithVersioningBody,
    version_comment: str,
    obey_mds: bool | Unset = True,
) -> Response[ErrorResponse | NodeEntry]:
    """Change metadata of node (new version).

     Change metadata of node (new version).

    Args:
        repository (str):
        node (str):
        version_comment (str):
        obey_mds (bool | Unset):  Default: True.
        body (ChangeMetadataWithVersioningBody):

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
        version_comment=version_comment,
        obey_mds=obey_mds,
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
    body: ChangeMetadataWithVersioningBody,
    version_comment: str,
    obey_mds: bool | Unset = True,
) -> ErrorResponse | NodeEntry | None:
    """Change metadata of node (new version).

     Change metadata of node (new version).

    Args:
        repository (str):
        node (str):
        version_comment (str):
        obey_mds (bool | Unset):  Default: True.
        body (ChangeMetadataWithVersioningBody):

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
        version_comment=version_comment,
        obey_mds=obey_mds,
    ).parsed


async def asyncio_detailed(
    repository: str,
    node: str,
    *,
    client: AuthenticatedClient | Client,
    body: ChangeMetadataWithVersioningBody,
    version_comment: str,
    obey_mds: bool | Unset = True,
) -> Response[ErrorResponse | NodeEntry]:
    """Change metadata of node (new version).

     Change metadata of node (new version).

    Args:
        repository (str):
        node (str):
        version_comment (str):
        obey_mds (bool | Unset):  Default: True.
        body (ChangeMetadataWithVersioningBody):

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
        version_comment=version_comment,
        obey_mds=obey_mds,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    node: str,
    *,
    client: AuthenticatedClient | Client,
    body: ChangeMetadataWithVersioningBody,
    version_comment: str,
    obey_mds: bool | Unset = True,
) -> ErrorResponse | NodeEntry | None:
    """Change metadata of node (new version).

     Change metadata of node (new version).

    Args:
        repository (str):
        node (str):
        version_comment (str):
        obey_mds (bool | Unset):  Default: True.
        body (ChangeMetadataWithVersioningBody):

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
            version_comment=version_comment,
            obey_mds=obey_mds,
        )
    ).parsed
