# Protocol

Canonical event schema is versioned from day one. Machine-validatable JSON Schemas for the common envelope and claims live in `packages/protocol/schemas/`. For v0.1, **Pydantic models in Meeting Core** are the complete runtime source of truth; additional event schemas will catch up as the protocol hardens.

**Current protocol version:** `0.1.0`  
**MVP languages:** `zh-CN`, `en`

## Common envelope

All events share:

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `event_id` | string (UUID) | yes | Unique event id |
| `protocol_version` | string | yes | Semver, e.g. `0.1.0` |
| `session_id` | string (UUID) | yes | Meeting session |
| `timestamp` | string (RFC3339) | yes | Event time (UTC preferred) |
| `type` | string | yes | Event type discriminator |
| `source` | string | yes | Producer id (`core`, `asr:funasr`, …) |
| `confidence` | number 0–1 | no | When applicable |
| `speaker_id` | string | no | Stable diarization id |
| `participant_id` | string | no | Mapped person id |
| `language` | string | no | BCP-47 (`zh-CN`, `en`) |
| `text` | string | no | Primary text payload |
| `provenance` | object | no | Origin / adapter / model metadata |
| `correlation_id` | string | no | Links research/alerts to triggers |

## Event types

| Type | Purpose |
|------|---------|
| `meeting.started` | Session began |
| `meeting.ended` | Session ended |
| `audio.activity` | VAD / energy activity |
| `speaker.detected` | New or updated speaker cluster |
| `speaker.turn` | Speaker turn boundary |
| `speaker.identity` | Optional enrolled identity match (consent-gated) |
| `transcript.partial` | Interim ASR |
| `transcript.final` | Final ASR segment |
| `translation.partial` | Interim translation |
| `translation.final` | Final translation (retains original linkage) |
| `claim.created` / `claim.updated` | Structured claim |
| `commitment.recorded` | Commitment |
| `decision.recorded` | Decision |
| `question.recorded` | Unanswered / posed question |
| `research.started` / `research.completed` | Background research lifecycle |
| `finding.published` | Agent finding with evidence |
| `alert.pushed` | Private/user alert |
| `private_speech.queued` / `private_speech.spoken` | Private TTS lifecycle |
| `meeting.pre_context_set` | Pre-meeting agenda/goals/facts |
| `meeting.consent_recorded` | Consent flag recorded |
| `meeting.exported` | Post-meeting package produced |
| `primitive.detected` | Number / deadline / price / risk primitive |
| `privacy.biometrics_cleared` | Biometric consent cleared |

## Claim states

Never overwrite original statements; retain provenance.

- `UNVERIFIED`
- `SUPPORTED_PROJECT_SOURCE`
- `SUPPORTED_EXTERNAL_SOURCE`
- `CONTRADICTED_PROJECT_SOURCE`
- `CONTRADICTED_EXTERNAL_SOURCE`
- `CONFLICTING_EVIDENCE`
- `INSUFFICIENT_INFORMATION`

## MCP resources

| URI | Description |
|-----|-------------|
| `meeting://sessions/{id}/state` | Live session summary |
| `meeting://sessions/{id}/transcript` | Transcript (+ translations) |
| `meeting://sessions/{id}/participants` | Speakers / people mapping |
| `meeting://sessions/{id}/claims` | Claims |
| `meeting://sessions/{id}/commitments` | Commitments |
| `meeting://sessions/{id}/decisions` | Decisions |
| `meeting://sessions/{id}/questions` | Questions |
| `meeting://sessions/{id}/findings` | Findings |
| `meeting://sessions/{id}/alerts` | Alerts |
| `meeting://sessions/{id}/research` | Research jobs |
| `meeting://sessions/{id}/primitives` | Intelligence primitives |
| `meeting://sessions/{id}/pre_meeting` | Pre-meeting context |
| `meeting://sessions/{id}/export` | Post-meeting package |

## MCP tools

`meeting.start_session`, `meeting.stop_session`, `meeting.get_live_state`, `meeting.get_recent_context`, `meeting.search_transcript`, `meeting.list_speakers`, `meeting.assign_speaker`, `meeting.update_participant`, `meeting.create_claim`, `meeting.update_claim`, `meeting.compare_claim`, `meeting.record_commitment`, `meeting.record_decision`, `meeting.record_question`, `meeting.publish_finding`, `meeting.push_private_alert`, `meeting.speak_private`, `meeting.set_mode`, `meeting.set_language`, `meeting.set_alert_threshold`, `meeting.set_pre_meeting_context`, `meeting.start_research`, `meeting.complete_research`, `meeting.export_package`, `meeting.list_sessions`, `meeting.search_sessions`, `meeting.delete_session`, `meeting.record_consent`.

## Transport rules

- Raw audio and low-latency deltas: WebRTC/WebSocket only.
- Structured inspection/control: MCP only.
- Agents must not block the realtime plane.
