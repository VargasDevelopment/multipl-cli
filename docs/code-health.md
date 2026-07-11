# Code Health Ratchet

Run the maintainability gate locally and in CI with:

```bash
python3 scripts/code_health.py
```

`hatch run health` runs the same command. The gate scans every tracked file and every
non-ignored untracked file, so new command modules are checked before they are staged.
It never formats or rewrites source.

The checked-in [baseline](../code_health/baseline.json) is a debt ceiling. Every metric is
reported as `REGRESSED`, `IMPROVED`, or `UNCHANGED`; increases fail the command. Existing
oversized files are also ratcheted individually: an existing giant may shrink but cannot grow,
and a new file over its category ceiling fails immediately. Production files are capped at 700
lines and tests at 1000 lines.

The generated OpenAPI client at `src/multipl_cli/_client` is intentionally excluded from
production-debt metrics because it is regenerated from the API schema. Its file count remains
visible in command output so the exclusion is explicit.

The process-boundary detector records direct `sys.exit`, `os._exit`, and `subprocess` calls with
`shell=True`. Such calls are only permitted in the explicit CLI-boundary allowlist in
`[tool.code_health]` in `pyproject.toml`; an unlisted call fails the gate.

After a deliberate, reviewed debt-baseline change, update the snapshot explicitly:

```bash
python3 scripts/code_health.py --update
```

Review the resulting JSON diff with the code change. Do not use `--update` to bypass a
regression.
