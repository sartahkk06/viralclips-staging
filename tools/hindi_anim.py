"""Hindi animated Short renderer (original flat 2D cartoon + Hindi voice + Hinglish captions).

Usage: python3 hindi_anim.py <out_dir> <spec.json>

spec.json:
{
  "palette": "blue" | "orange" | "green" | "purple" | "mix",   # sunburst colours; "mix" alternates per scene (default)
  "scenes": [
    {"hi": "Devanagari voice line (spoken)", "cap": "Hinglish caption, *word* = yellow highlight",
     "sil": 0,                      # optional extra silent seconds after the line (e.g. 4 for a countdown)
     "head": "BIG TOP TEXT",        # optional headline (Latin letters/digits only)
     "sub": "SECOND LINE",          # optional
     "v": {...}}                    # one visual block, see below
  ]
}
Visual blocks ("v"), choose one per scene:
  {"type": "host", "wave": true, "badge": "PAHELI"}                       # channel host character
  {"type": "chars", "people": [{"role": "man|woman|elder|kid|host|teacher|doctor", "shirt": "blue|red|green|purple|orange|teal|pink|brown",
                     "label": "NAME", "face": "smile|o|sad|angry|laugh", "wave": false, "say": "short bubble text"}]}   # 1-4 people
  {"type": "list", "items": ["TIP ONE", "TIP TWO"], "icons": ["check", ...]}   # items appear one by one
  {"type": "compare", "left": {"title": "GALAT", "items": ["..."]}, "right": {"title": "SAHI", "items": ["..."]}}
  {"type": "timer", "secs": 5}
  {"type": "icon", "name": "bulb|phone|clock|coin|book|heart|star|warning|check|cross|question|water|brain|money|lock|battery", "text": "CAPTION UNDER ICON"}
  {"type": "number", "value": 1024, "prefix": "", "suffix": ""}           # count-up number
  {"type": "options", "items": ["A) ...", "B) ...", "C) ..."], "answer": 1, "reveal": false}  # quiz options; reveal highlights answer
On-screen text must be Latin script (font has no Devanagari). Voice: SYSPIN Hindi male VITS (CC BY 4.0) via hindi_tts.py.
"""
import json, math, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT, SPEC = sys.argv[1], json.load(open(sys.argv[2]))
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 1920, 30
FB = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
FM = "/usr/share/fonts/truetype/google-fonts/Poppins-SemiBold.ttf"
SAY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hindi_tts.py")
SKIN, SKIN2, HAIR, GREYH, INK = (236, 188, 150), (205, 150, 110), (40, 30, 30), (200, 200, 205), (35, 25, 30)
YEL, WHITE, RED, GREEN = (255, 205, 60), (255, 255, 255), (230, 60, 60), (60, 190, 100)
SHIRTS = dict(blue=(50, 120, 210), red=(225, 80, 70), green=(70, 180, 110), purple=(160, 110, 220), orange=(245, 150, 50),
              teal=(40, 170, 170), pink=(235, 120, 170), brown=(150, 100, 60), white=(240, 240, 240))
PALS = dict(blue=((40, 90, 170), (30, 70, 140)), orange=((242, 140, 40), (226, 110, 30)), green=((50, 150, 90), (35, 120, 70)),
            purple=((120, 70, 180), (95, 55, 150)))


def F(s, m=False):
    return ImageFont.truetype(FM if m else FB, int(s))


def tts(text, path):
    subprocess.run(["python3", SAY, "male", text, os.path.abspath(path), "1.05"], check=True, capture_output=True)
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                                capture_output=True, text=True).stdout)


_BG = {}


