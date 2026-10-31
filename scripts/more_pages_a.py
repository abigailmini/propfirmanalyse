# PropAnalyse page types, part A: offers, crypto hub + crypto rule sheets, rule-change tracker + RSS.

def offers():
    c, bl = crumbs([("Home", "/"), ("Offers", "/offers/")])
    withc = [f for f in RANKED if (f.get("discount_code") or {}).get("code")]
    without = [f for f in RANKED if not (f.get("discount_code") or {}).get("code")]
    rows = ""
    for f in withc:
        dc = f["discount_code"]; p = pct_off(dc); cur = f.get("fee_currency")
        after = mh(f["_fee"] * (1 - p / 100), cur) if (p and f["_fee"]) else '<span class="nil">see checkout</span>'
        lv = f.get("last_verified") or TODAY
        rows += (f'<tr><td class="c-firm"><a href="{url("/firms/" + f["slug"] + "/")}"><b>{e(f["name"])}</b></a><small>{e(", ".join(ASSET_LABEL.get(a, a) for a in f["_assets"][:3]))}</small></td>'
                 f'<td>{code_html(f, False)}</td><td class="dv">{e(dc.get("value") or "Discount")}</td><td class="num n">{mh(f["_fee"], cur)}</td><td class="num n">{after}</td>'
                 f'<td class="n nowrap"><time datetime="{e(lv)}">{nice_date(lv)}</time></td><td>{score_html(f)}</td><td class="c-act">{visit(f)}</td></tr>')
    table_ = (f'<div class="tablewrap"><table class="mini offers"><caption class="sr">Prop firm discount codes</caption><thead><tr><th scope="col">Firm</th><th scope="col">Code</th><th scope="col">Offer</th>'
              f'<th scope="col" class="num">Fee from</th><th scope="col" class="num">After code</th><th scope="col">Checked</th><th scope="col">PA Score</th><th scope="col"><span class="sr">Link</span></th></tr></thead><tbody>{rows}</tbody></table></div>')
    n = len(withc)
    body = f"""<div class="wrap">{c}<header class="ph"><h1>Prop firm discount codes</h1><p class="lede"><span class="n">{n}</span> of <span class="n">{len(FIRMS)}</span> firms publish a code right now. We only list codes the firm shows on its own site, with the date we checked. Codes never change a firm's score or its order on this page, which is sorted by PA Score.</p></header>
{table_ if rows else '<p class="empty">No public codes found at last check.</p>'}
<p class="legend"><span>"After code" applies a percentage code to the cheapest published fee. Fixed-amount and auto-applied codes show "see checkout".</span><span>Codes can expire without notice. The checkout price is the final word.</span></p>
<section class="block"><h2>How we check codes</h2><div class="prose"><p>Each code was read from the firm's homepage banner, pricing page or checkout on the date shown. We do not run "exclusive" codes in exchange for ranking. If we ever add a PropAnalyse code, it will be labelled as ours and the firm's score will stay the same.</p>
<p>A discount lowers the entry fee, but resets, activation fees and refund rules often matter more. The <a href="{url('/tools/true-cost/')}">true-cost calculator</a> includes them.</p></div></section>
<section class="block"><h2>No public code right now</h2><p class="inline-list">{''.join(f'<a href="{url("/firms/" + f["slug"] + "/")}">{e(f["name"])}</a>' for f in without)}</p></section></div>"""
    ld = {"@context": "https://schema.org", "@type": "ItemList", "name": "Prop firm discount codes", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "item": {"@type": "Offer", "name": f"{f['name']} code {f['discount_code']['code']}", "description": f["discount_code"].get("value") or "", "url": ABS + "/firms/" + f["slug"] + "/"}} for i, f in enumerate(withc)]}
    month = datetime.date.fromisoformat(TODAY).strftime('%B %Y')
    page("/offers/", f"Prop Firm Discount Codes ({month}): {n} Verified Codes | PropAnalyse", f"{n} prop firm discount codes checked on each firm's own site, with the price after the code. Sorted by PA Score, not by commission.", body, [bl, ld])
    redirect("/discounts/", "/offers/")

