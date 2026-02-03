# RELEASE NOTES v6.19 (PR-05: GoldenSet v2 + Coverage + Baseline Regression)

Date: 2026-01-31

Changes
- Expanded Golden Conversation Set to v2 (60 cases) with category/tags
  - tools/golden_conversation_set_v2.jsonl
  - tools/golden_conversation_set.jsonl now points to v2
- tools/character_rehearsal_autoscore.py upgraded:
  - Generates logs/character_rehearsal_summary.json
  - Enforces required category-prefix coverage (hard gate)
  - Optional baseline diff: tools/character_rehearsal_baseline.json
  - Manual snapshot: --write_baseline
- tools/rehearsal_autoscore.py shows coverage + baseline regression status in scorecard (Section D)

Ops practice
- First time: run rehearsal, then (optionally) snapshot baseline:
  python tools/character_rehearsal_autoscore.py --write_baseline
- Thereafter: PR/changes should keep baseline stable; regressions are surfaced.

