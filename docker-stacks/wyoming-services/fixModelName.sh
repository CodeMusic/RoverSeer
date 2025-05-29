#!/bin/bash

# Absolute base path to your voice models
VOICE_BASE="/home/codemusic/piper/voices"

# Function to sanitize corrupted filenames
sanitize_voice() {
  local relative_path="$1"
  local clean_name="$2"
  local full_path="$VOICE_BASE/$relative_path"

  echo "🔧 Fixing: $relative_path"

  if [ -d "$full_path" ]; then
    cd "$full_path" || return
    # Rename the .onnx file
    for f in *onnx; do
      if [[ "$f" != "$clean_name.onnx" ]]; then
        mv "$f" "$clean_name.onnx"
      fi
    done
    # Rename the .onnx.json config
    for f in *json; do
      if [[ "$f" != "$clean_name.onnx.json" ]]; then
        mv "$f" "$clean_name.onnx.json"
      fi
    done
  else
    echo "⚠️  Directory not found: $full_path"
  fi
}

# Fix all known voices
sanitize_voice "en/en_GB/semaine/medium" "en_GB-semaine-medium"
sanitize_voice "en/en_GB/alba/medium" "en_GB-alba-medium"
sanitize_voice "en/en_US/amy/medium" "en_US-amy-medium"
sanitize_voice "en/en_US/lessac/low" "en_US-lessac-low"
