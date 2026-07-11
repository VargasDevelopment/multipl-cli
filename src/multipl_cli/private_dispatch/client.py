from __future__ import annotations

import httpx

from multipl_cli.private_dispatch.types import (
    Attempt,
    DispatchConfig,
    Lease,
    TaskContract,
    TaskIdentity,
    Work,
)


class PrivateApiError(RuntimeError):
    def __init__(self, operation: str, status_code: int | None = None) -> None:
        self.operation = operation
        self.status_code = status_code
        detail = f"status {status_code}" if status_code is not None else "network failure"
        super().__init__(f"Private API {operation} failed ({detail})")


def _mapping(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise PrivateApiError(f"parse {label}")
    return value


def _string(data: dict[str, object], key: str, label: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value:
        raise PrivateApiError(f"parse {label}")
    return value


def _positive_int(data: dict[str, object], key: str, label: str) -> int:
    value = data.get(key)
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise PrivateApiError(f"parse {label}")
    return value


def _identity(data: dict[str, object], label: str) -> TaskIdentity:
    return TaskIdentity(
        registry_id=_string(data, "registryId", label),
        type_id=_string(data, "typeId", label),
        version=_positive_int(data, "version", label),
    )


class PrivateClient:
    def __init__(self, config: DispatchConfig, transport: httpx.BaseTransport | None = None) -> None:
        self._client = httpx.Client(
            base_url=config.base_url,
            headers={
                "Authorization": f"Bearer {config.bearer}",
                "x-multipl-namespace": config.namespace,
                "x-multipl-lane": config.lane,
            },
            timeout=30,
            transport=transport,
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "PrivateClient":
        return self

    def __exit__(self, _exc_type, _exc, _tb) -> None:
        self.close()

    def _request(
        self,
        method: str,
        path: str,
        operation: str,
        *,
        payload: object | None = None,
        idempotency_key: str | None = None,
    ) -> httpx.Response:
        headers = {"Idempotency-Key": idempotency_key} if idempotency_key else None
        try:
            response = self._client.request(method, path, json=payload, headers=headers)
        except httpx.HTTPError as exc:
            raise PrivateApiError(operation) from exc
        if response.status_code < 200 or response.status_code >= 300:
            raise PrivateApiError(operation, response.status_code)
        return response

    def task_contracts(self) -> tuple[TaskContract, ...]:
        response = self._request("GET", "/private/v1/task-registry", "task registry")
        registry = _mapping(response.json(), "task registry")
        registry_id = _string(registry, "registryId", "task registry")
        raw_tasks = registry.get("tasks")
        if not isinstance(raw_tasks, list):
            raise PrivateApiError("parse task registry")
        contracts = []
        for raw_task in raw_tasks:
            task = _mapping(raw_task, "task registry entry")
            schema = _mapping(task.get("resultSchema"), "result schema")
            contracts.append(
                TaskContract(
                    identity=TaskIdentity(
                        registry_id=registry_id,
                        type_id=_string(task, "typeId", "task registry entry"),
                        version=_positive_int(task, "version", "task registry entry"),
                    ),
                    result_schema=schema,
                )
            )
        return tuple(contracts)

    def acquire(self, allowlist: tuple[TaskIdentity, ...], key: str) -> Attempt | None:
        response = self._request(
            "POST",
            "/private/v1/attempts/acquire-next",
            "acquire",
            payload={"taskAllowlist": [item.to_api() for item in allowlist]},
            idempotency_key=key,
        )
        if response.status_code == 204 or not response.content:
            return None
        body = _mapping(response.json(), "acquire response")
        raw_attempt = body.get("attempt")
        if raw_attempt is None:
            return None
        attempt = _mapping(raw_attempt, "attempt")
        lease = _mapping(attempt.get("lease"), "lease")
        return Attempt(
            attempt_id=_string(attempt, "id", "attempt"),
            work_id=_string(attempt, "workId", "attempt"),
            lease=Lease(
                lease_id=_string(lease, "leaseId", "lease"),
                generation=_positive_int(lease, "generation", "lease"),
                expires_at=_string(lease, "expiresAt", "lease"),
            ),
        )

    def work(self, work_id: str) -> Work:
        response = self._request("GET", f"/private/v1/work/{work_id}", "read work")
        data = _mapping(response.json(), "work")
        raw_input = _mapping(data.get("input"), "work input")
        return Work(
            work_id=_string(data, "workId", "work"),
            task=_identity(_mapping(data.get("task"), "work task"), "work task"),
            input=raw_input,
        )

    def renew(self, attempt: Attempt, key: str) -> Attempt:
        path = f"/private/v1/work/{attempt.work_id}/attempts/{attempt.attempt_id}/renew"
        response = self._request(
            "POST",
            path,
            "renew",
            payload={"lease": attempt.lease.request()},
            idempotency_key=key,
        )
        body = _mapping(response.json(), "renew response")
        raw = _mapping(body.get("attempt"), "renewed attempt")
        lease = _mapping(raw.get("lease"), "renewed lease")
        return Attempt(
            attempt_id=_string(raw, "id", "renewed attempt"),
            work_id=_string(raw, "workId", "renewed attempt"),
            lease=Lease(
                lease_id=_string(lease, "leaseId", "renewed lease"),
                generation=_positive_int(lease, "generation", "renewed lease"),
                expires_at=_string(lease, "expiresAt", "renewed lease"),
            ),
        )

    def submit(self, attempt: Attempt, payload: object, key: str) -> None:
        self._request(
            "PUT",
            f"/private/v1/work/{attempt.work_id}/result",
            "submit result",
            payload={
                "attemptId": attempt.attempt_id,
                "lease": attempt.lease.request(),
                "payload": payload,
            },
            idempotency_key=key,
        )
