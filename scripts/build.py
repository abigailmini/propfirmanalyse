#!/usr/bin/env python3
"""PropFirmAnalyse static site generator. Regenerates every page from data/firms.json.
Usage: python3 scripts/build.py  [env BASE_PATH=/propfirmanalyse SITE_URL=https://abigailmini.github.io]
"""
import json, os, re, math, html, shutil, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "site")
BASE = os.environ.get("BASE_PATH", "/propfirmanalyse").rstrip("/")
SITE_URL = os.environ.get("SITE_URL", "https://abigailmini.github.io").rstrip("/")
ABS = SITE_URL + BASE
T = json.load(open(os.path.join(ROOT, "i18n", "en.json")))
DATA = json.load(open(os.path.join(ROOT, "data", "firms.json")))
FIRMS = DATA["firms"]
TODAY = DATA.get("generated", datetime.date.today().isoformat())
YEAR_NOW = 2026
e = lambda s: html.escape(str(s), quote=True)

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
    if v is None: return "—"
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

def show(v, suffix=""):
    if v in (None, "", [], {}): return '<span class="na">' + T["unknown"] + "</span>"
    if v is True: return "Allowed"
    if v is False: return "Not allowed"
    if isinstance(v, list): return e(", ".join(str(x) for x in v))
    return e(str(v)) + suffix

def tri_label(v):
    v = tri(v)
    return {True: "Allowed", False: "Not allowed", "restricted": "Restricted", None: '<span class="na">' + T["unknown"] + "</span>"}[v]

# ---------------- page shell ----------------
def url(p): return BASE + p
def page(path, title, desc, body, jsonld=None, og_type="website", extra_head=""):
    canon = ABS + path
    ld = "".join('<script type="application/ld+json">' + json.dumps(j, ensure_ascii=False) + "</script>" for j in (jsonld or []))
    nav = [("/firms/", T["nav_firms"]), ("/compare/", T["nav_compare"]), ("/discounts/", T["nav_discounts"]), ("/best/", T["nav_best"]), ("/methodology/", T["nav_method"]), ("/about/", T["nav_about"])]
    navh = "".join(f'<a href="{url(h)}"{" aria-current=page" if path.startswith(h) else ""}>{e(t)}</a>' for h, t in nav)
    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{canon}">
<meta property="og:type" content="{og_type}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canon}"><meta property="og:image" content="{ABS}/assets/og.png"><meta property="og:site_name" content="PropFirmAnalyse">
<meta name="twitter:card" content="summary_large_image"><meta name="theme-color" content="#0b1426">
<link rel="icon" href="{url('/assets/favicon.svg')}" type="image/svg+xml"><link rel="stylesheet" href="{url('/assets/site.css')}">
<link rel="alternate" hreflang="en" href="{canon}"><link rel="alternate" hreflang="x-default" href="{canon}">{extra_head}{ld}</head>
<body><a class="skip" href="#main">Skip to content</a>
<header class="top"><div class="wrap bar"><a class="brand" href="{url('/')}"><span class="logo">PF<b>A</b></span><span>PropFirm<b>Analyse</b></span></a>
<button class="menu" aria-label="Menu" onclick="document.body.classList.toggle('nav-open')">☰</button><nav class="nav">{navh}</nav></div></header>
<main id="main">{body}</main>
<footer class="foot"><div class="wrap"><div class="fgrid"><div><a class="brand" href="{url('/')}"><span class="logo">PF<b>A</b></span><span>PropFirm<b>Analyse</b></span></a>
<p class="muted small">{e(T['tagline'])}</p></div><div><h4>Explore</h4>{navh}<a href="{url('/updates/')}">Verification log</a></div>
<div><h4>Disclosure</h4><p class="small">{e(T['ownership'])}</p></div></div>
<p class="small muted disc">{e(T['disclaimer'])}</p><p class="small muted">© {YEAR_NOW} PropFirmAnalyse · Data last verified {e(TODAY)} · <a href="{url('/llms.txt')}">llms.txt</a> · <a href="{url('/data/firms.json')}">Open data (JSON)</a></p></div></footer>
<script src="{url('/assets/site.js')}" defer></script></body></html>"""
    dest = os.path.join(OUT, path.lstrip("/"), "index.html") if path.endswith("/") else os.path.join(OUT, path.lstrip("/"))
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    open(dest, "w").write(doc)
    PAGES.append(path)
PAGES = []

def crumbs(items):
    lis = [{"@type": "ListItem", "position": i + 1, "name": n, "item": ABS + p} for i, (n, p) in enumerate(items)]
    html_ = '<nav class="crumbs">' + " / ".join(f'<a href="{url(p)}">{e(n)}</a>' for n, p in items) + "</nav>"
    return html_, {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": lis}

# ---------------- components ----------------
ASSET_LABEL = {"crypto": "Crypto", "forex": "Forex", "indices": "Indices", "commodities": "Commodities", "stocks": "Stocks", "futures": "Futures", "metals": "Metals", "energies": "Energies"}
def badge_score(f):
    s = f["_score"]; cls = "hi" if s >= 7 else ("mid" if s >= 5.5 else "lo")
    return f'<span class="score {cls}" title="PFA Score – data completeness {f["_complete"]}%">{s:.1f}</span>'

def code_html(f):
    dc = f.get("discount_code")
    if not dc or not dc.get("code"): return '<span class="na">—</span>'
    return f'<button class="code" data-copy="{e(dc["code"])}" title="{e(dc.get("value") or "")}">{e(dc["code"])}<small>{e(dc.get("value") or "")}</small></button>'

def tp_html(f):
    tp = f.get("trustpilot") or {}
    if not tp.get("score"):
        return '<span class="na" title="Trustpilot shows no rating (e.g. suspended for a guideline breach)">n/a</span>' if tp.get("count") else '<span class="na">—</span>'
    return f'<span class="tp">★ {num(tp["score"]):.1f}<small>{int(num(tp.get("count") or 0)):,}</small></span>'

def dd_html(f):
    a = f.get("max_daily_loss"); b = f.get("max_drawdown")
    return f'{e(a) if a else "—"} / {e(b) if b else "—"}' + (f'<small>{e(f["drawdown_type"])}</small>' if f.get("drawdown_type") else "")

def row(f):
    attrs = {
        "assets": " ".join(f["_assets"]), "types": " ".join(f["_types"]), "platforms": "|".join(p.lower() for p in f["_platforms"]),
        "fee": f["_fee"] if f["_fee"] is not None else "", "maxsize": max(f["_sizes"]) if f["_sizes"] else "",
        "split": f["_split"] if f["_split"] is not None else "", "score": f["_score"], "name": f["name"].lower(),
        "news": str(tri(f.get("news_trading"))).lower(), "weekend": str(tri(f.get("weekend_holding"))).lower(),
        "payout": f["_bucket"] or "", "restricted": "|".join(c.lower() for c in as_list(f.get("countries_restricted"))),
        "tp": num((f.get("trustpilot") or {}).get("score")) or "", "founded": num(f.get("founded")) or "",
    }
    da = " ".join(f'data-{k}="{e(v)}"' for k, v in attrs.items())
    assets = "".join(f'<span class="chip">{e(ASSET_LABEL.get(a, a.title()))}</span>' for a in f["_assets"]) or '<span class="na">—</span>'
    types = e(", ".join(as_list(f.get("challenge_types")))) or "—"
    plats = e(", ".join(f["_platforms"][:3])) + (f' <small>+{len(f["_platforms"]) - 3}</small>' if len(f["_platforms"]) > 3 else "") if f["_platforms"] else "—"
    return f"""<tr {da}><td class="firm"><a href="{url('/firms/' + f['slug'] + '/')}"><span class="av">{e(f['name'][:2])}</span><span><b>{e(f['name'])}</b><small>{e(f.get('hq') or '')}{' · est. ' + str(int(num(f['founded']))) if num(f.get('founded')) else ''}</small></span></a></td>
