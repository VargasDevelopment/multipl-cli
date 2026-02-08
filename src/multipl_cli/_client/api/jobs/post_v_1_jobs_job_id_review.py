from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.post_v1_jobs_job_id_review_body import PostV1JobsJobIdReviewBody
from ...models.post_v1_jobs_job_id_review_response_200 import PostV1JobsJobIdReviewResponse200
from ...types import Response


def _get_kwargs(
    job_id: str,
    *,
    body: PostV1JobsJobIdReviewBody,
    authorization: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["authorization"] = authorization

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/jobs/{job_id}/review".format(
            job_id=quote(str(job_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> PostV1JobsJobIdReviewResponse200 | None:
    if response.status_code == 200:
        response_200 = PostV1JobsJobIdReviewResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[PostV1JobsJobIdReviewResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    job_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: PostV1JobsJobIdReviewBody,
    authorization: str,
) -> Response[PostV1JobsJobIdReviewResponse200]:
    """
    Args:
        job_id (str):
        authorization (str):
        body (PostV1JobsJobIdReviewBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostV1JobsJobIdReviewResponse200]
    """

    kwargs = _get_kwargs(
        job_id=job_id,
        body=body,
        authorization=authorization,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    job_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: PostV1JobsJobIdReviewBody,
    authorization: str,
) -> PostV1JobsJobIdReviewResponse200 | None:
    """
    Args:
        job_id (str):
        authorization (str):
        body (PostV1JobsJobIdReviewBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostV1JobsJobIdReviewResponse200
    """

    return sync_detailed(
        job_id=job_id,
        client=client,
        body=body,
        authorization=authorization,
    ).parsed


async def asyncio_detailed(
    job_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: PostV1JobsJobIdReviewBody,
    authorization: str,
) -> Response[PostV1JobsJobIdReviewResponse200]:
    """
    Args:
        job_id (str):
        authorization (str):
        body (PostV1JobsJobIdReviewBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostV1JobsJobIdReviewResponse200]
    """

    kwargs = _get_kwargs(
        job_id=job_id,
        body=body,
        authorization=authorization,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    job_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: PostV1JobsJobIdReviewBody,
    authorization: str,
) -> PostV1JobsJobIdReviewResponse200 | None:
    """
    Args:
        job_id (str):
        authorization (str):
        body (PostV1JobsJobIdReviewBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostV1JobsJobIdReviewResponse200
    """

    return (
        await asyncio_detailed(
            job_id=job_id,
            client=client,
            body=body,
            authorization=authorization,
        )
    ).parsed
