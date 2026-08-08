# MacBook quick start

Run a full offline smoke test without microphone or API keys, then optionally open the browser capture UI.

## Prerequisites

- macOS with Terminal
- Python 3.11+ (Homebrew: `brew install python@3.12`)
- [uv](https://github.com/astral-sh/uv): `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Chrome recommended for mic capture (Safari is less reliable with this prototype)

## 1) Download

```bash
git clone https://github.com/Jensvatland/physical-meeting-copilot.git
cd physical-meeting-copilot
```

If you are testing an unmerged contribution branch, check it out explicitly after cloning.

## 2) Offline smoke (no mic)

```bash
chmod +x scripts/mac-smoke.sh
./scripts/mac-smoke.sh
```

This runs: dependency sync, lint, pytest, simulated multi-speaker meeting (incl. Hermes research), eval harness, MCP inventory, and a temporary gateway `/health` check.

**Success looks like:** `Smoke OK.` at the end.

## 3) Optional browser capture

```bash
export MEETING_CORE_DB=~/.physical-meeting-copilot/meetings.db
uv run meeting-gateway
open http://127.0.0.1:8787
```

Allow microphone → **Start meeting**.

### What you will see today

| Layer | Behavior on Mac now |
|-------|---------------------|
| Mic → server | Works (PCM over WebSocket) |
| VAD / activity | Works (energy-based) |
| Speaker labels | Simulated diarization (spk_1…) |
| Transcript text | **Simulated** (`[sim:zh-CN:…]`), not real Mandarin/English ASR |
| Translation | Glossary / stub only |
| Alerts / findings / research | Work when claims/events are injected (demo + MCP/Hermes path) |
| Private speech / AirPods | Lifecycle events only; no real device TTS yet |

So: the pipeline and UI are testable; **realistic live transcription is not**.

## 4) Optional MCP (Hermes / OpenClaw)

Use the same DB as the gateway:

```bash
export MEETING_CORE_DB=~/.physical-meeting-copilot/meetings.db
uv run python -m meeting_mcp
```

Point the host at `integrations/hermes/mcp.json` or `integrations/openclaw/mcp.json`.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `uv: command not found` | Restart Terminal after install, or `source $HOME/.local/bin/env` |
| DB path errors | Smoke script creates `~/.physical-meeting-copilot/`; core also auto-creates parent dirs |
| Mic denied | System Settings → Privacy → Microphone → Chrome |
| No useful transcript while speaking | Expected with sim ASR — use `simulate_meeting` for the real vertical-slice demo |
| Port 8787 busy | `MEETING_GATEWAY_PORT=8788 uv run meeting-gateway` |

## Still nicer without a live room test

Improvements that do **not** need a physical meeting:

1. Fixture WAV replay into the gateway (deterministic “fake mic” without speaking)
2. Sample UI screenshots / short GIF in README
3. One-click `brew`/`uvx` style install note
4. Wire a real local ASR later (FunASR) when you want spoken Mandarin to appear as Chinese text

See also [GOOD_FIRST_ISSUES.md](GOOD_FIRST_ISSUES.md).
