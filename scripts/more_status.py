# PropAnalyse firm status (2026-10-31): every firm is active, caution or closed (data/status.json, merged into firms.json by merge.py).
#   caution = still selling, but documented warning signs (Trustpilot rating suspended + payout-denial cluster, payout-denial cluster,
#             regulator action). Full firm page + red banner with the dated evidence; PA Score capped at ST_CAP (published on /methodology/);
#             ranked below every active firm; no offers / promo codes / best-of lists; Visit buttons read "Visit (caution)"; badge shows Caution.
#   closed  = no longer operating or selling. Firm page /firms/<slug>/ marked Closed (what happened, date, sources, what traders can do),
#             not rated, no offers or Visit links. Hub /closed-prop-firms/ (+ /zh/). Closed firms are NOT in FIRMS (no rule data).
#   /caution/ lists caution firms with the evidence. Status is re-checked every ST_REVIEW_DAYS days; firms request a review via /for-firms/.
# Exec'd LAST into build.py's namespace (after more_complaints.py). Globals prefixed ST_/st_.
ST_FILE = os.path.join(ROOT, "data", "status.json")
ST = json.load(open(ST_FILE))
ST_RULE = ST.get("rule", {})
ST_CAP = float(ST_RULE.get("caution_cap", 4.0))
ST_REVIEW_DAYS = int(ST_RULE.get("review_days", 30))
ST_CAUTION = ST.get("caution", {})
ST_CLOSED = sorted(ST.get("closed", []), key=lambda c: str(c.get("status_since") or ""), reverse=True)
ST_CLOSED_BY = {c["slug"]: c for c in ST_CLOSED}
ST_V = "1"
ASSET_V = "13"

def st_is_caution(f): return (f or {}).get("status") == "caution"
def st_date(d):
    d = str(d or "")
    try:
        if len(d) == 7: return datetime.date.fromisoformat(d + "-01").strftime("%B %Y")
        if len(d) == 4: return d
        return nice_date(d)
    except Exception: return d
def st_date_zh(d):
    d = str(d or "")
    p = d.split("-")
    if len(p) >= 2 and p[0].isdigit() and p[1].isdigit():
        return f"{p[0]} 年 {int(p[1])} 月" + (f" {int(p[2])} 日" if len(p) > 2 and p[2].isdigit() else "")
    return d
def st_next_check(s):
    base = s.get("checked") or TODAY
    try: return (datetime.date.fromisoformat(str(base)[:10]) + datetime.timedelta(days=ST_REVIEW_DAYS)).isoformat()
    except Exception: return ""
def st_host(u): return re.sub(r"^https?://(www\.)?", "", str(u or "")).split("/")[0]
def st_a(u, t=None):
    return f'<a href="{e(u)}" rel="nofollow noopener" target="_blank">{e(t or st_host(u))}</a>'

# ---------------- apply status to the dataset ----------------
ST_FIELD_MAP = {"status_since": "status_since", "status_reason": "status_reason", "status_sources": "status_sources", "status_evidence": "evidence", "status_checked": "checked"}
for _f in FIRMS:
    _s = ST_CAUTION.get(_f["slug"])
    if _s:
        _f["status"] = "caution"
        for _k, _src in ST_FIELD_MAP.items():
            if _s.get(_src) is not None: _f[_k] = _s[_src]
        _f["_score_formula"] = _f["_score"]
        _f["_score"] = round(min(_f["_score"], ST_CAP), 1)
        _f["_st_code"] = _f.get("discount_code")
        _f["discount_code"] = None          # no promo codes while a caution stands (offers, chips, carousel, /discounts/)
    else:
        _f["status"] = _f.get("status") or "active"
RANKED[:] = sorted(FIRMS, key=lambda f: (st_is_caution(f), -f["_score"]))
for _i, _f in enumerate(RANKED): _f["_rank"] = _i + 1
if "CRYPTO_FIRMS" in globals(): CRYPTO_FIRMS[:] = [f for f in RANKED if f in CRYPTO_FIRMS]
ST_CAUT = [f for f in RANKED if st_is_caution(f)]
ST_ACTIVE = [f for f in RANKED if not st_is_caution(f)]

# best-of lists, "Listed in", home list counts: caution firms never qualify
BEST[:] = [(s, t, d, (lambda fn: (lambda f: (not st_is_caution(f)) and bool(fn(f))))(fn)) for s, t, d, fn in BEST]
if "BEGINNERS" in globals():
    _st_prev_beginners = BEGINNERS
    def BEGINNERS(): return [f for f in _st_prev_beginners() if not st_is_caution(f)]

# ---------------- small components ----------------
ST_WARN = '<svg class="sti" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M12 3.5 21.5 20h-19z"/><path d="M12 10v4.5M12 17.4h.01"/></svg>'
ST_STOP = '<svg class="sti" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="8.8"/><path d="M5.8 18.2 18.2 5.8"/></svg>'
def st_chip(f=None, zh=False, closed=False):
    if closed: return f'<span class="stchip closed" title="{"已关闭" if zh else "Closed: no longer operating"}">{ST_STOP}{"已关闭" if zh else "Closed"}</span>'
    return f'<span class="stchip" title="{"警示：见公司页面上的证据" if zh else "Caution: see the evidence on the firm page"}">{ST_WARN}{"警示" if zh else "Caution"}</span>'

_st_prev_visit = visit
def visit(f, label=None, cls="visit"):
    if st_is_caution(f): return _st_prev_visit(f, "Visit (caution)", cls + " vcaution")
    return _st_prev_visit(f, label, cls)

