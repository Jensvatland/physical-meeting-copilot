# Mac / Linux quick start (v0.1)

Run a full offline smoke test without microphone or API keys, then optionally open the browser capture UI.

## Prerequisites

- macOS or Linux with Terminal
- Python 3.11+ (Homebrew: `brew install python@3.12`)
- [uv](https://github.com/astral-sh/uv): `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Chrome recommended for mic capture (Safari is less reliable with this prototype)

## 1) Download

```bash
git clone https://github.com/Jensvatland/physical-meeting-copilot.git
cd physical-meeting-copilot
```

Use the repository default branch (after MVP PRs land). See [STATUS.md](STATUS.md) for what works today.

## 2) Offline smoke (no mic)

```bash
chmod +x scripts/mac-smoke.sh
./scripts/mac-smoke.sh
```

Runs: dependency sync, lint, pytest, simulated multi-speaker meeting (Hermes research), eval harness, MCP inventory, temporary gateway `/health`.

**Success:** `Smoke OK.`

## 3) Optional browser capture

```bash
export MEETING_CORE_DB=~/.physical-meeting-copilot/meetings.db
uv run meeting-gateway
open http://127.0.0.1:8787
```

Accept the consent checkbox → allow microphone → **Start meeting**.

### What you will see today

| Layer | Behavior |
|-------|----------|
| Mic → server | Works (PCM over WebSocket) |
| VAD / activity | Works (energy-based) |
| Speaker labels | Simulated diarization |
| Transcript text | **Simulated** (`[sim:zh-CN:…]`) |
| Translation | Glossary / stub |
| Alerts / findings / research | Via demo + MCP/Hermes path |
| Private speech / AirPods | Lifecycle events only; no real device TTS yet |
| Languages | **zh-CN + en** MVP pair |

So: the pipeline and UI are testable; **realistic live transcription is not**.

## 4) Optional MCP

```bash
export MEETING_CORE_DB=~/.physical-meeting-copilot/meetings.db
uv run python -m meeting_mcp
```

Configs: `integrations/hermes/mcp.json`, `integrations/openclaw/mcp.json`.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `uv: command not found` | `source $HOME/.local/bin/env` or restart Terminal |
| `consent_required` | Check the UI box or send `"consent": true` |
| DB path errors | Smoke script creates `~/.physical-meeting-copilot/`; core also auto-creates parent dirs |
| Mic denied | System Settings → Privacy → Microphone → Chrome |
| No useful transcript while speaking | Expected with sim ASR — use smoke / `simulate_meeting` |
| Port busy | `MEETING_GATEWAY_PORT=8788 uv run meeting-gateway` |
