#!/usr/bin/env bash
# Create labels + starter GitHub issues that invite contributions.
#
# Requires a token with Issues + Metadata write on this repo:
#   gh auth login
#   bash scripts/bootstrap-community.sh
#
# Safe to re-run: skips labels/issues that already exist (by exact title).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

REPO="${GITHUB_REPOSITORY:-Jensvatland/physical-meeting-copilot}"

if ! command -v gh >/dev/null 2>&1; then
  echo "gh CLI required: https://cli.github.com/"
  exit 1
fi

echo "==> Repo: $REPO"
gh repo view "$REPO" --json nameWithOwner,hasIssuesEnabled >/dev/null

ensure_label() {
  local name="$1" color="$2" desc="$3"
  if gh label list --repo "$REPO" --limit 200 --json name --jq '.[].name' | grep -Fxq "$name"; then
    echo "  label exists: $name"
  else
    gh label create "$name" --repo "$REPO" --color "$color" --description "$desc"
    echo "  label created: $name"
  fi
}

echo "==> Labels"
ensure_label "good first issue" "7057ff" "Well-scoped starter tasks"
ensure_label "help wanted" "008672" "Extra attention appreciated"
ensure_label "bug" "d73a4a" "Something broken"
ensure_label "feature" "a2eeef" "New capability"
ensure_label "experiment" "f9d0c4" "Research / exploratory work"
ensure_label "documentation" "0075ca" "Docs / DX"
ensure_label "audio" "c5def5" "Capture, VAD, hardware"
ensure_label "STT" "bfdadc" "Speech-to-text adapters"
ensure_label "diarization" "d4c5f9" "Speaker labeling"
ensure_label "translation" "fef2c0" "MT / glossary"
ensure_label "AI" "e99695" "Agent / intelligence behavior"
ensure_label "models" "fad8c7" "Model packaging / selection"
ensure_label "MCP" "bfd4f2" "MCP server / resources / tools"
ensure_label "integration" "d1f0d1" "Host or system bridges"
ensure_label "iOS" "f0e6ff" "iPhone client"
ensure_label "iPadOS" "e6f0ff" "iPad client"
ensure_label "macOS" "eeeeee" "Mac tooling / capture"
ensure_label "privacy" "5319e7" "Consent, retention, biometrics"
ensure_label "security" "b60205" "Auth, threat model, secrets"
ensure_label "performance" "fbca04" "Latency / resource use"

issue_exists() {
  local title="$1"
  gh issue list --repo "$REPO" --state all --limit 200 --json title --jq '.[].title' | grep -Fxq "$title"
}

create_issue() {
  local title="$1"
  shift
  local labels_csv="$1"
  shift
  local body="$1"

  if issue_exists "$title"; then
    echo "  issue exists: $title"
    return
  fi

  local args=(issue create --repo "$REPO" --title "$title" --body "$body")
  IFS=',' read -ra labels <<<"$labels_csv"
  for label in "${labels[@]}"; do
    args+=(--label "$label")
  done
  url="$(gh "${args[@]}")"
  echo "  opened: $url"
}

echo "==> Starter issues"

create_issue \
  "Add README screenshots or a short GIF of the offline demo" \
  "good first issue,help wanted,documentation" \
  "$(cat <<'EOF'
## Why

Visitors should see what the tool looks like in ~10 seconds without running anything.

## Task

Add synthetic demo media to the README (or `docs/images/`):

- screenshot of the browser UI after `uv run meeting-gateway`, **or**
- short GIF of `bash scripts/try.sh` / `simulate_meeting` output

## Rules

- No real meeting recordings, transcripts, or personal data
- Keep the Simulated ASR honesty visible if showing the UI
- Prefer small assets (compress GIF/PNG)

## Done when

README shows at least one visual under **Try it** / **What works today**.

## Pointers

- `README.md`
- `clients/web/public/index.html`
- `bash scripts/try.sh`
EOF
)"

create_issue \
  "FunASR stub: tests for enable/disable and graceful failure" \
  "good first issue,help wanted,STT" \
  "$(cat <<'EOF'
## Why

China-profile ASR is still a stub. Tests should lock the contract so wiring a real runtime later is safer.

## Task

Expand `packages/meeting_core/tests/test_adapters.py` (or a new test module) for `FunASRSpeechRecognitionAdapter`:

1. Default / `FUNASR_ENABLED` unset → `health().degraded` and `transcribe_stream` raises a clear error
2. `FUNASR_ENABLED=1` without a real runtime → `NotImplementedError` (or documented RuntimeError) — still no crash in Meeting Core
3. `capabilities()` still advertises `zh-CN` + `en`

## Done when

`uv run pytest -q` covers the cases above. Do **not** vendor FunASR in this issue.

## Pointers

- `packages/meeting_core/src/meeting_core/adapters/asr/funasr_stub.py`
- `packages/meeting_core/src/meeting_core/adapters/base.py`
- `docs/STATUS.md`
EOF
)"

create_issue \
  "Expand eval harness with more text scenarios" \
  "good first issue,help wanted,AI" \
  "$(cat <<'EOF'
## Why

We need regression coverage without a live room. Text fixtures are enough for many intelligence paths.

## Task

Add 1–3 scenarios to `meeting_core.eval.harness`, for example:

- code-switching Mandarin/English
- numbers / dates / prices
- negation (“not 1M” vs “1M”)

## Done when

`uv run python -m meeting_core.eval.harness` passes including the new scenarios. No proprietary audio.

## Pointers

- `packages/meeting_core/src/meeting_core/eval/harness.py`
- `docs/STATUS.md`
EOF
)"

create_issue \
  "Browser UI accessibility pass (keep Simulated ASR banner)" \
  "good first issue,help wanted,documentation" \
  "$(cat <<'EOF'
