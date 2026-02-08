from __future__ import annotations

import json
import uuid
from pathlib import Path

import typer
from rich.table import Table

from multipl_cli._client.api.jobs.get_v_1_jobs_job_id import sync_detailed as get_job
from multipl_cli._client.api.public.get_v1_public_jobs import sync_detailed as list_public_jobs
from multipl_cli._client.api.public.get_v_1_public_jobs_job_id import (
    sync_detailed as get_public_job,
)
from multipl_cli._client.models.post_v1_jobs_body import PostV1JobsBody
from multipl_cli._client.models.post_v1_jobs_body_acceptance import PostV1JobsBodyAcceptance
from multipl_cli._client.models.post_v1_jobs_body_input import PostV1JobsBodyInput
from multipl_cli._client.types import UNSET
from multipl_cli.app_state import AppState
from multipl_cli.console import console
from multipl_cli.openapi_client import build_client, ensure_client_available
from multipl_cli.polling import extract_retry_after_seconds, sleep_with_jitter
from multipl_cli.x402.flow import PaymentFlowError, PaymentRequiredError, request_with_x402
from multipl_cli.x402.payer_cdp import CdpPayer
from multipl_cli.x402.payer_local_key import LocalKeyPayer
from multipl_cli.x402.payer_manual import ManualPayer
from multipl_cli.x402.proof import ProofError, load_proof_from_file, parse_proof_value

app = typer.Typer(no_args_is_help=True)


def _load_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text())
    except Exception as exc:
        raise typer.BadParameter(f"Invalid JSON file: {exc}") from exc
    if not isinstance(data, dict):
        raise typer.BadParameter("JSON must be an object")
    return data


@app.command("list")
def list_jobs(
    ctx: typer.Context,
    task_type: str | None = typer.Option(None, "--task-type", help="Filter by task type"),
    status: str | None = typer.Option(None, "--status", help="Filter by status"),
    limit: int = typer.Option(50, "--limit", help="Max jobs to return"),
    json_output: bool = typer.Option(False, "--json", help="Output JSON"),
) -> None:
    state = ctx.obj
    if not isinstance(state, AppState):
        console.print("[red]Internal error: missing app state[/red]")
        raise typer.Exit(code=1)

    ensure_client_available()
    client = build_client(state.base_url)

    response = list_public_jobs(
        client=client,
        state=status or UNSET,
        task_type=task_type or UNSET,
        limit=limit,
    )

    if response.status_code != 200 or response.parsed is None:
        console.print(f"[red]Failed to list jobs (status={response.status_code}).[/red]")
        raise typer.Exit(code=2)

    jobs = response.parsed.jobs
    if json_output:
        next_cursor = (
            None if response.parsed.next_cursor is UNSET else response.parsed.next_cursor
        )
        console.print(
            {
                "jobs": [job.to_dict() for job in jobs],
                "next_cursor": next_cursor,
            }
        )
        return

    table = Table(title="Jobs")
    table.add_column("ID")
    table.add_column("Task Type")
    table.add_column("State")
    table.add_column("Payout (c)")
    table.add_column("Created")
    table.add_column("Claimed")
    table.add_column("Submitted")
    table.add_column("Completed")

    for job in jobs:
        table.add_row(
            job.id,
            job.task_type,
            job.state,
            str(job.payout_cents) if job.payout_cents is not None else "-",
            job.created_at,
            job.claimed_at or "-",
            job.submitted_at or "-",
            job.completed_at or "-",
        )

    console.print(table)
    if response.parsed.next_cursor:
        console.print(f"Next cursor: {response.parsed.next_cursor}")


@app.command("get")
def get_job_cmd(
    ctx: typer.Context,
    job_id: str = typer.Argument(..., help="Job ID"),
    public: bool = typer.Option(False, "--public", help="Force public job view"),
    json_output: bool = typer.Option(False, "--json", help="Output JSON"),
) -> None:
    state = ctx.obj
    if not isinstance(state, AppState):
        console.print("[red]Internal error: missing app state[/red]")
        raise typer.Exit(code=1)

    ensure_client_available()
    profile = state.config.get_active_profile()

    if not public and profile.poster_api_key:
        client = build_client(state.base_url)
        response = get_job(client=client, job_id=job_id, authorization=f"Bearer {profile.poster_api_key}")
        if response.status_code == 200 and response.parsed is not None:
            console.print(response.parsed.to_dict() if json_output else response.parsed.to_dict())
            return
        if response.status_code not in {401, 403, 404}:
            console.print(f"[red]Failed to fetch job (status={response.status_code}).[/red]")
            raise typer.Exit(code=2)

    client = build_client(state.base_url)
    response = get_public_job(client=client, job_id=job_id)
    if response.status_code != 200 or response.parsed is None:
        console.print(f"[red]Failed to fetch public job (status={response.status_code}).[/red]")
        raise typer.Exit(code=2)
    console.print(response.parsed.to_dict() if json_output else response.parsed.to_dict())


