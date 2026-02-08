from __future__ import annotations

import json
from pathlib import Path

import typer

from multipl_cli.app_state import AppState
from multipl_cli.console import console
from multipl_cli.openapi_client import build_client, ensure_client_available
from multipl_cli.polling import extract_retry_after_seconds
from multipl_cli.x402.flow import PaymentFlowError, PaymentRequiredError, request_with_x402
from multipl_cli.x402.payer_cdp import CdpPayer
from multipl_cli.x402.payer_local_key import LocalKeyPayer
from multipl_cli.x402.payer_manual import ManualPayer
from multipl_cli.x402.proof import ProofCache, ProofError, load_proof_from_file, parse_proof_value

app = typer.Typer(no_args_is_help=True)


@app.command("get")
def get_result(
    ctx: typer.Context,
    job_id: str = typer.Argument(..., help="Job ID"),
    out: Path | None = typer.Option(None, "--out", help="Write result JSON to file"),
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

    client = build_client(state.base_url)

    def request_fn(extra_headers: dict[str, str] | None):
        headers = {"authorization": f"Bearer {profile.poster_api_key}"}
        if extra_headers:
            headers.update(extra_headers)
        return client.get_httpx_client().request(
            "get",
            f"/v1/jobs/{job_id}/results",
            headers=headers,
        )

    try:
        response = request_with_x402(
            request_fn,
            payer=payer,
            allow_pay=not no_pay,
            proof_cache=ProofCache.load(),
        )
    except PaymentRequiredError as exc:
        terms = exc.terms
        console.print("[yellow]Payment required to unlock results.[/yellow]")
        console.print({
            "recipient": terms.recipient,
            "amount": terms.amount,
            "asset": terms.asset,
            "network": terms.network,
            "payment_context": terms.payment_context,
            "facilitator": terms.facilitator,
            "hint": terms.hint,
        })
        raise typer.Exit(code=3) from exc
    except PaymentFlowError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=3) from exc

    if response.status_code == 200:
        payload = response.json()
        result = payload.get("result") if isinstance(payload, dict) else payload
        if out:
            out.write_text(json.dumps(result, indent=2))
            if json_output:
                console.print({"ok": True, "path": str(out)})
            else:
                console.print(f"[green]Wrote result to {out}[/green]")
        else:
            console.print(payload if json_output else result)
        return

    if response.status_code == 429:
        retry_after = extract_retry_after_seconds(response)
        if retry_after is not None:
            console.print(f"Rate limited. Retry after {retry_after}s.")
        else:
            console.print("Rate limited.")
        raise typer.Exit(code=4)

    if response.status_code in {409, 410, 422, 403}:
        console.print(f"[red]Results unavailable (status={response.status_code}).[/red]")
        try:
            console.print(response.json())
        except Exception:
            pass
        raise typer.Exit(code=1)

    console.print(f"[red]Failed to fetch results (status={response.status_code}).[/red]")
    raise typer.Exit(code=2)
