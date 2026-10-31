#!/usr/bin/env python3
"""PropAnalyse static site generator. Regenerates every page from data/firms.json.
Usage: python3 scripts/build.py  [env BASE_PATH= SITE_URL=https://propanalyse.com]
"""
import json, os, re, math, html, shutil, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "site")
BASE = os.environ.get("BASE_PATH", "").rstrip("/")
SITE_URL = os.environ.get("SITE_URL", "https://propanalyse.com").rstrip("/")
ABS = SITE_URL + BASE
T = json.load(open(os.path.join(ROOT, "i18n", "en.json")))
DATA = json.load(open(os.path.join(ROOT, "data", "firms.json")))
FIRMS = DATA["firms"]
TODAY = DATA.get("generated", datetime.date.today().isoformat())
YEAR_NOW = 2026
def e(s):
    # escape for HTML; source notes sometimes carry em/en dashes, shown as plain punctuation
    return html.escape(str(s), quote=True).replace(" \u2014 ", ", ").replace("\u2014", "-").replace(" \u2013 ", " - ").replace("\u2013", "-")

# ---------------- normalisation helpers ----------------
def num(x):
    if x is None: return None
    if isinstance(x, (int, float)): return float(x)
    m = re.search(r"-?\d+(?:\.\d+)?", str(x).replace(",", ""))
    return float(m.group()) if m else None

def max_pct(x):
    if x is None: return None
    if isinstance(x, (int, float)): return float(x)
    vals = [float(v) for v in re.findall(r"(\d+(?:\.\d+)?)\s*%", str(x))]
    return max(vals) if vals else num(x)

def first_pct(x):
    if x is None: return None
    if isinstance(x, (int, float)): return float(x)
    vals = re.findall(r"(\d+(?:\.\d+)?)\s*%", str(x))
    return float(vals[0]) if vals else None

def as_list(x):
    if x is None: return []
    return x if isinstance(x, list) else [x]

def tri(x):
    """True / False / 'restricted' / None"""
    if x is None: return None
    if isinstance(x, bool): return x
    s = str(x).lower()
    if s in ("true", "yes", "allowed"): return True
    if s in ("false", "no", "not allowed", "prohibited"): return False
    return "restricted"

def payout_bucket(f):
    s = (str(f.get("payout_frequency") or "")).lower().split(";")[0]  # headline (first-listed) plan only
    if not s: return None
    if any(k in s for k in ("daily", "on demand", "on-demand", "24h", "anytime", "any time", "instant")): return "daily"
    if "bi-weekly" in s or "biweekly" in s or "14" in s or "two weeks" in s or "2 weeks" in s: return "biweekly"
    if "week" in s or "7 day" in s or "5 day" in s or "8 day" in s: return "weekly"
    if "month" in s or "30" in s or "21" in s: return "monthly"
    return "other"
BUCKET_LABEL = {"daily": "Daily / on demand", "weekly": "Weekly", "biweekly": "Bi-weekly", "monthly": "Monthly", "other": "Varies"}

def sizes(f):
    s = [num(x) for x in as_list(f.get("account_sizes")) if num(x)]
    for p in as_list(f.get("programs")):
        for sf in as_list(p.get("sizes_fees")):
            if num(sf.get("size")): s.append(num(sf.get("size")))
    return sorted(set(s))

def fee_from(f):
    v = num(f.get("fee_from"))
    fees = [num(sf.get("fee")) for p in as_list(f.get("programs")) for sf in as_list(p.get("sizes_fees")) if num(sf.get("fee"))]
    if v is None and fees: v = min(fees)
    return v

def cost_per_k(f):
    r = [num(sf.get("fee")) / num(sf.get("size")) * 1000 for p in as_list(f.get("programs")) for sf in as_list(p.get("sizes_fees"))
         if num(sf.get("fee")) and num(sf.get("size"))]
    return min(r) if r else None

CUR = {"EUR": "€", "USD": "$", "GBP": "£"}
def money(v, cur="USD"):
    if v is None: return "not published"
    sym = CUR.get(cur or "USD", "$")
    return money_usd(v).replace("$", sym, 1)
def money_usd(v):
    if v >= 1_000_000: return "$" + (f"{v/1_000_000:.1f}".rstrip("0").rstrip(".")) + "M"
    if v >= 1000: return "$" + (f"{v/1000:.1f}".rstrip("0").rstrip(".")) + "K"
    return "$" + (f"{v:.2f}".rstrip("0").rstrip("."))

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
MISSING = 0.4

def score(f):
    comp, flags = {}, []
    tp = f.get("trustpilot") or {}
    if tp.get("score") and tp.get("count"):
        conf = 0.6 + 0.4 * clamp(math.log10(max(1, num(tp["count"]))) / 4)
        comp["trust"] = clamp((num(tp["score"]) - 3) / 2) * conf
    else: comp["trust"] = MISSING; flags.append("trust")
    c = cost_per_k(f)
    comp["cost"] = 1 - clamp((c - 3) / 12) if c is not None else MISSING
    if c is None: flags.append("cost")
    rs = []
    dl = first_pct(f.get("max_daily_loss")); md = first_pct(f.get("max_drawdown"))
    if dl is not None: rs.append(clamp(dl / 5))
    if md is not None: rs.append(clamp(md / 10))
    dt = (str(f.get("drawdown_type") or "")).lower()
    if dt: rs.append(0.4 if "trail" in dt else 1.0)
    for k in ("news_trading", "weekend_holding"):
        v = tri(f.get(k))
        if v is not None: rs.append(1.0 if v is True else (0.5 if v == "restricted" else 0.0))
    cr = f.get("consistency_rule")
    if cr is not None:
        s = str(cr).lower()
        rs.append(1.0 if (cr is False or s in ("none", "no", "false", "no consistency rule")) else 0.5)
    comp["rules"] = sum(rs) / len(rs) if rs else MISSING
    if not rs: flags.append("rules")
    ps = []
    sp = max_pct(f.get("profit_split"))
    if sp is not None: ps.append(clamp((sp - 60) / 40))
    fd = num(f.get("first_payout_days"))
    if fd is not None: ps.append(1 - clamp((fd - 1) / 30))
    b = payout_bucket(f)
    if b: ps.append({"daily": 1, "weekly": .8, "biweekly": .6, "monthly": .3, "other": .5}[b])
    comp["payout"] = sum(ps) / len(ps) if ps else MISSING
    if not ps: flags.append("payout")
    fy = num(f.get("founded"))
    comp["history"] = clamp((YEAR_NOW - fy) / 8) if fy else MISSING
    if not fy: flags.append("history")
    W = {"trust": .30, "cost": .20, "rules": .20, "payout": .20, "history": .10}
    total = sum(comp[k] * W[k] for k in W) * 10
    return round(total, 1), {k: round(v * 10, 1) for k, v in comp.items()}, flags

FIELDS_FOR_COMPLETENESS = ["assets", "challenge_types", "account_sizes", "fee_from", "profit_target", "max_daily_loss", "max_drawdown",
    "drawdown_type", "profit_split", "leverage", "platforms", "payout_frequency", "first_payout_days", "min_trading_days",
    "consistency_rule", "news_trading", "weekend_holding", "countries_restricted", "founded", "hq", "trustpilot"]
def completeness(f):
    have = 0
    for k in FIELDS_FOR_COMPLETENESS:
        v = f.get(k)
        if k == "fee_from": v = fee_from(f)
        if k == "account_sizes": v = sizes(f) or None
        if v not in (None, [], "", {}): have += 1
    return round(100 * have / len(FIELDS_FOR_COMPLETENESS))

for f in FIRMS:
    f["_score"], f["_comp"], f["_flags"] = score(f)
    f["_sizes"] = sizes(f); f["_fee"] = fee_from(f); f["_bucket"] = payout_bucket(f)
    f["_split"] = max_pct(f.get("profit_split")); f["_complete"] = completeness(f)
    f["_assets"] = [a.lower() for a in as_list(f.get("assets"))]
    f["_types"] = [t.lower() for t in as_list(f.get("challenge_types"))]
    f["_platforms"] = as_list(f.get("platforms"))
BY = {f["slug"]: f for f in FIRMS}
RANKED = sorted(FIRMS, key=lambda f: -f["_score"])
for i, f in enumerate(RANKED): f["_rank"] = i + 1

