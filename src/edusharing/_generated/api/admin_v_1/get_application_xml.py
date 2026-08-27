from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.get_application_xml_response_200 import GetApplicationXMLResponse200
from ...types import Response


def _get_kwargs(
    xml: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/admin/v1/applications/{xml}".format(
            xml=quote(str(xml), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | GetApplicationXMLResponse200 | None:
    if response.status_code == 200:
        response_200 = GetApplicationXMLResponse200.from_dict(response.json())

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
) -> Response[ErrorResponse | GetApplicationXMLResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    xml: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[ErrorResponse | GetApplicationXMLResponse200]:
    """list any xml properties (like from homeApplication.properties.xml)

     list any xml properties (like from homeApplication.properties.xml)

    Args:
        xml (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | GetApplicationXMLResponse200]
    """

    kwargs = _get_kwargs(
        xml=xml,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    xml: str,
    *,
    client: AuthenticatedClient | Client,
) -> ErrorResponse | GetApplicationXMLResponse200 | None:
    """list any xml properties (like from homeApplication.properties.xml)

     list any xml properties (like from homeApplication.properties.xml)

    Args:
        xml (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | GetApplicationXMLResponse200
    """

    return sync_detailed(
        xml=xml,
        client=client,
    ).parsed


async def asyncio_detailed(
    xml: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[ErrorResponse | GetApplicationXMLResponse200]:
    """list any xml properties (like from homeApplication.properties.xml)

     list any xml properties (like from homeApplication.properties.xml)

    Args:
        xml (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | GetApplicationXMLResponse200]
    """

    kwargs = _get_kwargs(
        xml=xml,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    xml: str,
    *,
    client: AuthenticatedClient | Client,
) -> ErrorResponse | GetApplicationXMLResponse200 | None:
    """list any xml properties (like from homeApplication.properties.xml)

     list any xml properties (like from homeApplication.properties.xml)

    Args:
        xml (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | GetApplicationXMLResponse200
    """

    return (
        await asyncio_detailed(
            xml=xml,
            client=client,
        )
    ).parsed
