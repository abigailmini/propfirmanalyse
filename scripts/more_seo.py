# PropAnalyse SEO content sprint (2026-10-31): richer "best" pages (+ beginners, + zh), 34 compare pairs with written verdicts,
# "Is X legit?" evidence pages for every firm, verification timeline on firm pages, a real /updates/ page, thin-page noindex guard.
# Exec'd last into build.py's namespace. Copy is ours; every number comes from data/*.json at build time.
SPRINT = "2026-10-31"
_PC = json.load(open(os.path.join(ROOT, "data", "payout_claims.json")))
CLAIMS = _PC["firms"]; CLAIM_DATE = _PC.get("checked", SPRINT)
def claim(f): return CLAIMS.get(f["slug"]) or {}
def claim_usd(f): return num(claim(f).get("value_usd"))
def cwhere(c): return c.get("where") or "homepage"
def onchain(c): return c.get("evidence_type") == "on-chain"
def big_usd(v):
    if v is None: return None
    if v >= 1e9: return f"${v / 1e9:.1f}B".replace(".0B", "B")
    if v >= 1e6: return f"${v / 1e6:.1f}M".replace(".0M", "M")
    return money_usd(v) if "money_usd" in globals() else f"${v:,.0f}"
def pmethods(f): return as_list(f["_c"].get("payout_methods") or f["_x"].get("payout_methods"))
def pays_crypto(f): return f["_c"].get("crypto_payout") is True or any(re.search(r"usdt|usdc|crypto|btc|eth|stablecoin", str(m), re.I) for m in pmethods(f))
def kyc(f):
    k = f["_x"].get("kyc_before_payout")
    return k if k is not None else f["_c"].get("kyc_before_payout")
def tp(f): return f.get("trustpilot") or {}
def tps(f): return num(tp(f).get("score"))
def tpc(f): return int(num(tp(f).get("count") or 0) or 0)
def years(f): return (YEAR_NOW - int(num(f["founded"]))) if num(f.get("founded")) else None
def static_dd(f): return "static" in str(f.get("drawdown_type") or "").lower()
def no_consistency(f):
    cr = f.get("consistency_rule")
    return cr is False or str(cr or "").strip().lower() in ("none", "no", "false")
def cheapest_entry(f):
    best = None
    for p in as_list(f.get("programs")):
        for sf in as_list(p.get("sizes_fees")):
            s, v = num(sf.get("size")), num(sf.get("fee"))
            if s and v and (best is None or v < best[2]): best = (p, s, v)
    return best
def fmoney(f, v): return money(v, f.get("fee_currency"))
def P(*xs): return "".join(f"<p>{x}</p>" for x in xs if x)
def UL(xs): return '<ul class="bul">' + "".join(f"<li>{x}</li>" for x in xs) + "</ul>" if xs else ""
def fl_names(fl, n=None): return nlist([f["name"] for f in (fl[:n] if n else fl)])
def a_firm(f): return f'<a href="{url("/firms/" + f["slug"] + "/")}">{e(f["name"])}</a>'
def a_legit(f, t=None): return f'<a href="{url("/firms/" + f["slug"] + "/legit/")}">{e(t or ("Is " + f["name"] + " legit?"))}</a>'
def faq_ld(qa, lang=None):
    d = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", a)}} for q, a in qa]}
    if lang: d["inLanguage"] = lang
    return d
def faq_html(qa): return "".join(f"<details><summary>{e(q)}</summary><p>{a}</p></details>" for q, a in qa)
def article_ld(h, d, path):
    return {"@context": "https://schema.org", "@type": "Article", "headline": h, "description": d, "datePublished": SPRINT, "dateModified": SPRINT,
            "author": {"@type": "Organization", "name": "PropAnalyse", "url": ABS + "/"}, "publisher": {"@type": "Organization", "name": "PropAnalyse"}, "mainEntityOfPage": ABS + path}
