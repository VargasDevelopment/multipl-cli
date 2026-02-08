from __future__ import annotations

import typer
from rich.table import Table

from multipl_cli.app_state import AppState
from multipl_cli.config import load_config, mask_secret, save_config
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


@app.command("set")
def set_config(
    key: str = typer.Argument(..., help="Config key (payer|base_url)"),
    value: str = typer.Argument(..., help="Config value"),
) -> None:
    config = load_config()
    if key == "payer":
        config.payer.type = value
        save_config(config)
        console.print(f"[green]Payer set to {value}.[/green]")
        return
    if key == "base_url":
        config.base_url = value
        save_config(config)
        console.print(f"[green]Base URL set to {value}.[/green]")
        return
    console.print("[red]Unknown config key. Use payer or base_url.[/red]")
    raise typer.Exit(code=1)
