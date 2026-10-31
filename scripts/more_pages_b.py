# PropAnalyse page types, part B: tools, quiz, glossary, FAQ, methodology, SEO files.

def tool_shell(path, name, h1, lede, form, out, explain, desc, title, faq_=None):
    c, bl = crumbs([("Home", "/"), ("Tools", "/tools/"), (name, path)])
    qa = faq_ or []
    faqh = ("<section class=\"block faq\"><h2>FAQ</h2>" + "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in qa) + "</section>") if qa else ""
    body = f"""<div class="wrap">{c}<header class="ph"><h1>{e(h1)}</h1><p class="lede">{lede}</p></header>
<div class="calc" data-tool="{path.strip('/').split('/')[-1]}"><form class="cform" onsubmit="return false">{form}</form><div class="cout" aria-live="polite">{out}</div></div>
<section class="block"><h2>How it works</h2><div class="prose">{explain}</div></section>{faqh}</div>
<script>window.PFA_FIRMS_URL="{url('/data/firms.json')}";window.PFA_BASE="{BASE}";</script><script src="{url('/assets/tools.js')}?v={ASSET_V}" defer></script>"""
    ld = [bl, {"@context": "https://schema.org", "@type": "WebApplication", "name": name, "url": ABS + path, "applicationCategory": "FinanceApplication", "operatingSystem": "Any", "offers": {"@type": "Offer", "price": 0, "priceCurrency": "USD"}, "isAccessibleForFree": True}]
    if qa: ld.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]})
    page(path, title, desc, body, ld)

def fld(i, lab, inp, hint=""):
    return f'<label class="fl" for="{i}"><span>{e(lab)}</span>{inp}{("<small>" + e(hint) + "</small>") if hint else ""}</label>'
def numin(i, v, step="any", mn="0", suffix=""):
    return f'<span class="ninp"><input type="number" inputmode="decimal" id="{i}" name="{i}" value="{v}" step="{step}" min="{mn}">{("<i>" + suffix + "</i>") if suffix else ""}</span>'
FIRM_PICK = lambda i="t-firm": f'<select id="{i}"><option value="">Custom (enter your own)</option>' + "".join(f'<option value="{f["slug"]}">{e(f["name"])}</option>' for f in sorted(FIRMS, key=lambda x: x["name"].lower())) + "</select>"

