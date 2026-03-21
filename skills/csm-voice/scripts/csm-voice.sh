#!/bin/bash
#
# CSM Voice Generator Wrapper
# Generates high-quality voice audio using CSM (Conversational Speech Model) via API
#

# Default values
SPEAKER=2
OUTPUT="/tmp/csm_output.wav"
PORTALV2_HOST="${CSM_HOST:-portalv2}"
PORTALV2_PORT="${CSM_PORT:-8150}"
API_URL="http://${PORTALV2_HOST}:${PORTALV2_PORT}/tts"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --speaker)
      SPEAKER="$2"
      shift 2
      ;;
    --output)
      OUTPUT="$2"
      shift 2
      ;;
    --host)
      PORTALV2_HOST="$2"
      API_URL="http://${PORTALV2_HOST}:${PORTALV2_PORT}/tts"
      shift 2
      ;;
    --quiet)
      QUIET=1
      shift
      ;;
    --help)
      echo "Usage: csm-voice.sh [OPTIONS] <text>"
      echo ""
      echo "Options:"
      echo "  --speaker N     Speaker ID (0-9, default: 2)"
      echo "  --output PATH   Output file path (default: /tmp/csm_output.wav)"
      echo "  --host HOST     CSM server host (default: portalv2)"
      echo "  --quiet         Suppress output, return JSON only"
      echo "  --help          Show this help message"
      echo ""
      echo "Environment variables:"
      echo "  CSM_HOST        CSM server hostname"
      echo "  CSM_PORT        CSM server port"
      exit 0
      ;;
    *)
      TEXT="$1"
      shift
      ;;
  esac
done

if [ -z "$TEXT" ]; then
  echo "Error: No text provided" >&2
  exit 1
fi

# Make API request
if [ -z "$QUIET" ]; then
  echo "Generating voice with CSM..." >&2
fi

RESPONSE=$(curl -s -X POST "${API_URL}" \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"${TEXT}\", \"speaker\": ${SPEAKER}}" \
  --output "${OUTPUT}" \
  -w "%{http_code}")

if [ "$RESPONSE" != "200" ]; then
  echo "Error: API returned HTTP $RESPONSE" >&2
  exit 1
fi

# Get file size
FILESIZE=$(stat -f%z "$OUTPUT" 2>/dev/null || stat -c%s "$OUTPUT" 2>/dev/null || echo "0")

if [ -z "$QUIET" ]; then
  echo "Success: ${OUTPUT} (${FILESIZE} bytes)"
else
  echo "{\"success\":true,\"outputPath\":\"${OUTPUT}\",\"size\":${FILESIZE},\"speaker\":${SPEAKER}}"
fi
