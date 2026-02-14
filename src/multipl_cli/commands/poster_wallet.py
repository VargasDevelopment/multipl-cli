from __future__ import annotations

import json
import os
from typing import Any

import httpx
import typer
from eth_account import Account
from eth_account.messages import encode_defunct

from multipl_cli._client.api.posters.post_v1_posters_wallet_bind import (
    sync_detailed as bind_poster_wallet,
)
from multipl_cli._client.api.posters.post_v1_posters_wallet_nonce import (
    sync_detailed as get_poster_wallet_nonce,
)
from multipl_cli._client.models.post_v1_posters_wallet_bind_body import (
    PostV1PostersWalletBindBody,
)
from multipl_cli._client.models.post_v1_posters_wallet_nonce_body import (
    PostV1PostersWalletNonceBody,
)
from multipl_cli.app_state import AppState
from multipl_cli.config import is_training_base_url, load_config
from multipl_cli.console import console
from multipl_cli.openapi_client import build_client, ensure_client_available
from multipl_cli.polling import extract_retry_after_seconds

app = typer.Typer(no_args_is_help=True)


def _state_from_ctx(ctx: typer.Context | None) -> AppState:
    if ctx is not None and isinstance(ctx.obj, AppState):
        return ctx.obj
    config = load_config()
    active_profile = config.get_active_profile()
    base_url = active_profile.base_url or config.base_url
    return AppState(
        config=config,
        profile_name=config.active_profile,
        base_url=base_url,
        training_mode=is_training_base_url(base_url),
    )


def _parse_response_json(response) -> Any | None:
    try:
        return json.loads(response.content.decode("utf-8"))
    except Exception:
        return None


def _require_valid_address(address: str) -> str:
    value = address.strip()
    if not (value.startswith("0x") and len(value) == 42):
        console.print("[red]Wallet address must be a 0x-prefixed 42-char string.[/red]")
        raise typer.Exit(code=1)
    return value


def _resolve_profile(state: AppState, profile_name: str | None):
    if profile_name and profile_name not in state.config.profiles:
        console.print(f"[red]Profile '{profile_name}' not found.[/red]")
        raise typer.Exit(code=1)
    if profile_name:
        state.config.active_profile = profile_name
    return state.config.get_active_profile()


def _print_rate_limit_and_exit(response) -> None:
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


def _require_wallet_private_key() -> str:
    private_key = os.environ.get("MULTIPL_WALLET_PRIVATE_KEY")
    if private_key is None or not private_key.strip():
        console.print(
            "[red]MULTIPL_WALLET_PRIVATE_KEY is required for automatic wallet signing.[/red]"
        )
        raise typer.Exit(code=1)
    key = private_key.strip()
    if not key.startswith("0x"):
        key = f"0x{key}"
    return key


def _sign_wallet_binding_message(message: str, private_key: str) -> str:
    encoded = encode_defunct(text=message)
    try:
        account = Account.from_key(private_key)
    except Exception as exc:
        console.print(f"[red]Invalid MULTIPL_WALLET_PRIVATE_KEY: {exc}[/red]")
        raise typer.Exit(code=1) from exc

    signed = account.sign_message(encoded)
    signature = signed.signature.hex()
    if not signature.startswith("0x"):
        signature = f"0x{signature}"
    return signature


def _request_nonce(
    *,
    client,
    address: str,
) -> dict[str, Any]:
    try:
        response = get_poster_wallet_nonce(
            client=client,
            body=PostV1PostersWalletNonceBody(address=address),
        )
    except httpx.HTTPError as exc:
        console.print(f"[red]Network error: {exc}[/red]")
        raise typer.Exit(code=2) from exc

    if response.status_code == 429:
        _print_rate_limit_and_exit(response)

    if response.status_code != 200:
        if response.status_code in {401, 403}:
            console.print("[red]Poster key required or invalid key.[/red]")
        else:
            console.print(f"[red]Failed to request wallet nonce (status={response.status_code}).[/red]")
        body = _parse_response_json(response)
        if body is not None:
            console.print(body)
        raise typer.Exit(code=2)

    payload = response.parsed.to_dict() if response.parsed is not None else _parse_response_json(response)
    if not isinstance(payload, dict):
        console.print("[red]Invalid wallet nonce response payload.[/red]")
        raise typer.Exit(code=2)
    return payload