<td data-label="{T['col_score']}">{badge_score(f)}</td><td data-label="{T['col_rating']}">{tp_html(f)}</td><td data-label="{T['col_markets']}">{assets}</td><td data-label="{T['col_types']}">{types}</td>
<td data-label="{T['col_fee']}">{money(f['_fee'], f.get('fee_currency'))}</td><td data-label="{T['col_maxsize']}">{money(max(f['_sizes'])) if f['_sizes'] else '—'}</td><td data-label="{T['col_split']}">{e(f.get('profit_split') or '—')}</td>
<td data-label="{T['col_dd']}">{dd_html(f)}</td><td data-label="{T['col_payout']}">{e(BUCKET_LABEL.get(f['_bucket'], '—')) if f['_bucket'] else '—'}</td><td data-label="{T['col_platforms']}">{plats}</td>
<td data-label="{T['col_code']}">{code_html(f)}</td><td class="act"><a class="btn sm ghost" href="{url('/firms/' + f['slug'] + '/')}">{T['view']}</a><a class="btn sm" href="{e(f.get('affiliate_url') or '#')}" rel="sponsored nofollow noopener" target="_blank" data-firm="{e(f['slug'])}">{T['visit']}</a></td></tr>"""

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

def filters_html():
    o = lambda v, t: f'<option value="{e(v)}">{e(t)}</option>'
    plats = "".join(o(k, v) for k, v in all_platforms())
    ctry = "".join(o(c.lower(), c) for c in all_countries())
    return f"""<form class="filters" id="filters" onsubmit="return false">
