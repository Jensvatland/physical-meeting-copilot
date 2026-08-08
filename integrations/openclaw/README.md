# OpenClaw integration

Second reference host. Meeting Core must work unchanged.

## Setup

1. Use the same DB as the gateway (default `~/.physical-meeting-copilot/meetings.db`):
   ```bash
   uv run meeting-gateway          # terminal 1
   uv run python -m meeting_mcp    # terminal 2
   ```
2. Mirror Hermes MCP config via [`mcp.json`](mcp.json) toward an OpenClaw-compatible client.
3. Keep host-specific prompts/tools in this folder only (`SKILL.md`).

## Event bridge

[`event_bridge.py`](event_bridge.py) forwards material meeting events with `host: openclaw` — no OpenClaw types inside `packages/meeting_core`.

## Contract

- Consume the same MCP resources/tools documented in `docs/PROTOCOL.md`.
- Do not require OpenClaw types inside Meeting Core.
- Prefer the same skill priorities as Hermes for material meeting signals.
