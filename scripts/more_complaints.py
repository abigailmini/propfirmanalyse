# PropAnalyse complaint register (2026-10-31): /complaints/ + /zh/complaints/ (static form -> prefilled email to complaints@ or a
# prefilled GitHub issue labelled "complaint"), a complaint block + "Report a problem" button on every firm page, a "complaint record"
# deduction documented on /methodology/ and /zh/methodology/, data/complaints.json published at /data/complaints.json, and the
# on-chain payout-ledger section on legit pages for firms whose payout claim carries a "ledger" (data/payout_claims.json).
# Exec'd LAST into build.py's namespace (after more_home.py). Globals are prefixed CP_/cp_ so they don't clobber other modules.
# With no verified + unresolved complaints the deduction is exactly zero and no score or rank changes.
CP_FILE = os.path.join(ROOT, "data", "complaints.json")
_CPD = json.load(open(CP_FILE))
COMPLAINTS = _CPD.get("complaints", [])
CP_TYPES = _CPD.get("types", {})
CP_TYPES_ZH = {"payout_denied": "拒绝出金", "payout_late": "出金延迟", "rule_changed": "购买后规则变更", "unfair_breach": "不公平的违规判定", "refund": "退款", "support": "客服问题"}
CP_STATUS = {"received": "Received", "verified": "Verified, awaiting firm", "rejected": "Rejected", "resolved": "Resolved", "unresolved": "Unresolved"}
CP_STATUS_ZH = {"received": "已收到", "verified": "已核实，等待公司回应", "rejected": "未采纳", "resolved": "已解决", "unresolved": "未解决"}
CP_TO = "complaints@propanalyse.com"
CP_GH = "https://github.com/abigailmini/propfirmanalyse/issues/new"
CP_WINDOW = 365      # days a verified + unresolved complaint keeps counting
CP_PER = 0.5         # PA Score points per counted complaint for a firm with ~0 Trustpilot reviews
CP_CAP = 2.0         # maximum deduction
CP_RESPONSE_DAYS = 7
CP_V = "1"
CP_START = "2026-10-31"
CP_DAY = datetime.date.fromisoformat(str(TODAY)[:10])

def cp_of(slug): return [c for c in COMPLAINTS if c.get("firm") == slug]
def cp_counts(slug):
    L = cp_of(slug)
    return {"received": len(L),
            "verified": sum(1 for c in L if c.get("evidence_ok") and c.get("status") in ("verified", "resolved", "unresolved")),
            "resolved": sum(1 for c in L if c.get("status") == "resolved"),
            "unresolved": sum(1 for c in L if c.get("status") == "unresolved" and c.get("evidence_ok"))}
def cp_counted(f):
    out = []
    for c in cp_of(f["slug"]):
        if c.get("status") != "unresolved" or not c.get("evidence_ok"): continue
        try: d = datetime.date.fromisoformat(str(c.get("date") or c.get("received"))[:10])
        except ValueError: continue
        if 0 <= (CP_DAY - d).days <= CP_WINDOW: out.append(c)
    return out
def cp_reviews(f): return int(num((f.get("trustpilot") or {}).get("count") or 0) or 0)
def cp_size(f): return math.sqrt(1 + cp_reviews(f) / 1000)
def cp_penalty(f):
    n = len(cp_counted(f))
    return 0.0 if n == 0 else min(CP_CAP, CP_PER * n / cp_size(f))

# apply the deduction (no-op while the register has no verified + unresolved complaints)
for _f in FIRMS:
    _f["_cp_pen"] = round(cp_penalty(_f), 2)
    if _f["_cp_pen"] > 0:
        _f["_score"] = round(max(0.0, _f["_score"] - _f["_cp_pen"]), 1)
        _f["_comp"]["complaints"] = -round(_f["_cp_pen"], 1)
if any(_f["_cp_pen"] for _f in FIRMS):
    RANKED[:] = sorted(FIRMS, key=lambda f: -f["_score"])
    for _i, _f in enumerate(RANKED): _f["_rank"] = _i + 1

