#!/bin/sh
# One-time setup per session: Python deps + CC0 voice (dataset license CC0, see MODEL_CARD)
pip install --break-system-packages -q piper-tts pillow
mkdir -p /home/claude/work/voices && cd /home/claude/work/voices
for f in en_US-joe-medium.onnx en_US-joe-medium.onnx.json MODEL_CARD; do
  [ -f "$f" ] || curl -sSL -o "$f" "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/joe/medium/$f"
done
grep -q "License: CC0" MODEL_CARD && echo "voice license OK (CC0)" || { echo "VOICE LICENSE NOT CC0 - STOP"; exit 1; }

# --- Hindi voice (SYSPIN Hindi male VITS by SPIRE Lab, IISc Bengaluru; license CC BY 4.0, credit in every description) ---
pip install --break-system-packages -q torch soundfile unidecode numpy
mkdir -p /home/claude/work/hindi && cd /home/claude/work/hindi
for f in extra.py chars.txt hi_male_vits_30hrs.pt README.md; do
  [ -f "$f" ] || curl -sSL -o "$f" "https://huggingface.co/SYSPIN/tts_vits_coquiai_HindiMale/resolve/main/$f"
done
grep -qi "license: cc-by-4.0" README.md && echo "hindi voice license OK (CC BY 4.0)" || { echo "HINDI VOICE LICENSE CHANGED - STOP"; exit 1; }
