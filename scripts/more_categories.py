# PropAnalyse account-type taxonomy (2026-10-31): Futures / CFD / Crypto exchange.
# Primary taxonomy = category (one per firm, data/raw + firms.json, set by scripts/categorize.py from each firm's own pages).
# Everything else is a filter on the ranking table: platform, markets, challenge type, payout (speed, split, method), country.
# Exec'd last into build.py's namespace.

CATS = [("futures", "Futures", "/futures/"), ("cfd", "CFD", "/cfd/"), ("crypto-exchange", "Crypto exchange", "/crypto-exchange/")]
CAT_NAME = {k: n for k, n, _ in CATS}
CAT_PATH = {k: p for k, _, p in CATS}
CAT_ZH_NAME = {"futures": "期货", "cfd": "差价合约 (CFD)", "crypto-exchange": "加密交易所"}
CAT_ZH_PATH = {k: "/zh" + p for k, _, p in CATS}
CAT_LOW = {"futures": "futures", "cfd": "CFD", "crypto-exchange": "crypto exchange"}

T.update({"nav_futures": "Futures", "nav_cfd": "CFD", "nav_cx": "Crypto exchange", "nav_zh": "中文"})
NAV[:] = [("/futures/", "nav_futures"), ("/cfd/", "nav_cfd"), ("/crypto-exchange/", "nav_cx"), ("/compare/", "nav_compare"),
          ("/tools/", "nav_tools"), ("/guides/", "nav_guides"), ("/zh/", "nav_zh")]
# pages that left the header stay one click away in the footer
FOOT_EXTRA[:] = [(p, t) for p, t in FOOT_EXTRA if p != "/zh/"]
FOOT_EXTRA[:0] = [("/firms/", "All firms"), ("/crypto/", "Crypto prop firms"), ("/offers/", "Offers"), ("/news/", "Rule changes"), ("/methodology/", "Methodology")]
ZH_ALT.update({p: "/zh" + p for _, _, p in CATS})
ZH_NAV[:] = [("/zh/", "排名"), ("/zh/futures/", "期货"), ("/zh/cfd/", "差价合约"), ("/zh/crypto-exchange/", "加密交易所"),
             ("/zh/sizes/100k/", "按账户规模"), ("/zh/countries/malaysia/", "按地区"), ("/zh/methodology/", "评分方法")]
ZH_FOOT[:0] = [("/zh/crypto/", "加密货币")]

# ---------- facet keys (derived at build time from the firm's own published lists) ----------
PLAT_KEYS = [("mt5", "MT5", r"\bmt5\b|metatrader ?5"), ("mt4", "MT4", r"\bmt4\b|metatrader ?4"), ("ctrader", "cTrader", r"ctrader"),
             ("dxtrade", "DXtrade", r"dx ?trade"), ("matchtrader", "Match-Trader", r"match[- ]?trader"), ("tradovate", "Tradovate", r"tradovate"),
             ("rithmic", "Rithmic", r"rithmic|r \| trader"), ("ninjatrader", "NinjaTrader", r"ninjatrader"),
             ("exchange", "Exchange account (Bybit, BloFin)", r"bybit|blofin|binance|\bokx\b"),
             ("own", "Firm's own platform", r"proprietary|terminal|topstepx|in-house|\bhyro\b")]
PLAT_SHORT = {k: l for k, l, _ in PLAT_KEYS} | {"exchange": "Exchange", "own": "Own platform"}
MKT_KEYS = [("forex", "Forex"), ("crypto", "Crypto"), ("indices", "Indices"), ("gold", "Gold & commodities"), ("stocks", "Stocks"), ("futures", "Futures")]
PM_KEYS = [("crypto", "Crypto (USDT / USDC)", r"usdt|usdc|crypto|\bbtc\b|\beth\b|confirmo"), ("bank", "Bank transfer (incl. Rise, Wise)", r"bank|wire|\bach\b|wise|aeropay|rise|workmarket|brokerage")]
SPEED_KEYS = [("daily", "Daily / on demand"), ("weekly", "Weekly"), ("biweekly", "Bi-weekly"), ("monthly", "Monthly")]
TYPE_KEYS = [("1-step", "1-step"), ("2-step", "2-step"), ("3-step", "3-step"), ("instant", "Instant funding")]

