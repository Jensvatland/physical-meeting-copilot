# Physical Meeting Copilot

Open-source, provider-independent runtime for AI-assisted physical face-to-face meetings.

> **The meeting runtime listens; the user’s personal AI understands.**

Reference brains: [Hermes](https://github.com/) and OpenClaw. Clients progress: browser/macOS prototype → iPhone → iPad.

## What this is

A Meeting Core that captures room audio, transcribes (Mandarin + English), diarizes speakers, translates while preserving originals, maintains structured meeting state, and exposes that state to personal AI agents via MCP — without embedding assistant/CRM/research logic in the core.

## Quick start

```bash
# Requires Python 3.11+ and uv
uv sync
uv run pytest
uv run ruff check .
```

Simulate a multi-speaker meeting (Phase 1 acceptance):

```bash
uv run python -m meeting_core.demo.simulate_meeting
```

## Architecture (summary)

```text
PHYSICAL MEETING → Capture → Realtime media (LiveKit preferred)
  → Meeting Core (events, transcript, claims, alerts)
  → Realtime UI  |  Meeting MCP → Hermes / OpenClaw / other agents
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Documentation

| Doc | Purpose |
|-----|---------|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design, planes, adapters |
| [ROADMAP.md](docs/ROADMAP.md) | Phases 0–45 and acceptance criteria |
| [PROTOCOL.md](docs/PROTOCOL.md) | Canonical event schema + MCP surface |
| [DECISIONS.md](docs/DECISIONS.md) | ADR index |
| [SECURITY.md](docs/SECURITY.md) | Threat model baseline |
| [PRIVACY.md](docs/PRIVACY.md) | Consent, biometrics, retention |
| [CHINA.md](docs/CHINA.md) | China-first deployment profile |
| [LICENSES.md](docs/LICENSES.md) | Dependency license notes |

## Design principles

1. Minimize custom code; integrate mature components.
2. Meeting Core is provider-independent behind adapters.
3. Raw realtime audio uses WebRTC/WebSocket — not MCP.
4. MCP carries structured context, tools, findings, alerts, actions.
5. China is a first-class profile; OpenAI is never mandatory.
6. Voice biometrics are optional, consent-based, separable, deletable.

## Status

Phases 0–1 complete; MCP façade + Hermes/OpenClaw stubs in place. Next: Phase 2 live audio (LiveKit). See [docs/ROADMAP.md](docs/ROADMAP.md).

## License

Apache-2.0 for core code unless a dependency forces a narrower boundary (documented in `docs/LICENSES.md`).
