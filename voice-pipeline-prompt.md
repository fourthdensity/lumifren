# Voice Pipeline Implementation Prompt

## Overview
Build a dual-mode voice system for OpenClaw that can toggle between **CSM (high quality, slow)** and **MeloTTS (fast, streaming)** voice pipelines for Discord voice channel integration.

## Architecture

```
Discord Voice Channel ←→ Bridge Bot ←→ Mode Router ←→ Pipeline A OR Pipeline B
                                                    ↓              ↓
                                               CSM Server    MeloTTS Local
                                               (portalv2)    (local GPU)
```

## Core Requirements

### 1. Mode Toggle System (Skill Pattern)
Create `skills/voice-pipeline/SKILL.md` with toggle commands:
- `/voice csm` — Use CSM pipeline (quality mode)
- `/voice fast` — Use MeloTTS pipeline (speed mode)
- `/voice status` — Show current mode and latency stats

State storage: `memory/voice-pipeline.json`
```json
{
  "mode": "csm",
  "csm": {
    "endpoint": "http://portalv2:8150",
    "speaker_id": 1,
    "chat_session": null
  },
  "fast": {
    "stt_model": "faster-whisper-base",
    "llm_model": "qwen2.5-3b-instruct",
    "tts_model": "melo-tts-en"
  }
}
```

### 2. CSM Pipeline (Existing)
**Latency:** 6-12s  
**Quality:** Excellent natural voice

Endpoints:
- POST `/transcribe` — audio file → text
- POST `/chat/create` → chat_id
- POST `/chat/speak` — text + chat_id → audio

### 3. Fast Pipeline (New - MeloTTS)
**Target latency:** <1s  
**Quality:** Good, slightly synthetic

Components:
- **STT:** `faster-whisper` (real-time streaming)
- **LLM:** `llama.cpp` with Qwen 2.5 3B (streaming generation)
- **TTS:** `MeloTTS` (real-time synthesis)

## Technical Implementation

### Directory Structure
```
skills/voice-pipeline/
├── SKILL.md                    # Toggle commands + usage
├── scripts/
│   ├── bridge-server.js        # Main Discord voice bridge
│   ├── mode-router.js          # Route to CSM or Fast
│   ├── fast-pipeline.js        # MeloTTS + llama.cpp integration
│   └── latency-monitor.js      # Track and report latency
├── config/
│   └── default.json            # Default settings
└── README.md                   # Setup instructions
```

### Fast Pipeline Details

**STT (faster-whisper):**
```javascript
// Real-time streaming transcription
// Use VAD (voice activity detection) to segment speech
// Stream audio chunks, get partial transcripts
```

**LLM (llama.cpp via Ollama):**
```javascript
// Stream tokens as they're generated
// Use system prompt: "You are Lumifren, a helpful AI. Be concise."
// Max tokens: 100 (keep responses short for voice)
```

**TTS (MeloTTS):**
```javascript
// Sentence-level synthesis
// Start generating audio on first complete sentence
// Stitch audio chunks together
// Target: <300ms per sentence
```

### Bridge Server (Discord Voice)

**Dependencies:**
- `@discordjs/voice` — Discord voice connection
- `@discordjs/opus` — Audio codec
- `prism-media` — Audio conversion
- `node-fetch` — HTTP requests

**Key Functions:**
```javascript
// Join voice channel
async function joinVoiceChannel(channelId) { }

// Handle user speech
async function onUserSpeech(userId, audioStream) { }

// Route to appropriate pipeline
async function routePipeline(mode, text) { }

// Play audio response
async function playAudio(audioBuffer) { }
```

### Latency Monitoring

Track per-interaction:
- STT time (speech → text)
- LLM time (text → response text)
- TTS time (response text → audio)
- Total round-trip

Log to `memory/voice-latency.json`:
```json
{
  "timestamp": "2025-02-12T07:30:00Z",
  "mode": "fast",
  "stt_ms": 450,
  "llm_ms": 320,
  "tts_ms": 180,
  "total_ms": 950
}
```

## Mode Switching Behavior

**CSM Mode:**
- Wait for full user speech (VAD silence detection)
- Send to CSM `/transcribe`
- Send text to CSM `/chat/speak`
- Play full response audio
- Expected: 6-12s latency

**Fast Mode:**
- Stream audio chunks to faster-whisper
- Get partial transcripts, detect sentence boundaries
- Stream to llama.cpp, get streaming tokens
- Detect sentence completion, start MeloTTS immediately
- Play audio chunks as they're ready
- Expected: <1s to first audio, continuous playback

## Integration with OpenClaw

The skill should:
1. Export a `/voice` command namespace
2. Read/write `memory/voice-pipeline.json` for state
3. Start bridge server as background process when activated
4. Log errors to `memory/voice-errors.json`

## Setup Instructions (README.md)

1. **Install dependencies:**
```bash
# MeloTTS
pip install melo-tts

# faster-whisper
pip install faster-whisper

# llama.cpp (via Ollama)
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5:3b

# Node dependencies
cd skills/voice-pipeline
npm install @discordjs/voice @discordjs/opus prism-media
```

2. **Configure:**
```bash
# Copy and edit config
cp config/default.json config/local.json
# Set your Discord bot token, CSM endpoint, etc.
```

3. **Start bridge:**
```bash
node scripts/bridge-server.js
```

4. **Toggle modes:**
```
/voice csm    # High quality, slow
/voice fast   # Lower quality, instant
/voice status # Check mode + latency stats
```

## Testing Checklist

- [ ] Bridge joins Discord voice channel
- [ ] CSM mode works (6-12s latency, natural voice)
- [ ] Fast mode works (<1s latency, acceptable voice)
- [ ] Mode toggle switches without restart
- [ ] Latency stats logged correctly
- [ ] Handles multiple users (queuing)
- [ ] Error handling (CSM down, GPU OOM, etc.)

## Output

Provide:
1. Complete `SKILL.md` with commands and behavior
2. Working `scripts/bridge-server.js`
3. `scripts/fast-pipeline.js` (MeloTTS + llama.cpp)
4. `scripts/mode-router.js` (toggle logic)
5. `config/default.json` template
6. `README.md` with setup instructions

## Constraints

- Keep CSM pipeline untouched (it's working on portalv2)
- Fast pipeline runs on same machine (or use portalv2 if GPU available)
- Must handle mode switching at runtime
- Log everything for debugging
- Use existing OpenClaw patterns (memory files, skill structure)

## Notes

- CSM server endpoint: `http://portalv2:8150`
- Target latency for fast mode: <1s end-to-end
- Voice quality trade-off is acceptable for fast mode
- Consider implementing speculative TTS for common phrases as v2
