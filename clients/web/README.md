# Browser client

Copilot prototype UI in `public/index.html` (v0.1).

## Run

```bash
./scripts/mac-smoke.sh
export MEETING_CORE_DB=~/.physical-meeting-copilot/meetings.db
uv run meeting-gateway
```

Open `http://127.0.0.1:8787` in **Chrome**. Accept the consent checkbox, allow the mic, then Start. Side panels show people, alerts, findings, suggested questions, and research.

## Notes

- Persistent **Simulated ASR** banner is required until a real ASR adapter is the default.
- Meeting languages for MVP: **zh-CN + en**.
- LiveKit remains the preferred production realtime transport later.
- Point MCP at the same `MEETING_CORE_DB` so Hermes/OpenClaw can inspect the live session.
