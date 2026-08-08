# Physical Meeting Copilot

Open-source, provider-independent runtime for AI-assisted physical face-to-face meetings.

> **The meeting runtime listens; the user’s personal AI understands.**

Reference brains: Hermes and OpenClaw. Clients progress: browser/macOS prototype → iPhone → iPad.

## What this is

A Meeting Core that captures room audio, transcribes (Mandarin + English), diarizes speakers, translates while preserving originals, maintains structured meeting state, and exposes that state to personal AI agents via MCP — without embedding assistant/CRM/research logic in the core.

## Quick start (Mac / Linux)

**Requires:** Python 3.11+ and [uv](https://github.com/astral-sh/uv).

```bash
git clone https://github.com/Jensvatland/physical-meeting-copilot.git
cd physical-meeting-copilot
# until merged: git checkout cursor/complete-runtime-foundation-e10f

chmod +x scripts/mac-smoke.sh
./scripts/mac-smoke.sh
```

That offline smoke test needs **no microphone and no API keys**. Details: [docs/MAC.md](docs/MAC.md).

### Optional: browser capture UI

```bash
export MEETING_CORE_DB=~/.physical-meeting-copilot/meetings.db
uv run meeting-gateway
# open http://127.0.0.1:8787 — Chrome — allow mic — Start meeting
```

> **Expectation:** mic → server works, but transcript text is still from a **simulated ASR** (`[sim:…]`). For the full claim → research → alert demo without speaking, rely on `simulate_meeting` (included in the smoke script).

### Optional: MCP for Hermes / OpenClaw

```bash
export MEETING_CORE_DB=~/.physical-meeting-copilot/meetings.db
uv run python -m meeting_mcp
```

### Docker

```bash
docker compose up --build
# overlays: docker-compose.china.yml / docker-compose.global.yml
```

## Architecture (summary)

```text
PHYSICAL MEETING → Capture → Realtime media (LiveKit preferred / WebSocket slice)
  → Meeting Core (events, transcript, claims, research, alerts)
  → Realtime UI  |  Meeting MCP → Hermes / OpenClaw / other agents
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Documentation

| Doc | Purpose |
|-----|---------|
| [MAC.md](docs/MAC.md) | MacBook download + smoke + mic expectations |
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

Runtime foundation (phases 0–22) is in place with **sim adapters** where production ML/providers are optional. Offline smoke is the supported first test; real FunASR/LiveKit/Qwen and iOS come next. See [docs/ROADMAP.md](docs/ROADMAP.md).

## License

Apache-2.0 for core code unless a dependency forces a narrower boundary (documented in `docs/LICENSES.md`).
