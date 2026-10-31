# ---------------- 2026-10-31 audit quick wins (docs/audit-2026-10-31.md) ----------------
# exec'd after more_status.py, before more_track.py. Prefix QW_/qw_.

# 1. Eligibility notes (e.g. Apex footer "intended for U.S. users only") override the country list.
_qw_prev_country_status = country_status
def country_status(f, aliases):
    if f.get("us_only") and "united states" not in aliases and "usa" not in aliases:
        return "partial", "Site footer: services intended for U.S. users only"
    return _qw_prev_country_status(f, aliases)

def qw_elig_html(f):
    if not f.get("eligibility_note"): return ""
    src = f'<a href="{e(f["eligibility_source"])}" rel="nofollow noopener" target="_blank">source</a>' if f.get("eligibility_source") else ""
    return f'<p class="note qwelig"><b>Eligibility.</b> {e(f["eligibility_note"])} {src}</p>'

_qw_prev_page = page
def page(path, title, desc, body, jsonld=None, og_type="website", extra_head="", lang="en"):
    m = re.fullmatch(r"/firms/([^/]+)/", path)
    f = BY.get(m.group(1)) if m else None
    if f and f.get("eligibility_note") and "qwelig" not in body:
        body = body.replace('<div class="pgrid">', qw_elig_html(f) + '<div class="pgrid">', 1)
    return _qw_prev_page(path, title, desc, body, jsonld, og_type, extra_head, lang)


# 2. Trust pages: /about/ (expanded), /disclosure/, /terms/, /contact/, /corrections/ (+ footer links, FundedXyz disclosure links)
QW_UPDATED = "2026-10-31"
QW_REPO = "https://github.com/abigailmini/propfirmanalyse"
QW_ISSUES = QW_REPO + "/issues/new"
def qw_nsrc(): return sum(len(as_list(f.get("source_urls")) + as_list(f["_x"].get("sources")) + as_list(f["_c"].get("sources"))) for f in FIRMS)
def qw_upd(): return f'<p class="small">Last updated <time datetime="{QW_UPDATED}">{nice_date(QW_UPDATED)}</time>.</p>'
def qw_toc(items): return '<nav class="qwtoc" aria-label="On this page"><ul class="bul">' + "".join(f'<li><a href="#{a}">{e(t)}</a></li>' for a, t in items) + "</ul></nav>"
def qw_fx():
    fx = BY.get("fundedxyz")
    return (fx, f'#{fx["_rank"]} of {len(FIRMS)}', f'{fx["_score"]:.1f}') if fx else (None, "", "")
QW_CSS = "<style>.qwtoc{margin:1rem 0 1.5rem}.qwtoc ul{columns:2;column-gap:2rem}@media(max-width:600px){.qwtoc ul{columns:1}}.qwkv{display:grid;grid-template-columns:max-content 1fr;gap:.35rem 1.25rem;margin:1rem 0}.qwkv dt{font-weight:600}.qwkv dd{margin:0}.qwbig{border:1px solid currentColor;border-radius:6px;padding:1rem 1.15rem;margin:1rem 0}.qwbig h2{margin-top:0}</style>"

