#!/usr/bin/env sh
set -eu
(set -o pipefail) 2>/dev/null && set -o pipefail

ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
OUT_DIR="$ROOT_DIR/src/multipl_cli/_client"

OPENAPI_PATH_RESOLVED=""
TMPFILE=""
cleanup() {
  if [ "$TMPFILE" != "" ] && [ -f "$TMPFILE" ]; then
    rm -f "$TMPFILE"
  fi
}
trap cleanup EXIT

if [ "${OPENAPI_PATH:-}" != "" ] && [ -f "$OPENAPI_PATH" ]; then
  OPENAPI_PATH_RESOLVED="$OPENAPI_PATH"
elif [ "${OPENAPI_URL:-}" != "" ]; then
  TMPFILE="$(mktemp -t multipl-openapi.XXXXXX.json)"
  curl -fsSL "$OPENAPI_URL" -o "$TMPFILE"
  OPENAPI_PATH_RESOLVED="$TMPFILE"
elif [ -f "$ROOT_DIR/openapi.json" ]; then
  OPENAPI_PATH_RESOLVED="$ROOT_DIR/openapi.json"
else
  echo "OpenAPI spec not found."
  echo "Provide one of:"
  echo "  - OPENAPI_PATH=/path/to/openapi.json"
  echo "  - OPENAPI_URL=https://.../openapi.json"
  echo "  - openapi.json in the repo root (${ROOT_DIR})"
  echo "If you have the private repo locally, you can set OPENAPI_PATH=../multipl/openapi.json"
  exit 1
fi

rm -rf "$OUT_DIR"

openapi-python-client generate \
  --path "$OPENAPI_PATH_RESOLVED" \
  --output-path "$OUT_DIR" \
  --meta none