def tools():
    c, bl = crumbs([("Home", "/"), ("Tools", "/tools/")])
    T_ = [("true-cost", "True-cost calculator", "Fee, retries, resets, activation and refund: what it really costs to reach your first payout, and the profit you need to break even."),
          ("drawdown", "Drawdown calculator", "Your daily and overall loss floors in dollars, for static, trailing and end-of-day trailing drawdown."),
          ("profit-target", "Profit-target calculator", "Dollar targets per phase, what a payout at target is worth after the split, and a realistic day count."),
          ("/quiz/", "Find your firm", "Seven questions, filtered against every firm in our dataset. Runs in your browser.")]
    items = "".join(f'<li><a href="{url(s if s.startswith("/") else "/tools/" + s + "/")}"><b>{e(t)}</b><span>{e(d)}</span><span class="cnt"></span>{ic("arrow")}</a></li>' for s, t, d in T_)
    page("/tools/", "Prop Firm Calculators: True Cost, Drawdown, Profit Target | PropAnalyse", "Free prop firm calculators: true cost to first payout, drawdown limits in dollars and profit targets, prefilled with each firm's published rules.",
         f'<div class="wrap">{c}<header class="ph"><h1>Prop firm calculators</h1><p class="lede">Every calculator can load a firm\'s published rules from our open dataset, and every input can be changed. Nothing you type leaves your browser.</p></header><ul class="shortlists">{items}</ul></div>', [bl])
    # true cost
    form = (fld("t-firm", "Firm", FIRM_PICK()) + fld("t-prog", "Program and size", '<select id="t-prog" disabled><option>Pick a firm first</option></select>') +
            fld("t-fee", "Challenge fee", numin("t-fee", 100, suffix="$")) + fld("t-disc", "Discount code", numin("t-disc", 0, suffix="% off"), "Prefilled when the firm publishes a % code") +
            fld("t-att", "Attempts until you pass", numin("t-att", 2, "1", "1"), "Be honest. Most traders need more than one") +
            fld("t-retry", "Retry price", numin("t-retry", 100, suffix="% of fee"), "100% if the firm has no retry discount") +
            fld("t-act", "Activation fee after passing", numin("t-act", 0, suffix="$")) +
            '<label class="tog"><input type="checkbox" id="t-ref"><span>Fee refunded with first payout</span></label>' +
            fld("t-split", "Profit split", numin("t-split", 80, suffix="%")) + fld("t-gross", "Gross profit at first payout", numin("t-gross", 1000, suffix="$")))
    out = ('<dl class="res"><div><dt>Spent before funded</dt><dd class="n" id="o-spent">-</dd></div><div><dt>Refund at first payout</dt><dd class="n" id="o-ref">-</dd></div>'
           '<div class="hl"><dt>Net cost to first payout</dt><dd class="n" id="o-net">-</dd></div><div><dt>Break-even gross profit</dt><dd class="n" id="o-be">-</dd></div>'
           '<div class="hl"><dt>You keep from first payout</dt><dd class="n" id="o-keep">-</dd></div></dl><p class="small" id="o-note"></p>')
    explain = ("<p><b>Spent before funded</b> = fee after discount for the first attempt, plus each retry at the retry price, plus any activation fee. "
               "<b>Net cost</b> takes off the refund if the firm returns the fee with your first payout (we refund one fee, the passing attempt). "
               "<b>Break-even</b> is the gross profit you need so that your share covers the net cost. "
               "<b>You keep</b> is your share of the gross profit minus the net cost.</p><p>Picking a firm fills in its published fee, split, codes and refund rules from our dataset. "
               "Where the firm doesn't publish a figure the field keeps your value. Per-payout caps, minimum payouts and payout schedules are not modelled.</p>")
    tool_shell("/tools/true-cost/", "True-cost calculator", "Prop firm true-cost calculator", "What a challenge really costs once you count retries, activation fees and refunds, and how much profit you need before you are ahead.",
               form, out, explain, "Prop firm true-cost calculator: challenge fee, retries, resets, activation fee and refund, giving your net cost to first payout and break-even profit.",
               "Prop Firm True-Cost Calculator: Cost to First Payout | PropAnalyse",
               [("What is the true cost of a prop firm challenge?", "The fee for every attempt you need, plus any activation fee, minus any refund paid with your first payout. If you need two attempts at a $100 challenge with no retry discount, you have spent $200 before you are funded."),
                ("Do prop firms refund the challenge fee?", "Some do, usually with the first or a later payout. Others never refund. Our firm reviews list each firm's published refund policy.")])
    # drawdown
    form = (fld("d-firm", "Firm preset", FIRM_PICK("d-firm")) + fld("d-size", "Account size", numin("d-size", 100000, suffix="$")) +
            fld("d-daily", "Daily loss limit", numin("d-daily", 5, suffix="%")) + fld("d-max", "Max drawdown", numin("d-max", 10, suffix="%")) +
            fld("d-type", "Drawdown type", '<select id="d-type"><option value="static">Static (from starting balance)</option><option value="trailing">Trailing (follows highest equity)</option><option value="eod">End-of-day trailing (highest close)</option></select>') +
            '<label class="tog"><input type="checkbox" id="d-lock" checked><span>Trailing floor stops at the starting balance</span></label>' +
            fld("d-day", "Balance at start of today", numin("d-day", 100000, suffix="$")) + fld("d-high", "Highest equity / close so far", numin("d-high", 100000, suffix="$")) +
            fld("d-eq", "Current equity", numin("d-eq", 100000, suffix="$")))
    out = ('<dl class="res"><div><dt>Daily floor (today)</dt><dd class="n" id="o-dfl">-</dd></div><div><dt>Overall floor</dt><dd class="n" id="o-mfl">-</dd></div>'
           '<div class="hl"><dt>Binding floor</dt><dd class="n" id="o-bind">-</dd></div><div class="hl"><dt>Room before breach</dt><dd class="n" id="o-room">-</dd></div></dl>'
           '<div class="gauge" aria-hidden="true"><i id="o-bar"></i></div><p class="small" id="o-dnote"></p>')
    explain = ("<p><b>Static</b>: the overall floor is fixed at starting balance minus the max drawdown. <b>Trailing</b>: the floor sits a fixed distance below your highest equity and moves up with it. "
               "Many firms stop the trail once it reaches the starting balance. <b>End-of-day trailing</b> works the same way but only updates on the daily close, so intraday peaks don't count.</p>"
               "<p>The daily floor here is today's starting balance minus the daily limit, worked out on the account size. Some firms base it on the day's starting equity, or on the higher of balance and equity. Check the firm's rule wording.</p>")
    tool_shell("/tools/drawdown/", "Drawdown calculator", "Prop firm drawdown calculator", "Turn the percentages into dollar floors. See which limit binds first and how much room you have left right now.",
               form, out, explain, "Prop firm drawdown calculator for static, trailing and end-of-day trailing drawdown: daily and overall loss floors in dollars and room before breach.",
               "Prop Firm Drawdown Calculator: Static, Trailing & EOD | PropAnalyse",
               [("What is the difference between static and trailing drawdown?", "Static drawdown fixes your loss floor relative to the starting balance. Trailing drawdown moves the floor up as your equity makes new highs, so open profits you give back count against you."),
                ("Which drawdown is easier to pass?", "Static, for most styles: the floor never moves closer to you. Trailing drawdown punishes trades that run into profit and then reverse.")])
    # profit target
    form = (fld("p-firm", "Firm preset", FIRM_PICK("p-firm")) + fld("p-size", "Account size", numin("p-size", 100000, suffix="$")) +
            fld("p-t1", "Phase 1 target", numin("p-t1", 8, suffix="%")) + fld("p-t2", "Phase 2 target", numin("p-t2", 5, suffix="%"), "0 for one-step") +
            fld("p-split", "Profit split", numin("p-split", 80, suffix="%")) + fld("p-avg", "Your average net return per trading day", numin("p-avg", 0.5, suffix="%")) +
            fld("p-min", "Minimum trading days per phase", numin("p-min", 0, "1", "0")))
    out = ('<dl class="res"><div><dt>Phase 1 target</dt><dd class="n" id="o-t1">-</dd></div><div><dt>Phase 2 target</dt><dd class="n" id="o-t2">-</dd></div>'
           '<div class="hl"><dt>Estimated trading days</dt><dd class="n" id="o-days">-</dd></div><div><dt>Payout if you make the same % funded</dt><dd class="n" id="o-pay">-</dd></div></dl><p class="small" id="o-pnote"></p>')
    explain = ("<p>Targets are a percentage of the starting balance. The day estimate divides each target by your average daily return, rounds up, and applies the minimum trading days. "
               "Real equity curves are lumpy, so treat this as a sanity check, not a forecast. If your average day is 0.3%, an 8% target takes about 27 trading days, which matters at firms with a time limit.</p>")
    tool_shell("/tools/profit-target/", "Profit-target calculator", "Prop firm profit-target calculator", "Dollar targets for each phase, a day count based on your real average return, and what a funded month at the same pace pays you.",
               form, out, explain, "Prop firm profit-target calculator: dollar targets per phase, estimated days to pass from your average daily return, and payout after split.",
               "Prop Firm Profit-Target Calculator: Days to Pass | PropAnalyse")

