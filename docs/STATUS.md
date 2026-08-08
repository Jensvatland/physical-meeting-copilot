# Status — what works today (v0.1 MVP)

Honest snapshot for contributors and evaluators. Prefer this over phase-number folklore.

## Works now (sim-backed where noted)

| Capability | Notes |
|------------|--------|
| Meeting Core sessions, events, SQLite | Real |
| Offline smoke (`./scripts/mac-smoke.sh`) | Real — no mic/keys |
| Simulated multi-speaker demo + Hermes research slice | Real logic; fixture text |
| Browser mic → WebSocket PCM → energy VAD | Real capture path |
| MCP stdio tools/resources | Real (local, no auth) |
| Post-meeting export, history search, prior-fact compare | Real heuristics |
| Docker Compose gateway | Runs **sim** stack |

## Simulated / stub (not production speech)

| Capability | Notes |
|------------|--------|
| ASR | `[sim:…]` text — not real Mandarin/English recognition |
| Diarization | Round-robin energy fixture |
| Translation | Tiny glossary / stub prefix |
| TTS / AirPods | Silent WAV + lifecycle events |
| LiveKit | Capability stub until SDK + env configured |
| FunASR / China models | Env flags / compose labels only |
| Postgres | Stub adapter — use SQLite |

## Not started

Native iOS / iPad clients, wearables, restaurant golden-acceptance audio suite, enterprise encryption/DPIA automation, community adapter marketplace.

## Supported meeting languages (v0.1)

**`zh-CN` (Mandarin) + `en` (English) only.**

Protocol fields accept BCP-47 tags for future adapters, but MVP docs, fixtures, and contribution focus stay on this pair. See [CONTRIBUTING.md](../CONTRIBUTING.md).