def _cp_css(): return f'<link rel="stylesheet" href="{url("/assets/complaints.css")}?v={CP_V}">'
def _cp_js(): return f'<script src="{url("/assets/complaints.js")}?v={CP_V}" defer></script>'
def cp_tlabel(t, zh=False): return (CP_TYPES_ZH if zh else CP_TYPES).get(t, t)

def cp_rows(L, zh=False, firm_col=True):
    if not L: return ""
    hd = (["编号"] + (["公司"] if firm_col else []) + ["类型", "日期", "状态", "公司回应"]) if zh else (["ID"] + (["Firm"] if firm_col else []) + ["Type", "Date", "Status", "Firm response"])
    tr = ""
    for c in sorted(L, key=lambda c: str(c.get("date") or ""), reverse=True):
        f = BY.get(c.get("firm"))
        fc = (f'<td><a href="{url("/firms/" + f["slug"] + "/")}">{e(f["name"])}</a></td>' if f else f'<td>{e(c.get("firm") or "")}</td>') if firm_col else ""
        resp = e(c.get("firm_response")) if c.get("firm_response") else ('<span class="nil">未回应</span>' if zh else '<span class="nil">No response yet</span>')
        tr += (f'<tr><td class="n">{e(c.get("id") or "")}</td>{fc}<td>{e(cp_tlabel(c.get("type"), zh))}</td><td class="n">{e(c.get("date") or "")}</td>'
               f'<td>{e((CP_STATUS_ZH if zh else CP_STATUS).get(c.get("status"), c.get("status") or ""))}</td><td>{resp}</td></tr>')
    return '<div class="tablewrap"><table class="mini log"><thead><tr>' + "".join(f'<th scope="col">{h}</th>' for h in hd) + f"</tr></thead><tbody>{tr}</tbody></table></div>"

def cp_block(f):
    k = cp_counts(f["slug"]); n = e(f["name"])
    stats = "".join(f'<div class="cpstat"><b class="n">{v}</b><span>{lab}</span></div>' for lab, v in
                    [("Received", k["received"]), ("Verified", k["verified"]), ("Resolved", k["resolved"]), ("Unresolved", k["unresolved"])])
    shown = [c for c in cp_of(f["slug"]) if c.get("evidence_ok") and c.get("status") in ("verified", "resolved", "unresolved")]
    if k["verified"] == 0:
        msg = f'<p class="cpnone"><b>No verified complaints yet.</b> {"We have received " + str(k["received"]) + " complaint" + ("s" if k["received"] != 1 else "") + " still being checked." if k["received"] else "Nothing has been reported to us about " + n + " so far."}</p>'
    else:
        msg = f'<p class="cpnone">{k["verified"]} verified complaint{"s" if k["verified"] != 1 else ""}: {k["resolved"]} resolved, {k["unresolved"]} unresolved.</p>'
    pen = (f'<p class="small">{len(cp_counted(f))} verified, unresolved complaint(s) from the last 12 months deduct <b class="n">{f["_cp_pen"]:.1f}</b> from the PA Score.</p>' if f["_cp_pen"]
           else '<p class="small">Nothing counts against its PA Score from complaints right now. Only verified complaints the firm has not resolved within 7 days count, for 12 months.</p>')
    return (f'<section class="block" id="complaints"><h2>Complaints about {n}</h2>'
            f'<p class="small">Traders can report a payout, rule or refund problem with {n}. We check the evidence, give the firm {CP_RESPONSE_DAYS} days to respond, and show the result here.</p>'
            f'<div class="cpgrid">{stats}</div>{msg}{cp_rows(shown, firm_col=False)}{pen}'
            f'<p class="cpact"><a class="btn" href="{url("/complaints/")}?firm={f["slug"]}#report">Report a problem</a><a class="btn line" href="{url("/complaints/")}#process">How complaints work</a></p></section>')

