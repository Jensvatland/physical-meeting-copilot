# ADR-0004: JSON Schema as canonical protocol source

- Status: Accepted
- Date: 2026-08-07

## Context

Events must be machine-validatable across Python core, MCP, Hermes, OpenClaw, and future Swift clients.

## Decision

Canonical schemas are JSON Schema Draft 2020-12 under `packages/protocol/schemas/`. Python models and (later) Swift/TS codegen consume them; protocol version is semver in every event.

## Consequences

+ Cross-language validation and generated clients.
+ Breaking changes require version bumps and ADR notes.
- Manual dual-maintenance avoided by treating schemas as source of truth.
