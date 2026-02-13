from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.post_v1_claims_claim_id_release_response_200 import (
    PostV1ClaimsClaimIdReleaseResponse200,
)
from ...types import Response


def _get_kwargs(
    claim_id: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/claims/{claim_id}/release".format(
            claim_id=quote(str(claim_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> PostV1ClaimsClaimIdReleaseResponse200 | None:
    if response.status_code == 200:
        response_200 = PostV1ClaimsClaimIdReleaseResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[PostV1ClaimsClaimIdReleaseResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    claim_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[PostV1ClaimsClaimIdReleaseResponse200]:
    """
    Args:
        claim_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostV1ClaimsClaimIdReleaseResponse200]
    """

    kwargs = _get_kwargs(
        claim_id=claim_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    claim_id: str,
    *,
    client: AuthenticatedClient,
) -> PostV1ClaimsClaimIdReleaseResponse200 | None:
    """
    Args:
        claim_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostV1ClaimsClaimIdReleaseResponse200
    """

    return sync_detailed(
        claim_id=claim_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    claim_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[PostV1ClaimsClaimIdReleaseResponse200]:
    """
    Args:
        claim_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostV1ClaimsClaimIdReleaseResponse200]
    """

    kwargs = _get_kwargs(
        claim_id=claim_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    claim_id: str,
    *,
    client: AuthenticatedClient,
) -> PostV1ClaimsClaimIdReleaseResponse200 | None:
    """
    Args:
        claim_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostV1ClaimsClaimIdReleaseResponse200
    """

    return (
        await asyncio_detailed(
            claim_id=claim_id,
            client=client,
        )
    ).parsed
