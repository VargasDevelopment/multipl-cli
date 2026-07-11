from __future__ import annotations

import json
import os
import re
import stat
from pathlib import Path
from urllib.parse import urlparse

from multipl_cli.private_dispatch.types import DispatchConfig, TaskIdentity, TaskPolicy

_TASK_KEY = re.compile(
    r"^(?P<registry>[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*)/"
    r"(?P<type>[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*)@(?P<version>[1-9][0-9]*)$"
)
_REASONING = {"low", "medium", "high", "xhigh"}
_TOP_LEVEL = {"baseUrl", "bearer", "scopeHeaders", "worktrees", "heartbeatSeconds"}
_TASK_FIELDS = {"cwd", "model", "reasoning"}
_SCOPE_HEADERS = {"x-multipl-namespace", "x-multipl-lane"}


class DispatchConfigError(ValueError):
    pass


def _object(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise DispatchConfigError(f"{label} must be a JSON object")
    return value


def _text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise DispatchConfigError(f"{label} must be a non-empty string")
    return value.strip()


def _secure_config_file(path: Path) -> None:
    try:
        metadata = path.stat()
    except FileNotFoundError as exc:
        raise DispatchConfigError(f"Private dispatcher config does not exist: {path}") from exc
    if not path.is_file():
        raise DispatchConfigError("Private dispatcher config must be a regular file")
    if metadata.st_uid != os.geteuid():
        raise DispatchConfigError("Private dispatcher config must be owned by the current user")
    mode = stat.S_IMODE(metadata.st_mode)
    if mode != 0o600:
        raise DispatchConfigError("Private dispatcher config permissions must be 0600")


def _is_under(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _identity(key: str) -> TaskIdentity:
    match = _TASK_KEY.fullmatch(key)
    if not match:
        raise DispatchConfigError(
            f"Invalid task key '{key}'; expected full registryId/typeId@positive-version"
        )
    return TaskIdentity(
        registry_id=match.group("registry"),
        type_id=match.group("type"),
        version=int(match.group("version")),
    )


def _task_policy(key: str, value: object) -> TaskPolicy:
    data = _object(value, f"worktrees.{key}")
    if set(data) != _TASK_FIELDS:
        raise DispatchConfigError(f"worktrees.{key} must contain exactly cwd, model, and reasoning")
    cwd = Path(_text(data["cwd"], f"worktrees.{key}.cwd")).expanduser().resolve()
    if not cwd.is_absolute() or not cwd.is_dir():
        raise DispatchConfigError(f"worktrees.{key}.cwd must be an existing absolute directory")
    reasoning = _text(data["reasoning"], f"worktrees.{key}.reasoning")
    if reasoning not in _REASONING:
        raise DispatchConfigError(f"worktrees.{key}.reasoning must be one of {sorted(_REASONING)}")
    return TaskPolicy(
        identity=_identity(key),
        cwd=cwd,
        model=_text(data["model"], f"worktrees.{key}.model"),
        reasoning=reasoning,
    )


def load_dispatch_config(path: Path) -> DispatchConfig:
    resolved = path.expanduser().resolve()
    _secure_config_file(resolved)
    try:
        data = _object(json.loads(resolved.read_text(encoding="utf-8")), "config")
    except (json.JSONDecodeError, OSError) as exc:
        raise DispatchConfigError(f"Cannot read private dispatcher config: {exc}") from exc
    if set(data) != _TOP_LEVEL:
        raise DispatchConfigError(
            "Private dispatcher config must contain exactly baseUrl, bearer, scopeHeaders, "
            "worktrees, and heartbeatSeconds"
        )
    base_url = _text(data["baseUrl"], "baseUrl").rstrip("/")
    parsed = urlparse(base_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise DispatchConfigError("baseUrl must be an absolute HTTP(S) URL")
    scope_headers = _object(data["scopeHeaders"], "scopeHeaders")
    if set(scope_headers) != _SCOPE_HEADERS:
        raise DispatchConfigError("scopeHeaders must contain exactly the private namespace and lane headers")
    raw_tasks = _object(data["worktrees"], "worktrees")
    if not raw_tasks:
        raise DispatchConfigError("worktrees must contain at least one exact allowlist entry")
    tasks = tuple(_task_policy(key, raw_tasks[key]) for key in sorted(raw_tasks))
    heartbeat = data["heartbeatSeconds"]
    if isinstance(heartbeat, bool) or not isinstance(heartbeat, (int, float)) or heartbeat <= 0:
        raise DispatchConfigError("heartbeatSeconds must be positive")
    state_dir = (resolved.parent / "dispatch-state").resolve()
    protected_paths = (resolved, state_dir)
    for task in tasks:
        for protected in protected_paths:
            if _is_under(protected, task.cwd):
                raise DispatchConfigError(
                    "Private dispatcher config and state must be outside every allowed task cwd"
                )
    return DispatchConfig(
        base_url=base_url,
        bearer=_text(data["bearer"], "bearer"),
        namespace=_text(scope_headers["x-multipl-namespace"], "x-multipl-namespace"),
        lane=_text(scope_headers["x-multipl-lane"], "x-multipl-lane"),
        tasks=tasks,
        state_dir=state_dir,
        heartbeat_seconds=float(heartbeat),
    )
