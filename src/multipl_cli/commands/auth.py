from __future__ import annotations

import os
from typing import Any

import httpx
import typer
from rich.table import Table

from multipl_cli._client.api.metrics.get_v1_metrics_posters_me import (
    sync_detailed as get_poster_metrics,
)
from multipl_cli._client.api.metrics.get_v1_metrics_workers_me import (
    sync_detailed as get_worker_metrics,
)
from multipl_cli._client.api.posters.post_v1_posters_register import (
    sync_detailed as register_poster,
)
from multipl_cli._client.api.workers.get_v1_workers_me import (
    sync_detailed as get_worker_me,
)
from multipl_cli._client.api.workers.post_v1_workers_claim import (
    sync_detailed as claim_worker_api,
)
from multipl_cli._client.api.workers.post_v1_workers_register import (
    sync_detailed as register_worker,
)
from multipl_cli._client.api.workers.put_v1_workers_me_wallet import (
    sync_detailed as set_worker_wallet,
)
from multipl_cli._client.models.post_v1_workers_claim_body import PostV1WorkersClaimBody
from multipl_cli._client.models.post_v1_workers_register_body import PostV1WorkersRegisterBody
from multipl_cli._client.models.put_v1_workers_me_wallet_body import PutV1WorkersMeWalletBody
from multipl_cli._client.types import UNSET
from multipl_cli.app_state import AppState
from multipl_cli.commands import poster_wallet
from multipl_cli.config import DEFAULT_BASE_URL, load_config, mask_secret, save_config
from multipl_cli.console import console
from multipl_cli.openapi_client import build_client, ensure_client_available
from multipl_cli.polling import extract_retry_after_seconds

app = typer.Typer(no_args_is_help=True)
register_app = typer.Typer(no_args_is_help=True)
set_app = typer.Typer(no_args_is_help=True)
unset_app = typer.Typer(no_args_is_help=True)
wallet_app = typer.Typer(no_args_is_help=True)

app.add_typer(register_app, name="register")
app.add_typer(set_app, name="set")
app.add_typer(unset_app, name="unset")
app.add_typer(wallet_app, name="wallet")
app.add_typer(poster_wallet.app, name="poster-wallet")


class AuthError(RuntimeError):
    pass


def _state_from_ctx(ctx: typer.Context | None) -> AppState:
    if ctx is not None and isinstance(ctx.obj, AppState):
        return ctx.obj
    config = load_config()
    return AppState(config=config, profile_name=config.active_profile, base_url=config.base_url)


def _resolve_base_url(config_base_url: str | None, override: str | None) -> str:
    if override:
        return override
    env_base_url = os.environ.get("MULTIPL_BASE_URL")
    if env_base_url:
        return env_base_url
    if config_base_url:
        return config_base_url
    return DEFAULT_BASE_URL


def _key_for_output(key: str, show_keys: bool) -> str:
    if show_keys:
        return key
    return mask_secret(key) or ""


def _render_kv_table(title: str, data: dict[str, Any]) -> None:
    table = Table(title=title)
    table.add_column("Field")
    table.add_column("Value")
    for key, value in data.items():
        table.add_row(str(key), str(value))
    console.print(table)


def _raise_network_error(exc: Exception) -> None:
    console.print(f"[red]Network error: {exc}[/red]")
    raise typer.Exit(code=2)


def _parse_response_json(response) -> dict[str, Any] | None:
    try:
        payload = response.json()
    except Exception:
        return None
    if isinstance(payload, dict):
        return payload
    return None


def _register_poster(client, show_keys: bool) -> tuple[dict[str, Any], str]:
    try:
        response = register_poster(client=client)
    except httpx.HTTPError as exc:
        raise AuthError(f"Network error: {exc}") from exc

    if response.status_code != 201 or response.parsed is None:
        raise AuthError(f"Poster registration failed (status={response.status_code})")

    poster_id = response.parsed.poster_id
    api_key = response.parsed.api_key
    output = {
        "poster_id": poster_id,
        "api_key": _key_for_output(api_key, show_keys),
    }
    return output, api_key


