# Security policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.1.x (preview) | Best-effort — report issues; no SLA |

## Threat model (baseline)

See [docs/SECURITY.md](docs/SECURITY.md) for the architectural threat model. Important v0.1 facts:

- MCP is **local stdio** with **no authentication** — treat as a same-user trust boundary.
- Gateway has **no session auth tokens** yet — bind to `127.0.0.1` for local demos.
- Do not expose `meeting-gateway` to the public internet without adding auth and TLS.

## Reporting a vulnerability

Please **do not** open a public GitHub issue for security vulnerabilities.

Email the repository owner listed on the GitHub profile for
[Jensvatland/physical-meeting-copilot](https://github.com/Jensvatland/physical-meeting-copilot)
with:

- description and impact
- reproduction steps
- any suggested fix

We will acknowledge when we can and coordinate disclosure.

## Prefer local-first

Default deployment assumes self-hosted SQLite and optional local/China adapters. Cloud keys are never required for the smoke path.
