from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

import httpx
import typer
from rich.table import Table

from multipl_cli._client.api.jobs.get_v1_jobs import sync_detailed as list_lane_jobs
from multipl_cli._client.api.jobs.get_v_1_jobs_job_id import sync_detailed as get_job
from multipl_cli._client.api.jobs.get_v_1_jobs_job_id_preview import (
    sync_detailed as get_job_preview,
)
from multipl_cli._client.api.jobs.get_v_1_jobs_job_id_stages import (
    sync_detailed as get_job_stages,
)
from multipl_cli._client.api.jobs.post_v_1_jobs_job_id_review import (
    sync_detailed as post_job_review,
)
from multipl_cli._client.api.public.get_v1_public_jobs import sync_detailed as list_public_jobs
from multipl_cli._client.api.public.get_v_1_public_jobs_job_id import (
    sync_detailed as get_public_job,
)
from multipl_cli._client.models.get_v1_jobs_lane import GetV1JobsLane
from multipl_cli._client.models.post_v1_jobs_job_id_review_body import (
    PostV1JobsJobIdReviewBody,
)
from multipl_cli._client.models.post_v1_jobs_job_id_review_body_decision import (
    PostV1JobsJobIdReviewBodyDecision,
)
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

CREATE_JOB_REQUEST_HINT_KEYS = {
    "stages",
    "taskType",
    "payoutCents",
    "deadlineSeconds",
    "jobTtlSeconds",
    "requestedModel",
    "estimatedTokens",
}


def _load_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text())
    except Exception as exc:
        raise typer.BadParameter(f"Invalid JSON file: {exc}") from exc
    if not isinstance(data, dict):
        raise typer.BadParameter("JSON must be an object")
    return data


def _format_preview_blob(value: Any, max_len: int = 4000) -> str:
    if value is None:
        text = "null"
    elif isinstance(value, str):
        text = value
    else:
        try:
            text = json.dumps(value, indent=2, sort_keys=True)
        except TypeError:
            text = str(value)
    if len(text) > max_len:
        return f"{text[:max_len]}... (truncated; use --json or --out)"
    return text


def _parse_response_json(response) -> Any | None:
    try:
        return json.loads(response.content.decode("utf-8"))
    except Exception:
        return None


def _looks_like_create_job_request(payload: dict[str, Any]) -> bool:
    return any(key in payload for key in CREATE_JOB_REQUEST_HINT_KEYS)


def _apply_create_job_overrides(
    request_payload: dict[str, Any],
    *,
    task_type: str | None,
    acceptance_payload: dict[str, Any] | None,
    requested_model: str | None,
    estimated_tokens: int | None,
    deadline_seconds: int | None,
    payout_cents: int | None,
    job_ttl_seconds: int | None,
    json_output: bool,
) -> None:
    if task_type is not None:
        existing_task_type = request_payload.get("taskType")
        if (
            isinstance(existing_task_type, str)
            and existing_task_type.strip()
            and existing_task_type != task_type
            and not json_output
        ):
            console.print("[yellow]Overriding file taskType with --task-type.[/yellow]")
        request_payload["taskType"] = task_type

    if acceptance_payload is not None:
        request_payload["acceptance"] = acceptance_payload
    if requested_model is not None:
        request_payload["requestedModel"] = requested_model
    if estimated_tokens is not None:
        request_payload["estimatedTokens"] = estimated_tokens
    if deadline_seconds is not None:
        request_payload["deadlineSeconds"] = deadline_seconds
    if payout_cents is not None:
        request_payload["payoutCents"] = payout_cents
    if job_ttl_seconds is not None:
        request_payload["jobTtlSeconds"] = job_ttl_seconds


