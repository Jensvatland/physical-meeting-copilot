# Security

Baseline threat model for Physical Meeting Copilot. Expanded checks land in Phase 14 / 43.

## Assets

- Raw meeting audio
- Transcripts and translations
- Participant identity mappings
- Optional voice biometrics (high sensitivity)
- Claims, findings, private alerts
- Agent bridge credentials / MCP access tokens
- Prior meeting history and project context references

## Trust boundaries

1. Capture device ↔ Realtime transport (LiveKit/WebSocket)
2. Realtime adapters ↔ Meeting Core
3. Meeting Core ↔ MCP clients (Hermes/OpenClaw/others)
4. Meeting Core ↔ storage disk / optional remote DB
5. Optional cloud ASR/TTS/LLM providers

## Threats (initial)

| Threat | Mitigation |
|--------|------------|
| Unauthorized session join | Session tokens; local-first bind defaults |
| MCP tool abuse | Authn/authz on MCP; least-privilege tools |
| Provider data exfiltration | Adapter allowlists; China/local profile; no mandatory cloud |
| Secret leakage in logs | Redact tokens; never log raw biometrics |
| Stolen laptop disk | Optional at-rest encryption (Phase 14); OS disk encryption recommended |
| Silent voice enrollment | Forbidden — explicit consent flag required |
| Stale research acting as fact | Provenance + claim states; correlation IDs |

## Defaults

- Local processing preferred
- No biometric enrollment without separate consent
- Minimum retention; explicit deletion APIs (Phase 14)
- Provider credentials only via environment / secret store — never committed
- Local demos should bind the gateway to `127.0.0.1`; do not expose unauthenticated Docker/gateway ports to the public internet

## Automated checks (Phase 0+)

- CI secret scanning hygiene via not committing `.env`
- GitHub CodeQL workflow (`.github/workflows/codeql.yml`)
- Dependabot for `uv` and GitHub Actions (`.github/dependabot.yml`)
- License review before new dependencies (`docs/LICENSES.md`)
- Unit tests for consent gates on speaker identity APIs

Vulnerability reporting process: [SECURITY.md](../SECURITY.md) at the repository root.
