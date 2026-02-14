from __future__ import annotations

import json
import re
import uuid
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import httpx
import typer
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError
from rich.table import Table

from multipl_cli._client.api.jobs.get_v1_jobs import sync_detailed as list_lane_jobs
from multipl_cli._client.api.jobs.get_v_1_jobs_job_id import sync_detailed as get_job
from multipl_cli._client.api.jobs.get_v_1_jobs_job_id_preview import (
    sync_detailed as get_job_preview,
)
from multipl_cli._client.api.jobs.get_v_1_jobs_job_id_stages import (
    sync_detailed as get_job_stages,
)
from multipl_cli._client.api.jobs.post_v_1_jobs_job_id_review import (
    sync_detailed as post_job_review,
)
from multipl_cli._client.api.training.post_v1_training_validate_job import (
    sync_detailed as training_validate_job,
)
from multipl_cli._client.api.public.get_v1_public_jobs import sync_detailed as list_public_jobs
from multipl_cli._client.api.public.get_v_1_public_jobs_job_id import (
    sync_detailed as get_public_job,
)
from multipl_cli._client.api.templates.get_v1_templates_id import (
    sync_detailed as get_template_by_id,
)
from multipl_cli._client.api.training.get_v1_training_templates_id import (
    sync_detailed as get_training_template_by_id,
)
from multipl_cli._client.models.get_v1_jobs_lane import GetV1JobsLane
from multipl_cli._client.models.get_v1_templates_id_response_200 import (
    GetV1TemplatesIdResponse200,
)
from multipl_cli._client.models.post_v1_jobs_body import PostV1JobsBody
from multipl_cli._client.models.post_v1_jobs_body_input import PostV1JobsBodyInput
from multipl_cli._client.models.post_v1_jobs_body_stages_item import PostV1JobsBodyStagesItem
from multipl_cli._client.models.post_v1_jobs_body_stages_item_input import (
    PostV1JobsBodyStagesItemInput,
)
from multipl_cli._client.models.post_v1_jobs_job_id_review_body import (
    PostV1JobsJobIdReviewBody,
)
from multipl_cli._client.models.post_v1_jobs_job_id_review_body_decision import (
    PostV1JobsJobIdReviewBodyDecision,
)
from multipl_cli._client.models.post_v1_training_validate_job_body import (
    PostV1TrainingValidateJobBody,
)
from multipl_cli._client.types import UNSET
from multipl_cli.app_state import AppState
from multipl_cli.console import console
from multipl_cli.openapi_client import build_client, ensure_client_available
from multipl_cli.polling import extract_retry_after_seconds, sleep_with_jitter
from multipl_cli.x402.flow import PaymentFlowError, PaymentRequiredError, request_with_x402
from multipl_cli.x402.payer_cdp import CdpPayer
from multipl_cli.x402.payer_local_key import LocalKeyPayer
from multipl_cli.x402.payer_manual import ManualPayer
from multipl_cli.x402.proof import ProofError, load_proof_from_file, parse_proof_value

app = typer.Typer(no_args_is_help=True)

CREATE_JOB_REQUEST_HINT_KEYS = {
    "stages",
    "taskType",
    "payoutCents",
    "deadlineSeconds",
    "jobTtlSeconds",
    "requestedModel",
    "estimatedTokens",
}
PLACEHOLDER_RE = re.compile(r"{{\s*([A-Za-z_][A-Za-z0-9_]*)\s*}}")
INTEGER_RE = re.compile(r"^-?\d+$")
NUMBER_RE = re.compile(r"^-?\d+(\.\d+)?$")


def _load_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text())
    except Exception as exc:
        raise typer.BadParameter(f"Invalid JSON file: {exc}") from exc
    if not isinstance(data, dict):
        raise typer.BadParameter("JSON must be an object")
    return data


def _format_preview_blob(value: Any, max_len: int = 4000) -> str:
    if value is None:
        text = "null"
    elif isinstance(value, str):
        text = value
    else:
        try:
            text = json.dumps(value, indent=2, sort_keys=True)
        except TypeError:
            text = str(value)
    if len(text) > max_len:
        return f"{text[:max_len]}... (truncated; use --json or --out)"
    return text


def _parse_response_json(response) -> Any | None:
    try:
        return json.loads(response.content.decode("utf-8"))
    except Exception:
        return None


def _looks_like_create_job_request(payload: dict[str, Any]) -> bool:
    return any(key in payload for key in CREATE_JOB_REQUEST_HINT_KEYS)


def _apply_create_job_overrides(
    request_payload: dict[str, Any],
    *,
    task_type: str | None,
    acceptance_payload: dict[str, Any] | None,
    requested_model: str | None,
    estimated_tokens: int | None,
    deadline_seconds: int | None,
    payout_cents: int | None,
    job_ttl_seconds: int | None,
    json_output: bool,
) -> None:
    if task_type is not None:
        existing_task_type = request_payload.get("taskType")
        if (
            isinstance(existing_task_type, str)
            and existing_task_type.strip()
            and existing_task_type != task_type
            and not json_output
        ):
            console.print("[yellow]Overriding file taskType with --task-type.[/yellow]")
        request_payload["taskType"] = task_type

    if acceptance_payload is not None:
        request_payload["acceptance"] = acceptance_payload
    if requested_model is not None:
        request_payload["requestedModel"] = requested_model
    if estimated_tokens is not None:
        request_payload["estimatedTokens"] = estimated_tokens
    if deadline_seconds is not None:
        request_payload["deadlineSeconds"] = deadline_seconds
    if payout_cents is not None:
        request_payload["payoutCents"] = payout_cents
    if job_ttl_seconds is not None:
        request_payload["jobTtlSeconds"] = job_ttl_seconds


def _parse_key_value_flag(raw: str, *, flag_name: str) -> tuple[str, str]:
    key, sep, value = raw.partition("=")
    if not sep:
        raise typer.BadParameter(f"Invalid {flag_name} value '{raw}'. Expected KEY=VALUE.")
    key = key.strip()
    if not key:
        raise typer.BadParameter(f"Invalid {flag_name} value '{raw}'. Key cannot be empty.")
    return key, value