def _pkeys(f):
    blob = " | ".join(f["_platforms"]).lower() + " | " + str((f.get("_c") or {}).get("crypto_venue") or "").lower()
    return [k for k, _, rx in PLAT_KEYS if re.search(rx, blob)]
def _mkeys(f):
    a = set(f["_assets"]); s = {k for k in ("forex", "crypto", "indices", "stocks", "futures") if k in a}
    if a & {"commodities", "metals", "energies", "gold"}: s.add("gold")
    if f.get("category") == "futures": s.add("futures")
    return [k for k, _ in MKT_KEYS if k in s]
def _pmkeys(f):
    blob = " | ".join(str(x) for x in as_list(f["_x"].get("payout_methods")) + as_list(f["_c"].get("payout_methods"))).lower()
    return [k for k, _, rx in PM_KEYS if re.search(rx, blob)]
for f in FIRMS:
    f["_pk"], f["_mk"], f["_pm"] = _pkeys(f), _mkeys(f), _pmkeys(f)

def cat_badge(f, zh=False, link=True):
    k = f.get("category")
    if not k: return ""
    n = (CAT_ZH_NAME if zh else CAT_NAME)[k]; p = (CAT_ZH_PATH if zh else CAT_PATH)[k]
    return f'<a class="cbadge" data-cat="{k}" href="{url(p)}">{e(n)}</a>' if link else f'<span class="cbadge" data-cat="{k}">{e(n)}</span>'
def acct_type_html(f):
    k = f.get("category")
    if not k: return NIL
    also = as_list(f.get("also_offers"))
    h = cat_badge(f) + (f' <span class="calso">Also sells {e(", ".join(CAT_LOW[a] for a in also))} accounts</span>' if also else "")
    if f.get("category_basis"):
        src = f.get("category_source")
        h += f'<small class="cbasis">{e(f["category_basis"])}' + (f' <a href="{e(src)}" rel="nofollow noopener" target="_blank">Source</a>' if src else "") + "</small>"
    return h
def plat_chips(f):
    pl = f["_platforms"]
    return ('<ul class="chips">' + "".join(f"<li>{e(p)}</li>" for p in pl) + "</ul>") if pl else NIL

