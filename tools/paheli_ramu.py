"""Demo Hindi paheli Short: "Ramu ke pitaji ke 4 bete" (classic riddle, original script + original 2D cartoon animation).
Usage: python3 paheli_ramu.py <out_dir>
Voice: SYSPIN Hindi male VITS (CC BY 4.0, credit in description). Font: Poppins (OFL). No music, no third-party footage.
"""
import math, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 1920, 30
FB = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
FM = "/usr/share/fonts/truetype/google-fonts/Poppins-SemiBold.ttf"
SAY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hindi_tts.py")
SKIN, HAIR, INK = (236, 188, 150), (40, 30, 30), (35, 25, 30)
YEL, WHITE, RED, GREEN = (255, 205, 60), (255, 255, 255), (230, 60, 60), (70, 200, 110)
KID_SHIRTS = [(66, 150, 240), (240, 110, 80), (110, 200, 120), (180, 120, 230)]
NAMES = ["SOMVAAR", "MANGALVAAR", "BUDHVAAR", "?"]

# hi = Devanagari voiceover, cap = Hinglish caption (*word* = highlighted), sil = extra silent seconds
SCENES = [
    dict(k="hook", hi="सिर्फ एक परसेंट लोग ही इस पहेली का सही जवाब दे पाते हैं।", cap="Sirf *1%* log hi is paheli ka sahi jawab de paate hain."),
    dict(k="family", hi="रामू के पापा के चार बेटे हैं।", cap="*Ramu* ke papa ke *4 bete* hain."),
    dict(k="names", hi="पहले बेटे का नाम है सोमवार। दूसरे का, मंगलवार। और तीसरे का, बुधवार।", cap="Pehla *Somvaar*, doosra *Mangalvaar*, teesra *Budhvaar*."),
    dict(k="ask", hi="तो बताओ, चौथे बेटे का नाम क्या है?", cap="Toh batao, *chauthe* bete ka naam kya hai?"),
    dict(k="timer", hi="सोचो, तुम्हारे पास बस पाँच सेकंड हैं।", cap="Socho, tumhare paas bas *5 second* hain.", sil=4.0),
    dict(k="wrong", hi="ज़्यादातर लोग बोलते हैं, गुरुवार। पर रुको!", cap="Zyaadatar log bolte hain *Guruvaar*... par *ruko!*"),
    dict(k="reveal", hi="जवाब तो सवाल में ही छुपा है। रामू के पापा के चार बेटे हैं, तो चौथा बेटा है, खुद रामू!", cap="Jawab sawaal mein hi chhupa hai. Chautha beta hai *khud RAMU!*"),
    dict(k="outro", hi="अपने सबसे होशियार दोस्त को टैग करो। और ऐसी ही पहेलियों के लिए, फॉलो कर लो।", cap="Sabse *hoshiyaar* dost ko tag karo. *Follow* kar lo!"),
]


def F(s, m=False):
    return ImageFont.truetype(FM if m else FB, s)


def tts(text, path):
    subprocess.run(["python3", SAY, "male", text, os.path.abspath(path), "1.05"], check=True, capture_output=True, cwd="/home/claude/work/hindi")
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True).stdout
    return float(out)


def sunburst(t, warm):
    c1, c2 = ((242, 140, 40), (226, 110, 30)) if warm else ((40, 90, 170), (30, 70, 140))
    img = Image.new("RGB", (W, H), c2)
    d = ImageDraw.Draw(img)
    cx, cy, R = W / 2, H * 0.42, 2400
    rot = t * 6
    for i in range(24):
        a0 = math.radians(rot + i * 15); a1 = math.radians(rot + i * 15 + 7.5)
        d.polygon([(cx, cy), (cx + R * math.cos(a0), cy + R * math.sin(a0)), (cx + R * math.cos(a1), cy + R * math.sin(a1))], fill=c1)
    vig = Image.new("L", (W, H), 0)
    ImageDraw.Draw(vig).ellipse([-300, -200, W + 300, H + 200], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(160))
    dark = Image.new("RGB", (W, H), (0, 0, 0))
    return Image.composite(img, dark, vig)


