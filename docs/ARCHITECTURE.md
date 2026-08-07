# Architecture

## Purpose

Physical Meeting Copilot is a **provider-independent meeting runtime**. It listens to physical conversations, normalizes realtime speech events, and exposes structured meeting state to personal AI hosts (Hermes, OpenClaw, others) over MCP.

The core does **not** own personal memory, CRM, document systems, research engines, ASR models, diarization models, or WebRTC stacks. Those live behind adapters or in the agent host.

## Planes

### Realtime plane

Audio, VAD, transcript/translation deltas, speaker turns, and private playback travel over **WebRTC / WebSocket** (LiveKit preferred).

### Agent plane

Meeting context, participants, transcript search, claims, evidence, findings, alerts, and actions travel over **MCP**.

```text
PHYSICAL MEETING
  ↓
CAPTURE (browser/Mac/iPhone/table mic/wearable)
  ↓
REALTIME MEDIA — LiveKit preferred
  ├─ SpeechRecognitionAdapter
  ├─ DiarizationAdapter
  ├─ SpeakerIdentityAdapter (optional)
  └─ TranslationAdapter
  ↓
MEETING CORE
  ├─ normalized events / session state
  ├─ transcript / translation
  ├─ participants / speaker mapping
  ├─ claims / commitments / decisions / questions
  └─ findings / evidence / alerts
  ↓                         ↓
Realtime UI             MEETING MCP
browser / iOS / iPad        ├─ Hermes
                            ├─ OpenClaw
                            └─ other MCP agents
```

## Packages

| Package | Role |
|---------|------|
| `packages/protocol` | Versioned JSON Schemas for events and resources |
| `packages/meeting_core` | Session lifecycle, event bus, stores, adapter contracts |
| `packages/mcp_server` | MCP resources + tools over Meeting Core |
| `integrations/hermes` | Skill + MCP config + event bridge (no host logic in core) |
| `integrations/openclaw` | Second reference integration |
| `clients/web` | Browser prototype UI |

## Adapter contracts

Stable interfaces (capability discovery, languages, streaming/batch, health, graceful failure, latency metrics):

- `CaptureAdapter`
- `RealtimeTransportAdapter`
- `SpeechRecognitionAdapter`
- `DiarizationAdapter`
- `SpeakerIdentityAdapter` (optional, consent-gated)
- `TranslationAdapter`
- `TextToSpeechAdapter`
- `StorageAdapter`
- `AgentBridgeAdapter`

Initial candidates (none mandatory): LiveKit; FunASR/SenseVoice; 3D-Speaker/pyannote; optional OpenAI Realtime; Qwen/OpenAI-compatible endpoints; provider/local TTS.

## User modes

| Mode | Behavior |
|------|----------|
| `INTERPRETER` | Continuous / near-continuous translation |
| `COPILOT` (default) | Summaries, risks, contradictions, research, suggested questions |
| `SILENT` | Visual notifications; audio only for critical alerts |

## Persistence

Default: SQLite via `StorageAdapter` (local-first). Optional PostgreSQL later (Phase 21) without changing core domain logic.

## China profile

China is first-class. The global stack and China stack share Meeting Core and protocol; provider selection differs. See [CHINA.md](CHINA.md).

## Non-goals (core)

- Building a new personal assistant
- Embedding Hermes/OpenClaw business logic
- Mandating any single cloud ASR/LLM vendor
- Treating AirPods as the sole room microphone
