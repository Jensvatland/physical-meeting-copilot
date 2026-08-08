# Browser client

Copilot prototype UI in `public/index.html`.

## Run

Prefer the offline smoke first ([docs/MAC.md](../../docs/MAC.md)):

```bash
bash scripts/try.sh
uv run meeting-gateway
```

Open `http://127.0.0.1:8787` in **Chrome**. The page captures microphone PCM, downsamples to 16 kHz, and streams frames over WebSocket to Meeting Core. Side panels show people, alerts, findings, suggested questions, and research status.

## Notes

- LiveKit remains the preferred production realtime transport.
- This WebSocket path exists so local demos work without cloud credentials.
- Transcript text is **simulated ASR** until FunASR (or another adapter) is wired.
- Point MCP at the same `MEETING_CORE_DB` so Hermes/OpenClaw can inspect the live session.
