from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.dynamic_config import DynamicConfig
from ...models.error_response import ErrorResponse
from ...types import UNSET, Response


def _get_kwargs(
    key: str,
    *,
    body: str,
    public: bool,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["public"] = public

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/config/v1/dynamic/{key}".format(
            key=quote(str(key), safe=""),
        ),
        "params": params,
    }

    _kwargs["json"] = body

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> DynamicConfig | ErrorResponse | None:
    if response.status_code == 200:
        response_200 = DynamicConfig.from_dict(response.json())

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
) -> Response[DynamicConfig | ErrorResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    key: str,
    *,
    client: AuthenticatedClient | Client,
    body: str,
    public: bool,
) -> Response[DynamicConfig | ErrorResponse]:
    """Set a config entry (admin rights required)

     the body must be a json encapsulated string

    Args:
        key (str):
        public (bool):
        body (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DynamicConfig | ErrorResponse]
    """

    kwargs = _get_kwargs(
        key=key,
        body=body,
        public=public,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    key: str,
    *,
    client: AuthenticatedClient | Client,
    body: str,
    public: bool,
) -> DynamicConfig | ErrorResponse | None:
    """Set a config entry (admin rights required)

     the body must be a json encapsulated string

    Args:
        key (str):
        public (bool):
        body (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DynamicConfig | ErrorResponse
    """

    return sync_detailed(
        key=key,
        client=client,
        body=body,
        public=public,
    ).parsed


async def asyncio_detailed(
    key: str,
    *,
    client: AuthenticatedClient | Client,
    body: str,
    public: bool,
) -> Response[DynamicConfig | ErrorResponse]:
    """Set a config entry (admin rights required)

     the body must be a json encapsulated string

    Args:
        key (str):
        public (bool):
        body (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DynamicConfig | ErrorResponse]
    """

    kwargs = _get_kwargs(
        key=key,
        body=body,
        public=public,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    key: str,
    *,
    client: AuthenticatedClient | Client,
    body: str,
    public: bool,
) -> DynamicConfig | ErrorResponse | None:
    """Set a config entry (admin rights required)

     the body must be a json encapsulated string

    Args:
        key (str):
        public (bool):
        body (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DynamicConfig | ErrorResponse
    """

    return (
        await asyncio_detailed(
            key=key,
            client=client,
            body=body,
            public=public,
        )
    ).parsed
