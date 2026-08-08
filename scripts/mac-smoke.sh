#!/usr/bin/env bash
# Offline Mac/Linux smoke test — no microphone, no cloud keys required.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if ! command -v uv >/dev/null 2>&1; then
  echo "uv not found. Install: curl -LsSf https://astral.sh/uv/install.sh | sh"
  exit 1
fi

export MEETING_CORE_DB="${MEETING_CORE_DB:-$HOME/.physical-meeting-copilot/meetings.db}"
mkdir -p "$(dirname "$MEETING_CORE_DB")"

echo "==> uv sync"
uv sync --group dev

echo "==> ruff"
uv run ruff check .

echo "==> pytest"
uv run pytest -q

echo "==> simulate meeting (Hermes research slice)"
uv run python -m meeting_core.demo.simulate_meeting

echo "==> eval harness"
uv run python -m meeting_core.eval.harness

echo "==> MCP tool/resource inventory"
uv run python -m meeting_mcp --list

echo "==> gateway health (temporary server)"
uv run python - <<'PY'
import os
import threading
import time
import urllib.request

import uvicorn

from meeting_gateway.app import app

host = "127.0.0.1"
port = int(os.environ.get("MEETING_SMOKE_PORT", "8799"))
config = uvicorn.Config(app, host=host, port=port, log_level="warning")
server = uvicorn.Server(config)
thread = threading.Thread(target=server.run, daemon=True)
thread.start()

deadline = time.time() + 10
url = f"http://{host}:{port}/health"
last_err = None
while time.time() < deadline:
    try:
        with urllib.request.urlopen(url, timeout=1) as resp:
            body = resp.read().decode()
            if '"ok":true' not in body.replace(" ", ""):
                raise RuntimeError(body)
            print(f"health ok: {body}")
            break
    except Exception as exc:  # noqa: BLE001 — smoke wait loop
        last_err = exc
        time.sleep(0.2)
else:
    raise SystemExit(f"gateway health failed: {last_err}")

server.should_exit = True
thread.join(timeout=5)
PY

cat <<EOF

Smoke OK.

Next (optional, needs browser mic — ASR text is still simulated):
  export MEETING_CORE_DB=$MEETING_CORE_DB
  uv run meeting-gateway
  open http://127.0.0.1:8787   # Chrome recommended

See docs/MAC.md for expectations and limits.
EOF
