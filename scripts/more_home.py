# PropAnalyse home v2 (2026-10-31): layout pattern David asked for (PFM-style), in our own design, copy and icons.
#   header  = logo + account-type switch + firm search + language switch, secondary nav row underneath
#   home    = headline + real-figure stat pills, offers carousel (codes read from firms' own sites) + "top rated" side panel,
#             browse tabs, then the ranking table (logo, score + stars, HQ + years, markets, platforms, entry fee, max allocation, promo)
#   /programs/ = every program we track in one table (real data only)
# Exec'd LAST into build.py's namespace (after more_seo.py). Redefines row/TABLE_COLS/visit/home/table/legend; the header is swapped
# on every written page in seo_files() so all page types (EN + /zh/) share it.

HOME_V = "2026-10-31"
FIRM_LOGO_DIR = os.path.join(ROOT, "src", "firms")
FLAG_DIR = os.path.join(ROOT, "src", "flags")
_LOGO_MAN = {}
try: _LOGO_MAN = json.load(open(os.path.join(FIRM_LOGO_DIR, "manifest.json")))
except Exception: pass

# ---------- own stroke icons (24px grid, 1.6 stroke) ----------
SICONS = {
    "firms": '<path d="M3 21h18M5 21V8l7-4.5L19 8v13M9.5 21v-5h5v5M9 11h.01M15 11h.01"/>',
    "list": '<path d="M9 6h11M9 12h11M9 18h11M4.5 6h.01M4.5 12h.01M4.5 18h.01"/>',
    "link": '<path d="M10 14a4.5 4.5 0 0 0 6.4.2l3-3a4.5 4.5 0 0 0-6.4-6.4l-1.2 1.2M14 10a4.5 4.5 0 0 0-6.4-.2l-3 3a4.5 4.5 0 0 0 6.4 6.4l1.2-1.2"/>',
    "shield": '<path d="M12 3.2 19.5 6v5.6c0 4.4-3.1 8-7.5 9.2-4.4-1.2-7.5-4.8-7.5-9.2V6zM8.8 12.2l2.2 2.2 4.3-4.6"/>',
    "trophy": '<path d="M8 20.5h8M12 16.5v4M7 4h10v5.5a5 5 0 0 1-10 0zM17 5.5h2.8V7a3.3 3.3 0 0 1-3.2 3.3M7 5.5H4.2V7a3.3 3.3 0 0 0 3.2 3.3"/>',
    "globe": '<circle cx="12" cy="12" r="8.6"/><path d="M3.6 12h16.8M12 3.4c2.4 2.4 3.6 5.3 3.6 8.6s-1.2 6.2-3.6 8.6c-2.4-2.4-3.6-5.3-3.6-8.6S9.6 5.8 12 3.4z"/>',
    "tag": '<path d="M3.8 12.6V4.4a.6.6 0 0 1 .6-.6h8.2l7.6 7.6a1.4 1.4 0 0 1 0 2l-6.2 6.2a1.4 1.4 0 0 1-2 0zM8.5 8.5h.01"/>',
    "chev-l": '<path d="M14.5 6 8.5 12l6 6"/>', "chev-r": '<path d="M9.5 6l6 6-6 6"/>',
    "check": '<path d="M5 12.5 9.5 17 19 7.5"/>',
    "grid": '<path d="M4 4h7v7H4zM13 4h7v7h-7zM4 13h7v7H4zM13 13h7v7h-7z"/>',
    "book": '<path d="M4 5.5A1.5 1.5 0 0 1 5.5 4H11v16H5.5A1.5 1.5 0 0 1 4 18.5zM20 5.5A1.5 1.5 0 0 0 18.5 4H13v16h5.5a1.5 1.5 0 0 0 1.5-1.5z"/>',
}
def si(n, cls=""):
    return (f'<svg class="si{(" " + cls) if cls else ""}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" '
            f'stroke-linejoin="round" aria-hidden="true" focusable="false">{SICONS[n]}</svg>')

# ---------- firm facts ----------
HQ_GUESS = [(r"\buae\b|united arab emirates|dubai|ajman|ras al khaimah|abu dhabi", "AE"), (r"czech|prague", "CZ"), (r"switzerland|zug", "CH"),
            (r"\buk\b|england|united kingdom|london|harpenden", "GB"), (r"saint lucia", "LC"), (r"\busa\b|, (tx|il|de|fl|ny|ca|wy)\b|texas|chicago|wilmington|austin|dallas", "US"),
            (r"israel", "IL"), (r"cyprus", "CY"), (r"australia", "AU"), (r"hong kong", "HK"), (r"singapore", "SG"), (r"estonia", "EE")]