# ---------- filter bar: account-type tabs + multi-select facets ----------
CARET = '<svg class="cv" viewBox="0 0 10 6" aria-hidden="true"><path d="M1 1l4 4 4-4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
def filters_html(firms=None, cats=True):
    fl = firms or FIRMS
    n = lambda fn: sum(1 for f in fl if fn(f))
    o = lambda v, t: f'<option value="{e(v)}">{e(t)}</option>'
    sel = lambda i, lab, opts: f'<label class="fl"><span>{e(lab)}</span><select id="{i}">{opts}</select></label>'
    def ms(k, lab, groups):
        body = ""
        for leg, name, kind, opts in groups:
            items = "".join(f'<label class="ck"><input type="{kind}" name="{name}" value="{e(v)}"{" checked" if kind == "radio" and v == "" else ""}>'
                            f'<span>{e(t)}</span>{"<small class=n>" + str(c) + "</small>" if c is not None else ""}</label>'
                            for v, t, c in opts if c is None or c > 0)
            if items: body += f'<fieldset><legend{"" if leg else " class=sr"}>{e(leg or lab)}</legend>{items}</fieldset>'
        return (f'<div class="fl ms" data-k="{k}"><span aria-hidden="true">{e(lab)}</span><details><summary><span class="sr">{e(lab)}: </span>'
                f'<span class="mv">Any</span>{CARET}</summary><div class="pop">{body}</div></details></div>')
    plat = ms("plat", "Platform", [(None, "plat", "checkbox", [(k, l, n(lambda f, k=k: k in f["_pk"])) for k, l, _ in PLAT_KEYS])])
    mkt = ms("mkt", "Markets", [(None, "mkt", "checkbox", [(k, l, n(lambda f, k=k: k in f["_mk"])) for k, l in MKT_KEYS])])
    typ = ms("type", "Challenge", [(None, "type", "checkbox", [(k, l, n(lambda f, k=k: k in f["_types"])) for k, l in TYPE_KEYS])])
    pay = ms("pay", "Payout", [("Payout cycle", "pay", "checkbox", [(k, l, n(lambda f, k=k: f["_bucket"] == k)) for k, l in SPEED_KEYS]),
                                ("Profit split", "split", "radio", [("", "Any", None), ("80", "80% or more", n(lambda f: (f["_split"] or 0) >= 80)), ("90", "90% or more", n(lambda f: (f["_split"] or 0) >= 90))]),
                                ("Payout method", "pm", "checkbox", [(k, l, n(lambda f, k=k: k in f["_pm"])) for k, l, _ in PM_KEYS])])
    ctry = "".join(o(c.lower(), c) for c in all_countries())
    tabs = ""
    if cats:
        segs = [("", "All", len(fl))] + [(k, nm, n(lambda f, k=k: f.get("category") == k)) for k, nm, _ in CATS]
        hubattr = lambda k, nm: f' data-hub="{url(CAT_PATH[k])}" data-hubt="{e(nm)} prop firms: guide and FAQ"' if k else ""
        tabs = ('<fieldset class="cats"><legend class="sr">Account type</legend><div class="segs">' + "".join(
            f'<label class="seg"><input type="radio" name="cat" value="{k}"{" checked" if not k else ""}{hubattr(k, nm)}><span>{e(nm)}<small class="n">{c}</small></span></label>' for k, nm, c in segs)
            + f'</div><a class="cats-hub" id="cats-hub" href="{url("/futures/")}" hidden></a></fieldset>')
    return f"""<form class="filters" id="filters" onsubmit="return false" role="search" aria-label="Filter firms">{tabs}
<div class="frow"><label class="q"><span class="sr">Search firm</span>{ic('search')}<input type="search" id="q" placeholder="Search firms" autocomplete="off" spellcheck="false"></label>
<div class="fprim">{plat}{mkt}{typ}{pay}
{sel('f-country', T['filter_country'], '<option value="">Any country</option>' + ctry)}
{sel('f-sort', T['sort'], o('score','PA Score') + o('fee','Lowest entry fee') + o('split','Highest split') + o('maxsize','Largest account') + o('payout','Fastest payouts') + o('tp','Trustpilot') + o('founded','Longest running') + o('name','A to Z'))}</div>
<button type="button" class="fbtn" id="f-more" aria-expanded="false" aria-controls="fmore">{ic('sliders')}<span>Filters</span><b class="n" id="f-active" hidden></b></button>
<p class="count" id="count" aria-live="polite"></p></div>
<div class="fmore" id="fmore">{sel('f-fee', T['filter_fee'], '<option value="">Any</option>' + o('50','$50 or less') + o('100','$100 or less') + o('200','$200 or less'))}
{sel('f-size', T['filter_size'], '<option value="">Any</option>' + o('10000','$10K+') + o('50000','$50K+') + o('100000','$100K+') + o('200000','$200K+') + o('300000','$300K+'))}
<label class="tog"><input type="checkbox" id="f-news"><span>{T['filter_news']}</span></label><label class="tog"><input type="checkbox" id="f-weekend"><span>{T['filter_weekend']}</span></label>
<button type="button" class="linkbtn" id="f-reset">{T['filter_reset']}</button></div>
<div class="achips" id="achips"></div></form>"""

# ---------- hub pages ----------
def _fee(f): return money(f["_fee"], f.get("fee_currency"))
def _cheapest(fl): return min((f for f in fl if f["_fee"] is not None), key=lambda f: f["_fee"], default=None)
def _pcount(fl, k): return sum(1 for f in fl if k in f["_pk"])