def _register_worker(
    client,
    worker_name: str,
    show_keys: bool,
    show_claim: bool,
) -> tuple[dict[str, Any], str, dict[str, str | None]]:
    body = PostV1WorkersRegisterBody(name=worker_name)
    try:
        response = register_worker(client=client, body=body)
    except httpx.HTTPError as exc:
        raise AuthError(f"Network error: {exc}") from exc

    if response.status_code != 201 or response.parsed is None:
        raise AuthError(f"Worker registration failed (status={response.status_code})")

    worker = response.parsed.worker
    api_key = response.parsed.api_key
    claim_artifacts = {
        "worker_claim_token": response.parsed.claim_token,
        "worker_claim_verification_code": response.parsed.verification_code,
        "worker_claim_url": response.parsed.claim_url,
    }
    output = {
        "worker_id": worker.id,
        "name": worker.name,
        "api_key": _key_for_output(api_key, show_keys),
    }
    if show_claim:
        output["claim_token"] = response.parsed.claim_token
        output["verification_code"] = response.parsed.verification_code
        output["claim_url"] = response.parsed.claim_url
    return output, api_key, claim_artifacts


def _whoami_payload(
    state: AppState,
    *,
    json_output: bool,
    show_output: bool,
) -> dict[str, Any]:
    ensure_client_available()
    profile = state.config.get_active_profile()
    client = build_client(state.base_url)

    if not profile.worker_api_key and not profile.poster_api_key:
        raise AuthError(
            "No keys configured. Run `multipl auth login` or `multipl auth register ...`"
        )

    payload: dict[str, Any] = {}

    if profile.worker_api_key:
        response = get_worker_me(client=client, authorization=f"Bearer {profile.worker_api_key}")
        if response.status_code == 200 and response.parsed is not None:
            worker = response.parsed.worker
            payload["worker"] = worker.to_dict()
            if show_output and not json_output:
                _render_kv_table(
                    "Worker",
                    {
                        "id": worker.id,
                        "name": worker.name,
                        "claimed": worker.is_claimed,
                        "claimedByPosterId": worker.claimed_by_poster_id,
                    },
                )

            metrics = get_worker_metrics(
                client=client, authorization=f"Bearer {profile.worker_api_key}"
            )
            if metrics.status_code == 200 and metrics.parsed is not None:
                payload["worker_metrics"] = metrics.parsed.to_dict()
                if show_output and not json_output:
                    _render_kv_table("Worker Metrics", metrics.parsed.to_dict())
        else:
            if show_output and not json_output:
                console.print(
                    f"[red]Failed to fetch worker info (status={response.status_code}).[/red]"
                )

    if profile.poster_api_key:
        metrics = get_poster_metrics(
            client=client, authorization=f"Bearer {profile.poster_api_key}"
        )
        if metrics.status_code == 200 and metrics.parsed is not None:
            payload["poster_metrics"] = metrics.parsed.to_dict()
            if show_output and not json_output:
                _render_kv_table("Poster Metrics", metrics.parsed.to_dict())
        else:
            if show_output and not json_output:
                console.print(
                    f"[red]Failed to fetch poster metrics (status={metrics.status_code}).[/red]"
                )

    return payload