COUNTRY = {"AE": "UAE", "CZ": "Czechia", "CH": "Switzerland", "GB": "UK", "LC": "Saint Lucia", "US": "USA", "IL": "Israel", "CY": "Cyprus", "AU": "Australia",
           "HK": "Hong Kong", "SG": "Singapore", "EE": "Estonia", "SC": "Seychelles", "MT": "Malta", "NL": "Netherlands", "BG": "Bulgaria", "CA": "Canada",
           "DE": "Germany", "PL": "Poland", "SK": "Slovakia", "SI": "Slovenia", "HU": "Hungary", "IE": "Ireland", "GI": "Gibraltar", "KN": "St Kitts & Nevis",
           "VC": "St Vincent", "KM": "Comoros", "RO": "Romania", "MY": "Malaysia", "VG": "BVI", "KY": "Cayman Islands", "BS": "Bahamas"}
def hq_cc(f):
    c = f.get("hq_country")
    if isinstance(c, dict): c = c.get("code")
    if c: return str(c).upper()
    hq = str(f.get("hq") or "").lower()
    for rx, cc in HQ_GUESS:
        if re.search(rx, hq): return cc
    return None
def founded_y(f): return int(num(f["founded"])) if num(f.get("founded")) else None
def alloc(f):
    """(usd, kind): published max allocation across accounts, else the largest single account (labelled as such)."""
    v = num(f.get("max_allocation_usd"))
    if v: return v, "alloc"
    return (max(f["_sizes"]), "account") if f["_sizes"] else (None, None)
ALLOC_MAX = max([alloc(f)[0] or 0 for f in FIRMS] + [1])
def kfmt(v):
    if v is None: return ""
    if v >= 1_000_000: return "$" + f"{v / 1_000_000:g}M"
    if v >= 1000: return "$" + f"{v / 1000:g}K"
    return "$" + f"{v:g}"

def promo(f):
    dc = f.get("discount_code") or {}
    if not dc.get("code"): return None
    p = dc.get("percent")
    if p is None: p = pct_off(dc)
    return {"code": dc["code"], "pct": p, "value": dc.get("value") or "", "src": dc.get("source") or dc.get("source_url") or "",
            "verified": dc.get("verified") or f.get("last_verified") or TODAY, "expires": dc.get("expires")}
_pct_off_prev = pct_off
def pct_off(dc):
    """Percent for 'price after code'. 'Up to N%' codes vary by product, so no single after-code price is computed."""
    if re.match(r"\s*up to", str((dc or {}).get("value") or ""), re.I): return None
    p = (dc or {}).get("percent")
    return float(p) if isinstance(p, (int, float)) else _pct_off_prev(dc)
def short_date(d):
    try: return datetime.date.fromisoformat(str(d)).strftime("%-d %b")
    except Exception: return str(d)

# ---------- small components ----------
def logo_html(f, px=40, eager=False):
    s = f["slug"]; m = _LOGO_MAN.get(s) or {}
    if os.path.exists(os.path.join(FIRM_LOGO_DIR, s + ".webp")):
        bg = m.get("plate") or m.get("bg") or "#ffffff"
        if bg == "transparent": bg = "#ffffff"
        lz = "" if eager else 'loading="lazy" '
        return (f'<span class="flogo" style="--lb:{e(bg)};width:{px}px;height:{px}px"><img src="{url("/assets/firms/" + s + ".webp")}?v={ASSET_V}" '
                f'srcset="{url("/assets/firms/" + s + "@2x.webp")}?v={ASSET_V} 2x" width="{px}" height="{px}" alt="{e(f["name"])} logo" {lz}decoding="async"></span>')
    ini = "".join(w[0] for w in re.findall(r"[A-Za-z0-9]+", f["name"])[:2]).upper()
    return f'<span class="flogo ini" style="width:{px}px;height:{px}px" role="img" aria-label="{e(f["name"])} logo"><b>{e(ini)}</b></span>'

def stars(score10):
    pct = max(0, min(100, score10 * 10))
    return f'<span class="stars" style="--v:{pct:.0f}%" aria-hidden="true"></span>'
def rate_html(f, big=False):
    s = f["_score"]
    return (f'<span class="rate{" big" if big else ""}" title="PA Score {s:.1f} of 10 (stars show the score on a 5-star scale)"><b class="n">{s:.1f}</b>{stars(s)}'
            f'<span class="sr"> PA Score out of 10</span></span>')

