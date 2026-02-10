from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from platformdirs import user_config_dir

APP_NAME = "multipl"
APP_AUTHOR = "Multipl"

CONFIG_FILE = "config.json"
CLAIMS_FILE = "claims.json"

DEFAULT_BASE_URL = "https://multipl.dev/api"


def config_dir() -> Path:
    return Path(user_config_dir(APP_NAME, APP_AUTHOR))


def config_path() -> Path:
    return config_dir() / CONFIG_FILE


def claims_path() -> Path:
    return config_dir() / CLAIMS_FILE


@dataclass
class Profile:
    name: str
    poster_api_key: str | None = None
    worker_api_key: str | None = None
    worker_claim_token: str | None = None
    worker_claim_verification_code: str | None = None
    worker_claim_url: str | None = None

    @classmethod
    def from_dict(cls, name: str, data: dict[str, Any]) -> "Profile":
        return cls(
            name=name,
            poster_api_key=data.get("poster_api_key"),
            worker_api_key=data.get("worker_api_key"),
            worker_claim_token=data.get("worker_claim_token"),
            worker_claim_verification_code=data.get("worker_claim_verification_code"),
            worker_claim_url=data.get("worker_claim_url"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "poster_api_key": self.poster_api_key,
            "worker_api_key": self.worker_api_key,
            "worker_claim_token": self.worker_claim_token,
            "worker_claim_verification_code": self.worker_claim_verification_code,
            "worker_claim_url": self.worker_claim_url,
        }


@dataclass
class PayerConfig:
    type: str = "local_key"
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "PayerConfig":
        if not data:
            return cls()
        return cls(type=data.get("type", "manual"), metadata=data.get("metadata", {}) or {})

    def to_dict(self) -> dict[str, Any]:
        return {"type": self.type, "metadata": self.metadata}


@dataclass
class Config:
    base_url: str
    active_profile: str
    profiles: dict[str, Profile] = field(default_factory=dict)
    payer: PayerConfig = field(default_factory=PayerConfig)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Config":
        base_url = data.get("base_url") or DEFAULT_BASE_URL
        active_profile = data.get("active_profile") or "default"
        profiles_raw = data.get("profiles") or {}
        profiles = {
            name: Profile.from_dict(name, value)
            for name, value in profiles_raw.items()
        }
        payer = PayerConfig.from_dict(data.get("payer"))
        return cls(base_url=base_url, active_profile=active_profile, profiles=profiles, payer=payer)

    def to_dict(self) -> dict[str, Any]:
        return {
            "base_url": self.base_url,
            "active_profile": self.active_profile,
            "profiles": {name: profile.to_dict() for name, profile in self.profiles.items()},
            "payer": self.payer.to_dict(),
        }

    def ensure_profile(self, name: str) -> Profile:
        profile = self.profiles.get(name)
        if profile:
            return profile
        profile = Profile(name=name)
        self.profiles[name] = profile
        return profile

    def get_active_profile(self) -> Profile:
        if self.active_profile in self.profiles:
            return self.profiles[self.active_profile]
        if self.profiles:
            first = next(iter(self.profiles.values()))
            self.active_profile = first.name
            return first
        profile = Profile(name="default")
        self.profiles[profile.name] = profile
        self.active_profile = profile.name
        return profile


def load_config() -> Config:
    base_url = os.environ.get("MULTIPL_BASE_URL") or DEFAULT_BASE_URL
    path = config_path()
    if not path.exists():
        config = Config(base_url=base_url, active_profile="default", profiles={"default": Profile("default")})
        save_config(config)
        return config
    data = json.loads(path.read_text())
    config = Config.from_dict(data)
    if not config.base_url:
        config.base_url = base_url
    if not config.profiles:
        config.profiles = {"default": Profile("default")}
        config.active_profile = "default"
        save_config(config)
    return config


def save_config(config: Config) -> None:
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config.to_dict(), indent=2, sort_keys=True))


def mask_secret(value: str | None, visible: int = 4) -> str | None:
    if value is None:
        return None
    trimmed = value.strip()
    if len(trimmed) <= visible * 2:
        return "*" * len(trimmed)
    return f"{trimmed[:visible]}...{trimmed[-visible:]}"


@dataclass
class ClaimsCache:
    claims_by_profile: dict[str, dict[str, str]] = field(default_factory=dict)

    @classmethod
    def load(cls) -> "ClaimsCache":
        path = claims_path()
        if not path.exists():
            return cls()
        data = json.loads(path.read_text())
        return cls(claims_by_profile=data.get("claims_by_profile", {}) or {})

    def save(self) -> None:
        path = claims_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {"claims_by_profile": self.claims_by_profile}
        path.write_text(json.dumps(data, indent=2, sort_keys=True))

    def get_claim(self, profile: str, job_id: str) -> str | None:
        return self.claims_by_profile.get(profile, {}).get(job_id)

    def set_claim(self, profile: str, job_id: str, claim_id: str) -> None:
        self.claims_by_profile.setdefault(profile, {})[job_id] = claim_id

    def drop_claim(self, profile: str, job_id: str) -> None:
        profile_claims = self.claims_by_profile.get(profile)
        if not profile_claims:
            return
        profile_claims.pop(job_id, None)