_st_prev_row = row
def row(f, rk=None):
    h = _st_prev_row(f, rk)
    if not st_is_caution(f): return h
    h = h.replace("<tr ", '<tr data-status="caution" class="st-caution" ', 1)
    return h.replace(f"<b>{e(f['name'])}</b>", f"<b>{e(f['name'])}</b>{st_chip()}", 1)

if "flink" in globals():
    _st_prev_flink = flink
    def flink(f, sub="/firms/"):
        h = _st_prev_flink(f, sub)
        return h + " " + st_chip() if st_is_caution(f) else h
    FIRMCOL = ("Firm", lambda f: flink(f), "")

if "top_rated" in globals():
    _st_prev_top_rated = top_rated
    def top_rated(cat):
        keep = RANKED[:]
        try:
            RANKED[:] = [f for f in keep if not st_is_caution(f)]
            return _st_prev_top_rated(cat)
        finally:
            RANKED[:] = keep

if "rate_html" in globals():
    _st_prev_rate = rate_html
    def rate_html(f, big=False):
        h = _st_prev_rate(f, big)
        if st_is_caution(f):
            h = h.replace('class="rate', 'class="rate st-capped', 1).replace(
                f'title="PA Score {f["_score"]:.1f} of 10', f'title="PA Score {f["_score"]:.1f} of 10, capped by the caution rule (formula {f["_score_formula"]:.1f})', 1)
        return h

if "badge_svg" in globals():
    _st_prev_badge_svg = badge_svg
    def badge_svg(f, size="standard", theme="light"):
        s = _st_prev_badge_svg(f, size, theme)
        if not st_is_caution(f): return s
        red = "#c4320a" if theme != "dark" else "#ff8a66"
        s = s.replace("</style>", f".st{{fill:{red}}}.sb{{stroke:{red}}}" + ("@media (prefers-color-scheme:dark){.st{fill:#ff8a66}.sb{stroke:#ff8a66}}" if theme == "auto" else "") + "</style>", 1)
        s = s.replace('<rect class="b"', '<rect class="b sb" stroke-width="1.5"', 1)
        s = re.sub(r'(<title id="t">)(.*?)(</title>)', lambda m: m.group(1) + m.group(2) + ". Caution: warnings listed on PropAnalyse" + m.group(3), s, count=1)
        if size == "compact":
            s = re.sub(r'<text x="52" y="37" class="m" font-size="10">.*?</text>', '<text x="52" y="37" class="st" font-size="10" font-weight="700">CAUTION \u00b7 warnings listed</text>', s, count=1)
        else:
            s = re.sub(r'<text x="16" y="104" class="m" font-size="10.5">.*?</text>', '<text x="16" y="104" class="st" font-size="10.5" font-weight="700">CAUTION \u00b7 score capped, warnings listed</text>', s, count=1)
        return s
    _st_prev_badge_data = badge_data
    def badge_data():
        d = _st_prev_badge_data()
        for f in ST_CAUT:
            if f["slug"] in d["firms"]: d["firms"][f["slug"]]["st"] = "caution"
        return d
    _st_prev_balt = balt
    def balt(f): return _st_prev_balt(f) + (" (caution)" if st_is_caution(f) else "")

# ---------------- banners ----------------
def st_evidence_list(s, zh=False):
    li = ""
    for x in s.get("evidence") or []:
        src = (f' <span class="stsrc">{st_a(x["url"], "来源" if zh else "Source")}' + (f', {e(st_date_zh(x["date"]) if zh else st_date(x["date"]))}' if x.get("date") else "") + "</span>") if x.get("url") else ""
        li += f'<li>{e(x.get("text_zh") if zh and x.get("text_zh") else x.get("text", ""))}{src}</li>'
    return f'<ul class="stev">{li}</ul>' if li else ""

def st_caution_banner(f):
    s = ST_CAUTION.get(f["slug"]) or {}
    n = e(f["name"]); since = s.get("status_since") or TODAY; nxt = st_next_check(s)
    resp = s.get("firm_response")
    resp_h = (f'<p class="stresp"><b>{n}\u2019s response:</b> {e(resp.get("text", ""))}' + ((f' ({st_a(resp["url"], "source")}' + (f', {e(st_date(resp.get("date")))}' if resp.get("date") else "") + ")") if resp.get("url") else "") + "</p>") if resp else ""
    score_line = (f'While the caution stands its PA Score is capped at <b class="n">{ST_CAP:.1f}</b>/10 (formula score <span class="n">{f["_score_formula"]:.1f}</span>), it is ranked below every active firm, '
                  f'and we show no offers, promo codes or best-of listings for it.')
    return f"""<section class="stban caution" id="status" role="note" aria-labelledby="st-h"><p class="stk">{ST_WARN}<span>Caution</span></p>
<h2 id="st-h">{n} is listed with a caution</h2><p class="stwhy">{e(s.get("status_reason") or "")}</p>{st_evidence_list(s)}{resp_h}
<p class="stfine">{score_line} Listed since <time datetime="{e(since)}">{e(st_date(since))}</time>; status re-checked every {ST_REVIEW_DAYS} days (next by <time datetime="{e(nxt)}">{e(st_date(nxt))}</time>). These are reports from the sources linked above, not a finding by PropAnalyse. {n} can request a review with evidence via <a href="{url("/for-firms/")}#status-review">For prop firms</a>.
<a href="{url("/methodology/")}#status">How caution works</a> · <a href="{url("/caution/")}">All firms with warnings</a></p></section>"""

