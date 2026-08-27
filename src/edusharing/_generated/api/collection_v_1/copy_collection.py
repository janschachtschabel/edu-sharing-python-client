from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.copy import Copy
from ...models.error_response import ErrorResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    repository: str,
    source_collection: str,
    *,
    target_collection: str | Unset = UNSET,
    copy_root: bool | Unset = True,
    copy_refs: bool | Unset = False,
    copy_permissions: bool | Unset = False,
    copy_child_collections: bool | Unset = True,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["targetCollection"] = target_collection

    params["copyRoot"] = copy_root

    params["copyRefs"] = copy_refs

    params["copyPermissions"] = copy_permissions

    params["copyChildCollections"] = copy_child_collections

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/collection/v1/collections/{repository}/{source_collection}/copy".format(
            repository=quote(str(repository), safe=""),
            source_collection=quote(str(source_collection), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Copy | ErrorResponse | None:
    if response.status_code == 200:
        response_200 = Copy.from_dict(response.json())

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
) -> Response[Copy | ErrorResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    repository: str,
    source_collection: str,
    *,
    client: AuthenticatedClient | Client,
    target_collection: str | Unset = UNSET,
    copy_root: bool | Unset = True,
    copy_refs: bool | Unset = False,
    copy_permissions: bool | Unset = False,
    copy_child_collections: bool | Unset = True,
) -> Response[Copy | ErrorResponse]:
    """Copy a collection.

     Copy a collection.

    Args:
        repository (str):
        source_collection (str):
        target_collection (str | Unset):
        copy_root (bool | Unset):  Default: True.
        copy_refs (bool | Unset):  Default: False.
        copy_permissions (bool | Unset):  Default: False.
        copy_child_collections (bool | Unset):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Copy | ErrorResponse]
    """

    kwargs = _get_kwargs(
        repository=repository,
        source_collection=source_collection,
        target_collection=target_collection,
        copy_root=copy_root,
        copy_refs=copy_refs,
        copy_permissions=copy_permissions,
        copy_child_collections=copy_child_collections,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repository: str,
    source_collection: str,
    *,
    client: AuthenticatedClient | Client,
    target_collection: str | Unset = UNSET,
    copy_root: bool | Unset = True,
    copy_refs: bool | Unset = False,
    copy_permissions: bool | Unset = False,
    copy_child_collections: bool | Unset = True,
) -> Copy | ErrorResponse | None:
    """Copy a collection.

     Copy a collection.

    Args:
        repository (str):
        source_collection (str):
        target_collection (str | Unset):
        copy_root (bool | Unset):  Default: True.
        copy_refs (bool | Unset):  Default: False.
        copy_permissions (bool | Unset):  Default: False.
        copy_child_collections (bool | Unset):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Copy | ErrorResponse
    """

    return sync_detailed(
        repository=repository,
        source_collection=source_collection,
        client=client,
        target_collection=target_collection,
        copy_root=copy_root,
        copy_refs=copy_refs,
        copy_permissions=copy_permissions,
        copy_child_collections=copy_child_collections,
    ).parsed


async def asyncio_detailed(
    repository: str,
    source_collection: str,
    *,
    client: AuthenticatedClient | Client,
    target_collection: str | Unset = UNSET,
    copy_root: bool | Unset = True,
    copy_refs: bool | Unset = False,
    copy_permissions: bool | Unset = False,
    copy_child_collections: bool | Unset = True,
) -> Response[Copy | ErrorResponse]:
    """Copy a collection.

     Copy a collection.

    Args:
        repository (str):
        source_collection (str):
        target_collection (str | Unset):
        copy_root (bool | Unset):  Default: True.
        copy_refs (bool | Unset):  Default: False.
        copy_permissions (bool | Unset):  Default: False.
        copy_child_collections (bool | Unset):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Copy | ErrorResponse]
    """

    kwargs = _get_kwargs(
        repository=repository,
        source_collection=source_collection,
        target_collection=target_collection,
        copy_root=copy_root,
        copy_refs=copy_refs,
        copy_permissions=copy_permissions,
        copy_child_collections=copy_child_collections,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    source_collection: str,
    *,
    client: AuthenticatedClient | Client,
    target_collection: str | Unset = UNSET,
    copy_root: bool | Unset = True,
    copy_refs: bool | Unset = False,
    copy_permissions: bool | Unset = False,
    copy_child_collections: bool | Unset = True,
) -> Copy | ErrorResponse | None:
    """Copy a collection.

     Copy a collection.

    Args:
        repository (str):
        source_collection (str):
        target_collection (str | Unset):
        copy_root (bool | Unset):  Default: True.
        copy_refs (bool | Unset):  Default: False.
        copy_permissions (bool | Unset):  Default: False.
        copy_child_collections (bool | Unset):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Copy | ErrorResponse
    """

    return (
        await asyncio_detailed(
            repository=repository,
            source_collection=source_collection,
            client=client,
            target_collection=target_collection,
            copy_root=copy_root,
            copy_refs=copy_refs,
            copy_permissions=copy_permissions,
            copy_child_collections=copy_child_collections,
        )
    ).parsed
