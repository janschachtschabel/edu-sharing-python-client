from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.contributor_data import ContributorData
from ...models.error_response import ErrorResponse
from ...models.get_contributors_kind import GetContributorsKind
from ...types import UNSET, Response, Unset


def _get_kwargs(
    repository: str,
    *,
    search_word: str | Unset = UNSET,
    kind: GetContributorsKind | Unset = UNSET,
    limit: int | Unset = 50,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["searchWord"] = search_word

    json_kind: str | Unset = UNSET
    if not isinstance(kind, Unset):
        json_kind = kind.value

    params["kind"] = json_kind

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/contributor/v1/{repository}".format(
            repository=quote(str(repository), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | list[ContributorData] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = ContributorData.from_dict(response_200_item_data)

            response_200.append(response_200_item)

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

    if response.status_code == 500:
        response_500 = ErrorResponse.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ErrorResponse | list[ContributorData]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    repository: str,
    *,
    client: AuthenticatedClient | Client,
    search_word: str | Unset = UNSET,
    kind: GetContributorsKind | Unset = UNSET,
    limit: int | Unset = 50,
) -> Response[ErrorResponse | list[ContributorData]]:
    """search managed contributors

     Search the contributor registry (autocomplete / management list).

    Args:
        repository (str):
        search_word (str | Unset):
        kind (GetContributorsKind | Unset):
        limit (int | Unset):  Default: 50.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | list[ContributorData]]
    """

    kwargs = _get_kwargs(
        repository=repository,
        search_word=search_word,
        kind=kind,
        limit=limit,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repository: str,
    *,
    client: AuthenticatedClient | Client,
    search_word: str | Unset = UNSET,
    kind: GetContributorsKind | Unset = UNSET,
    limit: int | Unset = 50,
) -> ErrorResponse | list[ContributorData] | None:
    """search managed contributors

     Search the contributor registry (autocomplete / management list).

    Args:
        repository (str):
        search_word (str | Unset):
        kind (GetContributorsKind | Unset):
        limit (int | Unset):  Default: 50.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | list[ContributorData]
    """

    return sync_detailed(
        repository=repository,
        client=client,
        search_word=search_word,
        kind=kind,
        limit=limit,
    ).parsed


async def asyncio_detailed(
    repository: str,
    *,
    client: AuthenticatedClient | Client,
    search_word: str | Unset = UNSET,
    kind: GetContributorsKind | Unset = UNSET,
    limit: int | Unset = 50,
) -> Response[ErrorResponse | list[ContributorData]]:
    """search managed contributors

     Search the contributor registry (autocomplete / management list).

    Args:
        repository (str):
        search_word (str | Unset):
        kind (GetContributorsKind | Unset):
        limit (int | Unset):  Default: 50.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | list[ContributorData]]
    """

    kwargs = _get_kwargs(
        repository=repository,
        search_word=search_word,
        kind=kind,
        limit=limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    *,
    client: AuthenticatedClient | Client,
    search_word: str | Unset = UNSET,
    kind: GetContributorsKind | Unset = UNSET,
    limit: int | Unset = 50,
) -> ErrorResponse | list[ContributorData] | None:
    """search managed contributors

     Search the contributor registry (autocomplete / management list).

    Args:
        repository (str):
        search_word (str | Unset):
        kind (GetContributorsKind | Unset):
        limit (int | Unset):  Default: 50.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | list[ContributorData]
    """

    return (
        await asyncio_detailed(
            repository=repository,
            client=client,
            search_word=search_word,
            kind=kind,
            limit=limit,
        )
    ).parsed