def quiz():
    c, bl = crumbs([("Home", "/"), ("Find your firm", "/quiz/")])
    def q(n, legend, name, opts, kind="radio"):
        o = "".join(f'<label class="opt"><input type="{kind}" name="{name}" value="{e(v)}"{" checked" if i == 0 and kind == "radio" else ""}><span>{e(t)}</span></label>' for i, (v, t) in enumerate(opts))
        return f'<fieldset class="qf"><legend><span class="n">{n}/7</span> {e(legend)}</legend><div class="opts">{o}</div></fieldset>'
    ctry = "".join(f'<option value="{e(cn.lower())}">{e(cn)}</option>' for cn in all_countries())
    form = (q(1, "What do you want to trade?", "mkt", [("", "Anything"), ("crypto", "Crypto"), ("forex", "Forex"), ("futures", "Futures"), ("indices", "Indices"), ("stocks", "Stocks")]) +
            q(2, "Most you'll pay for one challenge?", "fee", [("", "No limit"), ("50", "$50"), ("100", "$100"), ("200", "$200"), ("400", "$400")]) +
            q(3, "Evaluation style?", "type", [("", "No preference"), ("1-step", "One step"), ("2-step", "Two steps"), ("instant", "Instant funding, no evaluation")]) +
            q(4, "Account size you're aiming for?", "size", [("", "Any"), ("10000", "$10K or more"), ("50000", "$50K or more"), ("100000", "$100K or more"), ("200000", "$200K or more")]) +
            q(5, "What matters most?", "pri", [("score", "Overall PA Score"), ("cost", "Lowest cost"), ("payout", "Fast, frequent payouts"), ("split", "Highest split"), ("trust", "Track record and reviews"), ("rules", "Loosest rules")]) +
            q(6, "Must-haves", "must", [("news", "News trading"), ("weekend", "Weekend holding"), ("static", "Static drawdown"), ("mt5", "MT5")], "checkbox") +
            f'<fieldset class="qf"><legend><span class="n">7/7</span> Where do you live?</legend><label class="fl"><span class="sr">Country</span><select id="q-ctry"><option value="">Not restricted / skip</option>{ctry}</select></label></fieldset>')
    body = f"""<div class="wrap">{c}<header class="ph"><h1>Find your prop firm</h1><p class="lede">Answer seven questions. We filter every firm in our dataset against your answers and rank what's left by the factor you care about. The quiz runs in your browser, sends nothing, and treats FundedXyz like every other firm.</p></header>
<div class="quiz"><form id="quiz" onsubmit="return false">{form}</form><div class="qres" id="qres" aria-live="polite"><p class="small">Results update as you answer.</p></div></div></div>
<script>window.PFA_FIRMS_URL="{url('/data/firms.json')}";window.PFA_BASE="{BASE}";</script><script src="{url('/assets/quiz.js')}?v={ASSET_V}" defer></script>"""
    page("/quiz/", "Which Prop Firm Is Right for Me? 7-Question Firm Finder | PropAnalyse", "Answer seven questions on market, budget, challenge type and must-have rules to get a ranked shortlist of prop firms from our open dataset.", body,
         [bl, {"@context": "https://schema.org", "@type": "WebApplication", "name": "Prop firm finder", "url": ABS + "/quiz/", "applicationCategory": "FinanceApplication", "operatingSystem": "Any", "isAccessibleForFree": True}])

