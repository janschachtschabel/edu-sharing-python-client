from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.filter_ import Filter
from ...models.statistics import Statistics
from ...types import UNSET, Response, Unset


def _get_kwargs(
    context: str,
    *,
    body: Filter,
    properties: list[str] | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    json_properties: list[str] | Unset = UNSET
    if not isinstance(properties, Unset):
        json_properties = properties

    params["properties"] = json_properties

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/statistic/v1/facets/{context}".format(
            context=quote(str(context), safe=""),
        ),
        "params": params,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | Statistics | None:
    if response.status_code == 200:
        response_200 = Statistics.from_dict(response.json())

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
) -> Response[ErrorResponse | Statistics]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    context: str,
    *,
    client: AuthenticatedClient | Client,
    body: Filter,
    properties: list[str] | Unset = UNSET,
) -> Response[ErrorResponse | Statistics]:
    """Get statistics of repository.

     Statistics.

    Args:
        context (str):
        properties (list[str] | Unset):
        body (Filter):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | Statistics]
    """

    kwargs = _get_kwargs(
        context=context,
        body=body,
        properties=properties,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    context: str,
    *,
    client: AuthenticatedClient | Client,
    body: Filter,
    properties: list[str] | Unset = UNSET,
) -> ErrorResponse | Statistics | None:
    """Get statistics of repository.

     Statistics.

    Args:
        context (str):
        properties (list[str] | Unset):
        body (Filter):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | Statistics
    """

    return sync_detailed(
        context=context,
        client=client,
        body=body,
        properties=properties,
    ).parsed


async def asyncio_detailed(
    context: str,
    *,
    client: AuthenticatedClient | Client,
    body: Filter,
    properties: list[str] | Unset = UNSET,
) -> Response[ErrorResponse | Statistics]:
    """Get statistics of repository.

     Statistics.

    Args:
        context (str):
        properties (list[str] | Unset):
        body (Filter):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | Statistics]
    """

    kwargs = _get_kwargs(
        context=context,
        body=body,
        properties=properties,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    context: str,
    *,
    client: AuthenticatedClient | Client,
    body: Filter,
    properties: list[str] | Unset = UNSET,
) -> ErrorResponse | Statistics | None:
    """Get statistics of repository.

     Statistics.

    Args:
        context (str):
        properties (list[str] | Unset):
        body (Filter):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | Statistics
    """

    return (
        await asyncio_detailed(
            context=context,
            client=client,
            body=body,
            properties=properties,
        )
    ).parsed
