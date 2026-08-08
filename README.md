# Physical Meeting Copilot

**v0.1 preview** — an open-source experiment: an AI copilot for **real face-to-face meetings**.

> The meeting runtime listens; your personal AI understands.

[简体中文](README.zh-CN.md) · [Status](docs/STATUS.md) · [Contributing](CONTRIBUTING.md) · [Mac quick start](docs/MAC.md)

Clone it, run it, break it, improve it. AI coding agents welcome. You do not need permission to experiment.

Reference integrations: [`integrations/hermes`](integrations/hermes), [`integrations/openclaw`](integrations/openclaw). Clients today: browser prototype → later iPhone / iPad.

## Try it

**Need:** Python 3.11+ and a terminal (Mac/Linux). No microphone. No API keys.

```bash
git clone https://github.com/Jensvatland/physical-meeting-copilot.git
cd physical-meeting-copilot
bash scripts/try.sh
```

No git? Download the ZIP from GitHub → unzip → `cd` into the folder → same `bash scripts/try.sh`.

When that finishes, start the UI:

```bash
uv run meeting-gateway
```

Open [http://127.0.0.1:8787](http://127.0.0.1:8787) in Chrome → accept consent → Start meeting.

You will see a **Simulated ASR** notice. That is intentional in v0.1. Live transcript text is still **simulated** (`[sim:…]`). The offline demo inside `try.sh` is the full claim → research → alert slice.

More detail: [docs/MAC.md](docs/MAC.md).

## What works today?

| | |
|---|---|
| ✅ Working | Offline demo, Meeting Core + SQLite, browser mic→server, MCP, Hermes research slice, Docker sim stack |
| 🧪 Experimental | Simulated ASR / diarization / translation / TTS; LiveKit & FunASR stubs |
| 🚧 Planned | Real speech models, iOS/iPad, production LiveKit, auth for remote access |

Full honesty: [docs/STATUS.md](docs/STATUS.md).

## Supported languages (v0.1)

| Role | Languages |
|------|-----------|
| Meeting speech pair | **Mandarin (`zh-CN`) + English (`en`)** only |
| Project documentation | English (canonical) + Simplified Chinese README |
| Future locales | Welcome as adapters later — not in MVP scope |

Protocol fields are BCP-47-ready; contribution focus stays on this pair until a real ASR/MT adapter lands.

## How can I help?

You do not need an invitation. Pick something small and open a PR.

```bash
bash scripts/try.sh          # first run
bash scripts/mac-smoke.sh    # full contributor check
```

### Wanted right now

| If you like… | Try this |
|--------------|----------|
| Docs / visuals | README screenshot or short GIF |
| Tests | FunASR stub enable/disable coverage |
| Eval / AI | More text scenarios in the eval harness |
| UI | Accessibility pass (keep Simulated ASR banner) |
| Privacy | Clearer consent / recording notice |
| Models | Optional Qwen-compatible translation adapter |
| Integrations | OpenClaw ↔ Hermes parity checklist |
| Audio | Mic-less synthetic WAV replay into the gateway |
| Experiments | Alternative local STT behind the adapter interface |

Full list + one-command publisher: [docs/GOOD_FIRST_ISSUES.md](docs/GOOD_FIRST_ISSUES.md) (`bash scripts/bootstrap-community.sh`).

Read [CONTRIBUTING.md](CONTRIBUTING.md) (short). Coding agents: [AGENTS.md](AGENTS.md). AI-generated contributions are welcome — you still review/test before submitting.

## Architecture (summary)

```text
PHYSICAL MEETING → Capture → WebSocket (LiveKit later)
  → Meeting Core (events, transcript, claims, research, alerts)
  → Browser UI  |  Meeting MCP → Hermes / OpenClaw / other agents
```

## Docs

| | |
|---|---|
| [STATUS](docs/STATUS.md) · [Architecture](docs/ARCHITECTURE.md) · [Roadmap](docs/ROADMAP.md) | Product |
| [Protocol](docs/PROTOCOL.md) · [ADRs](docs/DECISIONS.md) · [China](docs/CHINA.md) | Design |
| [Security](SECURITY.md) · [Privacy](docs/PRIVACY.md) · [Community](docs/COMMUNITY.md) | Trust |

## Privacy

If you record real conversations, **you** must follow applicable law and get required consent. See [docs/PRIVACY.md](docs/PRIVACY.md).

## License

Apache-2.0 — see [LICENSE](LICENSE).
