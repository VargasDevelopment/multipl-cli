from __future__ import annotations

import typer

from multipl_cli import __version__
from multipl_cli.app_state import AppState
from multipl_cli.commands import (
    auth,
    claim,
    config_cmd,
    job,
    profile,
    result,
    submit,
    task,
    template,
)
from multipl_cli.commands.init import init_command
from multipl_cli.config import TRAINING_BASE_URL, is_training_base_url, load_config
from multipl_cli.console import console, set_training_mode

app = typer.Typer(no_args_is_help=False, invoke_without_command=True)


@app.callback()
def main(
    ctx: typer.Context,
    profile_name: str = typer.Option(
        None,
        "--profile",
        help="Profile to use (defaults to active profile)",
    ),
    base_url: str | None = typer.Option(
        None,
        "--base-url",
        help="Override base URL for this command",
    ),
    training: bool = typer.Option(
        False,
        "--training",
        help=f"Run this command against training mode ({TRAINING_BASE_URL})",
    ),
    version: bool = typer.Option(False, "--version", help="Show version", is_eager=True),
) -> None:
    if version:
        console.print(__version__)
        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())
        raise typer.Exit()

    config = load_config()
    if profile_name:
        if profile_name not in config.profiles:
            console.print(f"[red]Unknown profile '{profile_name}'.[/red]")
            raise typer.Exit(code=1)
        config.active_profile = profile_name
    active_profile = config.get_active_profile()
    active_profile_name = active_profile.name
    profile_base_url = active_profile.base_url or config.base_url
    if training and base_url:
        console.print("[red]Use either --training or --base-url, not both.[/red]")
        raise typer.Exit(code=1)
    effective_base_url = TRAINING_BASE_URL if training else (base_url or profile_base_url)
    training_mode = is_training_base_url(effective_base_url)
    set_training_mode(training_mode)

    ctx.obj = AppState(
        config=config,
        profile_name=active_profile_name,
        base_url=effective_base_url,
        training_mode=training_mode,
    )


app.add_typer(config_cmd.app, name="config")
app.add_typer(auth.app, name="auth")
app.add_typer(profile.app, name="profile")
app.add_typer(job.app, name="job")
app.add_typer(task.app, name="task")
app.add_typer(template.app, name="template")
app.add_typer(claim.app, name="claim")
app.add_typer(submit.app, name="submit")
app.add_typer(result.app, name="result")

app.command("init")(init_command)