def person(d, x, y, s, shirt, t, adult=False, wave=False, face="smile", label=None, lift=0):
    """Original flat cartoon person. (x, y) = feet centre, s = scale."""
    bob = math.sin(t * 4 + x) * 4 * s
    y = y + bob
    lw = int(7 * s)
    # legs
    for dx in (-18, 18):
        d.rounded_rectangle([x + dx * s - 13 * s, y - 95 * s, x + dx * s + 13 * s, y], radius=8 * s, fill=(60, 60, 80), outline=INK, width=lw)
        d.ellipse([x + dx * s - 22 * s, y - 14 * s, x + dx * s + 18 * s, y + 10 * s], fill=INK)
    # body
    top = y - 250 * s
    d.rounded_rectangle([x - 62 * s, top, x + 62 * s, y - 85 * s], radius=30 * s, fill=shirt, outline=INK, width=lw)
    for k in range(3):
        d.ellipse([x - 5 * s, top + (40 + k * 40) * s, x + 5 * s, top + (50 + k * 40) * s], fill=INK)
    # arms
    ang = math.sin(t * 7) * 25 if wave else 0
    d.line([x - 60 * s, top + 30 * s, x - 90 * s, top + 140 * s], fill=INK, width=int(24 * s))
    d.line([x - 60 * s, top + 30 * s, x - 90 * s, top + 140 * s], fill=shirt, width=int(12 * s))
    if wave:
        ex = x + 60 * s + 80 * s * math.cos(math.radians(-60 + ang)); ey = top + 30 * s + 80 * s * math.sin(math.radians(-60 + ang))
    else:
        ex, ey = x + 90 * s, top + 140 * s
    d.line([x + 60 * s, top + 30 * s, ex, ey], fill=INK, width=int(24 * s))
    d.line([x + 60 * s, top + 30 * s, ex, ey], fill=shirt, width=int(12 * s))
    d.ellipse([ex - 16 * s, ey - 16 * s, ex + 16 * s, ey + 16 * s], fill=SKIN, outline=INK, width=lw)
    d.ellipse([x - 106 * s, top + 124 * s, x - 74 * s, top + 156 * s], fill=SKIN, outline=INK, width=lw)
    # head
    hr = 72 * s
    hy = top - hr + 10 * s
    d.ellipse([x - hr, hy - hr, x + hr, hy + hr], fill=SKIN, outline=INK, width=lw)
    d.chord([x - hr, hy - hr, x + hr, hy + hr * 0.6], 180, 360, fill=HAIR)
    d.ellipse([x - hr - 10 * s, hy - 8 * s, x - hr + 14 * s, hy + 24 * s], fill=SKIN, outline=INK, width=lw)
    d.ellipse([x + hr - 14 * s, hy - 8 * s, x + hr + 10 * s, hy + 24 * s], fill=SKIN, outline=INK, width=lw)
    blink = (int(t * 10 + x) % 40) == 0
    for dx in (-26, 26):
        if blink:
            d.line([x + dx * s - 9 * s, hy + 8 * s, x + dx * s + 9 * s, hy + 8 * s], fill=INK, width=lw)
        else:
            d.ellipse([x + dx * s - 14 * s, hy - 8 * s, x + dx * s + 14 * s, hy + 20 * s], fill=WHITE, outline=INK, width=int(4 * s))
            d.ellipse([x + dx * s - 6 * s, hy, x + dx * s + 6 * s, hy + 12 * s], fill=INK)
    if adult:
        d.chord([x - 44 * s, hy + 22 * s, x + 44 * s, hy + 58 * s], 180, 360, fill=HAIR)  # mustache
        d.line([x - 34 * s, hy - 26 * s, x - 14 * s, hy - 22 * s], fill=INK, width=lw)
        d.line([x + 14 * s, hy - 22 * s, x + 34 * s, hy - 26 * s], fill=INK, width=lw)
    if face == "smile":
        d.arc([x - 22 * s, hy + 26 * s, x + 22 * s, hy + 52 * s], 10, 170, fill=INK, width=lw)
    elif face == "o":
        d.ellipse([x - 10 * s, hy + 34 * s, x + 10 * s, hy + 54 * s], fill=INK)
    if label:
        f = F(max(36, int(40 * s)) if len(label) > 2 else int(70 * s))
        tw = d.textlength(label, font=f)
        lx0, ly0 = x - tw / 2 - 18, hy - hr - 90 * s - lift
        d.rounded_rectangle([lx0, ly0, x + tw / 2 + 18, ly0 + f.size + 26], radius=18, fill=WHITE, outline=INK, width=5)
        d.text((x - tw / 2, ly0 + 8), label, font=f, fill=RED if label in ("?", "GURUVAAR?") else INK)


