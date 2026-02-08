from __future__ import annotations

import typer
from rich.table import Table

from multipl_cli.commands.whoami import whoami as whoami_command
from multipl_cli.config import load_config, mask_secret, save_config
from multipl_cli.console import console

app = typer.Typer(no_args_is_help=True)

app.command("whoami")(whoami_command)


@app.command("list")
def list_profiles() -> None:
    config = load_config()
    table = Table(title="Profiles")
    table.add_column("Active")
    table.add_column("Name")
    table.add_column("Poster Key")
    table.add_column("Worker Key")
    for name, profile in config.profiles.items():
        active = "*" if name == config.active_profile else ""
        table.add_row(
            active,
            name,
            mask_secret(profile.poster_api_key) or "-",
            mask_secret(profile.worker_api_key) or "-",
        )
    console.print(table)


@app.command("use")
def use_profile(name: str = typer.Argument(..., help="Profile name")) -> None:
    config = load_config()
    if name not in config.profiles:
        console.print(f"[red]Profile '{name}' not found.[/red]")
        raise typer.Exit(code=1)
    config.active_profile = name
    save_config(config)
    console.print(f"[green]Active profile set to {name}.[/green]")


@app.command("create")
def create_profile(
    name: str = typer.Argument(..., help="Profile name"),
    poster_key: str | None = typer.Option(None, "--poster-key", help="Poster API key"),
    worker_key: str | None = typer.Option(None, "--worker-key", help="Worker API key"),
    use: bool = typer.Option(True, "--use/--no-use", help="Set as active profile"),
) -> None:
    config = load_config()
    if name in config.profiles:
        console.print(f"[red]Profile '{name}' already exists.[/red]")
        raise typer.Exit(code=1)
    profile = config.ensure_profile(name)
    profile.poster_api_key = poster_key
    profile.worker_api_key = worker_key
    if use:
        config.active_profile = name
    save_config(config)
    console.print(f"[green]Profile '{name}' created.[/green]")


@app.command("delete")
def delete_profile(name: str = typer.Argument(..., help="Profile name")) -> None:
    config = load_config()
    if name not in config.profiles:
        console.print(f"[red]Profile '{name}' not found.[/red]")
        raise typer.Exit(code=1)
    config.profiles.pop(name)
    if config.active_profile == name:
        config.active_profile = next(iter(config.profiles.keys()), "default")
        if config.active_profile == "default" and "default" not in config.profiles:
            config.ensure_profile("default")
    save_config(config)
    console.print(f"[green]Profile '{name}' deleted.[/green]")
