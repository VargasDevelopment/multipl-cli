from __future__ import annotations

import json

import typer
from rich.table import Table

from multipl_cli._client.models.post_v1_claims_acquire_response_200 import (
    PostV1ClaimsAcquireResponse200,
)
from multipl_cli._client.models.post_v1_claims_claim_id_release_response_200 import (
    PostV1ClaimsClaimIdReleaseResponse200,
)
from multipl_cli.app_state import AppState
from multipl_cli.config import ClaimsCache
from multipl_cli.console import console
from multipl_cli.openapi_client import build_client, ensure_client_available
from multipl_cli.polling import extract_retry_after_seconds, poll_with_backoff

app = typer.Typer(no_args_is_help=True)


def _parse_json_body(response) -> dict:
    try:
        return response.json()
    except Exception:
        try:
            return json.loads(response.content.decode("utf-8"))
        except Exception:
            return {}


def _print_claim(claim: PostV1ClaimsAcquireResponse200) -> None:
    table = Table(title="Claim Acquired")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("claim.id", claim.claim.id)
    table.add_row("job.id", claim.job.id)
    table.add_row("taskType", claim.job.task_type)
    table.add_row("leaseExpiresAt", claim.claim.lease_expires_at)
    console.print(table)


COOLDOWN_CODES = {
    "worker_expiry_penalty",
    "worker_moderation_cooldown",
    "worker_active_claim_cap",
    "active_claim_limit_reached",
}


def _format_retry_after(retry_after: int | None, *, is_retrying: bool) -> str:
    if retry_after is None:
        return "Retrying with backoff..." if is_retrying else "Retry later."
    return f"{'Retrying' if is_retrying else 'Retry'} after {retry_after}s."


def _render_rate_limit_notice(payload: dict, retry_after: int | None, *, is_retrying: bool) -> str:
    code = payload.get("code") or payload.get("error")
    message = payload.get("message") or payload.get("guidance")
    if code in COOLDOWN_CODES:
        detail = message or "Worker cooldown active."
        return f"{detail} {_format_retry_after(retry_after, is_retrying=is_retrying)}"
    if payload.get("error") == "rate_limited":
        return f"Rate limited. {_format_retry_after(retry_after, is_retrying=is_retrying)}"
    return f"Rate limited. {_format_retry_after(retry_after, is_retrying=is_retrying)}"


@app.command("acquire")
def acquire(
    ctx: typer.Context,
    task_type: str | None = typer.Option(None, "--task-type", help="Task type to claim"),
    job_id: str | None = typer.Option(None, "--job", help="Claim a specific job ID"),
    mode: str = typer.Option(
        "single",
        "--mode",
        help="single | wait | drain",
        case_sensitive=False,
    ),
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
    saw_success = False

    def request_once():
        body: dict[str, str] = {}
        if task_type:
            body["taskType"] = task_type
        if job_id:
            body["jobId"] = job_id
        return client.get_httpx_client().request(
            "post",
            "/v1/claims/acquire",
            headers={
                "authorization": f"Bearer {profile.worker_api_key}",
                "Content-Type": "application/json",
            },
            json=body,
        )

    def handle_success(response):
        nonlocal saw_success
        data = response.json()
        parsed = PostV1ClaimsAcquireResponse200.from_dict(data)
        cache = ClaimsCache.load()
        cache.set_claim(state.profile_name, parsed.job.id, parsed.claim.id)
        cache.save()
        if json_output:
            console.print(parsed.to_dict())
        else:
            _print_claim(parsed)
        saw_success = True

    def handle_empty(_response):
        if mode == "drain" and saw_success:
            if not json_output:
                console.print("No jobs available. Drain complete.")
        else:
            if not json_output:
                console.print("No jobs available. Backing off...")

    def handle_rate_limited(response, retry_after):
        payload = _parse_json_body(response)
        if not json_output:
            console.print(_render_rate_limit_notice(payload, retry_after, is_retrying=True))

    def handle_transient_error(_error):
        if not json_output:
            console.print("Transient error. Retrying with backoff...")

    def handle_non_retryable(response):
        payload = _parse_json_body(response)
        console.print(
            f"[red]Acquire failed (status={response.status_code}).[/red] {payload or ''}"
        )
        if response.status_code in {400, 409, 422}:
            raise typer.Exit(code=1)
        raise typer.Exit(code=2)

    mode = mode.lower()
    if mode not in {"single", "wait", "drain"}:
        console.print("[red]Invalid mode. Use single, wait, or drain.[/red]")
        raise typer.Exit(code=1)
    if bool(task_type) == bool(job_id):
        console.print("[red]Provide exactly one of --task-type or --job.[/red]")
        raise typer.Exit(code=1)
    if job_id and mode != "single":
        console.print("[red]--job only supports --mode single.[/red]")
        raise typer.Exit(code=1)

    if mode == "single":
        response = request_once()
        status = response.status_code
        if status == 200:
            handle_success(response)
            return
        if status == 204:
            if json_output:
                console.print({"status": "empty"})
            else:
                console.print("No jobs available.")
            return
        if status == 429:
            retry_after = extract_retry_after_seconds(response)
            payload = _parse_json_body(response)
            if not json_output:
                console.print(_render_rate_limit_notice(payload, retry_after, is_retrying=False))
            raise typer.Exit(code=4)
        handle_non_retryable(response)
        return

    poll_with_backoff(
        request_fn=request_once,
        mode=mode,
        empty_statuses=[204],
        handle_success=handle_success,
        handle_empty=handle_empty,
        handle_rate_limited=handle_rate_limited,
        handle_transient_error=handle_transient_error,
        handle_non_retryable=handle_non_retryable,
    )


@app.command("release")
def release(
    ctx: typer.Context,
    claim_id: str = typer.Argument(..., help="Claim ID"),
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
    response = client.get_httpx_client().request(
        "post",
        f"/v1/claims/{claim_id}/release",
        headers={"authorization": f"Bearer {profile.worker_api_key}"},
    )

    if response.status_code != 200:
        console.print(f"[red]Release failed (status={response.status_code}).[/red]")
        raise typer.Exit(code=2)

    parsed = PostV1ClaimsClaimIdReleaseResponse200.from_dict(response.json())
    cache = ClaimsCache.load()
    cache.drop_claim(state.profile_name, parsed.job.id)
    cache.save()
    payload = {"ok": parsed.ok, "jobId": parsed.job.id, "claimId": parsed.claim.id}
    if json_output:
        console.print(payload)
    else:
        console.print(payload)
