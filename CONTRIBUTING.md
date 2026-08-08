# Contributing

Thanks for helping build Physical Meeting Copilot. This project is an early **v0.1** preview — honesty about sim vs real adapters matters more than feature count.

## Before you start

1. Read [docs/STATUS.md](docs/STATUS.md) — what actually works today.
2. Read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — Meeting Core stays provider-independent.
3. Run the offline smoke test:

```bash
./scripts/mac-smoke.sh
```

## Language policy (MVP)

- **Meeting pair:** Mandarin (`zh-CN`) + English (`en`) only for fixtures, demos, and default config.
- **Repo discussion / PR / issues:** English preferred (widest contributor reach). Simplified Chinese welcome in issues when clarifying China-deploy topics.
- **Docs:** English is canonical. Keep `README.zh-CN.md` (and small zh mirrors) in sync when changing user-facing status.
- **More spoken languages:** contribute as adapters + eval fixtures after v0.2 real ASR lands — don’t expand MVP defaults to a third language yet.

## Design constraints (please don’t break these)

1. No Hermes/OpenClaw business logic inside `packages/meeting_core`.
2. Raw audio stays on WebSocket/WebRTC — not MCP.
3. OpenAI (or any single cloud vendor) must never be mandatory.
4. Original transcript text is immutable; claims evolve via state/evidence.
5. Label simulated adapters clearly in UI and docs until they’re real.

## Development

```bash
uv sync --group dev
uv run ruff check .
uv run pytest -q
uv run python -m meeting_core.demo.simulate_meeting
```

### Suggested contribution areas

| Area | Why it’s valuable |
|------|-------------------|
| FunASR / SenseVoice adapter | Unlocks real Mandarin MVP path |
| LiveKit transport adapter | Production realtime plane |
| Eval audio/text fixtures | Regression without a live room |
| Docs / zh-CN mirrors | Lower onboarding friction |
| Browser UI clarity | Keep sim banner; improve consent/people UX |
| OpenClaw skill parity | Second host should feel first-class |

## Pull requests

- Target the repository default branch.
- Keep PRs focused; mention STATUS impact (“still sim” vs “real ASR”).
- Add/adjust tests for core behavior.
- Do not remove the Simulated ASR UI notice unless a real ASR path is the default.

## Reporting security issues

See [SECURITY.md](SECURITY.md) (do not file public issues for vulnerabilities).

## Code of conduct

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
