# China deployment profile

China is a **first-class** profile, not a fork.

## Goals

- Mandarin-primary physical meetings with English user assistance
- No mandatory dependency on blocked/unavailable Western APIs
- Local or in-country ASR, diarization, LLM, and TTS paths
- Same Meeting Core + protocol as the global profile

## Stack (Phase 11 / 40)

| Concern | Candidate | Status |
|---------|-----------|--------|
| Realtime transport | Self-hosted LiveKit / WebSocket slice | WebSocket done; LiveKit stub |
| ASR | FunASR / SenseVoice | Env-selectable FunASR stub + default sim ASR |
| Diarization | 3D-Speaker (and/or local pyannote where license OK) | Sim diarization |
| LLM / translation assist | Qwen-compatible OpenAI-style endpoints | Glossary sim |
| TTS (private alerts) | Local / China-region TTS adapter | Sim TTS lifecycle |
| Compose | `docker-compose.china.yml` | Present (profile/env only until models wire up) |

## Env notes (today)

- `MEETING_PROFILE=china` labels the deployment profile in `/health`.
- `MEETING_ASR=sim` (default) keeps the simulated ASR demo path.
- `FUNASR_ENABLED=1` or `MEETING_ASR=funasr` selects `FunASRSpeechRecognitionAdapter`.
- That adapter is still a **stub**: health is degraded and `transcribe_stream` raises `NotImplementedError` until SenseVoice/FunASR is wired.
- For demos, leave `FUNASR_ENABLED=0` and `MEETING_ASR=sim`.

## Rules

1. OpenAI must never be required for the China accept path.
2. Core domain code must not import China-only SDKs.
3. Adapter capability discovery declares languages and online/offline support.
4. Documentation ships in English and Simplified Chinese before open-source release (Phase 44); Gitee mirror strategy, not a permanent regional fork.

## Acceptance (Phase 11)

A Mandarin workflow completes without OpenAI: capture → transcript (Chinese text) → translation → MCP state visible to an agent host.
*(Today this path works via simulated ASR text, not FunASR.)*
