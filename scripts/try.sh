#!/usr/bin/env bash
# First-run helper — no microphone, no API keys.
# Usage:  bash scripts/try.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

ensure_uv() {
  if command -v uv >/dev/null 2>&1; then
    return
  fi
  if [[ -x "${HOME}/.local/bin/uv" ]]; then
    export PATH="${HOME}/.local/bin:${PATH}"
    return
  fi
  echo "Installing uv (one-time)…"
  curl -LsSf https://astral.sh/uv/install.sh | sh
  # shellcheck disable=SC1091
  source "${HOME}/.local/bin/env" 2>/dev/null || export PATH="${HOME}/.local/bin:${PATH}"
  if ! command -v uv >/dev/null 2>&1; then
    echo "uv still not on PATH. Open a new terminal, or run: source \"\$HOME/.local/bin/env\""
    exit 1
  fi
}

ensure_uv

export MEETING_CORE_DB="${MEETING_CORE_DB:-$HOME/.physical-meeting-copilot/meetings.db}"
mkdir -p "$(dirname "$MEETING_CORE_DB")"

echo "==> Installing dependencies"
uv sync --group dev

echo "==> Running offline meeting demo (no mic)"
uv run python -m meeting_core.demo.simulate_meeting

cat <<EOF

OK — it works on this machine.

Open the browser UI (Chrome recommended):

  uv run meeting-gateway

Then visit http://127.0.0.1:8787

Notes:
  • No API keys needed
  • Live transcript text is still simulated ([sim:…])
  • Full contributor check: bash scripts/mac-smoke.sh
  • More detail: docs/MAC.md
EOF
