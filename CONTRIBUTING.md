# Contributing

This is an open experiment to build an AI copilot for real-world, face-to-face meetings.

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
9. **New language support is welcome** (adapters + fixtures/eval coverage).
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
chmod +x scripts/mac-smoke.sh
./scripts/mac-smoke.sh
```

Offline smoke needs no microphone and no API keys. Details: [docs/MAC.md](docs/MAC.md).

Useful docs before larger changes:

- [docs/STATUS.md](docs/STATUS.md) — what works vs simulated today
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — planes, packages, adapters
- [AGENTS.md](AGENTS.md) — guidance for humans and coding agents
- [docs/ROADMAP.md](docs/ROADMAP.md) — planned work

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
export MEETING_CORE_DB=~/.physical-meeting-copilot/meetings.db
uv run meeting-gateway
# Chrome → http://127.0.0.1:8787
```

## Pull requests

- Target the repository default branch (prefer `main` once that is the default).
- Keep PRs focused and honest about sim vs real adapters.
- Fill out the PR template briefly.
- Forks and private experiments need no approval. Merges into this repo should stay reasonably secure, private, compatible, and maintainable.

## Security reports

Do not open public issues for vulnerabilities. See [SECURITY.md](SECURITY.md).

## Privacy

This project can process real conversations. Operators are responsible for complying with applicable laws and obtaining required consent before recording, transcribing, or processing meetings. See [docs/PRIVACY.md](docs/PRIVACY.md).