# ---------------- on-chain payout ledger (legit pages) ----------------
def cp_ledger_html(f):
    c = CLAIMS.get(f["slug"]) or {}; L = c.get("ledger")
    if not L: return ""
    host = re.sub(r"^https?://(www\.)?", "", L["url"]).rstrip("/")
    rows = "".join(f'<tr><td class="n">{e(s["utc"])}</td><td class="num n">{s["amount_usdt"]:,.0f}</td><td class="n"><code>{e(s["to"][:8] + "…" + s["to"][-6:])}</code></td>'
                   f'<td><a href="{e(s["url"])}" rel="nofollow noopener" target="_blank"><code>{e(s["tx"][:12] + "…" + s["tx"][-8:])}</code></a></td><td>Success</td></tr>' for s in L.get("samples", []))
    tbl = ('<div class="tablewrap"><table class="mini"><thead><tr><th scope="col">Date (UTC)</th><th scope="col" class="num">USDT</th><th scope="col">To</th><th scope="col">Transaction (BscScan)</th><th scope="col">Status</th></tr></thead>'
           f"<tbody>{rows}</tbody></table></div>")
    intro = (f'{e(f["name"])} publishes a payout ledger at <a href="{e(L["url"])}" rel="nofollow noopener" target="_blank">{e(host)}</a>: '
             f'<b class="n">{L["total_usdt"]:,.0f}</b> {e(L["token"])} across <b class="n">{L["count"]:,}</b> payouts on {e(L["network"])}, read {nice_date(L["read"])}. '
             f'Each row links to a transaction on BscScan. We opened {len(L.get("samples", []))} of them on bscscan.com: every one settled, and the amount and time match the ledger row. '
             f'Evidence type: <span class="evt">on-chain</span>, which is stronger than a homepage figure because anyone can re-check the samples.')
    return (f'<section class="gsec" id="payout-ledger"><h2>Public payout ledger (on-chain)</h2><p>{intro}</p>{tbl}'
            f'<h3>What this does and does not prove</h3>{UL([e(x) for x in L.get("caveats", [])])}</section>')

# ---------------- page wrapper: methodology sections, ledger on legit pages ----------------
CP_METH_EN = f"""<h2 id="complaints">Complaint record (deduction)</h2><p>Traders can report problems on our <a href="{url('/complaints/')}">complaints page</a>. A complaint only affects the score when all of these are true:</p>
<ul><li>We have <b>verified the evidence</b> (it is the trader's own account, the dates line up, and the rules in force that day support the complaint).</li>
<li>The firm had <b>{CP_RESPONSE_DAYS} days to respond</b> and did not resolve it (status "unresolved"). Resolved complaints stop counting the day they are resolved; rejected ones never count.</li>
<li>The problem happened in the <b>last 12 months</b>.</li></ul>
<p>Deduction = 0.5 × <i>N</i> ÷ √(1 + <i>R</i> ÷ 1,000) PA Score points, capped at 2.0, where <i>N</i> is the number of counted complaints and <i>R</i> is the firm's Trustpilot review count, our proxy for company size. One unresolved complaint costs a firm with almost no reviews about 0.5 points and a firm with 30,000 reviews about 0.09. The deduction is applied after the weighted total above.</p>
<p>The register started on {nice_date(CP_START)}. It has <b class="n">{len(COMPLAINTS)}</b> complaints so far, so the deduction is currently zero for every firm and no score has changed. We never invent or seed complaints. The register is public at <a href="{url('/data/complaints.json')}">/data/complaints.json</a> (no emails or account IDs).</p>
"""
CP_METH_ZH = f"""<h2 id="complaints">投诉记录（扣分项）</h2><p>交易者可以在<a href="{url('/zh/complaints/')}">投诉页面</a>提交问题。只有同时满足以下条件，投诉才会影响评分：</p>
<ul><li>我们已<b>核实证据</b>（确为本人账户、日期吻合、当天生效的规则支持该投诉）。</li><li>公司有 <b>{CP_RESPONSE_DAYS} 天时间回应</b>但未解决（状态为“未解决”）。已解决的投诉从解决当天起不再计入；未采纳的投诉从不计入。</li><li>问题发生在<b>最近 12 个月</b>内。</li></ul>
<p>扣分 = 0.5 × <i>N</i> ÷ √(1 + <i>R</i> ÷ 1,000)，最多扣 2.0 分。<i>N</i> 为计入的投诉数，<i>R</i> 为该公司的 Trustpilot 评价数（作为公司规模的近似值）。在上面的加权总分算出后再扣除。</p>
<p>投诉登记从 {CP_START} 开始，目前共有 <b class="n">{len(COMPLAINTS)}</b> 条投诉，因此所有公司的扣分均为零，没有任何评分发生变化。我们绝不编造或预置投诉。登记数据公开在 <a href="{url('/data/complaints.json')}">/data/complaints.json</a>（不含邮箱或账户编号）。</p>
"""
_cp_prev_page = page
def page(path, title, desc, body, jsonld=None, og_type="website", extra_head="", lang="en"):
    if path == "/methodology/" and 'id="complaints"' not in body:
        a = "<h2>What the score is not</h2>"
        body = body.replace(a, CP_METH_EN + a, 1) if a in body else body.replace("</article>", CP_METH_EN + "</article>", 1)
    elif path == "/zh/methodology/" and 'id="complaints"' not in body:
        a = "<h2>评分不代表什么</h2>"
        body = body.replace(a, CP_METH_ZH + a, 1) if a in body else body.replace("</article>", CP_METH_ZH + "</article>", 1)
    m = re.fullmatch(r"/firms/([^/]+)/legit/", path)
    if m and m.group(1) in BY and 'id="payout-ledger"' not in body:
        blk = cp_ledger_html(BY[m.group(1)])
        a = '<section class="gsec"><h2>Reasons for confidence</h2>'
        if blk and a in body:
            body = body.replace(a, blk + a, 1); extra_head = (extra_head or "") + _cp_css()
    return _cp_prev_page(path, title, desc, body, jsonld, og_type, extra_head, lang)