def promo_chip(f, size=""):
    p = promo(f)
    if not p: return None
    upto = bool(re.match(r"\s*up to", p["value"], re.I))
    top = (f'Up to {p["pct"]:g}%' if upto else f'{p["pct"]:g}% off') if p["pct"] else ("Auto-applied" if re.search(r"auto", p["value"], re.I) else "Code")
    t = e(p["value"]) if p["value"] else ""
    tt = f' title="{t}"' if t else ""
    return (f'<div class="promo{(" " + size) if size else ""}"{tt}><b class="pt n">{e(top)}</b>'
            f'<button type="button" class="pc" data-copy="{e(p["code"])}" aria-label="Copy code {e(p["code"])}"><span>{e(p["code"])}</span>{ic("copy")}</button></div>')

def flag_html(cc):
    if not cc: return ""
    if os.path.exists(os.path.join(FLAG_DIR, cc.lower() + ".svg")):
        return f'<img class="flag" src="{url("/assets/flags/" + cc.lower() + ".svg")}" width="20" height="15" alt="" loading="lazy" decoding="async">'
    return f'<span class="flag cc">{e(cc)}</span>'

def years_html(f):
    y = founded_y(f)
    if not y: return ""
    n = max(0, YEAR_NOW - y); frac = min(1, n / 12)
    lab = str(n) if n else "&lt;1"
    return (f'<span class="yrs" title="Founded {y}"><svg viewBox="0 0 36 36" aria-hidden="true"><circle cx="18" cy="18" r="15" class="yt"/>'
            f'<circle cx="18" cy="18" r="15" class="yv" pathLength="100" stroke-dasharray="{frac * 100:.1f} 100"/></svg><b class="n">{lab}</b>'
            f'<span class="sr"> years in business (founded {y})</span></span>')

PLAT_MONO = [("mt5", "MT5", "MetaTrader 5"), ("mt4", "MT4", "MetaTrader 4"), ("ctrader", "cT", "cTrader"), ("matchtrader", "MTR", "Match-Trader"),
             ("dxtrade", "DX", "DXtrade"), ("tradelocker", "TL", "TradeLocker"), ("tradingview", "TV", "TradingView"), ("tradovate", "TDV", "Tradovate"),
             ("ninjatrader", "NT", "NinjaTrader"), ("rithmic", "R", "Rithmic"), ("exchange", "EX", "Exchange account (Bybit, BloFin)"), ("own", "Own", "Firm's own platform")]
def plat_keys(f):
    ks = list(f.get("_pk") or []); blob = " | ".join(f["_platforms"]).lower()
    if "tradelocker" in blob: ks.append("tradelocker")
    if "tradingview" in blob: ks.append("tradingview")
    return [k for k, _, _ in PLAT_MONO if k in ks]
def plats_html(f, n=4):
    ks = plat_keys(f)
    if not ks: return NA
    L = {k: (m, t) for k, m, t in PLAT_MONO}
    full = ", ".join(f["_platforms"])
    items = "".join(f'<li data-p="{k}" title="{e(L[k][1])}">{e(L[k][0])}<span class="sr"> ({e(L[k][1])})</span></li>' for k in ks[:n])
    more = f'<li class="xn" title="{e(full)}">+{len(ks) - n}</li>' if len(ks) > n else ""
    return f'<ul class="pmono" aria-label="Platforms: {e(full)}">{items}{more}</ul>'

def asset_chips(f, n=3):
    mk = [ASSET_LABEL.get(a, a.title()) for a in f["_assets"]]
    if not mk: return NA
    extra = f'<li class="xn" title="{e(", ".join(mk[n:]))}">+{len(mk) - n}</li>' if len(mk) > n else ""
    return '<ul class="achips2">' + "".join(f"<li>{e(m)}</li>" for m in mk[:n]) + extra + "</ul>"

def alloc_html(f):
    v, kind = alloc(f)
    if v is None: return NA
    w = (v / ALLOC_MAX) ** 0.5
    note = "across accounts" if kind == "alloc" else "largest account"
    tt = f' title="{e(f.get("max_allocation_text"))}"' if kind == "alloc" and f.get("max_allocation_text") else ""
    return (f'<span class="alloc"{tt}><b class="n">{kfmt(v)}</b><i class="abar" style="--a:{w:.3f}" aria-hidden="true"></i><small>{note}</small></span>')

