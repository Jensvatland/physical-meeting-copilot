# ADR-0001: Python Meeting Core with adapter contracts

- Status: Accepted
- Date: 2026-08-07

## Context

Meeting Core must be portable, testable, and free of provider SDKs. Hermes and OpenClaw ecosystems are Python-friendly; iOS clients will consume the protocol over the network, not embed core logic.

## Decision

Implement Meeting Core and the reference MCP server in Python 3.11+, with explicit adapter Protocol/ABC contracts. iOS/browser remain thin clients.

## Consequences

+ Fast iteration, shared tooling with Hermes integrations, easy SQLite/tests.
+ Adapter SDKs can later expose TypeScript mirrors without moving domain logic.
- Native mobile must treat core as a remote service.
