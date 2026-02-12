from __future__ import annotations

from pathlib import Path

import pytest

from multipl_cli import polling_lock


def _configure_tmp_lock_dir(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(polling_lock, "config_dir", lambda: tmp_path)


def test_acquire_loop_lock_creates_and_releases_lock_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _configure_tmp_lock_dir(monkeypatch, tmp_path)

    lock = polling_lock.acquire_loop_lock(
        base_url="https://multipl.dev/api",
        worker_identity="worker:abc",
        task_type="research",
    )
    assert lock.path.exists()
    lock.release()
    assert not lock.path.exists()


def test_acquire_loop_lock_contention_raises(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _configure_tmp_lock_dir(monkeypatch, tmp_path)

    lock = polling_lock.acquire_loop_lock(
        base_url="https://multipl.dev/api",
        worker_identity="worker:abc",
        task_type="research",
    )

    with pytest.raises(polling_lock.LockHeldError):
        polling_lock.acquire_loop_lock(
            base_url="https://multipl.dev/api",
            worker_identity="worker:abc",
            task_type="research",
        )

    lock.release()


def test_acquire_loop_lock_force_steals_existing_lock(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _configure_tmp_lock_dir(monkeypatch, tmp_path)

    first = polling_lock.acquire_loop_lock(
        base_url="https://multipl.dev/api",
        worker_identity="worker:abc",
        task_type="research",
    )
    second = polling_lock.acquire_loop_lock(
        base_url="https://multipl.dev/api",
        worker_identity="worker:abc",
        task_type="research",
        force=True,
    )

    first.release()
    assert second.path.exists()
    second.release()
    assert not second.path.exists()