# ---------------- presentation helpers ----------------
ICONS = {
    "menu": '<path d="M224,128a8,8,0,0,1-8,8H40a8,8,0,0,1,0-16H216A8,8,0,0,1,224,128ZM40,72H216a8,8,0,0,0,0-16H40a8,8,0,0,0,0,16ZM216,184H40a8,8,0,0,0,0,16H216a8,8,0,0,0,0-16Z"/>',
    "x": '<path d="M205.66,194.34a8,8,0,0,1-11.32,11.32L128,139.31,61.66,205.66a8,8,0,0,1-11.32-11.32L116.69,128,50.34,61.66A8,8,0,0,1,61.66,50.34L128,116.69l66.34-66.35a8,8,0,0,1,11.32,11.32L139.31,128Z"/>',
    "ext": '<path d="M200,64V168a8,8,0,0,1-16,0V83.31L69.66,197.66a8,8,0,0,1-11.32-11.32L172.69,72H88a8,8,0,0,1,0-16H192A8,8,0,0,1,200,64Z"/>',
    "copy": '<path d="M216,32H88a8,8,0,0,0-8,8V80H40a8,8,0,0,0-8,8V216a8,8,0,0,0,8,8H168a8,8,0,0,0,8-8V176h40a8,8,0,0,0,8-8V40A8,8,0,0,0,216,32ZM160,208H48V96H160Zm48-48H176V88a8,8,0,0,0-8-8H96V48H208Z"/>',
    "search": '<path d="M229.66,218.34l-50.07-50.06a88.11,88.11,0,1,0-11.31,11.31l50.06,50.07a8,8,0,0,0,11.32-11.32ZM40,112a72,72,0,1,1,72,72A72.08,72.08,0,0,1,40,112Z"/>',
    "sliders": '<path d="M40,88H73a32,32,0,0,0,62,0h81a8,8,0,0,0,0-16H135a32,32,0,0,0-62,0H40a8,8,0,0,0,0,16Zm64-24A16,16,0,1,1,88,80,16,16,0,0,1,104,64ZM216,168H199a32,32,0,0,0-62,0H40a8,8,0,0,0,0,16h97a32,32,0,0,0,62,0h17a8,8,0,0,0,0-16Zm-48,24a16,16,0,1,1,16-16A16,16,0,0,1,168,192Z"/>',
    "arrow": '<path d="M221.66,133.66l-72,72a8,8,0,0,1-11.32-11.32L196.69,136H40a8,8,0,0,1,0-16H196.69L138.34,61.66a8,8,0,0,1,11.32-11.32l72,72A8,8,0,0,1,221.66,133.66Z"/>',
    "star": '<path d="M234.29,114.85l-45,38.83L203,211.75a16.4,16.4,0,0,1-24.5,17.82L128,198.49,77.47,229.57A16.4,16.4,0,0,1,53,211.75l13.76-58.07-45-38.83A16.46,16.46,0,0,1,31.08,86l59-4.76,22.76-55.08a16.36,16.36,0,0,1,30.27,0l22.75,55.08,59,4.76a16.46,16.46,0,0,1,9.37,28.86Z"/>',
}
def ic(n, cls=""):
    """Phosphor Icons (regular/fill, MIT) paths, inlined."""
    return f'<svg class="i{(" " + cls) if cls else ""}" viewBox="0 0 256 256" fill="currentColor" aria-hidden="true" focusable="false">{ICONS[n]}</svg>'

# Logo: brand/propanalyse-logo-source.png -> src/logo*.{png,webp} via scripts/logo.py. White-wordmark variant on dark scheme.
def brand():
    a = lambda n: url("/assets/" + n)
    return (f'<a class="brand" href="{url("/")}" aria-label="PropAnalyse home"><picture>'
            f'<source media="(prefers-color-scheme:dark)" type="image/webp" srcset="{a("logo-white.webp")}?v={ASSET_V} 2x, {a("logo-white@3x.webp")}?v={ASSET_V} 3x">'
            f'<source media="(prefers-color-scheme:dark)" srcset="{a("logo-white.png")}?v={ASSET_V}">'
            f'<source type="image/webp" srcset="{a("logo.webp")}?v={ASSET_V} 2x, {a("logo@3x.webp")}?v={ASSET_V} 3x">'
            f'<img class="logo" src="{a("logo.png")}?v={ASSET_V}" width="192" height="32" alt="PropAnalyse" decoding="async"></picture></a>')
def icons():
    return (f'<link rel="icon" href="{url("/favicon.ico")}" sizes="48x48"><link rel="icon" href="{url("/assets/favicon-32.png")}?v={ASSET_V}" type="image/png" sizes="32x32">'
            f'<link rel="apple-touch-icon" href="{url("/assets/apple-touch-icon.png")}?v={ASSET_V}">')

NA = '<span class="na" title="Not published by the firm"><span class="sr">Not published</span></span>'
NIL = '<span class="nil">' + T["unknown"] + '</span>'
def mh(v, cur="USD"):
    return NA if v is None else f'<span class="n">{money(v, cur)}</span>'

def nice_date(d):
    try: return datetime.date.fromisoformat(str(d)).strftime("%-d %b %Y")
    except Exception: return str(d)

def short_hq(hq):
    if not hq: return ""
    s = re.split(r"[(;]", hq)[0].strip().rstrip(",")
    return s

def show(v, suffix=""):
    if v in (None, "", [], {}): return NIL
    if v is True: return "Allowed"
    if v is False: return "Not allowed"
    if isinstance(v, list): return e(", ".join(str(x) for x in v))
    return e(str(v)) + suffix

def tri_label(v):
    v = tri(v)
    return {True: "Allowed", False: "Not allowed", "restricted": "Restricted", None: NIL}[v]

# ---------------- page shell ----------------
def url(p): return BASE + p
NAV = [("/firms/", "nav_firms"), ("/compare/", "nav_compare"), ("/discounts/", "nav_discounts"), ("/best/", "nav_best"), ("/methodology/", "nav_method"), ("/about/", "nav_about")]
def page(path, title, desc, body, jsonld=None, og_type="website", extra_head="", lang="en"):
    canon = ABS + path
    ld = "".join('<script type="application/ld+json">' + json.dumps(j, ensure_ascii=False) + "</script>" for j in (jsonld or []))
    zh = lang == "zh"; ZA = globals().get("ZH_ALT", {})
    UI = globals().get("ZH_UI") if zh else {"skip": "Skip to content", "menu": "Menu", "explore": "Explore", "disc": "Disclosure", "verified": "Data verified", "open": "Open data (JSON)"}
    TT = globals().get("T_ZH", T) if zh else T
    hl, loc, langlink = ("zh-Hans", "zh_CN", "") if zh else ("en", "en_US", "")
    if zh:
        en_p = next((k for k, v in ZA.items() if v == path), "/")
        alts = f'<link rel="alternate" hreflang="en" href="{ABS + en_p}"><link rel="alternate" hreflang="zh-Hans" href="{canon}"><link rel="alternate" hreflang="x-default" href="{ABS + en_p}">'
        navh = "".join(f'<a href="{url(h)}"{" aria-current=page" if path == h or (h != "/zh/" and path.startswith(h)) else ""}>{e(t)}</a>' for h, t in ZH_NAV) + f'<a href="{url(en_p)}" lang="en" hreflang="en">English</a>'
        footnav = "".join(f'<li><a href="{url(h)}">{e(t)}</a></li>' for h, t in ZH_NAV + ZH_FOOT) + f'<li><a href="{url(en_p)}" lang="en">English version</a></li>'
    else:
        zp = ZA.get(path)
        alts = f'<link rel="alternate" hreflang="en" href="{canon}">' + (f'<link rel="alternate" hreflang="zh-Hans" href="{ABS + zp}">' if zp else "") + f'<link rel="alternate" hreflang="x-default" href="{canon}">'
        navh = "".join((f'<a href="{url(ZA.get(path, "/zh/"))}" lang="zh-Hans" hreflang="zh-Hans">{e(T[k])}</a>' if h == "/zh/" else
                        f'<a href="{url(h)}"{" aria-current=page" if path.startswith(h) else ""}>{e(T[k])}</a>') for h, k in NAV)
        footnav = "".join(f'<li><a href="{url(h)}">{e(T[k])}</a></li>' for h, k in NAV) + "".join(f'<li><a href="{url(h)}">{e(t)}</a></li>' for h, t in globals().get("FOOT_EXTRA", [("/updates/", "Verification log")]))
        if zp: langlink = f'<a href="{url(zp)}" lang="zh-Hans" hreflang="zh-Hans">中文版</a>'
    vdate = zdate(TODAY) if zh else nice_date(TODAY)
    doc = f"""<!doctype html><html lang="{hl}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{canon}">
<meta property="og:type" content="{og_type}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canon}"><meta property="og:image" content="{ABS}/assets/og.png"><meta property="og:site_name" content="PropAnalyse"><meta property="og:locale" content="{loc}">
<meta name="twitter:card" content="summary_large_image"><meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)"><meta name="theme-color" content="#18233a" media="(prefers-color-scheme: dark)"><meta name="color-scheme" content="light dark">
<link rel="preload" href="{url('/assets/fonts/instrument-sans.woff2')}" as="font" type="font/woff2" crossorigin>
{icons()}<link rel="stylesheet" href="{url('/assets/site.css')}?v={ASSET_V}">
{alts}{extra_head}{ld}</head>
<body><a class="skip" href="#main">{e(UI["skip"])}</a>
<header class="top"><div class="wrap bar">{brand()}
<button class="menu" id="menu" type="button" aria-expanded="false" aria-controls="nav"><span class="sr">{e(UI["menu"])}</span>{ic("menu", "i-open")}{ic("x", "i-close")}</button><nav class="nav" id="nav" aria-label="Main">{navh}</nav></div></header>
<main id="main">{body}</main>
<footer class="foot"><div class="wrap fgrid"><div class="fbrand">{brand()}<p>{e(TT['tagline'])}</p></div>
<nav aria-label="Footer"><h2>{e(UI["explore"])}</h2><ul>{footnav}</ul></nav>
<div><h2>{e(UI["disc"])}</h2><p>{e(TT['ownership'])}</p></div></div>
<div class="wrap fine"><p>{e(TT['disclaimer'])}</p><p class="fmeta"><span>&copy; {YEAR_NOW} PropAnalyse</span><span>{e(UI["verified"])} <time datetime="{e(TODAY)}">{vdate}</time></span><a href="{url('/llms.txt')}">llms.txt</a><a href="{url('/data/firms.json')}">{e(UI["open"])}</a>{langlink}</p></div></footer>
<script src="{url('/assets/site.js')}?v={ASSET_V}" defer></script></body></html>"""
    dest = os.path.join(OUT, path.lstrip("/"), "index.html") if path.endswith("/") else os.path.join(OUT, path.lstrip("/"))
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    open(dest, "w").write(doc)
    PAGES.append(path)