GLOSSARY = [
 ("Prop firm", "A company that lets traders trade its capital (usually simulated) in exchange for a share of profits. Most retail prop firms earn mainly from evaluation fees."),
 ("Evaluation / challenge", "A paid test with a profit target and loss limits. Pass it and you get a funded account. Fail it and the fee is gone unless the firm offers a retry or refund."),
 ("One-step challenge", "A single phase: hit the target once without breaching the limits. Usually a higher target or tighter drawdown than each phase of a two-step."),
 ("Two-step challenge", "Two phases in a row, often 8% then 5% targets. Cheaper per dollar of account at many firms, but slower."),
 ("Instant funding", "A funded account with no evaluation. Costs more up front and usually comes with tighter drawdown or lower splits."),
 ("Profit target", "The gain, as a percentage of the starting balance, you need to pass a phase."),
 ("Daily loss limit", "The most you can lose in one trading day. Firms measure it from the day's starting balance, starting equity or the higher of the two. Read the wording."),
 ("Max drawdown", "The overall loss limit for the account. Breach it once and the account is closed."),
 ("Static drawdown", "A max drawdown fixed relative to the starting balance. The floor never moves."),
 ("Trailing drawdown", "A max drawdown that follows your highest equity upwards, so unrealised profit you give back counts against you. Often stops trailing at the starting balance."),
 ("End-of-day (EOD) drawdown", "A trailing drawdown that only updates on the daily close, ignoring intraday highs. Common at futures firms."),
 ("Profit split", "Your share of the profits on a funded account. Headline figures like 90% or 100% often only apply after scaling or as a paid add-on."),
 ("Payout cycle", "How often you can withdraw: on demand, weekly, bi-weekly or monthly. The first payout often has its own waiting period."),
 ("Consistency rule", "A cap on how much of your total profit can come from one day or one trade, such as no day above 40% of the target. It may apply to the evaluation, the funded account or both."),
 ("Minimum trading days", "The number of days you must place trades before you can pass a phase or request a payout."),
 ("Activation fee", "A one-time charge some firms, mostly futures, take after you pass and before the funded account goes live."),
 ("Reset", "Paying to restart a failed or struggling evaluation, usually at a discount to a new one."),
 ("Fee refund", "Return of the evaluation fee, usually paid with the first or a later payout from the funded account."),
 ("Scaling plan", "Rules for growing account size or split after consistent profitable months."),
 ("News trading", "Trading around high-impact economic releases. Some firms ban opening or closing trades a few minutes either side of the release."),
 ("Weekend holding", "Keeping positions open over the weekend. Matters a lot for crypto, which trades all week."),
 ("Perpetual futures", "Crypto futures with no expiry date. A funding rate paid between longs and shorts keeps the price close to spot. Crypto-native prop firms mostly trade perps."),
 ("Funding rate", "The periodic payment between long and short holders of a perpetual future. It can add to or subtract from your profit if you hold through funding times."),
 ("CFD", "Contract for difference: you trade the price change without owning the asset. Multi-asset prop firms offer crypto, indices and commodities as CFDs."),
 ("Leverage", "Position size relative to account balance. High leverage doesn't change the drawdown limit, it only makes it easier to hit."),
 ("Lot / contract size", "The unit of position size: lots for forex and CFDs, contracts for futures. Prop firms often cap the maximum lots or contracts per account size."),
 ("Expert advisor (EA)", "An automated strategy running on MetaTrader. Firms allow, restrict or ban them, and many ban copy-trading EAs across accounts."),
 ("Copy trading", "Mirroring trades from another account or trader. Usually banned between different people, sometimes allowed between your own accounts."),
 ("KYC", "Know Your Customer identity checks. Most firms require them before the first payout or before the funded contract."),
 ("PA Score", "PropAnalyse's 0 to 10 score. Trust 30%, cost 20%, rules 20%, payout 20%, track record 10%. Missing data scores 4/10. The formula is public on the methodology page."),
 ("Cost per $1K", "Evaluation fee divided by account size, times 1,000. The fairest way to compare a $49 $5K challenge with a $499 $100K one."),
 ("Payout cap", "A maximum amount per withdrawal, often tied to account size. Common at crypto-native firms."),
]
def glossary():
    c, bl = crumbs([("Home", "/"), ("Glossary", "/glossary/")])
    slug = lambda t: re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")
    items = "".join(f'<div id="{slug(t)}"><dt>{e(t)}</dt><dd>{e(d)}</dd></div>' for t, d in sorted(GLOSSARY, key=lambda x: x[0].lower()))
    idx = "".join(f'<a href="#{slug(t)}">{e(t)}</a>' for t, _ in sorted(GLOSSARY, key=lambda x: x[0].lower()))
    body = f'<div class="wrap">{c}<header class="ph"><h1>Prop trading glossary</h1><p class="lede">{len(GLOSSARY)} terms that decide whether you pass and get paid, in plain English.</p></header><p class="inline-list gidx">{idx}</p><dl class="gloss">{items}</dl></div>'
    ld = {"@context": "https://schema.org", "@type": "DefinedTermSet", "name": "Prop trading glossary", "url": ABS + "/glossary/", "hasDefinedTerm": [{"@type": "DefinedTerm", "name": t, "description": d, "url": ABS + "/glossary/#" + slug(t)} for t, d in GLOSSARY]}
    page("/glossary/", "Prop Firm Glossary: Drawdown, Splits, Consistency Rules Explained | PropAnalyse", f"{len(GLOSSARY)} prop trading terms explained: static vs trailing drawdown, consistency rules, profit split, activation fees, perpetual futures and more.", body, [bl, ld])

