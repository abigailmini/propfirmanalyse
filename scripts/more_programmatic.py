# PropAnalyse programmatic pages (2026-10-28): /countries/, /platforms/, /sizes/.
# Every number is computed from data/firms.json at build time. A page with too little real data is noindexed.
import statistics

CAT_LABEL = {"futures": "Futures", "cfd": "CFD", "crypto-exchange": "Crypto exchange"}   # account type (data: category)

def prog_shell(path, items, h1, title, desc, ans, facts, secs, qa, noindex=False, rel=None):
    c, bl = crumbs(items)
    sh_ = "".join(f'<section class="gsec"><h2>{e(h)}</h2>{b}</section>' for h, b in secs)
    faqh = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in qa)
    relh = f'<aside class="grel"><h2>Related</h2><ul class="lists">{rel}</ul></aside>' if rel else ""
    fh = "".join(f'<span>{x}</span>' for x in facts)
    body = f"""<div class="wrap">{c}<article class="guide"><header class="ph"><h1>{e(h1)}</h1><p class="meta"><span>Updated <time datetime="{TODAY}">{nice_date(TODAY)}</time></span><span>Data: {len(FIRMS)} firms, read from their own sites</span></p>
<p class="answer">{e(ans)}</p><p class="facts">{fh}</p></header><div class="gbody">{sh_}<section class="block faq"><h2>FAQ</h2>{faqh}</section>
<p class="small">Figures come from our dataset at build time. Scores use the <a href="{url('/methodology/')}">published formula</a>; FundedXyz is ours and is scored the same way. Changes are logged on <a href="{url('/news/')}">rule changes</a>.</p></div>{relh}</article></div>"""
    ld = [bl, {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]}]
    if noindex: NOINDEX.add(path)
    page(path, title, desc, body, ld, "article", extra_head='<meta name="robots" content="noindex,follow">' if noindex else "")

def hub_shell(path, items, h1, title, desc, lede, entries):
    c, bl = crumbs(items)
    li = "".join(f'<li><a href="{url(p)}"><b>{e(t)}</b><span>{e(d)}</span><span class="cnt"><b class="n">{n}</b> {e(u)}</span>{ic("arrow")}</a></li>' for p, t, d, n, u in entries)
    page(path, title, desc, f'<div class="wrap">{c}<header class="ph"><h1>{e(h1)}</h1><p class="lede">{lede}</p></header><ul class="shortlists">{li}</ul></div>', [bl])

def fcount(n, w="firm"): return f"{n} {w}{'' if n == 1 else 's'}"

# ---------------- countries ----------------
COUNTRIES = [  # slug, display, aliases matched case-insensitively against countries_restricted entries
 ("malaysia", "Malaysia", ["malaysia"]), ("indonesia", "Indonesia", ["indonesia"]), ("vietnam", "Vietnam", ["vietnam", "viet nam"]),
 ("philippines", "the Philippines", ["philippines"]), ("thailand", "Thailand", ["thailand"]), ("singapore", "Singapore", ["singapore"]),
 ("china", "China", ["china"]), ("hong-kong", "Hong Kong", ["hong kong"]), ("taiwan", "Taiwan", ["taiwan"]), ("india", "India", ["india"]),
 ("pakistan", "Pakistan", ["pakistan"]), ("bangladesh", "Bangladesh", ["bangladesh"]), ("sri-lanka", "Sri Lanka", ["sri lanka"]),
 ("nigeria", "Nigeria", ["nigeria"]), ("kenya", "Kenya", ["kenya"]), ("south-africa", "South Africa", ["south africa"]), ("ghana", "Ghana", ["ghana"]),
 ("egypt", "Egypt", ["egypt"]), ("morocco", "Morocco", ["morocco"]), ("turkey", "Turkey", ["turkey", "türkiye"]),
 ("uae", "the UAE", ["uae", "united arab emirates"]), ("saudi-arabia", "Saudi Arabia", ["saudi arabia"]), ("ukraine", "Ukraine", ["ukraine"]),
]
CATCHALL = ("fatf", "sanction", "high-risk")

