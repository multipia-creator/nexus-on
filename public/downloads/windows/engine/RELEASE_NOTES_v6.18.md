# RELEASE NOTES v6.18 (PR-04: Character Rehearsal Hard Gate)

Date: 2026-01-31

This release turns the Character Layer into a production-grade, auditable gate in ops rehearsal.

Changes
- tools/rehearsal_autoscore.py now runs character rehearsal autoscore by default (hard gate)
- Scorecard includes section D: Character Rehearsal (GoldenSet autoscore)
- Final PASS requires Character Rehearsal OK (all cases >= min_score; default 90)
- Evidence is written to logs/character_rehearsal_evidence.jsonl

CLI
- --run-character / --no-run-character
- --character-golden (default tools/golden_conversation_set.jsonl)
- --character-out (default logs/character_rehearsal_evidence.jsonl)
- --character-min-score (default 90)