PAGES = []

def crumbs(items):
    lis = [{"@type": "ListItem", "position": i + 1, "name": n, "item": ABS + p} for i, (n, p) in enumerate(items)]
    parts = [f'<a href="{url(p)}">{e(n)}</a>' for n, p in items[:-1]] + [f'<span aria-current="page">{e(items[-1][0])}</span>']
    html_ = '<nav class="crumbs" aria-label="Breadcrumb">' + '<span class="sep" aria-hidden="true">/</span>'.join(parts) + "</nav>"
    return html_, {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": lis}

# ---------------- components ----------------
ASSET_LABEL = {"crypto": "Crypto", "forex": "Forex", "indices": "Indices", "commodities": "Commodities", "stocks": "Stocks", "futures": "Futures", "metals": "Metals", "energies": "Energies"}
COMP_LABEL = {"trust": ("Trust", 30), "cost": ("Cost", 20), "rules": ("Rules", 20), "payout": ("Payout", 20), "history": ("Track record", 10)}

def ticks(v, d=0, cls=""):
    """Trackless 10-tick bar: ticks are drawn only up to the value (0-10)."""
    return f'<i class="ticks{(" " + cls) if cls else ""}" style="--s:{max(0, min(10, v)) / 10:.3f};--d:{d}" aria-hidden="true"></i>'

def score_html(f, d=None):
    s = f["_score"]
    return (f'<span class="sc" title="PA Score {s:.1f} of 10. Data completeness {f["_complete"]}%.">'
            f'<b class="n">{s:.1f}</b><span class="sr"> out of 10</span>{ticks(s, f["_rank"] if d is None else d)}</span>')
badge_score = score_html

def code_html(f, value=True):
    dc = f.get("discount_code")
    if not dc or not dc.get("code"): return NA
    v = dc.get("value") or ""
    btn = (f'<button type="button" class="code" data-copy="{e(dc["code"])}" aria-label="Copy code {e(dc["code"])}"{(" title=" + chr(34) + e(v) + chr(34)) if v else ""}>'
           f'<span>{e(dc["code"])}</span>{ic("copy")}</button>')
    return btn + (f'<small class="cv">{e(v)}</small>' if value and v else "")

def tp_html(f):
    tp = f.get("trustpilot") or {}
    if not tp.get("score"):
        if tp.get("count"):
            return (f'<span class="tp off" title="Trustpilot shows no rating on this profile (for example, suspended for a guideline breach).">'
                    f'No rating<small class="n">{int(num(tp["count"])):,}</small></span>')
        return NA
    return (f'<span class="tp">{ic("star")}<b class="n">{num(tp["score"]):.1f}</b>'
            f'<small class="n" title="Trustpilot reviews">{int(num(tp.get("count") or 0)):,}</small></span>')

def dd_html(f):
    a = f.get("max_daily_loss"); b = f.get("max_drawdown")
    if not a and not b: return NA
    t = f.get("drawdown_type")
    return (f'<span class="n">{e(a) if a else NA} / {e(b) if b else NA}</span>' + (f'<small title="{e(t)}">{e(t)}</small>' if t else ""))

def visit(f, label=None, cls="visit"):
    return (f'<a class="{cls}" href="{e(f.get("affiliate_url") or "#")}" rel="sponsored nofollow noopener" target="_blank" data-firm="{e(f["slug"])}">'
            f'{e(label or T["visit"])}{ic("ext")}<span class="sr"> (opens {e(f["name"])} in a new tab)</span></a>')

def row(f, rk=None):
    G = globals()
    attrs = {
        "cat": f.get("category") or "", "also": " ".join(as_list(f.get("also_offers"))), "pk": " ".join(f.get("_pk", [])),
        "mk": " ".join(f.get("_mk", [])), "pm": " ".join(f.get("_pm", [])),
        "assets": " ".join(f["_assets"]), "types": " ".join(f["_types"]), "platforms": "|".join(p.lower() for p in f["_platforms"]),
        "fee": f["_fee"] if f["_fee"] is not None else "", "maxsize": max(f["_sizes"]) if f["_sizes"] else "",
        "split": f["_split"] if f["_split"] is not None else "", "score": f["_score"], "name": f["name"].lower(),
        "news": str(tri(f.get("news_trading"))).lower(), "weekend": str(tri(f.get("weekend_holding"))).lower(),
        "payout": f["_bucket"] or "", "restricted": "|".join(c.lower() for c in as_list(f.get("countries_restricted"))),
        "tp": num((f.get("trustpilot") or {}).get("score")) or "", "founded": num(f.get("founded")) or "",
    }
    da = " ".join(f'data-{k}="{e(v)}"' for k, v in attrs.items())
    mk = [ASSET_LABEL.get(a, a.title()) for a in f["_assets"]]
    mkts = e(", ".join(mk)) if mk else NA
    types = e(", ".join(as_list(f.get("challenge_types")))) or NA
    pl = f["_platforms"]
    plats = (e(", ".join(pl[:3])) + (f' <span class="plus n">+{len(pl) - 3}</span>' if len(pl) > 3 else "")) if pl else NA
    hq = f.get("hq") or ""
    est = f"est. {int(num(f['founded']))}" if num(f.get("founded")) else ""
    sub = ", ".join(x for x in (G.get("CAT_NAME", {}).get(f.get("category"), ""), short_hq(hq), est) if x)
    split = f'<span class="n">{e(f["profit_split"])}</span>' if f.get("profit_split") else NA
    return f"""<tr {da}><td class="c-rk n">{(rk or f['_rank']):02d}</td><td class="c-firm"><a href="{url('/firms/' + f['slug'] + '/')}"><b>{e(f['name'])}</b>{('<small title="' + e(hq) + '">' + e(sub) + '</small>') if sub else ''}</a></td>
<td class="c-sc" data-label="{T['col_score']}">{score_html(f)}</td><td class="c-tp" data-label="{T['col_rating']}">{tp_html(f)}</td>
<td class="c-fee num" data-label="{T['col_fee']}" data-m="{T['col_fee']}">{mh(f['_fee'], f.get('fee_currency'))}</td><td class="c-max num" data-label="{T['col_maxsize']}">{mh(max(f['_sizes'])) if f['_sizes'] else NA}</td>
<td class="c-split" data-label="{T['col_split']}" data-m="{T['col_split']}">{split}</td><td class="c-dd" data-label="{T['col_dd']}" data-m="Daily/Max">{dd_html(f)}</td>
<td class="c-pay" data-label="{T['col_payout']}" data-m="{T['col_payout']}">{e(BUCKET_LABEL[f['_bucket']]) if f['_bucket'] else NA}</td><td class="c-mkt" data-label="{T['col_markets']}">{mkts}<small class="c-types">{types}</small></td><td class="c-plat" data-label="{T['col_platforms']}">{plats}</td>
<td class="c-code" data-label="{T['col_code']}">{code_html(f)}</td><td class="c-act">{visit(f)}</td></tr>"""

def all_platforms():
    s = {}
    for f in FIRMS:
        for p in f["_platforms"]: s[p.lower()] = p
    return sorted(s.items(), key=lambda kv: kv[1].lower())
def all_countries():
    s = set()
    for f in FIRMS:
        for c in as_list(f.get("countries_restricted")): s.add(c)
    return sorted(s)

# filters_html(firms=None, cats=True): account-type tabs + multi-select facets, defined in scripts/more_categories.py

TABLE_COLS = [("c-rk", '<abbr title="Rank by PA Score">#</abbr>'), ("c-firm", T["col_firm"]), ("c-sc", T["col_score"]), ("c-tp", T["col_rating"]),
              ("c-fee num", T["col_fee"]), ("c-max num", T["col_maxsize"]), ("c-split", T["col_split"]), ("c-dd", T["col_dd"]), ("c-pay", T["col_payout"]),
              ("c-mkt", T["col_markets"] + " / " + T["col_types"]), ("c-plat", T["col_platforms"]), ("c-code", T["col_code"]), ("c-act", '<span class="sr">Link</span>')]
SORT_KEYS = {"c-firm": "name", "c-sc": "score", "c-tp": "tp", "c-fee num": "fee", "c-max num": "maxsize", "c-split": "split", "c-pay": "payout"}
def th_html(c, t):
    k = SORT_KEYS.get(c)
    if not k: return f'<th class="{c}" scope="col">{t}</th>'
    aria = ' aria-sort="descending"' if k == "score" else ""
    return (f'<th class="{c}" scope="col" data-sort="{k}"{aria}><button type="button" class="sort">{t}'
            f'<svg class="si" viewBox="0 0 8 12" aria-hidden="true"><path class="su" d="M4 0 8 5H0z"/><path class="sd" d="M4 12 0 7h8z"/></svg></button></th>')
def table(firms, empty=False, local=False):
    head = "".join(th_html(c, t) for c, t in TABLE_COLS)
    emp = (f'<div class="empty" id="empty" hidden><p><b>No firm matches every filter.</b> Loosen one, or start again.</p>'
           f'<button type="button" class="btn line sm" data-reset>{T["filter_reset"]} filters</button></div>') if empty else ""
    return (f'<div class="tablewrap"><table class="firms" id="firms"><caption class="sr">Prop firms ranked by PA Score</caption>'
            f'<thead><tr>{head}</tr></thead><tbody>{"".join(row(f, i + 1 if local else None) for i, f in enumerate(firms))}</tbody></table></div>{emp}')

def legend():
    return (f'<p class="legend"><span>{NA} the firm does not publish this figure.</span>'
            f'<span>One formula scores every firm: <a href="{url("/methodology/")}">methodology</a>.</span></p>')

# ---------------- best-for lists ----------------
BEST = [
 ("crypto", "Crypto prop firms", "Firms that fund crypto trading (spot-style CFDs or perpetuals).", lambda f: "crypto" in f["_assets"]),
 ("forex", "Forex prop firms", "Firms with forex pairs in their instrument list.", lambda f: "forex" in f["_assets"]),
 ("futures", "Futures prop firms", "Firms funding CME-style futures accounts.", lambda f: "futures" in f["_assets"]),
 ("one-step", "1-step challenges", "Single-phase evaluations: one target, then funded.", lambda f: "1-step" in f["_types"]),
 ("instant-funding", "Instant funding", "Accounts funded without an evaluation phase.", lambda f: "instant" in f["_types"]),
 ("cheap-challenges", "Low-cost entry ($100 or less)", "Cheapest published entry fee at or under $100.", lambda f: f["_fee"] is not None and f["_fee"] <= 100),
 ("high-profit-split", "90%+ profit split", "Headline split of 90% or more (often after scaling).", lambda f: (f["_split"] or 0) >= 90),
 ("news-trading", "News trading allowed", "Firms whose rules allow trading through high-impact news.", lambda f: tri(f.get("news_trading")) is True),
 ("fast-payouts", "Fast payouts", "Daily, on-demand or weekly payout cycles.", lambda f: f["_bucket"] in ("daily", "weekly")),
 ("mt5", "MT5 prop firms", "Firms offering MetaTrader 5.", lambda f: any("mt5" in p.lower() or "metatrader 5" in p.lower() for p in f["_platforms"])),
]

def pair_link(a, b):
    return (f'<li><a href="{url("/compare/" + a + "-vs-" + b + "/")}"><span>{e(BY[a]["name"])}</span>'
            f'<i aria-hidden="true">vs</i><span class="sr"> versus </span><span>{e(BY[b]["name"])}</span></a></li>')

# ---------------- pages ----------------
ASSET_V = "11"
WEB_FONTS = ("instrument-sans.woff2",)   # bricolage/geist stay in src/fonts for scripts/og.html only
def write_assets():
    os.makedirs(os.path.join(OUT, "assets", "fonts"), exist_ok=True)
    for n in ("site.css", "site.js", "tools.js", "quiz.js", "og.png", "logo.png", "logo.webp", "logo@3x.webp", "logo-white.png", "logo-white.webp",
              "logo-white@3x.webp", "favicon-32.png", "favicon.ico", "apple-touch-icon.png"):
        src = os.path.join(ROOT, "src", n)
        if os.path.exists(src): shutil.copy(src, os.path.join(OUT, "assets", n))
    for n in ("favicon.ico", "apple-touch-icon.png"):   # root copies for crawlers/iOS that ignore <link>
        shutil.copy(os.path.join(ROOT, "src", n), os.path.join(OUT, n))
    stale = os.path.join(OUT, "assets", "favicon.svg")
    if os.path.exists(stale): os.remove(stale)
    fdir = os.path.join(ROOT, "src", "fonts")
    if os.path.isdir(fdir):
        for n in os.listdir(fdir):
            if n in WEB_FONTS: shutil.copy(os.path.join(fdir, n), os.path.join(OUT, "assets", "fonts", n))
    os.makedirs(os.path.join(OUT, "data"), exist_ok=True)
    pub = [{k: v for k, v in f.items() if not k.startswith("_")} | {"pa_score": f["_score"], "pa_components": f["_comp"], "data_completeness_pct": f["_complete"],
            "pa_rank": f["_rank"], "pa_fee_from": f["_fee"], "pa_split_max": f["_split"], "pa_payout_bucket": f["_bucket"], "pa_max_size": max(f["_sizes"]) if f["_sizes"] else None} for f in FIRMS]
    json.dump({"generated": TODAY, "firms": pub}, open(os.path.join(OUT, "data", "firms.json"), "w"), indent=1, ensure_ascii=False)

def home():
    n_prog = sum(len(as_list(f.get("programs"))) for f in FIRMS)
    n_codes = sum(1 for f in FIRMS if (f.get("discount_code") or {}).get("code"))
    lists = "".join(f'<li><a href="{url(p)}"><span>{e(n)} prop firms</span><b class="n">{sum(1 for f in FIRMS if f.get("category") == k)}</b></a></li>' for k, n, p in globals().get("CATS", []))
    lists += "".join(f'<li><a href="{url("/best/" + s + "/")}"><span>{e(t)}</span><b class="n">{sum(1 for f in FIRMS if fn(f))}</b></a></li>' for s, t, _, fn in BEST)
    pairs = "".join(pair_link(a, b) for a, b in PAIRS[:8])
    n_src = sum(len(as_list(f.get("source_urls"))) for f in FIRMS)
    avg_c = round(sum(f["_complete"] for f in FIRMS) / len(FIRMS))
    stat = lambda v, lab, suf="": f'<div><dt>{lab}</dt><dd><span class="n" data-count="{v}">{v}</span>{("<small>" + suf + "</small>") if suf else ""}</dd></div>'
    body = f"""<section class="mast wrap"><div><h1>{e(T['hero_title'])}</h1><p class="lede">{e(T['hero_sub'].format(n=len(FIRMS)))}</p>
<p class="hcta"><a class="btn" href="#table">Compare all {len(FIRMS)} firms</a><a class="btn line" href="{url('/methodology/')}">How we score</a></p></div>
<aside class="dset" aria-label="About this dataset"><dl>{stat(len(FIRMS), "Firms tracked")}{stat(n_prog, "Programs")}{stat(n_src, "Source pages cited")}{stat(avg_c, "Avg. data completeness", "%")}</dl>
<p class="src-line"><span>From each firm's own site. Verified <time datetime="{e(TODAY)}">{nice_date(TODAY)}</time></span><a href="{url('/data/firms.json')}">Open data (JSON)</a></p></aside></section>
<section class="wrap" id="table" aria-label="Firm table">{filters_html()}{table(RANKED, empty=True)}{legend()}</section>
<section class="wrap lower"><div class="rv"><h2>{e(T['best_for'])}</h2><ul class="lists">{lists}</ul></div>
<div class="rv"><h2>Head to head</h2><ul class="pairs">{pairs}</ul><p><a class="more" href="{url('/compare/')}">Pick any two firms{ic('arrow')}</a></p></div></section>"""
    ld = [{"@context": "https://schema.org", "@type": "WebSite", "name": "PropAnalyse", "url": ABS + "/"},
          {"@context": "https://schema.org", "@type": "ItemList", "name": "Prop firms ranked by PA Score", "itemListElement": [{"@type": "ListItem", "position": f["_rank"], "url": ABS + "/firms/" + f["slug"] + "/", "name": f["name"]} for f in RANKED]}]
    page("/", "Compare Prop Firms 2026: Fees, Rules & Payouts | PropAnalyse", f"Side-by-side data on {len(FIRMS)} crypto, forex and futures prop firms: challenge fees, drawdown, profit split, payout speed and discount codes.", body, ld)

def firms_index():
    c, ld = crumbs([("Home", "/"), ("All firms", "/firms/")])
    body = (f'<section class="wrap">{c}<header class="ph"><h1>All prop firms</h1><p class="lede">Filter by market, challenge type, account size, platform and your country. '
            f'Open a firm for its full rule sheet and sources.</p></header>{filters_html()}{table(RANKED, empty=True)}{legend()}</section>')
    page("/firms/", f"All {len(FIRMS)} Prop Firms Compared (2026) | PropAnalyse", "Filterable table of prop trading firms with fees, drawdown limits, profit split, platforms and payout frequency.", body, [ld])

def spec(title, rows):
    return (f'<section class="spec"><h2>{e(title)}</h2><dl>' + "".join(f'<div><dt>{e(k)}</dt><dd>{v}</dd></div>' for k, v in rows) + "</dl></section>")

def firm_summary(f):
    bits = [f"{f['name']} is a prop firm"]
    if num(f.get("founded")): bits.append(f"founded in {int(num(f['founded']))}")
    if f.get("hq"): bits.append(f"based in {f['hq']}")
    s = " ".join(bits[:1]) + (", " + ", ".join(bits[1:]) if len(bits) > 1 else "") + "."
    if f["_assets"]: s += " Markets: " + ", ".join(ASSET_LABEL.get(a, a) for a in f["_assets"]) + "."
    if f["_types"]: s += " Evaluation types: " + ", ".join(as_list(f.get("challenge_types"))) + "."
    if f["_fee"] is not None and f["_sizes"]: s += f" Published fees start at {money(f['_fee'], f.get('fee_currency'))}; account sizes run from {money(min(f['_sizes']))} to {money(max(f['_sizes']))}."
    if f.get("profit_split"): s += f" Profit split: {f['profit_split']}."
    return s

def faq(f):
    qa = []
    if f.get("profit_split"): qa.append((f"What profit split does {f['name']} pay?", f"{f['name']} lists a profit split of {f['profit_split']}" + (f" ({f['profit_split_scale']})" if f.get("profit_split_scale") else "") + f", per its website as of {f.get('last_verified', TODAY)}."))
    if f["_fee"] is not None: qa.append((f"How much is the cheapest {f['name']} challenge?", f"The lowest published fee is {money(f['_fee'], f.get('fee_currency'))}" + (f" for a {money(min(f['_sizes']))} account" if f['_sizes'] else "") + "."))
    if f.get("max_daily_loss") or f.get("max_drawdown"): qa.append((f"What are {f['name']}'s drawdown rules?", f"Daily loss limit: {f.get('max_daily_loss') or 'not published'}; maximum drawdown: {f.get('max_drawdown') or 'not published'}" + (f" ({f['drawdown_type']})" if f.get('drawdown_type') else "") + "."))
    if f.get("payout_frequency"): qa.append((f"How often does {f['name']} pay out?", f"Payout cycle: {f['payout_frequency']}." + (f" First payout eligible after {int(num(f['first_payout_days']))} days." if num(f.get('first_payout_days')) else "")))
    if f["_platforms"]: qa.append((f"Which platforms does {f['name']} support?", ", ".join(f["_platforms"]) + "."))
    nt = tri(f.get("news_trading"))
    if nt is not None: qa.append((f"Can you trade the news with {f['name']}?", {True: "Yes, news trading is allowed per the firm's rules.", False: "No, the firm restricts trading around news events.", "restricted": "Partly. News trading is restricted on some programs or windows; check the firm's rules page."}[nt]))
    return qa

def program_html(p, f):
    sf = [x for x in as_list(p.get("sizes_fees")) if num(x.get("size"))]
    cur = f.get("fee_currency")
    ladder = ""
    if sf:
        rows = "".join(f'<tr><td class="num n">{money(num(x.get("size")))}</td><td class="num n">{mh(num(x.get("fee")), cur)}</td>'
                       f'<td class="num n">{mh(num(x.get("fee")) / num(x.get("size")) * 1000, cur) if num(x.get("fee")) else NA}</td></tr>' for x in sf)
        ladder = f'<table class="ladder"><thead><tr><th class="num" scope="col">Account</th><th class="num" scope="col">Fee</th><th class="num" scope="col">Per $1K</th></tr></thead><tbody>{rows}</tbody></table>'
    strip = "".join(f'<div><dt>{k}</dt><dd class="n">{show(v)}</dd></div>' for k, v in [
        ("Profit target", p.get("profit_target")), ("Daily loss", p.get("max_daily_loss")), ("Max drawdown", p.get("max_drawdown")),
        ("Profit split", p.get("profit_split")), ("Min days", p.get("min_trading_days"))])
    ddt = f'<p class="ddt"><span>Drawdown</span> {e(p["drawdown_type"])}</p>' if p.get("drawdown_type") else ""
    return (f'<article class="prog"><h3>{e(p.get("name") or p.get("type") or "Program")}{(" <span class=" + chr(34) + "tag" + chr(34) + ">" + e(p.get("type")) + "</span>") if p.get("type") else ""}</h3>'
            f'<div class="pbody"><dl class="strip">{strip}</dl>{ddt}{ladder}</div></article>')

def firm_page(f):
    c, bl = crumbs([("Home", "/"), ("All firms", "/firms/"), (f["name"], f"/firms/{f['slug']}/")])
    progs = "".join(program_html(p, f) for p in as_list(f.get("programs")))
    comps = "".join(f'<div><dt>{COMP_LABEL[k][0]} <span class="n">{COMP_LABEL[k][1]}%</span></dt><dd>{ticks(v, i + 3, "sm")}<b class="n">{v:.1f}</b></dd></div>' for i, (k, v) in enumerate(f["_comp"].items()))
    dc = f.get("discount_code")
    dch = (f'<div class="deal"><span>Public code</span>{code_html(f)}</div>' if dc and dc.get("code")
           else '<p class="deal none">No public discount code on the firm\'s site at last check.</p>')
    srcs = "".join(f'<li><a href="{e(s)}" rel="nofollow noopener" target="_blank">{e(s)}</a></li>' for s in as_list(f.get("source_urls")))
    pairs = [(a, b) for a, b in PAIRS if f["slug"] in (a, b)]
    others = "".join(f'<li><a href="{url("/compare/" + a + "-vs-" + b + "/")}"><i>vs</i> {e(BY[b if a == f["slug"] else a]["name"])}</a></li>' for a, b in pairs)
    qa = faq(f)
    faqh = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in qa)
    restricted = as_list(f.get("countries_restricted"))
    tp = f.get("trustpilot") or {}
    tps = ((f'<span class="n">{num(tp["score"]):.1f}</span> / 5 from <span class="n">{int(num(tp.get("count") or 0)):,}</span> reviews') if tp.get("score")
           else (f'<span class="nil">No rating shown ({int(num(tp["count"])):,} reviews)</span>' if tp.get("count") else '<span class="nil">Not available</span>'))
    cpk = cost_per_k(f)
    meta = [x for x in (e(f.get("hq") or ""), f'Founded <span class="n">{int(num(f["founded"]))}</span>' if num(f.get("founded")) else "",
                        f'{T["last_verified"]} <time class="n" datetime="{e(f.get("last_verified") or TODAY)}">{nice_date(f.get("last_verified") or TODAY)}</time>') if x]
    sheet = "".join([
        spec("Cost", [("Fees from", mh(f["_fee"], f.get("fee_currency")).replace(NA, NIL)), ("Cheapest per $1K of account", mh(cpk, f.get("fee_currency")).replace(NA, NIL)),
                      ("Account sizes", ('<span class="n">' + e(", ".join(money(s) for s in f["_sizes"])) + "</span>") if f["_sizes"] else NIL)]),
        spec("Evaluation rules", [("Challenge types", show(f.get("challenge_types"))), ("Profit target", show(f.get("profit_target"))),
                                  ("Daily loss limit", show(f.get("max_daily_loss"))), ("Max drawdown", show(f.get("max_drawdown"))), ("Drawdown type", show(f.get("drawdown_type"))),
                                  ("Min trading days", show(f.get("min_trading_days"))), ("Consistency rule", show(f.get("consistency_rule")))]),
        spec("Payouts", [("Profit split", show(f.get("profit_split"))), ("Split scaling", show(f.get("profit_split_scale"))),
                         ("Payout frequency", show(f.get("payout_frequency"))), ("First payout (days)", show(f.get("first_payout_days")))]),
        spec("Trading conditions", [("Markets", show([ASSET_LABEL.get(a, a) for a in f["_assets"]])), ("Platforms", show(f["_platforms"])), ("Leverage", show(f.get("leverage"))),
                                    ("News trading", tri_label(f.get("news_trading"))), ("Weekend holding", tri_label(f.get("weekend_holding"))),
                                    ("Restricted countries", show(restricted) if restricted else '<span class="nil">Not listed</span>')]),
        spec("Reputation", [("Trustpilot", tps)]),
    ])
    s = f["_score"]
    body = f"""<div class="wrap">{c}<header class="phead"><h1>{e(f['name'])}</h1><p class="meta">{''.join('<span>' + m + '</span>' for m in meta)}</p>
<p class="lede">{e(firm_summary(f))}</p><div class="ctas">{visit(f, cls="btn")}{dch}</div></header>
<div class="pgrid"><aside class="side" aria-label="PA Score"><div class="scorebox"><p class="big n">{s:.1f}<small>/10</small></p>{ticks(s, 0, "lg")}
<p class="rk">PA Score, ranked <b class="n">#{f['_rank']}</b> of <span class="n">{len(FIRMS)}</span></p><dl class="comp">{comps}</dl>
<p class="small">Data completeness <b class="n">{f['_complete']}%</b>. Missing inputs score 4/10 by rule. <a href="{url('/methodology/')}">How scoring works</a></p></div>
{('<div class="cmpl"><h2>Compare</h2><ul>' + others + '</ul></div>') if others else ''}</aside>
<div class="pmain">{sheet}
{('<section class="block"><h2>Programs</h2>' + progs + '</section>') if progs else ''}
{('<section class="block faq"><h2>FAQ</h2>' + faqh + '</section>') if faqh else ''}
<section class="block"><h2>{T['sources']}</h2><p class="small">Every figure above was read from these pages on <time datetime="{e(f.get('last_verified') or TODAY)}">{nice_date(f.get('last_verified') or TODAY)}</time>. Firms change rules often, so confirm before you buy.</p><ol class="src">{srcs}</ol>
{('<p class="small notes"><b>Data notes.</b> ' + e(f['notes']) + '</p>') if f.get('notes') else ''}</section></div></div></div>"""
    org = {"@context": "https://schema.org", "@type": ["FinancialService", "Organization"], "name": f["name"], "url": f.get("site"),
           "foundingDate": str(int(num(f["founded"]))) if num(f.get("founded")) else None, "address": f.get("hq")}
    if (f.get("trustpilot") or {}).get("score"):
        org["aggregateRating"] = {"@type": "AggregateRating", "ratingValue": num(f["trustpilot"]["score"]), "bestRating": 5, "reviewCount": int(num(f["trustpilot"].get("count") or 0)), "author": {"@type": "Organization", "name": "Trustpilot"}}
    org = {k: v for k, v in org.items() if v is not None}
    lds = [org, bl]
    if qa: lds.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]})
    desc = f"{f['name']} prop firm rules, fees" + (f" from {money(f['_fee'], f.get('fee_currency'))}" if f['_fee'] is not None else "") + (f", {f['profit_split']} split" if f.get('profit_split') else "") + ", drawdown, payouts and discount code. Verified " + str(f.get('last_verified') or TODAY) + "."
    page(f"/firms/{f['slug']}/", f"{f['name']} Review 2026: Rules, Fees & Payouts | PropAnalyse", desc, body, lds, "article")

