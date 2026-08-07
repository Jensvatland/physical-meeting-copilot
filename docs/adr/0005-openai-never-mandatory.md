# ADR-0005: OpenAI never mandatory; China profile first-class

- Status: Accepted
- Date: 2026-08-07

## Context

Golden Acceptance Test is a multilingual physical meeting in China. Blocked or unavailable Western APIs must not prevent the core experience.

## Decision

OpenAI (and any single cloud vendor) is optional behind adapters. China profile uses FunASR/SenseVoice, 3D-Speaker, Qwen-compatible endpoints, and local/China TTS via `docker-compose.china.yml`.

## Consequences

+ Deployable under restricted egress.
+ Adapter conformance tests become critical.
- Reference demos must always include a non-OpenAI path.
