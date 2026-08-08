# Hermes integration

Minimal reference bridge. Host-specific Hermes logic stays here — not in Meeting Core.

## Setup

1. Share the same SQLite DB as the gateway:
   ```bash
   export MEETING_CORE_DB=~/.physical-meeting-copilot/meetings.db
   uv run meeting-gateway   # terminal 1
   uv run python -m meeting_mcp   # terminal 2 (stdio MCP)
   ```
2. Point Hermes at this server using [`mcp.json`](mcp.json).
3. Load [`SKILL.md`](SKILL.md) as the meeting-copilot skill.

## Event bridge

[`event_bridge.py`](event_bridge.py) subscribes to Meeting Core events and can run a **non-blocking** research vertical slice (`auto_research=True`): claim → `research.*` → finding → suggested question → private speech lifecycle.

## Demo vertical slice

Covered by the offline smoke / simulation:

```bash
uv run python -m meeting_core.demo.simulate_meeting
```

1. Simulated transcript produces a capacity claim.
2. Hermes starts background research (`research.started`).
3. Finding + suggested question published while the session continues.
4. Private speech lifecycle emits `private_speech.queued` / `spoken` (sim TTS; AirPods device path later).
