#!/bin/sh
# Start the lesson on an ephemeral port and check the preview both ways.
set -eu
cd "$(dirname "$0")/.."
AURA_BIN="${AURA_BIN:-/home/dev/code/grok-dev/aura-grok/build/aura}"
export AURA_PATH="${AURA_PATH:-/home/dev/code/grok-dev/aura-grok/lib}"
export AURA_SANDBOX=off
export AURA_PIPELINE_STRICT="${AURA_PIPELINE_STRICT:-force-soa}"
rt=$(mktemp -d)
log=$(mktemp)
export GUOGUO_RUNTIME="$rt"
export GUOGUO_PORT=0
pid=""
cleanup() {
  if [ -n "$pid" ]; then
    kill "$pid" 2>/dev/null || true
    sleep 0.2
    kill -9 "$pid" 2>/dev/null || true
    wait "$pid" 2>/dev/null || true
  fi
  rm -rf "$rt" "$log"
}
trap cleanup EXIT
"$AURA_BIN" aura/serve.aura >"$log" 2>&1 &
pid=$!
i=0
while [ ! -s "$rt/port" ]; do
  i=$((i + 1))
  if [ "$i" -gt 300 ]; then
    echo "server did not start" >&2
    cat "$log" >&2
    exit 1
  fi
  if ! kill -0 "$pid" 2>/dev/null; then
    echo "server exited" >&2
    cat "$log" >&2
    exit 1
  fi
  sleep 0.1
done
port=$(tr -d ' \r\n' < "$rt/port")
if ! python3 tests/http_check.py "http://127.0.0.1:$port" "$rt/live.aura"; then
  echo "---- server log ----" >&2
  cat "$log" >&2
  exit 1
fi
echo "HTTP_OK"