def visit(f, label=None, cls="visit"):
    aff = f.get("affiliate_url") if f.get("affiliate_url") not in (None, "", "#") else None
    href = aff or f.get("site") or "#"
    rel = "sponsored nofollow noopener" if aff else "nofollow noopener"
    return (f'<a class="{cls}" href="{e(href)}" rel="{rel}" target="_blank" data-firm="{e(f["slug"])}">'
            f'{e(label or T["visit"])}{ic("ext")}<span class="sr"> (opens {e(f["name"])} in a new tab)</span></a>')

# ---------- ranking table ----------
def row(f, rk=None):
    G = globals()
    v_alloc, _k = alloc(f)
    attrs = {
        "cat": f.get("category") or "", "also": " ".join(as_list(f.get("also_offers"))), "pk": " ".join(f.get("_pk", [])),
        "mk": " ".join(f.get("_mk", [])), "pm": " ".join(f.get("_pm", [])),
        "assets": " ".join(f["_assets"]), "types": " ".join(f["_types"]), "platforms": "|".join(p.lower() for p in f["_platforms"]),
        "fee": f["_fee"] if f["_fee"] is not None else "", "maxsize": max(f["_sizes"]) if f["_sizes"] else "", "alloc": v_alloc or "",
        "split": f["_split"] if f["_split"] is not None else "", "score": f["_score"], "name": f["name"].lower(),
        "news": str(tri(f.get("news_trading"))).lower(), "weekend": str(tri(f.get("weekend_holding"))).lower(),
        "payout": f["_bucket"] or "", "restricted": "|".join(c.lower() for c in as_list(f.get("countries_restricted"))),
        "tp": num((f.get("trustpilot") or {}).get("score")) or "", "founded": num(f.get("founded")) or "",
    }
    da = " ".join(f'data-{k}="{e(v)}"' for k, v in attrs.items())
    cat = G.get("CAT_NAME", {}).get(f.get("category"), "")
    cc = hq_cc(f); y = founded_y(f)
    sub = " · ".join(x for x in (cat, f"est. {y}" if y else "") if x)
    tp = f.get("trustpilot") or {}
    if tp.get("score"):
        tpl = (f'<small class="tpl" title="Trustpilot score and review count">Trustpilot <b class="n">{num(tp["score"]):.1f}</b> · '
               f'<span class="n">{int(num(tp.get("count") or 0)):,}</span></small>')
    else:
        tpl = '<small class="tpl">Trustpilot: no rating</small>' if tp.get("count") else ""
    ctry = (f'<span class="ctry">{flag_html(cc)}<span>{e(COUNTRY.get(cc, cc))}</span></span>' if cc else "") + years_html(f)
    fee = mh(f["_fee"], f.get("fee_currency"))
    split = f'<small>{int(f["_split"])}% split</small>' if f["_split"] else ""
    pc = promo_chip(f) or '<span class="nocode">No public code</span>'
    return f"""<tr {da}><td class="c-firm"><div class="fcell"><span class="rk n">{(rk or f['_rank']):02d}</span>{logo_html(f)}<a href="{url('/firms/' + f['slug'] + '/')}"><b>{e(f['name'])}</b><small>{e(sub)}</small></a></div></td>
<td class="c-sc" data-m="PA Score">{rate_html(f)}{tpl}</td><td class="c-ctry" data-m="HQ · years">{ctry or NA}</td>
<td class="c-mkt" data-m="Markets">{asset_chips(f)}</td><td class="c-plat" data-m="Platforms">{plats_html(f)}</td>
<td class="c-fee num" data-m="Entry fee">{fee}{split}</td><td class="c-alloc" data-m="Max allocation">{alloc_html(f)}</td>
<td class="c-code" data-m="Promo">{pc}</td><td class="c-act">{visit(f)}</td></tr>"""

TABLE_COLS[:] = [("c-firm", "Firm"), ("c-sc", "PA Score"), ("c-ctry", "HQ · years"), ("c-mkt", "Markets"), ("c-plat", "Platforms"),
                 ("c-fee num", "Entry fee"), ("c-alloc", "Max allocation"), ("c-code", "Promo"), ("c-act", '<span class="sr">Link</span>')]
