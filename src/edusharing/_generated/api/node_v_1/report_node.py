from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.report_node_mode import ReportNodeMode
from ...types import UNSET, Response, Unset


def _get_kwargs(
    repository: str,
    node: str,
    *,
    mode: ReportNodeMode | Unset = UNSET,
    reason: str,
    user_email: str,
    user_comment: str | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_mode: str | Unset = UNSET
    if not isinstance(mode, Unset):
        json_mode = mode.value

    params["mode"] = json_mode

    params["reason"] = reason

    params["userEmail"] = user_email

    params["userComment"] = user_comment

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/node/v1/nodes/{repository}/{node}/report".format(
            repository=quote(str(repository), safe=""),
            node=quote(str(node), safe=""),
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
    repository: str,
    node: str,
    *,
    client: AuthenticatedClient | Client,
    mode: ReportNodeMode | Unset = UNSET,
    reason: str,
    user_email: str,
    user_comment: str | Unset = UNSET,
) -> Response[Any | ErrorResponse]:
    """Report the node.

     Report a node to notify the admin about an issue)

    Args:
        repository (str):
        node (str):
        mode (ReportNodeMode | Unset):
        reason (str):
        user_email (str):
        user_comment (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ErrorResponse]
    """

    kwargs = _get_kwargs(
        repository=repository,
        node=node,
        mode=mode,
        reason=reason,
        user_email=user_email,
        user_comment=user_comment,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repository: str,
    node: str,
    *,
    client: AuthenticatedClient | Client,
    mode: ReportNodeMode | Unset = UNSET,
    reason: str,
    user_email: str,
    user_comment: str | Unset = UNSET,
) -> Any | ErrorResponse | None:
    """Report the node.

     Report a node to notify the admin about an issue)

    Args:
        repository (str):
        node (str):
        mode (ReportNodeMode | Unset):
        reason (str):
        user_email (str):
        user_comment (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ErrorResponse
    """

    return sync_detailed(
        repository=repository,
        node=node,
        client=client,
        mode=mode,
        reason=reason,
        user_email=user_email,
        user_comment=user_comment,
    ).parsed


async def asyncio_detailed(
    repository: str,
    node: str,
    *,
    client: AuthenticatedClient | Client,
    mode: ReportNodeMode | Unset = UNSET,
    reason: str,
    user_email: str,
    user_comment: str | Unset = UNSET,
) -> Response[Any | ErrorResponse]:
    """Report the node.

     Report a node to notify the admin about an issue)

    Args:
        repository (str):
        node (str):
        mode (ReportNodeMode | Unset):
        reason (str):
        user_email (str):
        user_comment (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ErrorResponse]
    """

    kwargs = _get_kwargs(
        repository=repository,
        node=node,
        mode=mode,
        reason=reason,
        user_email=user_email,
        user_comment=user_comment,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    node: str,
    *,
    client: AuthenticatedClient | Client,
    mode: ReportNodeMode | Unset = UNSET,
    reason: str,
    user_email: str,
    user_comment: str | Unset = UNSET,
) -> Any | ErrorResponse | None:
    """Report the node.

     Report a node to notify the admin about an issue)

    Args:
        repository (str):
        node (str):
        mode (ReportNodeMode | Unset):
        reason (str):
        user_email (str):
        user_comment (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ErrorResponse
    """

    return (
        await asyncio_detailed(
            repository=repository,
            node=node,
            client=client,
            mode=mode,
            reason=reason,
            user_email=user_email,
            user_comment=user_comment,
        )
    ).parsed