<div class="frow"><input type="search" id="q" placeholder="Search firm…" aria-label="Search firm">
<label>{T['filter_market']}<select id="f-asset"><option value="">All</option>{o('crypto','Crypto')}{o('forex','Forex')}{o('futures','Futures')}{o('indices','Indices')}{o('commodities','Commodities')}{o('stocks','Stocks')}</select></label>
<label>{T['filter_type']}<select id="f-type"><option value="">Any</option>{o('1-step','1-step')}{o('2-step','2-step')}{o('3-step','3-step')}{o('instant','Instant funding')}</select></label>
<label>{T['filter_size']}<select id="f-size"><option value="">Any</option>{o('10000','$10K+')}{o('50000','$50K+')}{o('100000','$100K+')}{o('200000','$200K+')}{o('300000','$300K+')}</select></label>
<label>{T['filter_platform']}<select id="f-plat"><option value="">Any</option>{plats}</select></label>
<label>{T['filter_fee']}<select id="f-fee"><option value="">Any</option>{o('50','≤ $50')}{o('100','≤ $100')}{o('200','≤ $200')}</select></label>
<label>{T['filter_split']}<select id="f-split"><option value="">Any</option>{o('80','80%+')}{o('90','90%+')}{o('100','100%')}</select></label>
<label>{T['filter_payout']}<select id="f-payout"><option value="">Any</option>{o('daily','Daily / on demand')}{o('weekly','Weekly or faster')}{o('biweekly','Bi-weekly or faster')}</select></label>
<label>{T['filter_country']}<select id="f-country"><option value="">Any country</option>{ctry}</select></label>
<label class="tog"><input type="checkbox" id="f-news"> {T['filter_news']}</label><label class="tog"><input type="checkbox" id="f-weekend"> {T['filter_weekend']}</label>
<label>{T['sort']}<select id="f-sort">{o('score','PFA Score')}{o('fee','Lowest entry fee')}{o('split','Highest split')}{o('tp','Trustpilot')}{o('founded','Longest running')}{o('name','A–Z')}</select></label>
<button type="button" class="btn ghost sm" id="f-reset">{T['filter_reset']}</button></div><p class="count" id="count" aria-live="polite"></p></form>"""

def table(firms):
    head = "".join(f"<th>{T[k]}</th>" for k in ["col_firm", "col_score", "col_rating", "col_markets", "col_types", "col_fee", "col_maxsize", "col_split", "col_dd", "col_payout", "col_platforms", "col_code"]) + "<th></th>"
    return f'<div class="tablewrap"><table class="firms" id="firms"><thead><tr>{head}</tr></thead><tbody>{"".join(row(f) for f in firms)}</tbody></table></div>'

# ---------------- best-for lists ----------------
BEST = [
 ("crypto", "Crypto prop firms", "Firms that fund crypto trading (spot-style CFDs or perpetuals).", lambda f: "crypto" in f["_assets"]),
 ("forex", "Forex prop firms", "Firms with forex pairs in their instrument list.", lambda f: "forex" in f["_assets"]),
 ("futures", "Futures prop firms", "Firms funding CME-style futures accounts.", lambda f: "futures" in f["_assets"]),
 ("one-step", "1-step challenges", "Single-phase evaluations: one target, then funded.", lambda f: "1-step" in f["_types"]),
 ("instant-funding", "Instant funding", "Accounts funded without an evaluation phase.", lambda f: "instant" in f["_types"]),
 ("cheap-challenges", "Low-cost entry (≤ $100)", "Cheapest published entry fee at or under $100.", lambda f: f["_fee"] is not None and f["_fee"] <= 100),
 ("high-profit-split", "90%+ profit split", "Headline split of 90% or more (often after scaling).", lambda f: (f["_split"] or 0) >= 90),
 ("news-trading", "News trading allowed", "Firms whose rules allow trading through high-impact news.", lambda f: tri(f.get("news_trading")) is True),
 ("fast-payouts", "Fast payouts", "Daily, on-demand or weekly payout cycles.", lambda f: f["_bucket"] in ("daily", "weekly")),
 ("mt5", "MT5 prop firms", "Firms offering MetaTrader 5.", lambda f: any("mt5" in p.lower() or "metatrader 5" in p.lower() for p in f["_platforms"])),
]

# ---------------- pages ----------------
def write_assets():
    os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)
    for n in ("site.css", "site.js", "favicon.svg", "og.png"):
        src = os.path.join(ROOT, "src", n)
        if os.path.exists(src): shutil.copy(src, os.path.join(OUT, "assets", n))
    os.makedirs(os.path.join(OUT, "data"), exist_ok=True)
    pub = [{k: v for k, v in f.items() if not k.startswith("_")} | {"pfa_score": f["_score"], "pfa_components": f["_comp"], "data_completeness_pct": f["_complete"]} for f in FIRMS]
    json.dump({"generated": TODAY, "firms": pub}, open(os.path.join(OUT, "data", "firms.json"), "w"), indent=1, ensure_ascii=False)

def home():
    chips = "".join(f'<a class="chip big" href="{url("/best/" + s + "/")}">{e(t)}</a>' for s, t, _, _ in BEST)
    top3 = RANKED[:3]
    stats = f'<div class="stats"><div><b>{len(FIRMS)}</b><span>firms tracked</span></div><div><b>{sum(len(as_list(f.get("programs"))) for f in FIRMS)}</b><span>programs</span></div><div><b>{sum(1 for f in FIRMS if f.get("discount_code"))}</b><span>public codes</span></div><div><b>{e(TODAY)}</b><span>last verified</span></div></div>'
    body = f"""<section class="hero"><div class="wrap"><h1>{e(T['hero_title'])}</h1><p class="lead">{e(T['hero_sub'].format(n=len(FIRMS)))}</p>{stats}
