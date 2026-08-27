from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.create_suggestion_request_dto import CreateSuggestionRequestDTO
from ...models.create_suggestions_type import CreateSuggestionsType
from ...models.error_response import ErrorResponse
from ...models.suggestion_response_dto import SuggestionResponseDTO
from ...types import UNSET, Response, Unset


def _get_kwargs(
    repository: str,
    node: str,
    *,
    body: list[CreateSuggestionRequestDTO] | Unset = UNSET,
    type_: CreateSuggestionsType,
    version: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    json_type_ = type_.value
    params["type"] = json_type_

    params["version"] = version

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/suggestions/v1/{repository}/{node}".format(
            repository=quote(str(repository), safe=""),
            node=quote(str(node), safe=""),
        ),
        "params": params,
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = []
        for body_item_data in body:
            body_item = body_item_data.to_dict()
            _kwargs["json"].append(body_item)

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | list[SuggestionResponseDTO] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = SuggestionResponseDTO.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

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
) -> Response[ErrorResponse | list[SuggestionResponseDTO]]:
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
    body: list[CreateSuggestionRequestDTO] | Unset = UNSET,
    type_: CreateSuggestionsType,
    version: str,
) -> Response[ErrorResponse | list[SuggestionResponseDTO]]:
    """Create suggestions

     Pass a list of suggestions for each property and value. For each entry, exactly one suggestion value
    is set for the respective property. If multiple suggestion values are defined for a property, they
    must be transmitted in separate entries for each value.
    * propertyId: abbreviation of the property (e.g., cclom:general_description)
    * value: suggestion value – corresponds to the data type of the property (string, long, double,
    boolean), always single-valued. Dates and times should always be provided in Unix timestamp format.
    * description: notes for the editor explaining why this suggestion is a good fit.
    * confidence: nominal value indicating how well the suggestion fits (value between 0-1).

    Args:
        repository (str):
        node (str):
        type_ (CreateSuggestionsType): Type of the suggestion
        version (str):
        body (list[CreateSuggestionRequestDTO] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | list[SuggestionResponseDTO]]
    """

    kwargs = _get_kwargs(
        repository=repository,
        node=node,
        body=body,
        type_=type_,
        version=version,
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
    body: list[CreateSuggestionRequestDTO] | Unset = UNSET,
    type_: CreateSuggestionsType,
    version: str,
) -> ErrorResponse | list[SuggestionResponseDTO] | None:
    """Create suggestions

     Pass a list of suggestions for each property and value. For each entry, exactly one suggestion value
    is set for the respective property. If multiple suggestion values are defined for a property, they
    must be transmitted in separate entries for each value.
    * propertyId: abbreviation of the property (e.g., cclom:general_description)
    * value: suggestion value – corresponds to the data type of the property (string, long, double,
    boolean), always single-valued. Dates and times should always be provided in Unix timestamp format.
    * description: notes for the editor explaining why this suggestion is a good fit.
    * confidence: nominal value indicating how well the suggestion fits (value between 0-1).

    Args:
        repository (str):
        node (str):
        type_ (CreateSuggestionsType): Type of the suggestion
        version (str):
        body (list[CreateSuggestionRequestDTO] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | list[SuggestionResponseDTO]
    """

    return sync_detailed(
        repository=repository,
        node=node,
        client=client,
        body=body,
        type_=type_,
        version=version,
    ).parsed


async def asyncio_detailed(
    repository: str,
    node: str,
    *,
    client: AuthenticatedClient | Client,
    body: list[CreateSuggestionRequestDTO] | Unset = UNSET,
    type_: CreateSuggestionsType,
    version: str,
) -> Response[ErrorResponse | list[SuggestionResponseDTO]]:
    """Create suggestions

     Pass a list of suggestions for each property and value. For each entry, exactly one suggestion value
    is set for the respective property. If multiple suggestion values are defined for a property, they
    must be transmitted in separate entries for each value.
    * propertyId: abbreviation of the property (e.g., cclom:general_description)
    * value: suggestion value – corresponds to the data type of the property (string, long, double,
    boolean), always single-valued. Dates and times should always be provided in Unix timestamp format.
    * description: notes for the editor explaining why this suggestion is a good fit.
    * confidence: nominal value indicating how well the suggestion fits (value between 0-1).

    Args:
        repository (str):
        node (str):
        type_ (CreateSuggestionsType): Type of the suggestion
        version (str):
        body (list[CreateSuggestionRequestDTO] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | list[SuggestionResponseDTO]]
    """

    kwargs = _get_kwargs(
        repository=repository,
        node=node,
        body=body,
        type_=type_,
        version=version,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository: str,
    node: str,
    *,
    client: AuthenticatedClient | Client,
    body: list[CreateSuggestionRequestDTO] | Unset = UNSET,
    type_: CreateSuggestionsType,
    version: str,
) -> ErrorResponse | list[SuggestionResponseDTO] | None:
    """Create suggestions

     Pass a list of suggestions for each property and value. For each entry, exactly one suggestion value
    is set for the respective property. If multiple suggestion values are defined for a property, they
    must be transmitted in separate entries for each value.
    * propertyId: abbreviation of the property (e.g., cclom:general_description)
    * value: suggestion value – corresponds to the data type of the property (string, long, double,
    boolean), always single-valued. Dates and times should always be provided in Unix timestamp format.
    * description: notes for the editor explaining why this suggestion is a good fit.
    * confidence: nominal value indicating how well the suggestion fits (value between 0-1).

    Args:
        repository (str):
        node (str):
        type_ (CreateSuggestionsType): Type of the suggestion
        version (str):
        body (list[CreateSuggestionRequestDTO] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | list[SuggestionResponseDTO]
    """

    return (
        await asyncio_detailed(
            repository=repository,
            node=node,
            client=client,
            body=body,
            type_=type_,
            version=version,
        )
    ).parsed
