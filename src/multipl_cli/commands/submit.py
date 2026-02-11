from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

import typer
from rich.table import Table

from multipl_cli._client.models.post_v1_claims_claim_id_submit_body import (
    PostV1ClaimsClaimIdSubmitBody,
)
from multipl_cli.acceptance import validate_acceptance
from multipl_cli.app_state import AppState
from multipl_cli.config import ClaimsCache
from multipl_cli.console import console
from multipl_cli.openapi_client import build_client, ensure_client_available

app = typer.Typer(no_args_is_help=True)


def _load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text())
    except Exception as exc:
        raise typer.BadParameter(f"Invalid JSON file: {exc}") from exc


def _fetch_acceptance_contract(client, job_id: str):
    response = client.get_httpx_client().request("get", f"/v1/public/jobs/{job_id}")
    if response.status_code != 200:
        console.print(f"[red]Failed to fetch job (status={response.status_code}).[/red]")
        raise typer.Exit(code=2)
    payload = response.json()
    if not isinstance(payload, dict):
        console.print("[red]Invalid public job response payload.[/red]")
        raise typer.Exit(code=2)
    job_payload = payload.get("job")
    if not isinstance(job_payload, dict):
        console.print("[red]Invalid public job response payload.[/red]")
        raise typer.Exit(code=2)
    acceptance_contract = job_payload.get("acceptanceContract")
    stages = payload.get("stages")
    is_staged = isinstance(stages, list) and len(stages) > 0
    return acceptance_contract, is_staged


def _build_validation_report(
    *,
    acceptance_contract: Any,
    payload: Any,
    is_staged: bool,
):
    if not is_staged:
        return validate_acceptance(acceptance_contract, payload), False

    report = validate_acceptance(None, payload)
    if report.checks:
        report.checks[0]["reason"] = "skipped local validation for staged job; server validates stage acceptance"
    return report, True


def _render_report(report):
    table = Table(title=f"Acceptance Report ({report.status})")
    table.add_column("Check")
    table.add_column("Passed")
    table.add_column("Reason")
    for check in report.checks:
        table.add_row(
            str(check.get("name")),
            "yes" if check.get("passed") else "no",
            str(check.get("reason") or ""),
        )
    console.print(table)


@app.command("validate")
def validate(
    ctx: typer.Context,
    job_id: str = typer.Option(..., "--job", help="Job ID"),
    file: Path = typer.Option(..., "--file", exists=True, dir_okay=False),
    json_output: bool = typer.Option(False, "--json", help="Output JSON"),
) -> None:
    state = ctx.obj
    if not isinstance(state, AppState):
        console.print("[red]Internal error: missing app state[/red]")
        raise typer.Exit(code=1)

    ensure_client_available()
    client = build_client(state.base_url)

    payload = _load_json(file)
    acceptance_contract, is_staged = _fetch_acceptance_contract(client, job_id)
    report, skipped_for_staged = _build_validation_report(
        acceptance_contract=acceptance_contract,
        payload=payload,
        is_staged=is_staged,
    )
    if skipped_for_staged and not json_output:
        console.print(
            "[yellow]Skipping local acceptance validation for staged jobs; server validation applies.[/yellow]"
        )
    if json_output:
        console.print(asdict(report))
    else:
        _render_report(report)

    if report.status in {"fail", "error"}:
        raise typer.Exit(code=1)


@app.command("send")
def send(
    ctx: typer.Context,
    job_id: str = typer.Option(..., "--job", help="Job ID"),
    file: Path = typer.Option(..., "--file", exists=True, dir_okay=False),
    claim_id: str | None = typer.Option(None, "--claim", help="Claim ID override"),
    force: bool = typer.Option(False, "--force", help="Send even if validation fails"),
    json_output: bool = typer.Option(False, "--json", help="Output JSON"),
) -> None:
    state = ctx.obj
    if not isinstance(state, AppState):
        console.print("[red]Internal error: missing app state[/red]")
        raise typer.Exit(code=1)

    ensure_client_available()
    profile = state.config.get_active_profile()
    if not profile.worker_api_key:
        console.print("[red]Worker API key not configured for active profile.[/red]")
        raise typer.Exit(code=2)

    client = build_client(state.base_url)
    payload = _load_json(file)

    if not force:
        acceptance_contract, is_staged = _fetch_acceptance_contract(client, job_id)
        report, skipped_for_staged = _build_validation_report(
            acceptance_contract=acceptance_contract,
            payload=payload,
            is_staged=is_staged,
        )
        if skipped_for_staged and not json_output:
            console.print(
                "[yellow]Skipping local acceptance validation for staged jobs; server validation applies.[/yellow]"
            )
        if json_output:
            console.print(asdict(report))
        else:
            _render_report(report)
        if report.status in {"fail", "error"}:
            if not json_output:
                console.print("[red]Validation failed. Use --force to override.[/red]")
            raise typer.Exit(code=1)

    resolved_claim_id = claim_id
    if not resolved_claim_id:
        cache = ClaimsCache.load()
        resolved_claim_id = cache.get_claim(state.profile_name, job_id)
    if not resolved_claim_id:
        console.print(
            "[red]Claim ID not found for this job. Provide --claim or acquire via CLI.[/red]"
        )
        raise typer.Exit(code=1)

    body = PostV1ClaimsClaimIdSubmitBody(output=payload)
    response = client.get_httpx_client().request(
        "post",
        f"/v1/claims/{resolved_claim_id}/submit",
        headers={
            "authorization": f"Bearer {profile.worker_api_key}",
            "Content-Type": "application/json",
        },
        json=body.to_dict(),
    )

    if response.status_code != 200:
        console.print(f"[red]Submit failed (status={response.status_code}).[/red]")
        raise typer.Exit(code=2)

    if json_output:
        try:
            console.print(response.json())
        except Exception:
            console.print({"ok": True})
    else:
        console.print("[green]Submission sent.[/green]")
