from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.qa_entry_response_dto import QAEntryResponseDTO
from ...types import UNSET, Response, Unset


def _get_kwargs(
    node_id: str,
    *,
    creator: str | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["creator"] = creator

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/qa/v1/{node_id}".format(
            node_id=quote(str(node_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | list[QAEntryResponseDTO] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = QAEntryResponseDTO.from_dict(response_200_item_data)

            response_200.append(response_200_item)

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
) -> Response[ErrorResponse | list[QAEntryResponseDTO]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    node_id: str,
    *,
    client: AuthenticatedClient | Client,
    creator: str | Unset = UNSET,
) -> Response[ErrorResponse | list[QAEntryResponseDTO]]:
    """Get all QA Entries of a specific nodeId or nodeId and creator

    Args:
        node_id (str):
        creator (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | list[QAEntryResponseDTO]]
    """

    kwargs = _get_kwargs(
        node_id=node_id,
        creator=creator,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    node_id: str,
    *,
    client: AuthenticatedClient | Client,
    creator: str | Unset = UNSET,
) -> ErrorResponse | list[QAEntryResponseDTO] | None:
    """Get all QA Entries of a specific nodeId or nodeId and creator

    Args:
        node_id (str):
        creator (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | list[QAEntryResponseDTO]
    """

    return sync_detailed(
        node_id=node_id,
        client=client,
        creator=creator,
    ).parsed


async def asyncio_detailed(
    node_id: str,
    *,
    client: AuthenticatedClient | Client,
    creator: str | Unset = UNSET,
) -> Response[ErrorResponse | list[QAEntryResponseDTO]]:
    """Get all QA Entries of a specific nodeId or nodeId and creator

    Args:
        node_id (str):
        creator (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | list[QAEntryResponseDTO]]
    """

    kwargs = _get_kwargs(
        node_id=node_id,
        creator=creator,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    node_id: str,
    *,
    client: AuthenticatedClient | Client,
    creator: str | Unset = UNSET,
) -> ErrorResponse | list[QAEntryResponseDTO] | None:
    """Get all QA Entries of a specific nodeId or nodeId and creator

    Args:
        node_id (str):
        creator (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | list[QAEntryResponseDTO]
    """

    return (
        await asyncio_detailed(
            node_id=node_id,
            client=client,
            creator=creator,
        )
    ).parsed