def about():
    c, bl = crumbs([("Home", "/"), ("About", "/about/")])
    fx, fxr, fxs = qw_fx(); nclosed = len(globals().get("ST_CLOSED", [])); ncaut = len(globals().get("ST_CAUTION", {}))
    body = f"""<div class="wrap">{c}<article class="prose"><h1>About PropAnalyse</h1>
<p class="lede">PropAnalyse is an independent, data-first guide to prop trading firms. We read each firm's own pricing, rules and payout pages, record every figure with the date and the source link, and put the firms side by side so a trader can see what a challenge really costs and what it takes to get paid.</p>
{qw_toc([("who", "Who we are"), ("what", "What we cover"), ("how", "How we work"), ("editorial", "Editorial policy"), ("independence", "Independence rules"), ("money", "How we make money"), ("ownership", "Ownership"), ("contact", "Contact and corrections")])}
<h2 id="who">Who we are</h2><p>PropAnalyse is a small research team of traders and builders. We publish as a brand rather than as named reviewers: what you should judge us on is the evidence, so every number on the site links to the page it came from, the scoring formula is public, and the full edit history of the site and dataset is public on <a href="{QW_REPO}" rel="noopener">GitHub</a>. We started in October 2026 because the existing comparison sites were forex-first, rarely dated their figures, and did not track when a firm quietly changed its rules.</p>
<h2 id="what">What we cover</h2><p>Today: <b class="n">{len(FIRMS)}</b> rated firms across crypto, CFD/forex and futures, <b class="n">{ncaut}</b> of them listed with a <a href="{url('/caution/')}">caution</a>, plus <b class="n">{nclosed}</b> <a href="{url('/closed-prop-firms/')}">firms that have shut down</a>. The data rests on <b class="n">{qw_nsrc()}</b> cited source pages. We cover crypto prop firms first and in the most depth, and we publish in English and Chinese.</p>
<h2 id="how">How we work</h2><ul class="bul">
<li><b>Primary sources only.</b> Fees, targets, drawdown, split, payout cycle, platforms and restrictions come from the firm's own site or help centre. Ratings come from the firm's public Trustpilot page. Nothing is copied from other comparison sites.</li>
<li><b>Unknown stays unknown.</b> If a firm does not publish a figure we show "Not published"; we never estimate.</li>
<li><b>Dated.</b> Each firm page shows when it was last verified and when a re-check is due. Our target is a full re-check of every firm at least every 30 days (see the <a href="{url('/updates/')}">verification log</a>).</li>
<li><b>Change log.</b> Every changed field is logged with the old value, the new value and the date, in the <a href="{url('/news/')}">rule-change log</a> (RSS and JSON too).</li>
<li><b>One formula.</b> The <a href="{url('/methodology/')}">PA Score</a> is calculated by a script, the same way for every firm. Nobody edits a score by hand.</li></ul>
<h2 id="editorial">Editorial policy</h2><ul class="bul">
<li>We report what firms publish and what independent sources show; we attribute claims and link them. We do not call a firm a scam or fraud unless a regulator or court has said so.</li>
<li>Caution and closed statuses follow a published rule with dated evidence, and are re-checked at least every 30 days. Firms can ask for a review with evidence.</li>
<li>Complaints count against a score only after we verify them and the firm has had 7 days to respond (<a href="{url('/complaints/')}">how complaints work</a>).</li>
<li>Promo codes are the firms' own public codes, checked on their sites. Expired codes are removed automatically on their end date.</li>
<li>Mistakes are corrected in the open: see our <a href="{url('/corrections/')}">corrections policy</a>.</li></ul>
<h2 id="independence">Independence rules</h2><ul class="bul">
<li>No firm can pay to change its data, score, rank, status or the order of any list.</li>
<li>Affiliate status is never an input to the score, and firms without an affiliate deal are listed and ranked exactly like firms with one.</li>
<li>We do not accept paid reviews, sponsored rankings or "featured" placements.</li>
<li>Firms do not see their score before it is published. They can send corrections with a link to their own page, like anyone else.</li>
<li>Our own firm, FundedXyz, gets no exceptions (below).</li></ul>
<h2 id="money">How we make money</h2><p>Some "Visit" links may become affiliate links: if you buy a challenge after clicking, the firm may pay us a commission at no extra cost to you. Where a link is an affiliate link it is marked <code>rel="sponsored"</code>. We do not sell data, ads or placements. Full details: <a href="{url('/disclosure/')}">disclosure</a>.</p>
<h2 id="ownership">Ownership</h2><div class="qwbig"><p><b>PropAnalyse is operated by the team behind <a href="{url('/firms/fundedxyz/')}">FundedXyz</a>, a crypto prop firm.</b> That is a conflict of interest and we treat it as one: FundedXyz is collected with the same checklist, scored by the same formula and ranked by the same rule as every other firm.{(" Right now it ranks " + fxr + " with a PA Score of " + fxs + ".") if fx else ""} Safeguards and the audit trail are on the <a href="{url('/disclosure/')}">disclosure page</a>.</p></div>
<h2 id="contact">Contact and corrections</h2><p>Spotted an outdated figure? Send the firm's own page that shows the change and we will re-verify. Routes are on the <a href="{url('/contact/')}">contact page</a>; how we handle fixes is in the <a href="{url('/corrections/')}">corrections policy</a>. Legal: <a href="{url('/terms/')}">terms of use</a>, <a href="{url('/privacy/')}">privacy</a>.</p>
{qw_upd()}</article></div>"""
    ld = {"@context": "https://schema.org", "@type": "AboutPage", "name": "About PropAnalyse", "url": ABS + "/about/",
          "publisher": {"@type": "Organization", "name": "PropAnalyse", "url": ABS + "/", "logo": ABS + "/assets/logo.png", "foundingDate": "2026-10",
                        "publishingPrinciples": ABS + "/about/#editorial", "correctionsPolicy": ABS + "/corrections/", "ownershipFundingInfo": ABS + "/disclosure/",
                        "sameAs": [QW_REPO]}}
    page("/about/", "About PropAnalyse: Editorial Policy & Ownership", f"Who runs PropAnalyse, how we verify {len(FIRMS)} prop firms, editorial and independence rules, how we make money, and our FundedXyz ownership disclosure.", body, [bl, ld], extra_head=QW_CSS)