def sunburst(t, pal):
    c1, c2 = PALS[pal]
    img = Image.new("RGB", (W, H), c2)
    d = ImageDraw.Draw(img)
    cx, cy, R, rot = W / 2, H * 0.42, 2400, t * 6
    for i in range(24):
        a0, a1 = math.radians(rot + i * 15), math.radians(rot + i * 15 + 7.5)
        d.polygon([(cx, cy), (cx + R * math.cos(a0), cy + R * math.sin(a0)), (cx + R * math.cos(a1), cy + R * math.sin(a1))], fill=c1)
    if "vig" not in _BG:
        v = Image.new("L", (W, H), 0)
        ImageDraw.Draw(v).ellipse([-300, -200, W + 300, H + 200], fill=255)
        _BG["vig"] = v.filter(ImageFilter.GaussianBlur(160))
    return Image.composite(img, Image.new("RGB", (W, H), (0, 0, 0)), _BG["vig"])


def ctext(d, y, s, f, fill, stroke=6, x=None):
    w = d.textlength(s, font=f)
    d.text(((W - w) / 2 if x is None else x - w / 2, y), s, font=f, fill=fill, stroke_width=stroke, stroke_fill=INK)


def fit(d, s, size, maxw):
    f = F(size)
    while d.textlength(s, font=f) > maxw and size > 30:
        size -= 4; f = F(size)
    return f