PAIRS = [("fundedxyz", "hyrotrader"), ("fundedxyz", "breakout-prop"), ("fundedxyz", "crypto-fund-trader"), ("hyrotrader", "breakout-prop"),
 ("hyrotrader", "crypto-fund-trader"), ("breakout-prop", "crypto-fund-trader"), ("ftmo", "fundednext"), ("ftmo", "the5ers"), ("fundednext", "fundingpips"),
 ("ftmo", "fundingpips"), ("the5ers", "fundingpips"), ("e8-markets", "ftmo"), ("apex-trader-funding", "topstep"), ("topstep", "myfundedfutures"), ("apex-trader-funding", "myfundedfutures")]

def compare_rows(a, b):
    sc = lambda f: f'<b class="n">{f["_score"]:.1f}</b> {ticks(f["_score"], 0, "sm")}'
    R = [("PA Score", sc, lambda f: f["_score"], 1), ("Trustpilot", tp_html, lambda f: num((f.get("trustpilot") or {}).get("score")), 1),
         ("Founded", lambda f: show(int(num(f["founded"]))) if num(f.get("founded")) else NIL, lambda f: -(num(f.get("founded")) or 9999), 1),
         ("HQ", lambda f: show(f.get("hq")), None, 0), ("Markets", lambda f: show([ASSET_LABEL.get(x, x) for x in f["_assets"]]), lambda f: len(f["_assets"]), 1),
         ("Challenge types", lambda f: show(f.get("challenge_types")), None, 0), ("Entry fee from", lambda f: mh(f["_fee"], f.get("fee_currency")).replace(NA, NIL), lambda f: -f["_fee"] if f["_fee"] is not None else None, 1),
         ("Cost per $1K allocation", lambda f: mh(cost_per_k(f), f.get("fee_currency")).replace(NA, NIL), lambda f: -cost_per_k(f) if cost_per_k(f) is not None else None, 1),
         ("Largest account", lambda f: mh(max(f["_sizes"])) if f["_sizes"] else NIL, lambda f: max(f["_sizes"]) if f["_sizes"] else None, 1),
         ("Profit target", lambda f: show(f.get("profit_target")), None, 0), ("Daily loss limit", lambda f: show(f.get("max_daily_loss")), lambda f: first_pct(f.get("max_daily_loss")), 1),
         ("Max drawdown", lambda f: show(f.get("max_drawdown")), lambda f: first_pct(f.get("max_drawdown")), 1), ("Drawdown type", lambda f: show(f.get("drawdown_type")), None, 0),
         ("Profit split", lambda f: show(f.get("profit_split")), lambda f: f["_split"], 1), ("Leverage", lambda f: show(f.get("leverage")), None, 0),
         ("Platforms", lambda f: show(f["_platforms"]), None, 0), ("Payout frequency", lambda f: show(f.get("payout_frequency")), None, 0),
         ("First payout (days)", lambda f: show(f.get("first_payout_days")), lambda f: -num(f.get("first_payout_days")) if num(f.get("first_payout_days")) is not None else None, 1),
         ("Min trading days", lambda f: show(f.get("min_trading_days")), None, 0), ("Consistency rule", lambda f: show(f.get("consistency_rule")), None, 0),
         ("News trading", lambda f: tri_label(f.get("news_trading")), None, 0), ("Weekend holding", lambda f: tri_label(f.get("weekend_holding")), None, 0),
         ("Discount code", lambda f: code_html(f).replace(NA, NIL), None, 0)]
    out, wins, compared = "", {a["slug"]: 0, b["slug"]: 0}, 0
    WIN = '<span class="sr"> (stronger figure)</span>'
    for label, fmt, key, cmp in R:
        ca = cb = ""
        if cmp and key:
            try:
                va, vb = key(a), key(b)
                if va is not None and vb is not None:
                    compared += 1
                    if va > vb: ca = "win"; wins[a["slug"]] += 1
                    elif vb > va: cb = "win"; wins[b["slug"]] += 1
            except Exception: pass
        cell = lambda f, w: f'<td{(" class=" + chr(34) + w + chr(34)) if w else ""}><span class="v">{fmt(f)}</span>{WIN if w else ""}</td>'
        out += f'<tr><th scope="row">{e(label)}</th>{cell(a, ca)}{cell(b, cb)}</tr>'
    return out, wins, compared