_cp_prev_firm_page = firm_page
def firm_page(f):
    _cp_prev_firm_page(f)
    path = f"/firms/{f['slug']}/"
    _patch_page(path, before='<section class="block" id="history">', html=cp_block(f))
    _patch_page(path, before="</aside>", html=f'<p class="cpaside"><a class="btn line sm" href="{url("/complaints/")}?firm={f["slug"]}#report">Report a problem</a></p>')
    _patch_page(path, before="</head>", html=_cp_css())

# ---------------- /complaints/ + /zh/complaints/ ----------------
CP_EN = dict(
    h1="Report a problem with a prop firm",
    lede="Payout denied, paid late, rules changed after you bought, a breach you think is wrong, a refund or support that went nowhere: tell us, with evidence. We check it, give the firm 7 days to answer, and publish the outcome on the firm's page.",
    steps=[("Received", "You send the complaint by email or as a GitHub issue. We log it with a reference ID. A received complaint is not public and does not affect any score."),
           ("We verify the evidence", "We check that it is your account, that the dates line up, and what the firm's rules said on that day (our rule-change log helps). Complaints we cannot support are rejected and never count."),
           ("The firm gets 7 days", "We send the firm the facts and your account or order ID (never your email unless you agree). Its response is shown next to the complaint on its page."),
           ("Outcome", "If the firm fixes it and you confirm, the complaint is resolved and stops counting. If not, it is unresolved: verified, unresolved complaints from the last 12 months count against the firm's PA Score.")],
    form_h="Send a complaint", firm="Firm", other="Another firm (name it in the description)", email="Your email (kept private)", acct="Account or order ID", type="Issue type", date="Date of the problem",
    desc="What happened", desc_ph="What you expected, what the firm did, what you have already tried", ev="Evidence links", ev_ph="Screenshots (any image host), support emails, payout request IDs, tx hashes. One per line.",
    ok="This is my own account and the facts are true to the best of my knowledge.", mail="Send by email", gh="Open a public GitHub issue",
    form_note="Nothing is stored on this site: the buttons only prepare a message in your email app or on GitHub. GitHub issues are public, so the issue version leaves out your email and account ID: send those to " + CP_TO + " with the issue number.",
    req="Required", pick="Choose…")