# ---------------- characters ----------------
def person(d, x, y, s, role="man", shirt="blue", t=0, wave=False, face="smile", label=None, say=None, lift=0):
    shirt_c = SHIRTS.get(shirt, SHIRTS["blue"])
    kid = role == "kid"
    s = s * (0.72 if kid else 1.0)
    bob = math.sin(t * 4 + x) * 4 * s
    y = y + bob
    lw = max(3, int(7 * s))
    skin = SKIN2 if role in ("elder", "teacher") else SKIN
    hair = GREYH if role == "elder" else HAIR
    # legs / dress
    if role == "woman":
        d.polygon([(x - 70 * s, y - 20 * s), (x + 70 * s, y - 20 * s), (x + 50 * s, y - 120 * s), (x - 50 * s, y - 120 * s)], fill=shirt_c, outline=INK)
        for dx in (-22, 22):
            d.ellipse([x + dx * s - 20 * s, y - 22 * s, x + dx * s + 18 * s, y + 6 * s], fill=INK)
    else:
        for dx in (-18, 18):
            d.rounded_rectangle([x + dx * s - 13 * s, y - 95 * s, x + dx * s + 13 * s, y], radius=8 * s, fill=(60, 60, 80), outline=INK, width=lw)
            d.ellipse([x + dx * s - 22 * s, y - 14 * s, x + dx * s + 18 * s, y + 10 * s], fill=INK)
    top = y - 250 * s
    d.rounded_rectangle([x - 62 * s, top, x + 62 * s, y - 85 * s], radius=30 * s, fill=shirt_c, outline=INK, width=lw)
    if role == "doctor":
        d.rounded_rectangle([x - 62 * s, top, x + 62 * s, y - 85 * s], radius=30 * s, fill=WHITE, outline=INK, width=lw)
        d.rectangle([x - 22 * s, top, x + 22 * s, top + 60 * s], fill=shirt_c)
        d.arc([x - 40 * s, top + 10 * s, x + 40 * s, top + 110 * s], 20, 160, fill=INK, width=lw)
    elif role == "woman":
        d.line([x - 60 * s, top + 10 * s, x + 50 * s, top + 160 * s], fill=YEL, width=int(18 * s))  # dupatta
    else:
        for k in range(3):
            d.ellipse([x - 5 * s, top + (40 + k * 40) * s, x + 5 * s, top + (50 + k * 40) * s], fill=INK)
    # arms
    ang = math.sin(t * 7) * 25 if wave else 0
    def arm(x0, y0, x1, y1):
        d.line([x0, y0, x1, y1], fill=INK, width=int(24 * s)); d.line([x0, y0, x1, y1], fill=WHITE if role == "doctor" else shirt_c, width=int(12 * s))
        d.ellipse([x1 - 16 * s, y1 - 16 * s, x1 + 16 * s, y1 + 16 * s], fill=skin, outline=INK, width=lw)
    arm(x - 60 * s, top + 30 * s, x - 90 * s, top + 140 * s)
    if wave:
        arm(x + 60 * s, top + 30 * s, x + 60 * s + 80 * s * math.cos(math.radians(-60 + ang)), top + 30 * s + 80 * s * math.sin(math.radians(-60 + ang)))
    else:
        arm(x + 60 * s, top + 30 * s, x + 90 * s, top + 140 * s)
    # head
    hr = 72 * s
    hy = top - hr + 10 * s
    if role == "woman":
        d.ellipse([x - hr - 6 * s, hy - hr - 6 * s, x + hr + 6 * s, hy + hr * 1.3], fill=hair)  # long hair behind
    d.ellipse([x - hr, hy - hr, x + hr, hy + hr], fill=skin, outline=INK, width=lw)
    if role == "woman":
        d.chord([x - hr, hy - hr, x + hr, hy + hr * 0.4], 180, 360, fill=hair)
        d.ellipse([x - 6 * s, hy - 30 * s, x + 6 * s, hy - 18 * s], fill=RED)  # bindi
    elif role == "elder":
        d.chord([x - hr, hy - hr, x + hr, hy + hr * 0.2], 200, 340, fill=hair)
        for dx in (-26, 26):
            d.ellipse([x + dx * s - 22 * s, hy - 14 * s, x + dx * s + 22 * s, hy + 26 * s], outline=INK, width=lw)
        d.line([x - 4 * s, hy + 6 * s, x + 4 * s, hy + 6 * s], fill=INK, width=lw)
    else:
        d.chord([x - hr, hy - hr, x + hr, hy + hr * 0.6], 180, 360, fill=hair)
    if role == "teacher":
        for dx in (-26, 26):
            d.rectangle([x + dx * s - 22 * s, hy - 12 * s, x + dx * s + 22 * s, hy + 22 * s], outline=INK, width=lw)
    for ex in (-1, 1):
        d.ellipse([x + ex * hr - 12 * s, hy - 8 * s, x + ex * hr + 12 * s, hy + 24 * s], fill=skin, outline=INK, width=lw)
    blink = (int(t * 10 + x) % 40) == 0
    for dx in (-26, 26):
        if blink:
            d.line([x + dx * s - 9 * s, hy + 8 * s, x + dx * s + 9 * s, hy + 8 * s], fill=INK, width=lw)
        else:
            d.ellipse([x + dx * s - 13 * s, hy - 6 * s, x + dx * s + 13 * s, hy + 20 * s], fill=WHITE, outline=INK, width=max(2, int(4 * s)))
            d.ellipse([x + dx * s - 6 * s, hy + 1 * s, x + dx * s + 6 * s, hy + 13 * s], fill=INK)
        if face == "angry":
            d.line([x + dx * s - 16 * s, hy - 22 * s + (8 * s if dx < 0 else -8 * s) * -1, x + dx * s + 16 * s, hy - 22 * s + (8 * s if dx < 0 else -8 * s)], fill=INK, width=lw)
    if role in ("man", "host", "elder", "teacher", "doctor"):
        d.chord([x - 40 * s, hy + 22 * s, x + 40 * s, hy + 54 * s], 180, 360, fill=hair)  # mustache
    if face == "smile":
        d.arc([x - 22 * s, hy + 26 * s, x + 22 * s, hy + 52 * s], 10, 170, fill=INK, width=lw)
    elif face == "laugh":
        d.chord([x - 26 * s, hy + 24 * s, x + 26 * s, hy + 62 * s], 0, 180, fill=INK)
        d.chord([x - 16 * s, hy + 40 * s, x + 16 * s, hy + 60 * s], 0, 180, fill=RED)
    elif face == "sad":
        d.arc([x - 20 * s, hy + 40 * s, x + 20 * s, hy + 64 * s], 200, 340, fill=INK, width=lw)
    elif face == "angry":
        d.line([x - 18 * s, hy + 48 * s, x + 18 * s, hy + 48 * s], fill=INK, width=lw)
    else:  # o
        d.ellipse([x - 10 * s, hy + 34 * s, x + 10 * s, hy + 54 * s], fill=INK)
    head_top = hy - hr
    if label:
        f = fit(d, label, max(36, int(44 * s)) if len(label) > 2 else int(70 * s), 300)
        tw = d.textlength(label, font=f)
        ly0 = head_top - 70 * s - f.size - lift
        d.rounded_rectangle([x - tw / 2 - 18, ly0, x + tw / 2 + 18, ly0 + f.size + 26], radius=18, fill=WHITE, outline=INK, width=5)
        d.text((x - tw / 2, ly0 + 8), label, font=f, fill=RED if label.endswith("?") else INK)
        head_top = ly0
    if say:
        bubble(d, x, head_top - 30, say)


