from __future__ import annotations

import typer
from rich.table import Table

from multipl_cli._client.api.jobs.get_v_1_jobs_job_id import sync_detailed as get_job
from multipl_cli._client.api.public.get_v1_public_jobs import sync_detailed as list_public_jobs
from multipl_cli._client.api.public.get_v_1_public_jobs_job_id import (
    sync_detailed as get_public_job,
)
from multipl_cli._client.types import UNSET
from multipl_cli.app_state import AppState
from multipl_cli.console import console
from multipl_cli.openapi_client import build_client, ensure_client_available

app = typer.Typer(no_args_is_help=True)


@app.command("list")
def list_jobs(
    ctx: typer.Context,
    task_type: str | None = typer.Option(None, "--task-type", help="Filter by task type"),
    status: str | None = typer.Option(None, "--status", help="Filter by status"),
    limit: int = typer.Option(50, "--limit", help="Max jobs to return"),
    json_output: bool = typer.Option(False, "--json", help="Output JSON"),
) -> None:
    state = ctx.obj
    if not isinstance(state, AppState):
        console.print("[red]Internal error: missing app state[/red]")
        raise typer.Exit(code=1)

    ensure_client_available()
    client = build_client(state.base_url)

    response = list_public_jobs(
        client=client,
        state=status or UNSET,
        task_type=task_type or UNSET,
        limit=limit,
    )

    if response.status_code != 200 or response.parsed is None:
        console.print(f"[red]Failed to list jobs (status={response.status_code}).[/red]")
        raise typer.Exit(code=2)

    jobs = response.parsed.jobs
    if json_output:
        next_cursor = (
            None if response.parsed.next_cursor is UNSET else response.parsed.next_cursor
        )
        console.print(
            {
                "jobs": [job.to_dict() for job in jobs],
                "next_cursor": next_cursor,
            }
        )
        return

    table = Table(title="Jobs")
    table.add_column("ID")
    table.add_column("Task Type")
    table.add_column("State")
    table.add_column("Payout (c)")
    table.add_column("Created")
    table.add_column("Claimed")
    table.add_column("Submitted")
    table.add_column("Completed")

    for job in jobs:
        table.add_row(
            job.id,
            job.task_type,
            job.state,
            str(job.payout_cents) if job.payout_cents is not None else "-",
            job.created_at,
            job.claimed_at or "-",
            job.submitted_at or "-",
            job.completed_at or "-",
        )

    console.print(table)
    if response.parsed.next_cursor:
        console.print(f"Next cursor: {response.parsed.next_cursor}")


@app.command("get")
def get_job_cmd(
    ctx: typer.Context,
    job_id: str = typer.Argument(..., help="Job ID"),
    public: bool = typer.Option(False, "--public", help="Force public job view"),
    json_output: bool = typer.Option(False, "--json", help="Output JSON"),
) -> None:
    state = ctx.obj
    if not isinstance(state, AppState):
        console.print("[red]Internal error: missing app state[/red]")
        raise typer.Exit(code=1)

    ensure_client_available()
    profile = state.config.get_active_profile()

    if not public and profile.poster_api_key:
        client = build_client(state.base_url)
        response = get_job(client=client, job_id=job_id, authorization=f"Bearer {profile.poster_api_key}")
        if response.status_code == 200 and response.parsed is not None:
            console.print(response.parsed.to_dict() if json_output else response.parsed.to_dict())
            return
        if response.status_code not in {401, 403, 404}:
            console.print(f"[red]Failed to fetch job (status={response.status_code}).[/red]")
            raise typer.Exit(code=2)

    client = build_client(state.base_url)
    response = get_public_job(client=client, job_id=job_id)
    if response.status_code != 200 or response.parsed is None:
        console.print(f"[red]Failed to fetch public job (status={response.status_code}).[/red]")
        raise typer.Exit(code=2)
    console.print(response.parsed.to_dict() if json_output else response.parsed.to_dict())
