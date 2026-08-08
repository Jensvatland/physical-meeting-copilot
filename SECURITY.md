# Security policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.1.x (preview) | Best-effort — report issues; no SLA |

## Important v0.1 trust boundaries

Architectural detail lives in [docs/SECURITY.md](docs/SECURITY.md). Facts that matter before exposing anything:

- MCP is **local stdio** with **no authentication** — treat it as a same-user trust boundary.
- The HTTP/WebSocket gateway has **no session auth** yet — prefer `MEETING_GATEWAY_HOST=127.0.0.1` for local demos.
- The default Docker Compose file binds the gateway to `0.0.0.0` for container networking. **Do not** expose it to the public internet without adding authentication and TLS.
- Never commit API keys, tokens, `.env` files, meeting recordings, or transcripts.

## Reporting a vulnerability

Please **do not** open a public GitHub issue for security vulnerabilities.

Prefer [GitHub Security Advisories](https://github.com/Jensvatland/physical-meeting-copilot/security/advisories/new) when available, or contact the repository owner listed on the GitHub profile for [Jensvatland/physical-meeting-copilot](https://github.com/Jensvatland/physical-meeting-copilot) with:

- description and impact
- reproduction steps
- any suggested fix

We will acknowledge when we can and coordinate disclosure.

## Prefer local-first

Default development assumes self-hosted SQLite and optional local/China adapters. Cloud keys are never required for the offline smoke path (`./scripts/mac-smoke.sh`).