def bubble(d, x, ybottom, text):
    f = F(46)
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        tr = (cur + " " + w_).strip()
        if d.textlength(tr, font=f) > 420 and cur:
            lines.append(cur); cur = w_
        else:
            cur = tr
    lines.append(cur)
    bw = max(d.textlength(l, font=f) for l in lines) + 60
    bh = len(lines) * 60 + 40
    bx = min(max(x - bw / 2, 30), W - 30 - bw)
    by = ybottom - bh - 30
    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=36, fill=WHITE, outline=INK, width=6)
    d.polygon([(x - 18, by + bh - 3), (x + 18, by + bh - 3), (x, by + bh + 30)], fill=WHITE, outline=INK)
    d.line([x - 15, by + bh - 3, x + 15, by + bh - 3], fill=WHITE, width=8)
    for i, l in enumerate(lines):
        d.text((bx + (bw - d.textlength(l, font=f)) / 2, by + 20 + i * 60), l, font=f, fill=INK)


# ---------------- icons ----------------
def icon(d, name, cx, cy, r, t=0):
    lw = max(6, int(r / 10))
    if name == "check":
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GREEN, outline=INK, width=lw)
        d.line([cx - r * .45, cy, cx - r * .1, cy + r * .4, cx + r * .5, cy - r * .4], fill=WHITE, width=int(lw * 1.6), joint="curve")
    elif name == "cross":
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED, outline=INK, width=lw)
        for a in (1, -1):
            d.line([cx - r * .4, cy - a * r * .4, cx + r * .4, cy + a * r * .4], fill=WHITE, width=int(lw * 1.6))
    elif name == "bulb":
        glow = 0.5 + 0.5 * math.sin(t * 5)
        d.ellipse([cx - r * 1.2, cy - r * 1.3, cx + r * 1.2, cy + r * 1.1], fill=(255, 240, int(120 + 80 * glow)))
        d.ellipse([cx - r * .8, cy - r, cx + r * .8, cy + r * .6], fill=YEL, outline=INK, width=lw)
        d.rectangle([cx - r * .35, cy + r * .55, cx + r * .35, cy + r * .95], fill=GREYH, outline=INK, width=lw)
    elif name == "phone":
        d.rounded_rectangle([cx - r * .55, cy - r, cx + r * .55, cy + r], radius=r * .2, fill=INK)
        d.rounded_rectangle([cx - r * .45, cy - r * .82, cx + r * .45, cy + r * .7], radius=r * .1, fill=(120, 200, 255))
        d.ellipse([cx - r * .08, cy + r * .78, cx + r * .08, cy + r * .94], fill=GREYH)
    elif name == "clock":
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=WHITE, outline=INK, width=lw)
        a = t * 2
        d.line([cx, cy, cx + r * .7 * math.cos(a), cy + r * .7 * math.sin(a)], fill=INK, width=lw)
        d.line([cx, cy, cx, cy - r * .5], fill=RED, width=lw)
    elif name in ("coin", "money"):
        for k in range(3):
            o = k * r * .25
            d.ellipse([cx - r + o, cy - r * .7 - o, cx + r * .6 + o, cy + r * .7 - o], fill=YEL, outline=INK, width=lw)
        d.text((cx - r * .1, cy - r * .95), "Rs", font=F(r * .6), fill=INK)
    elif name == "book":
        d.polygon([(cx - r, cy - r * .7), (cx, cy - r * .5), (cx, cy + r * .8), (cx - r, cy + r * .6)], fill=(70, 130, 220), outline=INK)
        d.polygon([(cx + r, cy - r * .7), (cx, cy - r * .5), (cx, cy + r * .8), (cx + r, cy + r * .6)], fill=(90, 160, 240), outline=INK)
    elif name == "heart":
        sc = 1 + 0.08 * math.sin(t * 8)
        rr = r * sc
        d.ellipse([cx - rr, cy - rr * .8, cx, cy + rr * .2], fill=RED); d.ellipse([cx, cy - rr * .8, cx + rr, cy + rr * .2], fill=RED)
        d.polygon([(cx - rr * .97, cy - rr * .15), (cx + rr * .97, cy - rr * .15), (cx, cy + rr)], fill=RED)
    elif name == "star":
        pts = []
        for k in range(10):
            a = math.radians(-90 + k * 36 + t * 20)
            rr = r if k % 2 == 0 else r * .45
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        d.polygon(pts, fill=YEL, outline=INK)
    elif name == "warning":
        d.polygon([(cx, cy - r), (cx + r, cy + r * .8), (cx - r, cy + r * .8)], fill=YEL, outline=INK)
        d.line([cx, cy - r * .35, cx, cy + r * .25], fill=INK, width=int(lw * 1.6)); d.ellipse([cx - lw, cy + r * .42, cx + lw, cy + r * .42 + 2 * lw], fill=INK)
    elif name == "question":
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(90, 160, 240), outline=INK, width=lw)
        ctext(d, cy - r * .75, "?", F(r * 1.3), WHITE, 0, x=cx)
    elif name == "water":
        d.ellipse([cx - r * .7, cy - r * .1, cx + r * .7, cy + r], fill=(70, 160, 240), outline=INK, width=lw)
        d.polygon([(cx, cy - r), (cx - r * .62, cy + r * .2), (cx + r * .62, cy + r * .2)], fill=(70, 160, 240))
    elif name == "brain":
        for k in range(5):
            a = math.radians(180 + k * 45)
            d.ellipse([cx + r * .5 * math.cos(a) - r * .45, cy + r * .4 * math.sin(a) - r * .45, cx + r * .5 * math.cos(a) + r * .45, cy + r * .4 * math.sin(a) + r * .45], fill=(240, 150, 180), outline=INK, width=lw)
    elif name == "lock":
        d.arc([cx - r * .5, cy - r, cx + r * .5, cy], 180, 360, fill=INK, width=int(lw * 1.6))
        d.rounded_rectangle([cx - r * .75, cy - r * .5, cx + r * .75, cy + r * .8], radius=r * .15, fill=YEL, outline=INK, width=lw)
    elif name == "battery":
        d.rounded_rectangle([cx - r, cy - r * .5, cx + r * .85, cy + r * .5], radius=r * .1, outline=INK, width=lw, fill=WHITE)
        d.rectangle([cx + r * .85, cy - r * .2, cx + r, cy + r * .2], fill=INK)
        lvl = (t * 0.4) % 1
        d.rectangle([cx - r * .85, cy - r * .36, cx - r * .85 + 1.6 * r * lvl, cy + r * .36], fill=GREEN)
    else:
        icon(d, "question", cx, cy, r, t)


