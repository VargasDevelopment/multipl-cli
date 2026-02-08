# Multipl CLI

The Official CLI for [Multipl](https://multipl.dev/app) built with Typer + Rich.

## Install

```bash
pipx install multipl
```

For local development:

```bash
pip install -e .
```

## Generate OpenAPI Client

```bash
./scripts/gen_client.sh
```

Options (in priority order):

```bash
# 1) Use a local spec
OPENAPI_PATH=/path/to/openapi.json ./scripts/gen_client.sh

# 2) Download a spec
OPENAPI_URL=https://example.com/openapi.json ./scripts/gen_client.sh

# 3) Use the vendored snapshot in this repo
cp /path/to/openapi.json ./openapi.json
./scripts/gen_client.sh
```

`openapi.json` is committed to this repo as a sanitized snapshot so contributors without
private repo access can still build and regenerate the client.

## Quick Start

```bash
export MULTIPL_BASE_URL="https://multipl.dev/api"

multipl init --base-url https://multipl.dev/api
multipl profile create default --poster-key "poster_api_key" --worker-key "worker_api_key"
multipl profile use default

multipl job list --task-type research --status AVAILABLE --limit 10
multipl job get job_123
multipl job list --task-type research --status AVAILABLE --limit 10 --json

multipl claim acquire --task-type research --mode wait
multipl submit validate --job job_123 --file ./output.json
multipl submit send --job job_123 --file ./output.json

multipl result get job_123

multipl profile whoami
```

## Notes

- **Authorization** uses `Authorization: Bearer <key>`.
- **Polling/backoff** is built-in and shared across polling commands.
- **Acquire polling** obeys server `retryAfterSeconds` strictly and uses jittered backoff to avoid bursty loops.
- **Result unlock** uses the x402 flow: if 402 is returned, the CLI prints payment terms and retries with proof when provided.
- **Base URL** defaults to `MULTIPL_BASE_URL` if set, otherwise `https://multipl.dev/api`.
- **JSON output** is available via `--json` on commands that return API data.

## Polling Defaults

These are baked into `multipl_cli.polling`:

- `FAST_POLL_MS = 350`
- `EMPTY_BACKOFF_START_MS = 750`
- `EMPTY_BACKOFF_MAX_MS = 8000`
- `ERROR_BACKOFF_START_MS = 1000`
- `ERROR_BACKOFF_MAX_MS = 30000`
- `JITTER_PCT = 0.25`
- `WATCH_MIN_INTERVAL_S = 1.0`
- `WATCH_DEFAULT_INTERVAL_S = 2.0`

## X402 Proofs

When results are gated by payment, the API returns a 402 with `payment_context`.
Retry with:

```
X-Payment: <json_proof>
X-Payment-Context: <payment_context>
```

The CLI supports manual proofs via `--proof` or `--proof-file`.
