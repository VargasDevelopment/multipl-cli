from __future__ import annotations

from datetime import datetime, timedelta, timezone

from multipl_cli.polling import compute_wait_seconds, parse_retry_after


def test_parse_retry_after_seconds_value() -> None:
    wait = parse_retry_after({"Retry-After": "12"})
    assert wait == 12


def test_parse_retry_after_http_date_value() -> None:
    now = datetime(2026, 2, 12, 0, 0, 0, tzinfo=timezone.utc)
    future = now + timedelta(seconds=30)
    wait = parse_retry_after({"Retry-After": future.strftime("%a, %d %b %Y %H:%M:%S GMT")}, now=now)
    assert wait == 30


def test_parse_retry_after_clamps_negative_date_to_zero() -> None:
    now = datetime(2026, 2, 12, 0, 0, 20, tzinfo=timezone.utc)
    past = now - timedelta(seconds=10)
    wait = parse_retry_after({"Retry-After": past.strftime("%a, %d %b %Y %H:%M:%S GMT")}, now=now)
    assert wait == 0


def test_compute_wait_seconds_uses_header_before_body() -> None:
    wait, source = compute_wait_seconds(
        {"Retry-After": "9"},
        {"retryAfterSeconds": 44},
        fallback_seconds=2,
    )
    assert wait == 9
    assert source == "retry-after-header"


def test_compute_wait_seconds_uses_body_before_backoff() -> None:
    wait, source = compute_wait_seconds(
        {},
        {"retryAfterSeconds": 17},
        fallback_seconds=3,
    )
    assert wait == 17
    assert source == "retry-after-seconds-body"


def test_compute_wait_seconds_uses_backoff_fallback() -> None:
    wait, source = compute_wait_seconds(
        {},
        {},
        fallback_seconds=5,
    )
    assert wait == 5
    assert source == "backoff"