def compare_page(sa, sb):
    a, b = BY.get(sa), BY.get(sb)
    if not a or not b: return
    path = f"/compare/{sa}-vs-{sb}/"
    c, bl = crumbs([("Home", "/"), ("Compare", "/compare/"), (f"{a['name']} vs {b['name']}", path)])
    rows, wins, compared = compare_rows(a, b)
    def verdict():
        lines = []
        if a["_fee"] is not None and b["_fee"] is not None and a["_fee"] != b["_fee"]:
            lo = a if a["_fee"] < b["_fee"] else b; lines.append(f"Cheaper entry: {lo['name']} ({money(lo['_fee'], lo.get('fee_currency'))} vs {money((b if lo is a else a)['_fee'], (b if lo is a else a).get('fee_currency'))}).")
        if a["_split"] and b["_split"] and a["_split"] != b["_split"]:
            hi = a if a["_split"] > b["_split"] else b; lines.append(f"Higher headline split: {hi['name']} ({hi.get('profit_split')}).")
        ra, rb = a["_bucket"], b["_bucket"]; order = ["daily", "weekly", "biweekly", "monthly", "other"]
        if ra and rb and ra != rb:
            fa = a if order.index(ra) < order.index(rb) else b; lines.append(f"Faster payout cycle: {fa['name']} ({BUCKET_LABEL[fa['_bucket']]}).")
        ta, tb = num((a.get("trustpilot") or {}).get("score")), num((b.get("trustpilot") or {}).get("score"))
        if ta and tb and ta != tb:
            t = a if ta > tb else b; lines.append(f"Higher Trustpilot rating: {t['name']} ({max(ta, tb):.1f}).")
        lines.append(f"Overall PA Score: {a['name']} {a['_score']:.1f} vs {b['name']} {b['_score']:.1f}.")
        return "".join(f"<li>{e(x)}</li>" for x in lines)
    disc = ""
    if "fundedxyz" in (sa, sb): disc = '<p class="note"><b>Disclosure.</b> PropAnalyse is run by the team behind FundedXYZ. This comparison uses the same data fields and scoring formula as every other page.</p>'
    wa, wb = wins[sa], wins[sb]
    tally = (f'<p class="tally"><span><b>{e(a["name"])}</b> stronger on <b class="n">{wa}</b></span><span><b>{e(b["name"])}</b> stronger on <b class="n">{wb}</b></span>'
             f'<span class="muted">of <span class="n">{compared}</span> lines where both publish a comparable figure</span></p>')
    headcell = lambda f, slug: (f'<th scope="col"><a class="fn" href="{url("/firms/" + slug + "/")}">{e(f["name"])}</a>'
                                f'<span class="hs"><b class="n">{f["_score"]:.1f}</b>{ticks(f["_score"], 1, "sm")}<span class="sr"> PA Score</span></span></th>')
    body = f"""<div class="wrap">{c}<header class="ph"><h1>{e(a['name'])} <i class="vs">vs</i> {e(b['name'])}</h1>
<p class="lede">Rule-by-rule comparison from each firm's own website, last verified <time datetime="{e(TODAY)}">{nice_date(TODAY)}</time>. The marked figure is the stronger one on that line.</p>{disc}</header>
<div class="cgrid"><section class="take"><h2>Quick take</h2><ul class="verdict">{verdict()}</ul>{tally}</section>
<div class="cmpwrap"><table class="cmp"><caption class="sr">{e(a['name'])} compared with {e(b['name'])}</caption><thead><tr><td></td>{headcell(a, sa)}{headcell(b, sb)}</tr></thead><tbody>{rows}</tbody>
<tfoot><tr><td></td><td>{visit(a, T['visit'], 'btn')}</td><td>{visit(b, T['visit'], 'btn')}</td></tr></tfoot></table>
<p class="legend"><span>{NIL} means we could not find the figure on the firm's own site. Sources are listed on each firm page.</span></p></div></div></div>"""
    qa = [(f"Which is cheaper, {a['name']} or {b['name']}?", f"Lowest published entry fee: {a['name']} {money(a['_fee'], a.get('fee_currency'))}, {b['name']} {money(b['_fee'], b.get('fee_currency'))}."),
          (f"Which has the higher profit split, {a['name']} or {b['name']}?", f"{a['name']}: {a.get('profit_split') or 'not published'}; {b['name']}: {b.get('profit_split') or 'not published'}.")]
    ld = [bl, {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": t}} for q, t in qa]}]
    page(path, f"{a['name']} vs {b['name']} (2026): Fees, Rules, Payouts Compared", f"{a['name']} vs {b['name']}: entry fees, drawdown, profit split, payout speed and platforms side by side. Verified {TODAY}.", body, ld, "article")

def pair_group(a):
    if a in ("fundedxyz", "hyrotrader", "breakout-prop", "crypto-fund-trader"): return "Crypto"
    return "Futures" if "futures" in BY[a]["_assets"] and "forex" not in BY[a]["_assets"] else "Forex / multi-asset"

def compare_index():
    c, bl = crumbs([("Home", "/"), ("Compare", "/compare/")])
    opts = "".join(f'<option value="{f["slug"]}">{e(f["name"])}</option>' for f in sorted(FIRMS, key=lambda x: x["name"].lower()))
    groups = {}
    for a, b in PAIRS:
        if a in BY and b in BY: groups.setdefault(pair_group(a), []).append((a, b))
    gh = "".join(f'<div><h3>{e(g)}</h3><ul class="pairs">{"".join(pair_link(a, b) for a, b in ps)}</ul></div>' for g, ps in groups.items())
    body = f"""<div class="wrap">{c}<header class="ph"><h1>Compare prop firms</h1><p class="lede">Pick any two firms for a side-by-side, or open one of the common match-ups below.</p></header>
<form class="picker" id="picker" onsubmit="return false"><label class="fl"><span>First firm</span><select id="pa">{opts}</select></label><i class="vs" aria-hidden="true">vs</i>
<label class="fl"><span>Second firm</span><select id="pb">{opts}</select></label><button class="btn" id="pgo" type="submit">{T['compare_cta']}</button></form>
<div id="live" class="cmpwrap" aria-live="polite"></div><section class="block"><h2>Popular comparisons</h2><div class="pgroups">{gh}</div></section></div>
<script>window.PFA_FIRMS_URL="{url('/data/firms.json')}";window.PFA_PAIRS={json.dumps([a + '-vs-' + b for a, b in PAIRS])};window.PFA_BASE="{BASE}";</script>"""
    page("/compare/", "Compare Prop Firms Side by Side | PropAnalyse", "Compare any two prop firms on fees, drawdown, profit split, payouts and platforms.", body, [bl])

def discounts():
    c, bl = crumbs([("Home", "/"), ("Discounts", "/discounts/")])
    withc = [f for f in RANKED if (f.get("discount_code") or {}).get("code")]
    without = [f for f in RANKED if not (f.get("discount_code") or {}).get("code")]
    rows = "".join(f"""<li class="dl"><a class="dn" href="{url('/firms/' + f['slug'] + '/')}"><b>{e(f['name'])}</b><small>From {money(f['_fee'], f.get('fee_currency')) if f['_fee'] is not None else 'n/a'}{(', ' + e(f.get('profit_split'))) if f.get('profit_split') else ''}</small></a>
<p class="dv">{e(f['discount_code'].get('value') or 'Discount')}</p><div class="dc">{code_html(f, False)}<small>Seen <time datetime="{e(f.get('last_verified') or TODAY)}">{nice_date(f.get('last_verified') or TODAY)}</time></small></div>{score_html(f)}{visit(f)}</li>""" for f in withc)
    body = f"""<div class="wrap">{c}<header class="ph"><h1>Prop firm discount codes</h1><p class="lede">Only codes published on each firm's own website. Codes expire; the firm's checkout is the final word.</p></header>
{('<ul class="deals">' + rows + '</ul>') if rows else '<p class="empty">No public codes found at last check.</p>'}
<section class="block"><h2>No public code right now</h2><p class="inline-list">{''.join(f'<a href="{url("/firms/" + f["slug"] + "/")}">{e(f["name"])}</a>' for f in without)}</p></section></div>"""
    page("/discounts/", f"Prop Firm Discount Codes ({datetime.date.fromisoformat(TODAY).strftime('%B %Y')}) | PropAnalyse", "Current public discount codes for prop firm challenges, checked against each firm's website.", body, [bl])

def best_pages():
    c, bl = crumbs([("Home", "/"), ("Best for", "/best/")])
    items = "".join(f'<li><a href="{url("/best/" + s + "/")}"><b>{e(t)}</b><span>{e(d)}</span><span class="cnt"><b class="n">{sum(1 for f in FIRMS if fn(f))}</b> firms</span>{ic("arrow")}</a></li>' for s, t, d, fn in BEST)
    page("/best/", "Best Prop Firms by Category | PropAnalyse", "Prop firms grouped by market, challenge type, cost, split and payout speed, ranked by PA Score.",
         f'<div class="wrap">{c}<header class="ph"><h1>Best prop firms for…</h1><p class="lede">Each list is a filter over the same firm table, ranked by the same PA Score.</p></header><ul class="shortlists">{items}</ul></div>', [bl])
    for s, t, d, fn in BEST:
        fl = [f for f in RANKED if fn(f)]
        c2, bl2 = crumbs([("Home", "/"), ("Best for", "/best/"), (t, f"/best/{s}/")])
        body = f'<div class="wrap">{c2}<header class="ph"><h1>Best {e(t.lower())} ({YEAR_NOW})</h1><p class="lede">{e(d)} <span class="n">{len(fl)}</span> firms match, ranked by PA Score.</p></header>{table(fl)}{legend()}</div>'
        ld = {"@context": "https://schema.org", "@type": "ItemList", "name": t, "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": ABS + "/firms/" + f["slug"] + "/", "name": f["name"]} for i, f in enumerate(fl)]}
        page(f"/best/{s}/", f"Best {t} {YEAR_NOW}, Ranked | PropAnalyse", f"{len(fl)} {t.lower()} ranked by PA Score with fees, split and payout data.", body, [bl2, ld])

