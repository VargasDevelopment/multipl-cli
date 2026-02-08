from __future__ import annotations

import typer

from multipl_cli.config import load_config, save_config
from multipl_cli.console import console


def init_command(
    base_url: str | None = typer.Option(None, "--base-url", help="API base URL"),
    profile_name: str = typer.Option("default", "--profile", help="Profile name"),
    poster_key: str | None = typer.Option(None, "--poster-key", help="Poster API key"),
    worker_key: str | None = typer.Option(None, "--worker-key", help="Worker API key"),
    payer: str | None = typer.Option(None, "--payer", help="Payer type (manual|local_key|cdp)"),
) -> None:
    config = load_config()
    if base_url:
        config.base_url = base_url
    profile = config.ensure_profile(profile_name)
    if poster_key is not None:
        profile.poster_api_key = poster_key
    if worker_key is not None:
        profile.worker_api_key = worker_key
    if payer:
        config.payer.type = payer
    config.active_profile = profile_name
    save_config(config)
    console.print("[green]Config initialized.[/green]")
