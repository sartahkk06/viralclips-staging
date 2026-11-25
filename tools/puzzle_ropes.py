"""Demo puzzle Short: The Burning Rope Puzzle (classic logic puzzle, original script + original 2D animation).
Usage: python3 puzzle_ropes.py <out_dir>
Voice: Piper en_US-joe-medium (CC0 dataset). Font: Poppins (OFL). No music, no third-party footage.
"""
import math, os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 1920, 30
FB = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
FM = "/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf"
VOICE = "/home/claude/work/voices/en_US-joe-medium.onnx"
BG_TOP, BG_BOT = (8, 14, 32), (14, 32, 58)
GOLD, ORANGE, WHITE, GREY, CYAN, ASH = (255, 205, 70), (255, 140, 30), (255, 255, 255), (150, 160, 185), (70, 210, 255), (70, 72, 82)
ROPE_A, ROPE_B = (226, 178, 110), (196, 150, 210)

SCENES = [
    dict(k="hook", vo="Two ropes. One lighter. Can you measure exactly forty five minutes?",
         cap="2 ropes. 1 lighter. Measure exactly 45 minutes?"),
    dict(k="rules", vo="Each rope takes exactly one hour to burn. But they burn unevenly. Half the rope is not half an hour.",
         cap="Each rope burns in 60 min… but UNEVENLY. Half the rope ≠ 30 min."),
    dict(k="pause", vo="Pause now, and comment your method. Three. Two. One.",
         cap="Pause. Comment your method. 3… 2… 1…"),
    dict(k="step1", vo="Light rope A at both ends, and rope B at one end. With two flames, rope A burns out in exactly thirty minutes.",
         cap="Light A at BOTH ends, B at ONE end. A is gone at 30 min."),
    dict(k="step2", vo="The moment A is gone, light the other end of B. B had thirty minutes left. From both ends, that becomes fifteen.",
         cap="Now light B's other end. 30 min left, so it burns in 15."),
    dict(k="reveal", vo="Thirty, plus fifteen. Exactly forty five minutes. No clock needed.",
         cap="30 + 15 = 45 minutes. No clock needed."),
    dict(k="outro", vo="Did you get it? Follow for a new puzzle every day.",
         cap="Got it? Follow for a new puzzle every day."),
]


def tts(text, path):
    subprocess.run(["python3", "-m", "piper", "-m", VOICE, "-f", path, "--length-scale", "0.9"],
                   input=text.encode(), check=True, capture_output=True)
    with wave.open(path) as w:
        return w.getnframes() / w.getframerate()


def F(sz, m=False):
    return ImageFont.truetype(FM if m else FB, sz)


# ---- rope model: uneven burn-time density along the rope (thicker = slower) ----
N = 400
xs = np.linspace(0, 1, N)


def density(seed):
    rng = np.random.default_rng(seed)
    d = 1 + 0.55 * np.sin(xs * 9 + seed) + 0.35 * np.sin(xs * 23 + 2 * seed) + 0.15 * rng.standard_normal(N).cumsum() / 8
    d = np.clip(d, 0.35, None)
    return d


DA, DB = density(1), density(4)
TA = np.concatenate([[0], np.cumsum((DA[1:] + DA[:-1]) / 2)]); TA = TA / TA[-1] * 60
TB = np.concatenate([[0], np.cumsum((DB[1:] + DB[:-1]) / 2)]); TB = TB / TB[-1] * 60


def pos_at(T, minutes):  # flame from left after `minutes`
    return float(np.interp(minutes, T, xs))


def pos_from_right(T, minutes):
    return float(np.interp(60 - minutes, T, xs))


X0, X1 = 120, 960


def draw_rope(d, y, D, col, burnt_ranges, label):
    # rope as varying-thickness segments; burnt ranges drawn as ash
    for i in range(N - 1):
        x = X0 + (X1 - X0) * xs[i]
        x2 = X0 + (X1 - X0) * xs[i + 1]
        th = 10 + 22 * (D[i] - 0.35) / 1.6
        burnt = any(a <= xs[i] <= b for a, b in burnt_ranges)
        c = ASH if burnt else col
        tt = 3 if burnt else th
        d.line([x, y + 6 * math.sin(xs[i] * 30), x2, y + 6 * math.sin(xs[i + 1] * 30)], fill=c, width=int(max(3, tt)))
    d.text((X0 - 80, y - 32), label, font=F(56), fill=WHITE, stroke_width=4, stroke_fill=(0, 0, 0))