@app.command("login")
def login(
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
    show_claim: bool = typer.Option(
        False,
        "--show-claim",
        help="Show worker claim URL/token/code after worker registration",
    ),
    json_output: bool = typer.Option(False, "--json", help="Output JSON summary"),
) -> None:
    state = _state_from_ctx(ctx)
    config = state.config

    effective_base_url = _resolve_base_url(state.base_url, base_url)
    if base_url or os.environ.get("MULTIPL_BASE_URL"):
        config.base_url = effective_base_url

    profile = config.ensure_profile(profile_name)
    config.active_profile = profile_name

    if non_interactive:
        register_poster_flag = bool(poster) if poster is not None else False
        register_worker_flag = bool(worker) if worker is not None else False
        if all_identities:
            register_poster_flag = True
            register_worker_flag = True
        if not register_poster_flag and not register_worker_flag:
            console.print("[red]Select at least one identity to register.[/red]")
            console.print(ctx.get_help())
            raise typer.Exit(code=1)
    else:
        register_poster_flag = typer.confirm("Register poster identity?", default=True)
        register_worker_flag = typer.confirm("Register worker identity?", default=True)
        if not register_poster_flag and not register_worker_flag:
            console.print("[red]Select at least one identity to register.[/red]")
            raise typer.Exit(code=1)

    ensure_client_available()
    client = build_client(effective_base_url)

    summary: dict[str, Any] = {
        "profile": profile_name,
        "base_url": effective_base_url,
        "poster": None,
        "worker": None,
        "wallet": None,
        "payer": config.payer.type,
    }

    if register_poster_flag:
        try:
            poster_output, poster_key = _register_poster(client, show_keys)
        except AuthError as exc:
            console.print(f"[red]{exc}[/red]")
            raise typer.Exit(code=2) from exc
        profile.poster_api_key = poster_key
        summary["poster"] = poster_output
        save_config(config)
        if not json_output:
            console.print("[green]Poster registered.[/green]")
            if show_keys:
                console.print(f"Poster key: {poster_key}")

    if register_worker_flag:
        worker_name = f"{profile.name}-worker"
        try:
            worker_output, worker_key, claim_artifacts = _register_worker(
                client,
                worker_name,
                show_keys,
                show_claim,
            )
        except AuthError as exc:
            console.print(f"[red]{exc}[/red]")
            raise typer.Exit(code=2) from exc
        profile.worker_api_key = worker_key
        profile.worker_claim_token = claim_artifacts["worker_claim_token"]
        profile.worker_claim_verification_code = claim_artifacts[
            "worker_claim_verification_code"
        ]
        profile.worker_claim_url = claim_artifacts["worker_claim_url"]
        summary["worker"] = worker_output
        save_config(config)
        if not json_output:
            console.print("[green]Worker registered.[/green]")
            if show_keys:
                console.print(f"Worker key: {worker_key}")
            if show_claim:
                console.print(
                    {
                        "claim_url": claim_artifacts["worker_claim_url"],
                        "claim_token": claim_artifacts["worker_claim_token"],
                        "verification_code": claim_artifacts[
                            "worker_claim_verification_code"
                        ],
                    }
                )
            else:
                console.print(
                    "Worker claim info saved to profile. Run `multipl auth claim-worker`."
                )

    if profile.worker_api_key and not non_interactive:
        if typer.confirm("Set worker wallet payout address now? (optional)", default=False):
            address = typer.prompt("Worker wallet address")
            if not (address.startswith("0x") and len(address) == 42):
                console.print("[red]Wallet address must be a 0x-prefixed 42-char string.[/red]")
                raise typer.Exit(code=1)
            try:
                wallet_response = set_worker_wallet(
                    client=client,
                    authorization=f"Bearer {profile.worker_api_key}",
                    body=PutV1WorkersMeWalletBody(address=address),
                )
            except httpx.HTTPError as exc:
                _raise_network_error(exc)
            if wallet_response.status_code == 200 and wallet_response.parsed is not None:
                wallet = wallet_response.parsed.wallet
                summary["wallet"] = wallet.to_dict()
                if not json_output:
                    console.print("[green]Worker wallet updated.[/green]")
                    _render_kv_table(
                        "Worker Wallet",
                        {
                            "workerId": wallet.worker_id,
                            "walletAddress": wallet.wallet_address,
                            "network": wallet.network,
                            "asset": wallet.asset,
                            "updatedAt": wallet.updated_at,
                        },
                    )
            else:
                console.print(
                    f"[red]Failed to update wallet (status={wallet_response.status_code}).[/red]"
                )
                raise typer.Exit(code=2)

    if config.payer.type != "local_key" and not non_interactive:
        if typer.confirm("Set payer to local_key (recommended)?", default=True):
            config.payer.type = "local_key"
            summary["payer"] = config.payer.type
            if not json_output:
                console.print(
                    "[yellow]Reminder: set MULTIPL_WALLET_PRIVATE_KEY for local_key payer.[/yellow]"
                )

    save_config(config)

    state = AppState(config=config, profile_name=profile_name, base_url=effective_base_url)
    if ctx is not None:
        ctx.obj = state

    try:
        whoami_payload = _whoami_payload(state, json_output=json_output, show_output=not json_output)
    except AuthError:
        whoami_payload = {}

    if json_output:
        summary["whoami"] = whoami_payload
        console.print(summary)


@register_app.command("poster")
def register_poster_command(
    ctx: typer.Context,
    profile_name: str | None = typer.Option(None, "--profile", help="Profile name"),
    show_key: bool = typer.Option(False, "--show-key", help="Show full API key"),
    json_output: bool = typer.Option(False, "--json", help="Output JSON"),
) -> None:
    state = _state_from_ctx(ctx)
    config = state.config
    if profile_name and profile_name not in config.profiles:
        console.print(f"[red]Profile '{profile_name}' not found.[/red]")
        raise typer.Exit(code=1)
    profile = config.ensure_profile(profile_name or config.active_profile)

    ensure_client_available()
    client = build_client(state.base_url)

    try:
        poster_output, poster_key = _register_poster(client, show_key)
    except AuthError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=2) from exc

    profile.poster_api_key = poster_key
    save_config(config)

    if json_output:
        console.print({"poster": poster_output})
        return

    console.print("[green]Poster registered.[/green]")
    if show_key:
        console.print(f"Poster key: {poster_key}")
    console.print("Next: multipl auth whoami")