CP_ZH = dict(
    h1="投诉自营交易公司",
    lede="被拒绝出金、出金延迟、购买后规则被修改、你认为不公平的违规判定、退款或客服无果：请附上证据告诉我们。我们会核实，给公司 7 天回应，并在该公司页面公布结果。",
    steps=[("已收到", "你通过邮件或 GitHub issue 提交投诉，我们记录并给出编号。已收到的投诉不公开，也不影响任何评分。"),
           ("核实证据", "我们核对是否为你本人的账户、日期是否吻合，以及当天公司规则的原文（可参考我们的规则变更记录）。无法证实的投诉不予采纳，从不计分。"),
           ("公司有 7 天回应", "我们把事实和你的账户或订单编号发给公司（未经你同意绝不提供你的邮箱）。公司的回应会显示在其页面的投诉旁边。"),
           ("结果", "公司解决且你确认后，投诉标记为已解决，不再计分。否则标记为未解决：最近 12 个月内已核实且未解决的投诉会扣减该公司的 PA 评分。")],
    form_h="提交投诉", firm="公司", other="其他公司（请在描述中写明名称）", email="你的邮箱（不公开）", acct="账户或订单编号", type="问题类型", date="问题发生日期",
    desc="发生了什么", desc_ph="你预期的结果、公司的做法、你已经尝试过什么", ev="证据链接", ev_ph="截图（任意图床）、客服邮件、出金申请编号、交易哈希。每行一个。",
    ok="这是我本人的账户，以上内容据我所知真实无误。", mail="通过邮件发送", gh="提交公开的 GitHub issue",
    form_note="本网站不保存任何内容：按钮只会在你的邮件程序或 GitHub 中生成消息。GitHub issue 是公开的，因此 issue 版本不包含你的邮箱和账户编号，请把它们连同 issue 编号发送到 " + CP_TO + "。",
    req="必填", pick="请选择…")

def cp_form(zh=False):
    T = CP_ZH if zh else CP_EN; r = f'<span class="req" aria-hidden="true">*</span>'
    firms = "".join(f'<option value="{e(f["slug"])}" data-en="{e(f["name"])}">{e(f["name"])}</option>' for f in sorted(FIRMS, key=lambda x: x["name"].lower()))
    types = "".join(f'<option value="{k}" data-en="{e(v)}">{e(cp_tlabel(k, zh))}</option>' for k, v in CP_TYPES.items())
    return f"""<form class="cform cpform" id="cpform" onsubmit="return false" novalidate data-to="{CP_TO}" data-gh="{CP_GH}" data-lang="{"zh" if zh else "en"}">
<label class="fl" for="cp-firm"><span>{T["firm"]} {r}</span><select id="cp-firm" required><option value="" data-en="">{T["pick"]}</option>{firms}<option value="other" data-en="Other firm">{T["other"]}</option></select></label>
<label class="fl" for="cp-type"><span>{T["type"]} {r}</span><select id="cp-type" required><option value="" data-en="">{T["pick"]}</option>{types}</select></label>
<label class="fl" for="cp-email"><span>{T["email"]} {r}</span><input id="cp-email" type="email" autocomplete="email" inputmode="email" required placeholder="you@example.com"></label>
<label class="fl" for="cp-acct"><span>{T["acct"]}</span><input id="cp-acct" autocomplete="off" placeholder="e.g. 123456 / ORD-7781"></label>
<label class="fl" for="cp-date"><span>{T["date"]}</span><input id="cp-date" type="date" max="{CP_DAY.isoformat()}"></label>
<label class="fl wide" for="cp-desc"><span>{T["desc"]} {r}</span><textarea id="cp-desc" rows="5" required placeholder="{T["desc_ph"]}"></textarea></label>
<label class="fl wide" for="cp-ev"><span>{T["ev"]}</span><textarea id="cp-ev" rows="3" placeholder="{T["ev_ph"]}"></textarea></label>
<label class="chk wide" for="cp-ok"><input id="cp-ok" type="checkbox" required> <span>{T["ok"]}</span></label>
<p class="cpmsg wide" id="cp-msg" role="alert" hidden></p>
<div class="ffact wide cpact"><a class="btn" id="cp-mail" href="mailto:{CP_TO}">{T["mail"]}</a><a class="btn line" id="cp-gh" href="{CP_GH}?labels=complaint" rel="noopener" target="_blank">{T["gh"]}</a></div>
</form><p class="small">{e(T["form_note"])}</p>"""

