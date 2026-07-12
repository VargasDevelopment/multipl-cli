#!/usr/bin/env python3
"""Ratchet checked-in maintainability debt without changing source formatting."""

from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
import tokenize
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from urllib.parse import unquote, urlsplit

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.11 is required by this project.
    import tomli as tomllib


DEFAULT_IGNORED_DIRS = {".git", ".pytest_cache", ".ruff_cache", "__pycache__", "build", "dist"}
MARKDOWN_LINK = re.compile(r"!?(?:\[[^\]]*\])\(([^)]+)\)")
REFERENCE_LINK = re.compile(r"^\s*\[[^\]]+\]:\s*(?:<([^>]+)>|(\S+))")


@dataclass(frozen=True)
class HealthConfig:
    production_roots: tuple[str, ...]
    test_root: str
    generated_client: str
    baseline: str
    production_line_limit: int
    test_line_limit: int
    sanctioned_cli_boundaries: frozenset[str]
    protected_line_limits: tuple[tuple[str, int], ...] = ()


def load_config(root: Path) -> HealthConfig:
    with (root / "pyproject.toml").open("rb") as handle:
        tool_config = tomllib.load(handle).get("tool", {}).get("code_health", {})
    return HealthConfig(
        production_roots=tuple(tool_config.get("production_roots", ["src", "scripts"])),
        test_root=tool_config.get("test_root", "tests"),
        generated_client=tool_config.get("generated_client", "src/multipl_cli/_client"),
        baseline=tool_config.get("baseline", "code_health/baseline.json"),
        production_line_limit=tool_config.get("production_line_limit", 700),
        test_line_limit=tool_config.get("test_line_limit", 1000),
        sanctioned_cli_boundaries=frozenset(tool_config.get("sanctioned_cli_boundaries", [])),
        protected_line_limits=tuple(
            sorted(
                (str(path), int(limit))
                for path, limit in tool_config.get("protected_line_limits", {}).items()
            )
        ),
    )


def repository_files(root: Path) -> list[Path]:
    """Return tracked plus non-ignored untracked files, with a non-git fallback for tests."""
    command = ["git", "ls-files", "--cached", "--others", "--exclude-standard"]
    result = subprocess.run(command, cwd=root, capture_output=True, text=True, check=False)
    if result.returncode == 0:
        return sorted(root / name for name in result.stdout.splitlines())

    files = []
    for path in root.rglob("*"):
        if path.is_file() and not any(part in DEFAULT_IGNORED_DIRS for part in path.parts):
            files.append(path)
    return sorted(files)


