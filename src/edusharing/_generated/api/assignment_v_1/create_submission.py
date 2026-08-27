from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.submission import Submission
from ...types import UNSET, Response


def _get_kwargs(
    assignment_id: str,
    *,
    user: str,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["user"] = user

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/assignment/v1/{assignment_id}/submissions/create".format(
            assignment_id=quote(str(assignment_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | Submission | None:
    if response.status_code == 200:
        response_200 = Submission.from_dict(response.json())

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
) -> Response[ErrorResponse | Submission]:
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
    user: str,
) -> Response[ErrorResponse | Submission]:
    """create submission

     create submission by username

    Args:
        assignment_id (str):
        user (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | Submission]
    """

    kwargs = _get_kwargs(
        assignment_id=assignment_id,
        user=user,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    assignment_id: str,
    *,
    client: AuthenticatedClient | Client,
    user: str,
) -> ErrorResponse | Submission | None:
    """create submission

     create submission by username

    Args:
        assignment_id (str):
        user (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | Submission
    """

    return sync_detailed(
        assignment_id=assignment_id,
        client=client,
        user=user,
    ).parsed


async def asyncio_detailed(
    assignment_id: str,
    *,
    client: AuthenticatedClient | Client,
    user: str,
) -> Response[ErrorResponse | Submission]:
    """create submission

     create submission by username

    Args:
        assignment_id (str):
        user (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | Submission]
    """

    kwargs = _get_kwargs(
        assignment_id=assignment_id,
        user=user,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    assignment_id: str,
    *,
    client: AuthenticatedClient | Client,
    user: str,
) -> ErrorResponse | Submission | None:
    """create submission

     create submission by username

    Args:
        assignment_id (str):
        user (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | Submission
    """

    return (
        await asyncio_detailed(
            assignment_id=assignment_id,
            client=client,
            user=user,
        )
    ).parsed
