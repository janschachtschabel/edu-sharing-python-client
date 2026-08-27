from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.mds_value import MdsValue
from ...types import UNSET, Response, Unset


def _get_kwargs(
    repository: str,
    metadataset: str,
    widget: str,
    *,
    caption: str,
    parent: str | Unset = UNSET,
    node_id: list[str] | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["caption"] = caption

    params["parent"] = parent

    json_node_id: list[str] | Unset = UNSET
    if not isinstance(node_id, Unset):
        json_node_id = node_id

    params["nodeId"] = json_node_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/mds/v1/metadatasets/{repository}/{metadataset}/values/{widget}/suggest".format(
            repository=quote(str(repository), safe=""),
            metadataset=quote(str(metadataset), safe=""),
            widget=quote(str(widget), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | MdsValue | None:
    if response.status_code == 200:
        response_200 = MdsValue.from_dict(response.json())

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
) -> Response[ErrorResponse | MdsValue]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    repository: str,
    metadataset: str,
    widget: str,
    *,
    client: AuthenticatedClient | Client,
    caption: str,
    parent: str | Unset = UNSET,
    node_id: list[str] | Unset = UNSET,
) -> Response[ErrorResponse | MdsValue]:
    """Suggest a value.

     Suggest a new value for a given metadataset and widget. The suggestion will be forwarded to the
    corresponding person in the metadataset file

    Args:
        repository (str):
        metadataset (str):
        widget (str):
        caption (str):
        parent (str | Unset):
        node_id (list[str] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | MdsValue]
    """

    kwargs = _get_kwargs(
        repository=repository,
        metadataset=metadataset,
        widget=widget,
        caption=caption,
        parent=parent,
        node_id=node_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repository: str,
    metadataset: str,
    widget: str,
    *,
    client: AuthenticatedClient | Client,
    caption: str,
    parent: str | Unset = UNSET,
    node_id: list[str] | Unset = UNSET,
) -> ErrorResponse | MdsValue | None:
    """Suggest a value.

     Suggest a new value for a given metadataset and widget. The suggestion will be forwarded to the
    corresponding person in the metadataset file

    Args:
        repository (str):
        metadataset (str):
        widget (str):
        caption (str):
        parent (str | Unset):
        node_id (list[str] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | MdsValue
    """

    return sync_detailed(
        repository=repository,
        metadataset=metadataset,
        widget=widget,
        client=client,
        caption=caption,
        parent=parent,
        node_id=node_id,
    ).parsed


async def asyncio_detailed(
    repository: str,
    metadataset: str,
    widget: str,
    *,
    client: AuthenticatedClient | Client,
    caption: str,
    parent: str | Unset = UNSET,
    node_id: list[str] | Unset = UNSET,
) -> Response[ErrorResponse | MdsValue]:
    """Suggest a value.

     Suggest a new value for a given metadataset and widget. The suggestion will be forwarded to the
    corresponding person in the metadataset file

    Args:
        repository (str):
        metadataset (str):
        widget (str):
        caption (str):
        parent (str | Unset):
        node_id (list[str] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | MdsValue]
    """

    kwargs = _get_kwargs(
        repository=repository,
        metadataset=metadataset,
        widget=widget,
        caption=caption,
        parent=parent,
        node_id=node_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    metadataset: str,
    widget: str,
    *,
    client: AuthenticatedClient | Client,
    caption: str,
    parent: str | Unset = UNSET,
    node_id: list[str] | Unset = UNSET,
) -> ErrorResponse | MdsValue | None:
    """Suggest a value.

     Suggest a new value for a given metadataset and widget. The suggestion will be forwarded to the
    corresponding person in the metadataset file

    Args:
        repository (str):
        metadataset (str):
        widget (str):
        caption (str):
        parent (str | Unset):
        node_id (list[str] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | MdsValue
    """

    return (
        await asyncio_detailed(
            repository=repository,
            metadataset=metadataset,
            widget=widget,
            client=client,
            caption=caption,
            parent=parent,
            node_id=node_id,
        )
    ).parsed