<div class="chips" aria-label="{T['best_for']}"><span class="muted small">{T['best_for']}:</span>{chips}</div></div></section>
<section class="wrap">{filters_html()}{table(RANKED)}<p class="small muted">Scores use one published formula for every firm — <a href="{url('/methodology/')}">see methodology</a>. “—” means the firm does not publish that figure.</p></section>
<section class="wrap grid3">{''.join(f'<a class="card" href="{url("/compare/" + a + "-vs-" + b + "/")}"><small>Compare</small><b>{e(BY[a]["name"])} vs {e(BY[b]["name"])}</b></a>' for a, b in PAIRS[:6])}</section>"""
    ld = [{"@context": "https://schema.org", "@type": "WebSite", "name": "PropFirmAnalyse", "url": ABS + "/"},
          {"@context": "https://schema.org", "@type": "ItemList", "name": "Prop firms ranked by PFA Score", "itemListElement": [{"@type": "ListItem", "position": f["_rank"], "url": ABS + "/firms/" + f["slug"] + "/", "name": f["name"]} for f in RANKED]}]
    page("/", "Compare Prop Firms 2026 — Fees, Rules & Payouts | PropFirmAnalyse", f"Side-by-side data on {len(FIRMS)} crypto, forex and futures prop firms: challenge fees, drawdown, profit split, payout speed and discount codes.", body, ld)

def firms_index():
    c, ld = crumbs([("Home", "/"), ("All firms", "/firms/")])
    body = f'<section class="wrap">{c}<h1>All prop firms</h1><p class="lead">Filter by market, challenge type, account size, platform and your country. Click a firm for full rules and sources.</p>{filters_html()}{table(RANKED)}</section>'
    page("/firms/", f"All {len(FIRMS)} Prop Firms Compared (2026) | PropFirmAnalyse", "Filterable table of prop trading firms with fees, drawdown limits, profit split, platforms and payout frequency.", body, [ld])

def kv(rows):
    return '<dl class="kv">' + "".join(f"<div><dt>{e(k)}</dt><dd>{v}</dd></div>" for k, v in rows) + "</dl>"

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
    if nt is not None: qa.append((f"Can you trade the news with {f['name']}?", {True: "Yes, news trading is allowed per the firm's rules.", False: "No, the firm restricts trading around news events.", "restricted": "Partly — news trading is restricted on some programs or windows. Check the firm's rules page."}[nt]))
    return qa

def firm_page(f):
    c, bl = crumbs([("Home", "/"), ("All firms", "/firms/"), (f["name"], f"/firms/{f['slug']}/")])
    progs = ""
    for p in as_list(f.get("programs")):
        sf = as_list(p.get("sizes_fees"))
        fees = "".join(f"<tr><td>{money(num(x.get('size')))}</td><td>{money(num(x.get('fee')), f.get('fee_currency'))}</td></tr>" for x in sf if num(x.get("size")))
        progs += f"""<div class="prog"><h3>{e(p.get('name') or p.get('type') or 'Program')} <span class="chip">{e(p.get('type') or '')}</span></h3>
{kv([('Profit target', show(p.get('profit_target'))), ('Daily loss', show(p.get('max_daily_loss'))), ('Max drawdown', show(p.get('max_drawdown'))), ('Drawdown type', show(p.get('drawdown_type'))), ('Profit split', show(p.get('profit_split'))), ('Min trading days', show(p.get('min_trading_days')))])}
{('<table class="mini"><thead><tr><th>Account</th><th>Fee</th></tr></thead><tbody>' + fees + '</tbody></table>') if fees else ''}</div>"""
    comps = "".join(f'<div class="bar"><span>{k.title()}</span><i style="--w:{v * 10}%"></i><b>{v:.1f}</b></div>' for k, v in f["_comp"].items())
    dc = f.get("discount_code")
    dch = f'<div class="deal"><span>Public code on {e(f["name"])}\'s site</span>{code_html(f)}</div>' if dc and dc.get("code") else '<p class="muted small">No public discount code found on the firm\'s site at last check.</p>'
    srcs = "".join(f'<li><a href="{e(s)}" rel="nofollow noopener" target="_blank">{e(s)}</a></li>' for s in as_list(f.get("source_urls")))
    pairs = [(a, b) for a, b in PAIRS if f["slug"] in (a, b)]
    others = "".join(f'<a class="chip" href="{url("/compare/" + a + "-vs-" + b + "/")}">vs {e(BY[b if a == f["slug"] else a]["name"])}</a>' for a, b in pairs)
    qa = faq(f)
    faqh = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in qa)
    restricted = as_list(f.get("countries_restricted"))
    body = f"""<section class="wrap">{c}<div class="phead"><span class="av lg">{e(f['name'][:2])}</span><div><h1>{e(f['name'])}</h1>
<p class="muted">{e(f.get('hq') or '')}{' · founded ' + str(int(num(f['founded']))) if num(f.get('founded')) else ''} · {T['last_verified']} {e(f.get('last_verified') or TODAY)}</p></div>
<div class="pscore">{badge_score(f)}<small>PFA Score · #{f['_rank']} of {len(FIRMS)}</small></div></div>
<p class="lead">{e(firm_summary(f))}</p>
<div class="ctas"><a class="btn" href="{e(f.get('affiliate_url') or '#')}" rel="sponsored nofollow noopener" target="_blank" data-firm="{e(f['slug'])}">{T['visit']} →</a>{dch}</div>
<div class="cols"><div><h2>Key rules</h2>{kv([
 ('Markets', show([ASSET_LABEL.get(a, a) for a in f['_assets']])), ('Challenge types', show(f.get('challenge_types'))),
 ('Account sizes', show([money(s) for s in f['_sizes']])), ('Fees from', money(f['_fee'], f.get('fee_currency'))), ('Profit target', show(f.get('profit_target'))),
 ('Daily loss limit', show(f.get('max_daily_loss'))), ('Max drawdown', show(f.get('max_drawdown'))), ('Drawdown type', show(f.get('drawdown_type'))),
 ('Profit split', show(f.get('profit_split'))), ('Split scaling', show(f.get('profit_split_scale'))), ('Leverage', show(f.get('leverage'))),
 ('Platforms', show(f['_platforms'])), ('Payout frequency', show(f.get('payout_frequency'))), ('First payout (days)', show(f.get('first_payout_days'))),
 ('Min trading days', show(f.get('min_trading_days'))), ('Consistency rule', show(f.get('consistency_rule'))), ('News trading', tri_label(f.get('news_trading'))),
 ('Weekend holding', tri_label(f.get('weekend_holding'))), ('Restricted countries', show(restricted) if restricted else ('<span class="na">Not listed</span>')),
 ('Trustpilot', (f"{num(f['trustpilot']['score']):.1f} / 5 from {int(num(f['trustpilot'].get('count') or 0)):,} reviews") if (f.get('trustpilot') or {}).get('score') else (f"<span class=na>No rating shown ({int(num(f['trustpilot']['count'])):,} reviews)</span>" if (f.get('trustpilot') or {}).get('count') else '<span class="na">Not available</span>'))])}</div>
