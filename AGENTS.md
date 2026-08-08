# Guidance for coding agents (and humans using them)

This repository welcomes contributions created with Cursor, Codex, Claude Code, Copilot, and other coding agents. **Humans remain responsible** for reviewing, testing, and submitting the result.

Goal: another person should be able to clone this repo, open it in an agent-friendly editor, and start contributing quickly.

## What this project is

**Physical Meeting Copilot** is an open-source, provider-independent runtime for AI-assisted *physical* face-to-face meetings.

- Meeting Core captures/normalizes meeting state (audio events → transcript/speakers/claims/research/alerts).
- Personal AI hosts (Hermes, OpenClaw, others) connect over **MCP**.
- The core does **not** own CRM, personal memory, or host-specific assistant logic.

Philosophy: this is an open experiment. Forks and experiments are welcome. Merges should stay secure, private, compatible, and maintainable.

## Architecture (short)

```text
PHYSICAL MEETING → Capture → WebSocket (LiveKit preferred later)
  → Meeting Core (events, transcript, claims, research, alerts)
  → Browser UI  |  Meeting MCP → Hermes / OpenClaw / other agents
```

Packages:

| Path | Role |
|------|------|
| `packages/protocol` | Versioned JSON Schemas |
| `packages/meeting_core` | Sessions, bus, stores, adapter contracts, pipeline |
| `packages/gateway` | Browser WebSocket PCM ingest + static UI |
| `packages/mcp_server` | MCP resources/tools over Meeting Core |
| `integrations/hermes` | Reference host bridge (not core logic) |
| `integrations/openclaw` | Second reference host bridge |
| `clients/web` | Browser prototype UI |

Read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), [docs/PROTOCOL.md](docs/PROTOCOL.md), and [docs/STATUS.md](docs/STATUS.md).

## Important boundaries — do not casually break

1. Keep vendor/provider code behind adapters implementing contracts in `packages/meeting_core/src/meeting_core/adapters/base.py`.
2. Do not put Hermes/OpenClaw business logic inside `packages/meeting_core`.
3. Raw audio stays on WebSocket/WebRTC — not MCP.
4. OpenAI / any single cloud vendor must never be mandatory for core flows.
5. Preserve Mandarin originals + translation provenance; do not overwrite originals.
6. Voice biometrics stay optional and consent-gated.
7. Do not claim real ASR/MT in UI/docs while sim adapters are still the default.
8. Do not commit secrets, recordings, transcripts, or personal data.

## How to run tests

```bash
uv sync --group dev
uv run ruff check .
uv run ruff format --check .
uv run pytest -q
uv run python -m meeting_core.demo.simulate_meeting
uv run python -m meeting_core.eval.harness
./scripts/mac-smoke.sh
```

CI (`.github/workflows/ci.yml`) runs lint, tests, simulate, eval, MCP inventory, and the smoke script.

## How to add a provider / adapter

1. Implement the relevant interface in `meeting_core.adapters.base` (e.g. `SpeechRecognitionAdapter`).
2. Place it under `packages/meeting_core/src/meeting_core/adapters/<area>/`.
3. Keep optional deps optional — degrade gracefully when unset (see `adapters/asr/funasr_stub.py`).
4. Wire selection via env / profile, not hard-coded vendor imports in session core.
5. Add tests for capabilities/health and a happy-path unit test (mock network/model).
6. Document license notes in `docs/LICENSES.md` before vendoring anything heavy.
7. Update [docs/STATUS.md](docs/STATUS.md) if the default path changes from sim → real.

## How to add an integration (MCP host / agent)

1. Prefer a folder under `integrations/<name>/` with `README.md`, optional `SKILL.md`, `mcp.json`, and a thin event bridge.
2. Talk to Meeting Core through MCP tools/resources or the event bus bridge pattern used by Hermes/OpenClaw.
3. Do not fork Meeting Core domain types into the host package unless necessary.
4. Add a focused test if the bridge has non-trivial behavior.

## Security requirements

- Never commit `.env`, keys, tokens, certificates, or private URLs with credentials.
- Prefer `127.0.0.1` for local gateway demos; do not advertise unauthenticated public binds.
- Redact secrets from logs.
- See [SECURITY.md](SECURITY.md) and [docs/SECURITY.md](docs/SECURITY.md).

## Privacy requirements

- Users/operators must obtain required consent before recording or processing conversations.
- Do not add silent biometric enrollment.
- Do not include real meeting recordings or personal transcripts in the repo or fixtures — use synthetic fixtures only.
- See [docs/PRIVACY.md](docs/PRIVACY.md).

## Coding conventions

- Python 3.11+, workspace managed with `uv`.
- Lint/format with Ruff (`pyproject.toml` settings).
- Prefer small, focused changes with tests near existing suites under `packages/*/tests`.
- Match existing style; do not drive-by refactor unrelated code.
- Keep docs honest about ✅ working / 🧪 experimental / 🚧 planned.

## What should NOT be changed casually

- Adapter contract shapes in `adapters/base.py` without an issue discussion
- Event envelope / protocol schemas without versioning consideration
- Default “OpenAI required” coupling of any kind
- Removal of the Simulated ASR honesty in the browser UI unless real ASR is the default
- License (Apache-2.0) or secret-bearing files

## Good starter tasks

See [docs/GOOD_FIRST_ISSUES.md](docs/GOOD_FIRST_ISSUES.md) and open issues labeled `good first issue`.