def disclosure():
    c, bl = crumbs([("Home", "/"), ("Disclosure", "/disclosure/")])
    fx, fxr, fxs = qw_fx()
    body = f"""<div class="wrap">{c}<article class="prose"><h1>Disclosure: ownership and affiliate links</h1>
<div class="qwbig"><h2>In one paragraph</h2><p><b>PropAnalyse is operated by the team behind FundedXyz, a crypto prop firm that we also review.</b> Some links to prop firms may be affiliate links that pay us a commission if you buy. Neither fact changes any firm's data, score, rank or status. FundedXyz is measured with the same checklist and formula as everyone else{(", and currently ranks " + fxr + " (PA Score " + fxs + ")") if fx else ""}.</p></div>
<h2 id="fundedxyz">The FundedXyz conflict</h2><p>We run a site that ranks prop firms, and the same team runs one of those firms. Readers should know that before trusting a ranking, so we say it on every FundedXyz page, in the site footer, on the About page and here. The safeguards:</p><ul class="bul">
<li><b>Same inputs.</b> FundedXyz's figures are read from fundedxyz.com on the same checklist, with the same "Not published" rule for anything it does not publish.</li>
<li><b>Same formula.</b> The PA Score is computed by a script; there is no manual adjustment for any firm. The code is public.</li>
<li><b>No default advantage.</b> FundedXyz has no pinned position, no "editor's pick" label and no special placement in tables, offers or best-of lists. It appears where its score puts it.</li>
<li><b>Comparison pages are generated</b> from the dataset with the same template for every pair, including pairs where FundedXyz loses.</li>
<li><b>Audit trail.</b> Every change to data, scores and page templates is in the public <a href="{QW_REPO}" rel="noopener">git history</a>, and every changed field is logged with old and new values in the <a href="{url('/news/')}">rule-change log</a>.</li></ul>
<p>If you think FundedXyz is treated more kindly than another firm on any page, tell us (see <a href="{url('/contact/')}">contact</a>) and we will publish the fix in the <a href="{url('/corrections/')}">corrections log</a>.</p>
<h2 id="affiliate">Affiliate links</h2><p>Some "Visit" and offer links may be affiliate links. If you buy after clicking, the firm may pay us a commission. It costs you nothing extra and never changes the price you see. Affiliate links are marked <code>rel="sponsored"</code>. Firms without an affiliate deal are listed, scored and ranked exactly like firms with one, and an affiliate deal is never an input to the score.</p>
<h2 id="codes">Promo codes</h2><p>The codes we show are the firms' own public codes, read from their websites on the date shown. We do not currently have exclusive codes. If we ever add one, it will be labelled as ours. Codes are hidden automatically after their published end date.</p>
<h2 id="no">What we never do</h2><ul class="bul"><li>Sell scores, ranks, reviews, "featured" spots or the removal of accurate information.</li><li>Let a firm see or approve its score before publication.</li><li>Publish a firm's data that we could not trace to a source.</li></ul>
<p>Related: <a href="{url('/about/')}">about and editorial policy</a>, <a href="{url('/methodology/')}">methodology</a>, <a href="{url('/terms/')}">terms</a>, <a href="{url('/privacy/')}">privacy</a>.</p>{qw_upd()}</article></div>"""
    page("/disclosure/", "Disclosure: FundedXyz Ownership & Affiliate Links", "PropAnalyse is operated by the team behind FundedXyz. How we keep rankings independent, how affiliate links work, and what we never do.", body, [bl], extra_head=QW_CSS)

