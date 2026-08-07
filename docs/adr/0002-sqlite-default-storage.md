# ADR-0002: SQLite as default StorageAdapter

- Status: Accepted
- Date: 2026-08-07

## Context

Local-first / self-hosted defaults are required for privacy and China/offline profiles. Enterprise may need PostgreSQL later.

## Decision

Default persistence is SQLite behind `StorageAdapter`. Domain code never imports a specific SQL dialect beyond the adapter.

## Consequences

+ Zero-ops local demos; crash-safe enough for Phase 1–13.
+ PostgreSQL can be added in Phase 21 without rewriting Meeting Core.
- Large multi-tenant SaaS is deferred.