def ST_CSS_LINK(): return f'<link rel="stylesheet" href="{url("/assets/status.css")}?v={ST_V}">'

# ---------------- page wrapper ----------------
ST_SCAM_RX = re.compile(r"We found no reason in the published data to call it one; its evidence level is \w+\. ")
_st_prev_page = page
def page(path, title, desc, body, jsonld=None, og_type="website", extra_head="", lang="en"):
    extra_head = (extra_head or "") + ST_CSS_LINK()
    m = re.fullmatch(r"/(firms|crypto)/([^/]+)/(legit/)?", path)
    f = BY.get(m.group(2)) if m else None
    if f and st_is_caution(f) and 'id="status"' not in body:
        ban = st_caution_banner(f)
        if '</nav><header class="phead">' in body: body = body.replace('</nav><header class="phead">', "</nav>" + ban + '<header class="phead">', 1)
        elif '</nav><article class="guide">' in body: body = body.replace('</nav><article class="guide">', "</nav>" + ban + '<article class="guide">', 1)
        elif "</nav>" in body: body = body.replace("</nav>", "</nav>" + ban, 1)
        else: body = ban + body
        if m.group(1) == "firms" and not m.group(3):
            body = re.sub(r'(<p class="rk">.*?</p>)', lambda mm: mm.group(1) + f'<p class="stcap">{ST_WARN}<span>Capped at {ST_CAP:.1f} by the <a href="{url("/methodology/")}#status">caution rule</a>. Formula score <b class="n">{f["_score_formula"]:.1f}</b>.</span></p>', body, count=1)
            body = body.replace("<p class=\"deal none\">No public discount code on the firm's site at last check.</p>", '<p class="deal none">Promo codes are not shown while a caution stands.</p>', 1)
        rep = (f"PropAnalyse does not make that call, and we found no regulator or court finding on the pages we checked. We do list {f['name']} with a caution: "
               f"{(ST_CAUTION[f['slug']].get('status_reason') or '').rstrip('.')}. The sources are linked on its page. ")
        body = ST_SCAM_RX.sub(lambda _m: rep, body)
        if jsonld: jsonld = json.loads(ST_SCAM_RX.sub(lambda _m: rep.replace('"', "'"), json.dumps(jsonld, ensure_ascii=False)))
        if "(Caution)" not in title: title = title.replace(" | PropAnalyse", " (Caution) | PropAnalyse")
    if path == "/methodology/" and 'id="status"' not in body:
        a = "<h2>What the score is not</h2>"
        body = body.replace(a, st_meth_en() + a, 1) if a in body else body.replace("</article>", st_meth_en() + "</article>", 1)
    elif path == "/zh/methodology/" and 'id="status"' not in body:
        a = "<h2>评分不代表什么</h2>"
        body = body.replace(a, st_meth_zh() + a, 1) if a in body else body.replace("</article>", st_meth_zh() + "</article>", 1)
    elif path == "/for-firms/" and 'id="status-review"' not in body:
        a = '<section class="block prose"><h2>Partnerships</h2>'
        blk = st_forfirms()
        body = body.replace(a, blk + a, 1) if a in body else body + blk
        body = body.replace('<option value="Other">Other</option>', '<option value="Status review">Review a caution or closed status</option><option value="Other">Other</option>', 1)
    return _st_prev_page(path, title, desc, body, jsonld, og_type, extra_head, lang)