def _request_bind(
    *,
    client,
    address: str,
    nonce: str,
    signature: str,
) -> dict[str, Any]:
    try:
        response = bind_poster_wallet(
            client=client,
            body=PostV1PostersWalletBindBody(address=address, nonce=nonce, signature=signature),
        )
    except httpx.HTTPError as exc:
        console.print(f"[red]Network error: {exc}[/red]")
        raise typer.Exit(code=2) from exc

    if response.status_code == 429:
        _print_rate_limit_and_exit(response)

    if response.status_code != 200:
        if response.status_code in {401, 403}:
            console.print("[red]Poster key or wallet signature invalid.[/red]")
        else:
            console.print(f"[red]Failed to bind poster wallet (status={response.status_code}).[/red]")
        body = _parse_response_json(response)
        if body is not None:
            console.print(body)
        raise typer.Exit(code=2)

    payload = response.parsed.to_dict() if response.parsed is not None else _parse_response_json(response)
    if not isinstance(payload, dict):
        console.print("[red]Invalid wallet bind response payload.[/red]")
        raise typer.Exit(code=2)
    return payload


@app.command("nonce")
def nonce(
    ctx: typer.Context,
    address: str = typer.Argument(..., help="0x wallet address"),
    profile_name: str | None = typer.Option(None, "--profile", help="Profile name"),
    json_output: bool = typer.Option(False, "--json", help="Output JSON"),
) -> None:
    wallet_address = _require_valid_address(address)
    state = _state_from_ctx(ctx)
    if state.training_mode:
        console.print(
            "[red]Poster wallet commands are disabled in training mode. "
            "Training does not use payouts or wallet binding.[/red]"
        )
        raise typer.Exit(code=1)

    profile = _resolve_profile(state, profile_name)
    if not profile.poster_api_key:
        console.print("[red]Poster API key not configured for this profile.[/red]")
        raise typer.Exit(code=2)

    ensure_client_available()
    client = build_client(state.base_url, api_key=profile.poster_api_key)
    payload = _request_nonce(client=client, address=wallet_address)

    if json_output:
        console.print(payload)
        return

    console.print("[green]Poster wallet nonce issued.[/green]")
    console.print(
        {
            "address": payload.get("address"),
            "nonce": payload.get("nonce"),
            "expiresAt": payload.get("expiresAt"),
        }
    )
    console.print("Use this challenge with `multipl auth poster-wallet bind <0xAddress>`.")


@app.command("bind")
def bind(
    ctx: typer.Context,
    address: str = typer.Argument(..., help="0x wallet address"),
    profile_name: str | None = typer.Option(None, "--profile", help="Profile name"),
    json_output: bool = typer.Option(False, "--json", help="Output JSON"),
    no_sign: bool = typer.Option(False, "--no-sign", help="Only fetch nonce and print manual bind fields"),
) -> None:
    wallet_address = _require_valid_address(address)
    state = _state_from_ctx(ctx)
    if state.training_mode:
        console.print(
            "[red]Poster wallet commands are disabled in training mode. "
            "Training does not use payouts or wallet binding.[/red]"
        )
        raise typer.Exit(code=1)

    profile = _resolve_profile(state, profile_name)
    if not profile.poster_api_key:
        console.print("[red]Poster API key not configured for this profile.[/red]")
        raise typer.Exit(code=2)

    ensure_client_available()
    client = build_client(state.base_url, api_key=profile.poster_api_key)
    nonce_payload = _request_nonce(
        client=client,
        address=wallet_address,
    )

    nonce_address = nonce_payload.get("address")
    nonce_value = nonce_payload.get("nonce")
    message_to_sign = nonce_payload.get("message")
    if not isinstance(nonce_address, str) or not isinstance(nonce_value, str) or not isinstance(
        message_to_sign, str
    ):
        console.print("[red]Wallet nonce response missing required fields.[/red]")
        raise typer.Exit(code=2)

    if no_sign:
        manual = {
            "address": nonce_address,
            "nonce": nonce_value,
            "signature": "<0x-signature-of-message>",
        }
        if json_output:
            console.print(
                {
                    "nonce": nonce_payload,
                    "messageToSign": message_to_sign,
                    "bindRequest": manual,
                }
            )
        else:
            console.print("[yellow]Signature step skipped (--no-sign).[/yellow]")
            console.print({"messageToSign": message_to_sign, "bindRequest": manual})
        raise typer.Exit(code=1)

    private_key = _require_wallet_private_key()
    signature = _sign_wallet_binding_message(message_to_sign, private_key)

    bind_payload = _request_bind(
        client=client,
        address=nonce_address,
        nonce=nonce_value,
        signature=signature,
    )

    if json_output:
        console.print(bind_payload)
        return

    console.print("[green]Poster wallet bound.[/green]")
    console.print(
        {
            "walletAddress": bind_payload.get("walletAddress", nonce_address),
            "walletBoundAt": bind_payload.get("walletBoundAt"),
        }
    )
