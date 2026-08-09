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

## Threats (current vs planned)

| Threat | Current mitigation (v0.1) | Planned |
|--------|---------------------------|---------|
| Unauthorized session join | Loopback bind defaults; Docker host publish `127.0.0.1`; non-loopback requires `MEETING_ALLOW_INSECURE_BIND=1` | Session tokens / gateway authn |
| MCP tool abuse | Local stdio only (same-user trust); no network MCP transport yet | Authn/authz on remote MCP |
| Provider data exfiltration | Adapter allowlists; China/local profile; no mandatory cloud | Stronger adapter policy controls |
| Secret leakage in logs | `.gitignore` for `.env` / recordings; never commit secrets | Dedicated secret scanners in CI |
| Stolen laptop disk | OS disk encryption recommended | Optional at-rest encryption |
| Silent voice enrollment | Forbidden — explicit biometric consent flag required; `meeting.delete_biometrics` | Stronger enrollment UX |
| Capture without consent | Consent required before transcript/audio ingest; browser checkbox | Richer legal notice / retention UX |
| Stale research acting as fact | Provenance + claim states; correlation IDs | Richer evidence UX |

## Defaults

- Local processing preferred
- No biometric enrollment without separate consent
- Recording/transcription blocked until `consent_recorded=true`
- Minimum retention; explicit deletion APIs (Phase 14)
- Provider credentials only via environment / secret store — never committed
- Local demos should bind the gateway to `127.0.0.1`; do not expose unauthenticated Docker/gateway ports to the public internet

## Automated checks (Phase 0+)

- `.gitignore` excludes `.env`, DBs, recordings, and transcripts (hygiene — not a secret scanner)
- GitHub CodeQL workflow (`.github/workflows/codeql.yml`)
- Dependabot for `uv` and GitHub Actions (`.github/dependabot.yml`)
- License review before new dependencies (`docs/LICENSES.md`)
- Unit tests for recording consent gates and biometric clear APIs

Vulnerability reporting process: [SECURITY.md](../SECURITY.md) at the repository root.