SORT_KEYS.clear(); SORT_KEYS.update({"c-firm": "name", "c-sc": "score", "c-ctry": "founded", "c-fee num": "fee", "c-alloc": "alloc"})
def table(firms, empty=False, local=False):
    head = "".join(th_html(c, t) for c, t in TABLE_COLS)
    emp = (f'<div class="empty" id="empty" hidden><p><b>No firm matches every filter.</b> Loosen one, or start again.</p>'
           f'<button type="button" class="btn line sm" data-reset>{T["filter_reset"]} filters</button></div>') if empty else ""
    return (f'<div class="tablewrap"><table class="firms v2" id="firms"><caption class="sr">Prop firms ranked by PA Score</caption>'
            f'<thead><tr>{head}</tr></thead><tbody>{"".join(row(f, i + 1 if local else None) for i, f in enumerate(firms))}</tbody></table></div>{emp}')

def legend():
    return (f'<p class="legend"><span>{NA} the firm does not publish this figure.</span><span>Stars show the PA Score (0 to 10) on a 5-star scale.</span>'
            f'<span>Max allocation is the firm\'s published cap across accounts; where none is published we show its largest single account.</span>'
            f'<span>One formula scores every firm: <a href="{url("/methodology/")}">methodology</a>.</span></p>')

# ---------- home ----------
def offer_card(f, eager=False):
    p = promo(f)
    fu = url("/firms/" + f["slug"] + "/")
    if p:
        meta = (f'<p class="ometa">{si("check")}<span>Verified <time datetime="{e(p["verified"])}">{short_date(p["verified"])}</time></span>'
                + (f'<a href="{e(p["src"])}" rel="nofollow noopener" target="_blank">Source<span class="sr"> for the {e(f["name"])} code</span></a>' if p["src"] else "")
                + (f'<span class="exp">Ends <time datetime="{e(p["expires"])}">{short_date(p["expires"])}</time></span>' if p.get("expires") else "") + "</p>")
        right = promo_chip(f)
    else:
        meta = '<p class="ometa"><span>No public code at last check</span></p>'
        right = f'<a class="vo" href="{fu}">View offer<span class="sr">: {e(f["name"])}</span></a>'
    return (f'<article class="ocard"><a class="ofirm" href="{fu}">{logo_html(f, 40, eager)}<span class="on"><b>{e(f["name"])}</b>{rate_html(f)}</span></a>'
            f'{right}{meta}</article>')

def top_rated(cat):
    fl = [f for f in RANKED if f.get("category") == cat][:3]
    medal = ["gold", "silver", "bronze"]
    return "".join(f'<li><span class="medal {medal[i]}" title="#{i + 1} by PA Score">{si("trophy")}<span class="sr">Rank {i + 1}</span></span>'
                   f'<a class="ofirm" href="{url("/firms/" + f["slug"] + "/")}">{logo_html(f, 36)}<span class="on"><b>{e(f["name"])}</b>{rate_html(f)}</span></a>'
                   f'{promo_chip(f, "sm") or ""}</li>' for i, f in enumerate(fl))

