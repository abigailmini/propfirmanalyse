# PropAnalyse /guides/: long-tail articles. Copy is ours; every number comes from data/firms.json at build time.

def fee_at(f, size):
    v = [num(sf.get("fee")) for p in as_list(f.get("programs")) for sf in as_list(p.get("sizes_fees")) if num(sf.get("size")) == size and num(sf.get("fee"))]
    return min(v) if v else None
def prog_at(f, size):
    best = None
    for p in as_list(f.get("programs")):
        for sf in as_list(p.get("sizes_fees")):
            if num(sf.get("size")) == size and num(sf.get("fee")) and (best is None or num(sf["fee"]) < best[1]): best = (p, num(sf["fee"]))
    return best
def flink(f, sub="/firms/"): return f'<a href="{url(sub + f["slug"] + "/")}">{e(f["name"])}</a>'
def gtable(rows, cols, cap):
    th = "".join(f'<th scope="col"{" class=num" if "num" in c else ""}>{e(l)}</th>' for l, _, c in cols)
    # mobile card hooks: rank column ("#") and the first other column (the firm) get roles; every cell carries its label
    rk = next((i for i, (l, _, _) in enumerate(cols) if l == "#"), None); fi = next(i for i in range(len(cols)) if i != rk)
    sc = next((i for i, (l, _, _) in enumerate(cols) if l in ("PA Score", "PA 评分")), None)
    role = lambda i: " gt-rk" if i == rk else (" gt-firm" if i == fi else (" gt-sc" if i == sc else ""))
    tb = "".join("<tr>" + "".join(f'<td class="{c}{role(i)}" data-label="{e(l)}">{fn(r)}</td>' for i, (l, fn, c) in enumerate(cols)) + "</tr>" for r in rows)
    return f'<div class="tablewrap"><table class="mini gt"><caption class="sr">{e(cap)}</caption><thead><tr>{th}</tr></thead><tbody>{tb}</tbody></table></div>'
def nlist(names): return ", ".join(names[:-1]) + (" and " if len(names) > 1 else "") + names[-1] if names else "none"
FIRMCOL = ("Firm", lambda f: flink(f), "")
SCORECOL = ("PA Score", lambda f: f'<b class="n">{f["_score"]:.1f}</b>', "n")

def g_best_crypto():
    fl = CRYPTO_FIRMS; nat = [f for f in fl if is_native(f)]
    top3 = [f["name"] for f in nat[:3]]
    ans = f"The best crypto prop firms on our published score are {nlist(top3)} among crypto-native firms. {fl[0]['name']} leads once multi-asset firms with crypto CFDs are included ({fl[0]['_score']:.1f}/10). We rank {len(fl)} firms that fund crypto with one formula, and FundedXyz, which we own, gets no special treatment."
    t = gtable(fl, [("#", lambda f: f'<span class="n">{fl.index(f) + 1}</span>', "n"), FIRMCOL, SCORECOL, ("Type", lambda f: "Crypto-native" if is_native(f) else "Multi-asset", ""),
                    ("From", lambda f: mh(f["_fee"], f.get("fee_currency")), "num n"), ("Split", lambda f: show(f.get("profit_split")), ""), ("Payouts", lambda f: e(BUCKET_LABEL.get(f["_bucket"], "")) or NIL, ""),
                    ("Crypto rules", lambda f: f'<a href="{url("/crypto/" + f["slug"] + "/")}">Sheet</a>', "")], "Crypto prop firms ranked")
    secs = [("The ranking", t),
            ("Crypto-native or multi-asset?", f"<p>Crypto-native firms ({nlist([f['name'] for f in nat])}) give you perpetual futures on exchange-style venues, high leverage and stablecoin payouts. Multi-asset firms list crypto as CFDs next to forex. That suits you if crypto is one market among several, but expect lower crypto leverage and wider spreads.</p>"),
            ("What moves a crypto firm up or down", "<p>Trust carries 30% of the score, so young crypto firms with few Trustpilot reviews start behind long-running forex firms. That is deliberate: track record is the one thing a new firm can't buy. Cost per $1K and payout speed are where crypto-native firms tend to score well.</p>"),
            ("Before you buy", f"<p>Open the firm's crypto rule sheet. It shows the venue, weekend rules, bot bans and payout method in one place. Then run the fee through the <a href=\"{url('/tools/true-cost/')}\">true-cost calculator</a> with an honest number of attempts.</p>")]
    faq_ = [("Which crypto prop firm is the most trusted?", "Trust in our score combines Trustpilot rating and review volume. " + max(fl, key=lambda f: f["_comp"]["trust"])["name"] + " has the highest trust component among crypto firms."),
            ("Do crypto prop firms pay in USDT?", "Most crypto-native firms pay in USDT or USDC. See our USDT payouts guide for the per-firm list.")]
    return ans, secs, faq_