def country_status(f, aliases):
    lst = as_list(f.get("countries_restricted"))
    if not lst: return "nolist", None
    for c in lst:
        cl = c.lower(); head = cl.split(" (")[0].strip()
        if any(a == head or a == cl or head.endswith(" " + a) or head.startswith(a + " ") or ("(" + a + ")") in cl for a in aliases):
            part = any(k in cl for k in (" only", "region", "non-mainland", "corsica"))
            return ("partial" if part else "restricted"), c
    return ("open_catchall" if any(any(k in c.lower() for k in CATCHALL) for c in lst) else "open"), None

def ctable(fl, cap, note=None):
    cols = [FIRMCOL, SCORECOL, ("Type", lambda f: e(CAT_LABEL.get(f.get("category"), f.get("category") or "")), ""),
            ("From", lambda f: mh(f["_fee"], f.get("fee_currency")), "num n"), ("Split", lambda f: show(f.get("profit_split")), ""),
            ("Payouts", lambda f: e(BUCKET_LABEL.get(f["_bucket"], "")) or NIL, "")]
    if note: cols.append(("Note", note, ""))
    return gtable(fl, cols, cap)

def country_pages():
    entries = []
    for slug, name, aliases in COUNTRIES:
        st = {f["slug"]: country_status(f, aliases) for f in RANKED}
        restricted = [f for f in RANKED if st[f["slug"]][0] == "restricted"]
        partial = [f for f in RANKED if st[f["slug"]][0] == "partial"]
        open_ = [f for f in RANKED if st[f["slug"]][0] in ("open", "open_catchall")]
        nolist = [f for f in RANKED if st[f["slug"]][0] == "nolist"]
        withlist = len(restricted) + len(partial) + len(open_)
        bare = name.replace("the ", "")
        path = f"/countries/{slug}/"
        avail = open_  # only firms whose own list leaves the country off; "no list" is never treated as acceptance
        top = avail[0] if avail else None
        cheap = min((f for f in avail if f["_fee"] is not None), key=lambda f: f["_fee"], default=None)
        cry = [f for f in avail if is_native(f)]
        fut_r = [f for f in restricted if f.get("category") == "futures"]
        nr = len(restricted)
        ans = ((f"None of the {len(FIRMS)} prop firms we track names {name} on its restricted-country list." if nr == 0 else
                f"{nr} of the {len(FIRMS)} prop firms we track name{'s' if nr == 1 else ''} {name} on {'its' if nr == 1 else 'their'} restricted-country list: {nlist([f['name'] for f in restricted])}.")
               + (f" {nlist([f['name'] for f in partial])} restrict{'s' if len(partial) == 1 else ''} it only in part." if partial else "")
               + f" {fcount(len(open_))} publish a list that leaves {name} off, and {len(nolist)} publish no country list we could verify, so confirm those at checkout."
               + (f" Among firms whose list leaves {name} off, the highest PA Score is {top['name']} ({top['_score']:.1f}/10)" if top else "")
               + (f" and the cheapest entry is {cheap['name']} at {money(cheap['_fee'], cheap.get('fee_currency'))}." if cheap else ("." if top else "")))
        def note_open(f, s=st):
            return '<small>Also bars FATF high-risk and sanctioned jurisdictions; check its current list</small>' if s[f["slug"]][0] == "open_catchall" else '<small>Not on its published list</small>'
        secs = []
        if restricted:
            secs.append((f"Firms that do not accept {bare}", ctable(restricted, f"Prop firms restricting {bare}", lambda f, s=st: f'<small>Listed as "{e(s[f["slug"]][1])}"</small>')))
        if partial:
            secs.append(("Partly restricted", ctable(partial, f"Partial restrictions for {bare}", lambda f, s=st: f'<small>{e(s[f["slug"]][1])}</small>')))
        secs.append((f"Not on the restricted list ({len(open_)})", ctable(open_, f"Prop firms whose published list leaves out {bare}", note_open) if open_ else "<p>None.</p>"))
        if nolist:
            secs.append((f"No country list published ({len(nolist)})", "<p>These firms do not publish a country list we could verify. No list is not the same as acceptance: read the firm's terms or ask support before you pay.</p>" + ctable(nolist, "Firms without a published country list", None)))
        ctx = []
        if fut_r: ctx.append(f"Futures firms are the strictest here: {e(nlist([f['name'] for f in fut_r]))} restrict{'s' if len(fut_r) == 1 else ''} {e(name)}. US-based futures firms tend to carry long country lists tied to their clearing and payment providers.")
        if cry: ctx.append(f"Crypto-native firms open to {e(name)} on our data: {e(nlist([f['name'] for f in cry]))}. They usually pay in USDT or USDC, which avoids bank-wire limits but still needs KYC.")
        ctx.append(f"Lists change without notice. We re-read each list when we verify the firm; the date sits on every firm page, and changes show on <a href=\"{url('/news/')}\">rule changes</a>.")
        secs.append(("What to know", "".join(f"<p>{x}</p>" for x in ctx)))
        qa = [(f"Can traders from {bare} join a prop firm?", f"Yes, most can. {len(open_)} firms with a published list leave {name} off it; {len(restricted)} restrict it." + (f" Restricting firms: {nlist([f['name'] for f in restricted])}." if restricted else "")),
              (f"Which prop firms don't accept {bare}?", (f"{nlist([f['name'] for f in restricted])} list {name} as restricted on their own sites." if restricted else f"None of the {withlist} firms with a published list restricts {name}.") + " Lists change, so check the firm's terms before paying.")]
        if cheap: qa.append((f"What is the cheapest prop firm available in {bare}?", f"{cheap['name']}, from {money(cheap['_fee'], cheap.get('fee_currency'))}, among firms whose published country list leaves {name} off. Firms without a published list may be cheaper; check their terms."))
        rel = "".join(f'<li><a href="{url("/countries/" + s2 + "/")}"><span>Prop firms in {e(n2.replace("the ", ""))}</span></a></li>' for s2, n2, _ in COUNTRIES if s2 != slug)
        facts = [f'<b class="n">{len(restricted)}</b> restrict', f'<b class="n">{len(open_)}</b> not listed', f'<b class="n">{len(nolist)}</b> no list published']
        h1 = f"Prop firms that accept traders from {bare}"
        prog_shell(path, [("Home", "/"), ("By country", "/countries/"), (bare, path)], h1,
                   f"Prop Firms Accepting {bare} Traders ({YEAR_NOW}): {len(restricted)} Restrict | PropAnalyse",
                   f"Which prop firms accept traders from {bare}: {len(restricted)} of {len(FIRMS)} restrict {bare}, read from each firm's own restricted-country list, with fees and PA Score.",
                   ans, facts, secs, qa, noindex=(withlist < 5), rel=rel)
        entries.append((path, bare, f"{len(restricted)} restrict, {len(open_)} leave it off their list.", len(open_) + len(nolist), "open or unlisted"))
    hub_shell("/countries/", [("Home", "/"), ("By country", "/countries/")], "Prop firms by country", f"Prop Firms by Country ({YEAR_NOW}): Who Accepts Your Country | PropAnalyse",
              "Which prop firms accept traders from Malaysia, Indonesia, Vietnam, Nigeria, Pakistan and more, read from each firm's own restricted-country list.",
              f"Each page checks one country against the restricted-country lists that {sum(1 for f in FIRMS if as_list(f.get('countries_restricted')))} of our {len(FIRMS)} firms publish. Firms with no published list are shown separately, never counted as accepting.", entries)