def _collect_template_input_keys(
    string_assignments: list[str],
    json_assignments: list[str],
) -> set[str]:
    keys: set[str] = set()
    for raw in string_assignments:
        key, _ = _parse_key_value_flag(raw, flag_name="--set")
        keys.add(key)
    for raw in json_assignments:
        key, _ = _parse_key_value_flag(raw, flag_name="--set-json")
        keys.add(key)
    return keys


def _schema_prefers_exclusive_issue_reference(schema: dict[str, Any]) -> bool:
    one_of = schema.get("oneOf")
    if not isinstance(one_of, list):
        return False

    required_sets: set[frozenset[str]] = set()
    for candidate in one_of:
        if not isinstance(candidate, dict):
            continue
        required = candidate.get("required")
        if not isinstance(required, list):
            continue
        required_sets.add(frozenset(str(value) for value in required))

    return frozenset({"issueNumber"}) in required_sets and frozenset({"issueUrl"}) in required_sets


def parse_github_issue_url(url: str) -> tuple[str, int]:
    original = url.strip()
    if not original:
        raise ValueError("Invalid GitHub issue URL: \nExpected: https://github.com/OWNER/REPO/issues/123")

    candidate = original
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", candidate):
        candidate = f"https://{candidate}"

    parsed = urlsplit(candidate)
    host = parsed.netloc.lower()
    if host != "github.com":
        raise ValueError(
            f"Invalid GitHub issue URL: {original}\n"
            "Expected: https://github.com/OWNER/REPO/issues/123"
        )

    segments = [segment for segment in parsed.path.split("/") if segment]
    if len(segments) != 4:
        raise ValueError(
            f"Invalid GitHub issue URL: {original}\n"
            "Expected: https://github.com/OWNER/REPO/issues/123"
        )

    owner, repo, kind, number = segments
    if kind != "issues":
        if kind == "pull":
            raise ValueError(
                f"Invalid GitHub issue URL: {original}\n"
                "Pull request URLs are not supported. "
                "Expected: https://github.com/OWNER/REPO/issues/123"
            )
        raise ValueError(
            f"Invalid GitHub issue URL: {original}\n"
            "Expected: https://github.com/OWNER/REPO/issues/123"
        )

    if not number.isdigit() or int(number) <= 0:
        raise ValueError(
            f"Invalid GitHub issue URL: {original}\n"
            "Expected: https://github.com/OWNER/REPO/issues/123"
        )

    return f"{owner}/{repo}", int(number)


def _parse_template_input_flags(
    string_assignments: list[str],
    json_assignments: list[str],
    *,
    schema: dict[str, Any],
) -> dict[str, Any]:
    def coerce_scalar_value(key: str, value: str) -> Any:
        schema_type = _resolve_schema_property_type(schema, key)
        if schema_type == "integer" and INTEGER_RE.fullmatch(value):
            return int(value)
        if schema_type == "number" and NUMBER_RE.fullmatch(value):
            return float(value)
        if schema_type == "boolean":
            normalized = value.lower()
            if normalized == "true":
                return True
            if normalized == "false":
                return False
        return value

    payload: dict[str, Any] = {}
    for raw in string_assignments:
        key, value = _parse_key_value_flag(raw, flag_name="--set")
        if key in payload:
            raise typer.BadParameter(f"Duplicate template input key '{key}'.")
        payload[key] = coerce_scalar_value(key, value)

    for raw in json_assignments:
        key, value = _parse_key_value_flag(raw, flag_name="--set-json")
        if key in payload:
            raise typer.BadParameter(f"Duplicate template input key '{key}'.")
        try:
            payload[key] = json.loads(value)
        except json.JSONDecodeError as exc:
            raise typer.BadParameter(
                f"Invalid JSON for --set-json {key}: {exc.msg} (at char {exc.pos})."
            ) from exc

    return payload


def _resolve_schema_property_type(schema: dict[str, Any], key: str) -> str | None:
    properties = schema.get("properties")
    if not isinstance(properties, dict):
        return None
    property_schema = properties.get(key)
    if not isinstance(property_schema, dict):
        return None
    property_type = property_schema.get("type")
    if isinstance(property_type, str):
        return property_type
    if (
        isinstance(property_type, list)
        and len(property_type) == 1
        and isinstance(property_type[0], str)
    ):
        return property_type[0]
    return None


def _format_validation_path(path: Any) -> str:
    if not path:
        return "(root)"
    tokens = [str(part) for part in path]
    return ".".join(tokens)


def _format_validation_error(error: ValidationError) -> list[str]:
    lines = [f"{_format_validation_path(error.path)}: {error.message}"]
    for sub_error in error.context:
        lines.append(f"{_format_validation_path(sub_error.path)}: {sub_error.message}")
    return lines


def _validate_template_input(input_payload: dict[str, Any], schema: dict[str, Any]) -> None:
    def collect_scalar_type_hints(error: ValidationError) -> list[str]:
        hints: list[str] = []
        if error.validator == "type":
            field_name = str(error.path[0]) if error.path else None
            expected_type = error.validator_value
            expected_type_name = (
                expected_type
                if isinstance(expected_type, str)
                else expected_type[0]
                if isinstance(expected_type, list) and len(expected_type) == 1
                else None
            )
            if field_name and expected_type_name in {"integer", "number", "boolean"}:
                hints.append(
                    f"Tip for '{field_name}': pass exact typing via --set-json "
                    f"{field_name}={json.dumps(input_payload.get(field_name))}"
                )
        for sub_error in error.context:
            hints.extend(collect_scalar_type_hints(sub_error))
        return hints

    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(input_payload), key=lambda err: tuple(str(part) for part in err.path))
    if not errors:
        return

    details: list[str] = []
    for error in errors:
        details.extend(_format_validation_error(error))
    hint_lines = sorted(set(hint for error in errors for hint in collect_scalar_type_hints(error)))
    detail_lines = "\n".join(f"  - {line}" for line in details)
    if hint_lines:
        hints = "\n".join(f"  - {line}" for line in hint_lines)
        raise typer.BadParameter(f"Template input validation failed:\n{detail_lines}\n{hints}")
    raise typer.BadParameter(f"Template input validation failed:\n{detail_lines}")


