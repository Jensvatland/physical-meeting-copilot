# Browser client

Copilot prototype UI in `public/index.html` (v0.1).

## Run

Prefer the offline smoke first ([docs/MAC.md](../../docs/MAC.md)):

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
- This WebSocket path exists so local demos work without cloud credentials.
- Point MCP at the same `MEETING_CORE_DB` so Hermes/OpenClaw can inspect the live session.