def flame(img, x, y, t, scale=1.0):
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g = ImageDraw.Draw(glow)
    f = 1 + 0.15 * math.sin(t * 40 + x)
    r = int(46 * scale * f)
    g.ellipse([x - r, y - r - 20, x + r, y + r - 20], fill=(255, 120, 20, 120))
    g.ellipse([x - r * 0.55, y - r * 0.9 - 20, x + r * 0.55, y + r * 0.4 - 20], fill=(255, 200, 60, 230))
    g.ellipse([x - r * 0.25, y - r * 0.55 - 20, x + r * 0.25, y + r * 0.1 - 20], fill=(255, 250, 220, 255))
    glow = glow.filter(ImageFilter.GaussianBlur(6))
    img.paste(glow, (0, 0), glow)


def bg():
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(0, H, 8):
        k = y / H
        d.rectangle([0, y, W, y + 8], fill=tuple(int(BG_TOP[i] * (1 - k) + BG_BOT[i] * k) for i in range(3)))
    for x in range(0, W, 90):
        d.line([x, 0, x, H], fill=(20, 34, 60), width=1)
    for y in range(0, H, 90):
        d.line([0, y, W, y], fill=(20, 34, 60), width=1)
    return img


BG = bg()


def ctext(d, y, s, f, fill, stroke=5):
    w = d.textlength(s, font=f)
    d.text(((W - w) / 2, y), s, font=f, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))


def clock(d, minutes, y=300, hl=None):
    d.rounded_rectangle([300, y, 780, y + 170], radius=30, fill=(10, 18, 36), outline=hl or CYAN, width=6)
    ctext(d, y + 12, "TIME PASSED", F(34, True), GREY, 0)
    ctext(d, y + 48, f"{int(minutes):02d} MIN", F(96), hl or WHITE, 0)


def ease(p):
    p = max(0.0, min(1.0, p))
    return p * p * (3 - 2 * p)


def wrap(d, s, f, mw):
    out, cur = [], ""
    for w_ in s.split():
        t = (cur + " " + w_).strip()
        if d.textlength(t, font=f) <= mw:
            cur = t
        else:
            out.append(cur); cur = w_
    out.append(cur)
    return out


YA, YB = 900, 1130


