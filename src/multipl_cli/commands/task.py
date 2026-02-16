from __future__ import annotations

import json
from typing import Any

import httpx
import typer
from rich.table import Table

from multipl_cli._client.api.task_types.get_v1_task_types import sync_detailed as get_task_types
from multipl_cli._client.models.get_v1_task_types_role import GetV1TaskTypesRole
from multipl_cli._client.types import UNSET
from multipl_cli.app_state import AppState
from multipl_cli.console import console
from multipl_cli.openapi_client import build_client, ensure_client_available
from multipl_cli.polling import extract_retry_after_seconds

app = typer.Typer(no_args_is_help=True)


def _parse_response_json(response) -> Any | None:
    try:
        return json.loads(response.content.decode("utf-8"))
    except Exception:
        return None


@app.command("list")
def list_task_types(
    ctx: typer.Context,
    role: str | None = typer.Option(
        None,
        "--role",
        help="Optional role filter: worker | verifier | both",
    ),
    json_output: bool = typer.Option(False, "--json", help="Output JSON"),
) -> None:
    state = ctx.obj
    if not isinstance(state, AppState):
        console.print("[red]Internal error: missing app state[/red]")
        raise typer.Exit(code=1)

    ensure_client_available()
    client = build_client(state.base_url)

    role_param = UNSET
    if role is not None:
        role_value = role.strip().lower()
        try:
            role_param = GetV1TaskTypesRole(role_value)
        except ValueError as exc:
            allowed = ", ".join(item.value for item in GetV1TaskTypesRole)
            console.print(f"[red]Invalid role '{role}'. Allowed values: {allowed}.[/red]")
            raise typer.Exit(code=1) from exc

    try:
        response = get_task_types(
            client=client,
            role=role_param,
        )
    except httpx.HTTPError as exc:
        console.print(f"[red]Network error: {exc}[/red]")
        raise typer.Exit(code=2) from exc

    if response.status_code == 429:
        retry_after = extract_retry_after_seconds(
            httpx.Response(
                status_code=int(response.status_code),
                headers=response.headers,
                content=response.content,
            )
        )
        if retry_after is not None:
            console.print(f"Rate limited. Retry after {retry_after}s.")
        else:
            console.print("Rate limited.")
        raise typer.Exit(code=4)

    if response.status_code != 200:
        if response.status_code in {401, 403}:
            console.print("[red]Task registry request unauthorized.[/red]")
        else:
            console.print(
                f"[red]Failed to list task types (status={response.status_code}).[/red]"
            )
        body = _parse_response_json(response)
        if body is not None:
            console.print(body)
        raise typer.Exit(code=2)

    payload = _parse_response_json(response)
    if payload is None and response.parsed is not None:
        payload = [item.to_dict() for item in response.parsed]
    if not isinstance(payload, list):
        console.print("[red]Invalid task types response payload.[/red]")
        raise typer.Exit(code=2)

    if json_output:
        console.print(payload)
        return

    table = Table(title="Task Types")
    table.add_column("Task Type")
    table.add_column("Name")
    table.add_column("Role")
    table.add_column("Public")

    for item in payload:
        if not isinstance(item, dict):
            continue
        table.add_row(
            str(item.get("id", "-")),
            str(item.get("displayName", "-")),
            str(item.get("role", "-")),
            str(item.get("public", "-")),
        )

    console.print(table)
