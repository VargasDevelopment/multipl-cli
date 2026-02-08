from __future__ import annotations

import typer

from multipl_cli.commands.auth import login as auth_login
from multipl_cli.console import console


def init_command(
    ctx: typer.Context,
    base_url: str | None = typer.Option(None, "--base-url", help="API base URL"),
    profile_name: str = typer.Option("default", "--profile", help="Profile name"),
    non_interactive: bool = typer.Option(
        False, "--non-interactive", help="Disable prompts"
    ),
    poster: bool | None = typer.Option(
        None, "--poster/--no-poster", help="Register poster identity"
    ),
    worker: bool | None = typer.Option(
        None, "--worker/--no-worker", help="Register worker identity"
    ),
    all_identities: bool = typer.Option(
        False, "--all", help="Register both poster and worker"
    ),
    show_keys: bool = typer.Option(False, "--show-keys", help="Show full API keys"),
    json_output: bool = typer.Option(False, "--json", help="Output JSON summary"),
) -> None:
    console.print(
        "[yellow]`multipl init` is deprecated. Launching `multipl auth login`...[/yellow]"
    )
    auth_login(
        ctx=ctx,
        base_url=base_url,
        profile_name=profile_name,
        non_interactive=non_interactive,
        poster=poster,
        worker=worker,
        all_identities=all_identities,
        show_keys=show_keys,
        json_output=json_output,
    )