def ctext(d, y, s, f, fill, stroke=6):
    w = d.textlength(s, font=f)
    d.text(((W - w) / 2, y), s, font=f, fill=fill, stroke_width=stroke, stroke_fill=INK)


def caption(img, d, cap):
    f = F(52)
    words = cap.split()
    lines, cur = [], []
    for w_ in words:
        trial = " ".join(x.replace("*", "") for x in cur + [w_])
        if d.textlength(trial, font=f) > W - 180 and cur:
            lines.append(cur); cur = [w_]
        else:
            cur.append(w_)
    lines.append(cur)
    top = 1580
    box = Image.new("RGBA", (W - 120, len(lines) * 70 + 34), (25, 20, 30, 200))
    img.paste(box, (60, top), box)
    for i, ln in enumerate(lines):
        plain = " ".join(x.replace("*", "") for x in ln)
        x = (W - d.textlength(plain, font=f)) / 2
        for w_ in ln:
            hl = "*" in w_
            ww = w_.replace("*", "")
            d.text((x, top + 16 + i * 70), ww, font=f, fill=YEL if hl else WHITE)
            x += d.textlength(ww + " ", font=f)


def ease(p):
    p = max(0.0, min(1.0, p)); return p * p * (3 - 2 * p)


def frame(k, lt, dur, t, idx):
    img = sunburst(t, warm=idx % 2 == 1)
    d = ImageDraw.Draw(img)
    kids_x = [180, 420, 660, 900]
    if k == "hook":
        a = ease(lt / 0.5)
        d.rounded_rectangle([300, 260, 780, 400], radius=40, fill=YEL, outline=INK, width=8)
        ctext(d, 272, "PAHELI", F(int(100 * (0.8 + 0.2 * a))), INK, 0)
        ctext(d, 450, "ONLY 1% GET IT", F(80), WHITE)
        person(d, W / 2, 1450, 1.6, (40, 110, 200), t, adult=True, wave=True)
    elif k == "family":
        person(d, W / 2, 1060, 1.25, (40, 110, 200), t, adult=True, label="RAMU KE PAPA")
        for i, x in enumerate(kids_x):
            if lt > 0.4 + i * 0.25:
                person(d, x, 1500, 0.8, KID_SHIRTS[i], t)
        ctext(d, 230, "4 BETE", F(110), YEL)
    elif k in ("names", "ask", "timer", "wrong", "reveal"):
        shown = 3 if k != "names" else min(3, int(lt / max(0.8, dur / 3.3)) + 1)
        for i, x in enumerate(kids_x):
            lab = None
            if i < shown:
                lab = NAMES[i]
            if i == 3 and k in ("ask", "timer"):
                lab = "?"
            if i == 3 and k == "wrong":
                lab = "GURUVAAR?"
            if i == 3 and k == "reveal":
                lab = "RAMU!" if lt > 1.5 else "?"
            person(d, x, 1500, 0.8, KID_SHIRTS[i], t, label=lab, face="o" if (i == 3 and k == "wrong") else "smile", lift=75 if i % 2 else 0)
        if k == "names":
            ctext(d, 260, "NAAM SUNO", F(100), WHITE)
        if k == "ask":
            ctext(d, 260, "4TH BETA?", F(120), YEL)
        if k == "timer":
            left = max(0, 5 - int(lt * 5 / max(dur - 0.3, 1)))
            cx, cy, r = W / 2, 520, 170
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(120, 25, 40), outline=YEL, width=14)
            frac = (lt * 5 / max(dur - 0.3, 1)) % 1
            d.arc([cx - r, cy - r, cx + r, cy + r], -90, -90 + 360 * (1 - frac), fill=WHITE, width=14)
            ctext(d, cy - 120, str(max(left, 1)), F(200), WHITE, 0)
        if k == "wrong":
            ctext(d, 260, "GURUVAAR?", F(120), WHITE)
            if lt > dur * 0.55:
                d.line([250, 300, 830, 400], fill=RED, width=22)
                ctext(d, 450, "RUKO!", F(130), RED)
        if k == "reveal":
            if lt > 1.5:
                ctext(d, 240, "JAWAB:", F(90), WHITE)
                ctext(d, 350, "RAMU", F(190), YEL)
            else:
                ctext(d, 300, "SAWAAL MEIN", F(90), WHITE)
                ctext(d, 400, "HI JAWAB", F(90), YEL)
    elif k == "outro":
        person(d, W * 0.32, 1450, 1.2, (40, 110, 200), t, adult=True, wave=True)
        person(d, W * 0.72, 1450, 0.95, KID_SHIRTS[3], t, label="RAMU", wave=True)
        d.rounded_rectangle([220, 280, 860, 420], radius=60, fill=WHITE, outline=INK, width=8)
        ctext(d, 300, "TAG A FRIEND", F(76), INK, 0)
        ctext(d, 480, "FOLLOW FOR", F(80), WHITE)
        ctext(d, 580, "DAILY PAHELI", F(80), YEL)
    return img