def cp_register(zh=False):
    L = [c for c in COMPLAINTS if c.get("status") != "rejected" and c.get("status") != "received"]
    tot = {k: sum(cp_counts(f["slug"])[k] for f in FIRMS) for k in ("received", "verified", "resolved", "unresolved")}
    labs = [("已收到", "received"), ("已核实", "verified"), ("已解决", "resolved"), ("未解决", "unresolved")] if zh else [("Received", "received"), ("Verified", "verified"), ("Resolved", "resolved"), ("Unresolved", "unresolved")]
    stats = "".join(f'<div class="cpstat"><b class="n">{tot[k]}</b><span>{lab}</span></div>' for lab, k in labs)
    if not L:
        empty = (f'<p class="cpnone"><b>登记表目前为空。</b>自 {CP_START} 开始登记以来，还没有经过核实的投诉。我们不会编造或预置任何投诉。</p>' if zh else
                 f'<p class="cpnone"><b>The register is empty.</b> No complaint has been verified since the register opened on {nice_date(CP_START)}. We do not invent or seed complaints, so every entry here will be a real one.</p>')
        return f'<div class="cpgrid">{stats}</div>{empty}'
    per = [f for f in RANKED if cp_counts(f["slug"])["received"]]
    pt = "".join(f'<tr><td><a href="{url("/firms/" + f["slug"] + "/#complaints")}">{e(f["name"])}</a></td>' + "".join(f'<td class="num n">{cp_counts(f["slug"])[k]}</td>' for _, k in labs) + "</tr>" for f in per)
    ph = "".join(f'<th scope="col" class="num">{lab}</th>' for lab, _ in labs)
    return (f'<div class="cpgrid">{stats}</div><div class="tablewrap"><table class="mini"><thead><tr><th scope="col">{"公司" if zh else "Firm"}</th>{ph}</tr></thead><tbody>{pt}</tbody></table></div>' + cp_rows(L, zh))