def terms():
    c, bl = crumbs([("Home", "/"), ("Terms of use", "/terms/")])
    body = f"""<div class="wrap">{c}<article class="prose"><h1>Terms of use</h1>
<p class="lede">Plain-English terms for using propanalyse.com. By using the site you agree to them.</p>
<h2>1. Information, not advice</h2><p>PropAnalyse publishes information about prop trading firms for general education. Nothing on the site is financial, investment, legal or tax advice, or a recommendation to buy any product. Prop-firm evaluations are paid products and most traders do not pass. Decide for yourself, and read the firm's own terms before you pay.</p>
<h2>2. Accuracy</h2><p>We take figures from each firm's own website on the date shown, but firms change prices and rules without notice and we can make mistakes. The firm's own site and contract always win. We do not guarantee that any figure, score, status or promo code is current or complete. Report errors through our <a href="{url('/corrections/')}">corrections process</a>.</p>
<h2>3. Scores and statuses are opinions based on data</h2><p>The PA Score, caution and closed statuses and evidence levels are our assessments, produced by the published <a href="{url('/methodology/')}">methodology</a> from cited sources. They are not a prediction of whether you will pass or be paid, and not a finding of wrongdoing.</p>
<h2>4. Third-party sites and links</h2><p>Links to firms and other sites are provided for convenience; we do not control those sites and are not responsible for their content, products, payouts or conduct. Some links may be affiliate links (see <a href="{url('/disclosure/')}">disclosure</a>). Any purchase is between you and the firm.</p>
<h2>5. Using our content and data</h2><p>You may quote individual figures and scores, and use the open dataset at <a href="{url('/data/firms.json')}">/data/firms.json</a>, if you credit "PropAnalyse" with a link to the relevant page. Do not copy pages wholesale, present our reviews as your own, or imply that PropAnalyse endorses you. The <a href="{url('/badge/')}">score badge</a> may be embedded by the firm it describes, unmodified and linking back to that firm's page. Firm names and logos belong to their owners and are used only to identify them.</p>
<h2>6. Complaints and submissions</h2><p>If you send a complaint, correction or listing request, you confirm it is true to the best of your knowledge and that you have the right to share it. We may edit or decline submissions, and publish verified complaints without your e-mail or account ID, as described on the <a href="{url('/complaints/')}">complaints page</a>.</p>
<h2>7. Acceptable use</h2><p>Do not attack, overload or scrape the site in a way that degrades it, or use it for anything unlawful. Reasonable automated access to the open data files and RSS feeds is welcome.</p>
<h2>8. Liability</h2><p>To the fullest extent allowed by law, PropAnalyse is not liable for losses arising from use of the site, including fees paid to a firm, failed evaluations, denied payouts or reliance on any figure, score or code. Nothing here limits liability that cannot be limited by law.</p>
<h2>9. Changes</h2><p>We may update these terms; the date below shows the latest version and the change history is public in our <a href="{QW_REPO}" rel="noopener">repository</a>.</p>
<p>Questions: <a href="{url('/contact/')}">contact</a>. See also <a href="{url('/privacy/')}">privacy</a>.</p>{qw_upd()}</article></div>"""
    page("/terms/", "Terms of Use | PropAnalyse", "PropAnalyse terms of use: information not advice, accuracy, scores as data-based opinions, affiliate links, reuse of our data, and liability.", body, [bl], extra_head=QW_CSS)