# ---------------- methodology + for-firms text ----------------
def st_trig_en(): return [x.get("en") for x in ST_RULE.get("triggers", []) if x.get("en")]
def st_trig_zh(): return [x.get("zh") for x in ST_RULE.get("triggers", []) if x.get("zh")]
def st_meth_en():
    trig = "".join(f"<li>{e(t)}</li>" for t in st_trig_en())
    return f"""<h2 id="status">Caution and closed firms</h2><p>Every firm has a status: <b>active</b>, <b>caution</b> or <b>closed</b>. Status is set from dated public sources, never from our opinion of a firm, and re-checked at least every {ST_REVIEW_DAYS} days.</p>
<p><b>Caution.</b> A firm that is still selling gets a caution when, at a check, any of these holds and is documented with a dated link:</p><ul>{trig}</ul>
<p>While a caution stands: <b>PA Score = the lower of the formula score and {ST_CAP:.1f}</b> (at most {ST_CAP / 2:g} stars), and the formula score is shown next to it; the firm is ranked below every active firm by default; it gets no offers, promo codes, carousel slot or best-of listing; its Visit buttons read \u201cVisit (caution)\u201d; and its badge shows Caution. The firm page and <a href="{url('/caution/')}">/caution/</a> list the evidence with links.</p>
<p>A caution is lifted at the first re-check where no trigger holds. A firm can ask for an earlier review with evidence (for example, proof that the disputed payouts were paid) through <a href="{url('/for-firms/')}#status-review">For prop firms</a>.</p>
<p><b>Closed.</b> A firm is closed when it has stopped operating or selling: its own announcement, a regulator or court action that stopped the business, a Trustpilot closure notice, or a domain that is parked, for sale or offline with no replacement site. Closed firms are not rated (no score, 0 stars), get no offers or Visit links, and keep a page that records what happened, when, the sources, and what affected traders can do. See <a href="{url('/closed-prop-firms/')}">closed prop firms</a>.</p>
<p><b>Wording.</b> We report what sources say and name the source. We do not call a firm a scam or fraud unless a regulator or court has, and then we quote it and link to it.</p>
"""
def st_meth_zh():
    trig = "".join(f"<li>{e(t)}</li>" for t in st_trig_zh())
    return f"""<h2 id="status">警示与已关闭的公司</h2><p>每家公司都有一个状态：<b>正常</b>、<b>警示</b>或<b>已关闭</b>。状态依据有日期的公开来源设定，而不是我们对公司的看法，并且至少每 {ST_REVIEW_DAYS} 天复查一次。</p>
<p><b>警示。</b>仍在销售的公司，在检查时只要满足以下任一条件、且有带日期的链接为证，就会被标记警示：</p><ul>{trig}</ul>
<p>警示期间：<b>PA 评分 = 公式评分与 {ST_CAP:.1f} 中较低者</b>（最多 {ST_CAP / 2:g} 星），并同时显示公式评分；默认排在所有正常公司之后；不展示优惠、折扣码、轮播位或“最佳”榜单；“访问”按钮显示为“访问（警示）”；徽章显示警示。公司页面和 <a href="{url('/caution/')}">/caution/</a> 列出证据与链接。</p>
<p>在任一次复查中不再满足任何条件时，警示即解除。公司可以通过<a href="{url('/for-firms/')}#status-review">合作公司页面</a>提交证据（例如已支付争议出金的证明），申请提前复查。</p>
<p><b>已关闭。</b>公司停止运营或销售时标记为已关闭：公司自己的公告、监管机构或法院令其停业的行动、Trustpilot 的关闭提示，或域名已停放、出售或下线且没有替代网站。已关闭的公司不评分（无评分、0 星），不提供优惠或访问链接，并保留一个页面记录发生了什么、何时发生、来源，以及受影响的交易者可以做什么。见<a href="{url('/zh/closed-prop-firms/')}">已关闭的自营交易公司</a>。</p>
<p><b>措辞。</b>我们只转述来源的说法并注明来源。除非监管机构或法院已作出认定（届时我们引用原文并附链接），我们不会称任何公司为骗局或欺诈。</p>
"""
def st_forfirms():
    return f"""<section class="block prose" id="status-review"><h2>Caution or closed status: request a review</h2><p>Some firms carry a <a href="{url('/caution/')}">caution</a> or are listed as <a href="{url('/closed-prop-firms/')}">closed</a>. Both are based on dated public sources, linked on the firm page, and re-checked every {ST_REVIEW_DAYS} days. If you think a status is wrong or out of date, send evidence with the form above (choose \u201cReview a caution or closed status\u201d) or write to <a href="mailto:{PARTNERS}">{PARTNERS}</a>.</p>
<p>Useful evidence: proof that disputed payouts were paid (dates, amounts, transaction IDs), Trustpilot reinstating your rating, a regulator closing its file, or, for a closed listing, your live site, checkout and terms. We reply with what we checked. A status can never be bought, and affiliate deals do not change it.</p></section>"""

# ---------------- closed firm pages ----------------
def st_logo_closed(c, px=48):
    ini = "".join(w[0] for w in re.findall(r"[A-Za-z0-9]+", c["name"])[:2]).upper()
    return f'<span class="flogo ini stgrey" style="width:{px}px;height:{px}px" role="img" aria-label="{e(c["name"])} (closed)"><b>{e(ini)}</b></span>'
def st_rate_closed(c, zh=False):
    t = "已关闭，不评分" if zh else "Closed: not rated"
    return f'<span class="rate st-closed" title="{t}"><b>{"不评分" if zh else "Not rated"}</b><span class="stars" style="--v:0%" aria-hidden="true"></span><span class="sr"> {t}</span></span>'
def st_srcs(c, zh=False):
    li = ""
    for s in c.get("status_sources") or []:
        meta = " · ".join(x for x in (e(s.get("publisher") or st_host(s.get("url"))), (e(st_date_zh(s.get("date")) if zh else st_date(s.get("date"))) if s.get("date") else "")) if x)
        q = f'<q>{e(s["quote"])}</q>' if s.get("quote") else ""
        li += f'<li>{st_a(s["url"], s.get("title") or st_host(s["url"]))}<small>{meta}</small>{q}</li>'
    return f'<ol class="src stsrcs">{li}</ol>'
def st_cat(c): return globals().get("CAT_NAME", {}).get(c.get("category"), "") or ""
def st_alts(c, n=4):
    return [f for f in ST_ACTIVE if f.get("category") == c.get("category")][:n] or ST_ACTIVE[:n]

