# RELEASE NOTES v6.17 (PR-03: Presence Policy + Character Rehearsal Gate)

Date: 2026-01-31

Changes:
- PresenceController is now policy-table driven (shared/character/presence_policy.py)
- presence_to_live2d uses policy ranges and deterministic sampling (v1.1)
- Added character rehearsal autoscore tool (tools/character_rehearsal_autoscore.py)
- Added bundled golden conversation set (tools/golden_conversation_set.jsonl)
- Added unit test ensuring autoscore tool runs

Ops integration:
- tools/rehearsal_autoscore.py includes summarize_character_rehearsal() helper (wiring to scorecard template is safe follow-up).

