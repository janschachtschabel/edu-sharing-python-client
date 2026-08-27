from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.search_parameters import SearchParameters
from ...types import UNSET, Response, Unset


def _get_kwargs(
    repository: str,
    mediacenter: str,
    *,
    body: SearchParameters,
    sort_properties: list[str] | Unset = UNSET,
    sort_ascending: list[bool] | Unset = UNSET,
    properties: list[str] | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    json_sort_properties: list[str] | Unset = UNSET
    if not isinstance(sort_properties, Unset):
        json_sort_properties = sort_properties

    params["sortProperties"] = json_sort_properties

    json_sort_ascending: list[bool] | Unset = UNSET
    if not isinstance(sort_ascending, Unset):
        json_sort_ascending = sort_ascending

    params["sortAscending"] = json_sort_ascending

    json_properties: list[str] | Unset = UNSET
    if not isinstance(properties, Unset):
        json_properties = properties

    params["properties"] = json_properties

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/mediacenter/v1/mediacenter/{repository}/{mediacenter}/licenses/export".format(
            repository=quote(str(repository), safe=""),
            mediacenter=quote(str(mediacenter), safe=""),
        ),
        "params": params,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | str | None:
    if response.status_code == 200:
        response_200 = cast(str, response.json())
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
) -> Response[ErrorResponse | str]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    repository: str,
    mediacenter: str,
    *,
    client: AuthenticatedClient | Client,
    body: SearchParameters,
    sort_properties: list[str] | Unset = UNSET,
    sort_ascending: list[bool] | Unset = UNSET,
    properties: list[str] | Unset = UNSET,
) -> Response[ErrorResponse | str]:
    """get nodes that are licensed by the given mediacenter

     e.g. cm:name

    Args:
        repository (str):
        mediacenter (str):
        sort_properties (list[str] | Unset):
        sort_ascending (list[bool] | Unset):
        properties (list[str] | Unset):
        body (SearchParameters):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | str]
    """

    kwargs = _get_kwargs(
        repository=repository,
        mediacenter=mediacenter,
        body=body,
        sort_properties=sort_properties,
        sort_ascending=sort_ascending,
        properties=properties,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repository: str,
    mediacenter: str,
    *,
    client: AuthenticatedClient | Client,
    body: SearchParameters,
    sort_properties: list[str] | Unset = UNSET,
    sort_ascending: list[bool] | Unset = UNSET,
    properties: list[str] | Unset = UNSET,
) -> ErrorResponse | str | None:
    """get nodes that are licensed by the given mediacenter

     e.g. cm:name

    Args:
        repository (str):
        mediacenter (str):
        sort_properties (list[str] | Unset):
        sort_ascending (list[bool] | Unset):
        properties (list[str] | Unset):
        body (SearchParameters):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | str
    """

    return sync_detailed(
        repository=repository,
        mediacenter=mediacenter,
        client=client,
        body=body,
        sort_properties=sort_properties,
        sort_ascending=sort_ascending,
        properties=properties,
    ).parsed


async def asyncio_detailed(
    repository: str,
    mediacenter: str,
    *,
    client: AuthenticatedClient | Client,
    body: SearchParameters,
    sort_properties: list[str] | Unset = UNSET,
    sort_ascending: list[bool] | Unset = UNSET,
    properties: list[str] | Unset = UNSET,
) -> Response[ErrorResponse | str]:
    """get nodes that are licensed by the given mediacenter

     e.g. cm:name

    Args:
        repository (str):
        mediacenter (str):
        sort_properties (list[str] | Unset):
        sort_ascending (list[bool] | Unset):
        properties (list[str] | Unset):
        body (SearchParameters):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | str]
    """

    kwargs = _get_kwargs(
        repository=repository,
        mediacenter=mediacenter,
        body=body,
        sort_properties=sort_properties,
        sort_ascending=sort_ascending,
        properties=properties,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    mediacenter: str,
    *,
    client: AuthenticatedClient | Client,
    body: SearchParameters,
    sort_properties: list[str] | Unset = UNSET,
    sort_ascending: list[bool] | Unset = UNSET,
    properties: list[str] | Unset = UNSET,
) -> ErrorResponse | str | None:
    """get nodes that are licensed by the given mediacenter

     e.g. cm:name

    Args:
        repository (str):
        mediacenter (str):
        sort_properties (list[str] | Unset):
        sort_ascending (list[bool] | Unset):
        properties (list[str] | Unset):
        body (SearchParameters):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | str
    """

    return (
        await asyncio_detailed(
            repository=repository,
            mediacenter=mediacenter,
            client=client,
            body=body,
            sort_properties=sort_properties,
            sort_ascending=sort_ascending,
            properties=properties,
        )
    ).parsed
