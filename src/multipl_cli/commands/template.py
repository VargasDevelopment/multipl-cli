from __future__ import annotations

import json
from typing import Any

import httpx
import typer
from rich.table import Table

from multipl_cli._client.api.templates.get_v1_templates import sync_detailed as list_templates
from multipl_cli._client.api.templates.get_v1_templates_id import (
    sync_detailed as get_template_by_id,
)
from multipl_cli._client.api.training.get_v1_training_templates import (
    sync_detailed as list_training_templates,
)
from multipl_cli._client.api.training.get_v1_training_templates_id import (
    sync_detailed as get_training_template_by_id,
)
from multipl_cli.app_state import AppState
from multipl_cli.config import resolve_poster_api_key
from multipl_cli.console import console
from multipl_cli.openapi_client import build_client, ensure_client_available
from multipl_cli.polling import extract_retry_after_seconds

app = typer.Typer(no_args_is_help=True)


def _parse_response_json(response) -> Any | None:
    try:
        return json.loads(response.content.decode("utf-8"))
    except Exception:
        return None


def _truncate(text: str, max_len: int = 120) -> str:
    if len(text) <= max_len:
        return text
    return f"{text[: max_len - 3]}..."


def _format_one_of_hint(input_schema: dict[str, Any]) -> str | None:
    one_of = input_schema.get("oneOf")
    if not isinstance(one_of, list) or not one_of:
        return None

    groups: list[str] = []
    for candidate in one_of:
        if not isinstance(candidate, dict):
            continue
        required = candidate.get("required")
        if not isinstance(required, list) or not required:
            continue
        names = [str(value) for value in required]
        groups.append(" and ".join(names))

    if not groups:
        return None
    return f"requires one of: {' or '.join(groups)}"


@app.command("list")
def list_templates_cmd(
    ctx: typer.Context,
    json_output: bool = typer.Option(False, "--json", help="Output JSON"),
    limit: int | None = typer.Option(None, "--limit", min=1, help="Limit templates"),
    query: str | None = typer.Option(
        None,
        "--query",
        help="Filter templates by id/displayName substring",
    ),
) -> None:
    state = ctx.obj
    if not isinstance(state, AppState):
        console.print("[red]Internal error: missing app state[/red]")
        raise typer.Exit(code=1)

    ensure_client_available()
    profile = state.config.get_active_profile()
    poster_api_key = resolve_poster_api_key(profile)
    if not state.training_mode and not poster_api_key:
        console.print("[red]Poster API key not configured for active profile.[/red]")
        raise typer.Exit(code=2)

    try:
        if state.training_mode:
            client = build_client(state.base_url)
            response = list_training_templates(client=client)
        else:
            client = build_client(state.base_url, api_key=poster_api_key)
            response = list_templates(client=client)
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

    if response.status_code in {401, 403}:
        if state.training_mode:
            console.print(
                "[red]Training template endpoint unavailable for current base URL/profile.[/red]"
            )
        else:
            console.print("[red]Poster key required or invalid key.[/red]")
        body = _parse_response_json(response)
        if body is not None:
            console.print(body)
        raise typer.Exit(code=2)

    if response.status_code != 200:
        console.print(f"[red]Failed to list templates (status={response.status_code}).[/red]")
        body = _parse_response_json(response)
        if body is not None:
            console.print(body)
        raise typer.Exit(code=2)

    payload = _parse_response_json(response)
    if payload is None and response.parsed is not None:
        payload = [item.to_dict() for item in response.parsed]
    if not isinstance(payload, list):
        console.print("[red]Invalid templates response payload.[/red]")
        raise typer.Exit(code=2)

    filtered = payload
    if query is not None:
        needle = query.strip().lower()
        filtered = [
            item
            for item in filtered
            if isinstance(item, dict)
            and (
                needle in str(item.get("id", "")).lower()
                or needle in str(item.get("displayName", "")).lower()
            )
        ]

    if limit is not None:
        filtered = filtered[:limit]

    if json_output:
        console.print_json(data=filtered)
        return

    table = Table(title="Templates")
    table.add_column("ID")
    table.add_column("Display Name")
    table.add_column("Stage Count")
    table.add_column("Task Type IDs")
    table.add_column("Public")

    for item in filtered:
        if not isinstance(item, dict):
            continue
        task_type_ids = item.get("taskTypeIds")
        task_type_text = (
            ",".join(str(task_type_id) for task_type_id in task_type_ids)
            if isinstance(task_type_ids, list)
            else "-"
        )
        table.add_row(
            str(item.get("id", "-")),
            str(item.get("displayName", "-")),
            str(item.get("stageCount", "-")),
            task_type_text,
            str(item.get("public", "-")),
        )

    console.print(table)


