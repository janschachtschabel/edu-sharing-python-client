from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.search_contributor_contributor_kind import SearchContributorContributorKind
from ...models.search_v_card import SearchVCard
from ...types import UNSET, Response, Unset


def _get_kwargs(
    repository: str,
    *,
    search_word: str,
    contributor_kind: SearchContributorContributorKind = SearchContributorContributorKind.PERSON,
    fields: list[str] | Unset = UNSET,
    contributor_properties: list[str] | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["searchWord"] = search_word

    json_contributor_kind = contributor_kind.value
    params["contributorKind"] = json_contributor_kind

    json_fields: list[str] | Unset = UNSET
    if not isinstance(fields, Unset):
        json_fields = fields

    params["fields"] = json_fields

    json_contributor_properties: list[str] | Unset = UNSET
    if not isinstance(contributor_properties, Unset):
        json_contributor_properties = contributor_properties

    params["contributorProperties"] = json_contributor_properties

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/search/v1/queries/{repository}/contributor".format(
            repository=quote(str(repository), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | list[SearchVCard] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = SearchVCard.from_dict(response_200_item_data)

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
) -> Response[ErrorResponse | list[SearchVCard]]:
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
    search_word: str,
    contributor_kind: SearchContributorContributorKind = SearchContributorContributorKind.PERSON,
    fields: list[str] | Unset = UNSET,
    contributor_properties: list[str] | Unset = UNSET,
) -> Response[ErrorResponse | list[SearchVCard]]:
    """Search for contributors

    Args:
        repository (str):
        search_word (str):
        contributor_kind (SearchContributorContributorKind):  Default:
            SearchContributorContributorKind.PERSON.
        fields (list[str] | Unset):
        contributor_properties (list[str] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | list[SearchVCard]]
    """

    kwargs = _get_kwargs(
        repository=repository,
        search_word=search_word,
        contributor_kind=contributor_kind,
        fields=fields,
        contributor_properties=contributor_properties,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repository: str,
    *,
    client: AuthenticatedClient | Client,
    search_word: str,
    contributor_kind: SearchContributorContributorKind = SearchContributorContributorKind.PERSON,
    fields: list[str] | Unset = UNSET,
    contributor_properties: list[str] | Unset = UNSET,
) -> ErrorResponse | list[SearchVCard] | None:
    """Search for contributors

    Args:
        repository (str):
        search_word (str):
        contributor_kind (SearchContributorContributorKind):  Default:
            SearchContributorContributorKind.PERSON.
        fields (list[str] | Unset):
        contributor_properties (list[str] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | list[SearchVCard]
    """

    return sync_detailed(
        repository=repository,
        client=client,
        search_word=search_word,
        contributor_kind=contributor_kind,
        fields=fields,
        contributor_properties=contributor_properties,
    ).parsed


async def asyncio_detailed(
    repository: str,
    *,
    client: AuthenticatedClient | Client,
    search_word: str,
    contributor_kind: SearchContributorContributorKind = SearchContributorContributorKind.PERSON,
    fields: list[str] | Unset = UNSET,
    contributor_properties: list[str] | Unset = UNSET,
) -> Response[ErrorResponse | list[SearchVCard]]:
    """Search for contributors

    Args:
        repository (str):
        search_word (str):
        contributor_kind (SearchContributorContributorKind):  Default:
            SearchContributorContributorKind.PERSON.
        fields (list[str] | Unset):
        contributor_properties (list[str] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | list[SearchVCard]]
    """

    kwargs = _get_kwargs(
        repository=repository,
        search_word=search_word,
        contributor_kind=contributor_kind,
        fields=fields,
        contributor_properties=contributor_properties,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    *,
    client: AuthenticatedClient | Client,
    search_word: str,
    contributor_kind: SearchContributorContributorKind = SearchContributorContributorKind.PERSON,
    fields: list[str] | Unset = UNSET,
    contributor_properties: list[str] | Unset = UNSET,
) -> ErrorResponse | list[SearchVCard] | None:
    """Search for contributors

    Args:
        repository (str):
        search_word (str):
        contributor_kind (SearchContributorContributorKind):  Default:
            SearchContributorContributorKind.PERSON.
        fields (list[str] | Unset):
        contributor_properties (list[str] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | list[SearchVCard]
    """

    return (
        await asyncio_detailed(
            repository=repository,
            client=client,
            search_word=search_word,
            contributor_kind=contributor_kind,
            fields=fields,
            contributor_properties=contributor_properties,
        )
    ).parsed