def methodology():
    c, bl = crumbs([("Home", "/"), ("Methodology", "/methodology/")])
    body = f"""<div class="wrap">{c}<article class="prose"><h1>How we collect data and score firms</h1>
<p class="note"><b>Ownership disclosure.</b> PropAnalyse is operated by the team behind FundedXYZ; FundedXYZ is scored by the same rules as every other firm. It gets no manual adjustment, no default sort position, and its data is collected with the same checklist.</p>
<h2>Where the numbers come from</h2><p>Every figure is read from the prop firm's own website (pricing, rules, FAQ or help-centre pages) and the date is recorded per firm. Ratings come from the firm's public Trustpilot page. If a firm does not publish a number, we show "Not published". We never estimate.</p>
<h2>The PA Score (0 to 10)</h2><p>One formula, applied mechanically by our build script:</p>
<table class="mini"><thead><tr><th scope="col">Component</th><th scope="col" class="num">Weight</th><th scope="col">Inputs</th></tr></thead><tbody>
<tr><td>Trust</td><td class="num n">30%</td><td>Trustpilot score (3.0 scores 0, 5.0 full marks), scaled by review volume (log₁₀ of count)</td></tr>
<tr><td>Cost</td><td class="num n">20%</td><td>Cheapest fee per $1,000 of account size across published programs</td></tr>
<tr><td>Rules</td><td class="num n">20%</td><td>Daily loss limit, max drawdown, static vs trailing drawdown, news trading, weekend holding, consistency rule</td></tr>
<tr><td>Payout</td><td class="num n">20%</td><td>Headline profit split, days to first payout, payout cycle</td></tr>
<tr><td>Track record</td><td class="num n">10%</td><td>Years in operation (8+ years = full marks)</td></tr></tbody></table>
<p>Payout cycle uses the firm's headline (first-listed) plan. Fees are compared in the currency the firm prices in (FTMO lists EUR); no FX conversion is applied. Trustpilot profiles that show no rating (e.g. suspended for a guideline breach) count as missing.</p><p>Missing inputs score 4/10 for that component, so withholding information never helps a firm. Each firm page shows its component breakdown and a data-completeness percentage.</p>
<h2>What the score is not</h2><p>It is not a prediction of whether you will pass or get paid, and it is not financial advice. Affiliate relationships do not affect scores or ordering.</p>
<h2>Corrections</h2><p>Firms change rules frequently. If you spot an outdated figure, tell us with a link to the firm's page and we will re-verify. See the <a href="{url('/updates/')}">verification log</a>.</p>
<p class="small">The full formula lives in <code>scripts/build.py</code>; the dataset is published at <a href="{url('/data/firms.json')}">/data/firms.json</a>.</p></article></div>"""
    page("/methodology/", "Methodology & Scoring | PropAnalyse", "How PropAnalyse collects prop firm data and calculates the PA Score. Ownership disclosure included.", body, [bl])

