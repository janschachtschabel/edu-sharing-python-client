from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.register_by_type_type import RegisterByTypeType
from ...types import UNSET, Response, Unset


def _get_kwargs(
    type_: RegisterByTypeType,
    *,
    base_url: str,
    client_id: str | Unset = UNSET,
    deployment_id: str | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["baseUrl"] = base_url

    params["client_id"] = client_id

    params["deployment_id"] = deployment_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/lti/v13/registration/{type_}".format(
            type_=quote(str(type_), safe=""),
        ),
        "params": params,
    }

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
    type_: RegisterByTypeType,
    *,
    client: AuthenticatedClient | Client,
    base_url: str,
    client_id: str | Unset = UNSET,
    deployment_id: str | Unset = UNSET,
) -> Response[Any | ErrorResponse]:
    """register LTI platform

    Args:
        type_ (RegisterByTypeType):
        base_url (str):
        client_id (str | Unset):
        deployment_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ErrorResponse]
    """

    kwargs = _get_kwargs(
        type_=type_,
        base_url=base_url,
        client_id=client_id,
        deployment_id=deployment_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    type_: RegisterByTypeType,
    *,
    client: AuthenticatedClient | Client,
    base_url: str,
    client_id: str | Unset = UNSET,
    deployment_id: str | Unset = UNSET,
) -> Any | ErrorResponse | None:
    """register LTI platform

    Args:
        type_ (RegisterByTypeType):
        base_url (str):
        client_id (str | Unset):
        deployment_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ErrorResponse
    """

    return sync_detailed(
        type_=type_,
        client=client,
        base_url=base_url,
        client_id=client_id,
        deployment_id=deployment_id,
    ).parsed


async def asyncio_detailed(
    type_: RegisterByTypeType,
    *,
    client: AuthenticatedClient | Client,
    base_url: str,
    client_id: str | Unset = UNSET,
    deployment_id: str | Unset = UNSET,
) -> Response[Any | ErrorResponse]:
    """register LTI platform

    Args:
        type_ (RegisterByTypeType):
        base_url (str):
        client_id (str | Unset):
        deployment_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ErrorResponse]
    """

    kwargs = _get_kwargs(
        type_=type_,
        base_url=base_url,
        client_id=client_id,
        deployment_id=deployment_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    type_: RegisterByTypeType,
    *,
    client: AuthenticatedClient | Client,
    base_url: str,
    client_id: str | Unset = UNSET,
    deployment_id: str | Unset = UNSET,
) -> Any | ErrorResponse | None:
    """register LTI platform

    Args:
        type_ (RegisterByTypeType):
        base_url (str):
        client_id (str | Unset):
        deployment_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ErrorResponse
    """

    return (
        await asyncio_detailed(
            type_=type_,
            client=client,
            base_url=base_url,
            client_id=client_id,
            deployment_id=deployment_id,
        )
    ).parsed
