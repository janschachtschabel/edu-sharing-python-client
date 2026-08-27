from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.submission_file import SubmissionFile
from ...models.submission_file_content_upload import SubmissionFileContentUpload
from ...types import Response


def _get_kwargs(
    assignment_id: str,
    submission_id: str,
    *,
    body: SubmissionFileContentUpload,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/assignment/v1/{assignment_id}/submissions/{submission_id}/files".format(
            assignment_id=quote(str(assignment_id), safe=""),
            submission_id=quote(str(submission_id), safe=""),
        ),
    }

    _kwargs["files"] = body.to_multipart()

    headers["Content-Type"] = "multipart/form-data; boundary=+++"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | SubmissionFile | None:
    if response.status_code == 200:
        response_200 = SubmissionFile.from_dict(response.json())

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
) -> Response[ErrorResponse | SubmissionFile]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    assignment_id: str,
    submission_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: SubmissionFileContentUpload,
) -> Response[ErrorResponse | SubmissionFile]:
    """Create a submission file

     Create a submission file

    Args:
        assignment_id (str):
        submission_id (str):
        body (SubmissionFileContentUpload): Multipart upload for submission files

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | SubmissionFile]
    """

    kwargs = _get_kwargs(
        assignment_id=assignment_id,
        submission_id=submission_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    assignment_id: str,
    submission_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: SubmissionFileContentUpload,
) -> ErrorResponse | SubmissionFile | None:
    """Create a submission file

     Create a submission file

    Args:
        assignment_id (str):
        submission_id (str):
        body (SubmissionFileContentUpload): Multipart upload for submission files

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | SubmissionFile
    """

    return sync_detailed(
        assignment_id=assignment_id,
        submission_id=submission_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    assignment_id: str,
    submission_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: SubmissionFileContentUpload,
) -> Response[ErrorResponse | SubmissionFile]:
    """Create a submission file

     Create a submission file

    Args:
        assignment_id (str):
        submission_id (str):
        body (SubmissionFileContentUpload): Multipart upload for submission files

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | SubmissionFile]
    """

    kwargs = _get_kwargs(
        assignment_id=assignment_id,
        submission_id=submission_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    assignment_id: str,
    submission_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: SubmissionFileContentUpload,
) -> ErrorResponse | SubmissionFile | None:
    """Create a submission file

     Create a submission file

    Args:
        assignment_id (str):
        submission_id (str):
        body (SubmissionFileContentUpload): Multipart upload for submission files

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | SubmissionFile
    """

    return (
        await asyncio_detailed(
            assignment_id=assignment_id,
            submission_id=submission_id,
            client=client,
            body=body,
        )
    ).parsed