def closed_firm_page(c):
    path = f"/firms/{c['slug']}/"
    n = e(c["name"]); since = c.get("status_since") or ""
    cat = st_cat(c); sincew = st_date(since); chk = c.get("checked") or TODAY
    crumbs_h, bl = crumbs([("Home", "/"), ("Closed prop firms", "/closed-prop-firms/"), (c["name"], path)])
    reg = c.get("regulator")
    reg_h = ""
    if reg:
        reg_h = (f'<section class="block" id="regulator"><h2>Regulator and court record</h2><div class="prose"><p><b>{e(reg.get("name") or "")}</b>' + (f', {e(st_date(reg.get("date")))}' if reg.get("date") else "") + f': {e(reg.get("action") or "")}</p>'
                 + (f'<blockquote class="stq"><p>{e(reg["quote"])}</p><footer>{st_a(reg["url"], reg.get("name") or "Source")}</footer></blockquote>' if reg.get("quote") and reg.get("url") else (f'<p>{st_a(reg["url"], "Source")}</p>' if reg.get("url") else ""))
                 + (f'<p>{e(reg["later"])}</p>' if reg.get("later") else "") + "</div></section>")
    act = c.get("trader_action")
    act_h = (f'<section class="block" id="what-to-do"><h2>If you had an account with {n}</h2><div class="prose"><p>{e(act or "We found no public claims or refund process for this firm.")}</p>'
             '<p class="small">General steps: keep your order receipts, account IDs and emails; if you paid by card, ask your card issuer about a chargeback (time limits apply); report losses to your local regulator or consumer agency. PropAnalyse cannot recover funds.</p></div></section>')
    alts = st_alts(c)
    alt_h = "".join(f'<li><a class="ofirm" href="{url("/firms/" + f["slug"] + "/")}">{logo_html(f, 36)}<span class="on"><b>{e(f["name"])}</b>{rate_html(f)}</span></a></li>' for f in alts)
    wh = c.get("what_happened") or ""
    qa = [(f"Is {c['name']} shut down?", f"Yes. {c.get('status_reason') or ''} We list it as closed since {sincew}; status checked {st_date(chk)}."),
          (f"When did {c['name']} close?", f"{sincew}. " + (c.get("status_reason") or "")),
          (f"What does the {c['name']} website show now?", c.get("site_now") or "Not checked."),
          (f"Can I still get my money back from {c['name']}?", (act or "We found no public claims or refund process.") + " PropAnalyse cannot recover funds."),
          (f"What are alternatives to {c['name']}?", "Active firms of the same account type, ranked by PA Score: " + ", ".join(f["name"] for f in alts) + ". Check each firm's own rules before you buy.")]
    meta = "".join(x for x in [
        (f'<span><a class="cbadge" data-cat="{e(c.get("category"))}" href="{url("/" + c["category"] + "/")}">{e(cat)}</a></span>') if cat else "",
        st_chip(closed=True), (f"<span>{e(c['hq'])}</span>") if c.get("hq") else "",
        (f'<span>Founded <span class="n">{e(str(c["founded"]))}</span></span>') if c.get("founded") else "",
        f'<span>Closed <span class="n">{e(sincew)}</span></span>', f'<span><a href="#sources"><span class="n">{len(c.get("status_sources") or [])}</span> sources</a></span>'])
    body = f"""<div class="wrap">{crumbs_h}<section class="stban closed" id="status" role="note" aria-labelledby="st-h"><p class="stk">{ST_STOP}<span>Closed</span></p>
<h2 id="st-h">{n} is closed{(" (since " + e(sincew) + ")") if since else ""}</h2><p class="stwhy">{e(c.get("status_reason") or "")}</p>
<p class="stfine">Not rated: closed firms get no PA Score, offers or links to buy. Checked <time datetime="{e(chk)}">{e(st_date(chk))}</time>, re-checked every {ST_REVIEW_DAYS} days. Out of date? <a href="{url("/for-firms/")}#status-review">Ask for a review</a> · <a href="{url("/closed-prop-firms/")}">All closed prop firms</a></p></section>
<header class="phead"><div class="sthead">{st_logo_closed(c)}<h1>Is {n} shut down?</h1></div><p class="meta">{meta}</p>
<p class="lede">{e(c.get("status_reason") or "")}</p></header>
<div class="pgrid"><aside class="side" aria-label="PA Score"><div class="scorebox stclosed"><p class="big n">\u2014</p>{st_rate_closed(c)}<p class="rk">Closed: not rated</p><p class="small">Closed firms keep a record here so traders searching for them find what happened. <a href="{url("/methodology/")}#status">How status works</a></p></div></aside>
<div class="pmain"><section class="block" id="what-happened"><h2>What happened to {n}</h2><div class="prose"><p>{e(wh)}</p>{(f'<p><b>Website today:</b> {e(c["site_now"])}</p>') if c.get("site_now") else ""}</div></section>
{reg_h}{act_h}
<section class="block" id="alternatives"><h2>Active {e(cat.lower() + " ") if cat else ""}prop firms instead</h2><p class="small">Ranked by PA Score among active firms of the same account type. Firms with a <a href="{url("/caution/")}">caution</a> are left out.</p><ul class="stalts">{alt_h}</ul></section>
<section class="block faq"><h2>FAQ</h2>{faq_html([(q, e(a)) for q, a in qa])}</section>
<section class="block" id="sources"><h2>Sources</h2><p class="small">What each source said, as read on {e(st_date(chk))}. We report these sources; we do not make findings of our own.</p>{st_srcs(c)}</section></div></div></div>"""
    title = f"Is {c['name']} Shut Down? Closed {sincew}: What Happened | PropAnalyse"
    desc = f"{c['name']} closed{(' (' + sincew + ')') if since else ''}: " + (c.get("status_reason") or "")
    desc = (desc[:152].rsplit(" ", 1)[0] + "…") if len(desc) > 156 else desc
    org = {"@context": "https://schema.org", "@type": "Organization", "name": c["name"]}
    if c.get("site"): org["url"] = c["site"]
    if c.get("founded"): org["foundingDate"] = str(c["founded"])
    if since: org["dissolutionDate"] = since
    page(path, title, desc, body, [bl, faq_ld(qa), org], "article")