@app.command("get")
def get_template_cmd(
    ctx: typer.Context,
    template_id: str = typer.Argument(..., help="Template ID"),
    json_output: bool = typer.Option(False, "--json", help="Output JSON"),
    full: bool = typer.Option(False, "--full", help="Show full prompt template text"),
) -> None:
    state = ctx.obj
    if not isinstance(state, AppState):
        console.print("[red]Internal error: missing app state[/red]")
        raise typer.Exit(code=1)

    ensure_client_available()
    profile = state.config.get_active_profile()
    poster_api_key = resolve_poster_api_key(profile)
    if not state.training_mode and not poster_api_key:
        console.print("[red]Poster API key not configured for active profile.[/red]")
        raise typer.Exit(code=2)

    try:
        if state.training_mode:
            client = build_client(state.base_url)
            response = get_training_template_by_id(id=template_id, client=client)
        else:
            client = build_client(state.base_url, api_key=poster_api_key)
            response = get_template_by_id(id=template_id, client=client)
    except httpx.HTTPError as exc:
        console.print(f"[red]Network error: {exc}[/red]")
        raise typer.Exit(code=2) from exc

    if response.status_code in {401, 403}:
        if state.training_mode:
            console.print(
                "[red]Training template endpoint unavailable for current base URL/profile.[/red]"
            )
        else:
            console.print("[red]Poster key required or invalid key.[/red]")
        body = _parse_response_json(response)
        if body is not None:
            console.print(body)
        raise typer.Exit(code=2)

    if response.status_code == 404:
        console.print(f"[red]Template not found: {template_id}[/red]")
        raise typer.Exit(code=1)

    if response.status_code != 200:
        console.print(f"[red]Failed to fetch template (status={response.status_code}).[/red]")
        body = _parse_response_json(response)
        if body is not None:
            console.print(body)
        raise typer.Exit(code=2)

    payload = _parse_response_json(response)
    if payload is None and response.parsed is not None:
        payload = response.parsed.to_dict()
    if not isinstance(payload, dict):
        console.print("[red]Invalid template response payload.[/red]")
        raise typer.Exit(code=2)

    if json_output:
        console.print_json(data=payload)
        return

    console.print(
        f"{payload.get('id', '-')}"
        f"  |  {payload.get('displayName', '-')}"
        f"  |  version={payload.get('version', '-')}"
        f"  |  public={payload.get('public', '-')}"
    )
    console.print(f"Description: {payload.get('description', '-')}")

    input_schema = payload.get("inputSchema")
    if isinstance(input_schema, dict):
        required = input_schema.get("required")
        required_text = (
            ", ".join(str(value) for value in required)
            if isinstance(required, list) and required
            else "(none)"
        )
        console.print(f"Input required fields: {required_text}")
        one_of_hint = _format_one_of_hint(input_schema)
        if one_of_hint is not None:
            console.print(f"Input constraints: {one_of_hint}")

    stages = payload.get("stages")
    if not isinstance(stages, list):
        console.print("[red]Invalid template response payload.[/red]")
        raise typer.Exit(code=2)

    table = Table(title="Stages")
    table.add_column("#")
    table.add_column("Title")
    table.add_column("Task Type ID")
    table.add_column("Capabilities")
    if full:
        table.add_column("Prompt Template")

    for stage in stages:
        if not isinstance(stage, dict):
            continue
        capabilities = stage.get("capabilities")
        capability_text = "-"
        if isinstance(capabilities, dict):
            capability_text = (
                f"net={capabilities.get('requiresNetwork', False)} "
                f"git={capabilities.get('requiresGit', False)} "
                f"sidefx={capabilities.get('allowsSideEffects', False)}"
            )
        row = [
            str(stage.get("index", "-")),
            str(stage.get("title", "-")),
            str(stage.get("taskTypeId", "-")),
            capability_text,
        ]
        if full:
            prompt = str(stage.get("promptTemplate", ""))
            row.append(prompt if full else _truncate(prompt))
        table.add_row(*row)

    console.print(table)

    if not full:
        for stage in stages:
            if not isinstance(stage, dict):
                continue
            prompt = str(stage.get("promptTemplate", ""))
            if prompt:
                console.print(f"Stage {stage.get('index', '-')}: {_truncate(prompt)}")

    console.print(f"Create: multipl job create --template {template_id} ...")