def itemlist_ld(name, fl):
    return {"@context": "https://schema.org", "@type": "ItemList", "name": name, "numberOfItems": len(fl),
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": ABS + "/firms/" + f["slug"] + "/", "name": f["name"]} for i, f in enumerate(fl)]}

# ---------------- beginner checklist (documented on /best/beginners/) ----------------
BEGIN_CRIT = [
 ("Entry fee $100 or less", lambda f: f["_fee"] is not None and f["_fee"] <= 100),
 ("Static drawdown on the headline plan", static_dd),
 ("No evaluation time limit", lambda f: f["_x"].get("has_time_limit") is False),
 ("No consistency rule", no_consistency),
 ("Fee refunded on some plan", lambda f: f["_x"].get("fee_refundable") is True),
 ("Trustpilot 4.3+ from 1,000+ reviews", lambda f: (tps(f) or 0) >= 4.3 and tpc(f) >= 1000),
]
def begin_met(f): return [n for n, fn in BEGIN_CRIT if fn(f)]
def BEGINNERS(): return sorted(RANKED, key=lambda f: (-len(begin_met(f)), -f["_score"]))

# ---------------- compare pairs: 15 -> 34, same account type ----------------
PAIRS += [("apex-trader-funding", "bulenox"), ("topstep", "bulenox"), ("myfundedfutures", "bulenox"),
          ("fundednext", "the5ers"), ("ftmo", "alpha-capital"), ("ftmo", "maven-trading"), ("fundingpips", "alpha-capital"), ("fundednext", "e8-markets"),
          ("the5ers", "e8-markets"), ("fundingpips", "maven-trading"), ("goat-funded-trader", "fundingpips"), ("blue-guardian", "fundingpips"),
          ("ftmo", "goat-funded-trader"), ("fundednext", "alpha-capital"), ("ftmo", "blue-guardian"), ("fundednext", "goat-funded-trader"),
          ("bitfunded", "hyrotrader"), ("bitfunded", "breakout-prop"), ("bitfunded", "crypto-fund-trader")]
# 2026-10-31 expansion: most-searched same-account-type rivals of the new firms (pairs whose firms are not listed are dropped in build.py)
PAIRS += [("lucid-trading", "tradeify"), ("fxify", "ftmo"), ("take-profit-trader", "topstep"),
          ("lucid-trading", "apex-trader-funding"), ("lucid-trading", "topstep"), ("tradeify", "apex-trader-funding"), ("tradeify", "topstep"),
          ("take-profit-trader", "apex-trader-funding"), ("take-profit-trader", "myfundedfutures"), ("fxify", "fundednext"), ("fxify", "the5ers"),
          ("propr", "hyrotrader"), ("propr", "fundedxyz"), ("propr", "breakout-prop"), ("hola-prime", "fundingpips"), ("hola-prime", "ftmo"),
          ("fintokei", "ftmo"), ("fintokei", "the5ers"), ("the-trading-pit", "ftmo"), ("the-trading-pit", "fundednext"),
          ("brightfunded", "ftmo"), ("brightfunded", "fundingpips"), ("city-traders-imperium", "ftmo"), ("city-traders-imperium", "the5ers"),
          ("atlas-funded", "ftmo"), ("atlas-funded", "fundednext"), ("ment-funding", "ftmo"), ("for-traders", "ftmo"), ("for-traders", "fundednext"),
          ("thinkcapital", "ftmo"), ("thinkcapital", "fundednext"), ("finotive-funding", "ftmo"), ("finotive-funding", "fundingpips"),
          ("funded-trading-plus", "ftmo"), ("funded-trading-plus", "the5ers"), ("earn2trade", "topstep"), ("earn2trade", "apex-trader-funding"),
          ("earn2trade", "take-profit-trader"), ("elite-trader-funding", "apex-trader-funding"), ("elite-trader-funding", "topstep"),
          ("topone-futures", "apex-trader-funding"), ("topone-futures", "topstep"), ("fondeo", "hyrotrader"), ("fondeo", "fundedxyz"),
          ("mubite", "hyrotrader"), ("mubite", "breakout-prop"), ("propw", "hyrotrader"), ("propw", "crypto-fund-trader"),
          ("tradeday", "topstep"), ("tradeday", "apex-trader-funding"), ("tradeday", "earn2trade"),
          ("daytraders", "topstep"), ("daytraders", "apex-trader-funding"), ("daytraders", "tradeify"),
          ("ftuk", "ftmo"), ("ftuk", "fundednext"), ("ftuk", "instant-funding")]
def pair_group(a): return CAT_LABEL.get(BY[a].get("category"), "Other") + " prop firms"
def pairs_of(slug): return [(a, b) for a, b in PAIRS if slug in (a, b) and a in BY and b in BY]

ORDER = ["daily", "weekly", "biweekly", "monthly", "other"]
def choose_reasons(x, y):
    R = []
    if x["_fee"] is not None and y["_fee"] is not None and x["_fee"] < y["_fee"]: R.append(f"you want the cheaper way in ({fmoney(x, x['_fee'])} vs {fmoney(y, y['_fee'])} for the smallest account)")
    cx, cy = cost_per_k(x), cost_per_k(y)
    if cx is not None and cy is not None and cx < cy * 0.9: R.append(f"you care about cost per $1K of account ({fmoney(x, cx)} vs {fmoney(y, cy)})")
    if x["_split"] and y["_split"] and x["_split"] > y["_split"]: R.append(f"a higher headline split matters ({e(x.get('profit_split'))})")
    if x["_bucket"] in ORDER and y["_bucket"] in ORDER and ORDER.index(x["_bucket"]) < ORDER.index(y["_bucket"]): R.append(f"you want a faster payout cycle ({BUCKET_LABEL[x['_bucket']].lower()})")
    if static_dd(x) and not static_dd(y) and y.get("drawdown_type"): R.append(f"you prefer a static drawdown floor ({e(y['name'])} uses {e(y['drawdown_type'])})")
    if tri(x.get("news_trading")) is True and tri(y.get("news_trading")) is not True: R.append("you trade high-impact news")
    if tri(x.get("weekend_holding")) is True and tri(y.get("weekend_holding")) is not True: R.append("you hold positions over the weekend")
    if no_consistency(x) and not no_consistency(y) and y.get("consistency_rule"): R.append("you do not want a consistency rule")
    if x["_x"].get("has_time_limit") is False and y["_x"].get("has_time_limit") is True: R.append("you do not want an evaluation deadline")
    if x["_x"].get("fee_refundable") is True and y["_x"].get("fee_refundable") is not True: R.append("you want the fee back when you get paid")
    px = {p.lower() for p in x["_platforms"]}; py = {p.lower() for p in y["_platforms"]}
    clean = lambda p: re.sub(r"\s*\(.*?\)", "", str(p)).strip()
    py = {clean(p).lower() for p in y["_platforms"]}
    only = [clean(p) for p in x["_platforms"] if clean(p).lower() not in py and "propriet" not in p.lower() and x["name"].split()[0].lower() not in p.lower() and len(clean(p)) <= 24]
    if only and py: R.append("you need " + e(nlist(only[:3])))
    if tpc(x) >= 1000 and tpc(x) > 3 * max(tpc(y), 1) and (tps(x) or 0) >= 4.0: R.append(f"review volume matters to you ({tpc(x):,} Trustpilot reviews vs {tpc(y):,})")
    if years(x) and (not years(y) or years(x) >= years(y) + 3): R.append(f"you want the longer track record (operating since {int(num(x['founded']))})")
    if claim_usd(x) and (not claim_usd(y) or claim_usd(x) >= 2 * claim_usd(y)): R.append(f"you weigh firm-reported payouts ({e(claim(x)['text'])})")
    return R[:6]

def size_table(a, b):
    from_a = {num(sf.get("size")) for p in as_list(a.get("programs")) for sf in as_list(p.get("sizes_fees")) if num(sf.get("size"))}
    from_b = {num(sf.get("size")) for p in as_list(b.get("programs")) for sf in as_list(p.get("sizes_fees")) if num(sf.get("size"))}
    both = sorted(from_a & from_b)
    if not both: return "", 0
    rows = ""
    for s in both:
        fa, fb = fee_at(a, s), fee_at(b, s)
        wa = fa is not None and fb is not None and fa < fb and a.get("fee_currency") == b.get("fee_currency")
        wb = fa is not None and fb is not None and fb < fa and a.get("fee_currency") == b.get("fee_currency")
        rows += (f'<tr><th scope="row" class="num n">{money(s)}</th><td class="num n{" lo" if wa else ""}">{fmoney(a, fa) if fa else NIL}</td>'
                 f'<td class="num n{" lo" if wb else ""}">{fmoney(b, fb) if fb else NIL}</td></tr>')
    cur = ' <span class="small">FTMO prices in EUR; no FX conversion is applied.</span>' if "EUR" in (a.get("fee_currency"), b.get("fee_currency")) else ""
    return (f'<p class="small">Cheapest program each firm sells at the sizes both offer.{cur}</p><div class="tablewrap"><table class="mini matrix"><thead><tr><th scope="col" class="num">Account</th>'
            f'<th scope="col" class="num">{e(a["name"])}</th><th scope="col" class="num">{e(b["name"])}</th></tr></thead><tbody>{rows}</tbody></table></div>'), len(both)

_compare_page_orig = compare_page
def compare_page(sa, sb):
    _compare_page_orig(sa, sb)
    a, b = BY.get(sa), BY.get(sb)
    if not a or not b: return
    path = f"/compare/{sa}-vs-{sb}/"
    ra, rb = choose_reasons(a, b), choose_reasons(b, a)
    lead = a if a["_score"] > b["_score"] else b; other = b if lead is a else a
    gap = abs(a["_score"] - b["_score"])
    cl = "a close call on our score" if gap < 0.3 else ("a clear but not huge gap" if gap < 1 else "a wide gap")
    same = a.get("category") == b.get("category")
    intro = (f"{e(lead['name'])} scores {lead['_score']:.1f}/10 and {e(other['name'])} {other['_score']:.1f}/10, {cl}. "
             + (f"Both are {CAT_LABEL.get(a.get('category'), '') if a.get('category') == 'cfd' else CAT_LABEL.get(a.get('category'), '').lower()} prop firms, so the rule differences below are like for like. " if same else "")
             + "Which one is better depends on how you trade, so here is who each firm suits, based only on what they publish.")
    pick = (f'<div class="pc"><div><h3>Pick {e(a["name"])} if</h3><ul class="pros">{"".join("<li>" + ic("plus") + "<span>" + x + "</span></li>" for x in ra) or "<li><span>No published figure clearly favours it.</span></li>"}</ul></div>'
            f'<div><h3>Pick {e(b["name"])} if</h3><ul class="pros">{"".join("<li>" + ic("plus") + "<span>" + x + "</span></li>" for x in rb) or "<li><span>No published figure clearly favours it.</span></li>"}</ul></div></div>')
    st, nsz = size_table(a, b)
    def pay(f):
        c = claim(f); pm = pmethods(f)
        bits = [f"<b>{e(f['name'])}</b>: {e(f.get('payout_frequency') or 'payout cycle not published')}."]
        if num(f.get("first_payout_days")) is not None: bits.append(f"First payout after {int(num(f['first_payout_days']))} days.")
        if pm: bits.append("Methods: " + e(", ".join(map(str, pm[:5]))) + ".")
        if c.get("text"): bits.append(f'The firm reports "{e(c["text"])}" (<a href="{e(c["source"])}" rel="nofollow noopener" target="_blank">homepage</a>, checked {nice_date(CLAIM_DATE)}).')
        return " ".join(bits)
    chg = [x for x in CHANGES if x["slug"] in (sa, sb) and x["field"] != "Listing"][:8]
    hist = change_table(chg) if chg else '<p class="small">No rule changes logged for either firm since tracking began. Any change will show here and on the <a href="' + url("/news/") + '">rule-change log</a>.</p>'
    bm = [n for n, fn in BEGIN_CRIT if fn(a)], [n for n, fn in BEGIN_CRIT if fn(b)]
    lists = [(s, t) for s, t, d, fn in BEST if fn(a) and fn(b)]
    more = [p for p in PAIRS if p != (sa, sb) and (sa in p or sb in p) and p[0] in BY and p[1] in BY][:6]
    rel = ("".join(f'<li><a href="{url("/best/" + s + "/")}">{e(BEST_H1.get(s, t))}</a></li>' for s, t in lists[:4])
           + "".join(f'<li><a href="{url("/compare/" + x + "-vs-" + y + "/")}">{e(BY[x]["name"])} vs {e(BY[y]["name"])}</a></li>' for x, y in more))
    qa = [(f"Which is cheaper, {a['name']} or {b['name']}?", f"Smallest published entry fee: {a['name']} {fmoney(a, a['_fee'])}, {b['name']} {fmoney(b, b['_fee'])}." + (f" Cheapest per $1K of account: {a['name']} {fmoney(a, cost_per_k(a))}, {b['name']} {fmoney(b, cost_per_k(b))}." if cost_per_k(a) and cost_per_k(b) else "")),
          (f"Which pays out faster, {a['name']} or {b['name']}?", f"{a['name']}: {a.get('payout_frequency') or 'not published'}. {b['name']}: {b.get('payout_frequency') or 'not published'}."),
          (f"Which has the higher profit split?", f"{a['name']}: {a.get('profit_split') or 'not published'}; {b['name']}: {b.get('profit_split') or 'not published'}. Headline splits often need scaling or an add-on."),
          (f"Which is better for beginners, {a['name']} or {b['name']}?", f"On our six-point beginner checklist {a['name']} meets {len(bm[0])} and {b['name']} meets {len(bm[1])}. The checklist is explained on the best prop firms for beginners page."),
          (f"Are {a['name']} and {b['name']} legit?", f"Both publish their rules and are listed with sources. See the evidence pages: propanalyse.com/firms/{sa}/legit/ and propanalyse.com/firms/{sb}/legit/.")]
    extra = f"""<div class="wrap cmore"><section class="block"><h2>Which should you choose?</h2><div class="prose">{P(intro)}</div>{pick}</section>
{('<section class="block"><h2>Price at each account size</h2>' + st + '</section>') if st else ''}
<section class="block"><h2>Payouts</h2><div class="prose">{P(pay(a), pay(b))}<p class="small">Firm-reported payout totals are the firms' own figures. We have not audited them.</p></div></section>
<section class="block"><h2>Rule changes</h2>{hist}</section>
<section class="block"><h2>Legit check</h2><div class="prose">{P("Track record, review volume, payout terms and restrictions for each firm, on one page each: " + a_legit(a) + " · " + a_legit(b))}</div></section>
<section class="block faq"><h2>FAQ</h2>{faq_html(qa)}</section>
{('<aside class="grel"><h2>Related</h2><ul class="lists">' + rel + '</ul></aside>') if rel else ''}</div>"""
    _patch_page(path, before="</main>", html=extra, ld=[faq_ld(qa)], strip_faq=True,
                title=f"{a['name']} vs {b['name']} ({YEAR_NOW}): Fees, Rules & Payouts Compared | PropAnalyse",
                desc=f"{a['name']} vs {b['name']}: entry fees at every size, drawdown, profit split, payout speed and who each firm suits. Data from each firm's site, verified {nice_date(TODAY)}.")

def _patch_page(path, before=None, html="", ld=None, strip_faq=False, title=None, desc=None, after=None):
    p = os.path.join(OUT, path.lstrip("/"), "index.html")
    t = open(p).read()
    if strip_faq: t = re.sub(r'<script type="application/ld\+json">\{"@context": "https://schema.org", "@type": "FAQPage".*?</script>', "", t, flags=re.S)
    if ld: t = t.replace("</head>", "".join('<script type="application/ld+json">' + json.dumps(j, ensure_ascii=False) + "</script>" for j in ld) + "</head>", 1)
    if title:
        t = re.sub(r"<title>.*?</title>", f"<title>{e(title)}</title>", t, count=1)
        t = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{e(title)}">', t, count=1)
    if desc:
        t = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{e(desc)}">', t, count=1)
        t = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{e(desc)}">', t, count=1)
    if html:
        if after and after in t: t = t.replace(after, after + html, 1)
        elif before and before in t: t = t.replace(before, html + before, 1)
    open(p, "w").write(t)

# ---------------- "best" pages: keep URLs + table, add answer, picks, method, FAQ ----------------
BEST.append(("beginners", "Prop firms for beginners", "Scored on a six-point beginner checklist: low fee, static drawdown, no deadline, no consistency rule, fee refund, review record.", lambda f: len(begin_met(f)) >= 3))
BEST_H1 = {"crypto": "Prop firms that allow crypto trading", "forex": "Best forex prop firms", "futures": "Best futures prop firms", "one-step": "Best 1-step challenge prop firms",
           "instant-funding": "Best instant funding prop firms", "cheap-challenges": "Cheapest prop firms", "high-profit-split": "Highest profit split prop firms",
           "news-trading": "Prop firms that allow news trading", "fast-payouts": "Prop firms with daily and weekly payouts", "mt5": "Best MT5 prop firms", "beginners": "Best prop firms for beginners"}
BEST_TITLE = {"crypto": "Prop Firms That Allow Crypto Trading ({y}): {n} Ranked", "forex": "Best Forex Prop Firms {y}: {n} Ranked by Fees & Rules",
              "futures": "Best Futures Prop Firms {y}: {n} Compared", "one-step": "Best 1-Step Challenge Prop Firms {y}: {n} Ranked",
              "instant-funding": "Best Instant Funding Prop Firms {y}: No-Evaluation Accounts Compared", "cheap-challenges": "Cheapest Prop Firms {y}: {n} Challenges Under $100",
              "high-profit-split": "Highest Profit Split Prop Firms {y}: 90% to 100% Splits Compared", "news-trading": "Prop Firms That Allow News Trading ({y})",
              "fast-payouts": "Prop Firms With Daily & Weekly Payouts ({y})", "mt5": "Best MT5 Prop Firms {y}: {n} Ranked", "beginners": "Best Prop Firms for Beginners {y}: 6-Point Checklist"}
def best_copy(s, fl):
    """returns answer, facts, sections, qa for one best list"""
    top = fl[:3]; n = len(fl)
    ch = min((f for f in fl if f["_fee"] is not None), key=lambda f: f["_fee"], default=None)
    fast = [f for f in fl if f["_bucket"] == "daily"]
    cats = {k: [f for f in fl if f.get("category") == k] for k in CAT_LABEL}
    catline = ", ".join(f"{len(v)} {CAT_LABEL[k].lower()}" for k, v in cats.items() if v)
    ans = f"{n} of the {len(FIRMS)} firms we track qualify. The top three on PA Score are {fl_names(top)}" + (f"; the cheapest entry is {ch['name']} at {fmoney(ch, ch['_fee'])}" if ch else "") + "."
    facts = [f'<b class="n">{n}</b> firms', f"{catline}" if catline else "", (f'cheapest <b class="n">{fmoney(ch, ch["_fee"])}</b>' if ch else ""), f'<b class="n">{len(fast)}</b> with daily payouts']
    picks = "".join(f"<li><b>{a_firm(f)}</b> ({f['_score']:.1f}/10, #{f['_rank']} overall). {e(verdict(f).split('. ')[1] if '. ' in verdict(f) else '')}.</li>" for f in top)
    secs = [("Top picks, explained", f'<ol class="bul">{picks}</ol>')]
    qa = []
    if s == "crypto":
        ce = cats["crypto-exchange"]; cf = [f for f in fl if f.get("category") != "crypto-exchange"]
        ans = (f"{n} firms we track let you trade crypto. {len(ce)} run crypto-exchange accounts (perpetuals priced from exchange data): {fl_names(ce)}. "
               f"The other {len(cf)} list crypto as CFDs next to forex, led by {cf[0]['name'] if cf else 'none'}. Highest PA Score overall: {fl[0]['name']} ({fl[0]['_score']:.1f}/10).")
        secs.append(("Exchange account or crypto CFD?", P("A crypto-exchange prop account gives you perpetual futures with funding rates, more pairs and 24/7 trading. A CFD firm quotes a handful of coins on MT5 or cTrader, usually with lower leverage and weekend limits.",
                     f'For the crypto-only ranking, see the <a href="{url("/guides/best-crypto-prop-firms/")}">best crypto prop firms guide</a> and the <a href="{url("/crypto-exchange/")}">crypto exchange hub</a>.')))
        qa += [("Which prop firms let you trade crypto?", ans), ("Do crypto prop firms pay in USDT?", f"{sum(1 for f in fl if pays_crypto(f))} of these {n} firms list a crypto payout method. Per-firm detail is in our USDT payouts guide.")]
    elif s == "cheap-challenges":
        byfee = sorted([f for f in fl if f["_fee"] is not None], key=lambda f: f["_fee"])
        rows = gtable(byfee, [("#", lambda f: f'<span class="n">{byfee.index(f) + 1}</span>', "n"), FIRMCOL, ("Entry fee", lambda f: fmoney(f, f["_fee"]), "num n"),
                              ("For", lambda f: money(cheapest_entry(f)[1]) if cheapest_entry(f) else NIL, "num n"), ("Per $1K", lambda f: fmoney(f, cost_per_k(f)) if cost_per_k(f) else NIL, "num n"), SCORECOL], "Cheapest prop firm entry fees")
        lo = byfee[0] if byfee else None
        cpk = min((f for f in fl if cost_per_k(f)), key=cost_per_k, default=None)
        ans = (f"The cheapest prop firm entry we track is {lo['name']} at {fmoney(lo, lo['_fee'])}" + (f" for a {money(cheapest_entry(lo)[1])} account" if cheapest_entry(lo) else "") + f". {n} firms sell a challenge for $100 or less. "
               + (f"Per $1K of account the cheapest is {cpk['name']} at {fmoney(cpk, cost_per_k(cpk))}, which matters more than the sticker price once you size up." if cpk else "")) if lo else ans
        secs.insert(0, ("Cheapest first", rows))
        secs.append(("Sticker price vs real cost", P("The lowest fee usually buys the smallest account. Compare cost per $1K and the reset price, then run your own pass rate through the " + f'<a href="{url("/tools/true-cost/")}">true-cost calculator</a>.',
                     f'Price at one size: <a href="{url("/sizes/10k/")}">$10K</a> · <a href="{url("/sizes/50k/")}">$50K</a> · <a href="{url("/sizes/100k/")}">$100K</a>.')))
        qa += [("What is the cheapest prop firm?", ans), ("Is the cheapest prop firm the best value?", "Not always. A low fee on a small account can cost more per $1K than a mid-size plan, and resets add up. Compare cost per $1K and refund terms.")]
    elif s == "instant-funding":
        sp = [f for f in fl if re.search(r"instant", str(f.get("profit_split") or ""), re.I)]
        ans = f"{n} firms we track sell instant funding (a funded account with no evaluation). The top three on PA Score are {fl_names(top)}" + (f", and the cheapest instant-capable firm starts at {fmoney(ch, ch['_fee'])} ({ch['name']}; that price may be for its evaluation, see the firm page)." if ch else ".")
        secs.append(("What instant accounts give up", P("Instant accounts skip the evaluation, so firms price the risk elsewhere: a higher fee per $1K, a lower split, a consistency rule or a tighter drawdown. " +
                     (f"In our data {fl_names(sp)} publish a different split for instant accounts." if sp else "Check whether the split and drawdown on the instant plan match the headline figures."),
                     "Read the instant program's own rules on the firm page; headline figures usually describe the evaluation route.")))
        qa += [("Which prop firms offer instant funding?", ans), ("Is instant funding worth it?", "It saves time, not money. You pay more up front for the same buying power, so it suits traders confident in their risk control.")]
    elif s == "high-profit-split":
        hundred = [f for f in fl if (f["_split"] or 0) >= 100]
        ans = f"{n} firms advertise a profit split of 90% or more; {len(hundred)} reach 100%: {fl_names(hundred) if hundred else 'none'}. Most headline splits are a ceiling reached through scaling or a paid add-on, not the starting rate."
        rows = gtable(fl, [FIRMCOL, ("Headline split", lambda f: show(f.get("profit_split")), ""), ("How you get there", lambda f: show(f.get("profit_split_scale")), "wide"), SCORECOL], "Profit split terms")
        secs.insert(0, ("Split terms by firm", rows))
        qa += [("Which prop firm has the highest profit split?", ans), ("Do you get the 100% split from day one?", "Rarely. Check the scaling column: most firms start at 80% and raise it after payouts or charge for the upgrade.")]
    elif s == "fast-payouts":
        wk = [f for f in fl if f["_bucket"] == "weekly"]
        fd = sorted([f for f in fl if num(f.get("first_payout_days")) is not None], key=lambda f: num(f["first_payout_days"]))
        ans = (f"{len(fast)} firms we track pay daily or on demand ({fl_names(fast)}) and {len(wk)} pay weekly. "
               + (f"The shortest published wait for a first payout is {fd[0]['name']} at {int(num(fd[0]['first_payout_days']))} days." if fd else ""))
        rows = gtable(fl, [FIRMCOL, ("Cycle", lambda f: e(BUCKET_LABEL.get(f["_bucket"], "")) or NIL, ""), ("First payout (days)", lambda f: show(f.get("first_payout_days")), "num n"), ("Terms", lambda f: show(f.get("payout_frequency")), "wide")], "Payout cycles")
        secs.insert(0, ("Payout terms by firm", rows))
        secs.append(("More on payout speed", P(f'The <a href="{url("/guides/fastest-payout-prop-firms/")}">fastest payout guide</a> covers minimum payouts, caps and the rules that slow the first withdrawal.')))
        qa += [("Which prop firms pay out daily?", ans), ("Does on-demand mean instant?", "No. On-demand means you can request any time; processing still takes hours to a few business days, and KYC comes first.")]
    elif s == "beginners":
        rows = gtable(fl, [("#", lambda f: f'<span class="n">{fl.index(f) + 1}</span>', "n"), FIRMCOL, ("Checklist", lambda f: f'<b class="n">{len(begin_met(f))}</b>/6', "n"),
                           ("Meets", lambda f: e(", ".join(begin_met(f))), "wide"), ("From", lambda f: fmoney(f, f["_fee"]) if f["_fee"] is not None else NIL, "num n"), SCORECOL], "Beginner checklist")
        ans = (f"The best prop firms for beginners on our checklist are {fl_names(top)}, each meeting {len(begin_met(top[0]))} or more of six beginner-friendly rules. "
               f"{n} firms meet at least three. The checklist favours rules that forgive mistakes (static drawdown, no deadline, no consistency rule) and a cheap, refundable first attempt.") if top else ans
        secs.insert(0, ("Checklist ranking", rows))
        secs.append(("The six checks", UL([e(nm) for nm, _ in BEGIN_CRIT]) + P("A firm that does not publish a rule does not get the point. Ties are broken by PA Score. The checklist is separate from the PA Score and does not change it.")))
        secs.append(("Habits that matter more than the firm", P("Start with the smallest account, risk well under the daily limit per trade, and read the firm's prohibited-strategy list before your first trade. Most failed first challenges break the daily loss rule, not the profit target.",
                     f'Use the <a href="{url("/tools/drawdown/")}">drawdown calculator</a> to see how much room you really have.')))
        qa += [("What is the best prop firm for beginners?", ans), ("Should a beginner pick a 1-step or 2-step challenge?", "Two-step challenges usually have wider drawdown and lower targets per phase, which forgives mistakes. One-step is faster but stricter.")]
    elif s == "futures":
        acts = [f for f in fl if num(f["_x"].get("activation_fee"))]
        ans = f"{n} firms we track fund futures: {len(cats['futures'])} are futures-first ({fl_names(cats['futures'])}) and the rest sell a futures product next to CFDs. Top on PA Score: {fl_names(top)}."
        secs.append(("Costs futures firms add", P("Futures evaluations are often monthly subscriptions, and some firms charge an activation fee after you pass" + (f" (in our data: {fl_names(acts)})" if acts else "") + ". Most use trailing or end-of-day drawdown, so read the drawdown type before the price.",
                     f'Compare: <a href="{url("/guides/cheapest-futures-prop-firm-50k/")}">cheapest $50K futures evaluation</a> · <a href="{url("/futures/")}">futures hub</a>.')))
        qa += [("What is the best futures prop firm?", ans)]
    elif s == "one-step":
        ans = f"{n} firms sell a 1-step challenge: one profit target, then funded. Top on PA Score: {fl_names(top)}" + (f"; cheapest entry {ch['name']} at {fmoney(ch, ch['_fee'])}." if ch else ".")
        secs.append(("1-step vs 2-step", P(f'One phase is faster but the drawdown is usually tighter. The numbers are in <a href="{url("/guides/one-step-vs-two-step-challenge/")}">one-step vs two-step</a>.')))
        qa += [("Which prop firms have a 1-step challenge?", ans)]
    elif s == "news-trading":
        ans = f"{n} firms we track allow trading through high-impact news on their headline rules: {fl_names(fl)}. Others restrict it on funded accounts only, so check the program you buy."
        secs.append(("How news rules usually work", P(f'Restrictions tend to bar opening or closing trades a few minutes either side of red-folder events. Details: <a href="{url("/guides/prop-firms-that-allow-news-trading/")}">news trading guide</a>.')))
        qa += [("Which prop firms allow news trading?", ans)]
    elif s == "mt5":
        ans = f"{n} firms we track offer MetaTrader 5. Top on PA Score: {fl_names(top)}" + (f"; cheapest entry {ch['name']} at {fmoney(ch, ch['_fee'])}." if ch else ".")
        secs.append(("Other platforms", P(f'See every platform: <a href="{url("/platforms/")}">prop firms by platform</a>.')))
        qa += [("Which prop firms use MT5?", ans)]
    elif s == "forex":
        ans = f"{n} firms we track list forex pairs. Top on PA Score: {fl_names(top)}" + (f"; cheapest entry {ch['name']} at {fmoney(ch, ch['_fee'])}." if ch else ".")
        secs.append(("What separates forex firms", P(f"Most forex firms look alike on fees. The differences are drawdown type, news and weekend rules, and how fast you can get paid. {len(fast)} of these pay daily or on demand.", f'See the <a href="{url("/cfd/")}">CFD hub</a> for the full ranking.')))
        qa += [("What is the best forex prop firm?", ans)]
    secs.append(("How this list is built", P(f"Filter: {e(next(d for s2, t, d, fn in BEST if s2 == s))} Order: PA Score (trust 30%, cost 20%, rules 20%, payout 20%, track record 10%), unless the table says otherwise. Data was read from each firm's own site; last full verification {nice_date(TODAY)}. FundedXyz is run by our team and scored the same way.",
                 f'Rule changes appear on the <a href="{url("/news/")}">change log</a> within one build.')))
    qa.append(("How often is this list updated?", f"Every build re-reads our dataset. Firms were last verified on {nice_date(TODAY)}; changes are logged with dates on the rule-change page."))
    return ans, [x for x in facts if x], secs, qa

def best_pages():
    c, bl = crumbs([("Home", "/"), ("Best for", "/best/")])
    items = "".join(f'<li><a href="{url("/best/" + s + "/")}"><b>{e(BEST_H1.get(s, t))}</b><span>{e(d)}</span><span class="cnt"><b class="n">{sum(1 for f in FIRMS if fn(f))}</b> firms</span>{ic("arrow")}</a></li>' for s, t, d, fn in BEST)
    page("/best/", f"Best Prop Firms {YEAR_NOW} by Category: Cheapest, Crypto, Instant, Beginners | PropAnalyse", "Best prop firm lists by market, challenge type, cost, profit split, payout speed and beginner fit, ranked by a published score.",
         f'<div class="wrap">{c}<header class="ph"><h1>Best prop firms for…</h1><p class="lede">Each list is a filter over the same firm table, ranked by the same PA Score. Every list says how it was built.</p></header><ul class="shortlists">{items}</ul></div>', [bl])
    for s, t, d, fn in BEST:
        fl = BEGINNERS() if s == "beginners" else [f for f in RANKED if fn(f)]
        fl = [f for f in fl if fn(f)]
        path = f"/best/{s}/"; h1 = BEST_H1.get(s, "Best " + t.lower()) + f" ({YEAR_NOW})"
        c2, bl2 = crumbs([("Home", "/"), ("Best for", "/best/"), (BEST_H1.get(s, t), path)])
        ans, facts, secs, qa = best_copy(s, fl)
        sh = "".join(f'<section class="gsec"><h2>{e(h)}</h2>{b}</section>' for h, b in secs)
        cmp = [(a, b) for a, b in PAIRS if a in BY and b in BY and fn(BY[a]) and fn(BY[b])][:6]
        rel = ("".join(f'<li><a href="{url("/compare/" + a + "-vs-" + b + "/")}"><span>{e(BY[a]["name"])} vs {e(BY[b]["name"])}</span></a></li>' for a, b in cmp)
               + "".join(f'<li><a href="{url("/firms/" + f["slug"] + "/legit/")}"><span>Is {e(f["name"])} legit?</span></a></li>' for f in fl[:3])
               + "".join([f'<li><a href="{url("/best/" + s2 + "/")}"><span>{e(BEST_H1.get(s2, t2))}</span></a></li>' for s2, t2, _, _ in BEST if s2 != s][:5]))
        zp = ZH_ALT.get(path)
        body = (f'<div class="wrap">{c2}<header class="ph"><h1>{e(h1)}</h1><p class="meta"><span>Data verified <time datetime="{TODAY}">{nice_date(TODAY)}</time></span><span>{len(FIRMS)} firms, read from their own sites</span>'
                + (f'<span><a href="{url(zp)}" lang="zh-Hans" hreflang="zh-Hans">中文</a></span>' if zp else "") + f'</p><p class="answer">{e(ans)}</p><p class="facts">{"".join("<span>" + x + "</span>" for x in facts)}</p></header>'
                + (table(fl) + legend() if s != "beginners" else "")
                + f'<article class="guide"><div class="gbody">{sh}<section class="block faq"><h2>FAQ</h2>{faq_html([(q, e(a)) for q, a in qa])}</section></div>'
                + f'<aside class="grel"><h2>Related</h2><ul class="lists">{rel}</ul></aside></article></div>')
        ld = [bl2, itemlist_ld(BEST_H1.get(s, t), fl), faq_ld(qa)]
        title = BEST_TITLE.get(s, "Best {t} {y}, Ranked").format(y=YEAR_NOW, n=len(fl), t=t) + " | PropAnalyse"
        desc = (ans[:150].rsplit(" ", 1)[0] + "…") if len(ans) > 155 else ans
        page(path, title, desc, body, ld, "article")


# ---------------- evidence level for "Is X legit?" (documented on /legit/) ----------------
def evidence(f):
    pts, why = 0, []
    s, c = tps(f) or 0, tpc(f)
    if s >= 4.3 and c >= 5000: pts += 2; why.append(f"Trustpilot {s:.1f} from {c:,} reviews")
    elif s >= 4.0 and c >= 1000: pts += 1; why.append(f"Trustpilot {s:.1f} from {c:,} reviews")
    v = claim_usd(f)
    if v and v >= 50e6: pts += 2; why.append(f"reports {big_usd(v)}+ paid")
    elif v and v >= 5e6: pts += 1; why.append(f"reports {big_usd(v)}+ paid")
    y = years(f)
    if y and y >= 5: pts += 1; why.append(f"operating since {int(num(f['founded']))}")
    if f["_complete"] >= 85: pts += 1; why.append(f"publishes {f['_complete']}% of the fields we track")
    lvl = "Strong" if pts >= 4 else ("Moderate" if pts >= 2 else "Limited")
    return lvl, pts, why
EVID_TXT = {"Strong": "Strong public track record", "Moderate": "Moderate public track record", "Limited": "Limited public track record"}

def caution(f):
    C = []
    if not tps(f): C.append("No usable Trustpilot rating" + (f" ({tpc(f):,} reviews but no score shown)" if tpc(f) else ""))
    elif tpc(f) < 1000: C.append(f"Few reviews: {tpc(f):,} on Trustpilot")
    elif (tps(f) or 5) < 4.0: C.append(f"Trustpilot below 4.0 ({tps(f):.1f} from {tpc(f):,} reviews)")
    if not num(f.get("founded")): C.append("Founding year not published on the pages we read")
    elif years(f) is not None and years(f) <= 2: C.append(f"Young firm (founded {int(num(f['founded']))})")
    if not claim(f).get("text"): C.append("No firm-wide payout total on its homepage at our check")
    if f.get("consistency_rule") and not no_consistency(f): C.append("Consistency rule: " + str(f["consistency_rule"])[:140])
    if num(f["_x"].get("activation_fee")): C.append(f"Activation fee after passing: {money(num(f['_x']['activation_fee']))}")
    if kyc(f) is True: C.append("Identity check (KYC) required before payout: have documents ready")
    if not as_list(f.get("countries_restricted")): C.append("No restricted-country list we could verify: confirm your country before paying")
    if f["_complete"] < 80: C.append(f"Publishes fewer rules than most ({f['_complete']}% data completeness)")
    return C[:7]

def verif_events(f):
    ev = []
    srcs = len(as_list(f.get("source_urls")))
    if f.get("last_verified"): ev.append((f["last_verified"], "Rules, fees and payout terms read", f"{srcs} pages on the firm's own site and its Trustpilot profile"))
    if f["_x"].get("checked"): ev.append((f["_x"]["checked"], "Costs, refunds and payout methods checked", f"{len(as_list(f['_x'].get('sources')))} help-centre / FAQ pages"))
    if f["_c"].get("checked"): ev.append((f["_c"]["checked"], "Crypto trading terms checked", f"{len(as_list(f['_c'].get('sources')))} pages"))
    if f.get("category"): ev.append((SPRINT, "Account type recorded", f"{CAT_LABEL.get(f['category'], f['category'])}, from the firm's product page"))
    c = claim(f)
    ev.append((CLAIM_DATE, "Homepage payout claims checked", (f'Firm reports "{c["text"]}"' if c.get("text") else "No firm-wide payout total shown")))
    return sorted(ev, key=lambda x: x[0], reverse=True)

def timeline_html(f):
    rows = "".join(f'<tr><td class="n nowrap"><time datetime="{e(d)}">{nice_date(d)}</time></td><td>{e(t)}</td><td>{e(x)}</td></tr>' for d, t, x in verif_events(f))
    return f'<div class="tablewrap"><table class="mini changes"><thead><tr><th scope="col">Date</th><th scope="col">Check</th><th scope="col">Detail</th></tr></thead><tbody>{rows}</tbody></table></div>'

def history_block(f, CL):
    rows = [x for x in CL if x["slug"] == f["slug"]][:12]
    ch = change_table(rows, firm_col=False) if rows else '<p class="small">No rule changes recorded since tracking began. Every future change to its rules, fees or payout terms will appear here with the date.</p>'
    nxt = (datetime.date.fromisoformat(f.get("last_verified") or TODAY) + datetime.timedelta(days=30)).isoformat()
    return (f'<section class="block" id="history"><h2>Changelog</h2><p class="small">Last verified <b><time datetime="{e(f.get("last_verified") or TODAY)}">{nice_date(f.get("last_verified") or TODAY)}</time></b>. '
            f'Next full re-check due by <time datetime="{nxt}">{nice_date(nxt)}</time> (we re-verify every firm at least every 30 days).</p>'
            f'<h3>Rule changes</h3>{ch}<h3>Verification timeline</h3>{timeline_html(f)}'
            f'<p class="small"><a href="{url("/news/")}">All rule changes</a> · <a href="{url("/news/feed.xml")}">RSS</a> · <a href="{url("/updates/")}">Verification log</a></p></section>')

def legit_page(f):
    path = f"/firms/{f['slug']}/legit/"
    lvl, pts, why = evidence(f)
    c = claim(f); P_, C_ = pros_cons(f)
    restricted = as_list(f.get("countries_restricted"))
    lv = f.get("last_verified") or TODAY
    nchg = len([x for x in CHANGES if x["slug"] == f["slug"] and x["field"] != "Listing"])
    ans = (f"{f['name']} shows a {EVID_TXT[lvl].lower()} in what we can check publicly" + (": " + "; ".join(why) if why else "") + ". "
           f"It publishes its rules, fees and payout terms on its own site ({f['_complete']}% of the fields we track) and scores {f['_score']:.1f}/10 on our formula. "
           "That is evidence, not a guarantee: nobody outside the firm can audit its payouts, so read the cautions below.")
    rows = [("Operating since", show(int(num(f["founded"]))) if num(f.get("founded")) else NIL), ("HQ / legal entity", show(f.get("hq"))),
            ("Trustpilot", (f'<span class="n">{tps(f):.1f}</span> / 5 from <span class="n">{tpc(f):,}</span> reviews' if tps(f) else (f'No score shown ({tpc(f):,} reviews)' if tpc(f) else NIL))),
            ("Firm-reported payouts", (f'"{e(c["text"])}" ({e(cwhere(c))}) <a href="{e(c["source"])}" rel="nofollow noopener" target="_blank">source</a>, checked {nice_date(CLAIM_DATE)}' if c.get("text") else '<span class="nil">No total on homepage</span>')),
            ("Public payout proof", show(c.get("proof"))), ("Payout terms", show(f.get("payout_frequency"))), ("First payout", show(f.get("first_payout_days")) + (" days" if num(f.get("first_payout_days")) is not None else "")),
            ("Payout methods", show(pmethods(f)) if pmethods(f) else NIL), ("KYC before payout", {True: "Required", False: "Not required"}.get(kyc(f), NIL)),
            ("Fee refund", show(f["_x"].get("refund_policy"))), ("Restricted countries", show(restricted) if restricted else '<span class="nil">No list we could verify</span>'),
            ("Data completeness", f'<b class="n">{f["_complete"]}%</b>'), ("Rule changes logged", f'<span class="n">{nchg}</span>'), ("Last verified", f'<time datetime="{e(lv)}">{nice_date(lv)}</time>')]
    tbl = '<div class="tablewrap"><table class="mini"><tbody>' + "".join(f'<tr><th scope="row">{e(k)}</th><td>{v}</td></tr>' for k, v in rows) + "</tbody></table></div>"
    srcs = [s for s in as_list(f.get("source_urls")) + as_list(f["_x"].get("sources")) if re.search(r"faq|help|payout|withdraw|rule|terms|objective|support", s, re.I)][:5]
    steps = [f"Read the payout rules on the firm's own pages first" + (": " + ", ".join(f'<a href="{e(s)}" rel="nofollow noopener" target="_blank">{e(re.sub(r"^https?://(www\.)?", "", s)[:60])}</a>' for s in srcs) if srcs else "."),
             "Search the firm's Trustpilot page for recent reviews mentioning denied payouts, and check whether the firm replies with a rule reference.",
             "Buy the smallest account first and request a payout as soon as you are eligible. A first small payout tests the process cheaply.",
             "Keep screenshots of your trades and the rules as they were on the day you bought. Rules change; our changelog shows when.",
             "Pay by a method with chargeback rights where possible, and never send funds to a personal wallet or account."]
    tl = timeline_html(f)
    chg = [x for x in CHANGES if x["slug"] == f["slug"]][:8]
    disc = ('<p class="note"><b>Disclosure.</b> FundedXyz is run by the team behind PropAnalyse. This page uses the same fields and the same evidence rules as every other firm.</p>' if f["slug"] == "fundedxyz" else "")
    secs = [("Evidence at a glance", tbl),
            ("Reasons for confidence", UL([e(x) for x in P_]) if P_ else P("Nothing in the published data stands out above the field.")),
            ("Cautions", UL([e(x) for x in caution(f) + [x for x in C_ if x not in caution(f)]][:8])),
            ("How to check before you pay", '<ol class="bul">' + "".join(f"<li>{x}</li>" for x in steps) + "</ol>"),
            ("Rule history and checks", (change_table(chg, firm_col=False) if chg else "") + tl),
            ("What legit means here", P(f"Prop firms like {e(f['name'])} sell evaluations on simulated accounts and share profits from that activity; the fee is a service fee, not a deposit. They are generally not licensed the way brokers are. "
                "We do not verify licences or audit payouts, so 'legit' here means the firm publishes clear rules, has a checkable record and reports paying traders. "
                f'Full scoring rules: <a href="{url("/methodology/")}">methodology</a> and <a href="{url("/legit/")}">how evidence levels work</a>.'))]
    others = pairs_of(f["slug"])
    rel = (f'<li><a href="{url("/firms/" + f["slug"] + "/")}"><span>{e(f["name"])} review {YEAR_NOW}</span></a></li>'
           + "".join(f'<li><a href="{url("/compare/" + a + "-vs-" + b + "/")}"><span>{e(BY[a]["name"])} vs {e(BY[b]["name"])}</span></a></li>' for a, b in others[:5])
           + "".join([f'<li><a href="{url("/best/" + s + "/")}"><span>{e(BEST_H1.get(s, t))}</span></a></li>' for s, t, d, fn in BEST if fn(f)][:4])
           + f'<li><a href="{url("/legit/")}"><span>Evidence check: all {len(FIRMS)} firms</span></a></li>')
    qa = [(f"Is {f['name']} legit?", ans),
          (f"Does {f['name']} actually pay out?", ((f"The firm reports {c['text']} on its {cwhere(c)} (checked {nice_date(CLAIM_DATE)}). " + ("Each payout links to an on-chain transaction; we opened a sample on the block explorer and they match, but we have not checked every row." if onchain(c) else "That is the firm's own figure; we have not audited it.")) if c.get("text") else f"{f['name']} did not show a firm-wide payout total on its homepage when we checked on {nice_date(CLAIM_DATE)}.") + (f" Trustpilot shows {tpc(f):,} reviews." if tpc(f) else "")),
          (f"How long does {f['name']} take to pay?", f"Published terms: {f.get('payout_frequency') or 'not published'}." + (f" First payout after {int(num(f['first_payout_days']))} days." if num(f.get('first_payout_days')) is not None else "")),
          (f"Is {f['name']} regulated?", "Prop evaluation firms are generally not licensed as brokers, and we do not verify licences. Check any regulation claim on the regulator's own register."),
          (f"Is {f['name']} a scam?", f"We found no reason in the published data to call it one; its evidence level is {lvl.lower()}. Read the cautions, test with the smallest account, and keep records.")]
    h1 = f"Is {f['name']} legit? Evidence check ({YEAR_NOW})"
    c_, bl = crumbs([("Home", "/"), ("All firms", "/firms/"), (f["name"] + " review", f"/firms/{f['slug']}/"), ("Is it legit?", path)])
    sh = "".join(f'<section class="gsec"><h2>{e(h)}</h2>{b}</section>' for h, b in secs)
    body = f"""<div class="wrap">{c_}<article class="guide"><header class="ph"><h1>{e(h1)}</h1><p class="meta"><span>Last verified <time datetime="{e(lv)}">{nice_date(lv)}</time></span><span>Payout claims checked <time datetime="{CLAIM_DATE}">{nice_date(CLAIM_DATE)}</time></span><span>Evidence level: <b>{lvl}</b></span></p>
<p class="answer">{e(ans)}</p>{disc}</header><div class="gbody">{sh}<section class="block faq"><h2>FAQ</h2>{faq_html([(q, e(a)) for q, a in qa])}</section>
<p class="small">No reviews on this page are invented, and we do not publish star ratings of our own. Every figure links back to the firm's page or its Trustpilot profile. Spot something out of date? Send us the firm's page and we will re-check.</p></div>
<aside class="grel"><h2>Related</h2><ul class="lists">{rel}</ul></aside></article></div>"""
    desc = f"Is {f['name']} legit? Track record, Trustpilot ({tps(f):.1f}/5), " if tps(f) else f"Is {f['name']} legit? Track record, "
    desc += ("reported payouts, " if c.get("text") else "") + f"payout terms, restrictions and rule history. Evidence level: {lvl.lower()}. Verified {nice_date(lv)}."
    page(path, f"Is {f['name']} Legit? {YEAR_NOW} Evidence: Payouts, Track Record & Cautions | PropAnalyse", desc, body, [bl, article_ld(h1, desc, path), faq_ld(qa)], "article")
    return lvl

def legit_hub():
    path = "/legit/"
    c_, bl = crumbs([("Home", "/"), ("Legit checks", path)])
    rows = sorted(RANKED, key=lambda f: (-evidence(f)[1], -f["_score"]))
    t = gtable(rows, [FIRMCOL, ("Evidence", lambda f: f'<a href="{url("/firms/" + f["slug"] + "/legit/")}">{evidence(f)[0]}</a>', ""), ("Points", lambda f: f'<b class="n">{evidence(f)[1]}</b>/6', "n"),
                      ("Reported payouts", lambda f: (e(big_usd(claim_usd(f)) + "+") + (' <span class="evt">on-chain</span>' if onchain(claim(f)) else "")) if claim_usd(f) else NIL, "num n"), ("Trustpilot", lambda f: (f'{tps(f):.1f} ({tpc(f):,})' if tps(f) else NIL), "n"),
                      ("Since", lambda f: show(int(num(f["founded"]))) if num(f.get("founded")) else NIL, "n"), SCORECOL], "Prop firm evidence levels")
    cnt = {k: sum(1 for f in FIRMS if evidence(f)[0] == k) for k in EVID_TXT}
    ans = (f"Of the {len(FIRMS)} prop firms we track, {cnt['Strong']} have a strong public track record, {cnt['Moderate']} moderate and {cnt['Limited']} limited, on six points we can check from outside. "
           f"{sum(1 for f in FIRMS if claim(f).get('text'))} firms show a firm-wide payout total on their homepage. None of this is an audit; it tells you how much public evidence exists before you pay.")
    secs = [("Evidence levels", t),
            ("How the six points work", UL(["2 points: Trustpilot 4.3+ from 5,000+ reviews (1 point: 4.0+ from 1,000+)", "2 points: firm reports $50M+ paid to traders on its homepage (1 point: $5M+)",
                                            "1 point: operating 5+ years (founding year published)", "1 point: publishes 85%+ of the rule fields we track"]) +
             P("Strong = 4 to 6 points, moderate = 2 to 3, limited = 0 or 1. Reported payout totals are the firms' own marketing figures, read from their homepages on " + nice_date(CLAIM_DATE) + ". A limited level often just means a young firm or one that publishes less; it is not an accusation.")),
            ("Signs a prop firm deserves caution", UL(["Rules that are vague about what voids a payout (\"gambling\", \"abuse\") without examples", "Payout terms that changed shortly before a wave of denials: check our changelog dates",
                                                       "No company name or address in the terms", "Payment requested to a personal wallet or account", "Reviews that are all five stars within a few weeks"]))]
    qa = [("Which prop firms are legit?", ans), ("Do prop firms actually pay out?", f"{sum(1 for f in FIRMS if claim(f).get('text'))} of the {len(FIRMS)} firms we track publish a payout total; the largest is {max(FIRMS, key=lambda f: claim_usd(f) or 0)['name']} ({claim(max(FIRMS, key=lambda f: claim_usd(f) or 0))['text']}). These are the firms' own figures."),
          ("Are prop firms regulated?", "Generally no. Most sell evaluations on simulated accounts and are not licensed as brokers. Treat any regulation claim as something to check on the regulator's register.")]
    sh = "".join(f'<section class="gsec"><h2>{e(h)}</h2>{b}</section>' for h, b in secs)
    body = f"""<div class="wrap">{c_}<article class="guide"><header class="ph"><h1>Are prop firms legit? Evidence for {len(FIRMS)} firms</h1><p class="meta"><span>Payout claims checked <time datetime="{CLAIM_DATE}">{nice_date(CLAIM_DATE)}</time></span><span>Rules verified <time datetime="{TODAY}">{nice_date(TODAY)}</time></span></p>
<p class="answer">{e(ans)}</p></header><div class="gbody">{sh}<section class="block faq"><h2>FAQ</h2>{faq_html([(q, e(a)) for q, a in qa])}</section></div>
<aside class="grel"><h2>Firm evidence pages</h2><ul class="lists">{"".join(f'<li><a href="{url("/firms/" + f["slug"] + "/legit/")}"><span>Is {e(f["name"])} legit?</span></a></li>' for f in rows)}</ul></aside></article></div>"""
    page(path, f"Are Prop Firms Legit? {YEAR_NOW} Evidence for {len(FIRMS)} Firms | PropAnalyse", f"Evidence levels for {len(FIRMS)} prop firms: reported payouts, Trustpilot volume, years operating and rule transparency. Not an audit; every figure sourced.",
         body, [bl, article_ld("Are prop firms legit?", ans, path), faq_ld(qa), itemlist_ld("Prop firm evidence levels", rows)], "article")

_firm_page_orig = firm_page
def firm_page(f):
    _firm_page_orig(f)
    lvl, pts, why = evidence(f); c = claim(f)
    box = (f'<section class="block" id="legit"><h2>Is {e(f["name"])} legit?</h2><div class="prose"><p>Evidence level: <b>{lvl}</b> ({pts}/6). ' + e(("; ".join(why) + ".")[:1].upper() + ("; ".join(why) + ".")[1:] if why else "Little public evidence beyond its published rules.") +
           (f' The firm reports "{e(c["text"])}" on its {e(cwhere(c))} (checked {nice_date(CLAIM_DATE)})' + ("; sample transactions verified on-chain." if onchain(c) else ".") if c.get("text") else "") +
           f' <a href="{url("/firms/" + f["slug"] + "/legit/")}">Full evidence check</a>.</p></div></section>')
    lists = "".join(f'<li><a href="{url("/best/" + s + "/")}">{e(BEST_H1.get(s, t))}</a></li>' for s, t, d, fn in BEST if fn(f))
    side = f'<div class="cmpl"><h2>Listed in</h2><ul>{lists}</ul></div>' if lists else ""
    _patch_page(f"/firms/{f['slug']}/", before='<section class="block" id="history">', html=box)
    if side: _patch_page(f"/firms/{f['slug']}/", before='</aside>', html=side)

def updates():
    c, bl = crumbs([("Home", "/"), ("Verification log", "/updates/")])
    today = datetime.date.fromisoformat(SPRINT)
    def due(f): return datetime.date.fromisoformat(f.get("last_verified") or TODAY) + datetime.timedelta(days=30)
    rows = "".join(f'<tr><td><a href="{url("/firms/" + f["slug"] + "/#history")}">{e(f["name"])}</a></td><td class="n"><time datetime="{e(f.get("last_verified") or TODAY)}">{nice_date(f.get("last_verified") or TODAY)}</time></td>'
                   f'<td class="n">{(today - datetime.date.fromisoformat(f.get("last_verified") or TODAY)).days}</td><td class="n"><time datetime="{due(f).isoformat()}">{nice_date(due(f).isoformat())}</time></td>'
                   f'<td class="num"><b class="n">{f["_complete"]}%</b></td><td class="num n">{len(as_list(f.get("source_urls")) + as_list(f["_x"].get("sources")) + as_list(f["_c"].get("sources")))}</td></tr>'
                   for f in sorted(FIRMS, key=lambda x: (x.get("last_verified") or "", x["name"].lower())))
    avg = round(sum(f["_complete"] for f in FIRMS) / len(FIRMS))
    latest = CHANGES[:15]
    nsrc = sum(len(as_list(f.get("source_urls")) + as_list(f["_x"].get("sources")) + as_list(f["_c"].get("sources"))) for f in FIRMS)
    body = (f'<div class="wrap">{c}<header class="ph"><h1>Verification log &amp; rule changes</h1>'
            f'<p class="lede">When each of the {len(FIRMS)} firms was last checked, when it is due again, and every rule change we have logged. Average data completeness is <b class="n">{avg}%</b> across <b class="n">{nsrc}</b> source pages. '
            f'Homepage payout claims were checked on {nice_date(CLAIM_DATE)}.</p><p class="ctas"><a class="btn line sm" href="{url("/news/feed.xml")}">{ic("rss")}RSS: rule changes</a><a class="btn line sm" href="{url("/news/changes.json")}">JSON</a><a class="btn line sm" href="{url("/news/")}">Full change log</a></p></header>'
            f'<section class="block"><h2>Latest rule changes</h2>{change_table(latest) if latest else "<p class=small>No changes yet.</p>"}</section>'
            f'<section class="block"><h2>Firm by firm</h2><p class="small">Oldest check first. Our target is a full re-check of every firm at least every 30 days; the due date is that target, not a promise from the firm.</p>'
            f'<div class="tablewrap"><table class="mini log"><thead><tr><th scope="col">Firm</th><th scope="col">Last verified</th><th scope="col">Days ago</th><th scope="col">Re-check due</th><th scope="col" class="num">Completeness</th><th scope="col" class="num">Source pages</th></tr></thead><tbody>{rows}</tbody></table></div></section>'
            f'<section class="block"><h2>How verification works</h2><div class="prose"><p>For each firm we open its pricing, rules, FAQ and payout pages and record each figure with the date. If a figure is not published, we leave it blank. Each build compares the dataset with the previous snapshot and logs every changed field, with the old and new value, to the change log and its RSS feed.</p>'
            f'<p>Data completeness is the share of our tracked fields (fees, targets, drawdown, split, payout cycle, platforms, restrictions and more) the firm publishes. A low number usually means the firm explains less on its public pages, which is itself useful to know. See the <a href="{url("/methodology/")}">methodology</a> for the scoring formula and the <a href="{url("/legit/")}">evidence levels</a> for payout claims.</p></div></section></div>')
    page("/updates/", "Prop Firm Verification Log & Rule Changes (Dated) | PropAnalyse", f"When each of {len(FIRMS)} prop firms was last verified, re-check due dates, data completeness and the latest dated rule changes. RSS and JSON feeds.", body, [bl],
         extra_head=f'<link rel="alternate" type="application/rss+xml" title="PropAnalyse rule changes" href="{ABS}/news/feed.xml">')


# ---------------- /zh/best/: five Chinese "best" lists ----------------
ZH_BEST = [("beginners", "新手"), ("cheap-challenges", "最便宜"), ("high-profit-split", "高分成"), ("instant-funding", "直接资金"), ("fast-payouts", "快速出金")]
ZH_ALT.update({f"/best/{s}/": f"/zh/best/{s}/" for s, _ in ZH_BEST})
ZH_FOOT += [("/zh/best/beginners/", "新手推荐"), ("/zh/best/cheap-challenges/", "最便宜的公司")]
BEGIN_ZH = {"Entry fee $100 or less": "入门费 100 美元以内", "Static drawdown on the headline plan": "主方案为静态回撤", "No evaluation time limit": "考核不限时",
            "No consistency rule": "无一致性规则", "Fee refunded on some plan": "部分方案退还挑战费", "Trustpilot 4.3+ from 1,000+ reviews": "Trustpilot 4.3 分以上且评价 1,000 条以上"}
def zh_best(s):
    path = f"/zh/best/{s}/"
    fn = next(x[3] for x in BEST if x[0] == s)
    fl = [f for f in (BEGINNERS() if s == "beginners" else RANKED) if fn(f)]
    top = fl[:3]; n = len(fl)
    ch = min((f for f in fl if f["_fee"] is not None), key=lambda f: f["_fee"], default=None)
    rk = zrank(fl)
    if s == "beginners":
        h1 = f"{YEAR_NOW} 新手最适合的自营交易公司"
        ans = f"按我们的六项新手清单，最适合新手的自营交易公司（prop firm）是 {zlist([f['name'] for f in top])}。共有 {n} 家公司满足至少三项。清单偏向能“原谅”失误的规则（静态回撤、不限时、无一致性规则），以及便宜且可退款的第一次尝试。"
        t = gtable(fl, [rk, ZFIRM, ("清单", lambda f: f'<b class="n">{len(begin_met(f))}</b>/6', "n"), ("满足项", lambda f: e("、".join(BEGIN_ZH.get(x, x) for x in begin_met(f))), "wide"), ZFEE, ZSCORE], "新手清单排名")
        secs = [("清单排名", t), ("六项清单", "<ul class=bul>" + "".join(f"<li>{e(BEGIN_ZH[nm])}</li>" for nm, _ in BEGIN_CRIT) + "</ul><p>公司没有公布的规则不得分；同分时按 PA 评分排序。这份清单独立于 PA 评分，不会改变评分。</p>"),
                ("比选公司更重要的习惯", "<p>先买最小的账户；每笔交易的风险远低于每日亏损上限；第一笔交易前读完公司的禁止策略清单。大多数第一次挑战失败，是因为触发了每日亏损规则，而不是没达到盈利目标。</p>")]
        qa = [("新手应该选哪家自营交易公司？", ans), ("新手选一阶段还是两阶段挑战？", "两阶段挑战通常回撤更宽、每阶段目标更低，更能容忍失误；一阶段更快，但规则更严。")]
    elif s == "cheap-challenges":
        by = sorted([f for f in fl if f["_fee"] is not None], key=lambda f: f["_fee"]); lo = by[0]
        h1 = f"{YEAR_NOW} 最便宜的自营交易公司：100 美元以内的挑战"
        ce = cheapest_entry(lo)
        ans = f"我们追踪的公司中，入门费最低的是 {lo['name']}，{fmoney(lo, lo['_fee'])}" + (f"（{money(ce[1])} 账户）" if ce else "") + f"。共有 {n} 家公司的挑战费在 100 美元以内。但最低价通常只买到最小的账户，按每 1K 账户成本比较更公平。"
        t = gtable(by, [("#", lambda f: f'<span class="n">{by.index(f) + 1}</span>', "n"), ZFIRM, ("入门费", lambda f: fmoney(f, f["_fee"]), "num n"), ("账户", lambda f: money(cheapest_entry(f)[1]) if cheapest_entry(f) else NIL_ZH, "num n"),
                        ("每 1K 成本", lambda f: fmoney(f, cost_per_k(f)) if cost_per_k(f) else NIL_ZH, "num n"), ZSCORE], "入门费排名")
        secs = [("按价格排序", t), ("标价和真实成本", f"<p>重置费、是否退款、通过率都会改变真实成本。用<a href=\"{url('/tools/true-cost/')}\">真实成本计算器</a>（英文）代入你自己的数字。按账户规模比较：<a href=\"{url('/zh/sizes/10k/')}\">10K</a>、<a href=\"{url('/zh/sizes/50k/')}\">50K</a>、<a href=\"{url('/zh/sizes/100k/')}\">100K</a>。</p>")]
        qa = [("最便宜的自营交易公司是哪家？", ans), ("最便宜就最划算吗？", "不一定。小账户的低价按每 1K 计算可能更贵，重置费也会累积。请比较每 1K 成本和退款条款。")]
    elif s == "high-profit-split":
        hundred = [f for f in fl if (f["_split"] or 0) >= 100]
        h1 = f"{YEAR_NOW} 分成比例最高的自营交易公司"
        ans = f"{n} 家公司宣传 90% 或以上的利润分成，其中 {len(hundred)} 家最高可达 100%：{zlist([f['name'] for f in hundred])}。多数最高分成需要通过扩容或付费附加项才能达到，并不是起始比例。"
        t = gtable(fl, [ZFIRM, ("宣传分成", lambda f: zsplit(f.get("profit_split")), ""), ("条件（英文原文）", lambda f: zshow(f.get("profit_split_scale")), "wide"), ZSCORE], "分成条款")
        secs = [("各公司分成条款", t), ("看分成时要注意", "<p>先看起始分成，再看达到最高分成要满足什么：出金次数、扩容计划，还是购买附加项。部分公司的直接资金账户分成更低。</p>")]
        qa = [("哪家自营交易公司分成最高？", ans), ("100% 分成是第一天就有吗？", "很少。多数公司从 80% 起步，出金几次或付费升级后才提高。")]
    elif s == "instant-funding":
        h1 = f"{YEAR_NOW} 直接资金（免考核）自营交易公司"
        ans = f"我们追踪的公司中有 {n} 家提供直接资金账户，即不用通过考核就拿到资金账户。PA 评分前三：{zlist([f['name'] for f in top])}。直接资金省时间不省钱：同样的购买力，费用更高，分成或回撤往往更严。"
        t = gtable(fl, [rk, ZFIRM, ZCAT, ZFEE, ZSPLIT, ZPAY, ZSCORE], "直接资金公司")
        secs = [("排名", t), ("直接资金账户放弃了什么", "<p>没有考核，公司会在别处定价风险：每 1K 费用更高、分成更低、有一致性规则或回撤更紧。表中的起步价可能是该公司考核方案的价格，直接资金方案请看公司详情页。</p>")]
        qa = [("哪些自营交易公司提供直接资金？", ans), ("直接资金值得吗？", "适合对风险控制有信心、想省时间的交易者；预算有限的新手通常更适合先做小额考核。")]
    else:
        fast = [f for f in fl if f["_bucket"] == "daily"]
        fd = sorted([f for f in fl if num(f.get("first_payout_days")) is not None], key=lambda f: num(f["first_payout_days"]))
        h1 = f"{YEAR_NOW} 出金最快的自营交易公司：每日与每周出金"
        ans = f"{len(fast)} 家公司支持每日或随时出金（{zlist([f['name'] for f in fast])}），{n - len(fast)} 家每周出金。" + (f"公布的首次出金等待期最短的是 {fd[0]['name']}，{int(num(fd[0]['first_payout_days']))} 天。" if fd else "")
        t = gtable(fl, [ZFIRM, ZPAY, ("首次出金（天）", lambda f: zshow(f.get("first_payout_days")), "num n"), ("条款（英文原文）", lambda f: zshow(f.get("payout_frequency")), "wide"), ZSCORE], "出金周期")
        secs = [("各公司出金条款", t), ("“随时出金”不等于“立即到账”", "<p>随时出金指随时可以申请，处理仍需数小时到几个工作日；首次出金前通常要完成身份验证（KYC）。用 USDT 出金时，先小额测试你自己控制的钱包。</p>")]
        qa = [("哪些自营交易公司每天出金？", ans), ("随时出金是马上到账吗？", "不是。申请随时可以提交，但处理和 KYC 需要时间。")]
    secs.append(("榜单如何生成", f"<p>筛选条件与英文版相同，排序按 PA 评分（信任 30%、成本 20%、规则 20%、出金 20%、历史 10%），表格另有说明的除外。数据取自各公司官网，最近一次全面核实为 {zdate(TODAY)}。FundedXyz 由本站团队运营，按同样规则评分。</p>"))
    qa.append(("榜单多久更新一次？", f"每次构建都会重新读取数据集。最近核实日期 {zdate(TODAY)}；规则变化会带日期记录在规则变更页面。"))
    rel = "".join(f'<li><a href="{url("/zh/best/" + s2 + "/")}"><span>{e(z)}自营交易公司</span></a></li>' for s2, z in ZH_BEST if s2 != s) + zh_rel(path)
    facts = [f'<b class="n">{n}</b> 家公司'] + ([f'最低 <b class="n">{fmoney(ch, ch["_fee"])}</b>'] if ch else [])
    zh_shell(path, [("首页", "/zh/"), ("榜单", path)], h1, f"{h1} | PropAnalyse", (ans[:110] + "…") if len(ans) > 112 else ans, ans, facts, secs, qa, rel=rel,
             ld_extra=[dict(itemlist_ld(h1, fl), inLanguage="zh-Hans")])

# ---------------- SEA country pages: local session times, payout routes ----------------
SEA = {"malaysia": ("Malaysia", "Malaysians", 8, "MYT"), "singapore": ("Singapore", "Singaporeans", 8, "SGT"), "philippines": ("the Philippines", "Filipinos", 8, "PHT"),
       "indonesia": ("Indonesia", "Indonesians", 7, "WIB"), "vietnam": ("Vietnam", "Vietnamese traders", 7, "ICT")}
def _hm(h): return f"{int(h) % 24:02d}:{int(round((h % 1) * 60)):02d}"
_prog_shell_orig = prog_shell
def prog_shell(path, items, h1, title, desc, ans, facts, secs, qa, noindex=False, rel=None):
    m = re.match(r"^/countries/([a-z-]+)/$", path)
    if m and m.group(1) in SEA:
        slug = m.group(1); nm, dem, off, tz = SEA[slug]
        aliases = next(a for s, _, a in COUNTRIES if s == slug)
        ok = [f for f in RANKED if country_status(f, aliases)[0] in ("open", "open_catchall")]
        cry = [f for f in RANKED if pays_crypto(f) and country_status(f, aliases)[0] not in ("restricted",)]
        ny_std, ny_dst = 14.5 + off, 13.5 + off   # NYSE / CME equity RTH open in UTC (9:30 ET) + offset
        secs = list(secs) + [
            (f"Trading hours in {tz} (UTC+{off})", P(f"US index futures and US stocks trade their main session from 9:30 to 16:00 New York time. In {tz} that is {_hm(ny_std)} to {_hm(ny_std + 6.5)} while the US is on standard time (early November to mid-March) and {_hm(ny_dst)} to {_hm(ny_dst + 6.5)} during US daylight time.",
                f"London opens at {_hm(8 + off)} {tz} in the northern winter and {_hm(7 + off)} in summer. If you can only trade evenings, a futures firm's US session fits; if you trade mornings, Asian-session forex and 24/7 crypto fit better.",
                "Daily loss limits reset at a server time set by each firm, often 17:00 New York, which can land in the middle of your night. Check it on the firm page before you hold trades across it.")),
            (f"Getting paid from {nm}", P(f"Bank wires from overseas firms can take days and carry FX fees. {len(cry)} firms that do not list {nm} as restricted publish a crypto payout method: {fl_names(cry)}. "
                "Stablecoin payouts arrive faster, but local tax and exchange rules still apply to you.", f'Per-firm payout methods: <a href="{url("/guides/crypto-prop-firms-usdt-payouts/")}">prop firms that pay in USDT</a>.'))]
        qa = list(qa) + [(f"What is the best prop firm for {dem}?", f"Among firms whose published list does not exclude {nm}, the highest PA Scores are {fl_names(ok, 3)}. Firms with no published list may also accept {nm}; confirm at checkout."),
                         (f"When should {dem} trade US futures?", f"The US cash session runs {_hm(ny_std)} to {_hm(ny_std + 6.5)} {tz} in the northern winter and {_hm(ny_dst)} to {_hm(ny_dst + 6.5)} in the northern summer."),
                         (f"Is prop trading legal in {nm}?", "We do not give legal or tax advice. Prop evaluations are services sold by overseas companies on simulated accounts; check local rules and how payouts are taxed with a qualified adviser.")]
        title = f"Best Prop Firms for {dem.replace(' traders', '')} ({YEAR_NOW}): Who Accepts {nm.replace('the ', '').title() if nm.startswith('the ') else nm} | PropAnalyse"
        h1 = f"Prop firms for {dem}: who accepts traders from {nm}"
    return _prog_shell_orig(path, items, h1, title, desc, ans, facts, secs, qa, noindex, rel)

# ---------------- guides: USDT covers every firm; crypto guide gets account-type split + payout claims ----------------
def g_usdt():
    rows = [f for f in RANKED if pmethods(f) or f["_c"]]
    cry = [f for f in rows if pays_crypto(f)]
    nat = [f for f in cry if f.get("category") == "crypto-exchange"]; oth = [f for f in cry if f.get("category") != "crypto-exchange"]
    ans = (f"{len(cry)} of the {len(FIRMS)} prop firms we track publish a crypto payout method (USDT, USDC or other coins): {fl_names(cry)}. "
           f"{len(nat)} of them are crypto-exchange firms and {len(oth)} are CFD or futures firms that also pay in crypto.") if cry else "Crypto payout data is still being verified."
    t = gtable(rows, [FIRMCOL, ("Payout methods", lambda f: show(pmethods(f)) if pmethods(f) else NIL, "wide"), ("Pays in crypto", lambda f: "Yes" if pays_crypto(f) else NIL, ""),
                      ("KYC first", lambda f: {True: "Required", False: "Not required"}.get(kyc(f), NIL), ""), ("Cycle", lambda f: e(BUCKET_LABEL.get(f["_bucket"], "")) or NIL, ""), SCORECOL], "Payout methods by firm")
    secs = [("Payout methods by firm", t),
            ("Network and fees", P("USDT on TRC20 is cheap to receive, while ERC20 can cost several dollars in gas. Check which network the firm sends on and whether it passes the fee to you. Send a small first withdrawal to a wallet you control before moving larger amounts.")),
            ("KYC still applies", P(f"Paying out in crypto doesn't mean anonymous. {sum(1 for f in cry if kyc(f) is True)} of these firms state an identity check before payout; most others run one before the funded contract."))]
    return ans, secs, [("Which prop firms pay in USDT?", ans), ("Do forex prop firms pay in crypto?", f"Some do: {fl_names(oth)} list a crypto method next to bank or card payouts." if oth else "Not in our current data.")]
_g_best_crypto_orig = g_best_crypto
def g_best_crypto():
    ans, secs, qa = _g_best_crypto_orig()
    ce = [f for f in RANKED if f.get("category") == "crypto-exchange"]
    t = gtable(ce, [FIRMCOL, ("Reported payouts", lambda f: e(claim(f)["text"]) if claim(f).get("text") else NIL, "wide"), ("Evidence", lambda f: f'<a href="{url("/firms/" + f["slug"] + "/legit/")}">{evidence(f)[0]}</a>', ""), SCORECOL], "Crypto exchange firms: payout evidence")
    secs = secs + [("Payout evidence for crypto-exchange firms", t + P(f"Reported totals are the firms' own homepage figures, checked {nice_date(CLAIM_DATE)}. Evidence levels are explained on <a href=\"{url('/legit/')}\">are prop firms legit?</a>"))]
    return ans, secs, qa + [("Which crypto prop firm has paid out the most?", (lambda m: f"Of the crypto-exchange firms, {m['name']} reports the largest total: {claim(m)['text']} (its own figure)." if m and claim_usd(m) else "No crypto-exchange firm publishes a total.")(max(ce, key=lambda f: claim_usd(f) or 0, default=None)))]
for _g in GUIDES:
    if _g["slug"] == "crypto-prop-firms-usdt-payouts": _g["fn"] = g_usdt; _g["h1"] = "Prop firms that pay out in USDT (crypto payouts)"; _g["desc"] = "Every prop firm we track that pays in USDT, USDC or other crypto, with payout methods, KYC and payout cycles side by side."
    if _g["slug"] == "best-crypto-prop-firms": _g["fn"] = g_best_crypto

FOOT_EXTRA += [("/legit/", "Legit checks"), ("/best/beginners/", "Best for beginners")]
_prog_prev_seo = programmatic
def programmatic():
    _prog_prev_seo()
    for s, _ in ZH_BEST: zh_best(s)
    for f in FIRMS: legit_page(f)
    legit_hub()

# ---------------- thin-page guard: noindex anything under ~250 useful words ----------------
THIN_EXEMPT = ("/", "/about/", "/methodology/", "/firms/", "/compare/", "/best/", "/guides/", "/countries/", "/platforms/", "/sizes/", "/tools/", "/quiz/", "/offers/", "/discounts/", "/zh/", "/news/", "/glossary/", "/faq/")
def words_in(path):
    p = os.path.join(OUT, path.lstrip("/"), "index.html") if path.endswith("/") else os.path.join(OUT, path.lstrip("/"))
    t = open(p).read(); m = re.search(r"<main.*?</main>", t, re.S); t = m.group(0) if m else t
    t = re.sub(r"<script.*?</script>|<nav.*?</nav>|<ol class=\"crumbs.*?</ol>", " ", t, flags=re.S); t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    cjk = len(re.findall(r"[\u4e00-\u9fff]", t)); return len(re.sub(r"[\u4e00-\u9fff]", " ", t).split()) + int(cjk / 1.6), p
THIN = []
_seo_prev_seo = seo_files
def seo_files():
    for path in list(PAGES):
        if path in THIN_EXEMPT or path.startswith("/tools/") or path in NOINDEX: continue
        n, p = words_in(path)
        if n < 250:
            THIN.append((path, n)); NOINDEX.add(path)
            t = open(p).read()
            if 'name="robots"' not in t: open(p, "w").write(t.replace("</head>", '<meta name="robots" content="noindex,follow"></head>', 1))
    _seo_prev_seo()
    L = ["", "## Best-of lists"] + [f"- [{BEST_H1.get(s, t)}]({ABS}/best/{s}/): {d}" for s, t, d, fn in BEST if f"/best/{s}/" not in NOINDEX]
    L += ["", "## Is it legit? (evidence pages)", f"- [Are prop firms legit? Evidence levels for {len(FIRMS)} firms]({ABS}/legit/): reported payouts (firms' own homepage figures, checked {CLAIM_DATE}), Trustpilot volume, years operating, rule transparency"]
    L += [f"- [Is {f['name']} legit?]({ABS}/firms/{f['slug']}/legit/): evidence {evidence(f)[0].lower()}" + (f"; reports {claim(f)['text']}" if claim(f).get("text") else "") for f in RANKED if f"/firms/{f['slug']}/legit/" not in NOINDEX]
    L += ["", "## 中文榜单"] + [f"- [{z}自营交易公司]({ABS}/zh/best/{s}/)" for s, z in ZH_BEST]
    L += ["", "## Freshness", f"- [Verification log]({ABS}/updates/): last-verified date, re-check due date and completeness per firm", f"- Payout claims dataset: {ABS}/data/payout_claims.json"]
    open(os.path.join(OUT, "llms.txt"), "a").write("\n".join(L) + "\n")
    shutil.copy(os.path.join(ROOT, "data", "payout_claims.json"), os.path.join(OUT, "data", "payout_claims.json"))
    if THIN: print("noindexed thin pages:", THIN)

