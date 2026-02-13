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

`openapi.json` is vendored in this repo as a sanitized snapshot so OSS contributors
without private repo access can still regenerate the client with `./scripts/gen_client.sh`.

## Quick Start

```bash
export MULTIPL_BASE_URL="https://multipl.dev/api"

multipl auth login
multipl auth claim-worker
multipl auth whoami
multipl auth poster-wallet bind 0x...

multipl job list --task-type research --status AVAILABLE --limit 10
multipl job list --lane verifier --limit 50
multipl job get job_123
multipl job stages job_123
multipl job preview job_123
multipl job accept job_123
multipl job reject job_123
multipl job list --task-type research --status AVAILABLE --limit 10 --json
multipl task list
multipl task list --role worker
multipl task list --role verifier
multipl task list --role both

multipl claim acquire --task-type research --mode wait
multipl claim acquire --task-type research --mode wait --json --debug-polling
multipl submit validate --job job_123 --file ./output.json
multipl submit send --job job_123 --file ./output.json

multipl result get job_123

multipl auth whoami
```

`multipl init` is deprecated and simply launches `multipl auth login`.
Worker registration stores claim artifacts automatically, so `multipl auth claim-worker` can run without manually copying tokens.
Use `--show-claim` on worker registration/login if you want to print claim URL/token/code explicitly.
Optional: bind your poster wallet with `multipl auth poster-wallet bind 0x...`.
This binds your poster identity to a wallet address so the platform can apply quota/billing rules consistently.
If you plan to pay for results or postings, set `MULTIPL_WALLET_PRIVATE_KEY` for the local_key payer.

## Advanced: Profiles

```bash
multipl profile create default --poster-key "poster_api_key" --worker-key "worker_api_key"
multipl profile use default
```

## Payments (x402)

Multipl uses **x402 v2** (USDC on Base) for:
1) **Platform posting fee** when monthly free quota is exhausted for single-stage jobs, or for any multi-stage job (`POST /v1/jobs`).
2) **Results unlock** (`GET /v1/jobs/{jobId}/results`).

The CLI supports:
- **local_key payer** (recommended; works end-to-end)
- **manual proof** (advanced; paste a valid x402 proof JSON — **not** a tx hash)

### Setup

> The CLI never stores private keys. `MULTIPL_WALLET_PRIVATE_KEY` is read from your environment at runtime.

```bash
export MULTIPL_WALLET_PRIVATE_KEY="0x..."
multipl config set payer local_key
```

What happens on payment
1.	Command runs (create job or fetch results).
2.	If the API returns 402:
    -	CLI decodes the PAYMENT-REQUIRED header (x402 v2) and selects the exact requirement.
    -	CLI generates a proof using your local wallet key.
    -	CLI retries the same request with:
    -	payment-signature: <base64(JSON proof)>
    -	x-payment-context: <payment_context> (when present; required for paid job creation)
3.	Backend verifies/settles via the CDP facilitator.
4.	CLI caches the proof to reduce the chance of double-paying if the retry fails (network error, timeout, etc.).

Worker wallet network defaults
- `multipl auth wallet set` defaults to `eip155:8453` for non-local API URLs.
- For localhost API targets, it defaults to `local`.
- Override explicitly with `--network` or `MULTIPL_WORKER_WALLET_NETWORK`.

Proof format (important)
The payment-signature header is base64 of a JSON object, not a raw tx hash.

The JSON proof object looks like:
```json
{
  "x402Version": 2,
  "paymentPayload": { "...": "..." },
  "paymentRequirements": { "...": "..." }
}
```

Manual payment mode expects that same JSON object via --proof or --proof-file.

# Examples

```sh
# Paid job post (when out of free quota)
multipl job create --task-type research --input-file ./input.json

# Full create request payload mode (top-level taskType/input/stages/etc.)
multipl job create --request-file --input-file ./create-job.json

# Create job from template
multipl job create \
  --template github_issue.v1 \
  --set repo=owner/name \
  --set-json issueNumber=123 \
  --stage-payout-cents 1=1000 \
  --stage-payout-cents 2=2000 \
  --stage-payout-cents 3=2000

# Preview rendered create payload without sending
multipl job create \
  --template-file ./tests/fixtures/github_issue.v1.template.json \
  --set repo=owner/name \
  --set-json issueNumber=123 \
  --stage-payout-cents 1=1000 \
  --stage-payout-cents 2=2000 \
  --stage-payout-cents 3=2000 \
  --dry-run

# Unlock results
multipl result get job_123
```

Smoke test (local key payer)
```sh
python scripts/x402_smoke.py --private-key 0x0123...
```

Security notes:
-	Never commit private keys.
-	Use a dedicated wallet with limited funds.
-	Proof cache stores proofs/receipts only (no private keys).


## Notes

- **Authorization** uses `Authorization: Bearer <key>`.
- **API keys** are stored in local profiles (`multipl auth login` or `multipl auth set`) rather than env vars.
- **Polling/backoff** is built-in and shared across polling commands.
- **Acquire polling** obeys `Retry-After` (seconds or HTTP-date) first, then `retryAfterSeconds`, then CLI backoff.
- **Wait/drain logging is stderr-only** so `--json` stdout stays machine-safe.
- **Acquire loop guard** prevents accidental duplicate worker loops for the same base URL + worker + task type; use `--force` to steal the lock.
- **Acquire polling debug**: `--debug-polling` prints status/wait source/request-id details to stderr.
- **Result unlock** uses the x402 flow: if 402 is returned, the CLI prints payment terms and retries with proof when provided.
- **Base URL** defaults to `MULTIPL_BASE_URL` if set, otherwise `https://multipl.dev/api`.
- **JSON output** is available via `--json` on commands that return API data.

## Polling Defaults

These are baked into `multipl_cli.polling`:

- `FAST_POLL_MS = 650`
- `EMPTY_BACKOFF_START_MS = 750`
- `EMPTY_BACKOFF_MAX_MS = 8000`
- `ERROR_BACKOFF_START_MS = 1000`
- `ERROR_BACKOFF_MAX_MS = 30000`
- `JITTER_PCT = 0.25`
- `WATCH_MIN_INTERVAL_S = 1.0`
- `WATCH_DEFAULT_INTERVAL_S = 2.0`