def home():
    n_prog = sum(len(as_list(f.get("programs"))) for f in FIRMS)
    n_src = sum(len(as_list(f.get("source_urls"))) for f in FIRMS)
    withc = [f for f in RANKED if promo(f)]; without = [f for f in RANKED if not promo(f)]
    month = datetime.date.fromisoformat(TODAY).strftime("%B")
    cards = withc + without[: (-len(withc)) % 6]
    pages_ = [cards[i:i + 6] for i in range(0, len(cards), 6)]
    car = "".join(f'<div class="opage">{"".join(offer_card(f, eager=(pi == 0)) for f in pg)}</div>' for pi, pg in enumerate(pages_))
    dots = "".join(f'<i{" class=on" if i == 0 else ""}></i>' for i in range(len(pages_)))
    pill = lambda icon, v, lab: f'<li>{si(icon)}<b class="n">{v}</b><span>{lab}</span></li>'
    CN = globals().get("CATS", [])
    order = [c for c in CN if c[0] == "crypto-exchange"] + [c for c in CN if c[0] != "crypto-exchange"]
    tr_tabs = "".join(f'<button type="button" class="trt" data-t="{k}" aria-pressed="{"true" if i == 0 else "false"}">{e("Crypto" if k == "crypto-exchange" else nm)}</button>' for i, (k, nm, _) in enumerate(order))
    tr_lists = "".join(f'<ol class="trl" data-t="{k}"{"" if i == 0 else " hidden"} aria-label="Top rated {e(nm.lower())} firms">{top_rated(k)}</ol>' for i, (k, nm, _) in enumerate(order))
    tr_more = "".join(f'<a class="trm" data-t="{k}"{"" if i == 0 else " hidden"} href="{url(p)}">All {e(nm.lower())} firms{ic("arrow")}</a>' for i, (k, nm, p) in enumerate(order))
    lists = "".join(f'<li><a href="{url(p)}"><span>{e(n)} prop firms</span><b class="n">{sum(1 for f in FIRMS if f.get("category") == k)}</b></a></li>' for k, n, p in CN)
    lists += "".join(f'<li><a href="{url("/best/" + s + "/")}"><span>{e(t)}</span><b class="n">{sum(1 for f in FIRMS if fn(f))}</b></a></li>' for s, t, _, fn in BEST)
    pairs = "".join(pair_link(a, b) for a, b in PAIRS[:8])
    ncx = sum(1 for f in FIRMS if f.get("category") == "crypto-exchange")
    body = f"""<section class="hero2"><div class="wrap">
<h1>Compare the best prop trading firms of 2026</h1>
<p class="hsub">Fees, rules and payout terms for {len(FIRMS)} firms, read from each firm's own pages, cited and dated. One published formula ranks them all.</p>
<ul class="hstats" aria-label="About this dataset">{pill("firms", len(FIRMS), "firms tracked")}{pill("list", n_prog, "programs")}{pill("link", n_src, "source pages cited")}{pill("shield", nice_date(TODAY), "last verified")}</ul>
<div class="hgrid">
<section class="opanel" aria-labelledby="off-h"><header class="oh"><span class="ocount">{si("tag")}<b class="n">{len(withc)}</b> live codes</span>
<h2 id="off-h">{e(month)} prop firm offers</h2>
<div class="octl"><button type="button" class="cb" data-d="-1" aria-label="Previous offers" disabled>{si("chev-l")}</button><span class="dots" aria-hidden="true">{dots}</span><button type="button" class="cb" data-d="1" aria-label="Next offers">{si("chev-r")}</button></div></header>
<div class="ocar" id="ocar" tabindex="0" role="region" aria-label="Offers, scroll for more">{car}</div>
<p class="ofoot">Codes are read from each firm's own site on the date shown and never affect a firm's score or rank. <a href="{url('/offers/')}">All offers with prices after code</a></p></section>
<aside class="tpanel" aria-labelledby="tr-h"><header><h2 id="tr-h">{si("trophy")}Top rated firms</h2><div class="trtabs" role="group" aria-label="Account type">{tr_tabs}</div></header>
{tr_lists}<p class="tnote"><span>Ranked by PA Score, not popularity or commission.</span>{tr_more}</p></aside>
</div></div></section>
<nav class="htabs wrap" aria-label="Browse"><a href="#table" aria-current="page">{si("grid")}Firms<small class="n">{len(FIRMS)}</small></a><a href="{url('/programs/')}">{si("list")}Programs<small class="n">{n_prog}</small></a><a href="{url('/offers/')}">{si("tag")}Offers<small class="n">{len(withc)}</small></a><a href="{url('/firms/')}">{si("book")}Reviews</a><a class="hl" href="{url('/crypto-exchange/')}"><span>Crypto exchange firms</span><small class="n">{ncx}</small><em>Our focus</em></a></nav>
<section class="wrap" id="table" aria-label="Firm table"><div class="tmeta"><a class="howv" href="{url('/methodology/')}">{si("shield")}How we verify and rank firms</a><span class="vdot"><i aria-hidden="true"></i>Data verified <time datetime="{e(TODAY)}">{nice_date(TODAY)}</time></span></div>
{filters_html()}{table(RANKED, empty=True)}{legend()}</section>
<section class="wrap lower"><div class="rv"><h2>{e(T['best_for'])}</h2><ul class="lists">{lists}</ul></div>
<div class="rv"><h2>Head to head</h2><ul class="pairs">{pairs}</ul><p><a class="more" href="{url('/compare/')}">Pick any two firms{ic('arrow')}</a></p></div></section>"""
    ld = [{"@context": "https://schema.org", "@type": "WebSite", "name": "PropAnalyse", "url": ABS + "/"},
          {"@context": "https://schema.org", "@type": "ItemList", "name": "Prop firms ranked by PA Score", "itemListElement": [{"@type": "ListItem", "position": f["_rank"], "url": ABS + "/firms/" + f["slug"] + "/", "name": f["name"]} for f in RANKED]}]
    page("/", "Compare Prop Firms 2026: Fees, Rules & Payouts | PropAnalyse", f"Side-by-side data on {len(FIRMS)} crypto, forex and futures prop firms: challenge fees, drawdown, profit split, payout speed and discount codes.", body, ld)

