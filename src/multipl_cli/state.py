from __future__ import annotations

import os
from pathlib import Path

from platformdirs import user_config_dir

APP_NAME = "multipl"
APP_AUTHOR = "Multipl"

MULTIPL_CLI_HOME_ENV_VAR = "MULTIPL_CLI_HOME"

CONFIG_FILE = "config.json"
CLAIMS_FILE = "claims.json"
LOCKS_DIR = "locks"


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def get_state_dir() -> Path:
    override = os.environ.get(MULTIPL_CLI_HOME_ENV_VAR)
    if override:
        return Path(override).expanduser()
    return Path(user_config_dir(APP_NAME, APP_AUTHOR))


def get_config_path() -> Path:
    return get_state_dir() / CONFIG_FILE


def get_claims_path() -> Path:
    return get_state_dir() / CLAIMS_FILE


def get_locks_dir() -> Path:
    return get_state_dir() / LOCKS_DIR


def get_lock_path(name: str) -> Path:
    return get_locks_dir() / f"{name}.lock"
