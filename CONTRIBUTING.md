# Contributing

This is an open experiment to build an AI copilot for real-world, face-to-face meetings. Early **v0.1** preview — honesty about sim vs real adapters matters more than feature count.

Everyone is welcome — developers, AI coding agents, researchers, students, companies, hobbyists, and people who simply want the tool. You do not need permission to experiment, fork, or propose ideas.

If you find something that can be improved, open an issue or submit a pull request.

## Ground rules

1. **Be respectful.** Disagreement is fine; hostility is not. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
2. **Search existing issues** before opening a duplicate.
3. **Bugs are welcome** even if you do not know how to fix them.
4. **Feature ideas are welcome.**
5. **Experimental PRs are welcome** — label them clearly and keep them focused.
6. **Small improvements are welcome** (docs, typo fixes, DX, tests).
7. **Documentation improvements are welcome.**
8. **New model/provider integrations are welcome** (as adapters, not hard-wired core logic).
9. **New language support is welcome** (adapters + fixtures/eval coverage) — see language policy below.
10. **New hardware/audio experiments are welcome.**
11. **AI-generated contributions are allowed** (Cursor, Codex, Claude Code, Copilot, and others).
12. **Humans remain responsible** for reviewing and testing AI-generated code before submitting it.
13. **Never commit** API keys, credentials, private meeting recordings, transcripts, or personal data.
14. **Add tests** where reasonably applicable.
15. **Explain what a PR changes and why.**
16. **Breaking architectural changes** should normally be discussed in an issue first.

We want contributions, not paperwork. Keep process light.

## Quick start for contributors

```bash
git clone https://github.com/Jensvatland/physical-meeting-copilot.git
cd physical-meeting-copilot
bash scripts/try.sh          # first run / demo
bash scripts/mac-smoke.sh    # full lint + tests
```

No microphone and no API keys. Details: [docs/MAC.md](docs/MAC.md).

Useful docs before larger changes:

- [docs/STATUS.md](docs/STATUS.md) — what works vs simulated today
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — planes, packages, adapters
- [AGENTS.md](AGENTS.md) — guidance for humans and coding agents
- [docs/ROADMAP.md](docs/ROADMAP.md) — planned work

## Language policy (MVP)

- **Meeting pair:** Mandarin (`zh-CN`) + English (`en`) only for fixtures, demos, and default config.
- **Repo discussion / PR / issues:** English preferred (widest contributor reach). Simplified Chinese welcome in issues when clarifying China-deploy topics.
- **Docs:** English is canonical. Keep `README.zh-CN.md` (and small zh mirrors) in sync when changing user-facing status.
- **More spoken languages:** contribute as adapters + eval fixtures after v0.2 real ASR lands — don’t expand MVP defaults to a third language yet.

## Design boundaries (please preserve)

1. Meeting Core stays **provider-independent**. Put vendor logic behind adapters.
2. Do **not** embed Hermes/OpenClaw/CRM/research-host business logic in `packages/meeting_core`.
3. Raw realtime audio travels over **WebSocket/WebRTC**, not MCP.
4. MCP carries structured context, tools, findings, alerts, and actions.
5. OpenAI (or any single cloud vendor) must **never** be mandatory.
6. Original transcript text is immutable; claims evolve via state and evidence.
7. Label simulated adapters clearly in UI and docs until a real path is default.
8. Voice biometrics remain optional, consent-gated, separable, and deletable.

## Development commands

```bash
uv sync --group dev
uv run ruff check .
uv run ruff format --check .
uv run pytest -q
uv run python -m meeting_core.demo.simulate_meeting
uv run python -m meeting_core.eval.harness
```

Optional live UI (ASR text is still simulated):

```bash
uv run meeting-gateway
# Chrome → http://127.0.0.1:8787 → accept consent → Start meeting
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

- Target the repository default branch (prefer `main` once that is the default).
- Keep PRs focused and honest about sim vs real adapters; mention STATUS impact.
- Fill out the PR template briefly.
- Do not remove the Simulated ASR UI notice unless a real ASR path is the default.
- Forks and private experiments need no approval. Merges into this repo should stay reasonably secure, private, compatible, and maintainable.

## Security reports

Do not open public issues for vulnerabilities. See [SECURITY.md](SECURITY.md).

## Privacy

This project can process real conversations. Operators are responsible for complying with applicable laws and obtaining required consent before recording, transcribing, or processing meetings. See [docs/PRIVACY.md](docs/PRIVACY.md).

## Code of conduct

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
