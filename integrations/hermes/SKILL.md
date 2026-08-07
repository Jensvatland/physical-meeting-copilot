# Hermes Skill — Physical Meeting Copilot

## Purpose

Connect Hermes to Meeting Core over MCP. Hermes owns personal memory, projects, relationships, files, email, web/browser research, specialist agents, and reasoning. Meeting Core owns live meeting state only.

## Priority signals

When consuming meeting events / recent context, prioritize:

1. Prices and numbers
2. Dates and deadlines
3. Commitments and warranties
4. Technical / regulatory / commercial claims
5. Changed statements vs prior meetings or documents
6. Contradictions and conflicting evidence
7. Unanswered questions
8. Material risk

## Behavior

- Background research must **not** block transcription.
- Use `meeting.get_recent_context` before answering contextual commands (“Check what he just said”, “Did he change the delivery date?”).
- Publish findings with provenance via `meeting.publish_finding`.
- Push concise private alerts via `meeting.push_private_alert` / `meeting.speak_private`.
- Suggested questions go through `meeting.record_question` with `suggested=true`.
- Never overwrite original transcript statements; update claim **state** only.

## Modes

Respect session mode (`COPILOT` default, `INTERPRETER`, `SILENT`). In `SILENT`, prefer visual findings; speak only critical alerts.

## Config

See `mcp.json` and `README.md` in this directory.
