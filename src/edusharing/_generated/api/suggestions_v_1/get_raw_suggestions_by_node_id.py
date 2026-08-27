from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_raw_suggestions_by_node_id_status_item import GetRawSuggestionsByNodeIdStatusItem
from ...models.property_suggestion import PropertySuggestion
from ...types import UNSET, Response, Unset


def _get_kwargs(
    repository: str,
    node: str,
    *,
    status: list[GetRawSuggestionsByNodeIdStatusItem] | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_status: list[str] | Unset = UNSET
    if not isinstance(status, Unset):
        json_status = []
        for status_item_data in status:
            status_item = status_item_data.value
            json_status.append(status_item)

    params["status"] = json_status

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/suggestions/v1/{repository}/{node}/raw".format(
            repository=quote(str(repository), safe=""),
            node=quote(str(node), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> list[PropertySuggestion] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = PropertySuggestion.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[list[PropertySuggestion]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    repository: str,
    node: str,
    *,
    client: AuthenticatedClient | Client,
    status: list[GetRawSuggestionsByNodeIdStatusItem] | Unset = UNSET,
) -> Response[list[PropertySuggestion]]:
    """Retrieve stored suggestion for the given nodeId in the raw format

    Args:
        repository (str):
        node (str):
        status (list[GetRawSuggestionsByNodeIdStatusItem] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list[PropertySuggestion]]
    """

    kwargs = _get_kwargs(
        repository=repository,
        node=node,
        status=status,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repository: str,
    node: str,
    *,
    client: AuthenticatedClient | Client,
    status: list[GetRawSuggestionsByNodeIdStatusItem] | Unset = UNSET,
) -> list[PropertySuggestion] | None:
    """Retrieve stored suggestion for the given nodeId in the raw format

    Args:
        repository (str):
        node (str):
        status (list[GetRawSuggestionsByNodeIdStatusItem] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list[PropertySuggestion]
    """

    return sync_detailed(
        repository=repository,
        node=node,
        client=client,
        status=status,
    ).parsed


async def asyncio_detailed(
    repository: str,
    node: str,
    *,
    client: AuthenticatedClient | Client,
    status: list[GetRawSuggestionsByNodeIdStatusItem] | Unset = UNSET,
) -> Response[list[PropertySuggestion]]:
    """Retrieve stored suggestion for the given nodeId in the raw format

    Args:
        repository (str):
        node (str):
        status (list[GetRawSuggestionsByNodeIdStatusItem] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list[PropertySuggestion]]
    """

    kwargs = _get_kwargs(
        repository=repository,
        node=node,
        status=status,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    node: str,
    *,
    client: AuthenticatedClient | Client,
    status: list[GetRawSuggestionsByNodeIdStatusItem] | Unset = UNSET,
) -> list[PropertySuggestion] | None:
    """Retrieve stored suggestion for the given nodeId in the raw format

    Args:
        repository (str):
        node (str):
        status (list[GetRawSuggestionsByNodeIdStatusItem] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list[PropertySuggestion]
    """

    return (
        await asyncio_detailed(
            repository=repository,
            node=node,
            client=client,
            status=status,
        )
    ).parsed
