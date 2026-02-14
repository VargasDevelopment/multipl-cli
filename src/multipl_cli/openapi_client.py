from __future__ import annotations

from typing import Any

from multipl_cli import __version__
from multipl_cli.console import console

USER_AGENT = f"multipl-cli {__version__}"


class ClientImportError(RuntimeError):
    pass


def _import_client_classes():
    try:
        from multipl_cli._client.client import Client  # type: ignore
    except ModuleNotFoundError as exc:  # pragma: no cover - defensive
        raise ClientImportError(
            "OpenAPI client not generated. Run ./scripts/gen_client.sh"
        ) from exc
    return Client


def build_client(base_url: str, api_key: str | None = None, timeout: float | None = 30.0):
    Client = _import_client_classes()
    headers: dict[str, str] = {"user-agent": USER_AGENT}
    if api_key:
        headers["authorization"] = f"Bearer {api_key}"
    return Client(base_url=base_url, headers=headers, timeout=timeout)


def clone_with_headers(client: Any, headers: dict[str, str]):
    if hasattr(client, "with_headers"):
        return client.with_headers(headers)
    merged = dict(client._headers or {})  # type: ignore[attr-defined]
    merged.update(headers)
    return build_client(
        client._base_url,  # type: ignore[attr-defined]
        api_key=None,
        timeout=client._timeout if getattr(client, "_timeout", None) is not None else 30.0,  # type: ignore[attr-defined]
    ).with_headers(merged)  # type: ignore


def ensure_client_available() -> None:
    try:
        _import_client_classes()
    except ClientImportError as exc:
        console.print(f"[red]{exc}[/red]")
        raise SystemExit(1) from exc