def _value_to_prompt_string(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True)
    return str(value)


def _render_prompt_template(prompt_template: str, template_input: dict[str, Any], *, stage_index: int) -> str:
    missing_keys: set[str] = set()

    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in template_input:
            missing_keys.add(key)
            return match.group(0)
        return _value_to_prompt_string(template_input[key])

    rendered = PLACEHOLDER_RE.sub(replace, prompt_template)
    if missing_keys:
        missing = ", ".join(sorted(missing_keys))
        raise typer.BadParameter(
            f"Template stage {stage_index} is missing placeholder values for: {missing}."
        )
    return rendered


def _parse_stage_payout_mappings(values: list[str]) -> dict[int, int]:
    payouts: dict[int, int] = {}
    for raw in values:
        stage_str, payout_str = _parse_key_value_flag(raw, flag_name="--stage-payout-cents")
        try:
            stage_index = int(stage_str)
        except ValueError as exc:
            raise typer.BadParameter(
                f"Invalid stage index '{stage_str}' in --stage-payout-cents '{raw}'."
            ) from exc
        if stage_index < 1:
            raise typer.BadParameter(
                f"Invalid stage index '{stage_index}' in --stage-payout-cents '{raw}'. "
                "Stage indices are 1-indexed."
            )

        try:
            payout_cents = int(payout_str)
        except ValueError as exc:
            raise typer.BadParameter(
                f"Invalid payout value '{payout_str}' in --stage-payout-cents '{raw}'."
            ) from exc
        if payout_cents < 0:
            raise typer.BadParameter(
                f"Invalid payout value '{payout_cents}' in --stage-payout-cents '{raw}'."
            )

        if stage_index in payouts:
            raise typer.BadParameter(
                f"Duplicate --stage-payout-cents mapping for stage {stage_index}."
            )
        payouts[stage_index] = payout_cents
    return payouts


def _multi_stage_payout_guidance(stage_count: int) -> str:
    if stage_count == 3:
        return (
            "--stage-payout-cents 1=1000 "
            "--stage-payout-cents 2=2000 "
            "--stage-payout-cents 3=2000"
        )
    return " ".join(
        f"--stage-payout-cents {stage_index}=1000"
        for stage_index in range(1, stage_count + 1)
    )


def _resolve_template_stage_payouts(
    *,
    stage_indices: list[int],
    mapped_stage_payouts: dict[int, int],
    payout_cents: int | None,
) -> dict[int, int]:
    expected = set(stage_indices)
    provided = set(mapped_stage_payouts.keys())
    unexpected = sorted(provided - expected)
    if unexpected:
        unexpected_text = ", ".join(str(stage_index) for stage_index in unexpected)
        raise typer.BadParameter(
            f"--stage-payout-cents provided unknown stage indices: {unexpected_text}."
        )

    if len(stage_indices) > 1:
        if payout_cents is not None:
            guidance = _multi_stage_payout_guidance(len(stage_indices))
            console.print("[red]Multi-stage jobs require explicit stage payouts.[/red]")
            console.print(f"You provided --payout-cents {payout_cents}.")
            console.print(f"Template stage count: {len(stage_indices)}")
            console.print("Example:")
            console.print(f"  {guidance}")
            raise typer.Exit(code=1)

        missing = [stage_index for stage_index in stage_indices if stage_index not in mapped_stage_payouts]
        if missing:
            missing_text = ", ".join(str(stage_index) for stage_index in missing)
            raise typer.BadParameter(
                f"Missing --stage-payout-cents for stage indices: {missing_text}."
            )
        return {stage_index: mapped_stage_payouts[stage_index] for stage_index in stage_indices}

    only_stage = stage_indices[0]
    if only_stage in mapped_stage_payouts:
        if payout_cents is not None and mapped_stage_payouts[only_stage] != payout_cents:
            raise typer.BadParameter(
                "Conflicting payouts: --payout-cents does not match --stage-payout-cents 1=..."
            )
        return {only_stage: mapped_stage_payouts[only_stage]}
    if payout_cents is None:
        raise typer.BadParameter(
            "Single-stage templates require --payout-cents or --stage-payout-cents 1=<cents>."
        )
    return {only_stage: payout_cents}


def _render_template_create_request(
    *,
    template: GetV1TemplatesIdResponse200,
    template_input: dict[str, Any],
    stage_payouts: dict[int, int],
) -> dict[str, Any]:
    sorted_stages = sorted(template.stages, key=lambda stage: stage.index)
    stage_models: list[PostV1JobsBodyStagesItem] = []
    for stage in sorted_stages:
        prompt = _render_prompt_template(
            stage.prompt_template,
            template_input,
            stage_index=stage.index,
        )
        stage_input_payload: dict[str, Any] = {
            **template_input,
            "prompt": prompt,
            "templateId": template.id,
            "templateStageIndex": stage.index,
            "templateStageTitle": stage.title,
        }
        stage_models.append(
            PostV1JobsBodyStagesItem(
                stage_id=f"stage_{stage.index}",
                stage_index=stage.index,
                name=stage.title,
                task_type=stage.task_type_id,
                payout_cents=stage_payouts[stage.index],
                input_=PostV1JobsBodyStagesItemInput.from_dict(stage_input_payload),
            )
        )

    request_body = PostV1JobsBody(
        task_type=sorted_stages[0].task_type_id,
        input_=PostV1JobsBodyInput.from_dict(dict(template_input)),
        stages=stage_models,
    )
    return request_body.to_dict()