def g_no_time_limit():
    no = [f for f in RANKED if f["_x"].get("has_time_limit") is False]; yes = [f for f in RANKED if f["_x"].get("has_time_limit") is True]
    unk = [f for f in RANKED if f["_x"].get("has_time_limit") is None]
    ans = f"{len(no)} of the {len(FIRMS)} firms we track publish no time limit on their evaluations: {nlist([f['name'] for f in no])}." if no else "None of the firms we have verified so far publishes an unlimited evaluation; see the table for details."
    if yes: ans += f" {len(yes)} still set a deadline ({nlist([f['name'] for f in yes])})."
    cols = [FIRMCOL, SCORECOL, ("Time limit", lambda f: show(f["_x"].get("time_limit")), ""), ("Min days", lambda f: show(f.get("min_trading_days")), "n"), ("From", lambda f: mh(f["_fee"], f.get("fee_currency")), "num n")]
    secs = [("No time limit", gtable(no, cols, "Prop firms with no time limit") if no else "<p>None verified yet.</p>"),
            ("With a time limit", gtable(yes, cols, "Prop firms with a time limit") if yes else "<p>None in our verified set.</p>"),
            ("Why it matters", f"<p>A deadline pushes you to oversize near the end, which is how most accounts breach. Without one, a slow, steady strategy works: 0.3% a day still clears an 8% target in about 27 trading days. Use the <a href=\"{url('/tools/profit-target/')}\">profit-target calculator</a> to check your own pace.</p>"
             "<p>Watch for inactivity rules. A firm can drop the deadline but still close accounts with no trades for 30 days.</p>")]
    if unk: secs.append(("Not yet verified", "<p class=\"small\">" + e(", ".join(f["name"] for f in unk)) + ": time-limit terms not yet in our dataset.</p>"))
    return ans, secs, [("Do prop firms still have time limits?", "Most large firms dropped them between 2023 and 2025, but some programs, especially instant or promotional ones, still set deadlines. Check the program, not only the firm.")]

