"""Render an original 1080x1920 Short: CC0 voiceover (Piper joe-medium) + animated text + burned captions.
Usage: python3 make_clip.py <out_dir> <spec.json>
spec.json: {"source": "...", "scenes": [{"vo": "spoken text", "cap": "caption", "big": [["TEXT", size, "PINK|CYAN|YELLOW|WHITE|GREY"], ...]}]}
A big line "COUNTER:<number>:<prefix>" animates a count-up to <number>.
Font: Poppins Bold (no emoji, no checkmarks; use words). Allowed symbols include ₹ ≈ × … ·
"""
import json, math, os, subprocess, sys, wave
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 1920, 30
FONT = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
FONT_M = "/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf"
VOICE = "/home/claude/work/voices/en_US-joe-medium.onnx"

BG1, BG2 = (10, 8, 24), (48, 12, 64)
PINK, CYAN, YELLOW, WHITE, GREY = (255, 64, 160), (60, 220, 255), (255, 214, 64), (255, 255, 255), (170, 170, 190)

SPEC = json.load(open(sys.argv[2]))
COLORS = dict(PINK=PINK, CYAN=CYAN, YELLOW=YELLOW, WHITE=WHITE, GREY=GREY)
SCENES = [dict(vo=s["vo"], cap=s["cap"], big=[(b[0], b[1], COLORS[b[2]]) for b in s["big"]]) for s in SPEC["scenes"]]
SOURCE = SPEC.get("source", "")


def tts(text, path):
    subprocess.run(["python3", "-m", "piper", "-m", VOICE, "-f", path, "--length-scale", "0.92"],
                   input=text.encode(), check=True, capture_output=True)
    with wave.open(path) as w:
        return w.getnframes() / w.getframerate()


def font(size, medium=False):
    return ImageFont.truetype(FONT_M if medium else FONT, size)


def bg_frame(t):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(0, H, 8):
        k = y / H
        c = tuple(int(BG1[i] * (1 - k) + BG2[i] * k) for i in range(3))
        d.rectangle([0, y, W, y + 8], fill=c)
    # drifting neon grid lines (original motion graphic)
    off = int((t * 60) % 120)
    for y in range(1100 + off, H, 120):
        d.line([0, y, W, y], fill=(90, 30, 110), width=2)
    for x in range(-W, 2 * W, 140):
        d.line([W // 2, 1100, x + int(math.sin(t) * 20), H], fill=(70, 25, 95), width=2)
    return img


def text_center(d, y, text, f, fill, stroke=6):
    w = d.textlength(text, font=f)
    d.text(((W - w) / 2, y), text, font=f, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))


def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if d.textlength(trial, font=f) <= maxw:
            cur = trial
        else:
            lines.append(cur); cur = wd
    lines.append(cur)
    return lines


def ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def render():
    audio_parts, timeline, t0 = [], [], 0.0
    for i, s in enumerate(SCENES):
        p = f"{OUT}/vo_{i}.wav"
        dur = tts(s["vo"], p) + 0.25
        audio_parts.append((p, dur))
        timeline.append((t0, dur, s))
        t0 += dur
    total = t0
    print("total seconds", round(total, 2))

    # audio: concat with 0.25s gaps
    with open(f"{OUT}/concat.txt", "w") as fh:
        for p, dur in audio_parts:
            fh.write(f"file '{os.path.abspath(p)}'\nfile '{os.path.abspath(OUT)}/gap.wav'\n")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "anullsrc=r=22050:cl=mono", "-t", "0.25", f"{OUT}/gap.wav"], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{OUT}/concat.txt",
                    "-af", "loudnorm=I=-14:TP=-1.5", "-ar", "44100", f"{OUT}/voice.wav"], check=True)

    proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                             "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", f"{OUT}/voice.wav",
                             "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                             "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart",
                             f"{OUT}/clip.mp4"], stdin=subprocess.PIPE)
    nframes = int(total * FPS)
    cap_f, src_f = font(58), font(30, medium=True)
    for n in range(nframes):
        t = n / FPS
        idx = max(i for i, (s0, _, _) in enumerate(timeline) if s0 <= t)
        s0, dur, sc = timeline[idx]
        lt = t - s0
        img = bg_frame(t)
        d = ImageDraw.Draw(img)
        # big animated lines, staggered pop-in
        y = 430
        for j, (txt, size, col) in enumerate(sc["big"]):
            a = ease((lt - j * 0.18) / 0.35)
            if a <= 0:
                y += int(size * 1.25); continue
            if txt.startswith("COUNTER:"):
                _, num, pre = (txt.split(":", 2) + [""])[:3]
                v = int(float(num) * ease(lt / max(0.6, dur * 0.6)))
                txt = f"{pre}{v:,}"
            sz = max(10, int(size * (0.7 + 0.3 * a)))
            f = font(sz)
            text_center(d, y + (1 - a) * 60, txt, f, col)
            y += int(size * 1.25)
        # caption box (burned-in)
        lines = wrap(d, sc["cap"], cap_f, W - 160)
        bh = len(lines) * 76 + 40
        top = 1380
        box = Image.new("RGBA", (W - 100, bh), (0, 0, 0, 170))
        img.paste(box, (50, top), box)
        for k, ln in enumerate(lines):
            text_center(d, top + 20 + k * 76, ln, cap_f, WHITE, stroke=3)
        # progress bar (helps loop feel) + source line
        d.rectangle([0, H - 14, int(W * t / total), H], fill=PINK)
        text_center(d, H - 120, SOURCE, src_f, GREY, stroke=2)
        proc.stdin.write(img.tobytes())
        if n == int(1.0 * FPS):
            img.save(f"{OUT}/thumb.png")
    proc.stdin.close(); proc.wait()
    json.dump({"duration": total, "scenes": [s["cap"] for s in SCENES]}, open(f"{OUT}/meta.json", "w"), indent=1)


if __name__ == "__main__":
    render()
