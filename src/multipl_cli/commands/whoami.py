from __future__ import annotations

import typer
from rich.table import Table

from multipl_cli._client.api.metrics.get_v1_metrics_posters_me import (
    sync_detailed as get_poster_metrics,
)
from multipl_cli._client.api.metrics.get_v1_metrics_workers_me import (
    sync_detailed as get_worker_metrics,
)
from multipl_cli._client.api.workers.get_v1_workers_me import sync_detailed as get_worker_me
from multipl_cli.app_state import AppState
from multipl_cli.console import console
from multipl_cli.openapi_client import build_client, ensure_client_available

app = typer.Typer(no_args_is_help=True)


@app.command("whoami")
def whoami(
    ctx: typer.Context,
    json_output: bool = typer.Option(False, "--json", help="Output JSON"),
) -> None:
    state = ctx.obj
    if not isinstance(state, AppState):
        console.print("[red]Internal error: missing app state[/red]")
        raise typer.Exit(code=1)

    ensure_client_available()
    profile = state.config.get_active_profile()
    client = build_client(state.base_url)

    if not profile.worker_api_key and not profile.poster_api_key:
        console.print("[yellow]No API keys configured for active profile.[/yellow]")
        raise typer.Exit(code=1)

    payload: dict = {}

    if profile.worker_api_key:
        response = get_worker_me(client=client, authorization=f"Bearer {profile.worker_api_key}")
        if response.status_code == 200 and response.parsed is not None:
            worker = response.parsed.worker
            payload["worker"] = worker.to_dict()
            if not json_output:
                table = Table(title="Worker")
                table.add_column("Field")
                table.add_column("Value")
                table.add_row("id", worker.id)
                table.add_row("name", worker.name)
                table.add_row("claimed", str(worker.is_claimed))
                table.add_row("claimedByPosterId", str(worker.claimed_by_poster_id))
                console.print(table)

            metrics = get_worker_metrics(
                client=client, authorization=f"Bearer {profile.worker_api_key}"
            )
            if metrics.status_code == 200 and metrics.parsed is not None:
                payload["worker_metrics"] = metrics.parsed.to_dict()
                if not json_output:
                    console.print({"worker_metrics": metrics.parsed.to_dict()})
        else:
            console.print(
                f"[red]Failed to fetch worker info (status={response.status_code}).[/red]"
            )

    if profile.poster_api_key:
        metrics = get_poster_metrics(
            client=client, authorization=f"Bearer {profile.poster_api_key}"
        )
        if metrics.status_code == 200 and metrics.parsed is not None:
            payload["poster_metrics"] = metrics.parsed.to_dict()
            if not json_output:
                console.print({"poster_metrics": metrics.parsed.to_dict()})
        else:
            console.print(
                f"[red]Failed to fetch poster metrics (status={metrics.status_code}).[/red]"
            )

    if json_output and payload:
        console.print(payload)
