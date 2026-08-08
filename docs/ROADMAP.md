# Roadmap

Phases are labels for history — **shipping truth lives in [STATUS.md](STATUS.md)**.  
Rule: a speech/provider phase is not “done” until it works **without** sim adapters for that capability.

## v0.1 — Public MVP (now)

Goal: an honest, local, contributor-friendly meeting runtime + MCP surface.

| Item | State |
|------|--------|
| Meeting Core + SQLite + protocol events | **ship** |
| Offline smoke + simulate_meeting | **ship** |
| Browser WebSocket capture UI | **ship** (sim ASR labeled) |
| MCP stdio for Hermes/OpenClaw configs | **ship** |
| Pre-meeting, claims, research lifecycle, export | **ship** (heuristics / sim bridge) |
| Docker Compose (sim stack) | **ship** |
| Docs: EN primary + zh-CN README thin set | **ship** |
| Minimal consent UX (browser) | **ship** |
| Real ASR / LiveKit / AirPods / iOS | **out** |

**MVP acceptance:** fresh clone → `./scripts/try.sh` / `./scripts/mac-smoke.sh` OK → optional browser shows **Simulated ASR** banner → MCP `--list` works with shared DB.

## v0.2 — First real speech path

- One local/China ASR adapter (e.g. FunASR) behind `SpeechRecognitionAdapter`
- Keep Mandarin originals; improve EN translation path
- `docker-compose.china.yml` actually runs that path without OpenAI

## v0.3 — Production realtime

- LiveKit adapter wired; reconnect/health matrix
- Diarization beyond round-robin; audio fixture eval

## Later (backlog)

| Theme | Notes |
|-------|--------|
| Adapter SDK + community tiers | After one real third-party adapter |
| Postgres optional storage | Same `StorageAdapter` contract |
| Restaurant / noise golden tests | Audio metrics, not text-only harness |
| iPhone / iPad / AirPods | Phases formerly 30–34 |
| Enterprise privacy / consent automation | Formerly 43 |
| Production v1.0 | Golden Acceptance Test (six-person China dinner) |

## Historical phase index (0–45)

Kept for continuity with earlier planning. Status values:

- **ship** — in v0.1 MVP  
- **sim** — structure exists; provider is simulated/stub  
- **partial** — incomplete  
- **later** — backlog  

| Phase | Name | Status |
|------:|------|--------|
| 0 | Repository / architecture | ship |
| 1 | Meeting Core | ship |
| 2 | Live audio (WS slice) | ship (LiveKit later) |
| 3 | Live transcription | sim |
| 4 | Diarization | sim |
| 5 | Translation | sim |
| 6 | Browser UI | ship |
| 7 | Meeting MCP | ship |
| 8 | Hermes vertical slice | sim host research |
| 9 | Private speech | sim TTS |
| 10 | OpenClaw | ship (thin mirror) |
| 11 | China profile | partial (compose labels) |
| 12 | Evaluation suite | ship (text scenarios) |
| 13 | Reliability / fallbacks | partial |
| 14 | Security / privacy baseline | partial |
| 15–20 | Pre-meeting → history API | ship |
| 21 | Storage abstraction | partial (Postgres stub) |
| 22 | Self-hosting | ship (sim stack) |
| 23–29 | Profiles / hardware / noise | later |
| 30–45 | iOS + production v1.0 | later |

## Golden Acceptance Test (v1.0 gate — not MVP)

Six people at a restaurant/business table in China; four Mandarin, one English, one code-switching; restaurant noise.

Must: real capture; usable speaker separation; Mandarin + English translation; quick speaker naming; Hermes continuously informed; detect material claim; background research without stopping transcription; compare with prior project info; contradiction or insufficient evidence; sourced finding; private AirPods alert; continue recording; structured post-meeting package.

This test outranks feature count for **v1.0**, not for public **v0.1**.