<aside><h2>Score breakdown</h2><div class="bars">{comps}</div><p class="small muted">Data completeness: {f['_complete']}%. Missing inputs score 4/10 by rule. <a href="{url('/methodology/')}">How scoring works</a>.</p>
{('<h3>Compare</h3><div class="chips">' + others + '</div>') if others else ''}</aside></div>
{('<h2>Programs</h2><div class="progs">' + progs + '</div>') if progs else ''}
{('<h2>FAQ</h2><div class="faq">' + faqh + '</div>') if faqh else ''}
<h2>{T['sources']}</h2><p class="small muted">Every figure above was read from these pages on {e(f.get('last_verified') or TODAY)}. Firms change rules often — confirm before you buy.</p><ul class="src">{srcs}</ul>
{('<p class="small muted">Data notes: ' + e(f['notes']) + '</p>') if f.get('notes') else ''}</section>"""
    org = {"@context": "https://schema.org", "@type": ["FinancialService", "Organization"], "name": f["name"], "url": f.get("site"),
           "foundingDate": str(int(num(f["founded"]))) if num(f.get("founded")) else None, "address": f.get("hq")}
    if (f.get("trustpilot") or {}).get("score"):
        org["aggregateRating"] = {"@type": "AggregateRating", "ratingValue": num(f["trustpilot"]["score"]), "bestRating": 5, "reviewCount": int(num(f["trustpilot"].get("count") or 0)), "author": {"@type": "Organization", "name": "Trustpilot"}}
    org = {k: v for k, v in org.items() if v is not None}
    lds = [org, bl]
    if qa: lds.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]})
    desc = f"{f['name']} prop firm rules, fees" + (f" from {money(f['_fee'], f.get('fee_currency'))}" if f['_fee'] is not None else "") + (f", {f['profit_split']} split" if f.get('profit_split') else "") + ", drawdown, payouts and discount code — verified " + str(f.get('last_verified') or TODAY) + "."
    page(f"/firms/{f['slug']}/", f"{f['name']} Review 2026: Rules, Fees & Payouts | PropFirmAnalyse", desc, body, lds, "article")

PAIRS = [("fundedxyz", "hyrotrader"), ("fundedxyz", "breakout-prop"), ("fundedxyz", "crypto-fund-trader"), ("hyrotrader", "breakout-prop"),
 ("hyrotrader", "crypto-fund-trader"), ("breakout-prop", "crypto-fund-trader"), ("ftmo", "fundednext"), ("ftmo", "the5ers"), ("fundednext", "fundingpips"),
 ("ftmo", "fundingpips"), ("the5ers", "fundingpips"), ("e8-markets", "ftmo"), ("apex-trader-funding", "topstep"), ("topstep", "myfundedfutures"), ("apex-trader-funding", "myfundedfutures")]

def compare_rows(a, b):
    R = [("PFA Score", lambda f: badge_score(f), lambda f: f["_score"], 1), ("Trustpilot", tp_html, lambda f: num((f.get("trustpilot") or {}).get("score")), 1),
         ("Founded", lambda f: show(int(num(f["founded"])) if num(f.get("founded")) else None), lambda f: -(num(f.get("founded")) or 9999), 1),
         ("HQ", lambda f: show(f.get("hq")), None, 0), ("Markets", lambda f: show([ASSET_LABEL.get(x, x) for x in f["_assets"]]), lambda f: len(f["_assets"]), 1),
         ("Challenge types", lambda f: show(f.get("challenge_types")), None, 0), ("Entry fee from", lambda f: money(f["_fee"], f.get("fee_currency")), lambda f: -f["_fee"] if f["_fee"] is not None else None, 1),
         ("Cost per $1K allocation", lambda f: money(cost_per_k(f), f.get("fee_currency")), lambda f: -cost_per_k(f) if cost_per_k(f) is not None else None, 1),
         ("Largest account", lambda f: money(max(f["_sizes"])) if f["_sizes"] else "—", lambda f: max(f["_sizes"]) if f["_sizes"] else None, 1),
         ("Profit target", lambda f: show(f.get("profit_target")), None, 0), ("Daily loss limit", lambda f: show(f.get("max_daily_loss")), lambda f: first_pct(f.get("max_daily_loss")), 1),
         ("Max drawdown", lambda f: show(f.get("max_drawdown")), lambda f: first_pct(f.get("max_drawdown")), 1), ("Drawdown type", lambda f: show(f.get("drawdown_type")), None, 0),
         ("Profit split", lambda f: show(f.get("profit_split")), lambda f: f["_split"], 1), ("Leverage", lambda f: show(f.get("leverage")), None, 0),
         ("Platforms", lambda f: show(f["_platforms"]), None, 0), ("Payout frequency", lambda f: show(f.get("payout_frequency")), None, 0),
         ("First payout (days)", lambda f: show(f.get("first_payout_days")), lambda f: -num(f.get("first_payout_days")) if num(f.get("first_payout_days")) is not None else None, 1),
         ("Min trading days", lambda f: show(f.get("min_trading_days")), None, 0), ("Consistency rule", lambda f: show(f.get("consistency_rule")), None, 0),
         ("News trading", lambda f: tri_label(f.get("news_trading")), None, 0), ("Weekend holding", lambda f: tri_label(f.get("weekend_holding")), None, 0),
         ("Discount code", code_html, None, 0)]
    out, wins = "", {a["slug"]: 0, b["slug"]: 0}
    for label, fmt, key, cmp in R:
        ca = cb = ""
        if cmp and key:
            try:
                va, vb = key(a), key(b)
                if va is not None and vb is not None and va != vb:
                    if va > vb: ca = ' class="win"'; wins[a["slug"]] += 1
                    else: cb = ' class="win"'; wins[b["slug"]] += 1
            except Exception: pass
        out += f"<tr><th>{e(label)}</th><td{ca}>{fmt(a)}</td><td{cb}>{fmt(b)}</td></tr>"
    return out, wins

def compare_page(sa, sb):
    a, b = BY.get(sa), BY.get(sb)
    if not a or not b: return
    path = f"/compare/{sa}-vs-{sb}/"
    c, bl = crumbs([("Home", "/"), ("Compare", "/compare/"), (f"{a['name']} vs {b['name']}", path)])
    rows, wins = compare_rows(a, b)
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
        lines.append(f"Overall PFA Score: {a['name']} {a['_score']:.1f} vs {b['name']} {b['_score']:.1f}.")
        return "".join(f"<li>{e(x)}</li>" for x in lines)
    disc = ""
    if "fundedxyz" in (sa, sb): disc = f'<p class="note">Disclosure: PropFirmAnalyse is run by the team behind FundedXYZ. This comparison uses the same data fields and scoring formula as every other page.</p>'
    body = f"""<section class="wrap">{c}<h1>{e(a['name'])} vs {e(b['name'])}</h1><p class="lead">Rule-by-rule comparison from each firm's own website, last verified {e(TODAY)}. Highlighted cells are the stronger figure on that line.</p>{disc}
