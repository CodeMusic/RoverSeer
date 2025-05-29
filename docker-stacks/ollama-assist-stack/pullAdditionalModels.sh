#!/bin/bash

# Sequential model pull script for Ollama

pull() {
  echo "⬇️ Pulling $1"
  curl -s -X POST http://localhost:11434/api/pull -d "{\"name\":\"$1\"}" | jq .
  echo "✅ Done: $1"
  echo
}

models=(
  "registry.ollama.ai/library/medllama2:latest"
  "registry.ollama.ai/HammerAI/llama-3-lexi-uncensored:latest"
  "registry.ollama.ai/ALIENTELLIGENCE/lifecoach:latest"
  "registry.ollama.ai/ALIENTELLIGENCE/psychologistv2:latest"
  "registry.ollama.ai/koesn/llama3-openbiollm-8b:q4_K_M"
  "registry.ollama.ai/ALIENTELLIGENCE/gooddoctor:latest"
  "registry.ollama.ai/ALIENTELLIGENCE/whiterabbitv2:latest"
  "registry.ollama.ai/ALIENTELLIGENCE/doctorai:latest"
  "registry.ollama.ai/ALIENTELLIGENCE/holybible:latest"
  "registry.ollama.ai/ALIENTELLIGENCE/attorney2:latest"
  "registry.ollama.ai/sebdg/emotional_llama:latest"
  "registry.ollama.ai/library/deepseek-llm:latest"
  "registry.ollama.ai/library/deepseek-v2:latest"
  "registry.ollama.ai/library/deepseek-coder-v2:latest"
  "registry.ollama.ai/library/gemma3:4b"
  "registry.ollama.ai/library/llava:latest"
  "registry.ollama.ai/library/openchat:latest"
  "registry.ollama.ai/library/openthinker:7b"
  "registry.ollama.ai/library/dolphin-mistral:latest"
  "registry.ollama.ai/library/smallthinker:latest"
  "registry.ollama.ai/library/magicoder:latest"
  "registry.ollama.ai/library/wizardlm2:latest"
)

for model in "${models[@]}"; do
  pull "$model"
done
