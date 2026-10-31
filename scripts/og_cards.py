"""Per-page Open Graph cards (1200x630 PNG) drawn with Pillow. Same tokens as site.css / scripts/og.html.
firm_card(f, out), compare_card(a, b, out), text_card(kicker, title, stats, out). Fonts: src/og-fonts (TTF from src/fonts woff2)."""
import os
from PIL import Image, ImageDraw, ImageFont
_R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1200, 630
INK, MUTE, RULE, BAND, ACC, BG = (11, 23, 48), (90, 102, 128), (207, 212, 222), (245, 246, 248), (52, 36, 248), (255, 255, 255)
RED, REDBG, GREEN, GREY = (176, 32, 32), (253, 236, 236), (16, 122, 70), (120, 128, 140)
_FC = {}
def font(size, wght=500, mono=False):
    k = (size, wght, mono)
    if k not in _FC:
        f = ImageFont.truetype(os.path.join(_R, "src", "og-fonts", "geist-mono.ttf" if mono else "instrument-sans.ttf"), size)
        try: f.set_variation_by_axes([wght])
        except Exception: pass
        _FC[k] = f
    return _FC[k]
def tw(d, s, f): return d.textlength(s, font=f)
def fit(d, s, size, maxw, wght=600, minsize=28):
    while size > minsize and tw(d, s, font(size, wght)) > maxw: size -= 2
    f = font(size, wght)
    if tw(d, s, f) > maxw:
        while len(s) > 3 and tw(d, s + "…", f) > maxw: s = s[:-1]
        s = s.rstrip() + "…"
    return s, f
_LOGO = None
def brand_logo(h=44):
    global _LOGO
    if _LOGO is None:
        im = Image.open(os.path.join(_R, "brand", "logo-crop.png")).convert("RGBA")
        _LOGO = im.resize((int(im.width * h / im.height), h), Image.LANCZOS)
    return _LOGO
def firm_logo(slug, size):
    for n in (f"{slug}@2x.webp", f"{slug}.webp", f"{slug}.png"):
        p = os.path.join(_R, "src", "firms", n)
        if os.path.exists(p):
            try:
                im = Image.open(p).convert("RGBA"); im.thumbnail((size, size), Image.LANCZOS); return im
            except Exception: pass
    return None
def logo_box(img, d, slug, name, x, y, size):
    d.rounded_rectangle((x, y, x + size, y + size), radius=14, fill=BG, outline=RULE, width=2)
    lg = firm_logo(slug, size - 20)
    if lg: img.paste(lg, (x + (size - lg.width) // 2, y + (size - lg.height) // 2), lg)
    else:
        ini = "".join(w[0] for w in name.split()[:2]).upper(); f = font(int(size * .38), 600)
        d.text((x + size / 2, y + size / 2), ini, font=f, fill=INK, anchor="mm")
def star(d, cx, cy, r, fill, frac=1.0, bg=RULE):
    import math
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5; rr = r if i % 2 == 0 else r * .45
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=bg)
    if frac >= 1: d.polygon(pts, fill=fill)
    elif frac > 0:
        m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).polygon(pts, fill=255)
        clip = Image.new("L", (W, H), 0); ImageDraw.Draw(clip).rectangle((cx - r, cy - r, cx - r + 2 * r * frac, cy + r), fill=255)
        from PIL import ImageChops
        d._image.paste(Image.new("RGB", (W, H), fill), (0, 0), ImageChops.multiply(m, clip))
def stars(d, x, y, score10, r=17, gap=8, color=ACC):
    v = max(0.0, min(5.0, score10 / 2))
    for i in range(5):
        star(d, x + r + i * (2 * r + gap), y + r, r, color, max(0.0, min(1.0, v - i)))
def mast(img, d, right):
    lg = brand_logo(44); img.paste(lg, (64, 46), lg)
    if right: d.text((W - 64, 68), right, font=font(19, 500), fill=MUTE, anchor="rm")
    d.line((64, 116, W - 64, 116), fill=RULE, width=1)
def band(d, cols, top=470, accent_idx=None, colors=None):
    d.rectangle((0, top, W, H), fill=BAND); d.line((0, top, W, top), fill=RULE, width=1)
    n = len(cols); cw = (W - 128) / n
    for i, (val, lab) in enumerate(cols):
        x = 64 + i * cw + (24 if i else 0)
        if i: d.line((64 + i * cw, top, 64 + i * cw, H), fill=(227, 230, 236), width=1)
        col = (colors or {}).get(i, INK)
        v, f = fit(d, val, 40, cw - 36, 600, 24)
        d.text((x, top + 34), v, font=f, fill=col)
        d.text((x, top + 92), lab, font=font(19, 500), fill=MUTE)
