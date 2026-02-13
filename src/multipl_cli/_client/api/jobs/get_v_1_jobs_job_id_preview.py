from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_v1_jobs_job_id_preview_response_200_type_0 import (
    GetV1JobsJobIdPreviewResponse200Type0,
)
from ...models.get_v1_jobs_job_id_preview_response_200_type_1 import (
    GetV1JobsJobIdPreviewResponse200Type1,
)
from ...types import Response


def _get_kwargs(
    job_id: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/jobs/{job_id}/preview".format(
            job_id=quote(str(job_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> GetV1JobsJobIdPreviewResponse200Type0 | GetV1JobsJobIdPreviewResponse200Type1 | None:
    if response.status_code == 200:

        def _parse_response_200(
            data: object,
        ) -> GetV1JobsJobIdPreviewResponse200Type0 | GetV1JobsJobIdPreviewResponse200Type1:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                response_200_type_0 = GetV1JobsJobIdPreviewResponse200Type0.from_dict(data)

                return response_200_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            response_200_type_1 = GetV1JobsJobIdPreviewResponse200Type1.from_dict(data)

            return response_200_type_1

        response_200 = _parse_response_200(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[GetV1JobsJobIdPreviewResponse200Type0 | GetV1JobsJobIdPreviewResponse200Type1]:
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
) -> Response[GetV1JobsJobIdPreviewResponse200Type0 | GetV1JobsJobIdPreviewResponse200Type1]:
    """
    Args:
        job_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetV1JobsJobIdPreviewResponse200Type0 | GetV1JobsJobIdPreviewResponse200Type1]
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
) -> GetV1JobsJobIdPreviewResponse200Type0 | GetV1JobsJobIdPreviewResponse200Type1 | None:
    """
    Args:
        job_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetV1JobsJobIdPreviewResponse200Type0 | GetV1JobsJobIdPreviewResponse200Type1
    """

    return sync_detailed(
        job_id=job_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    job_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[GetV1JobsJobIdPreviewResponse200Type0 | GetV1JobsJobIdPreviewResponse200Type1]:
    """
    Args:
        job_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetV1JobsJobIdPreviewResponse200Type0 | GetV1JobsJobIdPreviewResponse200Type1]
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
) -> GetV1JobsJobIdPreviewResponse200Type0 | GetV1JobsJobIdPreviewResponse200Type1 | None:
    """
    Args:
        job_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetV1JobsJobIdPreviewResponse200Type0 | GetV1JobsJobIdPreviewResponse200Type1
    """

    return (
        await asyncio_detailed(
            job_id=job_id,
            client=client,
        )
    ).parsed
