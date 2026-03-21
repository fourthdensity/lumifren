# SESSION-STATE.md — Active Working Memory

> This is my "RAM" — the only place specific details are safe. Updated continuously via WAL Protocol.

**Last Updated:** 2026-02-11T12:30:00Z  
**Current Context:** Proactive agent mode activated — fire-and-forget capability enabled

---

## Stable State (Long-Lived)

Facts unlikely to change frequently.

- User name
- Timezone
- Communication preferences
- Identity bindings


## Volatile Runtime State (Session-Scoped)

Temporary operational conditions.

- Active tasks
- Modes (proactive, debug, etc.)
- Temporary hypotheses


## Interface State (Expiring / High-Risk)

Tool behavior and syntax assumptions.

- Help outputs
- CLI quirks
- API behaviors

All interface state must be considered stale unless recently verified.

TTL Rules:

- Interface observations decay rapidly
- Old syntax knowledge must not be reused blindly
- Prefer fresh --help queries over memory

Heuristic:

If interface data origin is unknown or old, treat as invalid.

---

## Active Task

None — awaiting direction

## Previous Task (Completed)

- SpaceMolt Companion removed per user request
- Backup and self-improvement review completed

---

## Working Decisions

| Decision | Value | Source |
|----------|-------|--------|
| User name | Billy | USER.md |
| User timezone | Eastern Standard Time (EST) | ONBOARDING.md |
| User communication style | Minimal/sharp but grounded/casual — dual nature | ONBOARDING.md |
| Agent name | LUX | IDENTITY.md |
| Agent vibe | Minimal, sharp | IDENTITY.md |
| Self-improvement hook | Enabled | User request 2026-02-10 |
| Proactive agent skill | Installed | User added 2026-02-10 |
| **Proactive mode** | **ACTIVE** | Fire-and-forget capability enabled |

---

## Preferences Captured

| Preference | Value | Source |
|------------|-------|--------|
| User timezone | EST (UTC-5) | ONBOARDING.md |
| User archetype | Futurist, systems builder, "creating the new world" | ONBOARDING.md |
| Communication | Minimal/sharp + casual/conversational (dual) | ONBOARDING.md |
| Agent emoji | 🔆 | IDENTITY.md |
| Learning log location | `.learnings/` | Self-improvement skill |

---

## Key Proper Nouns

- **Billy** — the human I serve
- **LUX** — my name/agent identity
- **OpenClaw** — the platform I'm running on
- **Hal Labs / @halthelobster** — creator of proactive-agent skill

---

## Pending / In Progress

- [x] Create ONBOARDING.md
- [x] Create SESSION-STATE.md
- [x] Timezone captured (EST)
- [x] Communication style captured
- [x] Current focus captured (building LUX/systems)
- [ ] Complete remaining onboarding questions (drip mode)

## Known Issues

- [ ] **Image analysis broken** — 401 auth error with anthropic/claude-opus-4-6 (logged: ERR-20260210-001)
  - Impact: Cannot describe images sent by user
  - Possible fix: Check OpenClaw config for API key or switch models

---

## Working Buffer Reference

If context is lost, check `memory/working-buffer.md` for danger-zone exchanges.

---

*This file is updated via WAL Protocol — corrections and decisions are written here BEFORE responding.*
