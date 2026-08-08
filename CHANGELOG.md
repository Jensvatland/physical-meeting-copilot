# Changelog

All notable changes to this project are documented in this file.  
Format based on [Keep a Changelog](https://keepachangelog.com/). Versioning follows semver; **0.x is preview**.

## [0.1.0] — 2026-08-08

### Added
- Meeting Core sessions, event bus, SQLite persistence, MCP stdio façade
- Browser WebSocket PCM capture gateway + Copilot side panels
- Simulated ASR / diarization / translation / TTS adapters (labeled)
- Hermes research vertical slice + OpenClaw event bridge mirror
- Pre-meeting context, intelligence primitives, contradiction helpers, post-meeting export
- Offline `scripts/mac-smoke.sh`, eval text harness, Docker Compose (sim stack)
- Public MVP docs: STATUS, MAC, CONTRIBUTING, CoC, EN + zh-CN README

### Known limitations
- No real speech recognition yet (browser shows Simulated ASR)
- LiveKit / FunASR / Postgres are stubs or labels only
- MCP has no authentication (local stdio trust model)