def ease(p):
    p = max(0.0, min(1.0, p)); return p * p * (3 - 2 * p)


def visual(img, d, v, lt, dur, t):
    ty = v.get("type", "host")
    if ty == "host":
        if v.get("badge"):
            f = F(90); tw = d.textlength(v["badge"], font=f)
            d.rounded_rectangle([W / 2 - tw / 2 - 40, 600, W / 2 + tw / 2 + 40, 720], radius=40, fill=YEL, outline=INK, width=8)
            ctext(d, 608, v["badge"], f, INK, 0)
        person(d, W / 2, 1450, 1.55, "host", v.get("shirt", "blue"), t, wave=v.get("wave", True), face=v.get("face", "smile"), say=v.get("say"))
    elif ty == "chars":
        ppl = v["people"][:4]
        n = len(ppl)
        sc = {1: 1.5, 2: 1.25, 3: 1.0, 4: 0.85}[n]
        xs = {1: [W / 2], 2: [W * .3, W * .7], 3: [W * .2, W * .5, W * .8], 4: [180, 420, 660, 900]}[n]
        for i, p in enumerate(ppl):
            if lt < 0.25 * i:
                continue
            person(d, xs[i], 1470, sc, p.get("role", "man"), p.get("shirt", "blue"), t, p.get("wave", False), p.get("face", "smile"),
                   p.get("label"), p.get("say"), lift=70 if (n == 4 and i % 2) else 0)
    elif ty == "list":
        items, icons = v["items"], v.get("icons", [])
        step = max(0.7, (dur - 0.5) / max(1, len(items)))
        y = 640
        for i, it in enumerate(items):
            if lt < 0.3 + i * step:
                break
            a = ease((lt - 0.3 - i * step) / 0.3)
            x0 = 80 + (1 - a) * 200
            d.rounded_rectangle([x0, y, x0 + 920, y + 140], radius=30, fill=WHITE, outline=INK, width=6)
            icon(d, icons[i] if i < len(icons) else "check", x0 + 80, y + 70, 46, t)
            f = fit(d, it, 54, 760)
            d.text((x0 + 150, y + 70 - f.size * 0.65), it, font=f, fill=INK)
            y += 170
    elif ty == "compare":
        for side, x0, col, ic in (("left", 60, RED, "cross"), ("right", 560, GREEN, "check")):
            blk = v[side]
            if side == "right" and lt < dur * 0.35:
                continue
            d.rounded_rectangle([x0, 600, x0 + 460, 1440], radius=36, fill=WHITE, outline=col, width=10)
            icon(d, ic, x0 + 230, 700, 60, t)
            ctext(d, 780, blk["title"], fit(d, blk["title"], 60, 400), col, 0, x=x0 + 230)
            yy = 880
            for it in blk.get("items", [])[:4]:
                f = fit(d, it, 44, 400)
                ctext(d, yy, it, f, INK, 0, x=x0 + 230); yy += 120
    elif ty == "timer":
        secs = v.get("secs", 5)
        frac_total = lt / max(dur - 0.2, 0.5)
        left = max(1, secs - int(frac_total * secs))
        cx, cy, r = W / 2, 980, 230
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(120, 25, 40), outline=YEL, width=16)
        d.arc([cx - r, cy - r, cx + r, cy + r], -90, -90 + 360 * (1 - (frac_total * secs) % 1), fill=WHITE, width=16)
        ctext(d, cy - 160, str(left), F(260), WHITE, 0)
    elif ty == "icon":
        icon(d, v.get("name", "bulb"), W / 2, 1000, 230 * (0.8 + 0.2 * ease(lt / 0.4)), t)
        if v.get("text"):
            ctext(d, 1290, v["text"], fit(d, v["text"], 80, 980), WHITE)
    elif ty == "number":
        val = v["value"] * ease(lt / max(0.6, dur * 0.6))
        s = f"{v.get('prefix', '')}{int(val):,}{v.get('suffix', '')}"
        ctext(d, 860, s, fit(d, s, 220, 1000), YEL)
    elif ty == "options":
        ans, rev = v.get("answer", -1), v.get("reveal", False)
        y = 640
        for i, it in enumerate(v["items"][:4]):
            if lt < 0.2 + i * 0.35:
                break
            ok = rev and i == ans
            d.rounded_rectangle([90, y, 990, y + 150], radius=40, fill=GREEN if ok else WHITE, outline=INK, width=6)
            f = fit(d, it, 60, 820)
            d.text((140, y + 75 - f.size * 0.65), it, font=f, fill=WHITE if ok else INK)
            if ok:
                icon(d, "check", 920, y + 75, 50, t)
            y += 185


