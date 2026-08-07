# License notes

Core project license: **Apache-2.0**.

Review this file before adding dependencies. Prefer permissive licenses (Apache-2.0, MIT, BSD). Copyleft or research-only model weights must stay behind optional adapters and must not enter the maintained core.

## Runtime (Phase 0–1)

| Component | License | Notes |
|-----------|---------|-------|
| Python | PSF | Interpreter |
| pydantic | MIT | Domain models |
| jsonschema | MIT | Schema validation |
| pytest | MIT | Tests |
| ruff | MIT | Lint |
| mcp (Python SDK) | MIT | MCP server (Phase 7+) — verify version on add |
| starlette | BSD-3-Clause | Realtime gateway |
| uvicorn | BSD-3-Clause | ASGI server |
| websockets | BSD-3-Clause | WS client/server support |

## Planned adapters (not yet vendored)

| Candidate | Typical license posture | Gate |
|-----------|-------------------------|------|
| LiveKit | Apache-2.0 | Preferred realtime |
| FunASR / SenseVoice | Check model + code licenses before bundling | China ASR |
| 3D-Speaker | Check before Core tier | China diarization |
| pyannote | MIT code; model weights may differ | Optional |
| Qwen models | Model license varies by release | China LLM |
| OpenAI APIs | Proprietary service ToS | Optional only |

## Policy

- **Core tier adapters:** Apache/MIT/BSD compatible code paths only.
- **Verified / Community:** May wrap other licenses if declared in adapter metadata.
- Model weights are not “code dependencies”; document redistribution limits separately.