def complaints_page():
    T = CP_EN
    c, bl = crumbs([("Home", "/"), ("Report a problem", "/complaints/")])
    steps = "".join(f"<li><b>{e(h)}</b>{e(t)}</li>" for h, t in T["steps"])
    qa = [("Is my email published?", f"No. Your email only goes to {CP_TO} if you use the email button. The GitHub issue option is public, so it leaves out your email and account ID."),
          ("What counts against a firm's score?", f"Only complaints we have verified that the firm did not resolve within {CP_RESPONSE_DAYS} days, from the last 12 months. The deduction is scaled by company size (Trustpilot review count) and capped at 2 points. Details on the methodology page."),
          ("Can a firm pay to remove a complaint?", "No. A complaint stops counting only when it is resolved and the trader confirms it, or when it is older than 12 months. Affiliate deals and badges have no effect."),
          ("Can the firm reply?", f"Yes. We send the firm every verified complaint and give it {CP_RESPONSE_DAYS} days. Firms can also write to {CP_TO} with the reference ID; the response is shown next to the complaint."),
          ("What evidence helps?", "Screenshots of the denial or the breach notice, the support emails, the payout request ID, the date you bought the account, and transaction hashes for crypto payouts. A link to the rule as it read when you bought is the strongest evidence."),
          ("What if the complaint is about FundedXyz?", "FundedXyz is run by the team behind PropAnalyse. Complaints about it go through exactly the same process and are published the same way.")]
    body = f"""<div class="wrap">{c}<header class="ph"><h1>{T["h1"]}</h1><p class="lede">{e(T["lede"])}</p>
<p class="ctas"><a class="btn" href="#report">Report a problem</a><a class="btn line" href="#process">How it works</a><a class="btn line" href="#register">Public register</a></p></header>
<section class="block" id="process"><h2>How a complaint is handled</h2><ol class="cpsteps">{steps}</ol>
<p class="small">Statuses you will see: received, verified (waiting for the firm), resolved, unresolved, rejected. A firm page shows how many complaints were received, verified, resolved and unresolved.</p></section>
<section class="block" id="report"><h2>{T["form_h"]}</h2><p class="small">Fields marked * are required. Write in English or Chinese. One complaint per problem; if a firm has wronged you twice, send two.</p>{cp_form()}</section>
<section class="block" id="register"><h2>Public complaint register</h2><p class="small">Verified complaints by firm, with status and the firm's response. Rejected and not-yet-checked complaints are counted but not described. Data: <a href="{url('/data/complaints.json')}">/data/complaints.json</a>.</p>{cp_register()}</section>
<section class="block prose" id="score"><h2>How complaints affect the PA Score</h2><p>A verified complaint the firm leaves unresolved for {CP_RESPONSE_DAYS} days deducts points from its PA Score for 12 months: 0.5 × complaints ÷ √(1 + Trustpilot reviews ÷ 1,000), capped at 2 points, so a large firm is not punished for its size and a small firm cannot hide behind few reviews. Resolved complaints stop counting. While the register is empty, no score changes. Full rules: <a href="{url('/methodology/')}#complaints">methodology</a>.</p></section>
<section class="block prose"><h2>What we do not accept</h2><ul class="bul"><li>Complaints without your own account behind them, or about accounts you bought second-hand.</li><li>Breaches that the rules in force on that day clearly describe (we will tell you which rule).</li><li>Threats, personal data about firm staff, or anything we cannot check.</li></ul><p>Firms: to answer a complaint or flag one as false, write to <a href="mailto:{CP_TO}">{CP_TO}</a> with the reference ID. Data corrections go through <a href="{url('/for-firms/')}">for prop firms</a>.</p></section>
<section class="block faq"><h2>FAQ</h2>{faq_html([(q, e(a)) for q, a in qa])}</section></div>{_cp_js()}"""
    page("/complaints/", "Report a Prop Firm Problem: Payout Denied, Rule Changes, Refunds | PropAnalyse",
         "Complain about a prop firm with evidence: denied or late payouts, rule changes after purchase, unfair breaches, refunds. Verified, firm gets 7 days to respond, results public.",
         body, [bl, faq_ld(qa)], extra_head=_cp_css())

