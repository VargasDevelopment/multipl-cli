from __future__ import annotations

import hashlib
import json
import signal
import time
from contextlib import nullcontext
from dataclasses import dataclass
from types import FrameType
from urllib.parse import urlparse

import httpx
import typer
from rich.table import Table

from multipl_cli._client.api.training.post_v1_training_lease import (
    sync_detailed as training_lease,
)
from multipl_cli._client.models.post_v1_training_lease_body import PostV1TrainingLeaseBody
from multipl_cli._client.models.post_v1_claims_acquire_response_200 import (
    PostV1ClaimsAcquireResponse200,
)
from multipl_cli._client.models.post_v1_claims_claim_id_release_response_200 import (
    PostV1ClaimsClaimIdReleaseResponse200,
)
from multipl_cli._client.types import UNSET
from multipl_cli.app_state import AppState
from multipl_cli.config import ClaimsCache, resolve_worker_api_key
from multipl_cli.console import console
from multipl_cli.openapi_client import build_client, ensure_client_available
from multipl_cli.polling import (
    extract_request_id,
    extract_retry_after_seconds,
    maybe_extract_kind,
    parse_response_json,
    poll_with_backoff,
)
from multipl_cli.polling_lock import LockHeldError, acquire_loop_lock

app = typer.Typer(no_args_is_help=True)


def _parse_json_body(response) -> dict:
    try:
        return response.json()
    except Exception:
        try:
            return json.loads(response.content.decode("utf-8"))
        except Exception:
            return {}


def _preview_json(value: object, *, max_len: int = 280) -> str:
    try:
        rendered = json.dumps(value, separators=(",", ":"), sort_keys=True)
    except Exception:
        rendered = str(value)
    if len(rendered) <= max_len:
        return rendered
    return f"{rendered[:max_len]}... (truncated)"


def _print_claim(claim: PostV1ClaimsAcquireResponse200) -> None:
    table = Table(title="Claim Acquired")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("claim.id", claim.claim.id)
    table.add_row("claim.status", claim.claim.status.value)
    table.add_row("job.id", claim.job.id)
    table.add_row("taskType", claim.job.task_type)
    table.add_row("job.state", claim.job.state.value)
    table.add_row(
        "payoutCents",
        str(claim.job.payout_cents) if claim.job.payout_cents is not None else "-",
    )
    table.add_row(
        "deadlineSeconds",
        str(claim.job.deadline_seconds) if claim.job.deadline_seconds is not None else "-",
    )
    table.add_row(
        "requestedModel",
        claim.job.requested_model if claim.job.requested_model is not None else "-",
    )
    table.add_row(
        "estimatedTokens",
        str(claim.job.estimated_tokens) if claim.job.estimated_tokens is not None else "-",
    )
    table.add_row("leaseExpiresAt", claim.claim.lease_expires_at)
    table.add_row("job.expiresAt", claim.job.expires_at)
    table.add_row("input", _preview_json(claim.job.input_.to_dict()))
    console.print(table)


def _stderr(message: str) -> None:
    typer.echo(message, err=True)


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


def _short_base_url(base_url: str) -> str:
    parsed = urlparse(base_url)
    if parsed.netloc:
        return parsed.netloc
    return base_url


def _worker_identity(worker_api_key: str) -> str:
    digest = hashlib.sha256(worker_api_key.encode("utf-8")).hexdigest()[:12]
    return f"worker:{digest}"


def _lock_conflict_message(error: LockHeldError) -> str:
    pid = error.existing_payload.get("pid")
    started_at = error.existing_payload.get("startedAt")
    pid_msg = f" pid={pid}" if pid is not None else ""
    start_msg = f" startedAt={started_at}" if started_at else ""
    return (
        "Another `multipl claim acquire` wait/drain loop is already running for this "
        f"worker/task/baseUrl.{pid_msg}{start_msg} Use `--force` to steal the lock."
    )


@dataclass
class _HeartbeatReporter:
    interval_seconds: int = 30
    _last_emit: float = 0.0

    def maybe_emit(self, *, task_type: str, base_url: str, next_delay_seconds: float) -> None:
        now = time.monotonic()
        if self._last_emit > 0 and (now - self._last_emit) < self.interval_seconds:
            return
        self._last_emit = now
        _stderr(
            "Still waiting for a claim "
            f"(taskType={task_type}, base={_short_base_url(base_url)}). "
            f"Next poll in {max(next_delay_seconds, 0):.1f}s."
        )


