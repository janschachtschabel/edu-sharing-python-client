import datetime
from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.get_by_organization_async_content_type import GetByOrganizationAsyncContentType
from ...types import UNSET, Response, Unset


def _get_kwargs(
    org_id: str,
    *,
    body: list[list[str]] | Unset = UNSET,
    date_from: datetime.datetime,
    date_to: datetime.datetime,
    published: bool | Unset = UNSET,
    content_type: GetByOrganizationAsyncContentType | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    json_date_from = date_from.isoformat()
    params["dateFrom"] = json_date_from

    json_date_to = date_to.isoformat()
    params["dateTo"] = json_date_to

    params["published"] = published

    json_content_type: str | Unset = UNSET
    if not isinstance(content_type, Unset):
        json_content_type = content_type.value

    params["contentType"] = json_content_type

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/statistic/v1/statistics/nodes/organization/{org_id}/complete".format(
            org_id=quote(str(org_id), safe=""),
        ),
        "params": params,
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = []
        for body_item_data in body:
            body_item = body_item_data

            _kwargs["json"].append(body_item)

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | ErrorResponse | None:
    if response.status_code == 200:
        response_200 = cast(Any, None)
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
) -> Response[Any | ErrorResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    org_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: list[list[str]] | Unset = UNSET,
    date_from: datetime.datetime,
    date_to: datetime.datetime,
    published: bool | Unset = UNSET,
    content_type: GetByOrganizationAsyncContentType | Unset = UNSET,
) -> Response[Any | ErrorResponse]:
    """Schedules a asynchronous job to retrieve statistics for node actions for the given organization. The
    result will be added to your inbox in form of an csv.

     requires toolpermission TOOLPERMISSION_ORGANIZATION_STATISTICS_NODES

    Args:
        org_id (str):
        date_from (datetime.datetime):
        date_to (datetime.datetime):
        published (bool | Unset):
        content_type (GetByOrganizationAsyncContentType | Unset):
        body (list[list[str]] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ErrorResponse]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        body=body,
        date_from=date_from,
        date_to=date_to,
        published=published,
        content_type=content_type,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    org_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: list[list[str]] | Unset = UNSET,
    date_from: datetime.datetime,
    date_to: datetime.datetime,
    published: bool | Unset = UNSET,
    content_type: GetByOrganizationAsyncContentType | Unset = UNSET,
) -> Any | ErrorResponse | None:
    """Schedules a asynchronous job to retrieve statistics for node actions for the given organization. The
    result will be added to your inbox in form of an csv.

     requires toolpermission TOOLPERMISSION_ORGANIZATION_STATISTICS_NODES

    Args:
        org_id (str):
        date_from (datetime.datetime):
        date_to (datetime.datetime):
        published (bool | Unset):
        content_type (GetByOrganizationAsyncContentType | Unset):
        body (list[list[str]] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ErrorResponse
    """

    return sync_detailed(
        org_id=org_id,
        client=client,
        body=body,
        date_from=date_from,
        date_to=date_to,
        published=published,
        content_type=content_type,
    ).parsed


async def asyncio_detailed(
    org_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: list[list[str]] | Unset = UNSET,
    date_from: datetime.datetime,
    date_to: datetime.datetime,
    published: bool | Unset = UNSET,
    content_type: GetByOrganizationAsyncContentType | Unset = UNSET,
) -> Response[Any | ErrorResponse]:
    """Schedules a asynchronous job to retrieve statistics for node actions for the given organization. The
    result will be added to your inbox in form of an csv.

     requires toolpermission TOOLPERMISSION_ORGANIZATION_STATISTICS_NODES

    Args:
        org_id (str):
        date_from (datetime.datetime):
        date_to (datetime.datetime):
        published (bool | Unset):
        content_type (GetByOrganizationAsyncContentType | Unset):
        body (list[list[str]] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ErrorResponse]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        body=body,
        date_from=date_from,
        date_to=date_to,
        published=published,
        content_type=content_type,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    org_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: list[list[str]] | Unset = UNSET,
    date_from: datetime.datetime,
    date_to: datetime.datetime,
    published: bool | Unset = UNSET,
    content_type: GetByOrganizationAsyncContentType | Unset = UNSET,
) -> Any | ErrorResponse | None:
    """Schedules a asynchronous job to retrieve statistics for node actions for the given organization. The
    result will be added to your inbox in form of an csv.

     requires toolpermission TOOLPERMISSION_ORGANIZATION_STATISTICS_NODES

    Args:
        org_id (str):
        date_from (datetime.datetime):
        date_to (datetime.datetime):
        published (bool | Unset):
        content_type (GetByOrganizationAsyncContentType | Unset):
        body (list[list[str]] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ErrorResponse
    """

    return (
        await asyncio_detailed(
            org_id=org_id,
            client=client,
            body=body,
            date_from=date_from,
            date_to=date_to,
            published=published,
            content_type=content_type,
        )
    ).parsed
