# OpenClaw integration

Second reference host. Meeting Core must work unchanged.

## Setup

Mirror the Hermes MCP config (`mcp.json`) toward an OpenClaw-compatible MCP client. Keep host-specific prompts/tools in this folder only.

## Contract

- Consume the same MCP resources/tools documented in `docs/PROTOCOL.md`.
- Do not require OpenClaw types inside `packages/meeting_core`.
- Prefer the same skill priorities as Hermes for material meeting signals.
