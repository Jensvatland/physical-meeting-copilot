# Roadmap

Phases are complete only when code, tests, docs, fallbacks, license notes, and acceptance criteria pass — without provider-specific leakage into Meeting Core.

For a short “what works today” table, see [STATUS.md](STATUS.md).

## Current status

| Phase | Name | Status |
|------:|------|--------|
| 0 | Repository / architecture | **done** |
| 1 | Meeting Core | **done** |
| 2 | Live audio (WebSocket vertical slice) | **done** (PCM ingest + VAD + sim diarization/ASR; LiveKit SDK optional stub) |
| 3 | Live transcription | **partial** (sim ASR + FunASR stub; Mandarin retained) |
| 4 | Diarization | **done** (sim adapter + speaker.turn; production models TBD) |
| 5 | Translation | **partial** (glossary sim; Qwen adapter TBD) |
| 6 | Browser UI | **done** (transcript, people, alerts, findings, questions, research) |
| 7 | Meeting MCP | **done** (resources/tools + stdio MCP SDK transport) |
| 8 | Hermes | **done** (event bridge + non-blocking research vertical slice) |
| 9 | Private speech | **done** (sim TTS + queued/spoken events; AirPods path TBD) |
| 10 | OpenClaw | **done** (event bridge + mcp.json; same core unchanged) |
| 11 | China profile | **partial** (`docker-compose.china.yml` + FunASR stub) |
| 12 | Evaluation suite | **done** (one-command harness; expand scenarios ongoing) |
| 13 | Reliability / fallbacks | **partial** (health aggregate, crash-safe SQLite; full matrix TBD) |
| 14 | Security / privacy baseline | **partial** (consent, audit log, biometric clear, deletion) |
| 15 | Pre-meeting context | **done** |
| 16 | Intelligence primitives | **done** (heuristic numbers/dates/prices/risks) |
| 17 | Background research lifecycle | **done** |
| 18 | Contradiction / change detection | **done** (prior_facts compare) |
| 19 | Post-meeting package | **done** |
| 20 | Session history API | **done** (list/search/delete via manager + MCP) |
| 21 | Storage abstraction | **partial** (SQLite + memory; Postgres stub) |
| 22 | Self-hosting | **done** (Docker Compose + health + env templates) |
| 23–29 | Profiles / adapters / hardware | planned / stubs |
| 30–45 | iOS + production | planned |

## Phases 0–29 (runtime foundation)

### 0 — Repository / architecture

Inspect repo, docs/ADRs, protocol, CI, licenses.

**Accept:** CI works and implementation starts.

### 1 — Meeting Core

Sessions, event bus, schemas, participants/speakers, transcript/translation stores, SQLite, tests.

**Accept:** Simulated multi-speaker meeting maintains state.

### 2 — Live audio

Browser mic → LiveKit → backend; VAD/timestamps/sync.

**Accept:** Physical speech enters core live. *(WebSocket PCM path satisfies acceptance; LiveKit preferred for production.)*

### 3 — Live transcription

First ASR adapter; Mandarin + English partial/final text.

**Accept:** Mandarin appears live in Chinese.

### 4 — Diarization

Stable Speaker 1/2/3; overlap where supported.

**Accept:** Usable four-person attribution.

### 5 — Translation

Mandarin→English retaining original/speaker/time/provenance.

**Accept:** Conversational latency.

### 6 — Browser UI

Transcript, translation, speakers, alerts, research status, suggested questions, Ask Agent, People.

**Accept:** Usable without CLI.

### 7 — Meeting MCP

Resources/tools + mock-agent tests.

**Accept:** External MCP client can inspect/control state.

### 8 — Hermes

Skill + MCP/event bridge. Demo material claim → background research + suggested question while transcription continues.

**Accept:** Full Hermes vertical slice.

### 9 — Private speech

Mac→AirPods TTS, priority queue/interruption.

**Accept:** Private Hermes alert while capture continues. *(Sim TTS lifecycle done; device path TBD.)*

### 10 — OpenClaw

Second reference integration.

**Accept:** Same core works unchanged.

### 11 — China profile

FunASR/SenseVoice + 3D-Speaker + Qwen-compatible + local/China TTS; `docker-compose.china.yml`.

**Accept:** Mandarin workflow without OpenAI.

### 12 — Evaluation suite