# ---------------- platforms ----------------
PLATFORMS = [  # slug, label, match(lowercased platform string), blurb
 ("mt5", "MetaTrader 5", lambda p: "mt5" in p or "metatrader 5" in p, "MetaQuotes' multi-asset terminal and the default at most forex/CFD firms. Expert Advisors run natively, so check each firm's EA and copy-trading rules."),
 ("mt4", "MetaTrader 4", lambda p: "mt4" in p or "metatrader 4" in p, "The older MetaQuotes terminal. Fewer prop firms offer it each year."),
 ("ctrader", "cTrader", lambda p: "ctrader" in p, "Spotware's terminal with depth of market and cBots, popular with traders who want ECN-style order handling."),
 ("match-trader", "Match-Trader", lambda p: "match" in p and "trader" in p, "A browser and mobile platform used by many firms that moved off MetaTrader. Built-in prop dashboard; no EA ecosystem."),
 ("tradelocker", "TradeLocker", lambda p: "tradelocker" in p, "A web platform with TradingView charts built in. Common at newer forex firms."),
 ("dxtrade", "DXtrade", lambda p: "dxtrade" in p, "Devexperts' web and mobile platform, used by several CFD prop firms."),
 ("tradingview", "TradingView", lambda p: "tradingview" in p, "Trade straight from TradingView charts through the firm's broker connection."),
 ("ninjatrader", "NinjaTrader", lambda p: "ninjatrader" in p, "The common futures desktop platform. Check whether the firm covers the license and data fee."),
 ("tradovate", "Tradovate", lambda p: "tradovate" in p, "Cloud futures platform owned by NinjaTrader. Runs in a browser."),
 ("rithmic", "Rithmic", lambda p: "rithmic" in p or "r | trader" in p, "Futures data and order-routing feed behind R | Trader Pro and many third-party platforms."),
 ("bybit", "Bybit", lambda p: "bybit" in p, "Crypto exchange. Firms give you a Bybit demo or sub-account, so you trade real order-book perps."),
]

