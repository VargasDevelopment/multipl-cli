from __future__ import annotations

from dataclasses import dataclass

from multipl_cli.config import Config


@dataclass
class AppState:
    config: Config
    profile_name: str
    base_url: str
    training_mode: bool = False
