from __future__ import annotations

import fcntl
import json
import os
import stat
import uuid
from dataclasses import dataclass
from pathlib import Path

from multipl_cli.private_dispatch.journal_state import (
    JournalState,
    parse_state,
    serialize_state,
)


class DispatchLockHeld(RuntimeError):
    pass


def ensure_private_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(path, 0o700)
    if stat.S_IMODE(path.stat().st_mode) != 0o700:
        raise OSError(f"Dispatcher directory is not private: {path}")


def atomic_write(path: Path, content: bytes) -> None:
    ensure_private_dir(path.parent)
    temporary = path.parent / f".{path.name}.{uuid.uuid4().hex}.tmp"
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        os.chmod(path, 0o600)
        directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            temporary = None


def atomic_json(path: Path, payload: dict[str, object]) -> None:
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    atomic_write(path, serialized)


@dataclass
class ProcessLock:
    descriptor: int

    def close(self) -> None:
        fcntl.flock(self.descriptor, fcntl.LOCK_UN)
        os.close(self.descriptor)

    def __enter__(self) -> "ProcessLock":
        return self

    def __exit__(self, _exc_type, _exc, _tb) -> None:
        self.close()


def acquire_lock(state_dir: Path) -> ProcessLock:
    ensure_private_dir(state_dir)
    path = state_dir / "dispatch.lock"
    descriptor = os.open(path, os.O_RDWR | os.O_CREAT, 0o600)
    os.chmod(path, 0o600)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as exc:
        os.close(descriptor)
        raise DispatchLockHeld("Another private dispatch is already running") from exc
    return ProcessLock(descriptor)


class Journal:
    def __init__(self, state_dir: Path) -> None:
        self.path = state_dir / "journal.json"

    def load(self) -> JournalState | None:
        if not self.path.exists():
            return None
        return parse_state(self.path.read_bytes())

    def write(self, state: JournalState) -> None:
        atomic_write(self.path, serialize_state(state))

    def clear(self) -> None:
        try:
            self.path.unlink()
        except FileNotFoundError:
            return
        directory = os.open(self.path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
