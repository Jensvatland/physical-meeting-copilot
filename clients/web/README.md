# Browser client

Phase 2 vertical slice lives in `public/index.html`.

## Run

```bash
uv run meeting-gateway
```

Open `http://127.0.0.1:8787`. The page captures microphone PCM, downsamples to 16 kHz, and streams base64 frames over WebSocket to Meeting Core.

## Notes

- LiveKit remains the preferred production realtime transport.
- This WebSocket path exists so local demos work without cloud credentials.
- Phase 6 expands the full Copilot UI (alerts, People, Ask Agent, research).
