#!/usr/bin/env sh
set -eu
(set -o pipefail) 2>/dev/null && set -o pipefail

ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
OUT_DIR="$ROOT_DIR/src/multipl_cli/_client"

OPENAPI_PATH_RESOLVED=""
OPENAPI_SOURCE=""
TMPFILE=""
cleanup() {
  if [ "$TMPFILE" != "" ] && [ -f "$TMPFILE" ]; then
    rm -f "$TMPFILE"
  fi
}
trap cleanup EXIT

if [ "${OPENAPI_PATH:-}" != "" ] && [ -f "$OPENAPI_PATH" ]; then
  OPENAPI_PATH_RESOLVED="$OPENAPI_PATH"
  OPENAPI_SOURCE="OPENAPI_PATH"
elif [ "${OPENAPI_URL:-}" != "" ]; then
  TMPFILE="$(mktemp -t multipl-openapi.XXXXXX.json)"
  curl -fsSL "$OPENAPI_URL" -o "$TMPFILE"
  OPENAPI_PATH_RESOLVED="$TMPFILE"
  OPENAPI_SOURCE="OPENAPI_URL"
elif [ -f "$ROOT_DIR/openapi.json" ]; then
  OPENAPI_PATH_RESOLVED="$ROOT_DIR/openapi.json"
  OPENAPI_SOURCE="vendored openapi.json"
else
  echo "OpenAPI spec not found."
  echo "Provide one of:"
  echo "  - OPENAPI_PATH=/path/to/openapi.json"
  echo "  - OPENAPI_URL=https://.../openapi.json"
  echo "  - openapi.json in the repo root (${ROOT_DIR})"
  echo "If you have the private repo locally, you can set OPENAPI_PATH=../multipl/openapi.json"
  exit 1
fi

SPEC_SIZE_BYTES="$(wc -c < "$OPENAPI_PATH_RESOLVED" | tr -d '[:space:]')"
SPEC_SHA256=""
if command -v shasum >/dev/null 2>&1; then
  SPEC_SHA256="$(shasum -a 256 "$OPENAPI_PATH_RESOLVED" | awk '{print $1}')"
elif command -v sha256sum >/dev/null 2>&1; then
  SPEC_SHA256="$(sha256sum "$OPENAPI_PATH_RESOLVED" | awk '{print $1}')"
elif command -v openssl >/dev/null 2>&1; then
  SPEC_SHA256="$(openssl dgst -sha256 "$OPENAPI_PATH_RESOLVED" | awk '{print $NF}')"
fi

if [ "$SPEC_SHA256" != "" ]; then
  printf "OpenAPI source: %s\n" "$OPENAPI_SOURCE"
  printf "OpenAPI spec: %s (%s bytes, sha256=%s, sha256[0:8]=%s)\n" "$OPENAPI_PATH_RESOLVED" "$SPEC_SIZE_BYTES" "$SPEC_SHA256" "$(printf "%s" "$SPEC_SHA256" | cut -c1-8)"
else
  printf "OpenAPI source: %s\n" "$OPENAPI_SOURCE"
  printf "OpenAPI spec: %s (%s bytes)\n" "$OPENAPI_PATH_RESOLVED" "$SPEC_SIZE_BYTES"
fi

rm -rf "$OUT_DIR"

openapi-python-client generate \
  --path "$OPENAPI_PATH_RESOLVED" \
  --output-path "$OUT_DIR" \
  --meta none
