# PropAnalyse /zh/ (Simplified Chinese), 2026-10-30. Chinese copy written by us for these pages; nothing copied from competitors.
# Every number is computed from data/firms.json at build time, exactly like the English pages. Firm detail pages stay English for now.
import statistics
DOL = "$"
T_ZH = dict(T); T_ZH.update({k: v for k, v in json.load(open(os.path.join(ROOT, "i18n", "zh.json"))).items() if v})
ZH_COUNTRIES = [("china", "中国大陆"), ("hong-kong", "香港"), ("taiwan", "台湾"), ("singapore", "新加坡"), ("malaysia", "马来西亚")]
ZH_SIZES = [10000, 50000, 100000]
ZH_ALT = {"/": "/zh/", "/crypto/": "/zh/crypto/", "/methodology/": "/zh/methodology/"}
ZH_ALT.update({f"/countries/{s}/": f"/zh/countries/{s}/" for s, _ in ZH_COUNTRIES})
ZH_ALT.update({f"/sizes/{s // 1000}k/": f"/zh/sizes/{s // 1000}k/" for s in ZH_SIZES})
ZH_NAV = [("/zh/", "排名"), ("/zh/crypto/", "加密货币"), ("/zh/sizes/100k/", "按账户规模"), ("/zh/countries/malaysia/", "按地区"), ("/zh/methodology/", "评分方法")]
ZH_FOOT = [("/zh/sizes/10k/", "10K 挑战"), ("/zh/sizes/50k/", "50K 挑战"), ("/zh/countries/china/", "中国大陆"), ("/zh/countries/singapore/", "新加坡")]
ZH_UI = {"skip": "跳到正文", "menu": "菜单", "explore": "浏览", "disc": "利益披露", "verified": "数据核实于", "open": "开放数据 (JSON)"}
NIL_ZH = '<span class="nil">未公布</span>'
BUCKET_ZH = {"daily": "每日 / 随时", "weekly": "每周", "biweekly": "每两周", "monthly": "每月", "other": "不固定"}
CAT_ZH = {"futures": "期货", "cfd": "差价合约", "crypto-exchange": "加密交易所"}   # account type (data: category)
TYPE_ZH = {"1-step": "一阶段", "2-step": "两阶段", "3-step": "三阶段", "instant": "直接资金", "express": "快速", "lightning": "闪电"}

def zdate(d):
    try:
        y, m, dd = str(d)[:10].split("-"); return f"{int(y)}年{int(m)}月{int(dd)}日"
    except Exception: return e(str(d))
def zlist(names): return "、".join(names[:-1]) + (" 和 " if len(names) > 1 else "") + names[-1] if names else "无"
def zshow(v):
    if v in (None, "", [], {}): return NIL_ZH
    s = str(v).strip()
    if s.lower() in ("none", "no", "false", "n/a", "0%"): return "无"
    return e(s)
def zsplit(v):
    if v in (None, ""): return NIL_ZH
    if "fixed" in str(v).lower(): return "固定奖励"
    x = max_pct(v)
    return f"最高 {x:g}%" if x is not None else zshow(v)
def ztri(v):
    t = tri(v)
    return NIL_ZH if t is None else ("允许" if t is True else ("有限制" if t == "restricted" else "不允许"))
def zmh(v, cur="USD"): return NIL_ZH if v is None else mh(v, cur)
def ztype(t): return TYPE_ZH.get(str(t or "").lower(), str(t or ""))
ZFIRM = ("公司", lambda f: flink(f), "")
ZSCORE = ("PA 评分", lambda f: f'<b class="n">{f["_score"]:.1f}</b>', "n")
ZCAT = ("类型", lambda f: e(CAT_ZH.get(f.get("category"), f.get("category") or "")), "")
ZFEE = ("起步价", lambda f: zmh(f["_fee"], f.get("fee_currency")), "num n")
ZSPLIT = ("分成", lambda f: zsplit(f.get("profit_split")), "")
ZPAY = ("出金周期", lambda f: e(BUCKET_ZH.get(f["_bucket"], "")) or NIL_ZH, "")
def zrank(fl): return ("#", lambda f: f'<span class="n">{fl.index(f) + 1}</span>', "n")