def platform_pages():
    entries = []
    unknown = [f for f in RANKED if not f["_platforms"]]
    for slug, label, m, blurb in PLATFORMS:
        fl = [f for f in RANKED if any(m(p.lower()) for p in f["_platforms"])]
        if not fl: continue
        path = f"/platforms/{slug}/"
        cheap = min((f for f in fl if f["_fee"] is not None), key=lambda f: f["_fee"], default=None)
        cats = {}
        for f in fl:
            k = CAT_LABEL.get(f.get("category"), f.get("category")); cats[k] = cats.get(k, 0) + 1
        catline = ", ".join(f"{n} {k}" for k, n in sorted(cats.items(), key=lambda kv: -kv[1]))
        fast = [f for f in fl if f["_bucket"] in ("daily", "weekly")]
        ans = (f"{fcount(len(fl))} we track offer {label}: {nlist([f['name'] for f in fl])}. The highest PA Score among them is {fl[0]['name']} ({fl[0]['_score']:.1f}/10)"
               + (f", and the cheapest entry is {cheap['name']} at {money(cheap['_fee'], cheap.get('fee_currency'))}." if cheap else ".")
               + (f" {fcount(len(fast))} pay{'s' if len(fast) == 1 else ''} out daily or weekly." if fast else ""))
        others = lambda f: e(", ".join(p for p in f["_platforms"] if not m(p.lower()))[:90]) or '<small>only this</small>'
        t = gtable(fl, [FIRMCOL, SCORECOL, ("Type", lambda f: e(CAT_LABEL.get(f.get("category"), "")), ""), ("From", lambda f: mh(f["_fee"], f.get("fee_currency")), "num n"),
                        ("Split", lambda f: show(f.get("profit_split")), ""), ("Payouts", lambda f: e(BUCKET_LABEL.get(f["_bucket"], "")) or NIL, ""), ("Other platforms", others, "wide")], f"Prop firms on {label}")
        secs = [(f"{label} prop firms, ranked", t), (f"About {label}", f"<p>{e(blurb)}</p><p>Firms on {e(label)} in our data: {e(catline)}.</p>")]
        if unknown: secs.append(("Platform not published", f"<p class=\"small\">{e(nlist([f['name'] for f in unknown]))}: platform list not in our dataset yet, so they are left out rather than guessed.</p>"))
        qa = [(f"Which prop firms use {label}?", ans), (f"What is the cheapest {label} prop firm?", f"{cheap['name']}, from {money(cheap['_fee'], cheap.get('fee_currency'))}." if cheap else "No fee data yet.")]
        rel = "".join(f'<li><a href="{url("/platforms/" + s2 + "/")}"><span>{e(l2)} prop firms</span></a></li>' for s2, l2, _, _ in PLATFORMS if s2 != slug)
        prog_shell(path, [("Home", "/"), ("By platform", "/platforms/"), (label, path)], f"{label} prop firms ({YEAR_NOW})",
                   f"{label} Prop Firms {YEAR_NOW}: {len(fl)} Firms Ranked | PropAnalyse",
                   f"{len(fl)} prop firms that offer {label}, ranked by PA Score with fees, profit split, payout cycle and the other platforms each firm supports.",
                   ans, [f'<b class="n">{len(fl)}</b> firms', f'From <b class="n">{money(cheap["_fee"], cheap.get("fee_currency")) if cheap else "n/a"}</b>'], secs, qa, noindex=(len(fl) < 2), rel=rel)
        entries.append((path, label, blurb.split(". ")[0] + ".", len(fl), "firms"))
    hub_shell("/platforms/", [("Home", "/"), ("By platform", "/platforms/")], "Prop firms by trading platform", f"Prop Firms by Platform ({YEAR_NOW}): MT5, cTrader, TradingView, NinjaTrader | PropAnalyse",
              "Prop firms grouped by trading platform: MT5, MT4, cTrader, Match-Trader, TradeLocker, DXtrade, TradingView, NinjaTrader, Tradovate, Rithmic, Bybit.",
              "Pick the platform you already trade on. Each list is ranked by the same PA Score.", entries)