def site_faq():
    c, bl = crumbs([("Home", "/"), ("FAQ", "/faq/")])
    cheapest = min((f for f in FIRMS if f["_fee"] is not None), key=lambda f: f["_fee"])
    best = RANKED[0]
    daily = [f["name"] for f in RANKED if f["_bucket"] == "daily"]
    news_ok = [f["name"] for f in RANKED if tri(f.get("news_trading")) is True]
    crypto_top = next((f for f in RANKED if is_native(f)), None)
    QA = [
     ("What is the best prop firm right now?", f"On our published PA Score, {best['name']} ranks first at {best['_score']:.1f}/10. The best firm for you depends on market, budget and rules. Filter the full table or take the 7-question quiz."),
     ("What is the best crypto prop firm?", f"The top-scoring crypto-native firm is {crypto_top['name']} ({crypto_top['_score']:.1f}/10). The crypto hub compares venue, leverage, weekend rules and USDT payouts." if crypto_top else "See the crypto hub."),
     ("What is the cheapest prop firm challenge?", f"The lowest published entry fee in our dataset is {cheapest['name']} at {money(cheapest['_fee'], cheapest.get('fee_currency'))}. A low entry fee is not the same as low cost per $1K of account, or low true cost once retries are counted."),
     ("Which prop firms pay out daily or on demand?", (", ".join(daily) + ".") if daily else "None in our dataset at the moment."),
     ("Which prop firms allow news trading?", (", ".join(news_ok) + ".") if news_ok else "None in our dataset at the moment."),
     ("Are prop firms legit?", "Many pay out reliably and some have shut down owing traders. Look at years in operation, Trustpilot volume and rating, and how often the rules change. Our rule-change log shows the last one for every firm."),
     ("How do prop firms make money?", "Mostly from evaluation fees, because most traders fail. Profitable funded traders cost the firm money unless their trades are hedged or the account is simulated, which it usually is."),
     ("Is a funded account real money?", "Usually not. Most retail prop firms run funded accounts on demo or simulated capital and pay you a share of the simulated profit. A few route some accounts to live markets."),
     ("How does PropAnalyse rank firms?", "One public formula: trust 30%, cost 20%, rules 20%, payout 20%, track record 10%. Missing data scores 4/10. Firms cannot pay to change their score or position."),
     ("Who owns PropAnalyse?", "The team behind FundedXyz, a crypto prop firm. FundedXyz is scored by the same formula as every other firm, with no manual adjustment. This is disclosed on every relevant page."),
     ("Do you earn commission?", "Some Visit-site links may be affiliate links. Commission never changes data, scores or ordering. Codes we list are the firm's own public codes, dated."),
     ("How often is the data checked?", "Every firm shows a last-verified date. Changes we find are logged field by field with the date on the rule-changes page, which also has an RSS feed."),
     ("What is the difference between static and trailing drawdown?", "Static drawdown fixes the loss floor relative to your starting balance. Trailing drawdown raises the floor as your equity makes new highs. The drawdown calculator shows both in dollars."),
     ("Should I choose a one-step or two-step challenge?", "One-step is faster but usually has tighter limits or a higher fee. Two-step is cheaper per dollar of account at many firms. Our one-step vs two-step guide compares them with real numbers."),
     ("Can I use the data?", "Yes. The full dataset is published as JSON at /data/firms.json and the change log at /news/changes.json. Please link back."),
    ]
    faqh = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in QA)
    body = f'<div class="wrap">{c}<header class="ph"><h1>Prop firm FAQ</h1><p class="lede">Short answers, with numbers from our current dataset where there are any.</p></header><section class="faq solo">{faqh}</section></div>'
    page("/faq/", "Prop Firm FAQ: Best, Cheapest, Payouts, Legitimacy | PropAnalyse", "Straight answers on prop firms: best and cheapest firms, daily payouts, news trading, legitimacy, drawdown types and how PropAnalyse ranks firms.", body,
         [bl, {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in QA]}])

