# Proposed good first issues

These are **real** starter tasks derived from the current codebase. Prefer opening GitHub issues from this list (label `good first issue`) rather than inventing busywork.

## Documentation / DX

1. **README demo media** — Add a short GIF or screenshots of the browser UI and `simulate_meeting` output (synthetic only; no real meeting audio).
2. **Fixture WAV replay path** — Document or sketch how to feed a checked-in synthetic PCM/WAV into the gateway for deterministic mic-less UI demos (`docs/MAC.md` already calls this out).
3. **China profile doc pass** — Keep `docs/CHINA.md` aligned as FunASR wiring progresses beyond the stub/env selection path.

## Tests / tooling

4. **Eval scenario expansion** — Add text fixtures to `meeting_core.eval.harness` for negation or more code-switching (no proprietary audio required).
5. **Audio replay eval scaffold** — Start a synthetic PCM fixture path that the eval harness can mark as `audio` vs `text`.
6. **Ruff format in contributor habit** — Ensure `uv run ruff format` is clean across packages (CI already checks).

## Adapters / integrations

7. **Qwen-compatible translation adapter skeleton** — Optional HTTP adapter behind `TranslationAdapter`, env-gated, with mocked unit tests (do not make it mandatory).
8. **LiveKit adapter next step** — Flesh `livekit_stub.py` toward a real optional SDK path with clear degraded health when unset.
9. **OpenClaw skill parity checklist** — Compare `integrations/openclaw` vs `integrations/hermes` and document/fix missing auto-research behaviors.

## UI / accessibility

10. **Browser accessibility pass** — Keyboard focus, labels, and contrast for controls in `clients/web/public/index.html` without removing the Simulated ASR honesty banner or consent checkbox.
11. **Consent copy clarity** — Improve the session-start consent/recording notice so operators see responsibilities clearly (link to `docs/PRIVACY.md` already present).

## Privacy / security hygiene

12. ~~**Gateway bind warning**~~ — Done: non-loopback warning + `MEETING_ALLOW_INSECURE_BIND` gate; Docker host publish defaults to `127.0.0.1`.
13. **Redaction helper tests** — If adding log helpers for tokens, cover them with unit tests (no real secrets in fixtures).
14. **Optional gitleaks/trufflehog CI** — Add a secret-scanning workflow beyond `.gitignore` hygiene.

## Larger (still valuable, maybe not “first”)

15. **Real FunASR/SenseVoice wire-up** — Optional extra; keep sim default until quality/docs catch up.
16. **Synthetic multi-speaker audio suite** — Checked-in generated audio for regression without a live room.
17. **Gateway session tokens** — Minimal auth before advertising non-loopback binds.

When filing: include pointers to files, a short definition of done, and whether the change stays sim-honest.