def redirect(path, to):
    d = os.path.join(OUT, path.strip("/")); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w").write(f'<!doctype html><meta charset=utf-8><title>Moved</title><link rel=canonical href="{ABS}{to}"><meta name=robots content=noindex><meta http-equiv=refresh content="0;url={url(to)}"><a href="{url(to)}">Moved here</a>')

# ---------------- crypto ----------------
def cval(v, kind=None):
    if v in (None, "", []): return NIL
    if isinstance(v, bool): return "Yes" if v else "No"
    if v == "restricted": return "Restricted"
    return show(v)
def crypto_row(f):
    cc = f["_c"]
    return (f'<tr><td class="c-firm"><a href="{url("/crypto/" + f["slug"] + "/")}"><b>{e(f["name"])}</b></a><small>{"Crypto-native" if is_native(f) else "Multi-asset"}</small></td>'
            f'<td>{score_html(f)}</td><td>{cval(cc.get("crypto_venue"))}</td><td>{cval(cc.get("instrument_type"))}</td><td class="num n">{cval(cc.get("crypto_pairs"))}</td>'
            f'<td>{cval(cc.get("crypto_leverage"))}</td><td>{cval(cc.get("weekend_crypto"))}</td><td>{cval(cc.get("crypto_payout"))}</td><td>{cval(cc.get("bots_allowed"))}</td>'
            f'<td class="num n">{mh(f["_fee"], f.get("fee_currency"))}</td><td class="c-act">{visit(f)}</td></tr>')
CRYPTO_HEAD = ('<thead><tr><th scope="col">Firm</th><th scope="col">PA Score</th><th scope="col">Venue</th><th scope="col">Instrument</th><th scope="col" class="num">Pairs</th>'
               '<th scope="col">Crypto leverage</th><th scope="col">Weekend</th><th scope="col">Crypto payout</th><th scope="col">Bots</th><th scope="col" class="num">From</th><th scope="col"><span class="sr">Link</span></th></tr></thead>')

