# Proposed good first issues

These are **real** starter tasks derived from the current codebase. Prefer opening GitHub issues from this list (label `good first issue`) rather than inventing busywork.

## Documentation / DX

1. **README demo media** — Add a short GIF or screenshots of the browser UI and `simulate_meeting` output (synthetic only; no real meeting audio).
2. **Fixture WAV replay path** — Document or sketch how to feed a checked-in synthetic PCM/WAV into the gateway for deterministic mic-less UI demos (`docs/MAC.md` already calls this out).
3. **China profile doc pass** — Align `docs/CHINA.md` wording with what `docker-compose.china.yml` and `funasr_stub.py` actually do today.

## Tests / tooling

4. **FunASR stub tests** — Expand `packages/meeting_core/tests/test_adapters.py` for enable/disable + `NotImplementedError` when `FUNASR_ENABLED=1` without a runtime.
5. **Eval scenario expansion** — Add text fixtures to `meeting_core.eval.harness` for code-switching, numbers/dates/prices, or negation (no proprietary audio required).
6. **Ruff format in contributor habit** — Ensure `uv run ruff format` is clean across packages (CI already checks).

## Adapters / integrations

7. **Qwen-compatible translation adapter skeleton** — Optional HTTP adapter behind `TranslationAdapter`, env-gated, with mocked unit tests (do not make it mandatory).
8. **LiveKit adapter next step** — Flesh `livekit_stub.py` toward a real optional SDK path with clear degraded health when unset.
9. **OpenClaw skill parity checklist** — Compare `integrations/openclaw` vs `integrations/hermes` and document/fix any missing bridge behaviors.

## UI / accessibility

10. **Browser accessibility pass** — Keyboard focus, labels, and contrast for controls in `clients/web/public/index.html` without removing the Simulated ASR honesty banner.
11. **Consent copy clarity** — Improve the session-start consent/recording notice so operators see responsibilities clearly (link to `docs/PRIVACY.md`).

## Privacy / security hygiene

12. **Gateway bind warning** — Surface a startup log warning when `MEETING_GATEWAY_HOST` is not loopback, reminding operators there is no auth yet.
13. **Redaction helper tests** — If adding log helpers for tokens, cover them with unit tests (no real secrets in fixtures).

## Larger (still valuable, maybe not “first”)

14. **Real FunASR/SenseVoice wire-up** — Optional extra; keep sim default until quality/docs catch up.
15. **Synthetic multi-speaker audio suite** — Checked-in generated audio for regression without a live room.

When filing: include pointers to files, a short definition of done, and whether the change stays sim-honest.