def about():
    c, bl = crumbs([("Home", "/"), ("About", "/about/")])
    body = f"""<div class="wrap">{c}<article class="prose"><h1>About PropAnalyse</h1>
<p>PropAnalyse is a data-first comparison of prop trading firms across crypto, forex and futures. We track the rules that decide whether a trader can realistically pass and get paid: fees, drawdown type, profit split, payout cycle and restrictions.</p>
<p class="note"><b>Who runs this site.</b> PropAnalyse is operated by the team behind <a href="{url('/firms/fundedxyz/')}">FundedXYZ</a>, a crypto prop firm. FundedXYZ is listed and scored by exactly the same rules as every other firm; see <a href="{url('/methodology/')}">methodology</a>.</p>
<h2>How we make money</h2><p>Some "Visit site" links may become affiliate links. A firm cannot pay to change its data, score or ranking.</p>
<h2>Contact</h2><p>Corrections and firm data updates: please include a link to the firm's own page that shows the change.</p></article></div>"""
    ld = {"@context": "https://schema.org", "@type": "Organization", "name": "PropAnalyse", "url": ABS + "/"}
    page("/about/", "About PropAnalyse: Who We Are & Disclosure", "Who runs PropAnalyse, how the site is funded, and our ownership disclosure.", body, [bl, ld])

