from __future__ import annotations

from pathlib import Path

import typer

from multipl_cli.console import console
from multipl_cli.private_dispatch.config import DispatchConfigError, load_dispatch_config
from multipl_cli.private_dispatch.scheduler import run_dispatch

app = typer.Typer(no_args_is_help=True)


@app.command("dispatch-once")
def dispatch_once(
    config_path: Path = typer.Option(
        ...,
        "--config",
        exists=False,
        dir_okay=False,
        help="Path to the private dispatcher JSON config (must be mode 0600)",
    ),
) -> None:
    try:
        config = load_dispatch_config(config_path)
    except DispatchConfigError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=2) from exc
    result = run_dispatch(config)
    console.print(result.message)
    if result.code:
        raise typer.Exit(code=result.code)