# ---------- /programs/ : every program we track ----------
def programs_page():
    c, bl = crumbs([("Home", "/"), ("Programs", "/programs/")])
    rows = ""; n = 0
    for f in RANKED:
        cur = f.get("fee_currency")
        for p in as_list(f.get("programs")):
            sf = [x for x in as_list(p.get("sizes_fees")) if isinstance(x, dict)]
            sz = sorted(num(x.get("size")) for x in sf if num(x.get("size")))
            fees = [num(x.get("fee")) for x in sf if num(x.get("fee")) is not None]
            szs = (kfmt(sz[0]) + (" to " + kfmt(sz[-1]) if len(sz) > 1 else "")) if sz else NA
            ddv = " / ".join(str(x) for x in (p.get("max_daily_loss"), p.get("max_drawdown")) if x)
            mtd = p.get("min_trading_days")
            dt = f'<small>{e(p["drawdown_type"])}</small>' if p.get("drawdown_type") else ""
            n += 1
            rows += (f'<tr><td class="c-firm"><div class="fcell">{logo_html(f, 28)}<a href="{url("/firms/" + f["slug"] + "/")}"><b>{e(f["name"])}</b></a></div></td>'
                     f'<td>{e(p.get("name") or "")}</td><td class="nowrap">{e(p.get("type") or "") or NA}</td><td class="n nowrap">{szs}</td>'
                     f'<td class="num">{mh(min(fees), cur) if fees else NA}</td><td class="n">{e(p.get("profit_target") or "") or NA}</td>'
                     f'<td class="n">{e(ddv) or NA}{dt}</td><td class="n">{e(p.get("profit_split") or "") or NA}</td>'
                     f'<td class="num n">{e(str(mtd)) if mtd not in (None, "") else NA}</td></tr>')
    cats = " · ".join(f'<a href="{url(pth)}">{e(nm)}</a>' for _, nm, pth in globals().get("CATS", []))
    body = (f'<div class="wrap">{c}<header class="ph"><h1>Prop firm challenges and programs</h1><p class="lede">All <span class="n">{n}</span> programs from the '
            f'<span class="n">{len(FIRMS)}</span> firms we track, one row each: account sizes, cheapest entry fee, profit target, drawdown and split, as published on each firm\'s own site. '
            f'Firms are in PA Score order. Account-type hubs: {cats}.</p></header>'
            f'<div class="tablewrap"><table class="mini progs"><caption class="sr">Prop firm programs</caption><thead><tr><th scope="col">Firm</th><th scope="col">Program</th>'
            f'<th scope="col">Type</th><th scope="col">Sizes</th><th scope="col" class="num">Fee from</th><th scope="col">Target</th><th scope="col">Daily / max loss</th>'
            f'<th scope="col">Split</th><th scope="col" class="num">Min days</th></tr></thead><tbody>{rows}</tbody></table></div>'
            f'<p class="legend"><span>{NA} the firm does not publish this figure.</span><span>Targets show phase 1 / phase 2 where a program has two.</span>'
            f'<span>Full rule sheets and sources are on each firm\'s page.</span></p></div>')
    ld = {"@context": "https://schema.org", "@type": "Dataset", "name": "Prop firm programs", "description": f"{n} prop firm programs with sizes, fees, targets, drawdown and split, from each firm's own site.",
          "url": ABS + "/programs/", "dateModified": TODAY, "creator": {"@type": "Organization", "name": "PropAnalyse"}}
    page("/programs/", f"Prop Firm Challenges Compared (2026): {n} Programs, Fees & Rules | PropAnalyse",
         f"All {n} challenge programs from {len(FIRMS)} prop firms in one table: account sizes, entry fee, profit target, daily and max loss, split and minimum days.", body, [bl, ld])

_nf_prev_home = not_found
def not_found():
    programs_page(); _nf_prev_home()

# ---------- assets ----------
_wa_prev_home = write_assets
def write_assets():
    _wa_prev_home()
    for d, sub, ext in ((FIRM_LOGO_DIR, "firms", (".webp", ".svg")), (FLAG_DIR, "flags", (".svg",))):
        if not os.path.isdir(d): continue
        od = os.path.join(OUT, "assets", sub); os.makedirs(od, exist_ok=True)
        for n_ in os.listdir(d):
            if n_.endswith(ext): shutil.copy(os.path.join(d, n_), os.path.join(od, n_))

