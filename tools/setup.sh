#!/bin/sh
# One-time setup per session: Python deps + CC0 voice (dataset license CC0, see MODEL_CARD)
pip install --break-system-packages -q piper-tts pillow
mkdir -p /home/claude/work/voices && cd /home/claude/work/voices
for f in en_US-joe-medium.onnx en_US-joe-medium.onnx.json MODEL_CARD; do
  [ -f "$f" ] || curl -sSL -o "$f" "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/joe/medium/$f"
done
grep -q "License: CC0" MODEL_CARD && echo "voice license OK (CC0)" || { echo "VOICE LICENSE NOT CC0 - STOP"; exit 1; }