<div class="vs"><a href="{url('/firms/' + sa + '/')}" class="vsf"><span class="av lg">{e(a['name'][:2])}</span><b>{e(a['name'])}</b>{badge_score(a)}</a><span class="vsx">vs</span><a href="{url('/firms/' + sb + '/')}" class="vsf"><span class="av lg">{e(b['name'][:2])}</span><b>{e(b['name'])}</b>{badge_score(b)}</a></div>
<h2>Quick take</h2><ul class="verdict">{verdict()}</ul>
<div class="tablewrap"><table class="cmp"><thead><tr><th></th><th>{e(a['name'])}</th><th>{e(b['name'])}</th></tr></thead><tbody>{rows}</tbody></table></div>
<div class="ctas two"><a class="btn" href="{e(a.get('affiliate_url') or '#')}" rel="sponsored nofollow noopener" target="_blank">{T['visit']}: {e(a['name'])}</a><a class="btn" href="{e(b.get('affiliate_url') or '#')}" rel="sponsored nofollow noopener" target="_blank">{T['visit']}: {e(b['name'])}</a></div>
<p class="small muted">“Not published” means we could not find the figure on the firm's own site. Sources are listed on each firm page.</p></section>"""
    qa = [(f"Which is cheaper, {a['name']} or {b['name']}?", f"Lowest published entry fee: {a['name']} {money(a['_fee'], a.get('fee_currency'))}, {b['name']} {money(b['_fee'], b.get('fee_currency'))}."),
          (f"Which has the higher profit split, {a['name']} or {b['name']}?", f"{a['name']}: {a.get('profit_split') or 'not published'}; {b['name']}: {b.get('profit_split') or 'not published'}.")]
    ld = [bl, {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": t}} for q, t in qa]}]
    page(path, f"{a['name']} vs {b['name']} (2026): Fees, Rules, Payouts Compared", f"{a['name']} vs {b['name']}: entry fees, drawdown, profit split, payout speed and platforms side by side — verified {TODAY}.", body, ld, "article")

def compare_index():
    c, bl = crumbs([("Home", "/"), ("Compare", "/compare/")])
    opts = "".join(f'<option value="{f["slug"]}">{e(f["name"])}</option>' for f in sorted(FIRMS, key=lambda x: x["name"].lower()))
    cards = "".join(f'<a class="card" href="{url("/compare/" + a + "-vs-" + b + "/")}"><small>{"Crypto" if a in ("fundedxyz","hyrotrader","breakout-prop","crypto-fund-trader") else ("Futures" if "futures" in BY[a]["_assets"] and "forex" not in BY[a]["_assets"] else "Forex / multi")}</small><b>{e(BY[a]["name"])} vs {e(BY[b]["name"])}</b></a>' for a, b in PAIRS if a in BY and b in BY)
    body = f"""<section class="wrap">{c}<h1>Compare prop firms</h1><p class="lead">Pick any two firms for a live side-by-side, or open one of the popular match-ups.</p>
<form class="picker" id="picker" onsubmit="return false"><select id="pa">{opts}</select><span>vs</span><select id="pb">{opts}</select><button class="btn" id="pgo">{T['compare_cta']}</button></form>
<div id="live" class="tablewrap"></div><h2>Popular comparisons</h2><div class="grid3">{cards}</div></section>
<script>window.PFA_FIRMS_URL="{url('/data/firms.json')}";window.PFA_PAIRS={json.dumps([a + '-vs-' + b for a, b in PAIRS])};window.PFA_BASE="{BASE}";</script>"""
    page("/compare/", "Compare Prop Firms Side by Side | PropFirmAnalyse", "Compare any two prop firms on fees, drawdown, profit split, payouts and platforms.", body, [bl])

def discounts():
    c, bl = crumbs([("Home", "/"), ("Discounts", "/discounts/")])
    withc = [f for f in RANKED if (f.get("discount_code") or {}).get("code")]
    without = [f for f in RANKED if not (f.get("discount_code") or {}).get("code")]
    cards = "".join(f"""<div class="dcard"><div class="dh"><span class="av">{e(f['name'][:2])}</span><div><b><a href="{url('/firms/' + f['slug'] + '/')}">{e(f['name'])}</a></b><small>From {money(f['_fee'], f.get('fee_currency'))} · {e(f.get('profit_split') or '')}</small></div>{badge_score(f)}</div>
<p class="dv">{e(f['discount_code'].get('value') or 'Discount')}</p>{code_html(f)}<a class="btn sm" href="{e(f.get('affiliate_url') or '#')}" rel="sponsored nofollow noopener" target="_blank">{T['visit']}</a><small class="muted">Seen on firm's site {e(f.get('last_verified') or TODAY)}</small></div>""" for f in withc)
    body = f"""<section class="wrap">{c}<h1>Prop firm discount codes</h1><p class="lead">Only codes published on each firm's own website are listed. Codes expire — the firm's checkout is the final word.</p>
<div class="dgrid">{cards or '<p>No public codes found at last check.</p>'}</div>
<h2>No public code right now</h2><p class="chips">{''.join(f'<a class="chip" href="{url("/firms/" + f["slug"] + "/")}">{e(f["name"])}</a>' for f in without)}</p></section>"""
    page("/discounts/", f"Prop Firm Discount Codes ({datetime.date.fromisoformat(TODAY).strftime('%B %Y')}) | PropFirmAnalyse", "Current public discount codes for prop firm challenges, checked against each firm's website.", body, [bl])

def best_pages():
    c, bl = crumbs([("Home", "/"), ("Best for", "/best/")])
    cards = "".join(f'<a class="card" href="{url("/best/" + s + "/")}"><b>{e(t)}</b><small>{e(d)}</small><small>{sum(1 for f in FIRMS if fn(f))} firms</small></a>' for s, t, d, fn in BEST)
    page("/best/", "Best Prop Firms by Category | PropFirmAnalyse", "Prop firms grouped by market, challenge type, cost, split and payout speed — ranked by PFA Score.", f'<section class="wrap">{c}<h1>Best prop firms for…</h1><p class="lead">Each list is a data filter over our firm table, ranked by the same PFA Score.</p><div class="grid3">{cards}</div></section>', [bl])
    for s, t, d, fn in BEST:
        fl = [f for f in RANKED if fn(f)]
        c2, bl2 = crumbs([("Home", "/"), ("Best for", "/best/"), (t, f"/best/{s}/")])
        ol = "".join(f'<li><a href="{url("/firms/" + f["slug"] + "/")}"><b>{e(f["name"])}</b></a> {badge_score(f)} <span class="muted small">from {money(f["_fee"], f.get("fee_currency"))} · {e(f.get("profit_split") or "split n/a")} · {e(BUCKET_LABEL.get(f["_bucket"], "payout n/a")) if f["_bucket"] else "payout n/a"}</span></li>' for f in fl)
        body = f'<section class="wrap">{c2}<h1>Best {e(t.lower())} ({YEAR_NOW})</h1><p class="lead">{e(d)} {len(fl)} firms match; ranked by PFA Score.</p><ol class="rank">{ol}</ol>{table(fl)}</section>'
        ld = {"@context": "https://schema.org", "@type": "ItemList", "name": t, "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": ABS + "/firms/" + f["slug"] + "/", "name": f["name"]} for i, f in enumerate(fl)]}
        page(f"/best/{s}/", f"Best {t} {YEAR_NOW} — Ranked | PropFirmAnalyse", f"{len(fl)} {t.lower()} ranked by PFA Score with fees, split and payout data.", body, [bl2, ld])

