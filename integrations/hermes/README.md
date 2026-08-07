# Hermes integration

Minimal reference bridge. Host-specific Hermes logic stays here — not in Meeting Core.

## Setup

1. Run Meeting Core / MCP façade (stdio MCP transport lands fully in Phase 7/8).
2. Point Hermes MCP config at this server using `mcp.json`.
3. Load `SKILL.md` as the meeting-copilot skill.

## Event bridge

`event_bridge.py` shows how to subscribe to Meeting Core events and forward structured payloads to Hermes without coupling core to Hermes APIs.

## Demo vertical slice (Phase 8)

1. Simulated/live transcript produces a capacity claim.
2. Hermes starts background research (`research.started`).
3. Finding + suggested question published while transcription continues.
4. Private alert queued for AirPods (Phase 9).
