from __future__ import annotations

import pytest
import typer

from multipl_cli.commands import job


def test_parse_stage_payout_mappings_valid() -> None:
    payouts = job._parse_stage_payout_mappings(["1=1000", "2=2000", "3=2000"])
    assert payouts == {1: 1000, 2: 2000, 3: 2000}


def test_parse_stage_payout_mappings_rejects_duplicates() -> None:
    with pytest.raises(typer.BadParameter, match="Duplicate --stage-payout-cents mapping"):
        job._parse_stage_payout_mappings(["1=1000", "1=2000"])


def test_parse_stage_payout_mappings_rejects_invalid_values() -> None:
    with pytest.raises(typer.BadParameter, match="1-indexed"):
        job._parse_stage_payout_mappings(["0=1000"])
    with pytest.raises(typer.BadParameter, match="Invalid payout value"):
        job._parse_stage_payout_mappings(["1=abc"])
    with pytest.raises(typer.BadParameter, match="Invalid stage index"):
        job._parse_stage_payout_mappings(["foo=1000"])


def test_validate_template_input_one_of_issue_number_or_issue_url() -> None:
    schema = {
        "type": "object",
        "required": ["repo"],
        "properties": {
            "repo": {"type": "string"},
            "issueNumber": {"type": "integer", "minimum": 1},
            "issueUrl": {"type": "string", "minLength": 1},
        },
        "oneOf": [{"required": ["issueNumber"]}, {"required": ["issueUrl"]}],
        "additionalProperties": False,
    }

    job._validate_template_input({"repo": "octocat/hello-world", "issueNumber": 1}, schema)

    with pytest.raises(typer.BadParameter) as exc_info:
        job._validate_template_input({"repo": "octocat/hello-world"}, schema)

    message = str(exc_info.value)
    assert "Template input validation failed" in message
    assert "issueNumber" in message
    assert "issueUrl" in message


def test_parse_template_input_flags_coerces_integer_and_boolean() -> None:
    schema = {
        "type": "object",
        "properties": {
            "issueNumber": {"type": "integer"},
            "prEnabled": {"type": "boolean"},
        },
    }
    parsed = job._parse_template_input_flags(
        ["issueNumber=123", "prEnabled=true"],
        [],
        schema=schema,
    )
    assert parsed["issueNumber"] == 123
    assert isinstance(parsed["issueNumber"], int)
    assert parsed["prEnabled"] is True


def test_validate_template_input_type_mismatch_suggests_set_json() -> None:
    schema = {
        "type": "object",
        "required": ["issueNumber"],
        "properties": {
            "issueNumber": {"type": "integer", "minimum": 1},
        },
        "additionalProperties": False,
    }
    payload = job._parse_template_input_flags(
        ["issueNumber=abc"],
        [],
        schema=schema,
    )

    with pytest.raises(typer.BadParameter) as exc_info:
        job._validate_template_input(payload, schema)

    message = str(exc_info.value)
    assert "issueNumber" in message
    assert "--set-json issueNumber=\"abc\"" in message


def test_validate_template_input_array_requires_set_json() -> None:
    schema = {
        "type": "object",
        "required": ["acceptanceChecklist"],
        "properties": {
            "acceptanceChecklist": {
                "type": "array",
                "items": {"type": "string"},
            }
        },
        "additionalProperties": False,
    }
    payload = job._parse_template_input_flags(
        ["acceptanceChecklist=[\"a\",\"b\"]"],
        [],
        schema=schema,
    )

    with pytest.raises(typer.BadParameter) as exc_info:
        job._validate_template_input(payload, schema)

    assert "--set-json acceptanceChecklist" not in str(exc_info.value)


def test_render_prompt_template_substitutes_values() -> None:
    rendered = job._render_prompt_template(
        "Plan fixes for {{repo}} issue {{issueNumber}}",
        {"repo": "octocat/hello-world", "issueNumber": 42},
        stage_index=1,
    )
    assert rendered == "Plan fixes for octocat/hello-world issue 42"


def test_render_prompt_template_missing_placeholder_raises() -> None:
    with pytest.raises(typer.BadParameter, match="missing placeholder values"):
        job._render_prompt_template(
            "Plan fixes for {{repo}} issue {{issueNumber}}",
            {"repo": "octocat/hello-world"},
            stage_index=1,
        )