def relative(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def is_under(path: str, directory: str) -> bool:
    return path == directory or path.startswith(f"{directory.rstrip('/')}/")


def source_groups(root: Path, config: HealthConfig) -> tuple[list[Path], list[Path], list[Path], list[Path]]:
    all_files = repository_files(root)
    python_files = [path for path in all_files if path.suffix == ".py"]
    generated = [path for path in python_files if is_under(relative(root, path), config.generated_client)]
    production = [
        path
        for path in python_files
        if any(is_under(relative(root, path), item) for item in config.production_roots)
        and path not in generated
    ]
    tests = [path for path in python_files if is_under(relative(root, path), config.test_root)]
    return all_files, production, tests, generated


def dotted_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = dotted_name(node.value)
        return f"{prefix}.{node.attr}" if prefix else None
    return None


def is_mutable_default(node: ast.AST) -> bool:
    return isinstance(node, (ast.Dict, ast.List, ast.Set, ast.DictComp, ast.ListComp, ast.SetComp))


def handler_is_swallowed(handler: ast.ExceptHandler) -> bool:
    return bool(handler.body) and all(
        isinstance(statement, ast.Pass)
        or (
            isinstance(statement, ast.Expr)
            and isinstance(statement.value, ast.Constant)
            and statement.value.value is Ellipsis
        )
        for statement in handler.body
    )


def has_shell_true(call: ast.Call) -> bool:
    return any(
        keyword.arg == "shell" and isinstance(keyword.value, ast.Constant) and keyword.value.value is True
        for keyword in call.keywords
    )


def comment_metrics(source: str) -> tuple[int, int]:
    type_ignores = 0
    noqa_ruff = 0
    for token in tokenize.generate_tokens(StringIO(source).readline):
        if token.type != tokenize.COMMENT:
            continue
        comment = token.string.lower()
        type_ignores += int("type: ignore" in comment)
        noqa_ruff += int("noqa" in comment or "ruff: noqa" in comment)
    return type_ignores, noqa_ruff


def python_metrics(path: Path, source: str, is_test: bool, sanctioned: bool) -> dict[str, int]:
    metrics = {
        "type_ignores": 0,
        "noqa_or_ruff_suppressions": 0,
        "any_uses": 0,
        "casts": 0,
        "skipped_tests": 0,
        "only_tests": 0,
        "bare_excepts": 0,
        "swallowed_except_handlers": 0,
        "mutable_default_arguments": 0,
        "direct_sys_exit_calls": 0,
        "direct_os_exit_calls": 0,
        "subprocess_shell_true_calls": 0,
        "unsanctioned_process_boundary_calls": 0,
    }
    metrics["type_ignores"], metrics["noqa_or_ruff_suppressions"] = comment_metrics(source)
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as error:
        raise ValueError(f"Cannot parse {path}: {error.msg} at line {error.lineno}") from error

    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id == "Any":
            metrics["any_uses"] += 1
        elif (
            isinstance(node, ast.Attribute)
            and node.attr == "Any"
            and dotted_name(node.value) in {"typing", "typing_extensions"}
        ):
            metrics["any_uses"] += 1

        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            metrics["mutable_default_arguments"] += sum(
                is_mutable_default(default) for default in (*node.args.defaults, *node.args.kw_defaults) if default
            )
            if is_test:
                for decorator in node.decorator_list:
                    name = dotted_name(decorator.func) if isinstance(decorator, ast.Call) else dotted_name(decorator)
                    if name in {"pytest.mark.skip", "pytest.mark.skipif", "unittest.skip"}:
                        metrics["skipped_tests"] += 1
                    if name and name.endswith(".only"):
                        metrics["only_tests"] += 1

        if isinstance(node, ast.ExceptHandler):
            metrics["bare_excepts"] += int(node.type is None)
            metrics["swallowed_except_handlers"] += int(handler_is_swallowed(node))

        if not isinstance(node, ast.Call):
            continue
        name = dotted_name(node.func)
        if name in {"cast", "typing.cast", "typing_extensions.cast"}:
            metrics["casts"] += 1
        if is_test and name == "pytest.skip":
            metrics["skipped_tests"] += 1
        if is_test and name and name.endswith(".only"):
            metrics["only_tests"] += 1
        if name == "sys.exit":
            metrics["direct_sys_exit_calls"] += 1
            metrics["unsanctioned_process_boundary_calls"] += int(not sanctioned)
        elif name == "os._exit":
            metrics["direct_os_exit_calls"] += 1
            metrics["unsanctioned_process_boundary_calls"] += int(not sanctioned)
        elif name and name.startswith("subprocess.") and has_shell_true(node):
            metrics["subprocess_shell_true_calls"] += 1
            metrics["unsanctioned_process_boundary_calls"] += int(not sanctioned)
    return metrics


def broken_markdown_links(root: Path, markdown_files: list[Path]) -> list[str]:
    broken = []
    for path in markdown_files:
        in_fence = False
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if line.lstrip().startswith(("```", "~~~")):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            destinations = [match.group(1) for match in MARKDOWN_LINK.finditer(line)]
            reference = REFERENCE_LINK.match(line)
            if reference:
                destinations.append(reference.group(1) or reference.group(2))
            for destination in destinations:
                target = destination.strip().split(maxsplit=1)[0].strip("<>")
                parsed = urlsplit(target)
                if not target or parsed.scheme or target.startswith(("/", "#")):
                    continue
                target_path = unquote(parsed.path)
                if target_path and not (path.parent / target_path).exists():
                    broken.append(f"{relative(root, path)}:{line_number}:{target}")
    return sorted(broken)


def duplicate_command_modules(root: Path, python_files: list[Path]) -> list[str]:
    command_root = "src/multipl_cli/commands"
    modules: dict[str, list[str]] = {}
    for path in python_files:
        name = relative(root, path)
        if not is_under(name, command_root):
            continue
        suffix = name.removeprefix(f"{command_root}/")
        if suffix == "__init__.py":
            continue
        if suffix.endswith("/__init__.py"):
            module = suffix.removesuffix("/__init__.py")
        else:
            module = suffix.removesuffix(".py")
        modules.setdefault(module, []).append(name)
    return sorted(module for module, paths in modules.items() if len(paths) > 1)


def oversized_files(root: Path, paths: list[Path], limit: int) -> dict[str, int]:
    return {
        relative(root, path): len(path.read_text(encoding="utf-8").splitlines())
        for path in paths
        if len(path.read_text(encoding="utf-8").splitlines()) > limit
    }


def protected_line_regressions(root: Path, config: HealthConfig) -> list[str]:
    regressions = []
    for name, limit in config.protected_line_limits:
        path = root / name
        if not path.is_file():
            continue
        lines = len(path.read_text(encoding="utf-8").splitlines())
        if lines > limit:
            regressions.append(f"protected line ceiling {name}: {lines} (limit {limit})")
    return regressions


def collect_snapshot(root: Path, config: HealthConfig) -> tuple[dict[str, object], dict[str, list[str]]]:
    all_files, production, tests, generated = source_groups(root, config)
    metric_names = [
        "type_ignores",
        "noqa_or_ruff_suppressions",
        "any_uses",
        "casts",
        "skipped_tests",
        "only_tests",
        "bare_excepts",
        "swallowed_except_handlers",
        "mutable_default_arguments",
        "direct_sys_exit_calls",
        "direct_os_exit_calls",
        "subprocess_shell_true_calls",
        "unsanctioned_process_boundary_calls",
    ]
    metrics = dict.fromkeys(metric_names, 0)
    for path in production:
        source = path.read_text(encoding="utf-8")
        values = python_metrics(path, source, is_test=False, sanctioned=relative(root, path) in config.sanctioned_cli_boundaries)
        for name, count in values.items():
            metrics[name] += count
    for path in tests:
        values = python_metrics(path, path.read_text(encoding="utf-8"), is_test=True, sanctioned=False)
        for name in ("skipped_tests", "only_tests"):
            metrics[name] += values[name]

    markdown_files = [path for path in all_files if path.suffix.lower() == ".md"]
    details = {
        "broken_relative_markdown_links": broken_markdown_links(root, markdown_files),
        "duplicate_command_modules": duplicate_command_modules(root, production + tests + generated),
        "generated_client_files": [relative(root, path) for path in generated],
    }
    metrics.update(
        broken_relative_markdown_links=len(details["broken_relative_markdown_links"]),
        duplicate_command_modules=len(details["duplicate_command_modules"]),
        giant_production_files=len(oversized_files(root, production, config.production_line_limit)),
        giant_test_files=len(oversized_files(root, tests, config.test_line_limit)),
        generated_client_python_files=len(generated),
    )
    snapshot = {
        "schema_version": 1,
        "metrics": dict(sorted(metrics.items())),
        "oversized_files": {
            "production": oversized_files(root, production, config.production_line_limit),
            "tests": oversized_files(root, tests, config.test_line_limit),
        },
    }
    return snapshot, details


def metric_status(current: int, baseline: int) -> str:
    if current > baseline:
        return "REGRESSED"
    if current < baseline:
        return "IMPROVED"
    return "UNCHANGED"


def compare(snapshot: dict[str, object], baseline: dict[str, object]) -> tuple[list[str], list[str]]:
    messages = []
    regressions = []
    names = sorted(set(snapshot["metrics"]) | set(baseline.get("metrics", {})))
    for name in names:
        current = snapshot["metrics"].get(name, 0)
        previous = baseline.get("metrics", {}).get(name, 0)
        status = metric_status(current, previous)
        messages.append(f"{status:9} {name}: {current} (baseline {previous})")
        if status == "REGRESSED":
            regressions.append(f"{name}: {previous} -> {current}")

    for group in ("production", "tests"):
        current_files = snapshot["oversized_files"][group]
        baseline_files = baseline.get("oversized_files", {}).get(group, {})
        for path in sorted(set(current_files) | set(baseline_files)):
            current = current_files.get(path)
            previous = baseline_files.get(path)
            if current is None:
                status = "IMPROVED"
                detail = f"{previous} -> within ceiling"
            elif previous is None:
                status = "REGRESSED"
                detail = f"new oversized file ({current} lines)"
            else:
                status = metric_status(current, previous)
                detail = f"{current} (baseline {previous})"
            messages.append(f"{status:9} {group}_oversized {path}: {detail}")
            if status == "REGRESSED":
                regressions.append(f"{group} oversized {path}: {detail}")
    return messages, regressions


def read_baseline(path: Path) -> dict[str, object]:
    try:
        baseline = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ValueError(f"Baseline not found: {path}. Run with --update to create it.") from error
    if baseline.get("schema_version") != 1:
        raise ValueError(f"Unsupported baseline schema in {path}")
    return baseline


def write_baseline(path: Path, snapshot: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--baseline", type=Path, help="Override the baseline path relative to --root.")
    parser.add_argument("--update", action="store_true", help="Write the current measurements as the baseline.")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    config = load_config(root)
    baseline_path = (root / (args.baseline or Path(config.baseline))).resolve()
    try:
        snapshot, details = collect_snapshot(root, config)
        if args.update:
            write_baseline(baseline_path, snapshot)
            print(f"UPDATED {relative(root, baseline_path)}")
            return 0
        baseline = read_baseline(baseline_path)
    except ValueError as error:
        print(f"code health: {error}", file=sys.stderr)
        return 2

    messages, regressions = compare(snapshot, baseline)
    protected_regressions = protected_line_regressions(root, config)
    regressions.extend(protected_regressions)
    print(f"Generated client excluded from production debt: {config.generated_client} ({len(details['generated_client_files'])} files)")
    for message in messages:
        print(message)
    for regression in protected_regressions:
        print(f"REGRESSED  {regression}")
    for name in ("broken_relative_markdown_links", "duplicate_command_modules"):
        for item in details[name]:
            print(f"DETAIL    {name}: {item}")
    if regressions:
        print("code health regressed:", file=sys.stderr)
        for regression in regressions:
            print(f"  {regression}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
