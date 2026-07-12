from __future__ import annotations

import subprocess
import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

_SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "code_health.py"
_SPEC = spec_from_file_location("code_health", _SCRIPT_PATH)
assert _SPEC and _SPEC.loader
code_health = module_from_spec(_SPEC)
sys.modules[_SPEC.name] = code_health
_SPEC.loader.exec_module(code_health)


def _config() -> code_health.HealthConfig:
    return code_health.HealthConfig(
        production_roots=("src", "scripts"),
        test_root="tests",
        generated_client="src/multipl_cli/_client",
        baseline="code_health/baseline.json",
        production_line_limit=3,
        test_line_limit=4,
        sanctioned_cli_boundaries=frozenset({"src/multipl_cli/main.py"}),
        protected_line_limits=(("src/multipl_cli/private_dispatch/scheduler.py", 520),),
    )


def _write(root: Path, name: str, content: str) -> Path:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def test_python_detectors_cover_all_ast_and_token_metrics(tmp_path: Path) -> None:
    source = """from typing import Any, cast
import os
import subprocess
import sys

value: Any = typing.Any  # type: ignore[attr-defined]  # noqa: E501
suppressed = 1  # ruff: noqa

def defaults(items=[], *, options={}):
    try:
        cast(str, value)
    except:
        pass
    sys.exit(1)
    os._exit(1)
    subprocess.run(["x"], shell=True)
"""
    metrics = code_health.python_metrics(tmp_path / "sample.py", source, is_test=False, sanctioned=False)

    assert metrics["type_ignores"] == 1
    assert metrics["noqa_or_ruff_suppressions"] == 2
    assert metrics["any_uses"] == 2
    assert metrics["casts"] == 1
    assert metrics["bare_excepts"] == 1
    assert metrics["swallowed_except_handlers"] == 1
    assert metrics["mutable_default_arguments"] == 2
    assert metrics["direct_sys_exit_calls"] == 1
    assert metrics["direct_os_exit_calls"] == 1
    assert metrics["subprocess_shell_true_calls"] == 1
    assert metrics["unsanctioned_process_boundary_calls"] == 3


def test_test_detectors_find_skips_and_only_calls(tmp_path: Path) -> None:
    source = """import pytest

@pytest.mark.skip
def test_decorated(): pass

def test_runtime():
    pytest.skip("later")
    scenario.only()
"""
    metrics = code_health.python_metrics(tmp_path / "test_sample.py", source, is_test=True, sanctioned=False)

    assert metrics["skipped_tests"] == 2
    assert metrics["only_tests"] == 1


def test_sanctioned_cli_boundary_keeps_direct_calls_visible_but_permitted(tmp_path: Path) -> None:
    metrics = code_health.python_metrics(
        tmp_path / "main.py", "import sys\nsys.exit(1)\n", is_test=False, sanctioned=True
    )

    assert metrics["direct_sys_exit_calls"] == 1
    assert metrics["unsanctioned_process_boundary_calls"] == 0


def test_snapshot_excludes_generated_client_and_finds_docs_and_duplicate_commands(tmp_path: Path) -> None:
    _write(
        tmp_path,
        "src/multipl_cli/main.py",
        "from typing import Any\nvalue: Any\nfirst = 1\nsecond = 2\n",
    )
    _write(tmp_path, "src/multipl_cli/_client/generated.py", "from typing import Any\nvalue: Any\n")
    _write(tmp_path, "src/multipl_cli/commands/run.py", "first = True\n")
    _write(tmp_path, "src/multipl_cli/commands/run/__init__.py", "second = True\n")
    _write(tmp_path, "README.md", "[broken](missing.md)\n[external](https://example.com)\n")

    snapshot, details = code_health.collect_snapshot(tmp_path, _config())

    assert snapshot["metrics"]["any_uses"] == 1
    assert snapshot["metrics"]["generated_client_python_files"] == 1
    assert snapshot["metrics"]["giant_production_files"] == 1
    assert snapshot["oversized_files"]["production"] == {"src/multipl_cli/main.py": 4}
    assert details["generated_client_files"] == ["src/multipl_cli/_client/generated.py"]
    assert details["broken_relative_markdown_links"] == ["README.md:1:missing.md"]
    assert details["duplicate_command_modules"] == ["run"]


def test_oversized_file_ratchet_rejects_growth_and_new_giants() -> None:
    baseline = {
        "metrics": {"giant_production_files": 1, "giant_test_files": 0},
        "oversized_files": {"production": {"src/old.py": 701}, "tests": {}},
    }
    grown = {
        "metrics": {"giant_production_files": 1, "giant_test_files": 0},
        "oversized_files": {"production": {"src/old.py": 702}, "tests": {}},
    }
    new = {
        "metrics": {"giant_production_files": 2, "giant_test_files": 0},
        "oversized_files": {"production": {"src/old.py": 701, "src/new.py": 701}, "tests": {}},
    }

    _, grown_regressions = code_health.compare(grown, baseline)
    _, new_regressions = code_health.compare(new, baseline)

    assert "production oversized src/old.py: 702 (baseline 701)" in grown_regressions
    assert "production oversized src/new.py: new oversized file (701 lines)" in new_regressions


def test_protected_dispatcher_line_ceiling_rejects_growth_without_baseline_debt(
    tmp_path: Path,
) -> None:
    _write(tmp_path, "src/multipl_cli/private_dispatch/scheduler.py", "line = 1\n" * 4)
    config = code_health.HealthConfig(
        production_roots=("src",),
        test_root="tests",
        generated_client="src/generated",
        baseline="baseline.json",
        production_line_limit=700,
        test_line_limit=1000,
        sanctioned_cli_boundaries=frozenset(),
        protected_line_limits=(("src/multipl_cli/private_dispatch/scheduler.py", 3),),
    )

    assert code_health.protected_line_regressions(tmp_path, config) == [
        "protected line ceiling src/multipl_cli/private_dispatch/scheduler.py: 4 (limit 3)"
    ]


def test_repository_scan_includes_untracked_nonignored_files(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    _write(tmp_path, "tracked.py", "tracked = True\n")
    subprocess.run(["git", "add", "tracked.py"], cwd=tmp_path, check=True)
    _write(tmp_path, "src/multipl_cli/commands/unstaged.py", "unstaged = True\n")
    _write(tmp_path, ".gitignore", "ignored.py\n")
    _write(tmp_path, "ignored.py", "ignored = True\n")

    names = {path.relative_to(tmp_path).as_posix() for path in code_health.repository_files(tmp_path)}

    assert "tracked.py" in names
    assert "src/multipl_cli/commands/unstaged.py" in names
    assert "ignored.py" not in names