def st_closed_rows(zh=False):
    tr = ""
    for c in ST_CLOSED:
        srcs = c.get("status_sources") or []
        reason = (c.get("status_reason_zh") if zh else None) or c.get("status_reason") or ""
        tr += (f'<tr><td class="c-firm"><div class="fcell">{st_logo_closed(c, 32)}<a href="{url("/firms/" + c["slug"] + "/")}"><b>{e(c["name"])}</b><small>{e(st_cat(c))}</small></a></div></td>'
               f'<td class="n nowrap" data-label="{"关闭时间" if zh else "Closed"}"><time datetime="{e(c.get("status_since") or "")}">{e(st_date_zh(c.get("status_since")) if zh else st_date(c.get("status_since")))}</time></td>'
               f'<td class="wide" data-label="{"原因" if zh else "What happened"}">{e(reason)}</td>'
               f'<td class="n nowrap" data-label="{"来源" if zh else "Sources"}">' + " ".join(st_a(s["url"], str(i + 1)) for i, s in enumerate(srcs[:4])) + "</td></tr>")
    hd = ["公司", "关闭时间", "原因", "来源"] if zh else ["Firm", "Closed", "What happened", "Sources"]
    return ('<div class="tablewrap"><table class="mini sttable"><caption class="sr">' + ("已关闭的自营交易公司" if zh else "Closed prop firms") + '</caption><thead><tr>'
            + "".join(f'<th scope="col">{h}</th>' for h in hd) + f"</tr></thead><tbody>{tr}</tbody></table></div>")

def closed_hub():
    path = "/closed-prop-firms/"
    c_, bl = crumbs([("Home", "/"), ("Closed prop firms", path)])
    reg = [c for c in ST_CLOSED if c.get("regulator")]
    yrs = sorted({str(c.get("status_since") or "")[:4] for c in ST_CLOSED if c.get("status_since")})
    ans = (f"These {len(ST_CLOSED)} prop firms have shut down or stopped selling challenges" + (f" between {yrs[0]} and {yrs[-1]}" if len(yrs) > 1 else "") + ". "
           "Each row gives the date, what happened according to the sources, and links. "
           + (f"{len(reg)} involved a regulator or court ({', '.join(c['name'] for c in reg)}). " if reg else "")
           + "Closed firms are not rated and have no offers or buy links on PropAnalyse.")
    qa = [("Which prop firms have shut down?", ans),
          ("How can I tell if a prop firm is shut down?", "Signs we record: the firm's own closure or pause announcement, a regulator or court order, a Trustpilot notice that the company's website has closed, or a domain that is parked, for sale or offline with no replacement site. We check each firm's own domain on the date shown."),
          ("What happens to my account if a prop firm closes?", "It depends on the firm and any regulator involved. Where a receiver or claims process exists, the firm page links to it. Otherwise: keep receipts, account IDs and emails, ask your card issuer about a chargeback (time limits apply), and report to your local regulator or consumer agency."),
          ("How do I avoid a prop firm that might close?", "Look for a long track record, consistent payouts and clear rules. Firms with documented warning signs are on our caution list; the PA Score method is on the methodology page.")]
    cards = "".join(f'<li><a href="{url("/firms/" + c["slug"] + "/")}"><b>Is {e(c["name"])} shut down?</b><span>Closed {e(st_date(c.get("status_since")))}</span></a></li>' for c in ST_CLOSED)
    chk = ST.get("checked") or TODAY
    body = f"""<div class="wrap">{c_}<header class="ph"><h1>Closed and shut-down prop firms</h1><p class="meta"><span>{len(ST_CLOSED)} firms</span><span>Checked <time datetime="{e(chk)}">{e(st_date(chk))}</time></span><span>Re-checked every {ST_REVIEW_DAYS} days</span></p>
<p class="answer">{e(ans)}</p></header>
<section class="block">{st_closed_rows()}<p class="small">Sources are linked by number; each firm page quotes them. We report what the sources say and do not make findings of our own. Firms with live warning signs are on the <a href="{url('/caution/')}">caution list</a>. Something wrong or out of date? <a href="{url('/for-firms/')}#status-review">Ask for a review</a>.</p></section>
<section class="block"><h2>Firm pages</h2><ul class="stlinks">{cards}</ul></section>
<section class="block prose"><h2>How we mark a firm closed</h2><p>A firm is listed as closed when it has stopped operating or selling: its own announcement, a regulator or court action that stopped the business, a Trustpilot notice that the website has closed, or its domain is parked, for sale or offline with no replacement. A firm that relaunches and sells again goes back to normal review. Full rules: <a href="{url('/methodology/')}#status">methodology</a>.</p></section>
<section class="block faq"><h2>FAQ</h2>{faq_html([(q, e(a)) for q, a in qa])}</section></div>"""
    ld = [bl, faq_ld(qa), {"@context": "https://schema.org", "@type": "ItemList", "name": "Closed prop firms",
          "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": ABS + "/firms/" + c["slug"] + "/", "name": c["name"]} for i, c in enumerate(ST_CLOSED)]}]
    page(path, f"Closed Prop Firms: {len(ST_CLOSED)} Shut-Down Firms, Dates & What Happened | PropAnalyse",
         f"Which prop firms have shut down? {len(ST_CLOSED)} closed prop firms with the date, what happened and sources: " + ", ".join(c["name"] for c in ST_CLOSED[:4]) + " and more.", body, ld)

