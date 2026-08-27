from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.approve_relation_type import ApproveRelationType
from ...models.error_response import ErrorResponse
from ...models.node_relation_data import NodeRelationData
from ...types import Response


def _get_kwargs(
    repository: str,
    source: str,
    type_: ApproveRelationType,
    target: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/relation/v1/{repository}/{source}/{type_}/{target}/approve".format(
            repository=quote(str(repository), safe=""),
            source=quote(str(source), safe=""),
            type_=quote(str(type_), safe=""),
            target=quote(str(target), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | NodeRelationData | None:
    if response.status_code == 200:
        response_200 = NodeRelationData.from_dict(response.json())

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
) -> Response[ErrorResponse | NodeRelationData]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    repository: str,
    source: str,
    type_: ApproveRelationType,
    target: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[ErrorResponse | NodeRelationData]:
    """create a relation between nodes

     Creates a relation between two nodes of the given type.

    Args:
        repository (str):
        source (str):
        type_ (ApproveRelationType):
        target (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | NodeRelationData]
    """

    kwargs = _get_kwargs(
        repository=repository,
        source=source,
        type_=type_,
        target=target,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repository: str,
    source: str,
    type_: ApproveRelationType,
    target: str,
    *,
    client: AuthenticatedClient | Client,
) -> ErrorResponse | NodeRelationData | None:
    """create a relation between nodes

     Creates a relation between two nodes of the given type.

    Args:
        repository (str):
        source (str):
        type_ (ApproveRelationType):
        target (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | NodeRelationData
    """

    return sync_detailed(
        repository=repository,
        source=source,
        type_=type_,
        target=target,
        client=client,
    ).parsed


async def asyncio_detailed(
    repository: str,
    source: str,
    type_: ApproveRelationType,
    target: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[ErrorResponse | NodeRelationData]:
    """create a relation between nodes

     Creates a relation between two nodes of the given type.

    Args:
        repository (str):
        source (str):
        type_ (ApproveRelationType):
        target (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | NodeRelationData]
    """

    kwargs = _get_kwargs(
        repository=repository,
        source=source,
        type_=type_,
        target=target,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    source: str,
    type_: ApproveRelationType,
    target: str,
    *,
    client: AuthenticatedClient | Client,
) -> ErrorResponse | NodeRelationData | None:
    """create a relation between nodes

     Creates a relation between two nodes of the given type.

    Args:
        repository (str):
        source (str):
        type_ (ApproveRelationType):
        target (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | NodeRelationData
    """

    return (
        await asyncio_detailed(
            repository=repository,
            source=source,
            type_=type_,
            target=target,
            client=client,
        )
    ).parsed