def methodology():
    c, bl = crumbs([("Home", "/"), ("Methodology", "/methodology/")])
    body = f"""<section class="wrap prose">{c}<h1>How we collect data and score firms</h1>
<div class="note"><b>Ownership disclosure.</b> PropFirmAnalyse is operated by the team behind FundedXYZ; FundedXYZ is scored by the same rules as every other firm. It gets no manual adjustment, no default sort position, and its data is collected with the same checklist.</div>
<h2>Where the numbers come from</h2><p>Every figure is read from the prop firm's own website (pricing, rules, FAQ or help-centre pages) and the date is recorded per firm. Ratings come from the firm's public Trustpilot page. If a firm does not publish a number, we show “Not published” — we never estimate.</p>
<h2>The PFA Score (0–10)</h2><p>One formula, applied mechanically by our build script:</p>
<table class="mini"><thead><tr><th>Component</th><th>Weight</th><th>Inputs</th></tr></thead><tbody>
<tr><td>Trust</td><td>30%</td><td>Trustpilot score (3.0→0, 5.0→full), scaled by review volume (log₁₀ of count)</td></tr>
<tr><td>Cost</td><td>20%</td><td>Cheapest fee per $1,000 of account size across published programs</td></tr>
<tr><td>Rules</td><td>20%</td><td>Daily loss limit, max drawdown, static vs trailing drawdown, news trading, weekend holding, consistency rule</td></tr>
<tr><td>Payout</td><td>20%</td><td>Headline profit split, days to first payout, payout cycle</td></tr>
<tr><td>Track record</td><td>10%</td><td>Years in operation (8+ years = full marks)</td></tr></tbody></table>
<p>Payout cycle uses the firm's headline (first-listed) plan. Fees are compared in the currency the firm prices in (FTMO lists EUR); no FX conversion is applied. Trustpilot profiles that show no rating (e.g. suspended for a guideline breach) count as missing.</p><p>Missing inputs score 4/10 for that component, so withholding information never helps a firm. Each firm page shows its component breakdown and a data-completeness percentage.</p>
<h2>What the score is not</h2><p>It is not a prediction of whether you will pass or get paid, and it is not financial advice. Affiliate relationships do not affect scores or ordering.</p>
<h2>Corrections</h2><p>Firms change rules frequently. If you spot an outdated figure, tell us with a link to the firm's page and we will re-verify. See the <a href="{url('/updates/')}">verification log</a>.</p>
<p class="small muted">The full formula lives in <code>scripts/build.py</code>; the dataset is published at <a href="{url('/data/firms.json')}">/data/firms.json</a>.</p></section>"""
    page("/methodology/", "Methodology & Scoring | PropFirmAnalyse", "How PropFirmAnalyse collects prop firm data and calculates the PFA Score. Ownership disclosure included.", body, [bl])