def save(img, out):
    os.makedirs(os.path.dirname(out), exist_ok=True); img.save(out, "PNG")

def firm_card(f, out, fee_txt, verified_txt, rank_txt):
    img = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(img)
    caution = f.get("status") == "caution"
    mast(img, d, verified_txt)
    if caution: d.rectangle((0, 0, W, 8), fill=RED)
    logo_box(img, d, f["slug"], f["name"], 64, 162, 112)
    nm, nf = fit(d, f["name"], 66, 570, 600, 34)
    d.text((200, 168), nm, font=nf, fill=INK)
    sub = f.get("_sub") or ""
    d.text((202, 252), fit(d, sub, 22, 590, 500, 16)[0], font=font(22, 500), fill=MUTE)
    s = f["_score"]; sx = 800
    sf = font(150, 600); st = f"{s:.1f}"
    d.text((sx, 150), st, font=sf, fill=RED if caution else INK)
    d.text((sx + tw(d, st, sf) + 10, 260), "/10", font=font(34, 500), fill=MUTE)
    stars(d, sx + 4, 322, s, 17, 8, RED if caution else ACC)
    d.text((sx + 4, 372), rank_txt, font=font(20, 500), fill=MUTE)
    if caution: d.text((sx + 4, 404), "Capped by the caution rule", font=font(20, 600), fill=RED)
    tp = f.get("trustpilot") or {}
    tpv = f"{float(tp['score']):.1f} / 5" if tp.get("score") else "No rating"
    split = f.get("profit_split") or "Not published"
    band(d, [(fee_txt, "Fees from"), (split, "Profit split"), (tpv, "Trustpilot"), ("Caution" if caution else "Active", "Status")],
         colors={3: RED if caution else GREEN})
    save(img, out)

def compare_card(a, b, out, fee_a, fee_b, date_txt):
    img = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(img)
    mast(img, d, "Side by side · " + date_txt)
    t, tf = fit(d, f"{a['name']} vs {b['name']}", 58, W - 128, 600, 30)
    d.text((64, 140), t, font=tf, fill=INK)
    win = a if a["_score"] > b["_score"] else b if b["_score"] > a["_score"] else None
    for i, f in enumerate((a, b)):
        x = 64 + i * 552; y = 236
        if f is win: d.rectangle((x - 2, y - 8, x + 520, y - 4), fill=ACC)
        logo_box(img, d, f["slug"], f["name"], x, y + 8, 84)
        nm, nf = fit(d, f["name"], 34, 400, 600, 20)
        d.text((x + 104, y + 12), nm, font=nf, fill=INK)
        c = RED if f.get("status") == "caution" else INK
        sc = f"{f['_score']:.1f}"; scf = font(64, 600)
        d.text((x + 104, y + 52), sc, font=scf, fill=c)
        d.text((x + 104 + tw(d, sc, scf) + 8, y + 88), "/10 PA Score" + (" · caution" if f.get("status") == "caution" else ""), font=font(19, 500), fill=RED if f.get("status") == "caution" else MUTE)
        stars(d, x + 106, y + 140, f["_score"], 13, 6, RED if f.get("status") == "caution" else ACC)
    d.line((W / 2, 236, W / 2, 440), fill=RULE, width=1)
    band(d, [(fee_a, a["name"] + " fees from"), (a.get("profit_split") or "n/a", a["name"] + " split"),
             (fee_b, b["name"] + " fees from"), (b.get("profit_split") or "n/a", b["name"] + " split")])
    save(img, out)

def text_card(kicker, title, cols, out, right="", accent_line=None, tone=None):
    img = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(img)
    mast(img, d, right)
    if tone == "red": d.rectangle((0, 0, W, 8), fill=RED)
    d.text((64, 150), kicker, font=font(24, 600), fill=RED if tone == "red" else ACC)
    words = title.split(); lines, cur = [], ""
    f = font(62, 600)
    for w_ in words:
        tst = (cur + " " + w_).strip()
        if tw(d, tst, f) > W - 128 and cur: lines.append(cur); cur = w_
        else: cur = tst
    lines.append(cur)
    if len(lines) > 3:
        f = font(48, 600); lines, cur = [], ""
        for w_ in words:
            tst = (cur + " " + w_).strip()
            if tw(d, tst, f) > W - 128 and cur: lines.append(cur); cur = w_
            else: cur = tst
        lines.append(cur); lines = lines[:4]
    y = 196
    for ln in lines: d.text((64, y), ln, font=f, fill=INK); y += int(f.size * 1.12)
    if accent_line: d.text((64, y + 8), accent_line, font=font(24, 500), fill=MUTE)
    if cols: band(d, cols, colors={i: (RED if tone == "red" and i == 0 else INK) for i in range(len(cols))})
    save(img, out)
