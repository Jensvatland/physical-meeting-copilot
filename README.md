# Physical Meeting Copilot

An open-source experiment: an AI copilot for **real face-to-face meetings**.

> The meeting runtime listens; your personal AI understands.

Clone it, run it, break it, improve it. AI coding agents welcome. You do not need permission to experiment.

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

Open [http://127.0.0.1:8787](http://127.0.0.1:8787) in Chrome.

Live transcript text is still **simulated** (`[sim:…]`). The offline demo inside `try.sh` is the full claim → research → alert slice.

More detail: [docs/MAC.md](docs/MAC.md).

## What works today?

| | |
|---|---|
| ✅ Working | Offline demo, Meeting Core + SQLite, browser mic→server, MCP, Hermes research slice, Docker sim stack |
| 🧪 Experimental | Simulated ASR / diarization / translation / TTS; LiveKit & FunASR stubs |
| 🚧 Planned | Real speech models, iOS/iPad, production LiveKit, auth for remote access |

Full honesty: [docs/STATUS.md](docs/STATUS.md).

## How can I help?

```bash
bash scripts/try.sh          # first run
bash scripts/mac-smoke.sh    # full contributor check
```

Then open an issue or PR. Read [CONTRIBUTING.md](CONTRIBUTING.md) (short). Starter ideas: [docs/GOOD_FIRST_ISSUES.md](docs/GOOD_FIRST_ISSUES.md). Coding agents: [AGENTS.md](AGENTS.md).

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
