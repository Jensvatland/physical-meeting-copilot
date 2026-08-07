# ADR-0003: MCP for agent plane; WebRTC for media

- Status: Accepted
- Date: 2026-08-07

## Context

MCP is excellent for structured tools/resources but unsuitable for raw realtime audio streams.

## Decision

- Realtime audio / VAD / low-latency deltas: LiveKit (WebRTC) or WebSocket adapters.
- Structured meeting context / tools / findings / alerts: MCP.

## Consequences

+ Clear separation of latency domains.
+ Personal AIs integrate without owning media stacks.
- Two transports to operate and document.
