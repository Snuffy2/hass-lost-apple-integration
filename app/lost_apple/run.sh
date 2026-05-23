#!/usr/bin/env sh
set -eu

: "${LOST_APPLE_DB:=/data/lost_apple.sqlite3}"

if [ -z "${LOST_APPLE_PAIRING_TOKEN:-}" ]; then
  GENERATED_TOKEN="$(python3 - <<'PY'
import secrets
print(secrets.token_urlsafe(32))
PY
)"
  export LOST_APPLE_PAIRING_TOKEN="${GENERATED_TOKEN}"
fi

if [ -z "${LOST_APPLE_PAIRING_TOKEN}" ]; then
  printf 'LOST_APPLE_PAIRING_TOKEN is required but was not set.\n' >&2
  exit 1
fi

export LOST_APPLE_DB
export LOST_APPLE_PAIRING_TOKEN

python -m lost_apple_app
