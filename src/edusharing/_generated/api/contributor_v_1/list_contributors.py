from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.contributor_search_result import ContributorSearchResult
from ...models.error_response import ErrorResponse
from ...models.list_contributors_has_id_item import ListContributorsHasIdItem
from ...models.list_contributors_kind import ListContributorsKind
from ...models.list_contributors_sort_by import ListContributorsSortBy
from ...types import UNSET, Response, Unset


def _get_kwargs(
    repository: str,
    *,
    search_word: str | Unset = UNSET,
    kind: ListContributorsKind | Unset = UNSET,
    has_id: list[ListContributorsHasIdItem] | Unset = UNSET,
    sort_by: ListContributorsSortBy | Unset = ListContributorsSortBy.NAME,
    sort_ascending: bool | Unset = True,
    skip: int | Unset = 0,
    limit: int | Unset = 50,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["searchWord"] = search_word

    json_kind: str | Unset = UNSET
    if not isinstance(kind, Unset):
        json_kind = kind.value

    params["kind"] = json_kind

    json_has_id: list[str] | Unset = UNSET
    if not isinstance(has_id, Unset):
        json_has_id = []
        for has_id_item_data in has_id:
            has_id_item = has_id_item_data.value
            json_has_id.append(has_id_item)

    params["hasId"] = json_has_id

    json_sort_by: str | Unset = UNSET
    if not isinstance(sort_by, Unset):
        json_sort_by = sort_by.value

    params["sortBy"] = json_sort_by

    params["sortAscending"] = sort_ascending

    params["skip"] = skip

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/contributor/v1/{repository}/list".format(
            repository=quote(str(repository), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ContributorSearchResult | ErrorResponse | None:
    if response.status_code == 200:
        response_200 = ContributorSearchResult.from_dict(response.json())

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
) -> Response[ContributorSearchResult | ErrorResponse]:
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
    kind: ListContributorsKind | Unset = UNSET,
    has_id: list[ListContributorsHasIdItem] | Unset = UNSET,
    sort_by: ListContributorsSortBy | Unset = ListContributorsSortBy.NAME,
    sort_ascending: bool | Unset = True,
    skip: int | Unset = 0,
    limit: int | Unset = 50,
) -> Response[ContributorSearchResult | ErrorResponse]:
    """list managed contributors

     Filtered, sorted and paginated management list of the contributor registry, including the total
    match count. Requires the TOOLPERMISSION_MANAGE_CONTRIBUTORS toolpermission.

    Args:
        repository (str):
        search_word (str | Unset):
        kind (ListContributorsKind | Unset):
        has_id (list[ListContributorsHasIdItem] | Unset):
        sort_by (ListContributorsSortBy | Unset):  Default: ListContributorsSortBy.NAME.
        sort_ascending (bool | Unset):  Default: True.
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 50.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ContributorSearchResult | ErrorResponse]
    """

    kwargs = _get_kwargs(
        repository=repository,
        search_word=search_word,
        kind=kind,
        has_id=has_id,
        sort_by=sort_by,
        sort_ascending=sort_ascending,
        skip=skip,
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
    kind: ListContributorsKind | Unset = UNSET,
    has_id: list[ListContributorsHasIdItem] | Unset = UNSET,
    sort_by: ListContributorsSortBy | Unset = ListContributorsSortBy.NAME,
    sort_ascending: bool | Unset = True,
    skip: int | Unset = 0,
    limit: int | Unset = 50,
) -> ContributorSearchResult | ErrorResponse | None:
    """list managed contributors

     Filtered, sorted and paginated management list of the contributor registry, including the total
    match count. Requires the TOOLPERMISSION_MANAGE_CONTRIBUTORS toolpermission.

    Args:
        repository (str):
        search_word (str | Unset):
        kind (ListContributorsKind | Unset):
        has_id (list[ListContributorsHasIdItem] | Unset):
        sort_by (ListContributorsSortBy | Unset):  Default: ListContributorsSortBy.NAME.
        sort_ascending (bool | Unset):  Default: True.
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 50.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ContributorSearchResult | ErrorResponse
    """

    return sync_detailed(
        repository=repository,
        client=client,
        search_word=search_word,
        kind=kind,
        has_id=has_id,
        sort_by=sort_by,
        sort_ascending=sort_ascending,
        skip=skip,
        limit=limit,
    ).parsed


async def asyncio_detailed(
    repository: str,
    *,
    client: AuthenticatedClient | Client,
    search_word: str | Unset = UNSET,
    kind: ListContributorsKind | Unset = UNSET,
    has_id: list[ListContributorsHasIdItem] | Unset = UNSET,
    sort_by: ListContributorsSortBy | Unset = ListContributorsSortBy.NAME,
    sort_ascending: bool | Unset = True,
    skip: int | Unset = 0,
    limit: int | Unset = 50,
) -> Response[ContributorSearchResult | ErrorResponse]:
    """list managed contributors

     Filtered, sorted and paginated management list of the contributor registry, including the total
    match count. Requires the TOOLPERMISSION_MANAGE_CONTRIBUTORS toolpermission.

    Args:
        repository (str):
        search_word (str | Unset):
        kind (ListContributorsKind | Unset):
        has_id (list[ListContributorsHasIdItem] | Unset):
        sort_by (ListContributorsSortBy | Unset):  Default: ListContributorsSortBy.NAME.
        sort_ascending (bool | Unset):  Default: True.
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 50.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ContributorSearchResult | ErrorResponse]
    """

    kwargs = _get_kwargs(
        repository=repository,
        search_word=search_word,
        kind=kind,
        has_id=has_id,
        sort_by=sort_by,
        sort_ascending=sort_ascending,
        skip=skip,
        limit=limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    *,
    client: AuthenticatedClient | Client,
    search_word: str | Unset = UNSET,
    kind: ListContributorsKind | Unset = UNSET,
    has_id: list[ListContributorsHasIdItem] | Unset = UNSET,
    sort_by: ListContributorsSortBy | Unset = ListContributorsSortBy.NAME,
    sort_ascending: bool | Unset = True,
    skip: int | Unset = 0,
    limit: int | Unset = 50,
) -> ContributorSearchResult | ErrorResponse | None:
    """list managed contributors

     Filtered, sorted and paginated management list of the contributor registry, including the total
    match count. Requires the TOOLPERMISSION_MANAGE_CONTRIBUTORS toolpermission.

    Args:
        repository (str):
        search_word (str | Unset):
        kind (ListContributorsKind | Unset):
        has_id (list[ListContributorsHasIdItem] | Unset):
        sort_by (ListContributorsSortBy | Unset):  Default: ListContributorsSortBy.NAME.
        sort_ascending (bool | Unset):  Default: True.
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 50.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ContributorSearchResult | ErrorResponse
    """

    return (
        await asyncio_detailed(
            repository=repository,
            client=client,
            search_word=search_word,
            kind=kind,
            has_id=has_id,
            sort_by=sort_by,
            sort_ascending=sort_ascending,
            skip=skip,
            limit=limit,
        )
    ).parsed
