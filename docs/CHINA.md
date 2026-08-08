# China deployment profile

China is a **first-class** profile, not a fork. Same Meeting Core + protocol; provider selection differs.

## v0.1 honesty

`docker-compose.china.yml` sets **profile labels / env placeholders**. It does **not** yet start FunASR, 3D-Speaker, or Qwen containers. Mandarin workflow without OpenAI is the **goal**; today the smoke path uses **sim ASR** and needs no OpenAI either.

## Goals

- Mandarin-primary physical meetings with English operator assistance
- No mandatory dependency on blocked/unavailable Western APIs
- Local or in-country ASR, diarization, LLM, and TTS paths
- Same Meeting Core + protocol as the global profile

## Stack

| Concern | Candidate | v0.1 |
|---------|-----------|------|
| Realtime transport | Self-hosted LiveKit / WebSocket slice | WebSocket done; LiveKit stub |
| ASR | FunASR / SenseVoice | FunASR stub + sim ASR |
| Diarization | 3D-Speaker / local pyannote where license OK | Sim diarization |
| LLM / translation | Qwen-compatible endpoints | Glossary sim |
| TTS | Local / China-region TTS | Sim TTS lifecycle |
| Compose | `docker-compose.china.yml` | Env labels only |

## Rules

1. OpenAI must never be required for the China accept path.
2. Core domain code must not import China-only SDKs.
3. Adapter capability discovery declares languages and online/offline support.
4. Docs: English canonical + Simplified Chinese README for contributors; expand zh mirrors as the China path becomes real (do not wait for iOS).

## Languages

MVP meeting pair remains **`zh-CN` + `en`**. Additional Chinese topolects or other languages are post-MVP adapter work.

## Acceptance (target — v0.2+)

A Mandarin workflow completes without OpenAI: capture → Chinese transcript text → translation → MCP state visible to an agent host.