2/4/6 speakers, overlap, Mandarin/English/code-switching, technical terms, numbers, dates, prices, negation, restaurant/factory noise, echo.

**Accept:** One-command benchmark report.

### 13 — Reliability / fallbacks

Health, retry, reconnect, degraded modes, provider fallback, crash-safe sessions.

**Accept:** Optional provider failure does not lose meeting state.

### 14 — Security / privacy baseline

Encryption, secrets, retention/deletion, consent state, auditability, local-first defaults.

**Accept:** Threat model + automated checks.

### 15 — Pre-meeting context contract

Agenda, participants, roles, files, prior sessions, goals, watch items.

**Accept:** Hermes can prepare session before audio.

### 16 — Intelligence primitives

Normalized claims, commitments, decisions, questions, numbers, deadlines, risks.

**Accept:** Structured timeline objects.

### 17 — Background research lifecycle

Correlation IDs, started/completed, stale-result handling, evidence provenance.

**Accept:** Concurrent checks do not block meeting.

### 18 — Contradiction / change detection

Agents compare current statements with prior meetings/docs.

**Accept:** Changed price/date/spec generates finding.

### 19 — Post-meeting package

Transcript, translation, participants, decisions, commitments, open questions, findings, claims, actions.

**Accept:** Deterministic structured export.

### 20 — Session history API

Retrieve/search prior sessions.

**Accept:** Agent reliably references previous meeting.

### 21 — Storage abstraction

SQLite default, optional PostgreSQL.

**Accept:** Backend swap without core logic changes.

### 22 — Self-hosting

Docker Compose, health, env templates, backup/restore.

**Accept:** Fresh-machine deployment from docs.

### 23 — Global profile

`docker-compose.global.yml`, optional cloud adapters.

**Accept:** Global stack independent of China stack.

### 24 — Adapter SDK

Python/TypeScript SDKs, fixtures, conformance tests.

**Accept:** Sample third-party adapter passes.

### 25 — Community adapter tiers

Core / Verified / Community metadata and policy.

**Accept:** Support level declared without core changes.

### 26 — Hardware abstraction

External table mics / future wearables via `CaptureAdapter`.

**Accept:** Capture device swap does not affect core.

### 27 — Multi-mic experiments

Optional channel-aware capture / beamforming support.

**Accept:** Multi-channel metadata supported.

### 28 — Restaurant benchmark

Noisy dinner tests: music, cutlery, nearby voices, overlap, moving speakers.

**Accept:** Baseline + regression metrics.

### 29 — Technical vocabulary

Provider hotwords / context hints.

**Accept:** Domain glossary improves benchmark without core coupling.

## Phases 30–45 (iOS + production)

| Phase | Name | Accept (short) |
|------:|------|----------------|
| 30 | Native iOS foundation | App connects to dev Meeting Core |
| 31 | iPhone Capture Client | Real physical meeting capture/control |
| 32 | iPhone Live Copilot UI | Meeting followable primarily from iPhone |
| 33 | AirPods Integration | Private advice + independent room capture |
| 34 | iPad Meeting Console | Preferred table-side console |
| 35 | Speaker Management | Unknown speaker named in seconds |
| 36 | Pre-Meeting Intelligence UX | Prepared from same app |
| 37 | Proactive Meeting Intelligence | Useful findings without commands |
| 38 | Post-Meeting Intelligence | Workflow finishes in app |
| 39 | Dinner/Restaurant Mode | Useful in noisy dinner benchmark |
| 40 | Offline/China Mode | Core experience without blocked services |
| 41 | Provider/Adapter Ecosystem | Provider change without client rebuild |
| 42 | Wearables/Hardware | One non-phone accessory via contracts |
| 43 | Enterprise Privacy/Security/Consent | Enterprise deploy without concept changes |
| 44 | Open-Source Release | External developer can deploy/contribute |
| 45 | Production v1.0 | Golden Acceptance Test passes |

## Golden Acceptance Test

Six people at a restaurant/business table in China; four Mandarin, one English, one code-switching; restaurant noise.

Must: capture; usable speaker separation; Mandarin + English translation; quick speaker naming; Hermes continuously informed; detect material technical claim; background research without stopping transcription; compare with prior project info; find contradiction or insufficient evidence; return concise sourced finding; private AirPods alert with suggested question; continue recording; structured post-meeting package.

This test outranks feature count.