def _load_template_from_file(template_file: Path) -> GetV1TemplatesIdResponse200:
    payload = _load_json(template_file)
    try:
        return GetV1TemplatesIdResponse200.from_dict(payload)
    except Exception as exc:
        raise typer.BadParameter(f"Invalid template file: {exc}") from exc


def _fetch_template_from_api(
    *,
    base_url: str,
    template_id: str,
    training_mode: bool,
    poster_api_key: str | None,
) -> Any:
    if training_mode:
        client = build_client(base_url)
        response = get_training_template_by_id(id=template_id, client=client)
    else:
        if not poster_api_key:
            console.print("[red]Poster API key not configured for active profile.[/red]")
            raise typer.Exit(code=2)
        client = build_client(base_url, api_key=poster_api_key)
        response = get_template_by_id(id=template_id, client=client)

    if response.status_code == 200 and response.parsed is not None:
        return response.parsed

    if response.status_code == 404:
        console.print(f"[red]Unknown template id '{template_id}'.[/red]")
        raise typer.Exit(code=1)

    if response.status_code in {401, 403}:
        if training_mode:
            console.print(
                "[red]Training template endpoint unavailable for current base URL/profile.[/red]"
            )
        else:
            console.print("[red]Poster key required or invalid key.[/red]")
        body = _parse_response_json(response)
        if body is not None:
            console.print(body)
        raise typer.Exit(code=2)

    console.print(
        f"[red]Failed to fetch template '{template_id}' (status={response.status_code}).[/red]"
    )
    body = _parse_response_json(response)
    if body is not None:
        console.print(body)
    raise typer.Exit(code=2)


def _review_job(
    state: AppState,
    *,
    job_id: str,
    decision: PostV1JobsJobIdReviewBodyDecision,
    note: str | None,
    json_output: bool,
) -> None:
    ensure_client_available()
    profile = state.config.get_active_profile()
    if state.training_mode:
        console.print(
            "[red]`multipl job review` is unavailable in training mode. "
            "Training exercises are graded via `multipl submit send`.[/red]"
        )
        raise typer.Exit(code=1)

    if not state.training_mode and not profile.poster_api_key:
        console.print("[red]Poster API key not configured for active profile.[/red]")
        raise typer.Exit(code=2)

    client = build_client(state.base_url, api_key=profile.poster_api_key)
    body = PostV1JobsJobIdReviewBody(
        decision=decision,
        reason=note if note else UNSET,
    )
    response = post_job_review(
        client=client,
        job_id=job_id,
        body=body,
    )

    if response.status_code == 200:
        payload = response.parsed.to_dict() if response.parsed is not None else (_parse_response_json(response) or {})
        if json_output:
            console.print(payload)
            return

        job = payload.get("job") if isinstance(payload, dict) else None
        action = "accepted" if decision == PostV1JobsJobIdReviewBodyDecision.ACCEPT else "rejected"
        if isinstance(job, dict):
            state_value = job.get("state")
            if state_value is not None:
                console.print(f"Job {action}: {job.get('id', job_id)} (state={state_value})")
            else:
                console.print(f"Job {action}: {job.get('id', job_id)}")
        else:
            console.print(f"Job {action}: {job_id}")
        return

    if response.status_code in {401, 403}:
        console.print("[red]Poster key required or invalid key.[/red]")
        body_payload = _parse_response_json(response)
        if body_payload is not None:
            console.print(body_payload)
        raise typer.Exit(code=2)

    if response.status_code == 404:
        console.print("[red]Job not found.[/red]")
        raise typer.Exit(code=1)

    if response.status_code == 429:
        retry_after = extract_retry_after_seconds(
            httpx.Response(
                status_code=int(response.status_code),
                headers=response.headers,
                content=response.content,
            )
        )
        if retry_after is not None:
            console.print(f"Rate limited. Retry after {retry_after}s.")
        else:
            console.print("Rate limited.")
        raise typer.Exit(code=4)

    if response.status_code in {409, 422}:
        console.print(f"[red]Review failed (status={response.status_code}).[/red]")
        body_payload = _parse_response_json(response)
        if body_payload is not None:
            console.print(body_payload)
        raise typer.Exit(code=1)

    console.print(f"[red]Review failed (status={response.status_code}).[/red]")
    body_payload = _parse_response_json(response)
    if body_payload is not None:
        console.print(body_payload)
    raise typer.Exit(code=2)


@app.command("list")
def list_jobs(
    ctx: typer.Context,
    task_type: str | None = typer.Option(None, "--task-type", help="Filter by task type"),
    status: str | None = typer.Option(None, "--status", help="Filter by status"),
    lane: str | None = typer.Option(
        None,
        "--lane",
        help="Optional lane filter (supported value from API: verifier)",
    ),
    limit: int = typer.Option(50, "--limit", help="Max jobs to return"),
    json_output: bool = typer.Option(False, "--json", help="Output JSON"),
) -> None:
    state = ctx.obj
    if not isinstance(state, AppState):
        console.print("[red]Internal error: missing app state[/red]")
        raise typer.Exit(code=1)

    ensure_client_available()
    client = build_client(state.base_url)

    lane_enum: GetV1JobsLane | None = None
    if lane is not None:
        try:
            lane_enum = GetV1JobsLane(lane)
        except ValueError as exc:
            allowed = ", ".join(item.value for item in GetV1JobsLane)
            console.print(f"[red]Invalid lane '{lane}'. Allowed values: {allowed}.[/red]")
            raise typer.Exit(code=1) from exc

    if lane_enum is not None:
        if task_type or status:
            console.print(
                "[yellow]--task-type/--status are ignored when --lane is provided.[/yellow]"
            )
        response = list_lane_jobs(
            client=client,
            lane=lane_enum,
            limit=limit,
        )
    else:
        response = list_public_jobs(
            client=client,
            state=status or UNSET,
            task_type=task_type or UNSET,
            limit=limit,
        )

    if response.status_code == 429:
        retry_after = extract_retry_after_seconds(
            httpx.Response(
                status_code=int(response.status_code),
                headers=response.headers,
                content=response.content,
            )
        )
        if retry_after is not None:
            console.print(f"Rate limited. Retry after {retry_after}s.")
        else:
            console.print("Rate limited.")
        raise typer.Exit(code=4)

    if response.status_code != 200:
        console.print(f"[red]Failed to list jobs (status={response.status_code}).[/red]")
        body = _parse_response_json(response)
        if body is not None:
            console.print(body)
        raise typer.Exit(code=2)

    payload = _parse_response_json(response)
    if payload is None and response.parsed is not None:
        payload = response.parsed.to_dict()
    if not isinstance(payload, dict):
        console.print("[red]Invalid jobs response payload.[/red]")
        raise typer.Exit(code=2)

    if json_output:
        console.print(payload)
        return

    jobs = payload.get("jobs")
    if not isinstance(jobs, list):
        console.print("[red]Invalid jobs response payload.[/red]")
        raise typer.Exit(code=2)

    table = Table(title="Jobs")
    table.add_column("ID")
    table.add_column("Task Type")
    table.add_column("State")
    table.add_column("Payout (c)")
    table.add_column("Created")
    table.add_column("Claimed")
    table.add_column("Submitted")
    table.add_column("Completed")

    for job in jobs:
        if not isinstance(job, dict):
            continue
        table.add_row(
            str(job.get("id", "-")),
            str(job.get("taskType", "-")),
            str(job.get("state", "-")),
            str(job.get("payoutCents")) if job.get("payoutCents") is not None else "-",
            str(job.get("createdAt", "-")),
            str(job.get("claimedAt") or "-"),
            str(job.get("submittedAt") or "-"),
            str(job.get("completedAt") or "-"),
        )

    console.print(table)
    next_cursor = payload.get("nextCursor")
    if next_cursor:
        console.print(f"Next cursor: {next_cursor}")