def updates():
    c, bl = crumbs([("Home", "/"), ("Verification log", "/updates/")])
    rows = "".join(f'<tr><td><a href="{url("/firms/" + f["slug"] + "/")}">{e(f["name"])}</a></td><td class="n"><time datetime="{e(f.get("last_verified") or TODAY)}">{nice_date(f.get("last_verified") or TODAY)}</time></td>'
                   f'<td class="num"><span class="cmpl-v">{ticks(f["_complete"] / 10, 0, "sm")}<b class="n">{f["_complete"]}%</b></span></td><td class="num n">{len(as_list(f.get("source_urls")))}</td></tr>' for f in sorted(FIRMS, key=lambda x: x["name"].lower()))
    body = (f'<div class="wrap">{c}<header class="ph"><h1>Verification log &amp; rule changes</h1><p class="lede">When each firm was last checked, and how complete its public data is. Rule changes will be logged here as they are detected.</p></header>'
            f'<div class="tablewrap"><table class="mini log"><thead><tr><th scope="col">Firm</th><th scope="col">Last verified</th><th scope="col" class="num">Data completeness</th><th scope="col" class="num">Source pages</th></tr></thead><tbody>{rows}</tbody></table></div></div>')
    page("/updates/", "Prop Firm Rule Changes & Verification Log | PropAnalyse", "When each prop firm's rules were last verified and logged rule changes.", body, [bl])

def not_found():
    open(os.path.join(OUT, "404.html"), "w").write(
        f'<!doctype html><html lang="en"><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><title>Not found | PropAnalyse</title>'
        f'{icons()}<link rel=stylesheet href="{url("/assets/site.css")}?v={ASSET_V}">'
        f'<body><header class="top"><div class="wrap bar">{brand()}</div></header><main class="wrap nf"><p class="big n">404</p><h1>That page is not on the sheet.</h1>'
        f'<p class="lede">The firm or comparison may have moved. Every firm is still in the main table.</p><p><a class="btn" href="{url("/")}">Back to the table</a></p></main></body></html>')

def seo_files():
    sm = "".join(f"<url><loc>{ABS}{p}</loc><lastmod>{TODAY}</lastmod></url>" for p in PAGES)
    open(os.path.join(OUT, "sitemap.xml"), "w").write(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>')
    open(os.path.join(OUT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\n\nSitemap: {ABS}/sitemap.xml\n")
    lines = [f"# PropAnalyse", "", "> Data-first comparison of prop trading firms (crypto, forex, futures). Every figure is taken from the firm's own website; unknown values are left blank rather than estimated.",
             "", f"Operated by the team behind FundedXYZ; FundedXYZ is scored with the same formula as every other firm.", "", "## Key pages",
             f"- [All firms]({ABS}/firms/): filterable table", f"- [Methodology]({ABS}/methodology/): PA Score formula", f"- [Discount codes]({ABS}/discounts/)", f"- [Open dataset (JSON)]({ABS}/data/firms.json)", "", "## Firms"]
    lines += [f"- [{f['name']}]({ABS}/firms/{f['slug']}/): PA Score {f['_score']}, fee from {money(f['_fee'], f.get('fee_currency'))}, split {f.get('profit_split') or 'n/a'}, verified {f.get('last_verified') or TODAY}" for f in RANKED]
    lines += ["", "## Comparisons"] + [f"- [{BY[a]['name']} vs {BY[b]['name']}]({ABS}/compare/{a}-vs-{b}/)" for a, b in PAIRS if a in BY and b in BY]
    open(os.path.join(OUT, "llms.txt"), "w").write("\n".join(lines) + "\n")
    open(os.path.join(OUT, ".nojekyll"), "w").write("")
    if SITE_URL.startswith("https://") and "github.io" not in SITE_URL and not BASE: open(os.path.join(OUT, "CNAME"), "w").write(SITE_URL.split("://", 1)[1] + "\n")

for _m in ("more_core.py", "more_pages_a.py", "more_pages_b.py", "more_guides.py", "more_programmatic.py", "more_zh.py", "more_categories.py", "more_seo.py", "more_badge.py"):
    _p = os.path.join(ROOT, "scripts", _m); exec(compile(open(_p).read(), _p, "exec"))

if __name__ == "__main__":
    PAIRS[:] = [(a, b) for a, b in PAIRS if a in BY and b in BY]
    CHANGES = changelog()
    if os.path.exists(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT)
    write_assets(); home(); firms_index()
    for f in FIRMS: firm_page(f)
    compare_index()
    for a, b in PAIRS: compare_page(a, b)
    offers(); best_pages(); methodology(); about(); updates(); crypto_hub(); news(); tools(); quiz(); guides(); glossary(); site_faq(); programmatic(); not_found(); seo_files()
    print(f"built {len(PAGES)} pages -> {OUT}")
