"""Hindi TTS (SYSPIN VITS, CC BY 4.0). Usage: say2.py <male|female> <text> <out.wav> [tempo]
Splits into sentences, synthesizes each, joins with short natural pauses, light polish (tempo, EQ, loudness)."""
import sys, re, subprocess, numpy as np, torch, soundfile as sf
sys.path.insert(0, "/home/claude/work/hindi")  # SYSPIN extra.py + model files live here (see setup)
from extra import TTSTokenizer, VitsConfig, CharactersConfig, VitsCharacters
voice, text, out = sys.argv[1], sys.argv[2], sys.argv[3]
tempo = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
base = "/home/claude/work/hindi/"
letters = open(base + ("chars.txt" if voice == "male" else "chars_f.txt")).read().strip("\n")
cfg = VitsConfig(text_cleaner="multilingual_cleaners", characters=CharactersConfig(characters_class=VitsCharacters,
      pad="<PAD>", eos="<EOS>", bos="<BOS>", blank="<BLNK>", characters=letters, punctuations="!¡'(),-.:;¿? ", phonemes=None))
tok, cfg = TTSTokenizer.init_from_config(cfg)
net = torch.jit.load(base + f"hi_{voice}_vits_30hrs.pt")
parts = [p.strip() for p in re.split(r"(?<=[।?!])\s*", text) if p.strip()]
sr, chunks = 22050, []
for p in parts:
    x = torch.from_numpy(np.array(tok.text_to_ids(p))).unsqueeze(0)
    with torch.no_grad():
        y = net(x).squeeze().cpu().numpy()
    # trim leading/trailing near-silence
    idx = np.where(np.abs(y) > 0.02 * np.abs(y).max())[0]
    if len(idx): y = y[max(0, idx[0] - 600): idx[-1] + 1500]
    chunks.append(y)
    pause = 0.32 if p.endswith(("?", "!")) else 0.22
    chunks.append(np.zeros(int(sr * pause)))
sf.write(out + ".raw.wav", np.concatenate(chunks[:-1]), sr)
af = f"atempo={tempo},highpass=f=70,equalizer=f=3000:t=q:w=1.2:g=2,acompressor=threshold=-20dB:ratio=2.5:attack=5:release=80"
subprocess.run(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-i", out + ".raw.wav", "-af", af, "-ar", "22050", out], check=True)