@app.command("get")
def get_job_cmd(
    ctx: typer.Context,
    job_id: str = typer.Argument(..., help="Job ID"),
    public: bool = typer.Option(False, "--public", help="Force public job view"),
    json_output: bool = typer.Option(False, "--json", help="Output JSON"),
) -> None:
    state = ctx.obj
    if not isinstance(state, AppState):
        console.print("[red]Internal error: missing app state[/red]")
        raise typer.Exit(code=1)

    ensure_client_available()
    profile = state.config.get_active_profile()

    if state.training_mode:
        console.print(
            "[red]`multipl job get` is unavailable in training mode. "
            "Training exercises are ephemeral and not queryable via /v1/jobs.[/red]"
        )
        raise typer.Exit(code=1)

    if not public and profile.poster_api_key:
        client = build_client(state.base_url, api_key=profile.poster_api_key)
        response = get_job(client=client, job_id=job_id)
        if response.status_code == 200 and response.parsed is not None:
            console.print(response.parsed.to_dict() if json_output else response.parsed.to_dict())
            return
        if response.status_code not in {401, 403, 404}:
            console.print(f"[red]Failed to fetch job (status={response.status_code}).[/red]")
            raise typer.Exit(code=2)

    client = build_client(state.base_url)
    response = get_public_job(client=client, job_id=job_id)
    if response.status_code != 200 or response.parsed is None:
        console.print(f"[red]Failed to fetch public job (status={response.status_code}).[/red]")
        raise typer.Exit(code=2)
    console.print(response.parsed.to_dict() if json_output else response.parsed.to_dict())


@app.command("preview")
def preview_job(
    ctx: typer.Context,
    job_id: str = typer.Argument(..., help="Job ID"),
    out: Path | None = typer.Option(None, "--out", help="Write preview JSON to file"),
    json_output: bool = typer.Option(False, "--json", help="Output JSON"),
) -> None:
    state = ctx.obj
    if not isinstance(state, AppState):
        console.print("[red]Internal error: missing app state[/red]")
        raise typer.Exit(code=1)

    ensure_client_available()
    profile = state.config.get_active_profile()
    if state.training_mode:
        console.print(
            "[red]`multipl job preview` is unavailable in training mode. "
            "Training exercises are graded via `multipl submit send`.[/red]"
        )
        raise typer.Exit(code=1)

    if not state.training_mode and not profile.poster_api_key:
        console.print("[red]Poster API key not configured for active profile.[/red]")
        raise typer.Exit(code=2)

    client = build_client(state.base_url, api_key=profile.poster_api_key)
    response = get_job_preview(client=client, job_id=job_id)

    if response.status_code == 200:
        if response.parsed is not None:
            payload = response.parsed.to_dict()
        else:
            payload = _parse_response_json(response) or {}

        if out:
            try:
                out.write_text(json.dumps(payload, indent=2, sort_keys=True))
            except Exception as exc:
                console.print(f"[red]Failed to write preview: {exc}[/red]")
                raise typer.Exit(code=1) from exc

        if json_output:
            console.print(payload)
            return

        if out:
            console.print(f"[green]Wrote preview to {out}[/green]")

        if not isinstance(payload, dict):
            console.print(payload)
            return

        table = Table(title="Job Preview")
        table.add_column("Field")
        table.add_column("Value")

        if "commitmentSha256" in payload:
            table.add_row("commitmentSha256", str(payload.get("commitmentSha256")))
        if "previewJson" in payload:
            table.add_row("previewJson", _format_preview_blob(payload.get("previewJson")))
        if "acceptanceReport" in payload:
            table.add_row(
                "acceptanceReport",
                _format_preview_blob(payload.get("acceptanceReport")),
            )
        if "blocked" in payload:
            table.add_row("blocked", str(payload.get("blocked")))
        if "reason" in payload:
            table.add_row("reason", str(payload.get("reason")))

        console.print(table)
        return

    if response.status_code in {401, 403}:
        console.print("[red]Unauthorized (poster key missing/invalid).[/red]")
        body = _parse_response_json(response)
        if body is not None:
            console.print(body)
        raise typer.Exit(code=2)

    if response.status_code == 404:
        console.print("[red]Job not found or not accessible.[/red]")
        raise typer.Exit(code=2)

    if response.status_code == 429:
        retry_after = extract_retry_after_seconds(
            httpx.Response(
                status_code=int(response.status_code),
                headers=response.headers,
                content=response.content,
            )
        )
        if retry_after is not None:
            console.print(f"Rate limited. Retry after {retry_after}s.")
        else:
            console.print("Rate limited.")
        raise typer.Exit(code=4)

    if response.status_code in {409, 410, 422}:
        console.print(
            f"[red]Preview unavailable (status={response.status_code}).[/red]"
        )
        body = _parse_response_json(response)
        if body is not None:
            console.print(body)
        raise typer.Exit(code=1)

    console.print(f"[red]Failed to fetch preview (status={response.status_code}).[/red]")
    body = _parse_response_json(response)
    if body is not None:
        console.print(body)
    raise typer.Exit(code=2)