def contact():
    c, bl = crumbs([("Home", "/"), ("Contact", "/contact/")])
    to_p = globals().get("PARTNERS", "partners@propanalyse.com"); to_c = globals().get("CP_TO", "complaints@propanalyse.com")
    body = f"""<div class="wrap">{c}<article class="prose"><h1>Contact PropAnalyse</h1>
<p class="lede">Pick the route that matches what you need; each one goes to the person who handles it. Include links: we act on evidence.</p>
<dl class="qwkv">
<dt>Wrong or outdated figure</dt><dd>Use the <a href="{url('/for-firms/')}">correction form</a> (choose "Data correction") or <a href="{QW_ISSUES}?labels=correction&amp;title=Correction:%20" rel="noopener">open a GitHub issue</a>. Link the firm's page that shows the right figure. See the <a href="{url('/corrections/')}">corrections policy</a>.</dd>
<dt>Problem with a prop firm</dt><dd><a href="{url('/complaints/')}#report">Report a problem</a> (payout denied, rules changed, refund). E-mail: <a href="mailto:{to_c}">{to_c}</a>.</dd>
<dt>Prop firms</dt><dd>Listing requests, corrections to your own data, status reviews and partnerships: <a href="{url('/for-firms/')}">For prop firms</a>, or <a href="mailto:{to_p}">{to_p}</a>.</dd>
<dt>Privacy and deletion</dt><dd>See the <a href="{url('/privacy/')}">privacy notice</a>; send requests to <a href="mailto:{to_p}">{to_p}</a> with "Privacy" in the subject.</dd>
<dt>Anything else</dt><dd><a href="{QW_ISSUES}" rel="noopener">GitHub issues</a> (public) or <a href="mailto:{to_p}">{to_p}</a>.</dd></dl>
<p class="note"><b>Public or private?</b> GitHub issues are public; don't put your e-mail, account IDs or KYC documents in them. Use e-mail for anything private. If an e-mail ever bounces, open a GitHub issue saying so and we will reply there.</p>
<p>We aim to acknowledge corrections and complaints within 3 business days. We do not offer trading advice or help choosing a specific challenge by private message; the <a href="{url('/quiz/')}">firm finder</a> and <a href="{url('/compare/')}">comparisons</a> are built for that.</p>{qw_upd()}</article></div>"""
    page("/contact/", "Contact PropAnalyse: Corrections, Complaints, Firms", "How to reach PropAnalyse: data corrections, complaints about a prop firm, listing and status requests from firms, and privacy requests.", body, [bl, {"@context": "https://schema.org", "@type": "ContactPage", "name": "Contact PropAnalyse", "url": ABS + "/contact/"}], extra_head=QW_CSS)

