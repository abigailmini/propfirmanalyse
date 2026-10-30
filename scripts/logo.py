#!/usr/bin/env python3
"""brand/propanalyse-logo-source.png -> src/ logo + favicon assets. Run once when the logo changes.
logo.png/.webp (@2x, 64px tall), logo@3x.webp, logo-white.* (white wordmark for dark surfaces),
favicon-32.png, favicon.ico (16/32/48), apple-touch-icon.png (180, opaque), brand/logo-crop.png (full-res, for og)."""
import os, subprocess
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC, OUT = os.path.join(ROOT, "brand", "propanalyse-logo-source.png"), os.path.join(ROOT, "src")
im = Image.open(SRC).convert("RGBA")
a = im.getchannel("A")
# clear faint stray alpha noise, then crop to the real artwork
a = a.point(lambda v: 0 if v < 12 else v); im.putalpha(a)
bb = a.point(lambda v: 255 if v > 20 else 0).getbbox()
art = im.crop(bb)
MARK_W = 604 - bb[0]           # first empty column run after the "pa" mark (source px)
art.save(os.path.join(ROOT, "brand", "logo-crop.png"), optimize=True)

DARK_MARK = (143, 136, 255)   # #8f88ff: brand blue lifted for dark surfaces (>6:1 on #121b2e)
def white_wordmark(img):
    """Dark-scheme logo: white wordmark + lighter blue mark (the #3424f8 mark is ~2:1 on navy)."""
    img = img.copy(); px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, al = px[x, y]
            if al: px[x, y] = ((255, 255, 255) if x >= MARK_W else DARK_MARK) + (al,)
    return img
art_w = white_wordmark(art)

def rs(img, h):
    w = round(img.width * h / img.height)
    return img.convert("RGBa").resize((w, h), Image.LANCZOS).convert("RGBA")

def webp(png, out):
    subprocess.run(["cwebp", "-quiet", "-q", "92", "-alpha_q", "100", "-exact", png, "-o", out], check=True)

for name, src in (("logo", art), ("logo-white", art_w)):
    for h, suf in ((64, ""), (96, "@3x")):
        p = os.path.join(OUT, f"{name}{suf}.png")
        rs(src, h).save(p, optimize=True)
        webp(p, os.path.join(OUT, f"{name}{suf}.webp"))
        if suf: os.remove(p)       # 3x only ships as webp

# favicon: the "pa" mark only, centred on a square
mark = art.crop((0, 0, MARK_W, art.height)); mark = mark.crop(mark.getbbox())
def square(img, size, pad, bg=(0, 0, 0, 0)):
    inner = size - 2 * pad
    s = inner / max(img.size)
    m = img.convert("RGBa").resize((max(1, round(img.width * s)), max(1, round(img.height * s))), Image.LANCZOS).convert("RGBA")
    c = Image.new("RGBA", (size, size), bg)
    c.alpha_composite(m, ((size - m.width) // 2, (size - m.height) // 2))
    return c
square(mark, 32, 1).save(os.path.join(OUT, "favicon-32.png"), optimize=True)
square(mark, 256, 4).save(os.path.join(OUT, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])
square(mark, 180, 22, (255, 255, 255, 255)).convert("RGB").save(os.path.join(OUT, "apple-touch-icon.png"), optimize=True)
print("art", art.size, "mark", mark.size, "logo @2x", rs(art, 64).size)