def zh_shell(path, items, h1, title, desc, ans, facts, secs, qa, noindex=False, rel=None, ld_extra=None):
    c, bl = crumbs(items)
    en_p = next((k for k, v in ZH_ALT.items() if v == path), "/")
    sh_ = "".join(f'<section class="gsec"><h2>{e(h)}</h2>{b}</section>' for h, b in secs)
    faqh = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in qa)
    relh = f'<aside class="grel"><h2>相关页面</h2><ul class="lists">{rel}</ul></aside>' if rel else ""
    fh = "".join(f'<span>{x}</span>' for x in facts)
    body = f"""<div class="wrap">{c}<article class="guide"><header class="ph"><h1>{e(h1)}</h1><p class="meta"><span>更新于 <time datetime="{TODAY}">{zdate(TODAY)}</time></span><span>数据：{len(FIRMS)} 家公司，均取自其官网</span><span><a href="{url(en_p)}" lang="en" hreflang="en">English</a></span></p>
<p class="answer">{e(ans)}</p><p class="facts">{fh}</p></header><div class="gbody">{sh_}<section class="block faq"><h2>常见问题</h2>{faqh}</section>
<p class="small">本页数字在构建时由我们的数据集生成。评分使用<a href="{url('/zh/methodology/')}">公开公式</a>；FundedXYZ 由本站团队运营，按完全相同的规则评分，不作任何调整。规则变化记录在<a href="{url('/news/')}">规则变更</a>页面（英文）。点公司名进入英文详情页，可查看费用矩阵、规则原文与来源链接。</p></div>{relh}</article></div>"""
    ld = [bl, {"@context": "https://schema.org", "@type": "FAQPage", "inLanguage": "zh-Hans", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]}] + (ld_extra or [])
    if noindex: NOINDEX.add(path)
    page(path, title, desc, body, ld, "article", extra_head='<meta name="robots" content="noindex,follow">' if noindex else "", lang="zh")

def zh_rel(skip):
    L = [("/zh/", "2026 自营交易公司排名"), ("/zh/crypto/", "加密货币自营交易公司")] + [(f"/zh/countries/{s}/", f"接受{n}交易者的公司") for s, n in ZH_COUNTRIES] + [(f"/zh/sizes/{x // 1000}k/", f"{DOL}{x // 1000}K 挑战价格对比") for x in ZH_SIZES] + [("/zh/methodology/", "数据来源与评分方法")]
    return "".join(f'<li><a href="{url(p)}"><span>{e(t)}</span></a></li>' for p, t in L if p != skip)

