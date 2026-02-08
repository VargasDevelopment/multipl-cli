from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_v1_task_types_response_200_item import GetV1TaskTypesResponse200Item
from ...models.get_v1_task_types_role import GetV1TaskTypesRole
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    role: GetV1TaskTypesRole | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_role: str | Unset = UNSET
    if not isinstance(role, Unset):
        json_role = role.value

    params["role"] = json_role

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/task-types",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> list[GetV1TaskTypesResponse200Item] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = GetV1TaskTypesResponse200Item.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[list[GetV1TaskTypesResponse200Item]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    role: GetV1TaskTypesRole | Unset = UNSET,
) -> Response[list[GetV1TaskTypesResponse200Item]]:
    """
    Args:
        role (GetV1TaskTypesRole | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list[GetV1TaskTypesResponse200Item]]
    """

    kwargs = _get_kwargs(
        role=role,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    role: GetV1TaskTypesRole | Unset = UNSET,
) -> list[GetV1TaskTypesResponse200Item] | None:
    """
    Args:
        role (GetV1TaskTypesRole | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list[GetV1TaskTypesResponse200Item]
    """

    return sync_detailed(
        client=client,
        role=role,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    role: GetV1TaskTypesRole | Unset = UNSET,
) -> Response[list[GetV1TaskTypesResponse200Item]]:
    """
    Args:
        role (GetV1TaskTypesRole | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list[GetV1TaskTypesResponse200Item]]
    """

    kwargs = _get_kwargs(
        role=role,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    role: GetV1TaskTypesRole | Unset = UNSET,
) -> list[GetV1TaskTypesResponse200Item] | None:
    """
    Args:
        role (GetV1TaskTypesRole | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list[GetV1TaskTypesResponse200Item]
    """

    return (
        await asyncio_detailed(
            client=client,
            role=role,
        )
    ).parsed
