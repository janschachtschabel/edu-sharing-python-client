from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.assignment import Assignment
from ...models.create_or_update_assignment_1_status import CreateOrUpdateAssignment1Status
from ...models.error_response import ErrorResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    assignment_id: str,
    *,
    status: CreateOrUpdateAssignment1Status | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_status: str | Unset = UNSET
    if not isinstance(status, Unset):
        json_status = status.value

    params["status"] = json_status

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/assignment/v1/{assignment_id}/status".format(
            assignment_id=quote(str(assignment_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Assignment | ErrorResponse | None:
    if response.status_code == 200:
        response_200 = Assignment.from_dict(response.json())

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
) -> Response[Assignment | ErrorResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    assignment_id: str,
    *,
    client: AuthenticatedClient | Client,
    status: CreateOrUpdateAssignment1Status | Unset = UNSET,
) -> Response[Assignment | ErrorResponse]:
    """Set assignment Status

     Set assignment Status.

    Args:
        assignment_id (str):
        status (CreateOrUpdateAssignment1Status | Unset): Status of the assignment
            * DRAFT: Assignment is in draft state, only visible to creator
            * ASSIGNED: Assignment is assigned and visible to all users with assignee permission
            * CORRECTED: All submissions of this Assignment have been finished (only for type
            submission)
            * FINISHED: Assignment has been completed
            * CANCELED: Assignment has been canceled

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Assignment | ErrorResponse]
    """

    kwargs = _get_kwargs(
        assignment_id=assignment_id,
        status=status,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    assignment_id: str,
    *,
    client: AuthenticatedClient | Client,
    status: CreateOrUpdateAssignment1Status | Unset = UNSET,
) -> Assignment | ErrorResponse | None:
    """Set assignment Status

     Set assignment Status.

    Args:
        assignment_id (str):
        status (CreateOrUpdateAssignment1Status | Unset): Status of the assignment
            * DRAFT: Assignment is in draft state, only visible to creator
            * ASSIGNED: Assignment is assigned and visible to all users with assignee permission
            * CORRECTED: All submissions of this Assignment have been finished (only for type
            submission)
            * FINISHED: Assignment has been completed
            * CANCELED: Assignment has been canceled

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Assignment | ErrorResponse
    """

    return sync_detailed(
        assignment_id=assignment_id,
        client=client,
        status=status,
    ).parsed


async def asyncio_detailed(
    assignment_id: str,
    *,
    client: AuthenticatedClient | Client,
    status: CreateOrUpdateAssignment1Status | Unset = UNSET,
) -> Response[Assignment | ErrorResponse]:
    """Set assignment Status

     Set assignment Status.

    Args:
        assignment_id (str):
        status (CreateOrUpdateAssignment1Status | Unset): Status of the assignment
            * DRAFT: Assignment is in draft state, only visible to creator
            * ASSIGNED: Assignment is assigned and visible to all users with assignee permission
            * CORRECTED: All submissions of this Assignment have been finished (only for type
            submission)
            * FINISHED: Assignment has been completed
            * CANCELED: Assignment has been canceled

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Assignment | ErrorResponse]
    """

    kwargs = _get_kwargs(
        assignment_id=assignment_id,
        status=status,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    assignment_id: str,
    *,
    client: AuthenticatedClient | Client,
    status: CreateOrUpdateAssignment1Status | Unset = UNSET,
) -> Assignment | ErrorResponse | None:
    """Set assignment Status

     Set assignment Status.

    Args:
        assignment_id (str):
        status (CreateOrUpdateAssignment1Status | Unset): Status of the assignment
            * DRAFT: Assignment is in draft state, only visible to creator
            * ASSIGNED: Assignment is assigned and visible to all users with assignee permission
            * CORRECTED: All submissions of this Assignment have been finished (only for type
            submission)
            * FINISHED: Assignment has been completed
            * CANCELED: Assignment has been canceled

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Assignment | ErrorResponse
    """

    return (
        await asyncio_detailed(
            assignment_id=assignment_id,
            client=client,
            status=status,
        )
    ).parsed