def zh_closed_hub():
    path = "/zh/closed-prop-firms/"
    c_, bl = crumbs([("首页", "/zh/"), ("已关闭的公司", path)])
    reg = [c for c in ST_CLOSED if c.get("regulator")]
    ans = (f"以下 {len(ST_CLOSED)} 家自营交易公司（prop firm）已经关闭或停止销售挑战。每一行列出关闭时间、来源所述的经过和链接。"
           + (f"其中 {len(reg)} 家涉及监管机构或法院（{'、'.join(c['name'] for c in reg)}）。" if reg else "") + "已关闭的公司在 PropAnalyse 上不评分，也没有优惠或购买链接。")
    qa = [("哪些自营交易公司已经倒闭？", ans),
          ("怎么判断一家自营交易公司是否已关闭？", "我们记录的迹象：公司自己的关闭或暂停公告、监管机构或法院的命令、Trustpilot 显示该公司网站已关闭，或域名已停放、出售或下线且没有替代网站。我们会在标注日期当天检查公司自己的域名。"),
          ("自营交易公司关闭后，我的账户怎么办？", "取决于公司和是否有监管机构介入。如有接管人或索赔程序，公司页面会附上链接。否则请保留收据、账户编号和邮件，向发卡行咨询拒付（有时限），并向当地监管机构或消费者保护机构报告。")]
    chk = ST.get("checked") or TODAY
    body = f"""<div class="wrap">{c_}<header class="ph"><h1>已关闭、倒闭的自营交易公司</h1><p class="meta"><span>{len(ST_CLOSED)} 家公司</span><span>检查日期 {e(st_date_zh(chk))}</span><span>每 {ST_REVIEW_DAYS} 天复查</span></p>
<p class="answer">{e(ans)}</p></header>
<section class="block">{st_closed_rows(True)}<p class="small">来源按编号链接，各公司页面（英文）引用原文。我们只转述来源的说法，不作自己的认定。仍在营业但有警示迹象的公司见<a href="{url('/caution/')}" hreflang="en">警示名单（英文）</a>。<a href="{url('/closed-prop-firms/')}" lang="en" hreflang="en">English version</a></p></section>
<section class="block prose"><h2>我们如何标记“已关闭”</h2><p>公司停止运营或销售时标记为已关闭：公司自己的公告、监管机构或法院令其停业的行动、Trustpilot 显示网站已关闭，或域名已停放、出售或下线且没有替代网站。重新开业并恢复销售的公司会回到正常评测。完整规则见<a href="{url('/zh/methodology/')}#status">评分方法</a>。</p></section>
<section class="block faq"><h2>常见问题</h2>{faq_html([(q, e(a)) for q, a in qa])}</section></div>"""
    page(path, f"已关闭的自营交易公司：{len(ST_CLOSED)} 家倒闭公司、时间与经过 | PropAnalyse",
         f"哪些自营交易公司已经倒闭？{len(ST_CLOSED)} 家已关闭的 prop firm，附关闭时间、经过、监管行动和来源。", body, [bl, faq_ld(qa, "zh-CN")], lang="zh")

