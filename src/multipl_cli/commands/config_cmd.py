from __future__ import annotations

import typer
from rich.table import Table

from multipl_cli.app_state import AppState
from multipl_cli.config import mask_secret
from multipl_cli.console import console

app = typer.Typer(no_args_is_help=True)


@app.command("show")
def show(ctx: typer.Context) -> None:
    state = ctx.obj
    if not isinstance(state, AppState):
        console.print("[red]Internal error: missing app state[/red]")
        raise typer.Exit(code=1)

    config = state.config
    table = Table(title="Multipl Config")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("base_url", state.base_url)
    table.add_row("active_profile", config.active_profile)
    table.add_row("payer", config.payer.type)
    console.print(table)

    profiles = Table(title="Profiles")
    profiles.add_column("Name")
    profiles.add_column("Poster Key")
    profiles.add_column("Worker Key")
    for name, profile in config.profiles.items():
        profiles.add_row(
            name,
            mask_secret(profile.poster_api_key) or "-",
            mask_secret(profile.worker_api_key) or "-",
        )
    console.print(profiles)