@app.command("stages")
def get_job_stages_cmd(
    ctx: typer.Context,
    job_id: str = typer.Argument(..., help="Job ID"),
    json_output: bool = typer.Option(False, "--json", help="Output JSON"),
) -> None:
    state = ctx.obj
    if not isinstance(state, AppState):
        console.print("[red]Internal error: missing app state[/red]")
        raise typer.Exit(code=1)

    ensure_client_available()
    profile = state.config.get_active_profile()
    if state.training_mode:
        console.print(
            "[red]`multipl job stages` is unavailable in training mode. "
            "Training exercises are not persisted as staged jobs.[/red]"
        )
        raise typer.Exit(code=1)

    if not state.training_mode and not profile.poster_api_key:
        console.print("[red]Poster API key not configured for active profile.[/red]")
        raise typer.Exit(code=2)

    client = build_client(state.base_url, api_key=profile.poster_api_key)
    response = get_job_stages(client=client, job_id=job_id)

    if response.status_code == 200:
        payload = response.parsed.to_dict() if response.parsed is not None else (_parse_response_json(response) or {})
        if json_output:
            console.print(payload)
            return

        if not isinstance(payload, dict):
            console.print("[red]Invalid stages response payload.[/red]")
            raise typer.Exit(code=2)
        stages = payload.get("stages")
        if not isinstance(stages, list):
            console.print("[red]Invalid stages response payload.[/red]")
            raise typer.Exit(code=2)

        console.print(f"rootJobId: {payload.get('rootJobId')}")
        table = Table(title=f"Stages for {job_id}")
        table.add_column("#")
        table.add_column("Stage")
        table.add_column("State")
        table.add_column("Visibility")
        table.add_column("Assignment")
        table.add_column("Job ID")
        table.add_column("Reserved Worker")

        for stage in stages:
            if not isinstance(stage, dict):
                continue
            table.add_row(
                str(stage.get("stageIndex", "-")),
                str(stage.get("stageId", "-")),
                str(stage.get("state", "-")),
                str(stage.get("visibility", "-")),
                str(stage.get("assignmentMode") or "-"),
                str(stage.get("jobId") or "-"),
                str(stage.get("reservedWorkerId") or "-"),
            )
        console.print(table)
        return

    if response.status_code in {401, 403}:
        console.print("[red]Unauthorized (poster key missing/invalid).[/red]")
        body = _parse_response_json(response)
        if body is not None:
            console.print(body)
        raise typer.Exit(code=2)

    if response.status_code == 404:
        console.print("[red]Job not found or not accessible.[/red]")
        raise typer.Exit(code=2)

    if response.status_code == 429:
        retry_after = extract_retry_after_seconds(
            httpx.Response(
                status_code=int(response.status_code),
                headers=response.headers,
                content=response.content,
            )
        )
        if retry_after is not None:
            console.print(f"Rate limited. Retry after {retry_after}s.")
        else:
            console.print("Rate limited.")
        raise typer.Exit(code=4)

    console.print(f"[red]Failed to fetch stages (status={response.status_code}).[/red]")
    body = _parse_response_json(response)
    if body is not None:
        console.print(body)
    raise typer.Exit(code=2)