def _install_lock_signal_handlers(lock) -> tuple[dict[int, signal.Handlers], list[int]]:
    previous_handlers: dict[int, signal.Handlers] = {}
    tracked_signals = [signal.SIGINT]
    if hasattr(signal, "SIGTERM"):
        tracked_signals.append(signal.SIGTERM)

    def _handler(signum: int, _frame: FrameType | None) -> None:
        lock.release()
        previous = previous_handlers.get(signum)
        if callable(previous):
            previous(signum, _frame)
            return
        raise KeyboardInterrupt()

    for sig in tracked_signals:
        previous_handlers[sig] = signal.getsignal(sig)
        signal.signal(sig, _handler)

    return previous_handlers, tracked_signals


def _restore_signal_handlers(previous_handlers: dict[int, signal.Handlers], tracked_signals: list[int]) -> None:
    for sig in tracked_signals:
        signal.signal(sig, previous_handlers[sig])


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
    force: bool = typer.Option(
        False,
        "--force",
        help="Steal polling lock if another acquire wait/drain loop is running",
    ),
    debug_polling: bool = typer.Option(
        False,
        "--debug-polling",
        help="Print polling status/debug details to stderr",
    ),
    json_output: bool = typer.Option(False, "--json", help="Output JSON"),
) -> None:
    state = ctx.obj
    if not isinstance(state, AppState):
        console.print("[red]Internal error: missing app state[/red]")
        raise typer.Exit(code=1)

    ensure_client_available()
    mode = mode.lower()
    if mode not in {"single", "wait", "drain"}:
        console.print("[red]Invalid mode. Use single, wait, or drain.[/red]")
        raise typer.Exit(code=1)

    profile = state.config.get_active_profile()
    worker_api_key = resolve_worker_api_key(profile)
    if state.training_mode:
        if mode != "single":
            console.print("[red]Training acquire only supports --mode single.[/red]")
            raise typer.Exit(code=1)
        if task_type and job_id:
            console.print("[red]Provide only one of --task-type or --job in training mode.[/red]")
            raise typer.Exit(code=1)
        client = build_client(state.base_url)
        lease_body = PostV1TrainingLeaseBody(
            task_type=task_type if task_type else UNSET,
            exercise_id=job_id if job_id else UNSET,
        )
        try:
            response = training_lease(
                client=client,
                body=lease_body,
            )
        except httpx.HTTPError as exc:
            console.print(f"[red]Network error: {exc}[/red]")
            raise typer.Exit(code=2) from exc
        if int(response.status_code) != 200:
            payload = _parse_json_body(response)
            if json_output:
                console.print(payload)
            else:
                console.print(
                    f"[red]Training lease failed (status={response.status_code}).[/red] {payload or ''}"
                )
            raise typer.Exit(code=1 if response.status_code in {400, 409, 422} else 2)

        if response.parsed is None:
            console.print("[red]Invalid training lease response payload.[/red]")
            raise typer.Exit(code=2)

        payload = response.parsed.to_dict()
        lease = response.parsed.lease
        exercise = response.parsed.exercise

        lease_id = lease.lease_id
        exercise_id = exercise.id
        submit_token = lease.submit_token

        cache = ClaimsCache.load()
        cache.set_claim(state.profile_name, exercise_id, f"{lease_id}:{submit_token}")
        cache.save()

        if json_output:
            console.print(payload)
            return

        table = Table(title="Training Lease Acquired")
        table.add_column("Field")
        table.add_column("Value")
        table.add_row("lease.id", lease_id)
        table.add_row("exercise.id", exercise_id)
        table.add_row("exercise.title", exercise.title)
        table.add_row("taskType", exercise.task_type)
        table.add_row("expiresAt", lease.expires_at.isoformat())
        table.add_row("submitToken", submit_token)
        table.add_row("prompt", exercise.prompt)
        table.add_row("input", _preview_json(exercise.input_.to_dict()))
        table.add_row(
            "acceptanceContract",
            _preview_json(exercise.acceptance_contract.to_dict()),
        )
        console.print(table)
        return

    if not worker_api_key:
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
                "authorization": f"Bearer {worker_api_key}",
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

    heartbeat = _HeartbeatReporter()

    def handle_empty(_response):
        if mode == "drain" and saw_success and not json_output:
            console.print("No jobs available. Drain complete.")

    def handle_rate_limited(response, retry_after: int, source: str):
        payload = parse_response_json(response)
        kind = maybe_extract_kind(payload) or "rate limited"
        _stderr(
            "429 received: "
            f"reason={kind}, retry-after={retry_after}s. Sleeping and will retry."
        )
        if retry_after >= 60:
            _stderr(
                "Hint: long retry-after may indicate cooldown/penalty state "
                "or multiple worker loops running."
            )
        if debug_polling:
            request_id = extract_request_id(response.headers) or "-"
            _stderr(
                "[debug-polling] "
                f"status=429 wait={retry_after}s source={source} request_id={request_id}"
            )

    def handle_transient_error(error):
        if mode == "single":
            return
        if isinstance(error, Exception):
            status = "exception"
            request_id = "-"
        else:
            status = str(error.status_code)
            request_id = extract_request_id(error.headers) or "-"
        _stderr("Transient error. Sleeping with backoff and retrying.")
        if debug_polling:
            _stderr(
                "[debug-polling] "
                f"status={status} wait=backoff source=backoff request_id={request_id}"
            )

    def handle_sleep(seconds: float, reason: str, response, source: str) -> None:
        if mode not in {"wait", "drain"}:
            return
        if debug_polling:
            status = str(response.status_code) if response is not None else "exception"
            request_id = extract_request_id(response.headers) if response is not None else None
            _stderr(
                "[debug-polling] "
                f"status={status} wait={max(seconds, 0):.1f}s source={source} request_id={request_id or '-'}"
            )
        if reason != "rate_limited" and task_type:
            heartbeat.maybe_emit(
                task_type=task_type,
                base_url=state.base_url,
                next_delay_seconds=seconds,
            )

    def handle_non_retryable(response):
        payload = _parse_json_body(response)
        message = f"Acquire failed (status={response.status_code}). {payload or ''}".strip()
        if mode in {"wait", "drain"}:
            _stderr(message)
        else:
            console.print(f"[red]Acquire failed (status={response.status_code}).[/red] {payload or ''}")
        if response.status_code in {400, 409, 422}:
            raise typer.Exit(code=1)
        raise typer.Exit(code=2)

    if bool(task_type) == bool(job_id):
        console.print("[red]Provide exactly one of --task-type or --job.[/red]")
        raise typer.Exit(code=1)
    if job_id and mode != "single":
        console.print("[red]--job only supports --mode single.[/red]")
        raise typer.Exit(code=1)
    if force and mode == "single":
        console.print("[red]--force is only supported for --mode wait or --mode drain.[/red]")
        raise typer.Exit(code=1)

    if mode == "single":
        try:
            response = request_once()
        except httpx.HTTPError as exc:
            console.print(f"[red]Network error: {exc}[/red]")
            raise typer.Exit(code=2) from exc
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

    lock = None
    previous_handlers: dict[int, signal.Handlers] = {}
    tracked_signals: list[int] = []
    try:
        lock = acquire_loop_lock(
            base_url=state.base_url,
            worker_identity=_worker_identity(worker_api_key),
            task_type=task_type or "unknown",
            force=force,
        )
    except LockHeldError as exc:
        _stderr(_lock_conflict_message(exc))
        raise typer.Exit(code=3) from exc

    cleanup_context = lock if lock is not None else nullcontext()
    with cleanup_context:
        previous_handlers, tracked_signals = _install_lock_signal_handlers(lock)
        try:
            poll_with_backoff(
                request_fn=request_once,
                mode=mode,
                empty_statuses=[204],
                handle_success=handle_success,
                handle_empty=handle_empty,
                handle_rate_limited=handle_rate_limited,
                handle_transient_error=handle_transient_error,
                handle_non_retryable=handle_non_retryable,
                handle_sleep=handle_sleep,
            )
        finally:
            _restore_signal_handlers(previous_handlers, tracked_signals)


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
    worker_api_key = resolve_worker_api_key(profile)
    if not worker_api_key:
        console.print("[red]Worker API key not configured for active profile.[/red]")
        raise typer.Exit(code=2)

    client = build_client(state.base_url)
    try:
        response = client.get_httpx_client().request(
            "post",
            f"/v1/claims/{claim_id}/release",
            headers={"authorization": f"Bearer {worker_api_key}"},
        )
    except httpx.HTTPError as exc:
        console.print(f"[red]Network error: {exc}[/red]")
        raise typer.Exit(code=2) from exc

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
