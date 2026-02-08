from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.post_v1_jobs_body import PostV1JobsBody
from ...models.post_v1_jobs_response_201 import PostV1JobsResponse201
from ...models.post_v1_jobs_response_402 import PostV1JobsResponse402
from ...types import Response


def _get_kwargs(
    *,
    body: PostV1JobsBody,
    authorization: str,
    x_idempotency_key: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["authorization"] = authorization

    headers["x-idempotency-key"] = x_idempotency_key

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/jobs",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> PostV1JobsResponse201 | PostV1JobsResponse402 | None:
    if response.status_code == 201:
        response_201 = PostV1JobsResponse201.from_dict(response.json())

        return response_201

    if response.status_code == 402:
        response_402 = PostV1JobsResponse402.from_dict(response.json())

        return response_402

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[PostV1JobsResponse201 | PostV1JobsResponse402]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: PostV1JobsBody,
    authorization: str,
    x_idempotency_key: str,
) -> Response[PostV1JobsResponse201 | PostV1JobsResponse402]:
    """
    Args:
        authorization (str):
        x_idempotency_key (str):
        body (PostV1JobsBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostV1JobsResponse201 | PostV1JobsResponse402]
    """

    kwargs = _get_kwargs(
        body=body,
        authorization=authorization,
        x_idempotency_key=x_idempotency_key,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: PostV1JobsBody,
    authorization: str,
    x_idempotency_key: str,
) -> PostV1JobsResponse201 | PostV1JobsResponse402 | None:
    """
    Args:
        authorization (str):
        x_idempotency_key (str):
        body (PostV1JobsBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostV1JobsResponse201 | PostV1JobsResponse402
    """

    return sync_detailed(
        client=client,
        body=body,
        authorization=authorization,
        x_idempotency_key=x_idempotency_key,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: PostV1JobsBody,
    authorization: str,
    x_idempotency_key: str,
) -> Response[PostV1JobsResponse201 | PostV1JobsResponse402]:
    """
    Args:
        authorization (str):
        x_idempotency_key (str):
        body (PostV1JobsBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostV1JobsResponse201 | PostV1JobsResponse402]
    """

    kwargs = _get_kwargs(
        body=body,
        authorization=authorization,
        x_idempotency_key=x_idempotency_key,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: PostV1JobsBody,
    authorization: str,
    x_idempotency_key: str,
) -> PostV1JobsResponse201 | PostV1JobsResponse402 | None:
    """
    Args:
        authorization (str):
        x_idempotency_key (str):
        body (PostV1JobsBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostV1JobsResponse201 | PostV1JobsResponse402
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            authorization=authorization,
            x_idempotency_key=x_idempotency_key,
        )
    ).parsed