def crypto_hub():
    c, bl = crumbs([("Home", "/"), ("Crypto prop firms", "/crypto/")])
    nat = [f for f in CRYPTO_FIRMS if is_native(f)]; multi = [f for f in CRYPTO_FIRMS if not is_native(f)]
    with_c = sum(1 for f in CRYPTO_FIRMS if f["_c"])
    top = nat[0] if nat else CRYPTO_FIRMS[0]
    cheapest = min((f for f in CRYPTO_FIRMS if f["_fee"] is not None), key=lambda f: f["_fee"])
    fastest = [f for f in CRYPTO_FIRMS if f["_bucket"] == "daily"]
    cpairs = [(a, b) for a, b in PAIRS if a in BY and b in BY and "crypto" in BY[a]["_assets"] and "crypto" in BY[b]["_assets"]]
    tbl = lambda fl, cap: f'<div class="tablewrap"><table class="mini crypto"><caption class="sr">{e(cap)}</caption>{CRYPTO_HEAD}<tbody>{"".join(crypto_row(f) for f in fl)}</tbody></table></div>'
    guides_l = "".join(f'<li><a href="{url("/guides/" + g["slug"] + "/")}"><span>{e(g["h1"])}</span></a></li>' for g in GUIDES if g.get("crypto"))
    body = f"""<div class="wrap">{c}<header class="ph"><h1>Crypto prop firms, rule by rule</h1>
<p class="lede">{len(CRYPTO_FIRMS)} firms in our dataset fund crypto trading. {len(nat)} are crypto-native, running perpetuals on exchange-style venues; {len(multi)} offer crypto CFDs next to forex on MT5-type platforms. The highest-scoring crypto-native firm is <a href="{url('/firms/' + top['slug'] + '/')}">{e(top['name'])}</a> ({top['_score']:.1f}). The cheapest entry is {e(cheapest['name'])} at {money(cheapest['_fee'], cheapest.get('fee_currency'))}.{(' ' + str(len(fastest)) + ' pay out daily or on demand.') if fastest else ''}</p>
<p class="facts"><span><b class="n">{len(CRYPTO_FIRMS)}</b> firms</span><span><b class="n">{with_c}</b> crypto rule sheets</span><span>Verified <b class="n"><time datetime="{e(TODAY)}">{nice_date(TODAY)}</time></b></span></p>
<p class="note">Browsing by account type? Firms whose main product is crypto perpetuals on an exchange account or an exchange-priced terminal are on <a href="{url('/crypto-exchange/')}">crypto exchange prop firms</a>. To see every firm that lists crypto in the full ranking, open it <a href="{url('/?mkt=crypto')}">with the crypto filter on</a>.</p></header>
<section class="block"><h2>Crypto-native firms</h2><p class="small">Built for crypto first: perpetual futures, exchange order books or exchange demo accounts, usually paid out in stablecoins.</p>{tbl(nat, "Crypto-native prop firms")}</section>
<section class="block"><h2>Multi-asset firms with crypto</h2><p class="small">Crypto is offered as CFDs alongside forex and indices. Leverage on crypto is usually much lower than on forex, and weekend rules vary.</p>{tbl(multi, "Multi-asset prop firms offering crypto")}</section>
<p class="legend"><span>{NIL} means the firm does not publish the figure, or we have not verified it yet. Open a firm for sources.</span><span>Same <a href="{url('/methodology/')}">PA Score</a> for every firm. FundedXYZ is ours and is disclosed.</span></p>
<section class="block lower2"><div><h2>Crypto head to head</h2><ul class="pairs">{"".join(pair_link(a, b) for a, b in cpairs)}</ul></div>
<div><h2>Crypto guides</h2><ul class="lists">{guides_l}<li><a href="{url('/glossary/#perpetual-futures')}"><span>What perpetual futures are</span></a></li></ul></div></section>
<section class="block"><h2>What to check before buying a crypto challenge</h2><div class="prose">
<p><b>Where your orders go.</b> Exchange-style firms route to a demo on Bybit, BloFin or their own terminal, which gives you real order-book behaviour and funding rates. CFD firms quote their own crypto prices with wider spreads and often close crypto for maintenance.</p>
<p><b>Leverage you will actually get.</b> Crypto-native firms often allow 50x to 100x. Multi-asset firms commonly cap crypto at 1:1 to 1:5 even when forex runs at 1:100. Size your risk to the drawdown, not to the leverage.</p>
<p><b>Weekends and gaps.</b> Crypto trades all weekend. Some firms let you hold through it and some do not. Check the weekend column before you plan swing trades.</p>
<p><b>How you get paid.</b> Most crypto-native firms pay in USDT or USDC. Check the minimum payout, any per-payout cap, and whether KYC comes before the first withdrawal.</p>
<p><b>Bots and copy trading.</b> Grid bots, arbitrage and copy trading are where most crypto accounts get breached. The rule sheets below list what each firm bans.</p></div></section></div>"""
    ld = [bl, {"@context": "https://schema.org", "@type": "ItemList", "name": "Crypto prop firms ranked by PA Score", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": ABS + "/crypto/" + f["slug"] + "/", "name": f["name"]} for i, f in enumerate(CRYPTO_FIRMS)]},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
              {"@type": "Question", "name": "What is the best crypto prop firm?", "acceptedAnswer": {"@type": "Answer", "text": f"On our published PA Score the top crypto-native firm is {top['name']} ({top['_score']:.1f}/10). Rankings use the same formula for every firm and are updated when rules change."}},
              {"@type": "Question", "name": "What is the cheapest crypto prop firm challenge?", "acceptedAnswer": {"@type": "Answer", "text": f"{cheapest['name']} has the lowest published entry fee among crypto firms in our dataset: {money(cheapest['_fee'], cheapest.get('fee_currency'))}."}}]}]
    page("/crypto/", f"Best Crypto Prop Firms {YEAR_NOW}: {len(CRYPTO_FIRMS)} Firms, Rules Compared | PropAnalyse", f"{len(CRYPTO_FIRMS)} crypto prop firms compared on venue, perps vs CFD, crypto leverage, weekend holding, bots and USDT payouts. Ranked by a published score.", body, ld)
    for f in CRYPTO_FIRMS: crypto_page(f)