# ---------------- account sizes ----------------
SIZES = [5000, 10000, 25000, 50000, 100000, 200000]
def ksz(s): return f"{s // 1000}K"
def size_pages():
    entries = []
    for s in SIZES:
        rows = sorted([f for f in FIRMS if fee_at(f, s)], key=lambda f: fee_at(f, s))
        if not rows: continue
        path = f"/sizes/{ksz(s).lower()}/"
        P = lambda f, s=s: prog_at(f, s)[0]
        fees = [fee_at(f, s) for f in rows]
        med = statistics.median(fees)
        bytype = {}
        for f in FIRMS:
            if (f.get("fee_currency") or "USD") != "USD": continue
            for p in as_list(f.get("programs")):
                for sf in as_list(p.get("sizes_fees")):
                    if num(sf.get("size")) == s and num(sf.get("fee")):
                        bytype.setdefault(str(p.get("type") or "other"), []).append(num(sf["fee"]))
        tline = "; ".join(f"{t}: median {money(statistics.median(v))} across {len(v)} programs" for t, v in sorted(bytype.items()) if len(v) >= 2)
        a, z = rows[0], rows[-1]
        cry = [f for f in rows if "crypto" in f["_assets"]]
        mon = [f for f in rows if f["_x"].get("monthly_fee")]
        ans = (f"{fcount(len(rows))} we track sell a ${ksz(s)} account. The cheapest is {a['name']}'s {P(a).get('name')} at {money(fee_at(a, s), a.get('fee_currency'))}"
               f" ({money(fee_at(a, s) / (s / 1000), a.get('fee_currency'))} per $1K). The median is {money(med)}, and the most expensive is {z['name']} at {money(fee_at(z, s), z.get('fee_currency'))}."
               + (f" Cheapest firm with crypto: {cry[0]['name']} at {money(fee_at(cry[0], s), cry[0].get('fee_currency'))}." if cry and cry[0] is not a else "")
               + (f" {nlist([f['name'] for f in mon])} bill{'s' if len(mon) == 1 else ''} monthly, so that price repeats until you pass." if mon else ""))
        t = gtable(rows, [("#", lambda f: f'<span class="n">{rows.index(f) + 1}</span>', "n"), FIRMCOL, ("Program", lambda f: e(P(f).get("name") or "") + f'<small>{e(P(f).get("type") or "")}</small>', ""),
                          ("Fee", lambda f: mh(fee_at(f, s), f.get("fee_currency")) + ('<small>billed monthly</small>' if f["_x"].get("monthly_fee") else ''), "num n"),
                          ("Per $1K", lambda f: CUR.get(f.get("fee_currency") or "USD", "$") + f"{fee_at(f, s) / (s / 1000):.2f}", "num n"),
                          ("Target", lambda f: show(P(f).get("profit_target")), "n"), ("Daily / Max", lambda f: e(f'{P(f).get("max_daily_loss") or "-"} / {P(f).get("max_drawdown") or "-"}'), "n"),
                          ("Split", lambda f: show(P(f).get("profit_split")), ""), SCORECOL], f"${ksz(s)} prop firm challenges")
        secs = [(f"Every ${ksz(s)} challenge, cheapest first", t + '<p class="small">One row per firm: its cheapest program at this size. FTMO prices in EUR and is not converted.</p>')]
        if tline: secs.append(("By challenge type", f"<p>{e(tline)} (USD-priced programs only).</p>"))
        secs.append(("Price is not cost", f"<p>The cheapest row often carries the tightest daily limit or a trailing drawdown. Refund-on-first-payout and retry discounts change the real cost more than a small price gap. Run your numbers in the <a href=\"{url('/tools/true-cost/')}\">true-cost calculator</a>.</p>"))
        qa = [(f"What is the cheapest ${ksz(s)} prop firm challenge?", f"{a['name']}'s {P(a).get('name')} at {money(fee_at(a, s), a.get('fee_currency'))}, on our latest check."),
              (f"How much does a ${ksz(s)} prop firm account cost?", f"Across {len(rows)} firms the median ${ksz(s)} fee is {money(med)}, ranging from {money(fee_at(a, s), a.get('fee_currency'))} to {money(fee_at(z, s), z.get('fee_currency'))}.")]
        rel = "".join(f'<li><a href="{url("/sizes/" + ksz(x).lower() + "/")}"><span>${ksz(x)} challenges</span></a></li>' for x in SIZES if x != s)
        if s == 100000: rel += f'<li><a href="{url("/guides/cheapest-100k-prop-firm-challenge/")}"><span>Cheapest $100K challenge guide</span></a></li>'
        prog_shell(path, [("Home", "/"), ("By account size", "/sizes/"), (f"${ksz(s)}", path)], f"${ksz(s)} prop firm challenges compared",
                   f"Cheapest ${ksz(s)} Prop Firm Challenge ({YEAR_NOW}): {len(rows)} Firms by Price | PropAnalyse",
                   f"Every ${ksz(s)} prop firm challenge we track, cheapest first: {len(rows)} firms from {money(fee_at(a, s), a.get('fee_currency'))}, with target, drawdown, split and cost per $1K.",
                   ans, [f'<b class="n">{len(rows)}</b> firms', f'From <b class="n">{money(fee_at(a, s), a.get("fee_currency"))}</b>', f'Median <b class="n">{money(med)}</b>'], secs, qa, noindex=(len(rows) < 4), rel=rel)
        entries.append((path, f"${ksz(s)} accounts", f"Cheapest: {a['name']} at {money(fee_at(a, s), a.get('fee_currency'))}.", len(rows), "firms"))
    hub_shell("/sizes/", [("Home", "/"), ("By account size", "/sizes/")], "Prop firm challenges by account size", f"Prop Firm Challenges by Account Size ({YEAR_NOW}): $5K to $200K | PropAnalyse",
              "Prop firm challenge prices at $5K, $10K, $25K, $50K, $100K and $200K, cheapest first, with cost per $1K.", "Same firms, one size at a time. Each page lists the cheapest program at every firm that sells that size.", entries)

def programmatic():
    country_pages(); platform_pages(); size_pages()

FOOT_EXTRA[:0] = [("/countries/", "By country"), ("/platforms/", "By platform"), ("/sizes/", "By account size")]
_seo_prev = seo_files
def seo_files():
    _seo_prev()
    L = ["", "## By country"] + [f"- [Prop firms accepting {n.replace('the ', '')}]({ABS}/countries/{s}/)" for s, n, _ in COUNTRIES if f"/countries/{s}/" in PAGES and f"/countries/{s}/" not in NOINDEX]
    L += ["", "## By platform"] + [f"- [{l} prop firms]({ABS}/platforms/{s}/)" for s, l, _, _ in PLATFORMS if f"/platforms/{s}/" in PAGES and f"/platforms/{s}/" not in NOINDEX]
    L += ["", "## By account size"] + [f"- [${ksz(x)} challenges]({ABS}/sizes/{ksz(x).lower()}/)" for x in SIZES if f"/sizes/{ksz(x).lower()}/" in PAGES and f"/sizes/{ksz(x).lower()}/" not in NOINDEX]
    open(os.path.join(OUT, "llms.txt"), "a").write("\n".join(L) + "\n")
