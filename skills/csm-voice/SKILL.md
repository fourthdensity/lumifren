---
name: csm-voice
description: Generate high-quality voice audio using CSM (Conversational Speech Model) via local API. Use when the user requests voice responses, especially in Telegram or other messaging contexts. Triggers on voice message input, explicit voice requests, or when matching input modality (responding to voice with voice). Supports Speaker 2 default voice and multi-turn conversation context.
---

# CSM Voice

Generate high-quality neural text-to-speech using Sesame AI's CSM (Conversational Speech Model) running locally on an RTX 2080 Ti.

## Quick Start

### Generate Voice (One-off)
```bash
./scripts/csm-voice.sh "Hello there" --output=/tmp/out.wav
```

### With Custom Speaker
```bash
./scripts/csm-voice.sh "Hello" --speaker=5 --output=/tmp/out.wav
```

### JSON Output (for automation)
```bash
./scripts/csm-voice.sh "Hello" --quiet
# Output: {"success":true,"outputPath":"/tmp/csm_output.wav","size":368720,"speaker":2}
```

## API Details

- **Server**: `portalv2` (RTX 2080 Ti, local machine)
- **Endpoint**: `http://portalv2:8150/tts`
- **Network**: Tailscale private mesh (100.95.19.54)
- **Max Audio**: 90 seconds per request
- **Sample Rate**: 24kHz, mono, IEEE Float

## Voice Options

| Speaker | Description |
|---------|-------------|
| 0 | Neutral base voice |
| 1 | Alternative voice |
| 2 | **Default** — "flowy" natural voice (user preference) |
| 3-9 | Additional voice variations |

## Conversation Context

CSM supports multi-turn context for natural dialogue flow:
- Context ID auto-managed by server
- Last 10 conversation segments remembered
- Context expires after 1 hour
- Natural stop detection (EOS)

## Integration with OpenClaw

### Basic Voice Response
```bash
# Generate voice
curl -s -X POST http://portalv2:8150/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Your response here", "speaker": 2}' \
  --output /tmp/response.wav

# Send to Telegram
message send --media=/tmp/response.wav
```

### Wrapper Script Usage
```bash
# Simple usage
./scripts/csm-voice.sh "Hello from CSM"

# Custom output path
./scripts/csm-voice.sh "Hello" --output=/tmp/custom.wav

# Different speaker
./scripts/csm-voice.sh "Hello" --speaker=5

# JSON output for parsing
./scripts/csm-voice.sh "Hello" --quiet
```

## Response Patterns

### When User Sends Voice Message
Always respond with CSM voice (match modality):
1. Transcribe with Whisper (local)
2. Generate response
3. Convert to voice via CSM API
4. Send audio file

### Text-to-Voice Requests
User: "Say that in voice"
→ Use CSM, not built-in TTS

### Telegram Voice Notes
Use OGG/OPUS format for best compatibility:
```bash
# Convert WAV to OGG (Opus)
ffmpeg -i input.wav -c:a libopus -b:a 24k output.ogg
```

## Performance Notes

- **Short text** (5-10 words): ~10-30 seconds generation
- **Medium text** (20-50 words): ~1-2 minutes generation
- **Long text** (50-100 words): ~2-4 minutes generation
- Max 90 seconds audio output

If generation hangs, text may be too long — split into chunks.

## Environment Variables

```bash
export CSM_HOST=portalv2        # CSM server hostname
export CSM_PORT=8150            # CSM server port
```

## Troubleshooting

**Timeout/Hang:**
- Text too long — reduce to <50 words
- Server busy — retry after a moment

**Connection refused:**
- Check CSM server is running on portalv2
- Verify Tailscale connectivity

**Low quality:**
- Ensure Speaker 2 is being used (user preference)
- Check server logs for errors

## Related

- See `TOOLS.md` for CSM server setup details
- Whisper skill for transcription
- SAM TTS skill for retro robotic voice