def hub_copy(k, fl, also):
    top = fl[0]; ch = _cheapest(fl); fast = [f for f in fl if f["_bucket"] == "daily"]
    hi = [f for f in fl if (f["_split"] or 0) >= 90]
    names = nlist([f["name"] for f in fl])
    alsoN = nlist([f["name"] for f in also])
    if k == "futures":
        intro = ("Futures prop firms fund trading in exchange-listed contracts: CME Group index futures such as the E-mini and Micro Nasdaq and S&P, plus crude oil, gold and treasuries. "
                 "Orders go through futures platforms such as Rithmic, Tradovate and NinjaTrader, and the risk rules are written in dollars, usually a trailing or end-of-day drawdown, instead of the percentage limits CFD firms use.")
        checks = [("Subscription or one-off fee", "Some futures evaluations bill monthly until you pass, others charge once. Add any activation fee due on funding before you compare prices."),
                  ("How the drawdown trails", "Intraday trailing drawdown follows your open profit tick by tick. End-of-day trailing only moves at the close. The same dollar figure can be far tighter intraday."),
                  ("Contract limits and consistency", "Futures plans cap how many contracts you can hold and often add a consistency rule on payouts. Both decide how fast you can scale."),
                  ("Payout path", "Many futures firms pay after a set number of winning days and cap early withdrawals. Read the payout policy, not just the split.")]
        faq = [("What is a futures prop firm?", f"A firm that pays you a share of profits from a simulated or funded account trading exchange-listed futures, mostly CME Group contracts, on platforms such as Rithmic, Tradovate or NinjaTrader. We track {fcount(len(fl))} whose main product is futures: {names}."),
               ("Which platforms do futures prop firms use?", f"In our data {_pcount(fl, 'tradovate')} of {len(fl)} list Tradovate, {_pcount(fl, 'ninjatrader')} list NinjaTrader and {_pcount(fl, 'rithmic')} list Rithmic. Topstep runs its own TopstepX platform.")]
    elif k == "cfd":
        intro = ("CFD prop firms run simulated accounts on retail trading platforms: MetaTrader 5 and 4, cTrader, DXtrade and Match-Trader. "
                 "One account usually covers forex pairs, gold, index CFDs and often crypto CFDs. Risk is set in percentages, normally a daily loss limit plus an overall drawdown, and most firms sell 1-step and 2-step challenges, with instant funding at some.")
        checks = [("Daily loss: balance or equity", "A 5% daily limit measured on equity includes open trades; on balance it does not. Check which, and when the day resets."),
                  ("Static or trailing drawdown", "A static 10% stays fixed from the starting balance. A trailing one rises with your high-water mark, which leaves less room once you are in profit."),
                  ("News and weekend rules", "Many CFD firms block trading around high-impact news or force positions closed before the weekend, especially on funded accounts."),
                  ("Platform availability", "Platform access varies by country. Some firms lost or regained MT5 in recent years, so confirm your platform is offered where you live.")]
        faq = [("What is a CFD prop firm?", f"A firm that funds trading in contracts for difference (forex, gold, indices, often crypto) on platforms such as MT5, cTrader, DXtrade or Match-Trader. We track {fcount(len(fl))} whose main product is CFD accounts."),
               ("MT5, cTrader or Match-Trader: which is most common?", f"Among the CFD firms we track, {_pcount(fl, 'mt5')} list MT5, {_pcount(fl, 'matchtrader')} list Match-Trader, {_pcount(fl, 'ctrader')} list cTrader, {_pcount(fl, 'dxtrade')} list DXtrade and {_pcount(fl, 'mt4')} list MT4."),
               ("Can I trade crypto at a CFD prop firm?", f"Yes, {sum(1 for f in fl if 'crypto' in f['_assets'])} of {len(fl)} CFD firms list crypto CFDs. Leverage on crypto is usually much lower than on forex. For exchange-style crypto accounts see our crypto exchange prop firms.")]
    else:
        direct = [f for f in fl if "exchange" in f["_pk"]]
        intro = ("Crypto exchange prop firms are built for crypto traders. You trade perpetual futures either on an exchange account linked by API, such as Bybit or BloFin, or on the firm's own terminal priced from live exchange data. "
                 "Expect hundreds of pairs, markets that run through the weekend, more leverage than CFD firms allow, and payouts in USDT or USDC.")
        checks = [("Real exchange or in-house terminal", f"{nlist([f['name'] for f in direct])} connect{'s' if len(direct) == 1 else ''} to an exchange account. The others run their own platform on exchange price feeds, so fills and funding can differ from the exchange itself."),
                  ("Leverage versus drawdown", "High leverage does not change your drawdown. Size positions to the daily and maximum loss limits, not to the leverage you are offered."),
                  ("Position and exposure caps", "Crypto firms often cap total margin, notional exposure or low-cap altcoin size. Breaking these is a common reason for failed accounts."),
                  ("Payout network and minimum", "Check the stablecoin, the network (ERC-20, TRC-20, BEP-20), the minimum withdrawal and whether KYC is needed before the first payout.")]
        faq = [("What is a crypto exchange prop firm?", f"A crypto-first prop firm where you trade perpetual futures on an exchange account linked by API or on the firm's own exchange-priced terminal, usually paid in stablecoins. We track {fcount(len(fl))}: {names}."),
               ("Do I trade on a real exchange?", f"Only some firms do this. {nlist([f['name'] for f in direct]) if direct else 'None'} connect{'s' if len(direct) == 1 else ''} to an exchange account (demo or sub-account). The rest simulate trades on their own platform using live exchange prices. Either way the capital is simulated during evaluations."),
               ("How are crypto prop firm payouts made?", f"{sum(1 for f in fl if 'crypto' in f['_pm'])} of {len(fl)} pay out in stablecoins (USDT or USDC). Check the minimum payout and the network before you request one."),
               ("Crypto exchange firm or crypto CFDs at a CFD firm?", "CFD firms quote crypto as CFDs next to forex, often with low leverage and weekend restrictions. Exchange-style firms offer more pairs, perpetual contracts with funding rates and 24/7 trading.")]
    lo = CAT_LOW[k]
    faq = [(f"What is the best {lo} prop firm?",
            f"On our published PA Score the top firm in this category is {top['name']} ({top['_score']:.1f}/10)" + (f", followed by {fl[1]['name']} ({fl[1]['_score']:.1f})." if len(fl) > 1 else ".") + " Every firm is scored with the same formula.")] + faq
    if ch: faq.insert(1, (f"What is the cheapest {lo} prop firm?", f"{ch['name']} has the lowest published entry fee in this category: {_fee(ch)}. Prices change often, so confirm on the firm's site."))
    if also: faq.append((f"Do other firms sell {lo} accounts too?", f"Yes. {alsoN} {'is' if len(also) == 1 else 'are'} listed under another main account type but also sell{'s' if len(also) == 1 else ''} {lo} accounts."))
    facts = [f'<b class="n">{len(fl)}</b> firms', f'From <b class="n">{_fee(ch)}</b>' if ch else "", f'<b class="n">{len(fast)}</b> pay daily or on demand', f'<b class="n">{len(hi)}</b> with a 90%+ split']
    return intro, checks, faq, [x for x in facts if x]

