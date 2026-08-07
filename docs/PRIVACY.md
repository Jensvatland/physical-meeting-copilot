# Privacy

## Principles

1. Recording and analysis require **explicit, informed consent**.
2. Store the **minimum** needed for the user’s meeting workflow.
3. Design for **local / self-hosted** processing and regional data residency.
4. Original statements are retained with provenance; agent interpretations are separate objects.

## Consent

- Session start must surface recording/analysis status to the operator.
- Mapping a speaker to a named person is operator-driven.
- Voice biometric enrollment is **optional**, **separately consented**, **separately stored**, **exportable**, and **deletable**. Silent enrollment is a defect.

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
