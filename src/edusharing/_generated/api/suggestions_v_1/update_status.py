from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.suggestion_response_dto import SuggestionResponseDTO
from ...models.update_status_status import UpdateStatusStatus
from ...types import UNSET, Response, Unset


def _get_kwargs(
    repository: str,
    node: str,
    *,
    id: list[str] | Unset = UNSET,
    status: UpdateStatusStatus | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_id: list[str] | Unset = UNSET
    if not isinstance(id, Unset):
        json_id = id

    params["id"] = json_id

    json_status: str | Unset = UNSET
    if not isinstance(status, Unset):
        json_status = status.value

    params["status"] = json_status

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/suggestions/v1/{repository}/{node}".format(
            repository=quote(str(repository), safe=""),
            node=quote(str(node), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> list[SuggestionResponseDTO] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = SuggestionResponseDTO.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[list[SuggestionResponseDTO]]:
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
    id: list[str] | Unset = UNSET,
    status: UpdateStatusStatus | Unset = UNSET,
) -> Response[list[SuggestionResponseDTO]]:
    """Update suggestion status

    Args:
        repository (str):
        node (str):
        id (list[str] | Unset):
        status (UpdateStatusStatus | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list[SuggestionResponseDTO]]
    """

    kwargs = _get_kwargs(
        repository=repository,
        node=node,
        id=id,
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
    id: list[str] | Unset = UNSET,
    status: UpdateStatusStatus | Unset = UNSET,
) -> list[SuggestionResponseDTO] | None:
    """Update suggestion status

    Args:
        repository (str):
        node (str):
        id (list[str] | Unset):
        status (UpdateStatusStatus | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list[SuggestionResponseDTO]
    """

    return sync_detailed(
        repository=repository,
        node=node,
        client=client,
        id=id,
        status=status,
    ).parsed


async def asyncio_detailed(
    repository: str,
    node: str,
    *,
    client: AuthenticatedClient | Client,
    id: list[str] | Unset = UNSET,
    status: UpdateStatusStatus | Unset = UNSET,
) -> Response[list[SuggestionResponseDTO]]:
    """Update suggestion status

    Args:
        repository (str):
        node (str):
        id (list[str] | Unset):
        status (UpdateStatusStatus | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list[SuggestionResponseDTO]]
    """

    kwargs = _get_kwargs(
        repository=repository,
        node=node,
        id=id,
        status=status,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    node: str,
    *,
    client: AuthenticatedClient | Client,
    id: list[str] | Unset = UNSET,
    status: UpdateStatusStatus | Unset = UNSET,
) -> list[SuggestionResponseDTO] | None:
    """Update suggestion status

    Args:
        repository (str):
        node (str):
        id (list[str] | Unset):
        status (UpdateStatusStatus | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list[SuggestionResponseDTO]
    """

    return (
        await asyncio_detailed(
            repository=repository,
            node=node,
            client=client,
            id=id,
            status=status,
        )
    ).parsed