@app.command("create")
def create_job(
    ctx: typer.Context,
    task_type: str = typer.Option(..., "--task-type", help="Task type"),
    input_file: Path = typer.Option(..., "--input-file", exists=True, dir_okay=False),
    acceptance_file: Path | None = typer.Option(
        None, "--acceptance-file", exists=True, dir_okay=False
    ),
    payout_cents: int | None = typer.Option(None, "--payout-cents", help="Payout in cents"),
    requested_model: str | None = typer.Option(None, "--requested-model", help="Requested model"),
    estimated_tokens: int | None = typer.Option(None, "--estimated-tokens", help="Estimated tokens"),
    deadline_seconds: int | None = typer.Option(None, "--deadline-seconds", help="Deadline seconds"),
    job_ttl_seconds: int | None = typer.Option(None, "--job-ttl-seconds", help="Job TTL seconds"),
    idempotency_key: str | None = typer.Option(None, "--idempotency-key", help="Idempotency key"),
    wait: bool = typer.Option(False, "--wait", help="Retry on 429 with backoff"),
    max_attempts: int = typer.Option(5, "--max-attempts", help="Max attempts when --wait"),
    no_pay: bool = typer.Option(False, "--no-pay", help="Do not attempt x402 payment"),
    proof: str | None = typer.Option(None, "--proof", help="Inline JSON payment proof"),
    proof_file: Path | None = typer.Option(None, "--proof-file", help="Path to JSON proof"),
    json_output: bool = typer.Option(False, "--json", help="Output JSON"),
) -> None:
    state = ctx.obj
    if not isinstance(state, AppState):
        console.print("[red]Internal error: missing app state[/red]")
        raise typer.Exit(code=1)

    ensure_client_available()
    profile = state.config.get_active_profile()
    if not profile.poster_api_key:
        console.print("[red]Poster API key not configured for active profile.[/red]")
        raise typer.Exit(code=2)

    if proof and proof_file:
        console.print("[red]Use only one of --proof or --proof-file.[/red]")
        raise typer.Exit(code=1)

    manual_proof = None
    try:
        if proof_file:
            manual_proof = load_proof_from_file(proof_file)
        elif proof:
            manual_proof = parse_proof_value(proof)
    except ProofError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1) from exc

    payer_type = state.config.payer.type
    if manual_proof is not None:
        payer = ManualPayer(proof=manual_proof)
    elif payer_type == "local_key":
        payer = LocalKeyPayer()
    elif payer_type == "cdp":
        payer = CdpPayer()
    else:
        payer = ManualPayer(proof=None)

    input_payload = _load_json(input_file)
    input_model = PostV1JobsBodyInput.from_dict(input_payload)

    acceptance_model = UNSET
    if acceptance_file:
        acceptance_payload = _load_json(acceptance_file)
        acceptance_model = PostV1JobsBodyAcceptance.from_dict(acceptance_payload)

    body = PostV1JobsBody(
        task_type=task_type,
        input_=input_model,
        acceptance=acceptance_model,
        requested_model=requested_model if requested_model is not None else UNSET,
        estimated_tokens=estimated_tokens if estimated_tokens is not None else UNSET,
        deadline_seconds=deadline_seconds if deadline_seconds is not None else UNSET,
        payout_cents=payout_cents if payout_cents is not None else UNSET,
        job_ttl_seconds=job_ttl_seconds if job_ttl_seconds is not None else UNSET,
    )

    if not idempotency_key:
        idempotency_key = str(uuid.uuid4())
        if not json_output:
            console.print(f"Generated idempotency key: {idempotency_key}")

    client = build_client(state.base_url)

    def request_fn(extra_headers: dict[str, str] | None):
        headers = {
            "authorization": f"Bearer {profile.poster_api_key}",
            "x-idempotency-key": idempotency_key,
            "Content-Type": "application/json",
        }
        if extra_headers:
            headers.update(extra_headers)
        return client.get_httpx_client().request(
            "post",
            "/v1/jobs",
            headers=headers,
            json=body.to_dict(),
        )

    attempts = 0
    while True:
        attempts += 1
        try:
            response = request_with_x402(
                request_fn,
                payer=payer,
                allow_pay=not no_pay,
            )
        except PaymentRequiredError as exc:
            terms = exc.terms
            payload = {
                "recipient": terms.recipient,
                "amount": terms.amount,
                "asset": terms.asset,
                "network": terms.network,
                "payment_context": terms.payment_context,
                "facilitator": terms.facilitator,
                "hint": terms.hint,
            }
            if json_output:
                console.print(payload)
            else:
                console.print("[yellow]Payment required to create job.[/yellow]")
                console.print(payload)
            raise typer.Exit(code=3) from exc
        except PaymentFlowError as exc:
            console.print(f"[red]{exc}[/red]")
            raise typer.Exit(code=3) from exc

        if response.status_code == 201:
            payload = response.json()
            if json_output:
                payload["idempotency_key"] = idempotency_key
                console.print(payload)
            else:
                job = payload.get("job") if isinstance(payload, dict) else None
                if isinstance(job, dict):
                    console.print({"jobId": job.get("id"), "state": job.get("state")})
                else:
                    console.print(payload)
            return

        if response.status_code == 429:
            retry_after = extract_retry_after_seconds(response)
            if not wait or attempts >= max_attempts:
                if json_output:
                    console.print({"error": "rate_limited", "retry_after": retry_after})
                else:
                    if retry_after is not None:
                        console.print(f"Rate limited. Retry after {retry_after}s.")
                    else:
                        console.print("Rate limited.")
                raise typer.Exit(code=4)
            delay_ms = int((retry_after or 1) * 1000)
            sleep_with_jitter(delay_ms)
            continue

        console.print(f"[red]Job create failed (status={response.status_code}).[/red]")
        try:
            console.print(response.json())
        except Exception:
            pass
        raise typer.Exit(code=2)