def hub_page(k, nm, path):
    fl = [f for f in RANKED if f.get("category") == k]
    also = [f for f in RANKED if k in as_list(f.get("also_offers"))]
    intro, checks, faq, facts = hub_copy(k, fl, also)
    c, bl = crumbs([("Home", "/"), (f"{nm} prop firms", path)])
    others = "".join(f'<li><a href="{url(p)}"><span>{e(n2)} prop firms</span><b class="n">{sum(1 for f in FIRMS if f.get("category") == k2)}</b></a></li>' for k2, n2, p in CATS if k2 != k)
    relp = {"futures": [("/platforms/tradovate/", "Tradovate prop firms"), ("/platforms/ninjatrader/", "NinjaTrader prop firms"), ("/platforms/rithmic/", "Rithmic prop firms"), ("/guides/cheapest-futures-prop-firm-50k/", "Cheapest $50K futures evaluation"), ("/best/futures/", "Every firm with futures")],
            "cfd": [("/platforms/mt5/", "MT5 prop firms"), ("/platforms/ctrader/", "cTrader prop firms"), ("/platforms/match-trader/", "Match-Trader prop firms"), ("/guides/one-step-vs-two-step-challenge/", "1-step vs 2-step challenges"), ("/best/forex/", "Every firm with forex")],
            "crypto-exchange": [("/crypto/", "Crypto prop firms, rule by rule"), ("/platforms/bybit/", "Bybit prop firms"), ("/guides/crypto-prop-firms-usdt-payouts/", "Crypto prop firms with USDT payouts"), ("/guides/best-crypto-prop-firms/", "Best crypto prop firms"), ("/?mkt=crypto", "Every firm that lists crypto")]}[k]
    rel = others + "".join(f'<li><a href="{url(p)}"><span>{e(t)}</span></a></li>' for p, t in relp if p.startswith("/?") or p in PAGES or p.startswith("/best/"))
    also_h = ""
    if also:
        also_h = ('<section class="block"><h2>' + e(f"Also sell {CAT_LOW[k]} accounts") + '</h2><p class="small">Listed under their main account type, but these firms also sell this kind of account. Their scores and rows are on their own category page.</p><ul class="also">'
                  + "".join(f'<li><a href="{url("/firms/" + f["slug"] + "/")}"><b>{e(f["name"])}</b></a>{cat_badge(f)}<span>{e(f.get("category_basis") or "")}</span></li>' for f in also) + "</ul></section>")
    chk = "".join(f"<p><b>{e(h)}.</b> {e(t)}</p>" for h, t in checks)
    faqh = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in faq)
    crypto_note = (f'<p class="note">Searching for crypto prop firms in general? <a href="{url("/crypto/")}">Crypto prop firms, rule by rule</a> covers every firm that lists crypto, including CFD firms, with venue, leverage and weekend rules.</p>' if k == "crypto-exchange" else "")
    body = f"""<div class="wrap">{c}<header class="ph hubh"><h1>{e(nm)} prop firms</h1><p class="lede">{e(intro)}</p><p class="facts">{"".join("<span>" + x + "</span>" for x in facts)}<span>Verified <time datetime="{e(TODAY)}">{nice_date(TODAY)}</time></span></p>{crypto_note}</header>
<section class="hubt" id="table" aria-label="{e(nm)} firm table">{filters_html(fl, cats=False)}{table(fl, empty=True, local=True)}{legend()}</section>
{also_h}
<div class="hubgrid"><section class="block"><h2>What to check before you buy</h2><div class="prose">{chk}</div>
<p class="small">How firms are sorted into account types: <a href="{url('/methodology/#account-types')}">methodology</a>.</p></section>
<aside class="grel"><h2>Related</h2><ul class="lists">{rel}</ul></aside></div>
<section class="block faq"><h2>FAQ</h2>{faqh}</section></div>"""
    ld = [bl, {"@context": "https://schema.org", "@type": "ItemList", "name": f"{nm} prop firms ranked by PA Score", "numberOfItems": len(fl),
               "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": ABS + "/firms/" + f["slug"] + "/", "name": f["name"]} for i, f in enumerate(fl)]},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}]
    ch = _cheapest(fl)
    title = {"futures": f"Best Futures Prop Firms {YEAR_NOW}: {len(fl)} Firms Ranked (Rithmic, Tradovate) | PropAnalyse",
             "cfd": f"Best CFD Prop Firms {YEAR_NOW}: {len(fl)} Forex & CFD Firms Ranked (MT5, cTrader) | PropAnalyse",
             "crypto-exchange": f"Crypto Exchange Prop Firms {YEAR_NOW}: {len(fl)} Firms Trading Perps (Bybit) | PropAnalyse"}[k]
    desc = (f"{len(fl)} {CAT_LOW[k]} prop firms ranked by a published score: fees" + (f" from {_fee(ch)}" if ch else "") +
            ", drawdown, profit split, payout speed and platforms. Filter by platform, market, challenge type, payout and country.")
    page(path, title, desc, body, ld)