def g_cheapest_100k():
    rows = sorted([f for f in FIRMS if fee_at(f, 100000)], key=lambda f: fee_at(f, 100000))
    one = [f for f in rows if not f["_x"].get("monthly_fee")]
    a = one[0] if one else (rows[0] if rows else None)
    subs = [f for f in rows if f["_x"].get("monthly_fee")]
    ans = (f"The cheapest one-time $100K challenge we track is {a['name']}'s {prog_at(a, 100000)[0].get('name')} at {money(fee_at(a, 100000), a.get('fee_currency'))}. "
           + (f"Futures firms billed monthly ({nlist([f['name'] for f in subs])}) can look cheaper, but you pay that price every month until you pass. " if subs else "") +
           f"{len(rows)} firms sell a $100K account, and the most expensive costs {money(fee_at(rows[-1], 100000), rows[-1].get('fee_currency'))}. The sticker price is only part of it, so the table also shows target, drawdown and split for the cheapest program at each firm.") if a else "No $100K data."
    mon = lambda f: '<small>billed monthly</small>' if f["_x"].get("monthly_fee") else ''
    t = gtable(rows, [FIRMCOL, ("Program", lambda f: e(prog_at(f, 100000)[0].get("name") or ""), ""), ("Fee", lambda f: mh(fee_at(f, 100000), f.get("fee_currency")) + mon(f), "num n"),
                      ("Target", lambda f: show(prog_at(f, 100000)[0].get("profit_target")), "n"), ("Daily / Max", lambda f: e(f'{prog_at(f, 100000)[0].get("max_daily_loss") or "-"} / {prog_at(f, 100000)[0].get("max_drawdown") or "-"}'), "n"),
                      ("Split", lambda f: show(prog_at(f, 100000)[0].get("profit_split")), ""), SCORECOL], "Cheapest $100K challenges")
    med = sorted(fee_at(f, 100000) for f in rows)[len(rows) // 2] if rows else 0
    secs = [("$100K challenges, cheapest first", t),
            ("Reading the table", f"<p>The median $100K fee in our set is {money(med)}. The cheapest programs often pair the low price with a tighter daily limit, a trailing drawdown or a lower starting split. Two-step programs are usually cheaper than one-step at the same size. FTMO prices in euros, and we don't convert.</p>"),
            ("Count the retries", f"<p>A $100K challenge you pass on the third attempt costs three fees unless the firm discounts retries. Some firms refund the fee with your first payout. Put both into the <a href=\"{url('/tools/true-cost/')}\">true-cost calculator</a>.</p>")]
    return ans, secs, [("What is the cheapest 100K prop firm challenge?", ans.split(". ")[0] + "."), ("Is a cheap challenge worth it?", "Only if the rules suit your style. A tight daily limit or trailing drawdown can make a cheap challenge cost more in retries.")]

def g_fast_payouts():
    rows = [f for f in RANKED if f["_bucket"] in ("daily", "weekly")]
    ans = f"{len(rows)} firms in our dataset pay out daily, on demand or weekly on their headline plan: {nlist([f['name'] for f in rows])}." 
    fd = sorted([f for f in FIRMS if num(f.get("first_payout_days")) is not None], key=lambda f: num(f["first_payout_days"]))
    if fd: ans += f" The shortest published wait for a first payout is {fd[0]['name']} at {int(num(fd[0]['first_payout_days']))} days."
    t = gtable(rows, [FIRMCOL, ("Cycle", lambda f: e(BUCKET_LABEL[f["_bucket"]]), ""), ("First payout (days)", lambda f: show(f.get("first_payout_days")), "num n"), ("Payout terms", lambda f: show(f.get("payout_frequency")), "wide"), SCORECOL], "Fast-payout prop firms")
    secs = [("Daily, on-demand and weekly payouts", t),
            ("Cycle is not speed", "<p>An on-demand cycle can still come with a minimum profit, a per-payout cap or a processing window. A bi-weekly firm that pays the same day can beat a daily firm that takes five business days to process. Read the terms column.</p>"),
            ("First payout vs later payouts", "<p>Most firms make you wait longer for the first withdrawal, often 14 days or a minimum number of trading days, and then speed up. Where the firm publishes the wait, we show it.</p>")]
    return ans, secs, [("Which prop firm pays out the fastest?", ans)]

def g_static_trailing():
    st = [f for f in RANKED if "static" in str(f.get("drawdown_type") or "").lower()]; tr = [f for f in RANKED if "trail" in str(f.get("drawdown_type") or "").lower()]
    ans = (f"Static drawdown fixes your loss floor relative to the starting balance. Trailing drawdown raises the floor every time your equity makes a new high. "
           f"In our dataset {len(st)} firms use static drawdown on their headline plan and {len(tr)} use a trailing type. Futures firms are mostly trailing or end-of-day trailing.")
    ex = ("<p><b>Worked example, $100K account with 10% max drawdown.</b> Static: the floor is $90,000 forever. Trailing: you run to $106,000, the floor rises to $96,000, "
          "and a pullback to $96,000 ends the account even though you are still $6,000 up. End-of-day trailing only moves the floor on the daily close, so an intraday spike to $106,000 that closes at $102,000 moves it to $92,000.</p>"
          f"<p>Try your own numbers in the <a href=\"{url('/tools/drawdown/')}\">drawdown calculator</a>.</p>")
    cols = [FIRMCOL, ("Drawdown", lambda f: show(f.get("drawdown_type")), ""), ("Daily / Max", lambda f: dd_html(f), "n"), SCORECOL]
    secs = [("The difference", ex), ("Firms with static drawdown", gtable(st, cols, "Static drawdown firms")), ("Firms with trailing drawdown", gtable(tr, cols, "Trailing drawdown firms")),
            ("Which suits you", "<p>Static drawdown suits swing traders and anyone who lets winners run, because giving back open profit doesn't tighten the limit. Trailing drawdown suits scalpers who bank profit quickly. If you hold trades that swing in and out of profit, a trailing limit will hurt you.</p>")]
    return ans, secs, [("Is trailing drawdown bad?", "Not always, but it is stricter. Many firms stop trailing once the floor reaches the starting balance, after which it behaves like static."), ("Do any prop firms use static drawdown?", f"Yes: {nlist([f['name'] for f in st[:8]])}, among others.")]

def g_news():
    ok = [f for f in RANKED if tri(f.get("news_trading")) is True]; rs = [f for f in RANKED if tri(f.get("news_trading")) == "restricted"]; no = [f for f in RANKED if tri(f.get("news_trading")) is False]
    ans = f"{len(ok)} of {len(FIRMS)} firms we track allow news trading on their published rules: {nlist([f['name'] for f in ok])}. {len(rs)} restrict it on some programs or windows, and {len(no)} ban it."
    cols = [FIRMCOL, ("News", lambda f: tri_label(f.get("news_trading")), ""), ("Weekend", lambda f: tri_label(f.get("weekend_holding")), ""), ("Drawdown", lambda f: show(f.get("drawdown_type")), ""), SCORECOL]
    secs = [("News trading allowed", gtable(ok, cols, "News trading allowed")), ("Restricted or banned", gtable(rs + no, cols, "News trading restricted") if rs or no else "<p>None.</p>"),
            ("How restrictions usually work", "<p>Typical rules ban opening or closing trades within 2 to 5 minutes of a high-impact release, often only on funded accounts. Some firms let you hold through news but cancel profits from trades opened inside the window. The rule wording on the firm's site decides it, so check before NFP or CPI.</p>")]
    return ans, secs, [("Can you trade news with a prop firm?", ans)]

def g_one_two():
    def progs(t): return [(f, p) for f in FIRMS for p in as_list(f.get("programs")) if str(p.get("type") or "").lower() == t]
    def stat(t):
        ps = progs(t); fees = [num(sf["fee"]) for f, p in ps for sf in as_list(p.get("sizes_fees")) if num(sf.get("size")) == 100000 and num(sf.get("fee")) and not f.get("fee_currency")]
        dls = [first_pct(p.get("max_daily_loss")) for f, p in ps if first_pct(p.get("max_daily_loss")) is not None]
        mds = [first_pct(p.get("max_drawdown")) for f, p in ps if first_pct(p.get("max_drawdown")) is not None]
        md = lambda v: sorted(v)[len(v) // 2] if v else None
        return {"n": len(ps), "fee": md(fees), "dl": md(dls), "mdd": md(mds), "fees_n": len(fees)}
    a, b = stat("1-step"), stat("2-step")
    fmt = lambda v, s="%": (f"{v:g}{s}" if v is not None else "n/a")
    ans = (f"Across the {a['n']} one-step and {b['n']} two-step programs in our dataset, the median $100K fee is {money(a['fee']) if a['fee'] else 'n/a'} for one-step and {money(b['fee']) if b['fee'] else 'n/a'} for two-step. "
           f"Median limits are {fmt(a['dl'])} daily / {fmt(a['mdd'])} max for one-step, against {fmt(b['dl'])} / {fmt(b['mdd'])} for two-step. One-step is faster. Two-step usually gives you more room to lose.")
    tbl = (f'<div class="tablewrap"><table class="mini gt"><thead><tr><th scope="col"></th><th scope="col" class="num">One-step</th><th scope="col" class="num">Two-step</th></tr></thead><tbody>'
           f'<tr><th scope="row">Programs in dataset</th><td class="num n">{a["n"]}</td><td class="num n">{b["n"]}</td></tr>'
           f'<tr><th scope="row">Median $100K fee (USD-priced)</th><td class="num n">{money(a["fee"]) if a["fee"] else "n/a"}</td><td class="num n">{money(b["fee"]) if b["fee"] else "n/a"}</td></tr>'
           f'<tr><th scope="row">Median daily loss limit</th><td class="num n">{fmt(a["dl"])}</td><td class="num n">{fmt(b["dl"])}</td></tr>'
           f'<tr><th scope="row">Median max drawdown</th><td class="num n">{fmt(a["mdd"])}</td><td class="num n">{fmt(b["mdd"])}</td></tr></tbody></table></div>')
    both = [f for f in RANKED if "1-step" in f["_types"] and "2-step" in f["_types"]]
    secs = [("The numbers", tbl), ("When one-step wins", "<p>You trade a proven, consistent system and want funding fast. One phase means one fee and fewer days at risk of a rule breach. The trade-off is usually a tighter drawdown, often 6% max instead of 10%.</p>"),
            ("When two-step wins", "<p>You need room. A 10% max drawdown with a 5% daily limit survives a bad week that would end most one-step accounts. Each phase has a lower target, and the fee per $1K is often lower too.</p>"),
            ("Firms that sell both", f"<p>{', '.join(flink(f) for f in both)}. Open the review's fee matrix to compare the two programs at the same size.</p>")]
    return ans, secs, [("Is a one-step or two-step challenge easier?", "Neither is easier for everyone. One-step has one target but usually tighter limits. Two-step has two smaller targets and more room for drawdown.")]

def g_refunds():
    rows = [f for f in RANKED if f["_x"].get("refund_policy")]; yes = [f for f in rows if f["_x"].get("fee_refundable") is True]
    ans = f"{len(yes)} of the {len(rows)} firms with a published refund policy in our dataset return the challenge fee, usually with the first or a later payout: {nlist([f['name'] for f in yes])}." if rows else "Refund data is still being verified."
    t = gtable(rows, [FIRMCOL, ("Refunded?", lambda f: {True: "Yes", False: "No"}.get(f["_x"].get("fee_refundable"), NIL), ""), ("Policy", lambda f: show(f["_x"].get("refund_policy")), "wide"), ("Retry / reset", lambda f: show(f["_x"].get("reset_fee")), "wide")], "Prop firm refund policies")
    secs = [("Refund and retry terms", t), ("Read the condition", "<p>\"Refundable\" almost always means refunded with a payout, never refunded if you fail. Some firms pay it back on the first payout and some on the third or fourth. A few only refund on certain programs.</p>"),
            ("Put it in the maths", f"<p>A refunded fee only helps if you reach a payout. The <a href=\"{url('/tools/true-cost/')}\">true-cost calculator</a> subtracts the refund from your net cost when you tick the box.</p>")]
    return ans, secs, [("Do prop firms refund the challenge fee?", ans)]

def g_futures_50k():
    fut = [f for f in RANKED if "futures" in f["_assets"]]
    def tot(f):
        a = fee_at(f, 50000)
        if a is None: return None
        return a + (num(f["_x"].get("activation_fee")) or 0)
    rows = sorted([f for f in fut if fee_at(f, 50000)], key=lambda f: tot(f))
    a = rows[0] if rows else None
    ans = (f"The cheapest $50K futures evaluation in our dataset is {a['name']} at {money(fee_at(a, 50000))}" + (f" plus a {money(num(a['_x']['activation_fee']))} activation fee" if num(a["_x"].get("activation_fee")) else "") +
           f". We compare {len(rows)} futures firms on fee plus activation, the true entry price at futures firms.") if a else "No 50K futures data."
    t = gtable(rows, [FIRMCOL, ("50K fee", lambda f: mh(fee_at(f, 50000)) + ('<small>per month</small>' if f["_x"].get("monthly_fee") else ''), "num n"), ("Activation", lambda f: mh(num(f["_x"].get("activation_fee"))) if num(f["_x"].get("activation_fee")) else (NIL if f["_x"].get("activation_fee") is None else "None"), "num n"),
                      ("Fee + activation", lambda f: mh(tot(f)), "num n"), ("Reset (50K)", lambda f: mh(num(f["_x"].get("reset_fee_usd"))) if num(f["_x"].get("reset_fee_usd")) else show(f["_x"].get("reset_fee")), ""),
                      ("Drawdown", lambda f: show(f.get("drawdown_type")), ""), SCORECOL], "Cheapest 50K futures evaluations")
    secs = [("$50K futures evaluations", t), ("Monthly fees and activation", "<p>Many futures firms bill the evaluation monthly until you pass, then charge a one-time activation fee. A two-month pass at a $100-a-month firm with an $85 activation fee costs $285, not $100. Where the firm publishes it, we show the activation fee. Missing values mean not published.</p>"),
            ("Drawdown at futures firms", f"<p>Futures firms mostly use intraday trailing or end-of-day trailing drawdown, measured in dollars, not percent. Read our <a href=\"{url('/guides/static-vs-trailing-drawdown/')}\">static vs trailing guide</a> before you choose.</p>")]
    return ans, secs, [("What is the cheapest futures prop firm?", ans)]

def g_usdt():
    rows = [f for f in CRYPTO_FIRMS if f["_c"] or f["_x"].get("payout_methods")]
    pm = lambda f: as_list(f["_c"].get("payout_methods") or f["_x"].get("payout_methods"))
    cry = [f for f in rows if f["_c"].get("crypto_payout") is True or any(re.search(r"usdt|usdc|crypto|btc|eth", str(m), re.I) for m in pm(f))]
    ans = f"{len(cry)} crypto-capable firms in our dataset publish crypto payouts (USDT, USDC or other coins): {nlist([f['name'] for f in cry])}." if cry else "Crypto payout data is still being verified."
    t = gtable(rows, [FIRMCOL, ("Payout methods", lambda f: show(pm(f)) if pm(f) else NIL, "wide"), ("Paid in crypto", lambda f: cval(f["_c"].get("crypto_payout")), ""),
                      ("KYC first", lambda f: cval(f["_c"].get("kyc_before_payout") if f["_c"].get("kyc_before_payout") is not None else f["_x"].get("kyc_before_payout")), ""), ("Cycle", lambda f: e(BUCKET_LABEL.get(f["_bucket"], "")) or NIL, ""), SCORECOL], "Crypto payout methods")
    secs = [("Payout methods by firm", t), ("Network and fees", "<p>USDT on TRC20 is cheap to receive, while ERC20 can cost several dollars in gas. Check which network the firm sends on and whether it passes the fee to you. Send a small first withdrawal to a wallet you control before moving larger amounts.</p>"),
            ("KYC still applies", "<p>Paying out in crypto doesn't mean anonymous. Most firms run identity checks before the first payout or before signing the funded contract.</p>")]
    return ans, secs, [("Which prop firms pay in USDT?", ans)]

GUIDES = [
 {"slug": "best-crypto-prop-firms", "h1": f"Best crypto prop firms ({YEAR_NOW})", "desc": "Crypto prop firms ranked by a published score: crypto-native perps firms and multi-asset firms with crypto, with fees, splits and payout cycles.", "fn": g_best_crypto, "crypto": True},
 {"slug": "crypto-prop-firms-usdt-payouts", "h1": "Crypto prop firms that pay out in USDT", "desc": "Which crypto prop firms pay out in USDT or USDC, payout methods per firm, KYC requirements and payout cycles.", "fn": g_usdt, "crypto": True},
 {"slug": "prop-firms-no-time-limit", "h1": "Prop firms with no time limit", "desc": "Prop firms whose evaluations have no deadline, which still set one, and the inactivity rules to watch.", "fn": g_no_time_limit},
 {"slug": "cheapest-100k-prop-firm-challenge", "h1": "Cheapest $100K prop firm challenge", "desc": "Every $100K prop firm challenge we track, cheapest first, with the target, drawdown and split of each program.", "fn": g_cheapest_100k},
 {"slug": "fastest-payout-prop-firms", "h1": "Prop firms with the fastest payouts", "desc": "Prop firms with daily, on-demand and weekly payouts, days to first payout and the payout terms that slow things down.", "fn": g_fast_payouts},
 {"slug": "static-vs-trailing-drawdown", "h1": "Static vs trailing drawdown, explained with numbers", "desc": "Static, trailing and end-of-day drawdown explained with a worked $100K example, plus which prop firms use each type.", "fn": g_static_trailing},
 {"slug": "prop-firms-that-allow-news-trading", "h1": "Prop firms that allow news trading", "desc": "Which prop firms allow trading through high-impact news, which restrict it, and how the restrictions usually work.", "fn": g_news},
 {"slug": "one-step-vs-two-step-challenge", "h1": "One-step vs two-step challenge: the numbers", "desc": "Median fees and drawdown limits of one-step vs two-step prop firm challenges across our dataset, and when each wins.", "fn": g_one_two},
 {"slug": "prop-firm-fee-refunds", "h1": "Prop firms that refund the challenge fee", "desc": "Prop firm refund and retry policies side by side: who refunds the challenge fee, when, and on which programs.", "fn": g_refunds},
 {"slug": "cheapest-futures-prop-firm-50k", "h1": "Cheapest $50K futures prop firm evaluation", "desc": "$50K futures prop firm evaluations compared on fee plus activation fee, reset price and drawdown type.", "fn": g_futures_50k},
]

def guides():
    c, bl = crumbs([("Home", "/"), ("Guides", "/guides/")])
    items = "".join(f'<li><a href="{url("/guides/" + g["slug"] + "/")}"><b>{e(g["h1"])}</b><span>{e(g["desc"])}</span><span class="cnt"></span>{ic("arrow")}</a></li>' for g in GUIDES)
    page("/guides/", "Prop Firm Guides: Data-Backed Answers | PropAnalyse", "Data-backed prop firm guides: best crypto prop firms, cheapest $100K challenge, no time limit, fastest payouts, drawdown types, refunds.",
         f'<div class="wrap">{c}<header class="ph"><h1>Guides</h1><p class="lede">Each guide answers one question with numbers from our dataset. When a firm changes its rules, the guide updates on the next build.</p></header><ul class="shortlists">{items}</ul></div>', [bl])
    for g in GUIDES:
        ans, secs, qa = g["fn"]()
        path = f"/guides/{g['slug']}/"
        c2, bl2 = crumbs([("Home", "/"), ("Guides", "/guides/"), (g["h1"], path)])
        sh = "".join(f'<section class="gsec"><h2>{e(h)}</h2>{b}</section>' for h, b in secs)
        faqh = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in qa)
        rel = "".join(f'<li><a href="{url("/guides/" + x["slug"] + "/")}"><span>{e(x["h1"])}</span></a></li>' for x in GUIDES if x is not g)[:4000]
        body = f"""<div class="wrap">{c2}<article class="guide"><header class="ph"><h1>{e(g['h1'])}</h1><p class="meta"><span>Updated <time datetime="{TODAY}">{nice_date(TODAY)}</time></span><span>Data: {len(FIRMS)} firms, verified from their own sites</span></p>
<p class="answer">{e(ans)}</p></header><div class="gbody">{sh}<section class="block faq"><h2>FAQ</h2>{faqh}</section>
<p class="small">Figures are pulled from our dataset at build time. Scores use the <a href="{url('/methodology/')}">published formula</a>. Changes are logged on <a href="{url('/news/')}">rule changes</a>.</p></div>
<aside class="grel"><h2>More guides</h2><ul class="lists">{rel}</ul></aside></article></div>"""
        ld = [bl2, {"@context": "https://schema.org", "@type": "Article", "headline": g["h1"], "description": g["desc"], "dateModified": TODAY, "datePublished": "2026-10-26",
                    "author": {"@type": "Organization", "name": "PropAnalyse", "url": ABS + "/"}, "publisher": {"@type": "Organization", "name": "PropAnalyse"}, "mainEntityOfPage": ABS + path},
              {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]}]
        page(path, f"{g['h1']} | PropAnalyse", g["desc"], body, ld, "article")
