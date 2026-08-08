## Summary

<!-- What changed and why -->

## STATUS impact

- [ ] Docs / DX only
- [ ] Still uses **sim** adapters (no claim of real ASR/MT)
- [ ] Introduces or wires a **real** adapter (call out which)

## Test plan

- [ ] `./scripts/mac-smoke.sh` (or `uv run pytest -q` + simulate)
- [ ] Updated / added tests if core behavior changed
- [ ] UI still shows Simulated ASR unless real ASR is default

## Language / i18n

- [ ] Defaults remain `zh-CN` + `en` (or explicitly justified)
- [ ] User-facing status changes mirrored in `README.zh-CN.md` when needed
