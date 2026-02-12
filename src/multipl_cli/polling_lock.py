from __future__ import annotations

import hashlib
import json
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from multipl_cli.config import config_dir

LOCKS_DIR = "locks"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _safe_identifier(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:24]


def acquire_loop_lock_key(*, base_url: str, worker_identity: str, task_type: str) -> str:
    normalized_url = base_url.strip().rstrip("/")
    raw = f"{normalized_url}\n{worker_identity.strip()}\n{task_type.strip()}"
    return _safe_identifier(raw)


def acquire_loop_lock_path(key: str) -> Path:
    return config_dir() / LOCKS_DIR / f"claim-acquire-{key}.lock"


def _read_lock_payload(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
    except Exception:
        return {}
    if isinstance(data, dict):
        return data
    return {}


@dataclass
class LockHeldError(RuntimeError):
    path: Path
    existing_payload: dict[str, Any]

    def __post_init__(self) -> None:
        super().__init__(f"lock_held:{self.path}")


@dataclass
class AcquireLoopLock:
    path: Path
    token: str

    def release(self) -> None:
        payload = _read_lock_payload(self.path)
        if payload.get("token") != self.token:
            return
        try:
            self.path.unlink()
        except FileNotFoundError:
            return

    def __enter__(self) -> "AcquireLoopLock":
        return self

    def __exit__(self, _exc_type, _exc, _tb) -> None:
        self.release()


def acquire_loop_lock(
    *,
    base_url: str,
    worker_identity: str,
    task_type: str,
    force: bool = False,
) -> AcquireLoopLock:
    key = acquire_loop_lock_key(
        base_url=base_url,
        worker_identity=worker_identity,
        task_type=task_type,
    )
    path = acquire_loop_lock_path(key)
    path.parent.mkdir(parents=True, exist_ok=True)

    attempts = 0
    while True:
        attempts += 1
        token = uuid.uuid4().hex
        payload = {
            "token": token,
            "pid": os.getpid(),
            "startedAt": _utc_now_iso(),
            "baseUrl": base_url,
            "taskType": task_type,
            "workerIdentity": worker_identity,
        }
        serialized = json.dumps(payload, sort_keys=True)
        try:
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError as exc:
            existing = _read_lock_payload(path)
            if not force:
                raise LockHeldError(path=path, existing_payload=existing) from exc
            try:
                path.unlink()
            except FileNotFoundError:
                continue
            if attempts < 4:
                continue
            raise RuntimeError(f"Failed to steal lock at {path}") from exc
        else:
            with os.fdopen(fd, "w") as lock_file:
                lock_file.write(serialized)
            return AcquireLoopLock(path=path, token=token)