def corrections():
    c, bl = crumbs([("Home", "/"), ("Corrections policy", "/corrections/")])
    CL = globals().get("CHANGES") or []
    fixes = [x for x in CL if x.get("kind") == "Correction"][:12]
    rows = "".join(f'<tr><td class="n nowrap"><time datetime="{e(x["date"])}">{nice_date(x["date"])}</time></td><td><a href="{url("/firms/" + x["slug"] + "/#history")}">{e(x["firm"])}</a></td><td>{e(x["field"])}</td><td class="was">{e(str(x["old"]) if x["old"] is not None else "not recorded")}</td><td class="now">{e(str(x["new"]))}</td></tr>' for x in fixes)
    tbl = (f'<div class="tablewrap"><table class="mini log"><thead><tr><th scope="col">Date</th><th scope="col">Firm</th><th scope="col">Field</th><th scope="col">Was</th><th scope="col">Now</th></tr></thead><tbody>{rows}</tbody></table></div>') if rows else '<p class="small">No corrections logged yet.</p>'
    body = f"""<div class="wrap">{c}<article class="prose"><h1>Corrections policy</h1>
<p class="lede">We get things wrong sometimes, and firms change their rules without telling anyone. When a figure is wrong we fix it in the open, date it, and keep the old value on record.</p>
<h2>How to report an error</h2><p>Send the page on our site, what is wrong, and a link to the firm's own page (or another primary source) that shows the correct figure. Use the <a href="{url('/for-firms/')}">correction form</a>, a <a href="{QW_ISSUES}?labels=correction&amp;title=Correction:%20" rel="noopener">GitHub issue</a>, or the routes on the <a href="{url('/contact/')}">contact page</a>. Firms correcting their own data use the same process.</p>
<h2>What we do</h2><ol>
<li><b>Acknowledge</b> within 3 business days.</li><li><b>Re-verify</b> on the firm's own site, not just the report. If the source supports the change, we update the data; if it does not, we reply with what we found.</li>
<li><b>Publish</b> the fix: the field, the old value, the new value and the date go into the <a href="{url('/news/')}">change log</a> marked "Correction", and the firm page's "last verified" date updates.</li>
<li><b>Re-score</b> automatically: the PA Score is recalculated from the corrected data on the next build.</li></ol>
<h2>What counts as a correction</h2><p>A figure we recorded wrongly or missed (for example a cheaper program we had not captured) is a <b>correction</b>. A firm changing its price or rules is a <b>rule change</b>, logged as such. We keep both apart so the change log stays an honest record of what firms actually did.</p>
<h2>What we will not do</h2><ul class="bul"><li>Remove accurate, sourced information because a firm asks.</li><li>Change a score, rank or status without a change in the underlying data or evidence.</li><li>Delete old values: corrected figures stay in the log.</li></ul>
<p>Caution and closed statuses have their own review route with evidence: <a href="{url('/methodology/')}#status">status rule</a> and <a href="{url('/for-firms/')}#status-review">request a review</a>.</p>
<h2 id="log">Recent corrections</h2>{tbl}<p class="small">Full history: <a href="{url('/news/')}">rule-change and correction log</a>, <a href="{url('/news/changes.json')}">JSON</a>.</p>{qw_upd()}</article></div>"""
    page("/corrections/", "Corrections Policy | PropAnalyse", "How PropAnalyse corrects errors: how to report, how we re-verify on the firm's own site, and how every correction is dated and logged.", body, [bl], extra_head=QW_CSS)

def qw_pages():
    disclosure(); terms(); contact(); corrections()

FOOT_EXTRA.extend([("/disclosure/", "Disclosure"), ("/terms/", "Terms"), ("/contact/", "Contact"), ("/corrections/", "Corrections")])
if "ZH_FOOT" in globals(): ZH_FOOT.append(("/disclosure/", "利益披露 (English)"))

QW_FX_NOTE = ('<p class="note qwfx"><b>Disclosure.</b> PropAnalyse is operated by the team behind FundedXyz. FundedXyz is scored and ranked by the same formula as every other firm. '
              '<a href="{u}">Read the full disclosure</a>.</p>')