# ---------------- /zh/ ranking ----------------
def zh_home():
    fl = RANKED; top = fl[0]
    cheap = min((f for f in fl if f["_fee"] is not None), key=lambda f: f["_fee"])
    daily = [f for f in fl if f["_bucket"] == "daily"]; nat = [f for f in fl if is_native(f)]
    avgc = round(sum(f["_complete"] for f in fl) / len(fl))
    fx = BY.get("fundedxyz"); fxr = fl.index(fx) + 1 if fx else None
    ans = (f"我们用同一套公开公式给 {len(fl)} 家自营交易公司（prop firm）打分，满分 10 分。目前排名第一的是 {top['name']}（{top['_score']:.1f}），"
           f"入场费最低的是 {cheap['name']}，{money(cheap['_fee'], cheap.get('fee_currency'))} 起。{len(daily)} 家支持每日或随时申请出金，{len(nat)} 家是加密原生公司。"
           "所有数字都来自各公司官网；公司没有公布的一律标为“未公布”，我们不做估算。")
    t = gtable(fl, [zrank(fl), ZFIRM, ZSCORE, ZCAT, ZFEE, ZSPLIT, ZPAY, ("数据完整度", lambda f: f'<span class="n">{f["_complete"]}%</span>', "num n")], "自营交易公司排名")
    secs = [(f"{len(fl)} 家公司排名", t + '<p class="small">“起步价”是该公司所有公开方案中最低的挑战费用。FTMO 以欧元定价，未做汇率换算。</p>'),
            ("评分怎么算", f'<p>PA 评分由五部分组成：信任 30%（Trustpilot 分数，按评价数量加权）、成本 20%（每 1,000 美元账户规模的最低费用）、规则 20%（日亏损、最大回撤、静态或跟踪回撤、新闻交易、周末持仓、一致性规则）、出金 20%（分成比例、首次出金天数、出金周期）、经营年限 10%。</p><p>缺失的数据该项按 4/10 计算，所以不公布信息不会让公司得分更高。完整公式见<a href="{url("/zh/methodology/")}">评分方法</a>。</p>'),
            ("挑选前先看三件事", "<p><b>回撤类型。</b>同样是 10% 最大回撤，跟踪回撤会随账户新高上移，实际可承受的亏损比静态回撤小得多。</p><p><b>真实成本。</b>标价最低不等于最便宜：有的公司按月收费，有的在首次出金后退还挑战费，重考折扣也会改变总成本。</p><p><b>出金节奏。</b>首次出金要等多少天、之后多久能申请一次，决定了资金回笼速度。表中“出金周期”取自公司的主推方案。</p>")]
    qa = [("哪家自营交易公司最好？", f"按我们公开的 PA 评分，目前第一名是 {top['name']}（{top['_score']:.1f}/10），第二、三名是 {fl[1]['name']} 和 {fl[2]['name']}。所有公司使用同一公式，规则变化后排名会自动更新。"),
          ("最便宜的自营交易挑战是哪家？", f"{cheap['name']} 的公开入场费最低，{money(cheap['_fee'], cheap.get('fee_currency'))} 起。账户规模不同，价格排名也不同，可查看 10K、50K、100K 的价格对比页。"),
          ("FundedXYZ 和本站是什么关系？", "PropAnalyse 由 FundedXYZ 背后的团队运营。FundedXYZ 和其他公司使用完全相同的评分规则与数据清单，没有人工加分，也不默认置顶" + (f"，目前排在第 {fxr} 名。" if fxr else "。")),
          ("数据多久更新一次？", "每个公司页面都显示最近核实日期。规则、费用或出金条款发生变化时，我们会在规则变更页面记录日期与来源，并提供 RSS 和 JSON 订阅。")]
    ld = [{"@context": "https://schema.org", "@type": "ItemList", "name": "自营交易公司 PA 评分排名", "inLanguage": "zh-Hans", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": ABS + "/firms/" + f["slug"] + "/", "name": f["name"]} for i, f in enumerate(fl)]}]
    zh_shell("/zh/", [("首页", "/zh/")], f"{YEAR_NOW} 自营交易公司排名：规则、费用与出金对比",
             f"{YEAR_NOW} 自营交易公司排名：{len(fl)} 家 Prop Firm 费用、规则与出金对比 | PropAnalyse",
             f"{len(fl)} 家自营交易公司（prop firm）按同一公式评分：挑战费用、回撤规则、分成比例与出金周期，数据全部取自各公司官网，未公布即标注。",
             ans, [f'<b class="n">{len(fl)}</b> 家公司', f'平均完整度 <b class="n">{avgc}%</b>', f'<b class="n">{len(nat)}</b> 家加密原生'], secs, qa, rel=zh_rel("/zh/"), ld_extra=ld)

# ---------------- /zh/crypto/ ----------------
def zh_crypto():
    fl = CRYPTO_FIRMS; nat = [f for f in fl if is_native(f)]; multi = [f for f in fl if not is_native(f)]
    top = nat[0] if nat else fl[0]
    cheap = min((f for f in fl if f["_fee"] is not None), key=lambda f: f["_fee"])
    wk = [f for f in fl if tri(f.get("weekend_holding")) is True]
    ans = (f"我们的数据集中有 {len(fl)} 家公司提供加密货币交易。其中 {len(nat)} 家是加密原生公司（{zlist([f['name'] for f in nat])}），交易交易所式的永续合约；"
           f"另外 {len(multi)} 家把加密货币作为 CFD 与外汇、指数一起提供。加密原生公司中评分最高的是 {top['name']}（{top['_score']:.1f}/10），"
           f"入场费最低的是 {cheap['name']}，{money(cheap['_fee'], cheap.get('fee_currency'))} 起。{len(wk)} 家明确允许周末持仓。")
    t = gtable(fl, [zrank(fl), ZFIRM, ZSCORE, ("类型", lambda f: "加密原生" if is_native(f) else "多资产", ""), ZFEE, ZSPLIT, ZPAY,
                    ("周末持仓", lambda f: ztri(f.get("weekend_holding")), ""), ("新闻交易", lambda f: ztri(f.get("news_trading")), ""),
                    ("规则表", lambda f: f'<a href="{url("/crypto/" + f["slug"] + "/")}" lang="en">查看</a>', "")], "加密货币自营交易公司排名")
    secs = [("排名", t + f'<p class="note">只想看在交易所账户或交易所行情终端上交易永续合约的公司？见<a href="{url("/zh/crypto-exchange/")}">加密交易所类自营交易公司</a>；期货与 CFD 公司见<a href="{url("/zh/futures/")}">期货</a>和<a href="{url("/zh/cfd/")}">差价合约</a>分类。</p>' + '<p class="small">“规则表”链接到英文的加密货币专项规则：交易场所、合约类型、交易对数量、杠杆、机器人与跟单规则。</p>'),
            ("加密原生还是多资产？", f"<p>加密原生公司（{e(zlist([f['name'] for f in nat]))}）通常提供永续合约、交易所式订单簿、较高杠杆，并用稳定币出金。多资产公司把加密货币作为 CFD 放在外汇旁边，适合把加密只当作众多品种之一的交易者，但加密杠杆通常更低、点差更宽。</p>"),
            ("买加密挑战前要看什么", "<p><b>订单去哪里成交。</b>交易所式公司会接入 Bybit、BloFin 的模拟账户或自有终端，订单簿和资金费率更接近真实市场；CFD 公司自行报价，点差更宽，有时会因维护暂停加密品种。</p>"
             "<p><b>实际能用的杠杆。</b>加密原生公司常给 50 到 100 倍；多资产公司即使外汇给到 1:100，加密往往只有 1:1 到 1:5。仓位应按回撤限制来定，而不是按杠杆。</p>"
             "<p><b>周末与跳空。</b>加密货币周末照常交易，但并非每家公司都允许周末持仓。做波段前先看表中的“周末持仓”一栏。</p>"
             "<p><b>怎么收款。</b>多数加密原生公司用 USDT 或 USDC 出金。留意最低出金额、单次上限，以及首次出金前是否必须完成 KYC。</p>"
             "<p><b>机器人与跟单。</b>网格机器人、套利和跟单是加密账户最常见的违规原因。每家公司禁止什么，见英文规则表。</p>")]
    qa = [("最好的加密货币自营交易公司是哪家？", f"按 PA 评分，加密原生公司中排名第一的是 {top['name']}（{top['_score']:.1f}/10）。如果把提供加密 CFD 的多资产公司也算进来，第一名是 {fl[0]['name']}（{fl[0]['_score']:.1f}）。"),
          ("最便宜的加密货币挑战是哪家？", f"在我们追踪的加密公司中，{cheap['name']} 的公开入场费最低：{money(cheap['_fee'], cheap.get('fee_currency'))}。"),
          ("加密自营交易公司用什么出金？", "加密原生公司大多用 USDT 或 USDC 等稳定币出金，通常需要先完成 KYC。具体币种、链和最低金额以各公司官网为准。")]
    zh_shell("/zh/crypto/", [("首页", "/zh/"), ("加密货币", "/zh/crypto/")], "加密货币自营交易公司：逐条规则对比",
             f"{YEAR_NOW} 加密货币自营交易公司排名：{len(fl)} 家规则对比 | PropAnalyse",
             f"{len(fl)} 家提供加密货币交易的自营交易公司对比：永续合约还是 CFD、杠杆、周末持仓、机器人规则与 USDT 出金，按公开评分排序。",
             ans, [f'<b class="n">{len(fl)}</b> 家公司', f'<b class="n">{len(nat)}</b> 家加密原生', f'<b class="n">{money(cheap["_fee"], cheap.get("fee_currency"))}</b> 起'], secs, qa, rel=zh_rel("/zh/crypto/"))

# ---------------- /zh/countries/<slug>/ ----------------
ZH_CTX = {
 "china": "中国大陆交易者常选择用 USDT 等稳定币出金的公司。本页只核对各公司自己公布的限制名单，不涉及当地法规；参与境外金融服务前，请自行了解适用的规定。",
 "hong-kong": "我们按名单原文匹配：只有名单明确写出“Hong Kong”才算限制香港。若某公司只写“China”，是否包括香港请以其条款为准。",
 "taiwan": "我们按名单原文匹配：只有名单明确写出“Taiwan”才算限制台湾。名单写法不清楚时，请在付款前向客服确认。",
 "singapore": "我们按名单原文匹配：只有名单明确写出“Singapore”才算限制新加坡。付款与出金方式请以各公司官网为准。",
 "malaysia": "我们按名单原文匹配：只有名单明确写出“Malaysia”才算限制马来西亚。付款与出金方式请以各公司官网为准。",
}
def zh_country(slug, zname):
    aliases = next(a for s, _, a in COUNTRIES if s == slug)
    st = {f["slug"]: country_status(f, aliases) for f in RANKED}
    restricted = [f for f in RANKED if st[f["slug"]][0] == "restricted"]
    partial = [f for f in RANKED if st[f["slug"]][0] == "partial"]
    open_ = [f for f in RANKED if st[f["slug"]][0] in ("open", "open_catchall")]
    nolist = [f for f in RANKED if st[f["slug"]][0] == "nolist"]
    withlist = len(restricted) + len(partial) + len(open_)
    path = f"/zh/countries/{slug}/"
    top = open_[0] if open_ else None
    cheap = min((f for f in open_ if f["_fee"] is not None), key=lambda f: f["_fee"], default=None)
    cry = [f for f in open_ if is_native(f)]
    fut_r = [f for f in restricted if f.get("category") == "futures"]
    nr = len(restricted)
    ans = ((f"在我们追踪的 {len(FIRMS)} 家自营交易公司中，没有一家把{zname}列入限制国家名单。" if nr == 0 else
            f"在我们追踪的 {len(FIRMS)} 家自营交易公司中，有 {nr} 家把{zname}列入限制国家名单：{zlist([f['name'] for f in restricted])}。")
           + (f"{zlist([f['name'] for f in partial])} 只作部分限制。" if partial else "")
           + f"另有 {len(open_)} 家公布了名单但没有列出{zname}，{len(nolist)} 家没有公布我们能核实的国家名单，付款前请向它们确认。"
           + (f"在名单未列出{zname}的公司中，评分最高的是 {top['name']}（{top['_score']:.1f}/10）" if top else "")
           + (f"，入场费最低的是 {cheap['name']}，{money(cheap['_fee'], cheap.get('fee_currency'))} 起。" if cheap else ("。" if top else "")))
    def ct(fl, cap, note=None):
        cols = [ZFIRM, ZSCORE, ZCAT, ZFEE, ZSPLIT, ZPAY]
        if note: cols.append(("说明", note, ""))
        return gtable(fl, cols, cap)
    def note_open(f):
        return '<small>同时限制 FATF 高风险及受制裁地区，请查看其最新名单</small>' if st[f["slug"]][0] == "open_catchall" else '<small>未在其公布的名单上</small>'
    secs = []
    if restricted: secs.append((f"不接受{zname}的公司", ct(restricted, f"限制{zname}的公司", lambda f: f'<small>名单原文：“{e(st[f["slug"]][1])}”</small>')))
    if partial: secs.append(("部分限制", ct(partial, f"部分限制{zname}的公司", lambda f: f'<small>{e(st[f["slug"]][1])}</small>')))
    secs.append((f"名单未列出{zname}（{len(open_)} 家）", ct(open_, f"名单未列出{zname}的公司", note_open) if open_ else "<p>无。</p>"))
    if nolist: secs.append((f"未公布国家名单（{len(nolist)} 家）", "<p>这些公司没有公布我们能核实的国家名单。没有名单不等于接受：付款前请阅读其条款或咨询客服。</p>" + ct(nolist, "未公布国家名单的公司")))
    ctx = [ZH_CTX.get(slug, "")]
    if fut_r: ctx.append(f"期货公司最严格：{e(zlist([f['name'] for f in fut_r]))} 限制{zname}。美国期货公司的国家名单通常较长，与其清算和支付服务商有关。")
    if cry: ctx.append(f"按我们的数据，对{zname}开放的加密原生公司有：{e(zlist([f['name'] for f in cry]))}。它们通常用 USDT 或 USDC 出金，不受银行电汇限制，但仍需 KYC。")
    ctx.append(f'名单可能随时变化。每次核实公司时我们都会重读其名单，日期显示在每个公司页面，变化记录在<a href="{url("/news/")}">规则变更</a>页面。')
    secs.append(("须知", "".join(f"<p>{x}</p>" for x in ctx if x)))
    qa = [(f"{zname}的交易者可以参加自营交易公司吗？", f"大多数可以。公布了名单的公司中，{len(open_)} 家没有列出{zname}，{nr} 家明确限制。" + (f"限制的公司是：{zlist([f['name'] for f in restricted])}。" if restricted else "")),
          (f"哪些自营交易公司不接受{zname}？", (f"{zlist([f['name'] for f in restricted])} 在官网名单中把{zname}列为限制地区。" if restricted else f"在 {withlist} 家公布名单的公司中，没有一家限制{zname}。") + "名单会变化，付款前请再次查看公司条款。")]
    if cheap: qa.append((f"{zname}最便宜的自营交易公司是哪家？", f"在名单未列出{zname}的公司中，{cheap['name']} 最便宜，{money(cheap['_fee'], cheap.get('fee_currency'))} 起。没有公布名单的公司可能更便宜，请先确认其条款。"))
    zh_shell(path, [("首页", "/zh/"), (zname, path)], f"接受{zname}交易者的自营交易公司",
             f"接受{zname}交易者的自营交易公司（{YEAR_NOW}）：{nr} 家限制 | PropAnalyse",
             f"哪些自营交易公司接受{zname}交易者：{len(FIRMS)} 家中有 {nr} 家限制{zname}，逐一核对各公司官网的限制国家名单，附费用与 PA 评分。",
             ans, [f'<b class="n">{nr}</b> 家限制', f'<b class="n">{len(open_)}</b> 家未列出', f'<b class="n">{len(nolist)}</b> 家未公布名单'], secs, qa, noindex=(withlist < 5), rel=zh_rel(path))

# ---------------- /zh/sizes/<k>/ ----------------
def zh_size(s):
    k = f"{s // 1000}K"
    rows = sorted([f for f in FIRMS if fee_at(f, s)], key=lambda f: fee_at(f, s))
    if not rows: return
    path = f"/zh/sizes/{k.lower()}/"
    P = lambda f: prog_at(f, s)[0]
    fees = [fee_at(f, s) for f in rows]; med = statistics.median(fees)
    a, z = rows[0], rows[-1]
    cry = [f for f in rows if "crypto" in f["_assets"]]
    mon = [f for f in rows if f["_x"].get("monthly_fee")]
    per = lambda f: CUR.get(f.get("fee_currency") or "USD", DOL) + f"{fee_at(f, s) / (s / 1000):.2f}"
    ans = (f"我们追踪的公司中有 {len(rows)} 家提供 {DOL}{k} 账户。最便宜的是 {a['name']} 的 {P(a).get('name')}，{money(fee_at(a, s), a.get('fee_currency'))}（每 1,000 美元规模 {per(a)}）。"
           f"中位数是 {money(med)}，最贵的是 {z['name']}，{money(fee_at(z, s), z.get('fee_currency'))}。"
           + (f"提供加密货币的公司里最便宜的是 {cry[0]['name']}，{money(fee_at(cry[0], s), cry[0].get('fee_currency'))}。" if cry and cry[0] is not a else "")
           + (f"{zlist([f['name'] for f in mon])} 按月收费，通过之前每月都会重复扣费。" if mon else ""))
    t = gtable(rows, [zrank(rows), ZFIRM, ("方案", lambda f: e(P(f).get("name") or "") + f'<small>{e(ztype(P(f).get("type")))}</small>', ""),
                      ("费用", lambda f: mh(fee_at(f, s), f.get("fee_currency")) + ('<small>按月收费</small>' if f["_x"].get("monthly_fee") else ''), "num n"),
                      ("每 1K", lambda f: per(f), "num n"), ("盈利目标", lambda f: zshow(P(f).get("profit_target")), "n"),
                      ("日亏损 / 最大回撤", lambda f: e(f'{P(f).get("max_daily_loss") or "-"} / {P(f).get("max_drawdown") or "-"}'), "n"),
                      ("分成", lambda f: zsplit(P(f).get("profit_split")), ""), ZSCORE], f"{k} 自营交易挑战价格")
    secs = [(f"所有 {DOL}{k} 挑战，从便宜到贵", t + '<p class="small">每家公司只列出该规模下最便宜的一个方案。FTMO 以欧元定价，未做汇率换算。</p>'),
            ("价格不等于成本", f'<p>标价最低的方案往往日亏损限制最紧，或使用跟踪回撤。首次出金退还挑战费、重考折扣，对总成本的影响通常比几十美元的差价更大。可以用<a href="{url("/tools/true-cost/")}">真实成本计算器</a>（英文）算一算。</p>')]
    qa = [(f"最便宜的 {DOL}{k} 自营交易挑战是哪家？", f"按我们最近一次核实，是 {a['name']} 的 {P(a).get('name')}，{money(fee_at(a, s), a.get('fee_currency'))}。"),
          (f"{DOL}{k} 自营交易账户要多少钱？", f"在 {len(rows)} 家公司中，{DOL}{k} 挑战费的中位数是 {money(med)}，范围从 {money(fee_at(a, s), a.get('fee_currency'))} 到 {money(fee_at(z, s), z.get('fee_currency'))}。")]
    zh_shell(path, [("首页", "/zh/"), (f"{DOL}{k} 挑战", path)], f"{DOL}{k} 自营交易挑战价格对比",
             f"最便宜的 {DOL}{k} 自营交易挑战（{YEAR_NOW}）：{len(rows)} 家按价格排序 | PropAnalyse",
             f"我们追踪的所有 {DOL}{k} 自营交易挑战，从便宜到贵：{len(rows)} 家公司，{money(fee_at(a, s), a.get('fee_currency'))} 起，附盈利目标、回撤、分成与每 1,000 美元成本。",
             ans, [f'<b class="n">{len(rows)}</b> 家公司', f'<b class="n">{money(fee_at(a, s), a.get("fee_currency"))}</b> 起', f'中位数 <b class="n">{money(med)}</b>'], secs, qa, noindex=(len(rows) < 4), rel=zh_rel(path))

# ---------------- /zh/methodology/ ----------------
def zh_method():
    c, bl = crumbs([("首页", "/zh/"), ("评分方法", "/zh/methodology/")])
    body = f"""<div class="wrap">{c}<article class="prose"><h1>我们如何收集数据、如何评分</h1>
<p class="note"><b>利益披露。</b>PropAnalyse 由 FundedXYZ 背后的团队运营。FundedXYZ 与其他所有公司使用同一套评分规则：没有人工调整，不默认置顶，数据也按同一份清单收集。</p>
<h2>数字从哪里来</h2><p>每个数字都读自该公司自己的网站（价格页、规则页、FAQ 或帮助中心），并按公司记录核实日期。评分来自该公司公开的 Trustpilot 页面。公司没有公布的数字，我们显示“未公布”，从不估算。</p>
<h2 id="account-types">账户类型</h2><p>每家公司只归入一个账户类型，依据是该公司官网列出的交易平台和产品。如果一家公司销售两类账户，按主推产品归类，另一类记为“也提供”。账户类型不影响 PA 评分。</p>
<table class="mini"><thead><tr><th scope="col">类型</th><th scope="col">交易什么、在哪里交易</th></tr></thead><tbody>
<tr><td><a href="{url('/zh/futures/')}"><b>期货</b></a></td><td>交易所上市期货，主要是 CME 集团合约，通过 Rithmic、Tradovate、NinjaTrader 或公司自有期货平台交易；风控多为美元回撤。</td></tr>
<tr><td><a href="{url('/zh/cfd/')}"><b>差价合约 (CFD)</b></a></td><td>在 MT5、MT4、cTrader、DXtrade 或 Match-Trader 上交易外汇、黄金、指数，常含加密货币 CFD；风控多为百分比。</td></tr>
<tr><td><a href="{url('/zh/crypto-exchange/')}"><b>加密交易所</b></a></td><td>在通过 API 连接的交易所账户（Bybit、BloFin）或加密原生公司按交易所行情报价的自有终端上交易永续合约，通常以稳定币出金。</td></tr></tbody></table>
<h2>PA 评分（0 到 10 分）</h2><p>一个公式，由构建脚本机械地计算：</p>
<table class="mini"><thead><tr><th scope="col">组成</th><th scope="col" class="num">权重</th><th scope="col">输入</th></tr></thead><tbody>
<tr><td>信任</td><td class="num n">30%</td><td>Trustpilot 分数（3.0 记 0 分，5.0 记满分），按评价数量（log₁₀）加权</td></tr>
<tr><td>成本</td><td class="num n">20%</td><td>所有公开方案中，每 1,000 美元账户规模的最低费用</td></tr>
<tr><td>规则</td><td class="num n">20%</td><td>日亏损限制、最大回撤、静态或跟踪回撤、新闻交易、周末持仓、一致性规则</td></tr>
<tr><td>出金</td><td class="num n">20%</td><td>主推分成比例、首次出金天数、出金周期</td></tr>
<tr><td>经营年限</td><td class="num n">10%</td><td>运营年数（8 年以上记满分）</td></tr></tbody></table>
<p>出金周期取公司主推（列在第一位）的方案。费用按公司定价的币种比较（FTMO 用欧元），不做汇率换算。Trustpilot 页面不显示评分（例如因违反准则被暂停）时按缺失处理。</p><p>缺失的输入在该项记 4/10，所以隐瞒信息永远不会让公司得分更高。每个公司页面都显示分项得分和数据完整度百分比。</p>
<h2>评分不代表什么</h2><p>它不预测你能否通过考核或拿到出金，也不是投资建议。联盟推广关系不影响评分或排序。</p>
<h2>纠错</h2><p>公司经常修改规则。如果发现过时的数字，请附上该公司页面的链接告诉我们，我们会重新核实。参见<a href="{url('/updates/')}">核实记录</a>（英文）。</p>
<p class="small">完整公式在 <code>scripts/build.py</code>；数据集公开在 <a href="{url('/data/firms.json')}">/data/firms.json</a>。<a href="{url('/methodology/')}" lang="en" hreflang="en">English version</a></p></article></div>"""
    page("/zh/methodology/", "数据来源与评分方法 | PropAnalyse", "PropAnalyse 如何收集自营交易公司数据、如何计算 PA 评分，以及利益披露。", body, [bl], lang="zh")

def zh_pages():
    zh_home(); zh_crypto()
    for s, n in ZH_COUNTRIES: zh_country(s, n)
    for x in ZH_SIZES: zh_size(x)
    zh_method()

_prog_prev_zh = programmatic
def programmatic():
    _prog_prev_zh(); zh_pages()

FOOT_EXTRA.append(("/zh/", "中文"))
_seo_prev_zh = seo_files
def seo_files():
    _seo_prev_zh()
    L = ["", "## 中文 (zh-Hans)"] + [f"- [{ABS}{p}]({ABS}{p}): Chinese version of {ABS}{k}" for k, p in ZH_ALT.items() if p in PAGES and p not in NOINDEX]
    open(os.path.join(OUT, "llms.txt"), "a").write("\n".join(L) + "\n")
