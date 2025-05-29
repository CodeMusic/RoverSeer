#!/bin/bash

VOICE_ID="$1"

if [ -z "$VOICE_ID" ]; then
  echo "Usage: $0 en/en_US/amy/medium"
  exit 1
fi

echo "$VOICE_ID" > /home/codemusic/piper/.last_piper_voice

echo "🧹 Cleaning up old container..."
docker rm -f wyoming-piper 2>/dev/null

echo "🔁 Restarting Wyoming Piper with voice: $VOICE_ID"
cd /home/codemusic/piper-docker
PIPER_VOICE="$VOICE_ID" docker-compose up -d --build