def crypto_page(f):
    cc = f["_c"]; path = f"/crypto/{f['slug']}/"
    c, bl = crumbs([("Home", "/"), ("Crypto", "/crypto/"), (f["name"], path)])
    peers = [x for x in CRYPTO_FIRMS if x is not f]
    rows = [("Venue / platform", cval(cc.get("crypto_venue") or (", ".join(f["_platforms"]) if is_native(f) else None))), ("Instrument type", cval(cc.get("instrument_type"))),
            ("Crypto instruments", cval(cc.get("crypto_pairs"))), ("Examples", cval(cc.get("crypto_pairs_examples"))), ("Crypto leverage", cval(cc.get("crypto_leverage") or (f.get("leverage") if is_native(f) else None))),
            ("Weekend crypto trading", cval(cc.get("weekend_crypto"))), ("Crypto fees", cval(cc.get("crypto_fees"))), ("Min trade duration", cval(cc.get("min_trade_duration"))),
            ("Risk / position rule", cval(cc.get("max_position_or_risk_rule"))), ("Bots", cval(cc.get("bots_allowed"))), ("Copy trading", cval(cc.get("copy_trading"))),
            ("Banned strategies", cval(cc.get("banned_strategies"))), ("Payout methods", cval(cc.get("payout_methods") or f["_x"].get("payout_methods"))),
            ("Paid in crypto", cval(cc.get("crypto_payout"))), ("KYC before payout", cval(cc.get("kyc_before_payout")))]
    have = sum(1 for _, v in rows if v != NIL)
    core = [("Daily loss limit", show(f.get("max_daily_loss"))), ("Max drawdown", show(f.get("max_drawdown"))), ("Drawdown type", show(f.get("drawdown_type"))),
            ("Profit target", show(f.get("profit_target"))), ("Profit split", show(f.get("profit_split"))), ("Payout cycle", show(f.get("payout_frequency"))),
            ("Fees from", mh(f["_fee"], f.get("fee_currency")).replace(NA, NIL)), ("News trading", tri_label(f.get("news_trading")))]
    # how it sits against other crypto firms
    def rank_of(key, rev=True):
        vals = [(key(x), x["slug"]) for x in CRYPTO_FIRMS if key(x) is not None]
        if key(f) is None: return None
        vals.sort(key=lambda t: -t[0] if rev else t[0])
        return [s for _, s in vals].index(f["slug"]) + 1, len(vals)
    pos = [(lab, rank_of(k, r)) for lab, k, r in [("PA Score", lambda x: x["_score"], True), ("Entry fee (lowest first)", lambda x: x["_fee"], False),
                                                  ("Cost per $1K (lowest first)", cost_per_k, False), ("Headline split", lambda x: x["_split"], True)]]
    posh = "".join(f'<div><dt>{e(lab)}</dt><dd class="n">{("#" + str(r[0]) + " of " + str(r[1])) if r else NIL}</dd></div>' for lab, r in pos)
    intro = f"{f['name']} " + ("is a crypto-native prop firm" if is_native(f) else "is a multi-asset prop firm that also funds crypto") + "."
    if cc.get("crypto_venue"): intro += f" Crypto orders run on {cc['crypto_venue']}."
    if cc.get("instrument_type"): intro += f" Instruments are {cc['instrument_type']}."
    if cc.get("crypto_leverage"): intro += f" Crypto leverage: {cc['crypto_leverage']}."
    if cc.get("weekend_crypto") is not None: intro += " Weekend crypto trading is " + ("allowed." if cc["weekend_crypto"] else "not allowed.")
    if cc.get("crypto_payout"): intro += " Payouts can be taken in crypto."
    qa = [(f"Can you trade crypto on weekends with {f['name']}?", {True: "Yes, per the firm's rules.", False: "No, the firm does not allow weekend crypto trading or holding.", None: "The firm does not state it clearly; ask support before planning weekend trades."}[cc.get("weekend_crypto") if isinstance(cc.get("weekend_crypto"), bool) else None]),
          (f"What leverage does {f['name']} give on crypto?", (cc.get("crypto_leverage") or "Not published on the firm's site at our last check") + "."),
          (f"Does {f['name']} pay out in USDT or other crypto?", ("Payout methods listed: " + ", ".join(as_list(cc.get("payout_methods") or f["_x"].get("payout_methods"))) + ".") if (cc.get("payout_methods") or f["_x"].get("payout_methods")) else "Not published at our last check."),
          (f"Are trading bots allowed at {f['name']}?", {True: "Yes.", False: "No.", "restricted": "Only with restrictions; check the firm's rules.", None: "Not stated clearly by the firm."}.get(cc.get("bots_allowed"), "Not stated clearly by the firm."))]
    faqh = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in qa)
    srcs = "".join(f'<li><a href="{e(s)}" rel="nofollow noopener" target="_blank">{e(s)}</a></li>' for s in as_list(cc.get("sources")) or as_list(f.get("source_urls"))[:4])
    vs = "".join(f'<li><a href="{url("/crypto/" + x["slug"] + "/")}"><span>{e(x["name"])}</span><b class="n">{x["_score"]:.1f}</b></a></li>' for x in peers[:8])
    body = f"""<div class="wrap">{c}<header class="phead"><h1>{e(f['name'])} crypto rules</h1><p class="lede">{e(intro)}</p>
<div class="ctas">{visit(f, cls="btn")}<a class="btn line" href="{url('/firms/' + f['slug'] + '/')}">Full {e(f['name'])} review</a></div></header>
<div class="pgrid"><aside class="side"><div class="scorebox"><p class="big n">{f['_score']:.1f}<small>/10</small></p>{ticks(f['_score'], 0, "lg")}<p class="rk">Among <span class="n">{len(CRYPTO_FIRMS)}</span> crypto firms</p><dl class="comp">{posh}</dl></div>
<div class="cmpl"><h2>Other crypto firms</h2><ul class="lists">{vs}</ul></div></aside>
<div class="pmain">{spec("Crypto trading terms", rows)}{'' if cc else '<p class="note">Crypto-specific terms for this firm are still being verified. The core rules below apply to every instrument.</p>'}
{spec("Core rules (all instruments)", core)}<section class="block faq"><h2>FAQ</h2>{faqh}</section>
<section class="block"><h2>Sources</h2><p class="small">Checked <time datetime="{e(cc.get('checked') or f.get('last_verified') or TODAY)}">{nice_date(cc.get('checked') or f.get('last_verified') or TODAY)}</time>.</p><ol class="src">{srcs}</ol>{('<p class="small notes"><b>Notes.</b> ' + e(cc['notes']) + '</p>') if cc.get('notes') else ''}</section></div></div></div>"""
    ld = [bl, {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]}]
    if have < 4: NOINDEX.add(path)
    page(path, f"{f['name']} Crypto Rules {YEAR_NOW}: Leverage, Weekend, Bots, Payouts | PropAnalyse", f"{f['name']} crypto trading rules: venue, instrument type, crypto leverage, weekend holding, bots, payout in USDT. Sourced from the firm's own pages.", body, ld, "article",
         extra_head='<meta name="robots" content="noindex,follow">' if path in NOINDEX else "")

