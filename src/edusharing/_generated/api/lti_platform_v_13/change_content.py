from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.change_content_body import ChangeContentBody
from ...models.error_response import ErrorResponse
from ...models.node_entry import NodeEntry
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: ChangeContentBody | Unset = UNSET,
    jwt: str,
    version_comment: str | Unset = UNSET,
    mimetype: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["jwt"] = jwt

    params["versionComment"] = version_comment

    params["mimetype"] = mimetype

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/ltiplatform/v13/content",
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
    *,
    client: AuthenticatedClient | Client,
    body: ChangeContentBody | Unset = UNSET,
    jwt: str,
    version_comment: str | Unset = UNSET,
    mimetype: str,
) -> Response[ErrorResponse | NodeEntry]:
    """Custom edu-sharing endpoint to change content of node.

     Change content of node.

    Args:
        jwt (str):
        version_comment (str | Unset):
        mimetype (str):
        body (ChangeContentBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | NodeEntry]
    """

    kwargs = _get_kwargs(
        body=body,
        jwt=jwt,
        version_comment=version_comment,
        mimetype=mimetype,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: ChangeContentBody | Unset = UNSET,
    jwt: str,
    version_comment: str | Unset = UNSET,
    mimetype: str,
) -> ErrorResponse | NodeEntry | None:
    """Custom edu-sharing endpoint to change content of node.

     Change content of node.

    Args:
        jwt (str):
        version_comment (str | Unset):
        mimetype (str):
        body (ChangeContentBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | NodeEntry
    """

    return sync_detailed(
        client=client,
        body=body,
        jwt=jwt,
        version_comment=version_comment,
        mimetype=mimetype,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: ChangeContentBody | Unset = UNSET,
    jwt: str,
    version_comment: str | Unset = UNSET,
    mimetype: str,
) -> Response[ErrorResponse | NodeEntry]:
    """Custom edu-sharing endpoint to change content of node.

     Change content of node.

    Args:
        jwt (str):
        version_comment (str | Unset):
        mimetype (str):
        body (ChangeContentBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | NodeEntry]
    """

    kwargs = _get_kwargs(
        body=body,
        jwt=jwt,
        version_comment=version_comment,
        mimetype=mimetype,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: ChangeContentBody | Unset = UNSET,
    jwt: str,
    version_comment: str | Unset = UNSET,
    mimetype: str,
) -> ErrorResponse | NodeEntry | None:
    """Custom edu-sharing endpoint to change content of node.

     Change content of node.

    Args:
        jwt (str):
        version_comment (str | Unset):
        mimetype (str):
        body (ChangeContentBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | NodeEntry
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            jwt=jwt,
            version_comment=version_comment,
            mimetype=mimetype,
        )
    ).parsed
