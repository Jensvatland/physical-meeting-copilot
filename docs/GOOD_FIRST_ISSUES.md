# Good first issues

Real starter tasks from the codebase — not busywork.

## Publish them on GitHub

From a machine with write access to the repo:

```bash
gh auth login   # needs Issues write
bash scripts/bootstrap-community.sh
```

That creates labels + ~10 starter issues (`good first issue` / `help wanted` / `experiment`). Safe to re-run (skips existing titles).

Then enable **Discussions** in GitHub settings (General, Ideas, Q&A, Show and Tell, Experiments, Integrations).

## Starter list (same as the script)

| # | Title | Labels |
|---|-------|--------|
| 1 | README screenshots / short GIF | documentation |
| 2 | FunASR stub enable/disable tests | STT |
| 3 | Expand eval harness text scenarios | AI |
| 4 | Browser UI accessibility pass | documentation |
| 5 | Consent / recording notice clarity | privacy |
| 6 | Qwen-compatible translation adapter skeleton | translation, models |
| 7 | OpenClaw vs Hermes parity checklist | integration, MCP |
| 8 | Mic-less synthetic WAV/PCM replay | audio |
| 9 | Align China profile docs with reality | documentation |
| 10 | Experiment: alternative local STT adapter | experiment, STT, models |

## Rules of thumb

- Keep sim vs real honesty in UI/docs
- No real meeting audio, transcripts, or personal data in the repo
- Prefer adapters over core vendor lock-in
- AI-assisted PRs welcome — humans review/test before submit

See [CONTRIBUTING.md](../CONTRIBUTING.md) and [COMMUNITY.md](COMMUNITY.md).