@app.command("create")
def create_job(
    ctx: typer.Context,
    task_type: str | None = typer.Option(None, "--task-type", help="Task type override"),
    input_file: Path | None = typer.Option(
        None,
        "--input-file",
        exists=True,
        dir_okay=False,
        help="Legacy input JSON or full create request JSON",
    ),
    template: str | None = typer.Option(None, "--template", help="Template id"),
    template_file: Path | None = typer.Option(
        None,
        "--template-file",
        exists=True,
        dir_okay=False,
        help="Load template payload from local file",
    ),
    from_gh: str | None = typer.Option(
        None,
        "--from-gh",
        help="GitHub issue URL (https://github.com/OWNER/REPO/issues/123)",
    ),
    template_set: list[str] | None = typer.Option(
        None,
        "--set",
        help="Template variable mapping (KEY=VALUE)",
    ),
    template_set_json: list[str] | None = typer.Option(
        None,
        "--set-json",
        help="Template variable mapping (KEY=JSON)",
    ),
    stage_payout_cents: list[str] | None = typer.Option(
        None,
        "--stage-payout-cents",
        help='Stage payout mapping like "1=1000"',
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print create request JSON and exit"),
    request_file: bool = typer.Option(
        False,
        "--request-file",
        "--raw",
        help="Treat --input-file as full POST /v1/jobs request JSON",
    ),
    acceptance_file: Path | None = typer.Option(
        None, "--acceptance-file", exists=True, dir_okay=False
    ),
    payout_cents: int | None = typer.Option(None, "--payout-cents", help="Payout in cents"),
    requested_model: str | None = typer.Option(None, "--requested-model", help="Requested model"),
    estimated_tokens: int | None = typer.Option(None, "--estimated-tokens", help="Estimated tokens"),
    deadline_seconds: int | None = typer.Option(None, "--deadline-seconds", help="Deadline seconds"),
    job_ttl_seconds: int | None = typer.Option(None, "--job-ttl-seconds", help="Job TTL seconds"),
    idempotency_key: str | None = typer.Option(None, "--idempotency-key", help="Idempotency key"),
    wait: bool = typer.Option(False, "--wait", help="Retry on 429 with backoff"),
    max_attempts: int = typer.Option(5, "--max-attempts", help="Max attempts when --wait"),
    no_pay: bool = typer.Option(False, "--no-pay", help="Do not attempt x402 payment"),
    proof: str | None = typer.Option(None, "--proof", help="Inline JSON payment proof"),
    proof_file: Path | None = typer.Option(None, "--proof-file", help="Path to JSON proof"),
    json_output: bool = typer.Option(False, "--json", help="Output JSON"),
) -> None:
    state = ctx.obj
    if not isinstance(state, AppState):
        console.print("[red]Internal error: missing app state[/red]")
        raise typer.Exit(code=1)

    ensure_client_available()
    profile = state.config.get_active_profile()
    if not state.training_mode and not profile.poster_api_key:
        console.print("[red]Poster API key not configured for active profile.[/red]")
        raise typer.Exit(code=2)

    template_set_values = template_set or []
    template_set_json_values = template_set_json or []
    stage_payout_values = stage_payout_cents or []
    acceptance_payload = _load_json(acceptance_file) if acceptance_file else None
    template_mode = template is not None or template_file is not None

    request_payload: dict[str, Any]
    if template_mode:
        if from_gh is not None and template is None:
            console.print("[red]--from-gh requires --template.[/red]")
            raise typer.Exit(code=1)
        if request_file:
            console.print("[red]--request-file/--raw cannot be used with --template.[/red]")
            raise typer.Exit(code=1)
        if input_file is not None:
            console.print("[red]--input-file cannot be used with --template.[/red]")
            raise typer.Exit(code=1)
        if task_type is not None:
            console.print("[red]--task-type cannot be used with --template.[/red]")
            raise typer.Exit(code=1)

        if template_file is not None:
            template_payload = _load_template_from_file(template_file)
            if template is not None and template_payload.id != template:
                console.print(
                    f"[red]Template id mismatch: --template {template} != {template_payload.id} in --template-file.[/red]"
                )
                raise typer.Exit(code=1)
        else:
            if template is None:
                console.print("[red]--template is required when --template-file is not provided.[/red]")
                raise typer.Exit(code=1)
            template_payload = _fetch_template_from_api(
                base_url=state.base_url,
                template_id=template,
                training_mode=state.training_mode,
                poster_api_key=profile.poster_api_key,
            )

        if from_gh is not None:
            assigned_keys = _collect_template_input_keys(
                template_set_values,
                template_set_json_values,
            )
            conflicting_keys = sorted(assigned_keys.intersection({"repo", "issueNumber", "issueUrl"}))
            if conflicting_keys:
                conflict_text = ", ".join(conflicting_keys)
                raise typer.BadParameter(
                    f"--from-gh cannot be combined with --set/--set-json for: {conflict_text}."
                )

        template_schema = template_payload.input_schema.to_dict()
        template_input = _parse_template_input_flags(
            template_set_values,
            template_set_json_values,
            schema=template_schema,
        )
        if from_gh is not None:
            try:
                repo, issue_number = parse_github_issue_url(from_gh)
            except ValueError as exc:
                raise typer.BadParameter(str(exc)) from exc
            template_input["repo"] = repo
            template_input["issueNumber"] = issue_number
            if not _schema_prefers_exclusive_issue_reference(template_schema):
                template_input["issueUrl"] = from_gh
        _validate_template_input(template_input, template_schema)

        sorted_stages = sorted(template_payload.stages, key=lambda stage: stage.index)
        stage_indices = [stage.index for stage in sorted_stages]
        stage_payout_map = _parse_stage_payout_mappings(stage_payout_values)
        resolved_stage_payouts = _resolve_template_stage_payouts(
            stage_indices=stage_indices,
            mapped_stage_payouts=stage_payout_map,
            payout_cents=payout_cents,
        )

        request_payload = _render_template_create_request(
            template=template_payload,
            template_input=template_input,
            stage_payouts=resolved_stage_payouts,
        )
        _apply_create_job_overrides(
            request_payload,
            task_type=None,
            acceptance_payload=acceptance_payload,
            requested_model=requested_model,
            estimated_tokens=estimated_tokens,
            deadline_seconds=deadline_seconds,
            payout_cents=None,
            job_ttl_seconds=job_ttl_seconds,
            json_output=json_output,
        )
    else:
        if template_set_values or template_set_json_values or stage_payout_values:
            console.print(
                "[red]--set/--set-json/--stage-payout-cents require --template or --template-file.[/red]"
            )
            raise typer.Exit(code=1)
        if input_file is None:
            console.print("[red]--input-file is required unless --template is provided.[/red]")
            raise typer.Exit(code=1)

        input_payload = _load_json(input_file)
        full_request_mode = request_file or _looks_like_create_job_request(input_payload)
        if full_request_mode:
            request_payload = dict(input_payload)
            if "stages" in input_payload and not request_file and not json_output:
                console.print(
                    "[yellow]Detected top-level stages in --input-file; sending full create request.[/yellow]"
                )
        else:
            if task_type is None:
                console.print(
                    "[red]--task-type is required when --input-file is legacy input-only JSON.[/red]"
                )
                raise typer.Exit(code=1)
            request_payload = {
                "taskType": task_type,
                "input": input_payload,
            }

        _apply_create_job_overrides(
            request_payload,
            task_type=task_type,
            acceptance_payload=acceptance_payload,
            requested_model=requested_model,
            estimated_tokens=estimated_tokens,
            deadline_seconds=deadline_seconds,
            payout_cents=payout_cents,
            job_ttl_seconds=job_ttl_seconds,
            json_output=json_output,
        )

    task_type_in_payload = request_payload.get("taskType")
    if not isinstance(task_type_in_payload, str) or not task_type_in_payload.strip():
        console.print("[red]Create request must include taskType (file or --task-type).[/red]")
        raise typer.Exit(code=1)

    input_in_payload = request_payload.get("input")
    if not isinstance(input_in_payload, dict):
        console.print("[red]Create request must include an object input payload.[/red]")
        raise typer.Exit(code=1)

    if dry_run:
        console.print_json(data=request_payload)
        return

    if state.training_mode:
        client = build_client(state.base_url)
        response = training_validate_job(
            client=client,
            body=PostV1TrainingValidateJobBody.from_dict(request_payload),
        )
        if int(response.status_code) != 200:
            console.print(
                f"[red]Training validation failed (status={response.status_code}).[/red]"
            )
            parsed_error = _parse_response_json(response)
            if parsed_error is not None:
                console.print(parsed_error)
            raise typer.Exit(code=2)

        if response.parsed is None:
            console.print("[red]Invalid training validation response payload.[/red]")
            raise typer.Exit(code=2)

        payload = response.parsed.to_dict()
        passed = response.parsed.pass_
        diagnostics = payload.get("diagnostics", [])
        if json_output:
            console.print(payload)
        else:
            console.print("[green]Training validation: PASS[/green]" if passed else "[red]Training validation: FAIL[/red]")
            if diagnostics:
                for diagnostic in diagnostics:
                    if not isinstance(diagnostic, dict):
                        continue
                    code = diagnostic.get("code") or "diagnostic"
                    path = diagnostic.get("path")
                    message = diagnostic.get("message") or "validation issue"
                    if path:
                        console.print(f"- {code} ({path}): {message}")
                    else:
                        console.print(f"- {code}: {message}")
        if not passed:
            raise typer.Exit(code=1)
        return

    if proof and proof_file:
        console.print("[red]Use only one of --proof or --proof-file.[/red]")
        raise typer.Exit(code=1)

    manual_proof = None
    try:
        if proof_file:
            manual_proof = load_proof_from_file(proof_file)
        elif proof:
            manual_proof = parse_proof_value(proof)
    except ProofError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1) from exc

    payer_type = state.config.payer.type
    if manual_proof is not None:
        payer = ManualPayer(proof=manual_proof)
    elif payer_type == "local_key":
        payer = LocalKeyPayer()
    elif payer_type == "cdp":
        payer = CdpPayer()
    else:
        payer = ManualPayer(proof=None)

    if not idempotency_key:
        idempotency_key = str(uuid.uuid4())
        if not json_output:
            console.print(f"Generated idempotency key: {idempotency_key}")

    client = build_client(state.base_url)

    def request_fn(extra_headers: dict[str, str] | None):
        headers = {
            "authorization": f"Bearer {profile.poster_api_key}",
            "x-idempotency-key": idempotency_key,
            "Content-Type": "application/json",
        }
        if extra_headers:
            headers.update(extra_headers)
        return client.get_httpx_client().request(
            "post",
            "/v1/jobs",
            headers=headers,
            json=request_payload,
        )

    attempts = 0
    while True:
        attempts += 1
        try:
            response = request_with_x402(
                request_fn,
                payer=payer,
                allow_pay=not no_pay,
            )
        except PaymentRequiredError as exc:
            terms = exc.terms
            payload = {
                "recipient": terms.recipient,
                "amount": terms.amount,
                "asset": terms.asset,
                "network": terms.network,
                "payment_context": terms.payment_context,
                "facilitator": terms.facilitator,
                "hint": terms.hint,
            }
            if json_output:
                console.print(payload)
            else:
                console.print("[yellow]Payment required to create job.[/yellow]")
                console.print(payload)
            raise typer.Exit(code=3) from exc
        except PaymentFlowError as exc:
            console.print(f"[red]{exc}[/red]")
            raise typer.Exit(code=3) from exc

        if response.status_code == 201:
            payload = response.json()
            if json_output:
                payload["idempotency_key"] = idempotency_key
                console.print(payload)
            else:
                job = payload.get("job") if isinstance(payload, dict) else None
                if isinstance(job, dict):
                    console.print({"jobId": job.get("id"), "state": job.get("state")})
                else:
                    console.print(payload)
            return

        if response.status_code == 429:
            retry_after = extract_retry_after_seconds(response)
            if not wait or attempts >= max_attempts:
                if json_output:
                    console.print({"error": "rate_limited", "retry_after": retry_after})
                else:
                    if retry_after is not None:
                        console.print(f"Rate limited. Retry after {retry_after}s.")
                    else:
                        console.print("Rate limited.")
                raise typer.Exit(code=4)
            delay_ms = int((retry_after or 1) * 1000)
            sleep_with_jitter(delay_ms)
            continue

        console.print(f"[red]Job create failed (status={response.status_code}).[/red]")
        try:
            console.print(response.json())
        except Exception:
            pass
        raise typer.Exit(code=2)


@app.command("accept")
def accept_job(
    ctx: typer.Context,
    job_id: str = typer.Argument(..., help="Job ID"),
    note: str | None = typer.Option(None, "--note", help="Optional review note"),
    json_output: bool = typer.Option(False, "--json", help="Output JSON"),
) -> None:
    state = ctx.obj
    if not isinstance(state, AppState):
        console.print("[red]Internal error: missing app state[/red]")
        raise typer.Exit(code=1)
    _review_job(
        state,
        job_id=job_id,
        decision=PostV1JobsJobIdReviewBodyDecision.ACCEPT,
        note=note,
        json_output=json_output,
    )


@app.command("reject")
def reject_job(
    ctx: typer.Context,
    job_id: str = typer.Argument(..., help="Job ID"),
    note: str | None = typer.Option(None, "--note", help="Optional review note"),
    json_output: bool = typer.Option(False, "--json", help="Output JSON"),
) -> None:
    state = ctx.obj
    if not isinstance(state, AppState):
        console.print("[red]Internal error: missing app state[/red]")
        raise typer.Exit(code=1)
    _review_job(
        state,
        job_id=job_id,
        decision=PostV1JobsJobIdReviewBodyDecision.REJECT,
        note=note,
        json_output=json_output,
    )
