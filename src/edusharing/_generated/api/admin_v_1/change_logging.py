from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    name: str,
    loglevel: str,
    appender: str | Unset = "ConsoleAppender",
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["name"] = name

    params["loglevel"] = loglevel

    params["appender"] = appender

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/admin/v1/log/config",
        "params": params,
    }

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
    name: str,
    loglevel: str,
    appender: str | Unset = "ConsoleAppender",
) -> Response[Any | ErrorResponse]:
    """Change the loglevel for classes at runtime.

     Root appenders are used. Check the appender treshold.

    Args:
        name (str):
        loglevel (str):
        appender (str | Unset):  Default: 'ConsoleAppender'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ErrorResponse]
    """

    kwargs = _get_kwargs(
        name=name,
        loglevel=loglevel,
        appender=appender,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    name: str,
    loglevel: str,
    appender: str | Unset = "ConsoleAppender",
) -> Any | ErrorResponse | None:
    """Change the loglevel for classes at runtime.

     Root appenders are used. Check the appender treshold.

    Args:
        name (str):
        loglevel (str):
        appender (str | Unset):  Default: 'ConsoleAppender'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ErrorResponse
    """

    return sync_detailed(
        client=client,
        name=name,
        loglevel=loglevel,
        appender=appender,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    name: str,
    loglevel: str,
    appender: str | Unset = "ConsoleAppender",
) -> Response[Any | ErrorResponse]:
    """Change the loglevel for classes at runtime.

     Root appenders are used. Check the appender treshold.

    Args:
        name (str):
        loglevel (str):
        appender (str | Unset):  Default: 'ConsoleAppender'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ErrorResponse]
    """

    kwargs = _get_kwargs(
        name=name,
        loglevel=loglevel,
        appender=appender,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    name: str,
    loglevel: str,
    appender: str | Unset = "ConsoleAppender",
) -> Any | ErrorResponse | None:
    """Change the loglevel for classes at runtime.

     Root appenders are used. Check the appender treshold.

    Args:
        name (str):
        loglevel (str):
        appender (str | Unset):  Default: 'ConsoleAppender'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ErrorResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            name=name,
            loglevel=loglevel,
            appender=appender,
        )
    ).parsed