def methodology():
    c, bl = crumbs([("Home", "/"), ("Methodology", "/methodology/")])
    body = f"""<div class="wrap">{c}<article class="prose"><h1>PropAnalyse is an audit, not a review site</h1>
<p>Most prop firm sites sell placement. Their rankings move with commission, and firms without a deal get pushed into an "unlisted" corner. PropAnalyse works like an audit instead. We make four commitments, and you can check every one of them:</p>
<table class="mini"><tbody>
<tr><td><b>Published scoring</b></td><td>One formula scores every firm. It's below and in <code>scripts/build.py</code>. Nobody adjusts it by hand.</td></tr>
<tr><td><b>Dated rule changes</b></td><td>Every change to a firm's fees, limits or payout terms is logged with the date and the old and new values, on <a href="{url('/news/')}">rule changes</a>, with RSS and JSON feeds.</td></tr>
<tr><td><b>True cost, not sticker price</b></td><td>Retries, activation fees and refunds are part of the price. The <a href="{url('/tools/true-cost/')}">true-cost calculator</a> works out your cost to first payout.</td></tr>
<tr><td><b>No pay-to-rank</b></td><td>Affiliate links may exist, but no payment changes a firm's data, score, order or which page it appears on.</td></tr></tbody></table>
<p class="note"><b>Ownership disclosure.</b> PropAnalyse is operated by the team behind FundedXyz. FundedXyz is scored by the same rules as every other firm. It gets no manual adjustment and no default sort position, and its data is collected with the same checklist.</p>
<h2>Where the numbers come from</h2><p>Every figure is read from the prop firm's own website (pricing, rules, FAQ or help-centre pages), and the date is recorded per firm. Ratings come from the firm's public Trustpilot page. If a firm doesn't publish a number, we show "Not published". We never estimate.</p>
<h2 id="account-types">Account types</h2><p>Every firm sits in exactly one account type, chosen from the platforms and products on the firm's own site. If a firm sells two kinds of account, we file it under its main product and list the other as "also sells".</p>
<table class="mini"><thead><tr><th scope="col">Type</th><th scope="col">What you trade, and where</th></tr></thead><tbody>
<tr><td><a href="{url('/futures/')}"><b>Futures</b></a></td><td>Exchange-listed futures, mostly CME Group contracts, through Rithmic, Tradovate, NinjaTrader or the firm's own futures platform. Risk limits are usually dollar drawdowns.</td></tr>
<tr><td><a href="{url('/cfd/')}"><b>CFD</b></a></td><td>Forex, gold, index and often crypto CFDs on MT5, MT4, cTrader, DXtrade or Match-Trader. Risk limits are usually percentages.</td></tr>
<tr><td><a href="{url('/crypto-exchange/')}"><b>Crypto exchange</b></a></td><td>Crypto perpetuals on an exchange account linked by API (Bybit, BloFin) or on a crypto-first firm's own terminal priced from exchange data. Usually paid in stablecoins.</td></tr></tbody></table>
<p>The account type has no effect on the PA Score. Everything else (platform, markets, challenge type, payout speed, split, payout method, country) is a filter on the ranking tables, and filtered views can be shared by URL. Each firm's type, a one-line reason and the source page are in <a href="{url('/data/firms.json')}">the dataset</a> (fields <code>category</code>, <code>also_offers</code>, <code>category_basis</code>, <code>category_source</code>).</p>
<h2>The PA Score (0 to 10)</h2><p>One formula, applied mechanically by our build script:</p>
<table class="mini"><thead><tr><th scope="col">Component</th><th scope="col" class="num">Weight</th><th scope="col">Inputs</th></tr></thead><tbody>
<tr><td>Trust</td><td class="num n">30%</td><td>Trustpilot score (3.0 scores 0, 5.0 scores full marks), scaled by review volume (log₁₀ of count)</td></tr>
<tr><td>Cost</td><td class="num n">20%</td><td>Cheapest fee per $1,000 of account size across published programs</td></tr>
<tr><td>Rules</td><td class="num n">20%</td><td>Daily loss limit, max drawdown, static vs trailing drawdown, news trading, weekend holding, consistency rule</td></tr>
<tr><td>Payout</td><td class="num n">20%</td><td>Headline profit split, days to first payout, payout cycle</td></tr>
<tr><td>Track record</td><td class="num n">10%</td><td>Years in operation (8+ years = full marks)</td></tr></tbody></table>
<p>Payout cycle uses the firm's headline (first-listed) plan. Fees are compared in the currency the firm prices in (FTMO lists EUR), with no FX conversion. Trustpilot profiles that show no rating (for example, suspended for a guideline breach) count as missing.</p><p>Missing inputs score 4/10 for that component, so holding back information never helps a firm. Each firm page shows its component breakdown and a data-completeness percentage.</p>
<h2>How the rule-change log works</h2><p>Each build compares the dataset with the previous snapshot and writes every changed field to <code>data/changelog.json</code> with the date. The log is append-only and generated, not written by hand. Entries before our first verified snapshot were rebuilt from the dataset's git history.</p>
<h2>Pros, cons and verdicts</h2><p>Pros and cons on each review come from fixed thresholds on the data. Examples: a split of 90% or more, cost per $1K of $5 or less, trailing drawdown, a daily limit of 3% or less, founded less than three years ago. The verdict names the firm's strongest and weakest score components. The same rules apply to every firm.</p>
<h2>What the score is not</h2><p>It doesn't predict whether you will pass or get paid, and it is not financial advice.</p>
<h2>Corrections</h2><p>Firms change rules often. If you spot an outdated figure, send a link to the firm's page and we will re-verify. The fix will show up in the rule-change log. See also the <a href="{url('/updates/')}">verification log</a>.</p>
<p class="small">Dataset: <a href="{url('/data/firms.json')}">/data/firms.json</a>. Change log: <a href="{url('/news/changes.json')}">/news/changes.json</a>.</p></article></div>"""
    page("/methodology/", "Methodology: Published Scoring, Rule-Change Log, No Pay-to-Rank | PropAnalyse", "How PropAnalyse audits prop firms: a published scoring formula, dated rule-change log, true-cost maths and no pay-to-rank. Ownership disclosed.", body, [bl])

