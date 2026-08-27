from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.create_tool_defintition_body import CreateToolDefintitionBody
from ...models.error_response import ErrorResponse
from ...models.node_entry import NodeEntry
from ...types import UNSET, Response, Unset


def _get_kwargs(
    repository: str,
    *,
    body: CreateToolDefintitionBody,
    rename_if_exists: bool | Unset = False,
    version_comment: str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["renameIfExists"] = rename_if_exists

    params["versionComment"] = version_comment

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/tool/v1/tools/{repository}/tooldefinitions".format(
            repository=quote(str(repository), safe=""),
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
    *,
    client: AuthenticatedClient | Client,
    body: CreateToolDefintitionBody,
    rename_if_exists: bool | Unset = False,
    version_comment: str | Unset = UNSET,
) -> Response[ErrorResponse | NodeEntry]:
    """Create a new tool definition object.

     Create a new tool definition object.

    Args:
        repository (str):
        rename_if_exists (bool | Unset):  Default: False.
        version_comment (str | Unset):
        body (CreateToolDefintitionBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | NodeEntry]
    """

    kwargs = _get_kwargs(
        repository=repository,
        body=body,
        rename_if_exists=rename_if_exists,
        version_comment=version_comment,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repository: str,
    *,
    client: AuthenticatedClient | Client,
    body: CreateToolDefintitionBody,
    rename_if_exists: bool | Unset = False,
    version_comment: str | Unset = UNSET,
) -> ErrorResponse | NodeEntry | None:
    """Create a new tool definition object.

     Create a new tool definition object.

    Args:
        repository (str):
        rename_if_exists (bool | Unset):  Default: False.
        version_comment (str | Unset):
        body (CreateToolDefintitionBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | NodeEntry
    """

    return sync_detailed(
        repository=repository,
        client=client,
        body=body,
        rename_if_exists=rename_if_exists,
        version_comment=version_comment,
    ).parsed


async def asyncio_detailed(
    repository: str,
    *,
    client: AuthenticatedClient | Client,
    body: CreateToolDefintitionBody,
    rename_if_exists: bool | Unset = False,
    version_comment: str | Unset = UNSET,
) -> Response[ErrorResponse | NodeEntry]:
    """Create a new tool definition object.

     Create a new tool definition object.

    Args:
        repository (str):
        rename_if_exists (bool | Unset):  Default: False.
        version_comment (str | Unset):
        body (CreateToolDefintitionBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | NodeEntry]
    """

    kwargs = _get_kwargs(
        repository=repository,
        body=body,
        rename_if_exists=rename_if_exists,
        version_comment=version_comment,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    *,
    client: AuthenticatedClient | Client,
    body: CreateToolDefintitionBody,
    rename_if_exists: bool | Unset = False,
    version_comment: str | Unset = UNSET,
) -> ErrorResponse | NodeEntry | None:
    """Create a new tool definition object.

     Create a new tool definition object.

    Args:
        repository (str):
        rename_if_exists (bool | Unset):  Default: False.
        version_comment (str | Unset):
        body (CreateToolDefintitionBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | NodeEntry
    """

    return (
        await asyncio_detailed(
            repository=repository,
            client=client,
            body=body,
            rename_if_exists=rename_if_exists,
            version_comment=version_comment,
        )
    ).parsed
