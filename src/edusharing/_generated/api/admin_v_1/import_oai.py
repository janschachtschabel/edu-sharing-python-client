from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    base_url: str,
    set_: str,
    metadata_prefix: str,
    metadataset: str | Unset = UNSET,
    class_name: str = "org.edu_sharing.repository.server.jobs.quartz.ImporterJob",
    importer_class_name: str
    | Unset = "org.edu_sharing.repository.server.importer.OAIPMHLOMImporter",
    record_handler_class_name: str
    | Unset = "org.edu_sharing.repository.server.importer.RecordHandlerLOM",
    binary_handler_class_name: str | Unset = UNSET,
    persistent_handler_class_name: str | Unset = UNSET,
    file_url: str | Unset = UNSET,
    oai_ids: str | Unset = UNSET,
    force_update: bool | Unset = False,
    from_: str | Unset = UNSET,
    until: str | Unset = UNSET,
    period_in_days: str | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["baseUrl"] = base_url

    params["set"] = set_

    params["metadataPrefix"] = metadata_prefix

    params["metadataset"] = metadataset

    params["className"] = class_name

    params["importerClassName"] = importer_class_name

    params["recordHandlerClassName"] = record_handler_class_name

    params["binaryHandlerClassName"] = binary_handler_class_name

    params["persistentHandlerClassName"] = persistent_handler_class_name

    params["fileUrl"] = file_url

    params["oaiIds"] = oai_ids

    params["forceUpdate"] = force_update

    params["from"] = from_

    params["until"] = until

    params["periodInDays"] = period_in_days

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/admin/v1/import/oai",
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
    *,
    client: AuthenticatedClient | Client,
    base_url: str,
    set_: str,
    metadata_prefix: str,
    metadataset: str | Unset = UNSET,
    class_name: str = "org.edu_sharing.repository.server.jobs.quartz.ImporterJob",
    importer_class_name: str
    | Unset = "org.edu_sharing.repository.server.importer.OAIPMHLOMImporter",
    record_handler_class_name: str
    | Unset = "org.edu_sharing.repository.server.importer.RecordHandlerLOM",
    binary_handler_class_name: str | Unset = UNSET,
    persistent_handler_class_name: str | Unset = UNSET,
    file_url: str | Unset = UNSET,
    oai_ids: str | Unset = UNSET,
    force_update: bool | Unset = False,
    from_: str | Unset = UNSET,
    until: str | Unset = UNSET,
    period_in_days: str | Unset = UNSET,
) -> Response[Any | ErrorResponse]:
    """Import oai data

     Import oai data.

    Args:
        base_url (str):
        set_ (str):
        metadata_prefix (str):
        metadataset (str | Unset):
        class_name (str):  Default: 'org.edu_sharing.repository.server.jobs.quartz.ImporterJob'.
        importer_class_name (str | Unset):  Default:
            'org.edu_sharing.repository.server.importer.OAIPMHLOMImporter'.
        record_handler_class_name (str | Unset):  Default:
            'org.edu_sharing.repository.server.importer.RecordHandlerLOM'.
        binary_handler_class_name (str | Unset):
        persistent_handler_class_name (str | Unset):
        file_url (str | Unset):
        oai_ids (str | Unset):
        force_update (bool | Unset):  Default: False.
        from_ (str | Unset):
        until (str | Unset):
        period_in_days (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ErrorResponse]
    """

    kwargs = _get_kwargs(
        base_url=base_url,
        set_=set_,
        metadata_prefix=metadata_prefix,
        metadataset=metadataset,
        class_name=class_name,
        importer_class_name=importer_class_name,
        record_handler_class_name=record_handler_class_name,
        binary_handler_class_name=binary_handler_class_name,
        persistent_handler_class_name=persistent_handler_class_name,
        file_url=file_url,
        oai_ids=oai_ids,
        force_update=force_update,
        from_=from_,
        until=until,
        period_in_days=period_in_days,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    base_url: str,
    set_: str,
    metadata_prefix: str,
    metadataset: str | Unset = UNSET,
    class_name: str = "org.edu_sharing.repository.server.jobs.quartz.ImporterJob",
    importer_class_name: str
    | Unset = "org.edu_sharing.repository.server.importer.OAIPMHLOMImporter",
    record_handler_class_name: str
    | Unset = "org.edu_sharing.repository.server.importer.RecordHandlerLOM",
    binary_handler_class_name: str | Unset = UNSET,
    persistent_handler_class_name: str | Unset = UNSET,
    file_url: str | Unset = UNSET,
    oai_ids: str | Unset = UNSET,
    force_update: bool | Unset = False,
    from_: str | Unset = UNSET,
    until: str | Unset = UNSET,
    period_in_days: str | Unset = UNSET,
) -> Any | ErrorResponse | None:
    """Import oai data

     Import oai data.

    Args:
        base_url (str):
        set_ (str):
        metadata_prefix (str):
        metadataset (str | Unset):
        class_name (str):  Default: 'org.edu_sharing.repository.server.jobs.quartz.ImporterJob'.
        importer_class_name (str | Unset):  Default:
            'org.edu_sharing.repository.server.importer.OAIPMHLOMImporter'.
        record_handler_class_name (str | Unset):  Default:
            'org.edu_sharing.repository.server.importer.RecordHandlerLOM'.
        binary_handler_class_name (str | Unset):
        persistent_handler_class_name (str | Unset):
        file_url (str | Unset):
        oai_ids (str | Unset):
        force_update (bool | Unset):  Default: False.
        from_ (str | Unset):
        until (str | Unset):
        period_in_days (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ErrorResponse
    """

    return sync_detailed(
        client=client,
        base_url=base_url,
        set_=set_,
        metadata_prefix=metadata_prefix,
        metadataset=metadataset,
        class_name=class_name,
        importer_class_name=importer_class_name,
        record_handler_class_name=record_handler_class_name,
        binary_handler_class_name=binary_handler_class_name,
        persistent_handler_class_name=persistent_handler_class_name,
        file_url=file_url,
        oai_ids=oai_ids,
        force_update=force_update,
        from_=from_,
        until=until,
        period_in_days=period_in_days,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    base_url: str,
    set_: str,
    metadata_prefix: str,
    metadataset: str | Unset = UNSET,
    class_name: str = "org.edu_sharing.repository.server.jobs.quartz.ImporterJob",
    importer_class_name: str
    | Unset = "org.edu_sharing.repository.server.importer.OAIPMHLOMImporter",
    record_handler_class_name: str
    | Unset = "org.edu_sharing.repository.server.importer.RecordHandlerLOM",
    binary_handler_class_name: str | Unset = UNSET,
    persistent_handler_class_name: str | Unset = UNSET,
    file_url: str | Unset = UNSET,
    oai_ids: str | Unset = UNSET,
    force_update: bool | Unset = False,
    from_: str | Unset = UNSET,
    until: str | Unset = UNSET,
    period_in_days: str | Unset = UNSET,
) -> Response[Any | ErrorResponse]:
    """Import oai data

     Import oai data.

    Args:
        base_url (str):
        set_ (str):
        metadata_prefix (str):
        metadataset (str | Unset):
        class_name (str):  Default: 'org.edu_sharing.repository.server.jobs.quartz.ImporterJob'.
        importer_class_name (str | Unset):  Default:
            'org.edu_sharing.repository.server.importer.OAIPMHLOMImporter'.
        record_handler_class_name (str | Unset):  Default:
            'org.edu_sharing.repository.server.importer.RecordHandlerLOM'.
        binary_handler_class_name (str | Unset):
        persistent_handler_class_name (str | Unset):
        file_url (str | Unset):
        oai_ids (str | Unset):
        force_update (bool | Unset):  Default: False.
        from_ (str | Unset):
        until (str | Unset):
        period_in_days (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ErrorResponse]
    """

    kwargs = _get_kwargs(
        base_url=base_url,
        set_=set_,
        metadata_prefix=metadata_prefix,
        metadataset=metadataset,
        class_name=class_name,
        importer_class_name=importer_class_name,
        record_handler_class_name=record_handler_class_name,
        binary_handler_class_name=binary_handler_class_name,
        persistent_handler_class_name=persistent_handler_class_name,
        file_url=file_url,
        oai_ids=oai_ids,
        force_update=force_update,
        from_=from_,
        until=until,
        period_in_days=period_in_days,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    base_url: str,
    set_: str,
    metadata_prefix: str,
    metadataset: str | Unset = UNSET,
    class_name: str = "org.edu_sharing.repository.server.jobs.quartz.ImporterJob",
    importer_class_name: str
    | Unset = "org.edu_sharing.repository.server.importer.OAIPMHLOMImporter",
    record_handler_class_name: str
    | Unset = "org.edu_sharing.repository.server.importer.RecordHandlerLOM",
    binary_handler_class_name: str | Unset = UNSET,
    persistent_handler_class_name: str | Unset = UNSET,
    file_url: str | Unset = UNSET,
    oai_ids: str | Unset = UNSET,
    force_update: bool | Unset = False,
    from_: str | Unset = UNSET,
    until: str | Unset = UNSET,
    period_in_days: str | Unset = UNSET,
) -> Any | ErrorResponse | None:
    """Import oai data

     Import oai data.

    Args:
        base_url (str):
        set_ (str):
        metadata_prefix (str):
        metadataset (str | Unset):
        class_name (str):  Default: 'org.edu_sharing.repository.server.jobs.quartz.ImporterJob'.
        importer_class_name (str | Unset):  Default:
            'org.edu_sharing.repository.server.importer.OAIPMHLOMImporter'.
        record_handler_class_name (str | Unset):  Default:
            'org.edu_sharing.repository.server.importer.RecordHandlerLOM'.
        binary_handler_class_name (str | Unset):
        persistent_handler_class_name (str | Unset):
        file_url (str | Unset):
        oai_ids (str | Unset):
        force_update (bool | Unset):  Default: False.
        from_ (str | Unset):
        until (str | Unset):
        period_in_days (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ErrorResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            base_url=base_url,
            set_=set_,
            metadata_prefix=metadata_prefix,
            metadataset=metadataset,
            class_name=class_name,
            importer_class_name=importer_class_name,
            record_handler_class_name=record_handler_class_name,
            binary_handler_class_name=binary_handler_class_name,
            persistent_handler_class_name=persistent_handler_class_name,
            file_url=file_url,
            oai_ids=oai_ids,
            force_update=force_update,
            from_=from_,
            until=until,
            period_in_days=period_in_days,
        )
    ).parsed
