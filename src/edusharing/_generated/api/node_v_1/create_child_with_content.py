from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.children_file_content_upload import ChildrenFileContentUpload
from ...models.error_response import ErrorResponse
from ...models.node_entry import NodeEntry
from ...types import UNSET, Response, Unset


def _get_kwargs(
    repository: str,
    node: str,
    *,
    body: ChildrenFileContentUpload,
    type_: str,
    aspects: list[str] | Unset = UNSET,
    rename_if_exists: bool | Unset = False,
    version_comment: str | Unset = UNSET,
    assoc_type: str | Unset = UNSET,
    obey_mds: bool | Unset = True,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["type"] = type_

    json_aspects: list[str] | Unset = UNSET
    if not isinstance(aspects, Unset):
        json_aspects = aspects

    params["aspects"] = json_aspects

    params["renameIfExists"] = rename_if_exists

    params["versionComment"] = version_comment

    params["assocType"] = assoc_type

    params["obeyMds"] = obey_mds

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/node/v1/nodes/{repository}/{node}/children/_content".format(
            repository=quote(str(repository), safe=""),
            node=quote(str(node), safe=""),
        ),
        "params": params,
    }

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
    body: ChildrenFileContentUpload,
    type_: str,
    aspects: list[str] | Unset = UNSET,
    rename_if_exists: bool | Unset = False,
    version_comment: str | Unset = UNSET,
    assoc_type: str | Unset = UNSET,
    obey_mds: bool | Unset = True,
) -> Response[ErrorResponse | NodeEntry]:
    """Create a new child with content.

     Create a new child with content.

    Args:
        repository (str):
        node (str):
        type_ (str):
        aspects (list[str] | Unset):
        rename_if_exists (bool | Unset):  Default: False.
        version_comment (str | Unset):
        assoc_type (str | Unset):
        obey_mds (bool | Unset):  Default: True.
        body (ChildrenFileContentUpload): Multipart upload for node content

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
        type_=type_,
        aspects=aspects,
        rename_if_exists=rename_if_exists,
        version_comment=version_comment,
        assoc_type=assoc_type,
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
    body: ChildrenFileContentUpload,
    type_: str,
    aspects: list[str] | Unset = UNSET,
    rename_if_exists: bool | Unset = False,
    version_comment: str | Unset = UNSET,
    assoc_type: str | Unset = UNSET,
    obey_mds: bool | Unset = True,
) -> ErrorResponse | NodeEntry | None:
    """Create a new child with content.

     Create a new child with content.

    Args:
        repository (str):
        node (str):
        type_ (str):
        aspects (list[str] | Unset):
        rename_if_exists (bool | Unset):  Default: False.
        version_comment (str | Unset):
        assoc_type (str | Unset):
        obey_mds (bool | Unset):  Default: True.
        body (ChildrenFileContentUpload): Multipart upload for node content

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
        type_=type_,
        aspects=aspects,
        rename_if_exists=rename_if_exists,
        version_comment=version_comment,
        assoc_type=assoc_type,
        obey_mds=obey_mds,
    ).parsed


async def asyncio_detailed(
    repository: str,
    node: str,
    *,
    client: AuthenticatedClient | Client,
    body: ChildrenFileContentUpload,
    type_: str,
    aspects: list[str] | Unset = UNSET,
    rename_if_exists: bool | Unset = False,
    version_comment: str | Unset = UNSET,
    assoc_type: str | Unset = UNSET,
    obey_mds: bool | Unset = True,
) -> Response[ErrorResponse | NodeEntry]:
    """Create a new child with content.

     Create a new child with content.

    Args:
        repository (str):
        node (str):
        type_ (str):
        aspects (list[str] | Unset):
        rename_if_exists (bool | Unset):  Default: False.
        version_comment (str | Unset):
        assoc_type (str | Unset):
        obey_mds (bool | Unset):  Default: True.
        body (ChildrenFileContentUpload): Multipart upload for node content

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
        type_=type_,
        aspects=aspects,
        rename_if_exists=rename_if_exists,
        version_comment=version_comment,
        assoc_type=assoc_type,
        obey_mds=obey_mds,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    node: str,
    *,
    client: AuthenticatedClient | Client,
    body: ChildrenFileContentUpload,
    type_: str,
    aspects: list[str] | Unset = UNSET,
    rename_if_exists: bool | Unset = False,
    version_comment: str | Unset = UNSET,
    assoc_type: str | Unset = UNSET,
    obey_mds: bool | Unset = True,
) -> ErrorResponse | NodeEntry | None:
    """Create a new child with content.

     Create a new child with content.

    Args:
        repository (str):
        node (str):
        type_ (str):
        aspects (list[str] | Unset):
        rename_if_exists (bool | Unset):  Default: False.
        version_comment (str | Unset):
        assoc_type (str | Unset):
        obey_mds (bool | Unset):  Default: True.
        body (ChildrenFileContentUpload): Multipart upload for node content

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
            type_=type_,
            aspects=aspects,
            rename_if_exists=rename_if_exists,
            version_comment=version_comment,
            assoc_type=assoc_type,
            obey_mds=obey_mds,
        )
    ).parsed
