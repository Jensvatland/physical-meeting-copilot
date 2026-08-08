# Status — what works today (v0.1 MVP)

Honest snapshot for contributors and people evaluating the project. Prefer this over phase-number folklore.

## Works now (sim-backed where noted)

| Capability | Notes |
|------------|--------|
| Meeting Core sessions, event bus, SQLite | Real |
| Offline try / smoke (`./scripts/try.sh`, `./scripts/mac-smoke.sh`) | Real — no mic, no API keys |
| Simulated multi-speaker demo + Hermes research slice | Real orchestration; fixture text |
| Browser mic → WebSocket PCM → energy VAD | Real capture path |
| MCP stdio tools/resources | Real (local, no auth) |
| Claims / findings / alerts / suggested questions | Real heuristics + demo path |
| Post-meeting export, history search, prior-fact compare | Real |
| Docker Compose gateway | Runs the **sim** stack |
| Consent UI surface at session start (browser) | Present; operators still own legal consent |

## Simulated / stub (not production speech)

| Capability | Notes |
|------------|--------|
| ASR | `[sim:…]` text — not real Mandarin/English recognition |
| Diarization | Energy / round-robin style sim labels |
| Translation | Tiny glossary / stub |
| TTS / AirPods private speech | Lifecycle events + silent WAV; no real device path yet |
| LiveKit | Capability stub until SDK + env configured |
| FunASR / China models | Env flags + stub; not a full runtime wire-up |
| Postgres storage | Stub adapter — use SQLite |
| Gateway auth | None yet — local bind recommended |

## Planned / not started

- Production ASR/MT/diarization adapters (incl. China-first stack)
- LiveKit as preferred realtime transport
- Native iOS / iPad clients, wearables
- Stronger eval fixtures (audio replay, noise/overlap / restaurant golden-acceptance suite)
- Enterprise retention/encryption/DPIA automation
- Authenticated remote MCP / gateway exposure
- Community adapter marketplace

See [ROADMAP.md](ROADMAP.md) for phase detail.

## Supported meeting languages (v0.1)

**`zh-CN` (Mandarin) + `en` (English) only.**

Protocol fields accept BCP-47 tags for future adapters, but MVP docs, fixtures, and contribution focus stay on this pair. See [CONTRIBUTING.md](../CONTRIBUTING.md).
