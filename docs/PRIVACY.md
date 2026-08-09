# Privacy

## Operator responsibility

Physical Meeting Copilot can record, transcribe, translate, and analyze real conversations.

**You (the operator / deployer) are responsible for complying with applicable laws and for obtaining any required consent before recording, transcribing, or otherwise processing meetings or biometric data.**

This document describes product principles and technical defaults. It is **not** country-by-country legal advice.

## Principles

1. Recording and analysis require **explicit, informed consent**.
2. Store the **minimum** needed for the user’s meeting workflow.
3. Design for **local / self-hosted** processing and regional data residency.
4. Original statements are retained with provenance; agent interpretations are separate objects.

## Consent

- Browser UI requires an explicit consent checkbox before capture can start; the gateway rejects session create without `consent_recorded=true`.
- Meeting Core blocks transcript/audio ingest until `record_consent(recorded=True)`.
- Mapping a speaker to a named person is operator-driven.
- Voice biometric enrollment is **optional**, **separately consented**, **separately stored**, **exportable**, and **deletable** (`meeting.delete_biometrics`). Silent enrollment is a defect.
- Do not commit real meeting recordings, transcripts, or personal data to the repository or shared fixtures.

## Biometrics

Voiceprints are sensitive biometric data (GDPR special category / PIPL sensitive personal information). Meeting Core keeps identity adapters behind a consent flag; disabling biometrics must leave transcription/diarization usable.

## Retention

- Default: keep session artifacts until user deletes them.
- Enterprise: retention policies (Phase 43) without changing core concepts.
- Deletion must cover audio references, transcripts, mappings, biometrics, and derived findings.

## Modes and private alerts

Private speech / AirPods alerts are user-directed outputs. They must not leak to shared room speakers by default. Capture routing and private playback are independently routable.

## Regional notes

- **GDPR:** lawful basis, DPIA guidance, DSR (access/erase) before enterprise release.
- **PIPL:** China profile favors in-country processing; cross-border transfer requires explicit configuration — not a silent default.

Practical deployment checklists expand in Phase 43. See also [CHINA.md](CHINA.md) and [SECURITY.md](SECURITY.md).
