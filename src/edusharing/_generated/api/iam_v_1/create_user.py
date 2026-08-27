from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.user import User
from ...models.user_profile_edit import UserProfileEdit
from ...types import UNSET, Response, Unset


def _get_kwargs(
    repository: str,
    person: str,
    *,
    body: UserProfileEdit,
    password: str | Unset = UNSET,
    return_result: bool | Unset = True,
    setup_home_dir: bool | Unset = True,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["password"] = password

    params["returnResult"] = return_result

    params["setupHomeDir"] = setup_home_dir

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/iam/v1/people/{repository}/{person}".format(
            repository=quote(str(repository), safe=""),
            person=quote(str(person), safe=""),
        ),
        "params": params,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | User | None:
    if response.status_code == 200:
        response_200 = User.from_dict(response.json())

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
) -> Response[ErrorResponse | User]:
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
    body: UserProfileEdit,
    password: str | Unset = UNSET,
    return_result: bool | Unset = True,
    setup_home_dir: bool | Unset = True,
) -> Response[ErrorResponse | User]:
    """Create a new user.

     Create a new user. (admin rights are required.)

    Args:
        repository (str):
        person (str):
        password (str | Unset):
        return_result (bool | Unset):  Default: True.
        setup_home_dir (bool | Unset):  Default: True.
        body (UserProfileEdit):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | User]
    """

    kwargs = _get_kwargs(
        repository=repository,
        person=person,
        body=body,
        password=password,
        return_result=return_result,
        setup_home_dir=setup_home_dir,
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
    body: UserProfileEdit,
    password: str | Unset = UNSET,
    return_result: bool | Unset = True,
    setup_home_dir: bool | Unset = True,
) -> ErrorResponse | User | None:
    """Create a new user.

     Create a new user. (admin rights are required.)

    Args:
        repository (str):
        person (str):
        password (str | Unset):
        return_result (bool | Unset):  Default: True.
        setup_home_dir (bool | Unset):  Default: True.
        body (UserProfileEdit):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | User
    """

    return sync_detailed(
        repository=repository,
        person=person,
        client=client,
        body=body,
        password=password,
        return_result=return_result,
        setup_home_dir=setup_home_dir,
    ).parsed


async def asyncio_detailed(
    repository: str,
    person: str,
    *,
    client: AuthenticatedClient | Client,
    body: UserProfileEdit,
    password: str | Unset = UNSET,
    return_result: bool | Unset = True,
    setup_home_dir: bool | Unset = True,
) -> Response[ErrorResponse | User]:
    """Create a new user.

     Create a new user. (admin rights are required.)

    Args:
        repository (str):
        person (str):
        password (str | Unset):
        return_result (bool | Unset):  Default: True.
        setup_home_dir (bool | Unset):  Default: True.
        body (UserProfileEdit):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | User]
    """

    kwargs = _get_kwargs(
        repository=repository,
        person=person,
        body=body,
        password=password,
        return_result=return_result,
        setup_home_dir=setup_home_dir,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    person: str,
    *,
    client: AuthenticatedClient | Client,
    body: UserProfileEdit,
    password: str | Unset = UNSET,
    return_result: bool | Unset = True,
    setup_home_dir: bool | Unset = True,
) -> ErrorResponse | User | None:
    """Create a new user.

     Create a new user. (admin rights are required.)

    Args:
        repository (str):
        person (str):
        password (str | Unset):
        return_result (bool | Unset):  Default: True.
        setup_home_dir (bool | Unset):  Default: True.
        body (UserProfileEdit):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | User
    """

    return (
        await asyncio_detailed(
            repository=repository,
            person=person,
            client=client,
            body=body,
            password=password,
            return_result=return_result,
            setup_home_dir=setup_home_dir,
        )
    ).parsed