def seo_files():
    sm = "".join(f"<url><loc>{ABS}{p}</loc><lastmod>{TODAY}</lastmod></url>" for p in PAGES if p not in NOINDEX)
    open(os.path.join(OUT, "sitemap.xml"), "w").write(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>')
    open(os.path.join(OUT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\n\nSitemap: {ABS}/sitemap.xml\n")
    L = ["# PropAnalyse", "", "> The prop firm audit. Data-first comparison of prop trading firms (crypto first; forex, futures and multi-asset too). Every figure comes from the firm's own website with a date. Unknown values stay blank rather than estimated. Published scoring formula, dated field-level rule-change log, true-cost calculator, no pay-to-rank.",
         "", "Operated by the team behind FundedXyz. FundedXyz is scored with the same formula as every other firm.", "", "## Key pages",
         f"- [All firms]({ABS}/firms/): filterable table", f"- [Crypto prop firms]({ABS}/crypto/): venue, perps vs CFD, crypto leverage, weekend, bots, USDT payouts",
         f"- [Rule changes]({ABS}/news/): dated old→new diffs; [RSS]({ABS}/news/feed.xml); [JSON]({ABS}/news/changes.json)",
         f"- [Discount codes]({ABS}/offers/)", f"- [True-cost calculator]({ABS}/tools/true-cost/)", f"- [Drawdown calculator]({ABS}/tools/drawdown/)", f"- [Profit-target calculator]({ABS}/tools/profit-target/)",
         f"- [Firm finder quiz]({ABS}/quiz/)", f"- [Methodology]({ABS}/methodology/): PA Score formula", f"- [FAQ]({ABS}/faq/)", f"- [Glossary]({ABS}/glossary/)", f"- [Open dataset (JSON)]({ABS}/data/firms.json)", "", "## Firm reviews"]
    L += [f"- [{f['name']} review]({ABS}/firms/{f['slug']}/): PA Score {f['_score']}, fee from {money(f['_fee'], f.get('fee_currency'))}, split {f.get('profit_split') or 'n/a'}, verified {f.get('last_verified') or TODAY}" for f in RANKED]
    L += ["", "## Crypto rule sheets"] + [f"- [{f['name']} crypto rules]({ABS}/crypto/{f['slug']}/)" for f in CRYPTO_FIRMS if f"/crypto/{f['slug']}/" not in NOINDEX]
    L += ["", "## Guides"] + [f"- [{g['h1']}]({ABS}/guides/{g['slug']}/)" for g in GUIDES]
    L += ["", "## Comparisons"] + [f"- [{BY[a]['name']} vs {BY[b]['name']}]({ABS}/compare/{a}-vs-{b}/)" for a, b in PAIRS if a in BY and b in BY]
    open(os.path.join(OUT, "llms.txt"), "w").write("\n".join(L) + "\n")
    open(os.path.join(OUT, ".nojekyll"), "w").write("")
    if SITE_URL.startswith("https://") and "github.io" not in SITE_URL and not BASE: open(os.path.join(OUT, "CNAME"), "w").write(SITE_URL.split("://", 1)[1] + "\n")