## Why

The prototype UI should be usable with keyboard and clearer labels before more people try the mic path.

## Task

Improve `clients/web/public/index.html`:

- focus order / visible focus
- button and control labels
- contrast where cheap to fix
- do **not** remove the Simulated ASR honesty banner

## Done when

You can start/stop a meeting and navigate main controls with keyboard only. Note remaining gaps in the PR.

## Pointers

- `clients/web/public/index.html`
- `clients/web/README.md`
- `docs/PRIVACY.md` (consent copy nearby is fair game)
EOF
)"

create_issue \
  "Clarify session-start consent / recording notice" \
  "good first issue,help wanted,privacy" \
  "$(cat <<'EOF'
## Why

Operators are responsible for legal consent. The UI should make that obvious without sounding corporate.

## Task

Improve the session-start consent / recording notice in the browser UI and link to `docs/PRIVACY.md`.

Keep language short and practical — not country-by-country legal advice.

## Done when

A first-time operator can see that recording/transcription requires their consent responsibility before starting.

## Pointers

- `clients/web/public/index.html`
- `docs/PRIVACY.md`
- `packages/gateway/src/meeting_gateway/app.py` (`record_consent`)
EOF
)"

create_issue \
  "Qwen-compatible translation adapter skeleton (optional, env-gated)" \
  "good first issue,help wanted,translation,models" \
  "$(cat <<'EOF'
## Why

Translation is glossary/sim today. A thin optional HTTP adapter unblocks experiments without making any cloud vendor mandatory.

## Task

Add an optional `TranslationAdapter` implementation that talks to an OpenAI-compatible / Qwen-compatible endpoint:

- env-gated (`QWEN_BASE_URL` / `QWEN_API_KEY` or similar — document in `.env.example`)
- degraded health when unset
- mocked unit tests (no live network in CI)
- **do not** make it the default; keep sim as default

## Done when

Adapter exists, tests pass offline, STATUS/README still say translation is experimental unless explicitly enabled.

## Pointers

- `packages/meeting_core/src/meeting_core/adapters/base.py`
- `packages/meeting_core/src/meeting_core/adapters/translation/sim.py`
- `docs/LICENSES.md`
- ADR: OpenAI never mandatory
EOF
)"

create_issue \
  "OpenClaw vs Hermes: parity checklist + small gaps" \
  "good first issue,help wanted,integration,MCP" \
  "$(cat <<'EOF'
## Why

OpenClaw should feel first-class next to Hermes. Right now it is a thinner mirror.

## Task

1. Compare `integrations/hermes` and `integrations/openclaw` (README, SKILL, event bridge, mcp.json)
2. Write a short parity checklist in `integrations/openclaw/README.md`
3. Fix any small, safe gaps (docs or thin bridge behavior)
4. Add/adjust a focused test if behavior changes

## Done when

A contributor can see what matches, what differs, and what is intentionally host-specific.

## Pointers

- `integrations/hermes/`
- `integrations/openclaw/`
- `docs/PROTOCOL.md`
EOF
)"

create_issue \
  "Mic-less UI demo: synthetic WAV/PCM replay into the gateway" \
  "good first issue,help wanted,audio" \
  "$(cat <<'EOF'
## Why

People should exercise the browser/gateway path without speaking into a mic.

## Task

Propose and/or implement a deterministic path:

- checked-in **synthetic** PCM/WAV fixture (no real meetings)
- a small script or gateway hook to replay frames into the ingest pipeline
- document it in `docs/MAC.md`

## Done when

`docs/MAC.md` describes a mic-less UI demo, and ideally `bash`-level steps work on Mac/Linux.

## Pointers

- `packages/gateway/src/meeting_gateway/app.py`
- `packages/meeting_core/src/meeting_core/realtime/pipeline.py`
- `docs/MAC.md`
- `docs/GOOD_FIRST_ISSUES.md`
EOF
)"

create_issue \
  "Align China profile docs with actual compose + FunASR stub" \
  "good first issue,help wanted,documentation" \
  "$(cat <<'EOF'
## Why

`docs/CHINA.md` should not over-claim. Contributors in China need an honest map of what runs today.

## Task

Read and align:

- `docs/CHINA.md`
- `docker-compose.china.yml`
- `packages/meeting_core/src/meeting_core/adapters/asr/funasr_stub.py`
- `docs/STATUS.md`

Fix wording so stubs vs working paths are obvious.

## Done when

A reader can tell what to run today vs what is still planned for the China profile.

## Pointers

See files above.
EOF
)"

create_issue \
  "Experiment: alternative local STT engine behind SpeechRecognitionAdapter" \
  "experiment,help wanted,STT,models" \
  "$(cat <<'EOF'
## Why

We want provider-independent speech. Sim ASR is the default; experiments are welcome.

## Task

Prototype an alternative local STT engine as an adapter (Whisper.cpp, Faster-Whisper, Vosk, SenseVoice, … — your choice):

- implement `SpeechRecognitionAdapter`
- env-gated, optional dependency
- degraded health when unset
- keep Meeting Core free of vendor lock-in
- document license notes in `docs/LICENSES.md`

Forks/experiments need no approval. Open a PR if you want it upstream.

## Done when

README/STATUS still honest; adapter can be enabled for demos; tests mock the heavy dependency.
EOF
)"

echo
echo "Done."
echo "Next (manual in GitHub settings):"
echo "  • Enable Discussions (General, Ideas, Q&A, Show and Tell, Experiments, Integrations)"
echo "  • Set default branch to main when ready"
echo "  • Enable secret scanning + push protection"
echo "  • Pin 'good first issue' / 'help wanted' in the About sidebar if you like"
echo
echo "Browse: https://github.com/$REPO/issues"