@register_app.command("worker")
def register_worker_command(
    ctx: typer.Context,
    profile_name: str | None = typer.Option(None, "--profile", help="Profile name"),
    show_key: bool = typer.Option(False, "--show-key", help="Show full API key"),
    show_claim: bool = typer.Option(
        False,
        "--show-claim",
        help="Show worker claim URL/token/code",
    ),
    json_output: bool = typer.Option(False, "--json", help="Output JSON"),
) -> None:
    state = _state_from_ctx(ctx)
    config = state.config
    profile = config.ensure_profile(profile_name or config.active_profile)

    ensure_client_available()
    client = build_client(state.base_url)

    worker_name = f"{profile.name}-worker"
    try:
        worker_output, worker_key, claim_artifacts = _register_worker(
            client,
            worker_name,
            show_key,
            show_claim,
        )
    except AuthError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=2) from exc

    profile.worker_api_key = worker_key
    profile.worker_claim_token = claim_artifacts["worker_claim_token"]
    profile.worker_claim_verification_code = claim_artifacts["worker_claim_verification_code"]
    profile.worker_claim_url = claim_artifacts["worker_claim_url"]
    save_config(config)

    if json_output:
        console.print({"worker": worker_output})
        return

    console.print("[green]Worker registered.[/green]")
    if show_key:
        console.print(f"Worker key: {worker_key}")
    if show_claim:
        console.print(
            {
                "claim_url": claim_artifacts["worker_claim_url"],
                "claim_token": claim_artifacts["worker_claim_token"],
                "verification_code": claim_artifacts["worker_claim_verification_code"],
            }
        )
    else:
        console.print("Worker claim info saved to profile. Run `multipl auth claim-worker`.")
    console.print("Next: multipl auth whoami")


@app.command(
    "claim-worker",
    help="Claim a worker agent under the current poster profile (links poster ↔ worker for convenience flows).",
)
def claim_worker_command(
    ctx: typer.Context,
    claim_token: str | None = typer.Argument(None, help="Worker claim token"),
    verification_code: str | None = typer.Option(
        None, "--verification-code", help="Optional worker verification code"
    ),
    profile_name: str | None = typer.Option(None, "--profile", help="Profile name"),
    json_output: bool = typer.Option(False, "--json", help="Output JSON"),
) -> None:
    state = _state_from_ctx(ctx)
    config = state.config

    if profile_name and profile_name not in config.profiles:
        console.print(f"[red]Profile '{profile_name}' not found.[/red]")
        raise typer.Exit(code=1)
    profile = config.ensure_profile(profile_name or config.active_profile)

    if not profile.poster_api_key:
        console.print("[red]Poster API key not configured for this profile.[/red]")
        raise typer.Exit(code=2)

    resolved_claim_token = claim_token or profile.worker_claim_token
    if not resolved_claim_token:
        console.print(
            "[red]No worker claim token found. Run `multipl auth register worker --show-claim` "
            "(or `multipl auth login --show-claim`) to generate/save claim info.[/red]"
        )
        raise typer.Exit(code=1)

    resolved_verification_code = verification_code or profile.worker_claim_verification_code

    ensure_client_available()
    client = build_client(state.base_url)

    body = PostV1WorkersClaimBody(
        claim_token=resolved_claim_token,
        verification_code=resolved_verification_code if resolved_verification_code else UNSET,
    )

    try:
        response = claim_worker_api(
            client=client,
            authorization=f"Bearer {profile.poster_api_key}",
            body=body,
        )
    except httpx.HTTPError as exc:
        _raise_network_error(exc)

    if response.status_code == 200 and response.parsed is not None:
        payload = response.parsed.to_dict()
        profile.worker_claim_token = None
        profile.worker_claim_verification_code = None
        profile.worker_claim_url = None
        save_config(config)
        if json_output:
            console.print(payload)
            return
        worker = payload.get("worker", {})
        claimed_by = (
            worker.get("claimedByPosterId")
            if isinstance(worker, dict)
            else None
        )
        console.print("[green]Worker claimed under poster profile.[/green]")
        console.print(
            {
                "workerId": worker.get("id") if isinstance(worker, dict) else None,
                "workerName": worker.get("name") if isinstance(worker, dict) else None,
                "isClaimed": worker.get("isClaimed") if isinstance(worker, dict) else None,
                "claimedByPosterId": claimed_by,
            }
        )
        return

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

    payload = _parse_response_json(response)

    if response.status_code in {401, 403}:
        console.print("[red]Poster key required or invalid key.[/red]")
        if payload is not None:
            console.print(payload)
        raise typer.Exit(code=2)

    if response.status_code == 400:
        console.print("[red]Worker claim verification failed.[/red]")
        if payload is not None:
            console.print(payload)
        raise typer.Exit(code=1)

    if response.status_code == 404:
        console.print("[red]Worker claim token not found.[/red]")
        if payload is not None:
            console.print(payload)
        raise typer.Exit(code=1)

    if response.status_code == 409:
        message = None
        if payload is not None and isinstance(payload.get("error"), str):
            message = payload["error"]
        if message:
            console.print(f"[yellow]{message}[/yellow]")
        else:
            console.print("[yellow]Worker already claimed by another poster.[/yellow]")
        if payload is not None:
            console.print(payload)
        raise typer.Exit(code=1)

    console.print(f"[red]Worker claim failed (status={response.status_code}).[/red]")
    if payload is not None:
        console.print(payload)
    raise typer.Exit(code=2)