# ---------- /zh/ hubs ----------
ZH_INTRO = {
 "futures": "期货自营交易公司（futures prop firm）资助的是交易所上市的期货合约，主要是 CME 集团的股指期货（如 E-mini 与微型纳指、标普），以及原油、黄金和国债期货。下单通过 Rithmic、Tradovate、NinjaTrader 等期货平台完成，风控以美元金额计算，通常是跟踪回撤或收盘回撤，而不是 CFD 公司常用的百分比限制。",
 "cfd": "差价合约（CFD）自营交易公司在 MT5、MT4、cTrader、DXtrade、Match-Trader 等零售交易平台上提供模拟账户。一个账户通常涵盖外汇、黄金、指数 CFD，很多还包括加密货币 CFD。风控按百分比设定，一般是日亏损限制加最大回撤；大多数公司提供一阶段和两阶段挑战，部分公司提供直接资金账户。",
 "crypto-exchange": "加密交易所类自营交易公司专为加密货币交易者设计：你在通过 API 连接的交易所账户（如 Bybit、BloFin）上交易永续合约，或在公司自建、按交易所实时价格报价的交易终端上交易。通常有数百个交易对、周末照常交易、杠杆高于 CFD 公司，并以 USDT 或 USDC 出金。",
}
ZH_CHECK = {
 "futures": ["<p><b>按月订阅还是一次性收费。</b>有的期货考核在通过前按月扣费，有的一次性收费。比较价格时要把出资时的激活费算进去。</p>", "<p><b>回撤怎么跟踪。</b>盘中跟踪回撤随浮动盈利逐笔上移，收盘跟踪只在收盘时调整。同样的美元数字，盘中跟踪要紧得多。</p>", "<p><b>合约上限与一致性规则。</b>期货方案限制可持有的合约数量，出金时常附带一致性规则，两者决定了你能多快放大仓位。</p>"],
 "cfd": ["<p><b>日亏损按余额还是净值。</b>按净值计算的 5% 日亏损包含持仓浮亏，按余额则不包含。还要看每日重置的时间点。</p>", "<p><b>静态还是跟踪回撤。</b>静态 10% 从初始余额起固定不变；跟踪回撤随账户新高上移，盈利后可承受的亏损反而更小。</p>", "<p><b>新闻与周末规则。</b>很多 CFD 公司禁止在重大新闻前后交易，或要求周末前平仓，资金账户尤其如此。</p>"],
 "crypto-exchange": ["<p><b>真实交易所还是自建终端。</b>部分公司连接交易所账户，其余公司在自己的平台上用交易所行情模拟成交，成交与资金费率可能与交易所本身不同。</p>", "<p><b>杠杆不改变回撤。</b>按日亏损和最大回撤来控制仓位，而不是按可用杠杆。</p>", "<p><b>出金网络与最低金额。</b>确认稳定币种类、链（ERC-20、TRC-20、BEP-20）、最低提现额，以及首次出金前是否需要 KYC。</p>"],
}
def zh_hub(k):
    nm = CAT_ZH_NAME[k]; path = CAT_ZH_PATH[k]
    fl = [f for f in RANKED if f.get("category") == k]; also = [f for f in RANKED if k in as_list(f.get("also_offers"))]
    top = fl[0]; ch = _cheapest(fl); fast = [f for f in fl if f["_bucket"] == "daily"]
    PZ = PLAT_SHORT | {"exchange": "交易所账户", "own": "自有平台"}
    zplat = ("平台", lambda f: e("、".join(PZ[x] for x in f["_pk"])) or NIL_ZH, "")
    t = gtable(fl, [zrank(fl), ZFIRM, ZSCORE, ZFEE, ZSPLIT, ZPAY, zplat], f"{nm}自营交易公司排名")
    ans = (f"我们追踪的公司中，有 {len(fl)} 家以{nm}账户为主：{zlist([f['name'] for f in fl])}。按同一套公开公式，评分最高的是 {top['name']}（{top['_score']:.1f}/10）"
           + (f"，入场费最低的是 {ch['name']}，{_fee(ch)} 起" if ch else "") + f"。{len(fast)} 家支持每日或随时出金。")
    secs = [(f"{len(fl)} 家{nm}公司排名", t + f'<p class="small">想按平台、品种、挑战类型、出金方式或国家筛选？请使用<a href="{url(CAT_PATH[k])}" lang="en">英文版排名表</a>（支持多选筛选）。</p>'),
            ("这类账户是什么", f"<p>{e(ZH_INTRO[k])}</p>"), ("购买前先看", "".join(ZH_CHECK[k]))]
    if also: secs.append((f"同样提供{nm}账户的公司", "<p>" + "、".join(f'<a href="{url("/firms/" + f["slug"] + "/")}">{e(f["name"])}</a>（主类别：{e(CAT_ZH_NAME[f["category"]])}）' for f in also) + f"。它们的主要产品属于其他类别，但也销售{nm}账户。</p>"))
    other = "、".join(f'<a href="{url(CAT_ZH_PATH[k2])}">{e(CAT_ZH_NAME[k2])}</a>' for k2, _, _ in CATS if k2 != k)
    secs.append(("分类方法", f'<p>每家公司按其主要账户类型归入一个类别（期货、差价合约或加密交易所），依据是该公司官网对交易平台和交易品种的说明；若同时提供两类账户，以主推产品为准，另一类记为“也提供”。其他类别：{other}。详见<a href="{url("/zh/methodology/")}">评分方法</a>。</p>'))
    qa = [(f"最好的{nm}自营交易公司是哪家？", f"按 PA 评分，目前是 {top['name']}（{top['_score']:.1f}/10）" + (f"，其次是 {fl[1]['name']}（{fl[1]['_score']:.1f}）。" if len(fl) > 1 else "。") + "所有公司使用同一公式评分。")]
    if ch: qa.append((f"最便宜的{nm}挑战是哪家？", f"{ch['name']} 的公开入场费最低，{_fee(ch)} 起。价格经常变动，购买前请到官网确认。"))
    if k == "crypto-exchange":
        direct = [f for f in fl if "exchange" in f["_pk"]]
        qa.append(("是在真实交易所上交易吗？", f"只有部分公司如此：{zlist([f['name'] for f in direct])} 连接交易所账户（模拟盘或子账户），其余公司在自建平台上用交易所实时价格模拟成交。考核阶段的资金都是模拟资金。"))
        qa.append(("和 CFD 公司的加密货币有什么区别？", "CFD 公司把加密货币作为差价合约与外汇一起报价，杠杆通常较低，周末规则也更严；交易所类公司交易对更多，是带资金费率的永续合约，并且 24/7 交易。"))
    elif k == "futures":
        qa.append(("期货自营交易公司用什么平台？", f"在我们的数据中，{len(fl)} 家里有 {_pcount(fl, 'tradovate')} 家列出 Tradovate，{_pcount(fl, 'ninjatrader')} 家列出 NinjaTrader，{_pcount(fl, 'rithmic')} 家列出 Rithmic；Topstep 使用自有的 TopstepX 平台。"))
    else:
        qa.append(("MT5、cTrader 还是 Match-Trader 更常见？", f"在我们追踪的 CFD 公司中，{_pcount(fl, 'mt5')} 家提供 MT5，{_pcount(fl, 'matchtrader')} 家提供 Match-Trader，{_pcount(fl, 'ctrader')} 家提供 cTrader，{_pcount(fl, 'dxtrade')} 家提供 DXtrade。"))
    ld = [{"@context": "https://schema.org", "@type": "ItemList", "name": f"{nm}自营交易公司 PA 评分排名", "inLanguage": "zh-Hans", "numberOfItems": len(fl),
           "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": ABS + "/firms/" + f["slug"] + "/", "name": f["name"]} for i, f in enumerate(fl)]}]
    rel = "".join(f'<li><a href="{url(CAT_ZH_PATH[k2])}"><span>{e(CAT_ZH_NAME[k2])}自营交易公司</span></a></li>' for k2, _, _ in CATS if k2 != k) + zh_rel(path)
    zh_shell(path, [("首页", "/zh/"), (f"{nm}", path)], f"{YEAR_NOW} {nm}自营交易公司排名",
             f"{YEAR_NOW} {nm}自营交易公司排名：{len(fl)} 家公司费用、规则与出金对比 | PropAnalyse",
             f"{len(fl)} 家{nm}自营交易公司（prop firm）按同一公式评分：挑战费用、回撤规则、分成比例、出金周期与交易平台，数据取自各公司官网。",
             ans, [f'<b class="n">{len(fl)}</b> 家公司', (f'最低 <b class="n">{_fee(ch)}</b>' if ch else ""), f'<b class="n">{len(fast)}</b> 家每日出金'], secs, qa, rel=rel, ld_extra=ld)