def render():
    parts, tl, t0 = [], [], 0.0
    for i, s in enumerate(SCENES):
        p = f"{OUT}/vo_{i}.wav"
        dur = tts(s["hi"], p)
        sil = s.get("sil", 0) + 0.35
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "anullsrc=r=22050:cl=mono", "-t", str(sil), f"{OUT}/gap_{i}.wav"], check=True)
        parts += [p, f"{OUT}/gap_{i}.wav"]
        tl.append((t0, dur + sil, s, i)); t0 += dur + sil
    total = t0
    with open(f"{OUT}/concat.txt", "w") as fh:
        for p in parts:
            fh.write(f"file '{os.path.abspath(p)}'\n")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{OUT}/concat.txt",
                    "-af", "loudnorm=I=-14:TP=-1.5", "-ar", "44100", f"{OUT}/voice.wav"], check=True)
    proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                             "-r", str(FPS), "-i", "-", "-i", f"{OUT}/voice.wav", "-c:v", "libx264", "-preset", "veryfast",
                             "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest",
                             "-movflags", "+faststart", f"{OUT}/clip.mp4"], stdin=subprocess.PIPE)
    for n in range(int(total * FPS)):
        t = n / FPS
        s0, dur, sc, idx = [x for x in tl if x[0] <= t][-1]
        lt = t - s0
        img = frame(sc["k"], lt, dur, t, idx)
        d = ImageDraw.Draw(img)
        caption(img, d, sc["cap"])
        d.rectangle([0, H - 14, int(W * t / total), H], fill=YEL)
        proc.stdin.write(img.tobytes())
        if n == int(1.5 * FPS):
            img.save(f"{OUT}/thumb.png")
    proc.stdin.close(); proc.wait()
    print("seconds", round(total, 1))


if __name__ == "__main__":
    render()
