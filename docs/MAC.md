# Mac / Linux — download & run

Run an offline first-try without microphone or API keys, then optionally open the browser capture UI.

## Prerequisites

- macOS or Linux with Terminal
- Python 3.11+ (Homebrew: `brew install python@3.12`)
- [uv](https://github.com/astral-sh/uv) — `try.sh` can install it, or: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Chrome recommended for mic capture (Safari is less reliable with this prototype)

## 1. Get the code

```bash
git clone https://github.com/Jensvatland/physical-meeting-copilot.git
cd physical-meeting-copilot
```

Or: GitHub → **Code → Download ZIP** → unzip → `cd` into the folder.

See [STATUS.md](STATUS.md) for what works today.

## 2. Try it (no mic, no keys)

```bash
bash scripts/try.sh
```

This installs [uv](https://github.com/astral-sh/uv) if needed, syncs dependencies, and runs the offline meeting demo.

**Success:** you see `OK — it works on this machine.`

## 3. Optional browser UI

```bash
uv run meeting-gateway
```

Chrome → [http://127.0.0.1:8787](http://127.0.0.1:8787) → accept the consent checkbox → allow mic → **Start meeting**.

Database default is `~/.physical-meeting-copilot/meetings.db` (no `export` needed).

### What you will see today

| Layer | Behavior |
|-------|----------|
| Mic → server | Works (PCM over WebSocket) |
| VAD / activity | Works (energy-based) |
| Speaker labels | Simulated diarization |
| Transcript text | **Simulated** (`[sim:zh-CN:…]`) — not real ASR yet |
| Translation | Glossary / stub |
| Alerts / findings / research | Via demo + MCP/Hermes path |
| Private speech / AirPods | Lifecycle events only; no real device TTS yet |
| Languages | **zh-CN + en** MVP pair |

So: the pipeline and UI are testable; **realistic live transcription is not**.

## 4. Optional MCP

```bash
uv run python -m meeting_mcp
```

Point Hermes/OpenClaw at `integrations/hermes/mcp.json` or `integrations/openclaw/mcp.json`.

## 5. Contributor smoke (stricter)

```bash
bash scripts/mac-smoke.sh
```

Runs lint, format check, pytest, demo, eval, MCP inventory, temporary gateway `/health`.

**Success:** `Smoke OK.`

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `uv: command not found` | `source "$HOME/.local/bin/env"` or open a new terminal |
| `consent_required` | Check the UI box or send `"consent": true` |
| DB path errors | Smoke script creates `~/.physical-meeting-copilot/`; core also auto-creates parent dirs |
| Mic denied | System Settings → Privacy → Microphone → Chrome |
| Useless live transcript | Expected with sim ASR — use `try.sh` / `simulate_meeting` for the real demo |
| Port 8787 busy | `MEETING_GATEWAY_PORT=8788 uv run meeting-gateway` |
