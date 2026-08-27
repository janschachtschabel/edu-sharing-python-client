from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.change_user_avatar_body import ChangeUserAvatarBody
from ...models.error_response import ErrorResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    repository: str,
    person: str,
    *,
    body: ChangeUserAvatarBody | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/iam/v1/people/{repository}/{person}/avatar".format(
            repository=quote(str(repository), safe=""),
            person=quote(str(person), safe=""),
        ),
    }

    if not isinstance(body, Unset):
        _kwargs["files"] = body.to_multipart()

    headers["Content-Type"] = "multipart/form-data; boundary=+++"

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
    repository: str,
    person: str,
    *,
    client: AuthenticatedClient | Client,
    body: ChangeUserAvatarBody | Unset = UNSET,
) -> Response[Any | ErrorResponse]:
    """Set avatar of the user.

     Set avatar of the user. (To set foreign avatars, admin rights are required.)

    Args:
        repository (str):
        person (str):
        body (ChangeUserAvatarBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ErrorResponse]
    """

    kwargs = _get_kwargs(
        repository=repository,
        person=person,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repository: str,
    person: str,
    *,
    client: AuthenticatedClient | Client,
    body: ChangeUserAvatarBody | Unset = UNSET,
) -> Any | ErrorResponse | None:
    """Set avatar of the user.

     Set avatar of the user. (To set foreign avatars, admin rights are required.)

    Args:
        repository (str):
        person (str):
        body (ChangeUserAvatarBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ErrorResponse
    """

    return sync_detailed(
        repository=repository,
        person=person,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    repository: str,
    person: str,
    *,
    client: AuthenticatedClient | Client,
    body: ChangeUserAvatarBody | Unset = UNSET,
) -> Response[Any | ErrorResponse]:
    """Set avatar of the user.

     Set avatar of the user. (To set foreign avatars, admin rights are required.)

    Args:
        repository (str):
        person (str):
        body (ChangeUserAvatarBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ErrorResponse]
    """

    kwargs = _get_kwargs(
        repository=repository,
        person=person,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    person: str,
    *,
    client: AuthenticatedClient | Client,
    body: ChangeUserAvatarBody | Unset = UNSET,
) -> Any | ErrorResponse | None:
    """Set avatar of the user.

     Set avatar of the user. (To set foreign avatars, admin rights are required.)

    Args:
        repository (str):
        person (str):
        body (ChangeUserAvatarBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ErrorResponse
    """

    return (
        await asyncio_detailed(
            repository=repository,
            person=person,
            client=client,
            body=body,
        )
    ).parsed
