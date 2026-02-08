from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_v1x402_verify_response_200 import GetV1X402VerifyResponse200
from ...models.get_v1x402_verify_response_402 import GetV1X402VerifyResponse402
from ...types import Response


def _get_kwargs() -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/x402/verify",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> GetV1X402VerifyResponse200 | GetV1X402VerifyResponse402 | None:
    if response.status_code == 200:
        response_200 = GetV1X402VerifyResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 402:
        response_402 = GetV1X402VerifyResponse402.from_dict(response.json())

        return response_402

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[GetV1X402VerifyResponse200 | GetV1X402VerifyResponse402]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[GetV1X402VerifyResponse200 | GetV1X402VerifyResponse402]:
    """Verification-only x402 endpoint. No auth required. See https://multipl.dev/skill.md for real
    integration.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetV1X402VerifyResponse200 | GetV1X402VerifyResponse402]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
) -> GetV1X402VerifyResponse200 | GetV1X402VerifyResponse402 | None:
    """Verification-only x402 endpoint. No auth required. See https://multipl.dev/skill.md for real
    integration.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetV1X402VerifyResponse200 | GetV1X402VerifyResponse402
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[GetV1X402VerifyResponse200 | GetV1X402VerifyResponse402]:
    """Verification-only x402 endpoint. No auth required. See https://multipl.dev/skill.md for real
    integration.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetV1X402VerifyResponse200 | GetV1X402VerifyResponse402]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
) -> GetV1X402VerifyResponse200 | GetV1X402VerifyResponse402 | None:
    """Verification-only x402 endpoint. No auth required. See https://multipl.dev/skill.md for real
    integration.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetV1X402VerifyResponse200 | GetV1X402VerifyResponse402
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
