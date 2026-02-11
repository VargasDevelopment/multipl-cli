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
    return acceptance_contract


def _build_validation_report(
    *,
    acceptance_contract: Any,
    payload: Any,
):
    return validate_acceptance(acceptance_contract, payload)


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


def _failed_checks(acceptance_report: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not isinstance(acceptance_report, dict):
        return []
    checks = acceptance_report.get("checks")
    if not isinstance(checks, list):
        return []
    failures: list[dict[str, Any]] = []
    for check in checks:
        if not isinstance(check, dict):
            continue
        if check.get("passed") is False:
            failures.append(check)
    return failures


def _print_failed_acceptance(acceptance_report: dict[str, Any] | None) -> None:
    console.print("[bold red]FAILED ACCEPTANCE[/bold red]")
    failures = _failed_checks(acceptance_report)
    if failures:
        for check in failures[:5]:
            check_name = str(check.get("name") or "check")
            reason = str(check.get("reason") or "failed")
            console.print(f"[red]- {check_name}: {reason}[/red]")
    else:
        console.print("[red]- Acceptance checks failed on the server.[/red]")
    console.print(
        "[yellow]Next step: edit the payload and resubmit; you can reuse the same job while the lease is valid.[/yellow]"
    )


def _response_json(response) -> dict[str, Any]:
    try:
        payload = response.json()
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


def _cached_job_for_claim(cache: ClaimsCache, profile_name: str, claim_id: str) -> str | None:
    profile_claims = cache.claims_by_profile.get(profile_name, {})
    for cached_job_id, cached_claim_id in profile_claims.items():
        if cached_claim_id == claim_id:
            return cached_job_id
    return None


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
    acceptance_contract = _fetch_acceptance_contract(client, job_id)
    report = _build_validation_report(
        acceptance_contract=acceptance_contract,
        payload=payload,
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
        acceptance_contract = _fetch_acceptance_contract(client, job_id)
        report = _build_validation_report(
            acceptance_contract=acceptance_contract,
            payload=payload,
        )
        if json_output:
            console.print(asdict(report))
        else:
            _render_report(report)
        if report.status in {"fail", "error"}:
            if not json_output:
                console.print("[red]Validation failed. Use --force to override.[/red]")
            raise typer.Exit(code=1)

    cache = ClaimsCache.load()
    profile_claims = cache.claims_by_profile.get(state.profile_name, {})
    other_cached_jobs = [cached_job_id for cached_job_id in profile_claims if cached_job_id != job_id]
    if other_cached_jobs and not json_output:
        console.print(
            f"[yellow]Warning: you also have cached claims for other jobs: {', '.join(other_cached_jobs[:3])}.[/yellow]"
        )

    resolved_claim_id = claim_id
    if not resolved_claim_id:
        resolved_claim_id = cache.get_claim(state.profile_name, job_id)
    if not resolved_claim_id:
        console.print(
            "[red]Claim ID not found for this job. Provide --claim or acquire via CLI.[/red]"
        )
        raise typer.Exit(code=1)

    if claim_id:
        cached_job_id = _cached_job_for_claim(cache, state.profile_name, resolved_claim_id)
        if cached_job_id and cached_job_id != job_id:
            console.print(
                f"[red]Claim {resolved_claim_id} is cached for job {cached_job_id}, not {job_id}.[/red]"
            )
            console.print("[yellow]Use a matching claim or run `multipl claim acquire --job <jobId>`.[/yellow]")
            raise typer.Exit(code=1)

    body = PostV1ClaimsClaimIdSubmitBody(output=payload)
    submit_payload = body.to_dict()
    submit_payload["expectedJobId"] = job_id
    response = client.get_httpx_client().request(
        "post",
        f"/v1/claims/{resolved_claim_id}/submit",
        headers={
            "authorization": f"Bearer {profile.worker_api_key}",
            "Content-Type": "application/json",
        },
        json=submit_payload,
    )

    if response.status_code != 200:
        error_payload = _response_json(response)
        if response.status_code == 409 and error_payload.get("code") == "claim_job_mismatch":
            console.print(
                f"[red]Claim/job mismatch: {error_payload.get('message') or 'claim does not match --job'}[/red]"
            )
            raise typer.Exit(code=1)
        console.print(f"[red]Submit failed (status={response.status_code}).[/red]")
        raise typer.Exit(code=2)

    response_payload = _response_json(response)
    acceptance_report = response_payload.get("acceptanceReport")
    acceptance_status = (
        acceptance_report.get("status")
        if isinstance(acceptance_report, dict)
        else None
    )
    if acceptance_status in {"fail", "error"}:
        if json_output:
            console.print(response_payload)
        else:
            _print_failed_acceptance(acceptance_report if isinstance(acceptance_report, dict) else None)
        raise typer.Exit(code=1)

    if json_output:
        try:
            console.print(response.json())
        except Exception:
            console.print({"ok": True})
    else:
        console.print("[green]Submission accepted (PASS).[/green]")
