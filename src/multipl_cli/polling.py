from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Callable, Iterable

import httpx

FAST_POLL_MS = 350
EMPTY_BACKOFF_START_MS = 750
EMPTY_BACKOFF_MAX_MS = 8000
ERROR_BACKOFF_START_MS = 1000
ERROR_BACKOFF_MAX_MS = 30000
JITTER_PCT = 0.25
WATCH_MIN_INTERVAL_S = 1.0
WATCH_DEFAULT_INTERVAL_S = 2.0

TRANSIENT_STATUS_CODES = {408, 425, 500, 502, 503, 504}


@dataclass
class BackoffState:
    empty_delay_ms: int = EMPTY_BACKOFF_START_MS
    error_delay_ms: int = ERROR_BACKOFF_START_MS

    def reset_empty(self) -> None:
        self.empty_delay_ms = EMPTY_BACKOFF_START_MS

    def reset_error(self) -> None:
        self.error_delay_ms = ERROR_BACKOFF_START_MS

    def bump_empty(self) -> None:
        self.empty_delay_ms = min(int(self.empty_delay_ms * 1.6), EMPTY_BACKOFF_MAX_MS)

    def bump_error(self) -> None:
        self.error_delay_ms = min(self.error_delay_ms * 2, ERROR_BACKOFF_MAX_MS)


def sleep_with_jitter(ms: int, jitter_pct: float = JITTER_PCT) -> None:
    delta = ms * jitter_pct
    jittered = ms + random.uniform(-delta, delta)
    time.sleep(max(jittered, 0) / 1000.0)


def extract_retry_after_seconds(response: httpx.Response) -> int | None:
    header_value = response.headers.get("Retry-After") or response.headers.get("retry-after")
    if header_value:
        try:
            return max(0, int(float(header_value)))
        except ValueError:
            pass
    try:
        data = response.json()
    except Exception:
        return None
    if isinstance(data, dict):
        value = data.get("retryAfterSeconds")
        if isinstance(value, (int, float)):
            return max(0, int(value))
    return None


def is_transient_exception(error: Exception) -> bool:
    return isinstance(
        error,
        (
            httpx.TimeoutException,
            httpx.NetworkError,
            httpx.RemoteProtocolError,
            httpx.ConnectError,
        ),
    )


def poll_with_backoff(
    request_fn: Callable[[], httpx.Response],
    *,
    mode: str,
    empty_statuses: Iterable[int],
    handle_success: Callable[[httpx.Response], None],
    handle_empty: Callable[[httpx.Response], None] | None = None,
    handle_rate_limited: Callable[[httpx.Response, int | None], None] | None = None,
    handle_transient_error: Callable[[Exception | httpx.Response], None] | None = None,
    handle_non_retryable: Callable[[httpx.Response], None] | None = None,
) -> None:
    if mode not in {"wait", "drain"}:
        raise ValueError("poll_with_backoff supports only wait/drain modes")

    empty_set = set(empty_statuses)
    state = BackoffState()
    saw_success = False

    while True:
        try:
            response = request_fn()
        except Exception as exc:
            if not is_transient_exception(exc):
                raise
            if handle_transient_error:
                handle_transient_error(exc)
            sleep_with_jitter(state.error_delay_ms)
            state.bump_error()
            continue

        status = response.status_code
        if status == 200:
            state.reset_empty()
            state.reset_error()
            saw_success = True
            handle_success(response)
            if mode == "wait":
                return
            sleep_with_jitter(FAST_POLL_MS)
            continue

        if status in empty_set:
            state.reset_error()
            if handle_empty:
                handle_empty(response)
            if mode == "drain" and saw_success:
                return
            sleep_with_jitter(state.empty_delay_ms)
            state.bump_empty()
            continue

        if status == 429:
            retry_after = extract_retry_after_seconds(response)
            if handle_rate_limited:
                handle_rate_limited(response, retry_after)
            if retry_after is not None:
                time.sleep(max(retry_after, 0))
                state.reset_error()
                continue
            sleep_with_jitter(state.error_delay_ms)
            state.bump_error()
            continue

        if status in TRANSIENT_STATUS_CODES:
            if handle_transient_error:
                handle_transient_error(response)
            sleep_with_jitter(state.error_delay_ms)
            state.bump_error()
            continue

        if handle_non_retryable:
            handle_non_retryable(response)
        return


class RateLimitCooldown(RuntimeError):
    def __init__(self, retry_after_seconds: int | None, payload: dict | None = None):
        super().__init__("rate_limited")
        self.retry_after_seconds = retry_after_seconds
        self.payload = payload or {}