# ---------- header: account-type switch + search + language, secondary nav row ----------
SUBNAV_EN = [("/", "Home"), ("/offers/", "Offers"), ("/programs/", "Programs"), ("/compare/", "Compare"), ("/tools/", "Tools"), ("/firms/", "Reviews"),
             ("/legit/", "Legit checks"), ("/news/", "Rule changes"), ("/best/fast-payouts/", "Payouts"), ("/guides/", "Guides")]
def _cur(path, h):
    if h in ("/", "/zh/"): return path == h
    return path.startswith(h)
def header_html(path, zh, alt):
    CN = globals().get("CATS", [])
    if zh:
        cats = [("/zh/", "全部")] + [(CAT_ZH_PATH[k], CAT_ZH_NAME[k].split(" ")[0]) for k, _, _ in CN]
        sub = list(globals().get("ZH_NAV", []))
        lang = f'<div class="lang">{si("globe")}<a href="{url(alt or "/")}" lang="en" hreflang="en">EN</a><span aria-current="true">中文</span></div>'
        srch = ""; home_ = "/zh/"
    else:
        cats = [("/", "All")] + [(p, nm) for k, nm, p in CN]
        sub = SUBNAV_EN
        lang = f'<div class="lang">{si("globe")}<span aria-current="true">EN</span><a href="{url(alt or "/zh/")}" lang="zh-Hans" hreflang="zh-Hans">中文</a></div>'
        opts = "".join(f'<option value="{e(f["name"])}"></option>' for f in RANKED)
        fmap = e(json.dumps({f["name"].lower(): url("/firms/" + f["slug"] + "/") for f in FIRMS}))
        srch = (f'<form class="hsearch" action="{url("/firms/")}" method="get" role="search" data-firms="{fmap}">'
                f'<label><span class="sr">Search firms</span>{ic("search")}<input type="search" name="q" placeholder="Search {len(FIRMS)} firms" list="firmlist" autocomplete="off" spellcheck="false"></label>'
                f'<datalist id="firmlist">{opts}</datalist></form>')
        home_ = "/"
    def catlinks(cls):
        on = [h for h, _ in cats if _cur(path, h)]
        cur = on[-1] if on else (home_ if path in (home_, "/firms/") else None)
        lab = "账户类型" if zh else "Account type"
        return (f'<nav class="catsw {cls}" aria-label="{lab}">' + "".join(f'<a href="{url(h)}"{" aria-current=page" if h == cur else ""}>{e(t)}</a>' for h, t in cats) + "</nav>")
    subl = "".join(f'<a href="{url(h)}"{" aria-current=page" if _cur(path, h) else ""}>{e(t)}</a>' for h, t in sub)
    return (f'<header class="top v2"><div class="wrap bar">{brand()}{catlinks("d")}{srch}{lang}'
            f'<button class="menu" id="menu" type="button" aria-expanded="false" aria-controls="nav"><span class="sr">{"菜单" if zh else "Menu"}</span>{ic("menu", "i-open")}{ic("x", "i-close")}</button></div></header>'
            f'<div class="subbar">{catlinks("m")}<nav class="subnav" id="nav" aria-label="{"主导航" if zh else "Main"}"><div class="wrap">{subl}</div></nav></div>')

_HDR_RX = re.compile(r'<header class="top">.*?</header>', re.S)
def swap_headers():
    for p in list(dict.fromkeys(PAGES)):
        fp = os.path.join(OUT, p.lstrip("/"), "index.html") if p.endswith("/") else os.path.join(OUT, p.lstrip("/"))
        if not os.path.exists(fp): continue
        doc = open(fp).read()
        zh = '<html lang="zh-Hans"' in doc
        mm = re.search(r'<link rel="alternate" hreflang="' + ("en" if zh else "zh-Hans") + r'" href="([^"]+)">', doc)
        alt = (mm.group(1).replace(ABS, "", 1) or "/") if mm else None
        new = _HDR_RX.sub(lambda _: header_html(p, zh, alt), doc, count=1)
        if new != doc: open(fp, "w").write(new)
    fp = os.path.join(OUT, "404.html")
    if os.path.exists(fp):
        doc = open(fp).read(); open(fp, "w").write(_HDR_RX.sub(lambda _: header_html("/404", False, None), doc, count=1))

_seo_prev_home = seo_files
def seo_files():
    _seo_prev_home(); swap_headers()