def _review_job(
    state: AppState,
    *,
    job_id: str,
    decision: PostV1JobsJobIdReviewBodyDecision,
    note: str | None,
    json_output: bool,
) -> None:
    ensure_client_available()
    profile = state.config.get_active_profile()
    if not profile.poster_api_key:
        console.print("[red]Poster API key not configured for active profile.[/red]")
        raise typer.Exit(code=2)

    client = build_client(state.base_url)
    body = PostV1JobsJobIdReviewBody(
        decision=decision,
        reason=note if note else UNSET,
    )
    response = post_job_review(
        client=client,
        job_id=job_id,
        authorization=f"Bearer {profile.poster_api_key}",
        body=body,
    )

    if response.status_code == 200:
        payload = response.parsed.to_dict() if response.parsed is not None else (_parse_response_json(response) or {})
        if json_output:
            console.print(payload)
            return

        job = payload.get("job") if isinstance(payload, dict) else None
        action = "accepted" if decision == PostV1JobsJobIdReviewBodyDecision.ACCEPT else "rejected"
        if isinstance(job, dict):
            state_value = job.get("state")
            if state_value is not None:
                console.print(f"Job {action}: {job.get('id', job_id)} (state={state_value})")
            else:
                console.print(f"Job {action}: {job.get('id', job_id)}")
        else:
            console.print(f"Job {action}: {job_id}")
        return

    if response.status_code in {401, 403}:
        console.print("[red]Poster key required or invalid key.[/red]")
        body_payload = _parse_response_json(response)
        if body_payload is not None:
            console.print(body_payload)
        raise typer.Exit(code=2)

    if response.status_code == 404:
        console.print("[red]Job not found.[/red]")
        raise typer.Exit(code=1)

    if response.status_code == 429:
        retry_after = extract_retry_after_seconds(
            httpx.Response(
                status_code=int(response.status_code),
                headers=response.headers,
                content=response.content,
            )
        )
        if retry_after is not None:
            console.print(f"Rate limited. Retry after {retry_after}s.")
        else:
            console.print("Rate limited.")
        raise typer.Exit(code=4)

    if response.status_code in {409, 422}:
        console.print(f"[red]Review failed (status={response.status_code}).[/red]")
        body_payload = _parse_response_json(response)
        if body_payload is not None:
            console.print(body_payload)
        raise typer.Exit(code=1)

    console.print(f"[red]Review failed (status={response.status_code}).[/red]")
    body_payload = _parse_response_json(response)
    if body_payload is not None:
        console.print(body_payload)
    raise typer.Exit(code=2)


@app.command("list")
def list_jobs(
    ctx: typer.Context,
    task_type: str | None = typer.Option(None, "--task-type", help="Filter by task type"),
    status: str | None = typer.Option(None, "--status", help="Filter by status"),
    lane: str | None = typer.Option(
        None,
        "--lane",
        help="Optional lane filter (supported value from API: verifier)",
    ),
    limit: int = typer.Option(50, "--limit", help="Max jobs to return"),
    json_output: bool = typer.Option(False, "--json", help="Output JSON"),
) -> None:
    state = ctx.obj
    if not isinstance(state, AppState):
        console.print("[red]Internal error: missing app state[/red]")
        raise typer.Exit(code=1)

    ensure_client_available()
    client = build_client(state.base_url)

    lane_enum: GetV1JobsLane | None = None
    if lane is not None:
        try:
            lane_enum = GetV1JobsLane(lane)
        except ValueError as exc:
            allowed = ", ".join(item.value for item in GetV1JobsLane)
            console.print(f"[red]Invalid lane '{lane}'. Allowed values: {allowed}.[/red]")
            raise typer.Exit(code=1) from exc

    if lane_enum is not None:
        if task_type or status:
            console.print(
                "[yellow]--task-type/--status are ignored when --lane is provided.[/yellow]"
            )
        response = list_lane_jobs(
            client=client,
            lane=lane_enum,
            limit=limit,
        )
    else:
        response = list_public_jobs(
            client=client,
            state=status or UNSET,
            task_type=task_type or UNSET,
            limit=limit,
        )

    if response.status_code == 429:
        retry_after = extract_retry_after_seconds(
            httpx.Response(
                status_code=int(response.status_code),
                headers=response.headers,
                content=response.content,
            )
        )
        if retry_after is not None:
            console.print(f"Rate limited. Retry after {retry_after}s.")
        else:
            console.print("Rate limited.")
        raise typer.Exit(code=4)

    if response.status_code != 200:
        console.print(f"[red]Failed to list jobs (status={response.status_code}).[/red]")
        body = _parse_response_json(response)
        if body is not None:
            console.print(body)
        raise typer.Exit(code=2)

    payload = _parse_response_json(response)
    if payload is None and response.parsed is not None:
        payload = response.parsed.to_dict()
    if not isinstance(payload, dict):
        console.print("[red]Invalid jobs response payload.[/red]")
        raise typer.Exit(code=2)

    if json_output:
        console.print(payload)
        return

    jobs = payload.get("jobs")
    if not isinstance(jobs, list):
        console.print("[red]Invalid jobs response payload.[/red]")
        raise typer.Exit(code=2)

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
        if not isinstance(job, dict):
            continue
        table.add_row(
            str(job.get("id", "-")),
            str(job.get("taskType", "-")),
            str(job.get("state", "-")),
            str(job.get("payoutCents")) if job.get("payoutCents") is not None else "-",
            str(job.get("createdAt", "-")),
            str(job.get("claimedAt") or "-"),
            str(job.get("submittedAt") or "-"),
            str(job.get("completedAt") or "-"),
        )

    console.print(table)
    next_cursor = payload.get("nextCursor")
    if next_cursor:
        console.print(f"Next cursor: {next_cursor}")


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