def caption(img, d, cap):
    f = F(52)
    lines, cur = [], []
    for w_ in cap.split():
        trial = " ".join(x.replace("*", "") for x in cur + [w_])
        if d.textlength(trial, font=f) > W - 180 and cur:
            lines.append(cur); cur = [w_]
        else:
            cur.append(w_)
    lines.append(cur)
    top = 1600
    box = Image.new("RGBA", (W - 120, len(lines) * 70 + 34), (25, 20, 30, 205))
    img.paste(box, (60, top), box)
    for i, ln in enumerate(lines):
        plain = " ".join(x.replace("*", "") for x in ln)
        x = (W - d.textlength(plain, font=f)) / 2
        for w_ in ln:
            ww = w_.replace("*", "")
            d.text((x, top + 16 + i * 70), ww, font=f, fill=YEL if "*" in w_ else WHITE)
            x += d.textlength(ww + " ", font=f)


def render():
    scenes = SPEC["scenes"]
    pal = SPEC.get("palette", "mix")
    order = ["blue", "orange", "purple", "green"]
    parts, tl, t0 = [], [], 0.0
    for i, s in enumerate(scenes):
        p = f"{OUT}/vo_{i}.wav"
        dur = tts(s["hi"], p)
        sil = s.get("sil", 0) + 0.35
        g = f"{OUT}/gap_{i}.wav"
        subprocess.run(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "anullsrc=r=22050:cl=mono", "-t", str(sil), g], check=True)
        parts += [p, g]
        tl.append((t0, dur + sil, s, i)); t0 += dur + sil
    total = t0
    with open(f"{OUT}/concat.txt", "w") as fh:
        for p in parts:
            fh.write(f"file '{os.path.abspath(p)}'\n")
    subprocess.run(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{OUT}/concat.txt",
                    "-af", "loudnorm=I=-14:TP=-1.5", "-ar", "44100", f"{OUT}/voice.wav"], check=True)
    proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                             "-r", str(FPS), "-i", "-", "-i", f"{OUT}/voice.wav", "-c:v", "libx264", "-preset", "veryfast",
                             "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest",
                             "-movflags", "+faststart", f"{OUT}/clip.mp4"], stdin=subprocess.PIPE)
    for n in range(int(total * FPS)):
        t = n / FPS
        s0, dur, sc, idx = [x for x in tl if x[0] <= t][-1]
        lt = t - s0
        p = pal if pal != "mix" else order[idx % len(order)]
        img = sunburst(t, p)
        d = ImageDraw.Draw(img)
        visual(img, d, sc.get("v", {"type": "host"}), lt, dur, t)
        if sc.get("head"):
            a = ease(lt / 0.35)
            ctext(d, 230, sc["head"], fit(d, sc["head"], int(110 * (0.8 + 0.2 * a)), 980), YEL)
        if sc.get("sub"):
            ctext(d, 380, sc["sub"], fit(d, sc["sub"], 76, 980), WHITE)
        caption(img, d, sc["cap"])
        d.rectangle([0, H - 14, int(W * t / total), H], fill=YEL)
        proc.stdin.write(img.tobytes())
        if n == int(1.5 * FPS):
            img.save(f"{OUT}/thumb.png")
    proc.stdin.close(); proc.wait()
    print("seconds", round(total, 1))


if __name__ == "__main__":
    render()