@app.command("whoami")
def whoami_command(
    ctx: typer.Context,
    profile_name: str | None = typer.Option(None, "--profile", help="Profile name"),
    json_output: bool = typer.Option(False, "--json", help="Output JSON"),
) -> None:
    state = _state_from_ctx(ctx)
    if profile_name:
        if profile_name not in state.config.profiles:
            console.print(f"[red]Profile '{profile_name}' not found.[/red]")
            raise typer.Exit(code=1)
        state.config.active_profile = profile_name
    try:
        payload = _whoami_payload(state, json_output=json_output, show_output=True)
    except AuthError as exc:
        console.print(f"[yellow]{exc}[/yellow]")
        raise typer.Exit(code=1) from exc

    if json_output:
        console.print(payload)


@set_app.command("poster-key")
def set_poster_key(
    key: str = typer.Argument(..., help="Poster API key"),
    profile_name: str | None = typer.Option(None, "--profile", help="Profile name"),
) -> None:
    config = load_config()
    profile = config.ensure_profile(profile_name or config.active_profile)
    profile.poster_api_key = key
    save_config(config)
    console.print("[green]Poster key saved.[/green]")


@set_app.command("worker-key")
def set_worker_key(
    key: str = typer.Argument(..., help="Worker API key"),
    profile_name: str | None = typer.Option(None, "--profile", help="Profile name"),
) -> None:
    config = load_config()
    profile = config.ensure_profile(profile_name or config.active_profile)
    profile.worker_api_key = key
    save_config(config)
    console.print("[green]Worker key saved.[/green]")


@unset_app.command("poster-key")
def unset_poster_key(
    profile_name: str | None = typer.Option(None, "--profile", help="Profile name"),
) -> None:
    config = load_config()
    profile = config.ensure_profile(profile_name or config.active_profile)
    profile.poster_api_key = None
    save_config(config)
    console.print("[green]Poster key cleared.[/green]")


@unset_app.command("worker-key")
def unset_worker_key(
    profile_name: str | None = typer.Option(None, "--profile", help="Profile name"),
) -> None:
    config = load_config()
    profile = config.ensure_profile(profile_name or config.active_profile)
    profile.worker_api_key = None
    save_config(config)
    console.print("[green]Worker key cleared.[/green]")


@wallet_app.command("set")
def wallet_set_command(
    ctx: typer.Context,
    address: str = typer.Argument(..., help="0x wallet address"),
    profile_name: str | None = typer.Option(None, "--profile", help="Profile name"),
    json_output: bool = typer.Option(False, "--json", help="Output JSON"),
) -> None:
    if not (address.startswith("0x") and len(address) == 42):
        console.print("[red]Wallet address must be a 0x-prefixed 42-char string.[/red]")
        raise typer.Exit(code=1)

    state = _state_from_ctx(ctx)
    config = state.config
    profile = config.ensure_profile(profile_name or config.active_profile)

    if not profile.worker_api_key:
        console.print("[red]Worker API key not configured for this profile.[/red]")
        raise typer.Exit(code=1)

    ensure_client_available()
    client = build_client(state.base_url)

    try:
        response = set_worker_wallet(
            client=client,
            authorization=f"Bearer {profile.worker_api_key}",
            body=PutV1WorkersMeWalletBody(address=address),
        )
    except httpx.HTTPError as exc:
        _raise_network_error(exc)

    if response.status_code != 200 or response.parsed is None:
        console.print(f"[red]Failed to update wallet (status={response.status_code}).[/red]")
        raise typer.Exit(code=2)

    wallet = response.parsed.wallet
    if json_output:
        console.print({"wallet": wallet.to_dict()})
        return

    console.print("[green]Worker wallet updated.[/green]")
    _render_kv_table(
        "Worker Wallet",
        {
            "workerId": wallet.worker_id,
            "walletAddress": wallet.wallet_address,
            "network": wallet.network,
            "asset": wallet.asset,
            "updatedAt": wallet.updated_at,
        },
    )