def frame(k, p, t, lt):
    img = BG.copy()
    d = ImageDraw.Draw(img)
    if k == "hook":
        a = ease(lt / 0.4)
        ctext(d, 300, "THE BURNING", F(int(110 * (0.7 + 0.3 * a))), GOLD)
        ctext(d, 430, "ROPE PUZZLE", F(int(110 * (0.7 + 0.3 * a))), ORANGE)
        draw_rope(d, YA, DA, ROPE_A, [], "A"); draw_rope(d, YB, DB, ROPE_B, [], "B")
        if lt > 1.2:
            ctext(d, 1330, "MEASURE 45 MIN?", F(92), WHITE)
    elif k == "rules":
        clock(d, 60 * ease(p))
        draw_rope(d, YA, DA, ROPE_A, [], "A"); draw_rope(d, YB, DB, ROPE_B, [], "B")
        ctext(d, 560, "EACH ROPE = 60 MIN", F(76), GOLD)
        if p > 0.45:
            ctext(d, 660, "BUT UNEVEN", F(76), ORANGE)
            # mid-point marker with a "NOT 30" tag
            mx = (X0 + X1) // 2
            d.line([mx, YA - 70, mx, YB + 60], fill=ORANGE, width=4)
            ctext(d, 1300, "HALF ROPE ≠ 30 MIN", F(80), WHITE)
    elif k == "pause":
        draw_rope(d, YA, DA, ROPE_A, [], "A"); draw_rope(d, YB, DB, ROPE_B, [], "B")
        ctext(d, 330, "PAUSE", F(150), GOLD)
        ctext(d, 520, "COMMENT YOUR", F(80), WHITE)
        ctext(d, 610, "METHOD", F(80), WHITE)
        n = 3 - int(min(2.99, max(0, (lt - 1.2) / 0.75)))
        ctext(d, 1270, str(n), F(220), ORANGE)
    elif k == "step1":
        m = 30 * ease((lt - 0.8) / max(1, (DUR[k] - 1.6)))
        clock(d, m)
        aL, aR = pos_at(TA, m), pos_from_right(TA, m)
        bL = pos_at(TB, m)
        draw_rope(d, YA, DA, ROPE_A, [(0, aL), (aR, 1)], "A")
        draw_rope(d, YB, DB, ROPE_B, [(0, bL)], "B")
        ctext(d, 560, "A: BOTH ENDS", F(72), GOLD)
        ctext(d, 650, "B: ONE END", F(72), ROPE_B)
        if m < 29.9:
            for x in (aL, aR):
                flame(img, X0 + (X1 - X0) * x, YA, t)
        flame(img, X0 + (X1 - X0) * bL, YB, t)
        if m >= 29.9:
            ctext(d, 1300, "A GONE = 30 MIN", F(84), ORANGE)
    elif k == "step2":
        m = 30 + 15 * ease((lt - 0.8) / max(1, (DUR[k] - 1.6)))
        clock(d, m, hl=ORANGE if m >= 44.9 else None)
        bL = pos_at(TB, m)
        bR = pos_from_right(TB, m - 30)
        draw_rope(d, YA, DA, ROPE_A, [(0, 1)], "A")
        draw_rope(d, YB, DB, ROPE_B, [(0, bL), (bR, 1)], "B")
        ctext(d, 560, "LIGHT B's", F(72), WHITE)
        ctext(d, 650, "OTHER END", F(72), ORANGE)
        if m < 44.9:
            flame(img, X0 + (X1 - X0) * bL, YB, t); flame(img, X0 + (X1 - X0) * bR, YB, t)
        ctext(d, 1300, "2 FLAMES = 15 MIN", F(84), GOLD)
    elif k == "reveal":
        clock(d, 45, hl=GOLD)
        draw_rope(d, YA, DA, ROPE_A, [(0, 1)], "A"); draw_rope(d, YB, DB, ROPE_B, [(0, 1)], "B")
        s = ["30", "+ 15", "= 45 MIN"]
        for i, part in enumerate(s):
            if lt > 0.3 + i * 0.5:
                ctext(d, 560 + i * 110, part, F(100), [WHITE, ORANGE, GOLD][i])
    elif k == "outro":
        ctext(d, 520, "GOT IT?", F(140), GOLD)
        ctext(d, 720, "NEW PUZZLE", F(90), WHITE)
        ctext(d, 820, "EVERY DAY", F(90), WHITE)
        draw_rope(d, YA + 150, DA, ROPE_A, [], "A"); draw_rope(d, YB + 150, DB, ROPE_B, [], "B")
    return img


def render():
    global DUR
    DUR, parts, t0, tl = {}, [], 0.0, []
    for i, s in enumerate(SCENES):
        p = f"{OUT}/vo_{i}.wav"
        dur = tts(s["vo"], p) + 0.35
        DUR[s["k"]] = dur
        tl.append((t0, dur, s)); parts.append(p); t0 += dur
    total = t0
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "anullsrc=r=22050:cl=mono", "-t", "0.35", f"{OUT}/gap.wav"], check=True)
    with open(f"{OUT}/concat.txt", "w") as fh:
        for p in parts:
            fh.write(f"file '{os.path.abspath(p)}'\nfile '{os.path.abspath(OUT)}/gap.wav'\n")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{OUT}/concat.txt",
                    "-af", "loudnorm=I=-14:TP=-1.5", "-ar", "44100", f"{OUT}/voice.wav"], check=True)
    proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                             "-r", str(FPS), "-i", "-", "-i", f"{OUT}/voice.wav", "-c:v", "libx264", "-preset", "veryfast",
                             "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest",
                             "-movflags", "+faststart", f"{OUT}/clip.mp4"], stdin=subprocess.PIPE)
    capf = F(54)
    for n in range(int(total * FPS)):
        t = n / FPS
        s0, dur, sc = [x for x in tl if x[0] <= t][-1]
        lt = t - s0
        img = frame(sc["k"], lt / dur, t, lt)
        d = ImageDraw.Draw(img)
        lines = wrap(d, sc["cap"], capf, W - 160)
        top = 1520
        box = Image.new("RGBA", (W - 100, len(lines) * 72 + 36), (0, 0, 0, 175))
        img.paste(box, (50, top), box)
        for i, ln in enumerate(lines):
            ctext(d, top + 18 + i * 72, ln, capf, WHITE, 3)
        d.rectangle([0, H - 14, int(W * t / total), H], fill=ORANGE)
        proc.stdin.write(img.tobytes())
        if n == int(2.0 * FPS):
            img.save(f"{OUT}/thumb.png")
    proc.stdin.close(); proc.wait()
    print("seconds", round(total, 1))


if __name__ == "__main__":
    render()