_qw_prev_page2 = page
def page(path, title, desc, body, jsonld=None, og_type="website", extra_head="", lang="en"):
    if "fundedxyz" in path and "qwfx" not in body and "/disclosure/" not in body:
        note = QW_FX_NOTE.format(u=url("/disclosure/")) if lang != "zh" else f'<p class="note qwfx"><b>利益披露。</b>PropAnalyse 由 FundedXyz 的团队运营；FundedXyz 与其他公司使用同一评分公式。<a href="{url("/disclosure/")}">完整披露（英文）</a></p>'
        if '<p class="note"><b>Disclosure.</b>' in body:
            body = re.sub(r'<p class="note"><b>Disclosure\.</b>.*?</p>', note, body, count=1)
        elif "</nav>" in body: body = body.replace("</nav>", "</nav>" + note, 1)
        else: body = note + body
    return _qw_prev_page2(path, title, desc, body, jsonld, og_type, extra_head, lang)

def qw_finalize():
    # footer "Disclosure" column: link to the full page (base template is plain text)
    for root, _, files in os.walk(OUT):
        for fn in files:
            if not fn.endswith(".html"): continue
            p = os.path.join(root, fn); s = open(p).read(); o = s
            for h in ("Disclosure", "利益披露"):
                k = f"<div><h2>{h}</h2><p>"
                i = s.find(k)
                if i >= 0 and "qwfd" not in s:
                    j = s.find("</p>", i)
                    lab = "Full disclosure" if h == "Disclosure" else "完整披露（英文）"
                    s = s[:j] + f' <a class="qwfd" href="{url("/disclosure/")}">{lab}</a>' + s[j:]
            if s != o: open(p, "w").write(s)


# 3. Mobile: stack wide data tables into cards at <768px (labels from the header row)
ASSET_V = "14"
QW_STACK_RX = re.compile(r'<table class="mini (?:offers|crypto|sttable)[^"]*"[^>]*>.*?</table>', re.S)
def qw_stack_table(t):
    if "qwstack" in t: return t
    head = t.split("</thead>")[0]
    labs = [re.sub(r"<[^>]+>", "", h).strip() if 'class="sr"' not in h else "" for h in re.findall(r"<th[^>]*>(.*?)</th>", head, re.S)]
    t = t.replace('<table class="mini ', '<table class="qwstack mini ', 1)
    def row(m):
        i = [0]
        def cell(c):
            k = i[0]; i[0] += 1
            attrs, inner = c.group(1), c.group(2)
            lab = labs[k] if k < len(labs) else ""
            plain = re.sub(r"<[^>]+>", "", inner)
            extra = ""
            if k > 0 and lab and "data-l=" not in attrs and "data-label=" not in attrs: extra += f' data-l="{e(lab)}"'
            elif "data-label=" in attrs: attrs = attrs.replace("data-label=", "data-l=")
            if k > 0 and len(plain.strip()) > 38 and "qwfull" not in attrs:
                attrs = (attrs.replace('class="', 'class="qwfull ', 1) if 'class="' in attrs else attrs + ' class="qwfull"')
            return f"<td{attrs}{extra}>{inner}</td>"
        return re.sub(r"<td([^>]*)>(.*?)</td>", cell, m.group(0), flags=re.S)
    body = t.split("</thead>", 1)
    return body[0] + "</thead>" + re.sub(r"<tr[^>]*>.*?</tr>", row, body[1], flags=re.S) if len(body) == 2 else t

_qw_prev_finalize = qw_finalize
def qw_finalize():
    _qw_prev_finalize()
    for root, _, files in os.walk(OUT):
        for fn in files:
            if not fn.endswith(".html"): continue
            p = os.path.join(root, fn); s = open(p).read()
            if 'class="mini offers' in s or 'class="mini crypto' in s or 'class="mini sttable' in s:
                n = QW_STACK_RX.sub(lambda m: qw_stack_table(m.group(0)), s)
                if n != s: open(p, "w").write(n)
