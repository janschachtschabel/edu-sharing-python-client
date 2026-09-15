from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.update_config_file_path_prefix import UpdateConfigFilePathPrefix
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: str | Unset = UNSET,
    filename: str,
    path_prefix: UpdateConfigFilePathPrefix,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["filename"] = filename

    json_path_prefix = path_prefix.value
    params["pathPrefix"] = json_path_prefix

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/admin/v1/configFile",
        "params": params,
    }

    if not isinstance(body, Unset):
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
    *,
    client: AuthenticatedClient | Client,
    body: str | Unset = UNSET,
    filename: str,
    path_prefix: UpdateConfigFilePathPrefix,
) -> Response[Any | ErrorResponse]:
    """update a base system config file (e.g. edu-sharing.conf)

    Args:
        filename (str):
        path_prefix (UpdateConfigFilePathPrefix):
        body (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ErrorResponse]
    """

    kwargs = _get_kwargs(
        body=body,
        filename=filename,
        path_prefix=path_prefix,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: str | Unset = UNSET,
    filename: str,
    path_prefix: UpdateConfigFilePathPrefix,
) -> Any | ErrorResponse | None:
    """update a base system config file (e.g. edu-sharing.conf)

    Args:
        filename (str):
        path_prefix (UpdateConfigFilePathPrefix):
        body (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ErrorResponse
    """

    return sync_detailed(
        client=client,
        body=body,
        filename=filename,
        path_prefix=path_prefix,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: str | Unset = UNSET,
    filename: str,
    path_prefix: UpdateConfigFilePathPrefix,
) -> Response[Any | ErrorResponse]:
    """update a base system config file (e.g. edu-sharing.conf)

    Args:
        filename (str):
        path_prefix (UpdateConfigFilePathPrefix):
        body (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ErrorResponse]
    """

    kwargs = _get_kwargs(
        body=body,
        filename=filename,
        path_prefix=path_prefix,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: str | Unset = UNSET,
    filename: str,
    path_prefix: UpdateConfigFilePathPrefix,
) -> Any | ErrorResponse | None:
    """update a base system config file (e.g. edu-sharing.conf)

    Args:
        filename (str):
        path_prefix (UpdateConfigFilePathPrefix):
        body (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ErrorResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            filename=filename,
            path_prefix=path_prefix,
        )
    ).parsed
