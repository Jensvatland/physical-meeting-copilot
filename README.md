# Physical Meeting Copilot

**v0.1 preview** — open-source, provider-independent runtime for AI-assisted physical face-to-face meetings.

> **The meeting runtime listens; the user’s personal AI understands.**

[简体中文](README.zh-CN.md) · [Status](docs/STATUS.md) · [Contributing](CONTRIBUTING.md) · [Mac quick start](docs/MAC.md)

Reference integrations: [`integrations/hermes`](integrations/hermes), [`integrations/openclaw`](integrations/openclaw). Clients today: browser prototype → later iPhone / iPad.

## What this is

A **Meeting Core** that can capture room audio, maintain structured meeting state (transcript, speakers, claims, research, alerts), and expose that state to personal AI agents over **MCP** — without embedding assistant/CRM/research logic in the core.

**v0.1 uses simulated ASR/diarization/translation.** Mic → server works; spoken words are **not** yet turned into real Mandarin/English text. The offline demo (`simulate_meeting`) is the supported vertical slice.

## Supported languages (v0.1)

| Role | Languages |
|------|-----------|
| Meeting speech pair | **Mandarin (`zh-CN`) + English (`en`)** only |
| Project documentation | English (canonical) + Simplified Chinese README |
| Future locales | Welcome as adapters later — not in MVP scope |

Protocol fields are BCP-47-ready; contribution focus stays on this pair until a real ASR/MT adapter lands.

## Quick start

**Requires:** Python 3.11+ and [uv](https://github.com/astral-sh/uv).

```bash
git clone https://github.com/Jensvatland/physical-meeting-copilot.git
cd physical-meeting-copilot
chmod +x scripts/mac-smoke.sh
./scripts/mac-smoke.sh
```

No microphone and no API keys. Details: [docs/MAC.md](docs/MAC.md).

### Optional browser UI

```bash
export MEETING_CORE_DB=~/.physical-meeting-copilot/meetings.db
uv run meeting-gateway
# Chrome → http://127.0.0.1:8787 → accept consent → Start meeting
```

You will see a **Simulated ASR** notice. That is intentional in v0.1.

### Optional MCP (Hermes / OpenClaw)

```bash
export MEETING_CORE_DB=~/.physical-meeting-copilot/meetings.db
uv run python -m meeting_mcp
```

### Docker (sim stack)

```bash
docker compose up --build
```

## How to contribute

We want help — especially on real speech adapters and eval fixtures.

1. Read [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/STATUS.md](docs/STATUS.md)
2. Run `./scripts/mac-smoke.sh`
3. Open a PR against the default branch

Good first areas: docs clarity, eval scenarios, FunASR/LiveKit adapter wiring, UI polish (keep the sim banner until ASR is real).

## Architecture (summary)

```text
PHYSICAL MEETING → Capture → WebSocket (LiveKit later)
  → Meeting Core (events, transcript, claims, research, alerts)
  → Browser UI  |  Meeting MCP → Hermes / OpenClaw / other agents
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Documentation

| Doc | Purpose |
|-----|---------|
| [STATUS.md](docs/STATUS.md) | What works vs simulated **today** |
| [MAC.md](docs/MAC.md) | Mac/Linux download + smoke |
| [ROADMAP.md](docs/ROADMAP.md) | MVP → v1.0 |
| [PROTOCOL.md](docs/PROTOCOL.md) | Events + MCP surface |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Planes and adapters |
| [SECURITY.md](docs/SECURITY.md) / [PRIVACY.md](docs/PRIVACY.md) | Baseline threat & consent |
| [CHINA.md](docs/CHINA.md) | China-first profile intent |
| [LICENSES.md](docs/LICENSES.md) | Dependency notes |

## Design principles

1. Minimize custom code; integrate mature components.
2. Meeting Core is provider-independent behind adapters.
3. Raw realtime audio uses WebRTC/WebSocket — not MCP.
4. MCP carries structured context, tools, findings, alerts, actions.
5. China is a first-class profile; OpenAI is never mandatory.
6. Voice biometrics are optional, consent-based, separable, deletable.

## License

Apache-2.0 — see [LICENSE](LICENSE).
