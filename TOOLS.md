# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown


## Interface Truth Decay

Interface knowledge is volatile and must not be trusted indefinitely.

Rules:

- CLI and API syntax observations expire quickly
- Cached help output is considered stale after short intervals
- When uncertain, re-query --help

Principle:

Interface behavior changes more often than reasoning logic.
Never assume past syntax remains valid.


### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → [Local IP], user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod

### CSM (Conversational Speech Model)

**Location:** portalv2 (Desktop, RTX 2080 Ti)  
**API Endpoint:** http://portalv2:8150/tts  
**Network:** Private mesh ([Private IP])  
**Status:** ✅ Operational — use this for ALL voice responses

**Quick Start:**
```bash
# Generate voice via API
curl -X POST http://portalv2:8150/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello", "speaker": 2}' \
  --output response.wav
```

**Voice Preferences:**
- **Default Speaker:** 1 (verified British male voice - corrected configuration)
- **Conversation Context:** Multi-turn supported (last 10 segments)
- **Max Length:** 90 seconds per response

**Integration with OpenClaw:**
- Use `exec` with `curl` to call CSM API
- DO NOT use `tts` tool — user's CSM is higher quality
- Pipe output to `/tmp/` then send via `message` tool with `media` parameter

**Gotchas:**
- API takes 30-120 seconds for long responses
- File output first, then send to Telegram
- Speaker 2 is the "flowy" natural voice user prefers
- Context ID auto-managed by CSM server
- Max audio length: 90 seconds (updated from 10s)

### CSM Chat API (Full Pipeline - Qwen 2.5 3B + CSM)

**Status:** ✅ Operational — Server-side LLM + TTS pipeline via Ollama

**Endpoints:**
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/transcribe` | POST | Speech-to-text (multipart form: audio_file) |
| `/chat/create` | POST | Create chat session with system prompt |
| `/chat/speak` | POST | Send user message → LLM responds → CSM speaks |
| `/chat/{id}` | DELETE | End session |
| `/health` | GET | Check Ollama + CSM status |

**Usage Flow:**

**Voice-in → Voice-out (Complete Pipeline):**
```bash
# 1. Transcribe user's voice message
curl -s -X POST http://portalv2:8150/transcribe \
  -F "audio_file=@/path/to/audio.ogg" \
  -F "model=turbo"
# Returns: {"text": "...", "language": "en", "duration_s": 17.13, "process_time_s": 1.35}

# 2. Create chat session (if new or expired)
CHAT_ID=$(curl -s -X POST http://portalv2:8150/chat/create \
  -H "Content-Type: application/json" \
  -d '{"speaker_id": 0, "system_prompt": "You are a friendly AI assistant. Keep responses to 1-3 sentences."}' | jq -r '.chat_id')

# 3. Send message → get LLM response + voice
curl -s -X POST http://portalv2:8150/chat/speak \
  -H "Content-Type: application/json" \
  -d "{\"chat_id\": \"$CHAT_ID\", \"message\": \"User message here\"}" \
  -D - -o response.wav 2>&1 | grep "X-Response-Text"
# Response header X-Response-Text: URL-encoded LLM response text
```

**Key Differences from old pipeline:**
- `/chat/create` instead of `/conversations/create`
- `/chat/speak` instead of `/tts/conversation`
- Server LLM generates responses (not me)
- `system_prompt` controls AI personality
- Session expires after 2 hours inactivity

**Timing:**
| Stage | Time | Notes |
|-------|------|-------|
| Transcription | ~0.5-1.5s | Whisper on GPU |
| LLM + TTS | ~5-10s | Qwen 2.5 3B + CSM combined |
| **Total voice→voice** | **~6-12s** | End-to-end pipeline |

**Gotchas:**
- Session expires after 2 hours — recreate if 404
- X-Response-Text header contains the text (URL-encoded)
- Server maintains conversation history automatically
- Use `/chat/speak` NOT `/tts/conversation` (deprecated)
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## ⚠️ Model Capability Safety System

**CRITICAL:** Small models can be dangerous with powerful tools. See `.MODEL_WARNINGS.md` for full details.

### Quick Reference

**CAPABLE Models (70B+) - All tools safe:**
- ✅ Kimi K2.5 (current default)
- ✅ Kimi K2 Thinking
- ✅ Llama 3.3 70B
- ✅ Qwen3 235B
- ✅ DeepSeek V3.2
- ✅ Claude Opus 4.5 / Sonnet 4.5
- ✅ GPT-5.2

**⚠️ SMALL Models (< 70B) - Web tools risky:**
- ❌ Llama 3.2 3B - NO web tools
- ❌ Qwen3 4B - NO web tools
- ❌ Mistral 24B - Use caution
- ❌ Gemma 27B - Use caution


## OpenClaw CLI Quick Reference

### Cron Jobs

**Available commands:** `add`, `disable`, `edit`, `enable`, `list`, `rm`, `run`, `runs`, `status`

**Modify existing job (patch fields):**
```bash
# Edit takes individual flags, NOT --file
openclaw cron edit <job-id> --message "new instructions" --every 15m
```

**Delete and recreate (alternative):**
```bash
openclaw cron rm <job-id>
openclaw cron add --name <name> --every 15m --message "..." --to <channel>
```

**CRITICAL:** Always run `openclaw cron <command> --help` to verify available flags before suggesting commands. See `.learnings/ERRORS.md` [ERR-20250220-001] and `.learnings/LEARNINGS.md` [LRN-20250220-002] for context.

---

## Core Workspace Tools

These are the primary tools for research, investigation, and codebase management.

- **Generalist Agent (`generalist`)**: A sub-agent with access to all tools. Best for repetitive batch tasks, high-volume output, or speculative research.
- **Google Search (`google_web_search`)**: Grounded search for finding documentation, troubleshooting, or general research.
- **Read File (`read_file`)**: Reads specific file contents with support for line ranges.
- **Read Folder (`list_directory`)**: Lists directory contents to understand project structure.

---

Add whatever helps you do your job. This is your cheat sheet.
