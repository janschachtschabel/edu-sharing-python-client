from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.import_oai_xml_body import ImportOaiXMLBody
from ...models.node import Node
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: ImportOaiXMLBody | Unset = UNSET,
    record_handler_class_name: str
    | Unset = "org.edu_sharing.repository.server.importer.RecordHandlerLOM",
    binary_handler_class_name: str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["recordHandlerClassName"] = record_handler_class_name

    params["binaryHandlerClassName"] = binary_handler_class_name

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/admin/v1/import/oai/xml",
        "params": params,
    }

    if not isinstance(body, Unset):
        _kwargs["files"] = body.to_multipart()

    headers["Content-Type"] = "multipart/form-data; boundary=+++"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | Node | None:
    if response.status_code == 200:
        response_200 = Node.from_dict(response.json())

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
) -> Response[ErrorResponse | Node]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: ImportOaiXMLBody | Unset = UNSET,
    record_handler_class_name: str
    | Unset = "org.edu_sharing.repository.server.importer.RecordHandlerLOM",
    binary_handler_class_name: str | Unset = UNSET,
) -> Response[ErrorResponse | Node]:
    """Import single xml via oai (for testing)

    Args:
        record_handler_class_name (str | Unset):  Default:
            'org.edu_sharing.repository.server.importer.RecordHandlerLOM'.
        binary_handler_class_name (str | Unset):
        body (ImportOaiXMLBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | Node]
    """

    kwargs = _get_kwargs(
        body=body,
        record_handler_class_name=record_handler_class_name,
        binary_handler_class_name=binary_handler_class_name,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: ImportOaiXMLBody | Unset = UNSET,
    record_handler_class_name: str
    | Unset = "org.edu_sharing.repository.server.importer.RecordHandlerLOM",
    binary_handler_class_name: str | Unset = UNSET,
) -> ErrorResponse | Node | None:
    """Import single xml via oai (for testing)

    Args:
        record_handler_class_name (str | Unset):  Default:
            'org.edu_sharing.repository.server.importer.RecordHandlerLOM'.
        binary_handler_class_name (str | Unset):
        body (ImportOaiXMLBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | Node
    """

    return sync_detailed(
        client=client,
        body=body,
        record_handler_class_name=record_handler_class_name,
        binary_handler_class_name=binary_handler_class_name,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: ImportOaiXMLBody | Unset = UNSET,
    record_handler_class_name: str
    | Unset = "org.edu_sharing.repository.server.importer.RecordHandlerLOM",
    binary_handler_class_name: str | Unset = UNSET,
) -> Response[ErrorResponse | Node]:
    """Import single xml via oai (for testing)

    Args:
        record_handler_class_name (str | Unset):  Default:
            'org.edu_sharing.repository.server.importer.RecordHandlerLOM'.
        binary_handler_class_name (str | Unset):
        body (ImportOaiXMLBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | Node]
    """

    kwargs = _get_kwargs(
        body=body,
        record_handler_class_name=record_handler_class_name,
        binary_handler_class_name=binary_handler_class_name,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: ImportOaiXMLBody | Unset = UNSET,
    record_handler_class_name: str
    | Unset = "org.edu_sharing.repository.server.importer.RecordHandlerLOM",
    binary_handler_class_name: str | Unset = UNSET,
) -> ErrorResponse | Node | None:
    """Import single xml via oai (for testing)

    Args:
        record_handler_class_name (str | Unset):  Default:
            'org.edu_sharing.repository.server.importer.RecordHandlerLOM'.
        binary_handler_class_name (str | Unset):
        body (ImportOaiXMLBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | Node
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            record_handler_class_name=record_handler_class_name,
            binary_handler_class_name=binary_handler_class_name,
        )
    ).parsed