def about():
    c, bl = crumbs([("Home", "/"), ("About", "/about/")])
    body = f"""<section class="wrap prose">{c}<h1>About PropFirmAnalyse</h1>
<p>PropFirmAnalyse is a data-first comparison of prop trading firms across crypto, forex and futures. We track the rules that decide whether a trader can realistically pass and get paid: fees, drawdown type, profit split, payout cycle and restrictions.</p>
<div class="note"><b>Who runs this site.</b> PropFirmAnalyse is operated by the team behind <a href="{url('/firms/fundedxyz/')}">FundedXYZ</a>, a crypto prop firm. FundedXYZ is listed and scored by exactly the same rules as every other firm — see <a href="{url('/methodology/')}">methodology</a>.</div>
<h2>How we make money</h2><p>Some “Visit site” links may become affiliate links. A firm cannot pay to change its data, score or ranking.</p>
<h2>Contact</h2><p>Corrections and firm data updates: please include a link to the firm's own page that shows the change.</p></section>"""
    ld = {"@context": "https://schema.org", "@type": "Organization", "name": "PropFirmAnalyse", "url": ABS + "/"}
    page("/about/", "About PropFirmAnalyse — Who We Are & Disclosure", "Who runs PropFirmAnalyse, how the site is funded, and our ownership disclosure.", body, [bl, ld])

def updates():
    c, bl = crumbs([("Home", "/"), ("Verification log", "/updates/")])
    rows = "".join(f'<tr><td><a href="{url("/firms/" + f["slug"] + "/")}">{e(f["name"])}</a></td><td>{e(f.get("last_verified") or TODAY)}</td><td>{f["_complete"]}%</td><td>{len(as_list(f.get("source_urls")))}</td></tr>' for f in sorted(FIRMS, key=lambda x: x["name"].lower()))
    body = f'<section class="wrap">{c}<h1>Verification log & rule changes</h1><p class="lead">When each firm was last checked, and how complete its public data is. Rule changes will be logged here as they are detected.</p><div class="tablewrap"><table class="mini"><thead><tr><th>Firm</th><th>Last verified</th><th>Data completeness</th><th>Source pages</th></tr></thead><tbody>{rows}</tbody></table></div></section>'
    page("/updates/", "Prop Firm Rule Changes & Verification Log | PropFirmAnalyse", "When each prop firm's rules were last verified and logged rule changes.", body, [bl])

def not_found():
    open(os.path.join(OUT, "404.html"), "w").write(f'<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><title>Not found</title><link rel=stylesheet href="{url("/assets/site.css")}"><main class="wrap" style="padding:4rem 1rem"><h1>Page not found</h1><p><a class="btn" href="{url("/")}">Back to the comparison</a></p></main>')

def seo_files():
    sm = "".join(f"<url><loc>{ABS}{p}</loc><lastmod>{TODAY}</lastmod></url>" for p in PAGES)
    open(os.path.join(OUT, "sitemap.xml"), "w").write(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>')
    open(os.path.join(OUT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\n\nSitemap: {ABS}/sitemap.xml\n")
    lines = [f"# PropFirmAnalyse", "", "> Data-first comparison of prop trading firms (crypto, forex, futures). Every figure is taken from the firm's own website; unknown values are left blank rather than estimated.",
             "", f"Operated by the team behind FundedXYZ; FundedXYZ is scored with the same formula as every other firm.", "", "## Key pages",
             f"- [All firms]({ABS}/firms/): filterable table", f"- [Methodology]({ABS}/methodology/): PFA Score formula", f"- [Discount codes]({ABS}/discounts/)", f"- [Open dataset (JSON)]({ABS}/data/firms.json)", "", "## Firms"]
    lines += [f"- [{f['name']}]({ABS}/firms/{f['slug']}/): PFA Score {f['_score']}, fee from {money(f['_fee'], f.get('fee_currency'))}, split {f.get('profit_split') or 'n/a'}, verified {f.get('last_verified') or TODAY}" for f in RANKED]
    lines += ["", "## Comparisons"] + [f"- [{BY[a]['name']} vs {BY[b]['name']}]({ABS}/compare/{a}-vs-{b}/)" for a, b in PAIRS if a in BY and b in BY]
    open(os.path.join(OUT, "llms.txt"), "w").write("\n".join(lines) + "\n")
    open(os.path.join(OUT, ".nojekyll"), "w").write("")

if __name__ == "__main__":
    PAIRS[:] = [(a, b) for a, b in PAIRS if a in BY and b in BY]
    if os.path.exists(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT)
    write_assets(); home(); firms_index()
    for f in FIRMS: firm_page(f)
    compare_index()
    for a, b in PAIRS: compare_page(a, b)
    discounts(); best_pages(); methodology(); about(); updates(); not_found(); seo_files()
    print(f"built {len(PAGES)} pages -> {OUT}")
