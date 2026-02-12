from __future__ import annotations

import random
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any, Callable, Iterable, Mapping

import httpx

FAST_POLL_MS = 650
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


def _header_value(headers: Mapping[str, str], name: str) -> str | None:
    for key, value in headers.items():
        if key.lower() == name.lower():
            return value
    return None


def parse_retry_after(headers: Mapping[str, str], now: datetime | None = None) -> int | None:
    header_value = _header_value(headers, "Retry-After")
    if not header_value:
        return None
    value = header_value.strip()
    if not value:
        return None
    try:
        return max(0, int(float(value)))
    except ValueError:
        pass
    try:
        target = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    if target.tzinfo is None:
        target = target.replace(tzinfo=timezone.utc)
    now_dt = now or datetime.now(timezone.utc)
    delta_seconds = int((target - now_dt).total_seconds())
    return max(0, delta_seconds)


def _retry_after_from_body(body: Any) -> int | None:
    if not isinstance(body, dict):
        return None
    value = body.get("retryAfterSeconds")
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return max(0, int(value))
    return None


def maybe_extract_kind(body: Any) -> str | None:
    if not isinstance(body, dict):
        return None
    for key in ("kind", "reason", "code", "error"):
        value = body.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def compute_wait_seconds(
    headers: Mapping[str, str],
    body: Any,
    *,
    fallback_seconds: int,
    now: datetime | None = None,
) -> tuple[int, str]:
    retry_after_header = parse_retry_after(headers, now=now)
    if retry_after_header is not None:
        return retry_after_header, "retry-after-header"
    retry_after_body = _retry_after_from_body(body)
    if retry_after_body is not None:
        return retry_after_body, "retry-after-seconds-body"
    return max(0, int(fallback_seconds)), "backoff"


def extract_request_id(headers: Mapping[str, str]) -> str | None:
    for key in ("x-request-id", "reqId", "req-id"):
        value = _header_value(headers, key)
        if value:
            return value
    return None


def extract_retry_after_seconds(response: httpx.Response) -> int | None:
    retry_after_header = parse_retry_after(response.headers)
    if retry_after_header is not None:
        return retry_after_header
    try:
        data = response.json()
    except Exception:
        return None
    return _retry_after_from_body(data)


def parse_response_json(response: httpx.Response) -> dict[str, Any]:
    try:
        data = response.json()
    except Exception:
        return {}
    if isinstance(data, dict):
        return data
    return {}


def _fallback_error_wait_seconds(error_delay_ms: int) -> int:
    if error_delay_ms <= 0:
        return 0
    return max(1, int(error_delay_ms / 1000))


def _sleep_seconds(seconds: float) -> None:
    time.sleep(max(seconds, 0))


def _sleep_with_callback(
    *,
    seconds: float,
    reason: str,
    response: httpx.Response | None,
    source: str,
    handle_sleep: Callable[[float, str, httpx.Response | None, str], None] | None,
) -> None:
    if handle_sleep:
        handle_sleep(seconds, reason, response, source)
    _sleep_seconds(seconds)


def _sleep_with_jitter_and_callback(
    *,
    ms: int,
    reason: str,
    response: httpx.Response | None,
    source: str,
    handle_sleep: Callable[[float, str, httpx.Response | None, str], None] | None,
) -> None:
    seconds = max(ms, 0) / 1000.0
    if handle_sleep:
        handle_sleep(seconds, reason, response, source)
    sleep_with_jitter(ms)


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
    handle_rate_limited: Callable[[httpx.Response, int, str], None] | None = None,
    handle_transient_error: Callable[[Exception | httpx.Response], None] | None = None,
    handle_non_retryable: Callable[[httpx.Response], None] | None = None,
    handle_sleep: Callable[[float, str, httpx.Response | None, str], None] | None = None,
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
            _sleep_with_jitter_and_callback(
                ms=state.error_delay_ms,
                reason="transient_exception",
                response=None,
                source="backoff",
                handle_sleep=handle_sleep,
            )
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
            _sleep_with_jitter_and_callback(
                ms=FAST_POLL_MS,
                reason="fast_poll",
                response=response,
                source="fast-poll",
                handle_sleep=handle_sleep,
            )
            continue

        if status in empty_set:
            state.reset_error()
            if handle_empty:
                handle_empty(response)
            if mode == "drain" and saw_success:
                return
            _sleep_with_jitter_and_callback(
                ms=state.empty_delay_ms,
                reason="empty",
                response=response,
                source="backoff",
                handle_sleep=handle_sleep,
            )
            state.bump_empty()
            continue

        if status == 429:
            body = parse_response_json(response)
            wait_seconds, source = compute_wait_seconds(
                response.headers,
                body,
                fallback_seconds=_fallback_error_wait_seconds(state.error_delay_ms),
            )
            if handle_rate_limited:
                handle_rate_limited(response, wait_seconds, source)
            if source == "backoff":
                _sleep_with_jitter_and_callback(
                    ms=state.error_delay_ms,
                    reason="rate_limited",
                    response=response,
                    source=source,
                    handle_sleep=handle_sleep,
                )
                state.bump_error()
                continue
            _sleep_with_callback(
                seconds=wait_seconds,
                reason="rate_limited",
                response=response,
                source=source,
                handle_sleep=handle_sleep,
            )
            state.reset_error()
            continue

        if status in TRANSIENT_STATUS_CODES:
            if handle_transient_error:
                handle_transient_error(response)
            _sleep_with_jitter_and_callback(
                ms=state.error_delay_ms,
                reason="transient_response",
                response=response,
                source="backoff",
                handle_sleep=handle_sleep,
            )
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