@app.command("preview")
def preview_job(
    ctx: typer.Context,
    job_id: str = typer.Argument(..., help="Job ID"),
    out: Path | None = typer.Option(None, "--out", help="Write preview JSON to file"),
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

    client = build_client(state.base_url)
    response = get_job_preview(
        client=client, job_id=job_id, authorization=f"Bearer {profile.poster_api_key}"
    )

    if response.status_code == 200:
        if response.parsed is not None:
            payload = response.parsed.to_dict()
        else:
            payload = _parse_response_json(response) or {}

        if out:
            try:
                out.write_text(json.dumps(payload, indent=2, sort_keys=True))
            except Exception as exc:
                console.print(f"[red]Failed to write preview: {exc}[/red]")
                raise typer.Exit(code=1) from exc

        if json_output:
            console.print(payload)
            return

        if out:
            console.print(f"[green]Wrote preview to {out}[/green]")

        if not isinstance(payload, dict):
            console.print(payload)
            return

        table = Table(title="Job Preview")
        table.add_column("Field")
        table.add_column("Value")

        if "commitmentSha256" in payload:
            table.add_row("commitmentSha256", str(payload.get("commitmentSha256")))
        if "previewJson" in payload:
            table.add_row("previewJson", _format_preview_blob(payload.get("previewJson")))
        if "acceptanceReport" in payload:
            table.add_row(
                "acceptanceReport",
                _format_preview_blob(payload.get("acceptanceReport")),
            )
        if "blocked" in payload:
            table.add_row("blocked", str(payload.get("blocked")))
        if "reason" in payload:
            table.add_row("reason", str(payload.get("reason")))

        console.print(table)
        return

    if response.status_code in {401, 403}:
        console.print("[red]Unauthorized (poster key missing/invalid).[/red]")
        body = _parse_response_json(response)
        if body is not None:
            console.print(body)
        raise typer.Exit(code=2)

    if response.status_code == 404:
        console.print("[red]Job not found or not accessible.[/red]")
        raise typer.Exit(code=2)

    if response.status_code == 429:
        retry_after = extract_retry_after_seconds(
            httpx.Response(
                status_code=int(response.status_code),
                headers=response.headers,
                content=response.content,
            )
        )
        if retry_after is not None:
            console.print(f"Rate limited. Retry after {retry_after}s.")
        else:
            console.print("Rate limited.")
        raise typer.Exit(code=4)

    if response.status_code in {409, 410, 422}:
        console.print(
            f"[red]Preview unavailable (status={response.status_code}).[/red]"
        )
        body = _parse_response_json(response)
        if body is not None:
            console.print(body)
        raise typer.Exit(code=1)

    console.print(f"[red]Failed to fetch preview (status={response.status_code}).[/red]")
    body = _parse_response_json(response)
    if body is not None:
        console.print(body)
    raise typer.Exit(code=2)


@app.command("stages")
def get_job_stages_cmd(
    ctx: typer.Context,
    job_id: str = typer.Argument(..., help="Job ID"),
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

    client = build_client(state.base_url)
    response = get_job_stages(
        client=client,
        job_id=job_id,
        authorization=f"Bearer {profile.poster_api_key}",
    )

    if response.status_code == 200:
        payload = response.parsed.to_dict() if response.parsed is not None else (_parse_response_json(response) or {})
        if json_output:
            console.print(payload)
            return

        if not isinstance(payload, dict):
            console.print("[red]Invalid stages response payload.[/red]")
            raise typer.Exit(code=2)
        stages = payload.get("stages")
        if not isinstance(stages, list):
            console.print("[red]Invalid stages response payload.[/red]")
            raise typer.Exit(code=2)

        console.print(f"rootJobId: {payload.get('rootJobId')}")
        table = Table(title=f"Stages for {job_id}")
        table.add_column("#")
        table.add_column("Stage")
        table.add_column("State")
        table.add_column("Visibility")
        table.add_column("Assignment")
        table.add_column("Job ID")
        table.add_column("Reserved Worker")

        for stage in stages:
            if not isinstance(stage, dict):
                continue
            table.add_row(
                str(stage.get("stageIndex", "-")),
                str(stage.get("stageId", "-")),
                str(stage.get("state", "-")),
                str(stage.get("visibility", "-")),
                str(stage.get("assignmentMode") or "-"),
                str(stage.get("jobId") or "-"),
                str(stage.get("reservedWorkerId") or "-"),
            )
        console.print(table)
        return

    if response.status_code in {401, 403}:
        console.print("[red]Unauthorized (poster key missing/invalid).[/red]")
        body = _parse_response_json(response)
        if body is not None:
            console.print(body)
        raise typer.Exit(code=2)

    if response.status_code == 404:
        console.print("[red]Job not found or not accessible.[/red]")
        raise typer.Exit(code=2)

    if response.status_code == 429:
        retry_after = extract_retry_after_seconds(
            httpx.Response(
                status_code=int(response.status_code),
                headers=response.headers,
                content=response.content,
            )
        )
        if retry_after is not None:
            console.print(f"Rate limited. Retry after {retry_after}s.")
        else:
            console.print("Rate limited.")
        raise typer.Exit(code=4)

    console.print(f"[red]Failed to fetch stages (status={response.status_code}).[/red]")
    body = _parse_response_json(response)
    if body is not None:
        console.print(body)
    raise typer.Exit(code=2)


@app.command("create")
def create_job(
    ctx: typer.Context,
    task_type: str | None = typer.Option(None, "--task-type", help="Task type override"),
    input_file: Path = typer.Option(
        ...,
        "--input-file",
        exists=True,
        dir_okay=False,
        help="Legacy input JSON or full create request JSON",
    ),
    request_file: bool = typer.Option(
        False,
        "--request-file",
        "--raw",
        help="Treat --input-file as full POST /v1/jobs request JSON",
    ),
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
    acceptance_payload = _load_json(acceptance_file) if acceptance_file else None

    full_request_mode = request_file or _looks_like_create_job_request(input_payload)
    if full_request_mode:
        request_payload = dict(input_payload)
        if "stages" in input_payload and not request_file and not json_output:
            console.print(
                "[yellow]Detected top-level stages in --input-file; sending full create request.[/yellow]"
            )
    else:
        if task_type is None:
            console.print(
                "[red]--task-type is required when --input-file is legacy input-only JSON.[/red]"
            )
            raise typer.Exit(code=1)
        request_payload = {
            "taskType": task_type,
            "input": input_payload,
        }

    _apply_create_job_overrides(
        request_payload,
        task_type=task_type,
        acceptance_payload=acceptance_payload,
        requested_model=requested_model,
        estimated_tokens=estimated_tokens,
        deadline_seconds=deadline_seconds,
        payout_cents=payout_cents,
        job_ttl_seconds=job_ttl_seconds,
        json_output=json_output,
    )

    task_type_in_payload = request_payload.get("taskType")
    if not isinstance(task_type_in_payload, str) or not task_type_in_payload.strip():
        console.print("[red]Create request must include taskType (file or --task-type).[/red]")
        raise typer.Exit(code=1)

    input_in_payload = request_payload.get("input")
    if not isinstance(input_in_payload, dict):
        console.print("[red]Create request must include an object input payload.[/red]")
        raise typer.Exit(code=1)

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
            json=request_payload,
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


@app.command("accept")
def accept_job(
    ctx: typer.Context,
    job_id: str = typer.Argument(..., help="Job ID"),
    note: str | None = typer.Option(None, "--note", help="Optional review note"),
    json_output: bool = typer.Option(False, "--json", help="Output JSON"),
) -> None:
    state = ctx.obj
    if not isinstance(state, AppState):
        console.print("[red]Internal error: missing app state[/red]")
        raise typer.Exit(code=1)
    _review_job(
        state,
        job_id=job_id,
        decision=PostV1JobsJobIdReviewBodyDecision.ACCEPT,
        note=note,
        json_output=json_output,
    )


@app.command("reject")
def reject_job(
    ctx: typer.Context,
    job_id: str = typer.Argument(..., help="Job ID"),
    note: str | None = typer.Option(None, "--note", help="Optional review note"),
    json_output: bool = typer.Option(False, "--json", help="Output JSON"),
) -> None:
    state = ctx.obj
    if not isinstance(state, AppState):
        console.print("[red]Internal error: missing app state[/red]")
        raise typer.Exit(code=1)
    _review_job(
        state,
        job_id=job_id,
        decision=PostV1JobsJobIdReviewBodyDecision.REJECT,
        note=note,
        json_output=json_output,
    )