def zh_complaints_page():
    T = CP_ZH
    c, bl = crumbs([("首页", "/zh/"), ("投诉", "/zh/complaints/")])
    steps = "".join(f"<li><b>{e(h)}</b>{e(t)}</li>" for h, t in T["steps"])
    qa = [("我的邮箱会公开吗？", f"不会。只有使用邮件按钮时，你的邮箱才会发送到 {CP_TO}。GitHub issue 是公开的，因此不包含你的邮箱和账户编号。"),
          ("什么投诉会扣减公司评分？", f"只有我们核实过、公司在 {CP_RESPONSE_DAYS} 天内未解决、且发生在最近 12 个月内的投诉。扣分按公司规模（Trustpilot 评价数）调整，最多扣 2 分。详见评分方法。"),
          ("公司能付钱删除投诉吗？", "不能。投诉只有在已解决并经交易者确认、或超过 12 个月后才不再计分。联盟推广和徽章都没有影响。"),
          ("公司可以回应吗？", f"可以。每条核实过的投诉我们都会发给公司，并给 {CP_RESPONSE_DAYS} 天时间。公司也可以附上编号写信到 {CP_TO}，回应会显示在投诉旁边。"),
          ("投诉 FundedXyz 怎么办？", "FundedXyz 由 PropAnalyse 背后的团队运营。针对它的投诉走完全相同的流程，以同样方式公布。")]
    body = f"""<div class="wrap">{c}<header class="ph"><h1>{T["h1"]}</h1><p class="lede">{e(T["lede"])}</p>
<p class="ctas"><a class="btn" href="#report">提交投诉</a><a class="btn line" href="#process">处理流程</a><a class="btn line" href="#register">公开登记</a></p></header>
<section class="block" id="process"><h2>投诉如何处理</h2><ol class="cpsteps">{steps}</ol><p class="small">你会看到的状态：已收到、已核实（等待公司回应）、已解决、未解决、未采纳。每家公司页面都会显示投诉的收到、核实、解决和未解决数量。</p></section>
<section class="block" id="report"><h2>{T["form_h"]}</h2><p class="small">带 * 的为必填项。可用中文或英文填写。一个问题一条投诉。</p>{cp_form(True)}</section>
<section class="block" id="register"><h2>公开投诉登记</h2><p class="small">按公司列出已核实的投诉、状态和公司回应。未采纳和尚未核实的投诉只计数，不展示内容。数据：<a href="{url('/data/complaints.json')}">/data/complaints.json</a>。</p>{cp_register(True)}</section>
<section class="block prose" id="score"><h2>投诉如何影响 PA 评分</h2><p>已核实、且公司 {CP_RESPONSE_DAYS} 天内未解决的投诉，会在 12 个月内扣减该公司的 PA 评分：0.5 × 投诉数 ÷ √(1 + Trustpilot 评价数 ÷ 1,000)，最多扣 2 分。这样大公司不会因规模大而吃亏，小公司也无法因评价少而躲避。已解决的投诉不再计分。登记表为空时，评分不变。完整规则见<a href="{url('/zh/methodology/')}#complaints">评分方法</a>。</p></section>
<section class="block prose"><h2>我们不受理的投诉</h2><ul class="bul"><li>不是你本人账户的投诉，或二手购买的账户。</li><li>当天生效的规则明确写明的违规（我们会告诉你是哪条规则）。</li><li>威胁、公司员工的个人信息，或任何无法核实的内容。</li></ul><p>公司如需回应或指出不实投诉，请附编号写信到 <a href="mailto:{CP_TO}">{CP_TO}</a>。<a href="{url('/complaints/')}" lang="en" hreflang="en">English version</a></p></section>
<section class="block faq"><h2>常见问题</h2>{faq_html([(q, e(a)) for q, a in qa])}</section></div>{_cp_js()}"""
    page("/zh/complaints/", "投诉自营交易公司：拒绝出金、规则变更、退款 | PropAnalyse",
         "附证据投诉自营交易公司：拒绝或延迟出金、购买后规则变更、不公平违规判定、退款。我们核实后给公司 7 天回应，结果公开。",
         body, [bl, faq_ld(qa, "zh-CN")], extra_head=_cp_css(), lang="zh")

FOOT_EXTRA.append(("/complaints/", "Report a problem"))
ZH_FOOT.append(("/zh/complaints/", "投诉"))
ZH_ALT["/complaints/"] = "/zh/complaints/"

_cp_prev_seo = seo_files
def seo_files():
    os.makedirs(os.path.join(OUT, "assets"), exist_ok=True); os.makedirs(os.path.join(OUT, "data"), exist_ok=True)
    for n in ("complaints.js", "complaints.css"): shutil.copy(os.path.join(ROOT, "src", "complaints", n), os.path.join(OUT, "assets", n))
    shutil.copy(CP_FILE, os.path.join(OUT, "data", "complaints.json"))
    complaints_page(); zh_complaints_page()
    _cp_prev_seo()
    p = os.path.join(OUT, "llms.txt")
    if os.path.exists(p):
        open(p, "a").write(f"\n## Complaints\n- [Report a problem]({ABS}/complaints/): trader complaints with evidence (payout denied/late, rule changed after purchase, unfair breach, refund, support); verified, firm gets {CP_RESPONSE_DAYS} days, outcome on the firm page\n"
                           f"- [Complaint register (JSON)]({ABS}/data/complaints.json): {len(COMPLAINTS)} complaints so far; only verified + unresolved complaints from the last 12 months affect the PA Score (see methodology)\n")