# ---------------- rule-change tracker ----------------
def news():
    CL = CHANGES
    c, bl = crumbs([("Home", "/"), ("Rule changes", "/news/")])
    dates = sorted({x["date"] for x in CL}, reverse=True)
    firms_changed = sorted({x["slug"] for x in CL})
    kinds = sorted({x["kind"] for x in CL})
    opts = "".join(f'<option value="{e(s)}">{e(BY[s]["name"] if s in BY else s)}</option>' for s in firms_changed if s)
    kopts = "".join(f'<option value="{e(k)}">{e(k)}</option>' for k in kinds)
    groups = ""
    for d in dates[:60]:
        rows = [x for x in CL if x["date"] == d]
        groups += f'<section class="block cday" id="d-{d}"><h2><time datetime="{d}">{nice_date(d)}</time> <span class="n cnt">{len(rows)} changes</span></h2>{change_table(rows)}</section>'
    body = f"""<div class="wrap">{c}<header class="ph"><h1>Prop firm rule changes</h1>
<p class="lede">Every change to a firm's fees, drawdown, split, payout terms or codes in our dataset, with the date we saw it and the old and new values side by side. The log is generated from the data, so it can't be edited after the fact. <span class="n">{len(CL)}</span> changes across <span class="n">{len(firms_changed)}</span> firms so far.</p>
<p class="ctas"><a class="btn line sm" href="{url('/news/feed.xml')}">{ic('rss')}RSS feed</a><a class="btn line sm" href="{url('/news/changes.json')}">JSON</a></p></header>
<form class="picker newsf" id="newsf" onsubmit="return false"><label class="fl"><span>Firm</span><select id="nf-firm"><option value="">All firms</option>{opts}</select></label>
<label class="fl"><span>Type</span><select id="nf-kind"><option value="">All types</option>{kopts}</select></label></form>
{groups or '<p class="empty">No changes recorded yet.</p>'}
<section class="block"><h2>How this log works</h2><div class="prose"><p>Each firm's record lives in <code>data/raw/</code>. Every build compares the dataset with the last snapshot and writes any differences to <code>data/changelog.json</code>, field by field. A null on the "Was" side means we recorded the figure for the first time. When a firm stops publishing a figure, the "Now" side reads "none".</p>
<p>The first entries were rebuilt from the dataset's git history, starting with our first fully verified snapshot on 26 Oct 2026. The <a href="{url('/updates/')}">verification log</a> shows when each firm was last checked.</p></div></section></div>
<script>(function(){{var f=document.getElementById('nf-firm'),k=document.getElementById('nf-kind');function run(){{var a=f.value,b=k.value;document.querySelectorAll('.changes tbody tr').forEach(function(r){{var ok=(!a||r.dataset.s===a)&&(!b||r.dataset.k===b);r.hidden=!ok}});document.querySelectorAll('.cday').forEach(function(s){{s.hidden=!s.querySelector('tbody tr:not([hidden])')}})}}f.onchange=k.onchange=run}})();</script>"""
    body = body.replace("<tr><td class=\"n nowrap\">", "<tr><td class=\"n nowrap\">")
    page("/news/", "Prop Firm Rule Changes: Dated Log of Fees, Drawdown & Payout Changes | PropAnalyse", f"Dated, field-level log of prop firm rule changes: {len(CL)} changes across {len(firms_changed)} firms, with old and new values. RSS and JSON feeds.", body, [bl],
         extra_head=f'<link rel="alternate" type="application/rss+xml" title="PropAnalyse rule changes" href="{ABS}/news/feed.xml">')
    # feeds
    os.makedirs(os.path.join(OUT, "news"), exist_ok=True)
    json.dump({"generated": TODAY, "source": ABS + "/news/", "changes": CL}, open(os.path.join(OUT, "news", "changes.json"), "w"), indent=1, ensure_ascii=False)
    items, seen = [], {}
    for x in CL: seen.setdefault((x["date"], x["slug"]), []).append(x)
    for (d, s), xs in list(seen.items())[:100]:
        nm = xs[0]["firm"]
        desc = "; ".join(f'{x["field"]}: {x["old"] or "none"} → {x["new"] or "none"}' for x in xs[:25])
        link = ABS + (f"/firms/{s}/#history" if s in BY else "/news/")
        pub = datetime.datetime.combine(datetime.date.fromisoformat(d), datetime.time(12)).strftime("%a, %d %b %Y %H:%M:%S +0000")
        items.append(f"<item><title>{html.escape(nm)}: {len(xs)} rule {'change' if len(xs) == 1 else 'changes'}</title><link>{link}</link><guid isPermaLink=\"false\">{d}-{s}-{len(xs)}</guid><pubDate>{pub}</pubDate><description>{html.escape(desc)}</description></item>")
    open(os.path.join(OUT, "news", "feed.xml"), "w").write(f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>PropAnalyse: prop firm rule changes</title><link>{ABS}/news/</link><description>Dated field-level changes to prop firm rules, fees and payouts.</description><language>en</language>{"".join(items)}</channel></rss>')
