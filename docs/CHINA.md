# China deployment profile

China is a **first-class** profile, not a fork.

## Goals

- Mandarin-primary physical meetings with English user assistance
- No mandatory dependency on blocked/unavailable Western APIs
- Local or in-country ASR, diarization, LLM, and TTS paths
- Same Meeting Core + protocol as the global profile

## Planned stack (Phase 11 / 40)

| Concern | Candidate |
|---------|-----------|
| Realtime transport | Self-hosted LiveKit |
| ASR | FunASR / SenseVoice |
| Diarization | 3D-Speaker (and/or local pyannote where license OK) |
| LLM / translation assist | Qwen-compatible OpenAI-style endpoints |
| TTS (private alerts) | Local / China-region TTS adapter |
| Compose | `docker-compose.china.yml` |

## Rules

1. OpenAI must never be required for the China accept path.
2. Core domain code must not import China-only SDKs.
3. Adapter capability discovery declares languages and online/offline support.
4. Documentation ships in English and Simplified Chinese before open-source release (Phase 44); Gitee mirror strategy, not a permanent regional fork.

## Acceptance (Phase 11)

A Mandarin workflow completes without OpenAI: capture → transcript (Chinese text) → translation → MCP state visible to an agent host.
