from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.suggestion_param import SuggestionParam
from ...models.suggestions import Suggestions
from ...types import UNSET, Response, Unset


def _get_kwargs(
    repository: str,
    metadataset: str,
    *,
    body: SuggestionParam | Unset = UNSET,
    locale: str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(locale, Unset):
        headers["locale"] = locale

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/mds/v1/metadatasets/{repository}/{metadataset}/values".format(
            repository=quote(str(repository), safe=""),
            metadataset=quote(str(metadataset), safe=""),
        ),
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | Suggestions | None:
    if response.status_code == 200:
        response_200 = Suggestions.from_dict(response.json())

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
) -> Response[ErrorResponse | Suggestions]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    repository: str,
    metadataset: str,
    *,
    client: AuthenticatedClient | Client,
    body: SuggestionParam | Unset = UNSET,
    locale: str | Unset = UNSET,
) -> Response[ErrorResponse | Suggestions]:
    """Get values.

     Get values.

    Args:
        repository (str):
        metadataset (str):
        locale (str | Unset):  Example: de_DE.
        body (SuggestionParam | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | Suggestions]
    """

    kwargs = _get_kwargs(
        repository=repository,
        metadataset=metadataset,
        body=body,
        locale=locale,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repository: str,
    metadataset: str,
    *,
    client: AuthenticatedClient | Client,
    body: SuggestionParam | Unset = UNSET,
    locale: str | Unset = UNSET,
) -> ErrorResponse | Suggestions | None:
    """Get values.

     Get values.

    Args:
        repository (str):
        metadataset (str):
        locale (str | Unset):  Example: de_DE.
        body (SuggestionParam | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | Suggestions
    """

    return sync_detailed(
        repository=repository,
        metadataset=metadataset,
        client=client,
        body=body,
        locale=locale,
    ).parsed


async def asyncio_detailed(
    repository: str,
    metadataset: str,
    *,
    client: AuthenticatedClient | Client,
    body: SuggestionParam | Unset = UNSET,
    locale: str | Unset = UNSET,
) -> Response[ErrorResponse | Suggestions]:
    """Get values.

     Get values.

    Args:
        repository (str):
        metadataset (str):
        locale (str | Unset):  Example: de_DE.
        body (SuggestionParam | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | Suggestions]
    """

    kwargs = _get_kwargs(
        repository=repository,
        metadataset=metadataset,
        body=body,
        locale=locale,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    metadataset: str,
    *,
    client: AuthenticatedClient | Client,
    body: SuggestionParam | Unset = UNSET,
    locale: str | Unset = UNSET,
) -> ErrorResponse | Suggestions | None:
    """Get values.

     Get values.

    Args:
        repository (str):
        metadataset (str):
        locale (str | Unset):  Example: de_DE.
        body (SuggestionParam | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | Suggestions
    """

    return (
        await asyncio_detailed(
            repository=repository,
            metadataset=metadataset,
            client=client,
            body=body,
            locale=locale,
        )
    ).parsed