def category_hubs():
    for k, nm, p in CATS: hub_page(k, nm, p)
    for k, _, _ in CATS: zh_hub(k)

_prog_prev_cat = programmatic
def programmatic():
    _prog_prev_cat(); category_hubs()

_seo_prev_cat = seo_files
def seo_files():
    _seo_prev_cat()
    L = ["", "## Account types (primary taxonomy)", "Every firm has one main account type, read from the firm's own platform and product pages; firms that sell a second type list it as also_offers in /data/firms.json.",
         f"- [Futures prop firms]({ABS}/futures/): CME futures via Rithmic, Tradovate, NinjaTrader or the firm's own platform",
         f"- [CFD prop firms]({ABS}/cfd/): forex, gold, index and crypto CFDs on MT5, MT4, cTrader, DXtrade, Match-Trader",
         f"- [Crypto exchange prop firms]({ABS}/crypto-exchange/): crypto perpetuals on an exchange account via API (Bybit, BloFin) or a firm terminal priced from exchange data",
         f"- Filters on every ranking table (URL parameters, comma-separated for multi-select): cat, plat (mt5, mt4, ctrader, dxtrade, matchtrader, tradovate, rithmic, ninjatrader, exchange, own), mkt (forex, crypto, indices, gold, stocks, futures), type (1-step, 2-step, 3-step, instant), pay (daily, weekly, biweekly, monthly), split (80, 90), pm (crypto, bank), country. Example: {ABS}/?cat=cfd&plat=mt5,ctrader&split=90",
         ""]
    for k, nm, _ in CATS:
        L.append(f"### {nm}")
        L += [f"- {f['name']}" + (f" (also offers: {', '.join(CAT_NAME[a] for a in as_list(f.get('also_offers')))})" if f.get("also_offers") else "") + f": {f.get('category_basis') or ''}" for f in RANKED if f.get("category") == k]
    open(os.path.join(OUT, "llms.txt"), "a").write("\n".join(L) + "\n")
