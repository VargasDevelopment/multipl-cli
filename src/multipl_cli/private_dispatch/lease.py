from __future__ import annotations

from datetime import datetime, timezone

MINIMUM_SAFETY_MARGIN = 0.5
MAXIMUM_SAFETY_MARGIN = 5.0


class LeaseExpired(RuntimeError):
    pass


def parse_expires_at(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise LeaseExpired("Lease expiry is not a valid timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise LeaseExpired("Lease expiry must include a timezone")
    return parsed.astimezone(timezone.utc)


def remaining_seconds(value: str, *, now: datetime | None = None) -> float:
    current = now or datetime.now(timezone.utc)
    return (parse_expires_at(value) - current.astimezone(timezone.utc)).total_seconds()


def safety_margin(remaining: float) -> float:
    return min(MAXIMUM_SAFETY_MARGIN, max(MINIMUM_SAFETY_MARGIN, remaining * 0.2))


def launch_is_safe(expires_at: str, *, now: datetime | None = None) -> bool:
    remaining = remaining_seconds(expires_at, now=now)
    return remaining > safety_margin(remaining)


def renewal_delay(
    expires_at: str,
    heartbeat_seconds: float,
    *,
    now: datetime | None = None,
) -> float:
    remaining = remaining_seconds(expires_at, now=now)
    if remaining <= 0:
        raise LeaseExpired("Lease expired before renewal")
    return max(0.0, min(heartbeat_seconds, remaining - safety_margin(remaining)))


def renewal_timeout(expires_at: str, *, now: datetime | None = None) -> float:
    remaining = remaining_seconds(expires_at, now=now)
    if remaining <= 0:
        raise LeaseExpired("Lease expired before renewal")
    return remaining
