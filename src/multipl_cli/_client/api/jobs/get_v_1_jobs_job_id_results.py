from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_v1_jobs_job_id_results_response_200 import GetV1JobsJobIdResultsResponse200
from ...models.get_v1_jobs_job_id_results_response_402 import GetV1JobsJobIdResultsResponse402
from ...types import Response


def _get_kwargs(
    job_id: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/jobs/{job_id}/results".format(
            job_id=quote(str(job_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> GetV1JobsJobIdResultsResponse200 | GetV1JobsJobIdResultsResponse402 | None:
    if response.status_code == 200:
        response_200 = GetV1JobsJobIdResultsResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 402:
        response_402 = GetV1JobsJobIdResultsResponse402.from_dict(response.json())

        return response_402

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[GetV1JobsJobIdResultsResponse200 | GetV1JobsJobIdResultsResponse402]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    job_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[GetV1JobsJobIdResultsResponse200 | GetV1JobsJobIdResultsResponse402]:
    """
    Args:
        job_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetV1JobsJobIdResultsResponse200 | GetV1JobsJobIdResultsResponse402]
    """

    kwargs = _get_kwargs(
        job_id=job_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    job_id: str,
    *,
    client: AuthenticatedClient,
) -> GetV1JobsJobIdResultsResponse200 | GetV1JobsJobIdResultsResponse402 | None:
    """
    Args:
        job_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetV1JobsJobIdResultsResponse200 | GetV1JobsJobIdResultsResponse402
    """

    return sync_detailed(
        job_id=job_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    job_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[GetV1JobsJobIdResultsResponse200 | GetV1JobsJobIdResultsResponse402]:
    """
    Args:
        job_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetV1JobsJobIdResultsResponse200 | GetV1JobsJobIdResultsResponse402]
    """

    kwargs = _get_kwargs(
        job_id=job_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    job_id: str,
    *,
    client: AuthenticatedClient,
) -> GetV1JobsJobIdResultsResponse200 | GetV1JobsJobIdResultsResponse402 | None:
    """
    Args:
        job_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetV1JobsJobIdResultsResponse200 | GetV1JobsJobIdResultsResponse402
    """

    return (
        await asyncio_detailed(
            job_id=job_id,
            client=client,
        )
    ).parsed
