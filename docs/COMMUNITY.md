# Community

This project is an open experiment. Anyone is welcome to test it, improve it, challenge the architecture, build integrations, submit ideas, open issues, and contribute code.

You do not need permission to experiment or fork.

## Kickstart checklist (maintainers)

```bash
# Creates labels + starter "good first issue" / experiment issues
bash scripts/bootstrap-community.sh
```

Then in GitHub **Settings**:

1. Enable **Discussions** (categories below)
2. Confirm **Issues** stay enabled
3. Enable **secret scanning** + push protection
4. Set default branch to `main` when the foundation lives there
5. Optionally pin “Help wanted” / link Issues in the repo About blurb

## Issues vs Discussions

| Use | For |
|-----|-----|
| **Issues** | Actionable work: bugs, concrete features, integration requests, experiments aimed at a merge path |
| **Discussions** | Broader ideas, Q&A, show-and-tell, open-ended research chat |

Suggested Discussion categories:

- **General** — anything on-topic
- **Ideas** — product/architecture brainstorming
- **Q&A** — “how do I…?”
- **Show and Tell** — demos, forks, write-ups
- **Experiments** — STT/diarization/models/hardware/latency notes
- **Integrations** — Hermes, OpenClaw, MCP hosts, providers, CRM/knowledge bridges

Starter issue ideas: [GOOD_FIRST_ISSUES.md](GOOD_FIRST_ISSUES.md).

## Maintainer model (intentionally simple)

- Maintainers review PRs.
- Technical disagreements can be discussed publicly.
- Major architectural changes should be discussed in an issue before large implementation.
- Governance can evolve if the community grows.

No CLA, no committees, no mandatory issue assignment.

## Labels

See [GITHUB_LABELS.md](GITHUB_LABELS.md).

## AI coding agents

Contributions created with Cursor, Codex, Claude Code, Copilot, and similar tools are welcome. Humans remain responsible for the submitted code. See [AGENTS.md](../AGENTS.md) and [CONTRIBUTING.md](../CONTRIBUTING.md).
