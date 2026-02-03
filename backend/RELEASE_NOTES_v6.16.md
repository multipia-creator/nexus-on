# RELEASE NOTES v6.16 (Character PR-01/02)

Date: 2026-01-31

This release adds the Character Chatbot layer as a first-class subsystem, focusing on:
- Contract enforcement for structured chat responses (chat_response schema)
- Live2D PresencePacket schema and deterministic presence generation
- Character state engine (decide_state / should_auto_trigger_sexy) with confirm-first tool policy
- New Supervisor endpoint: POST /character/chat

Key files:
- shared/schemas/chat_response.schema.json
- shared/schemas/live2d_presence_packet.schema.json
- shared/character/state_engine.py
- shared/character/presence.py
- nexus_supervisor/app.py (new route /character/chat)
- conftest.py (ensures 'shared' is importable in tests)

All tests: 26 passed, 1 skipped (pytest -q).
