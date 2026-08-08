# Physical Meeting Copilot

Open-source experimental runtime for an AI copilot in **real-world, face-to-face meetings**.

> **The meeting runtime listens; the user’s personal AI understands.**

This project exists because we want this tool to exist. Everyone is welcome to clone it, run it, test it, experiment, report problems, suggest ideas, build integrations, improve features, open pull requests, and fork it.

You do not need permission to experiment.

[Contributing](CONTRIBUTING.md) · [Status](docs/STATUS.md) · [Agents](AGENTS.md) · [Community](docs/COMMUNITY.md) · [Mac/Linux quick start](docs/MAC.md) · [Security](SECURITY.md)

## What is this?

A **Meeting Core** that can capture room audio, transcribe (Mandarin + English path), diarize speakers, translate while preserving originals, maintain structured meeting state, and expose that state to personal AI agents via **MCP** — without embedding assistant/CRM/research logic in the core.

Reference integrations: Hermes and OpenClaw. Clients today: browser prototype → later iPhone / iPad / macOS.

## Why does it exist?

Physical meetings still lose context, contradictions, and follow-ups in the noise. We want a provider-independent, local-first runtime that *listens* and lets *your* agents understand — especially for Mandarin/English rooms and China-capable deployments where OpenAI is never mandatory.

## What currently works?

| | |
|---|---|
| ✅ **Working today** | Meeting Core, SQLite, offline smoke, browser mic→WebSocket capture, MCP stdio, Hermes research demo slice, export/history heuristics, Docker sim stack |
| 🧪 **Experimental** | Simulated ASR/diarization/translation/TTS; LiveKit/FunASR/Postgres stubs; unauthenticated local gateway |
| 🚧 **Planned** | Real ASR/MT adapters, LiveKit production path, iOS/iPad clients, stronger audio eval suites, auth for remote exposure |

Details: [docs/STATUS.md](docs/STATUS.md).

## How do I try it?

**Requires:** Python 3.11+ and [uv](https://github.com/astral-sh/uv).

```bash
git clone https://github.com/Jensvatland/physical-meeting-copilot.git
cd physical-meeting-copilot
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

> Docker publishes the gateway without auth. Use only on trusted networks; prefer local binds for demos. See [SECURITY.md](SECURITY.md).

## How can I help?

1. Read [CONTRIBUTING.md](CONTRIBUTING.md) (lightweight rules; AI-assisted PRs welcome).
2. Skim [docs/STATUS.md](docs/STATUS.md) and [AGENTS.md](AGENTS.md).
3. Run `./scripts/mac-smoke.sh`.
4. Open an issue or PR — bugs, docs, adapters, languages, hardware experiments, integrations.

Starter ideas: [docs/GOOD_FIRST_ISSUES.md](docs/GOOD_FIRST_ISSUES.md).

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
| [STATUS.md](docs/STATUS.md) | Honest “works / experimental / planned” |
| [MAC.md](docs/MAC.md) | Download + smoke + mic expectations |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design, planes, adapters |
| [ROADMAP.md](docs/ROADMAP.md) | Phases and acceptance criteria |
| [PROTOCOL.md](docs/PROTOCOL.md) | Canonical event schema + MCP surface |
| [DECISIONS.md](docs/DECISIONS.md) | ADR index |
| [SECURITY.md](SECURITY.md) / [docs/SECURITY.md](docs/SECURITY.md) | Reporting + threat model |
| [PRIVACY.md](docs/PRIVACY.md) | Consent, biometrics, retention |
| [COMMUNITY.md](docs/COMMUNITY.md) | Issues, Discussions, maintainers |
| [CHINA.md](docs/CHINA.md) | China-first deployment profile |
| [LICENSES.md](docs/LICENSES.md) | Dependency license notes |
| [AGENTS.md](AGENTS.md) | Instructions for coding agents |

## Design principles

1. Minimize custom code; integrate mature components.
2. Meeting Core is provider-independent behind adapters.
3. Raw realtime audio uses WebRTC/WebSocket — not MCP.
4. MCP carries structured context, tools, findings, alerts, actions.
5. China is a first-class profile; OpenAI is never mandatory.
6. Voice biometrics are optional, consent-based, separable, deletable.

## Privacy note

If you record or process real conversations, **you** are responsible for complying with applicable laws and obtaining required consent. See [docs/PRIVACY.md](docs/PRIVACY.md).

## License

Apache-2.0 for core code unless a dependency forces a narrower boundary (documented in `docs/LICENSES.md`).
