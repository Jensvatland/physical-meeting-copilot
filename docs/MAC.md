# Mac / Linux — download & run

## 1. Get the code

```bash
git clone https://github.com/Jensvatland/physical-meeting-copilot.git
cd physical-meeting-copilot
```

Or: GitHub → **Code → Download ZIP** → unzip → `cd` into the folder.

## 2. Try it (no mic, no keys)

```bash
bash scripts/try.sh
```

This installs [uv](https://github.com/astral-sh/uv) if needed, syncs dependencies, and runs the offline meeting demo.

**Success:** you see `OK — it works on this machine.`

### Prerequisites

- Python 3.11+ (`brew install python@3.12` on Mac)
- Network once (to install uv / packages)

## 3. Optional browser UI

```bash
uv run meeting-gateway
```

Chrome → [http://127.0.0.1:8787](http://127.0.0.1:8787) → allow mic → **Start meeting**.

Database default is `~/.physical-meeting-copilot/meetings.db` (no `export` needed).

### What you will see today

| Layer | Today |
|-------|--------|
| Mic → server | Works |
| Transcript text | **Simulated** (`[sim:…]`) — not real ASR yet |
| Speakers / translation | Simulated / glossary |
| Alerts & research | Work via demo + MCP/Hermes path |

## 4. Optional MCP

```bash
uv run python -m meeting_mcp
```

Point Hermes/OpenClaw at `integrations/hermes/mcp.json` or `integrations/openclaw/mcp.json`.

## Contributor smoke (stricter)

```bash
bash scripts/mac-smoke.sh
```

Runs lint, format check, pytest, demo, eval, MCP list, gateway health.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `uv: command not found` | `source "$HOME/.local/bin/env"` or open a new terminal |
| Mic denied | System Settings → Privacy → Microphone → Chrome |
| Useless live transcript | Expected with sim ASR — use `try.sh` / `simulate_meeting` for the real demo |
| Port 8787 busy | `MEETING_GATEWAY_PORT=8788 uv run meeting-gateway` |