def caution_hub():
    path = "/caution/"
    c_, bl = crumbs([("Home", "/"), ("Firms with warnings", path)])
    rows = ""
    for f in ST_CAUT:
        s = ST_CAUTION[f["slug"]]
        ev = [x for x in (s.get("evidence") or []) if x.get("url")]
        rows += (f'<tr><td class="c-firm"><div class="fcell">{logo_html(f, 32)}<a href="{url("/firms/" + f["slug"] + "/")}#status"><b>{e(f["name"])}</b><small>{e(globals().get("CAT_NAME", {}).get(f.get("category"), ""))}</small></a></div></td>'
                 f'<td class="n nowrap" data-label="Since"><time datetime="{e(s.get("status_since") or "")}">{e(st_date(s.get("status_since")))}</time></td>'
                 f'<td class="wide" data-label="Why">{e(s.get("summary") or s.get("status_reason") or "")}</td>'
                 f'<td class="n nowrap" data-label="PA Score">{rate_html(f)}<small class="stf">formula {f["_score_formula"]:.1f}</small></td>'
                 f'<td class="n nowrap" data-label="Sources">' + " ".join(st_a(x["url"], str(i + 1)) for i, x in enumerate(ev[:4])) + "</td></tr>")
    tbl = ('<div class="tablewrap"><table class="mini sttable"><caption class="sr">Prop firms with a caution</caption><thead><tr><th scope="col">Firm</th><th scope="col">Since</th><th scope="col">Why</th><th scope="col">PA Score</th><th scope="col">Sources</th></tr></thead>'
           f"<tbody>{rows}</tbody></table></div>")
    secs = "".join(f'<section class="block stfirm" id="{f["slug"]}"><h2><a href="{url("/firms/" + f["slug"] + "/")}">{e(f["name"])}</a> {st_chip()}</h2><p>{e(ST_CAUTION[f["slug"]].get("status_reason") or "")}</p>{st_evidence_list(ST_CAUTION[f["slug"]])}'
                   + (f'<p class="stresp"><b>Firm response:</b> {e(ST_CAUTION[f["slug"]]["firm_response"].get("text", ""))}</p>' if ST_CAUTION[f["slug"]].get("firm_response") else "") + "</section>" for f in ST_CAUT)
    ans = (f"{len(ST_CAUT)} of the {len(FIRMS)} prop firms we track carry a caution: {', '.join(f['name'] for f in ST_CAUT)}. "
           "They are still selling, but dated public sources show warning signs, mainly recent reviews reporting denied or unpaid payouts, in most cases on a Trustpilot profile whose rating Trustpilot has suspended. "
           f"While a caution stands, the PA Score is capped at {ST_CAP:.1f}/10 and the firm gets no offers or best-of listings.")
    trig = "".join(f"<li>{e(t)}</li>" for t in st_trig_en())
    qa = [("Which prop firms have warnings?", ans),
          ("Does a caution mean the firm is a scam?", "No. A caution means dated public sources show warning signs, which we link to. We do not call a firm a scam or fraud unless a regulator or court has said so."),
          ("How does a firm get off the caution list?", f"A caution is lifted at the first {ST_REVIEW_DAYS}-day re-check where no trigger holds. Firms can ask for an earlier review with evidence through the For prop firms page."),
          ("Should I buy a challenge from a firm with a caution?", "Read the evidence and the firm's payout rules first. If you go ahead, buy the smallest account, request a payout as soon as you are eligible, keep records, and pay with a method that has chargeback rights.")]
    chk = ST.get("checked") or TODAY
    body = f"""<div class="wrap">{c_}<header class="ph"><h1>Prop firms with warnings</h1><p class="meta"><span>{len(ST_CAUT)} firms</span><span>Checked <time datetime="{e(chk)}">{e(st_date(chk))}</time></span><span>Re-checked every {ST_REVIEW_DAYS} days</span></p>
<p class="answer">{e(ans)}</p></header>
<section class="block">{tbl}<p class="small">Sources are linked by number. These are reports from the sources, not findings by PropAnalyse. Firms that have shut down are on <a href="{url('/closed-prop-firms/')}">closed prop firms</a>.</p></section>
<section class="block prose"><h2>When a firm gets a caution</h2><ul class="bul">{trig}</ul><p>While it stands: PA Score capped at {ST_CAP:.1f} (formula score shown alongside), ranked below every active firm, no offers, promo codes or best-of listings, Visit buttons labelled \u201cVisit (caution)\u201d, and the badge shows Caution. Full rules on the <a href="{url('/methodology/')}#status">methodology</a> page; firms can <a href="{url('/for-firms/')}#status-review">request a review</a>.</p></section>
{secs}
<section class="block faq"><h2>FAQ</h2>{faq_html([(q, e(a)) for q, a in qa])}</section></div>"""
    page(path, f"Prop Firms With Warnings ({len(ST_CAUT)}): Payout Complaints, Suspended Ratings | PropAnalyse",
         f"{len(ST_CAUT)} prop firms with a caution: " + ", ".join(f["name"] for f in ST_CAUT) + ". Dated evidence: suspended Trustpilot ratings, payout-denial reports.", body,
         [bl, faq_ld(qa), {"@context": "https://schema.org", "@type": "ItemList", "name": "Prop firms with a caution", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": ABS + "/firms/" + f["slug"] + "/", "name": f["name"]} for i, f in enumerate(ST_CAUT)]}])

FOOT_EXTRA.extend([("/caution/", "Firms with warnings"), ("/closed-prop-firms/", "Closed prop firms")])
ZH_FOOT.append(("/zh/closed-prop-firms/", "已关闭的公司"))
ZH_ALT["/closed-prop-firms/"] = "/zh/closed-prop-firms/"

_st_prev_write_assets = write_assets
def write_assets():
    _st_prev_write_assets()
    shutil.copy(os.path.join(ROOT, "src", "status", "status.css"), os.path.join(OUT, "assets", "status.css"))
    p = os.path.join(OUT, "data", "firms.json"); d = json.load(open(p))
    for x in d["firms"]:
        f = BY.get(x["slug"])
        if f and st_is_caution(f): x["pa_score_formula"] = f["_score_formula"]; x["pa_score_capped_by"] = "caution"; x["discount_code"] = None
    d["status_note"] = f"status = active | caution | closed. Caution caps pa_score at {ST_CAP} (pa_score_formula = uncapped). Closed firms are listed in closed_firms and /data/status.json."
    d["closed_firms"] = [{"slug": c["slug"], "name": c["name"], "status": "closed", "status_since": c.get("status_since"), "status_reason": c.get("status_reason"),
                          "status_sources": c.get("status_sources")} for c in ST_CLOSED]
    json.dump(d, open(p, "w"), indent=1, ensure_ascii=False)
    shutil.copy(ST_FILE, os.path.join(OUT, "data", "status.json"))

_st_prev_seo = seo_files
def seo_files():
    for c in ST_CLOSED:
        if c["slug"] not in BY: closed_firm_page(c)
    closed_hub(); zh_closed_hub(); caution_hub()
    _st_prev_seo()
    p = os.path.join(OUT, "llms.txt")
    if os.path.exists(p):
        L = ["", "## Firm status (caution and closed)", f"Every firm is active, caution or closed. Caution caps the PA Score at {ST_CAP}/10 and removes offers and best-of listings; closed firms are not rated. Rules: {ABS}/methodology/#status",
             f"- [Prop firms with warnings]({ABS}/caution/): {len(ST_CAUT)} firms"]
        L += [f"- [{f['name']} (caution)]({ABS}/firms/{f['slug']}/): {ST_CAUTION[f['slug']].get('status_reason')}" for f in ST_CAUT]
        L += [f"- [Closed prop firms]({ABS}/closed-prop-firms/): {len(ST_CLOSED)} firms ([中文]({ABS}/zh/closed-prop-firms/))"]
        L += [f"- [Is {c['name']} shut down?]({ABS}/firms/{c['slug']}/): closed {st_date(c.get('status_since'))}. {c.get('status_reason')}" for c in ST_CLOSED]
        open(p, "a").write("\n".join(L) + "\n")


# /offers/ and /discounts/: caution firms are left out entirely (not even in the "no public code" list)
def st_without_caution(fn):
    def w(*a, **k):
        keep = RANKED[:]
        try:
            RANKED[:] = [f for f in keep if not st_is_caution(f)]
            return fn(*a, **k)
        finally:
            RANKED[:] = keep
    return w
for _n in ("offers", "discounts"):
    if _n in globals(): globals()[_n] = st_without_caution(globals()[_n])
