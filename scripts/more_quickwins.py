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
QW_STACK_RX = re.compile(r'<table class="mini (?:offers|crypto|sttable|qwsizes)[^"]*"[^>]*>.*?</table>', re.S)
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
            if any(x in s for x in ('class="mini offers', 'class="mini crypto', 'class="mini sttable', 'class="mini qwsizes')):
                n = QW_STACK_RX.sub(lambda m: qw_stack_table(m.group(0)), s)
                if n != s: open(p, "w").write(n)


# 4. Titles <= 60 chars (scripts/qw_titles.py): rewrite <title> and og:title after all modules have run
exec(compile(open(os.path.join(ROOT, "scripts", "qw_titles.py")).read(), "qw_titles.py", "exec"))
_qw_prev_finalize2 = qw_finalize
def qw_finalize():
    _qw_prev_finalize2()
    for root, _, files in os.walk(OUT):
        for fn in files:
            if fn != "index.html": continue
            p = os.path.join(root, fn); s = open(p).read()
            m = re.search(r"<title>(.*?)</title>", s)
            if not m: continue
            path = "/" + os.path.relpath(root, OUT).replace(os.sep, "/").strip(".").strip("/") + "/"
            path = "/" if path == "//" else path
            old = html.unescape(m.group(1)); new = qw_short_title(old, path)
            if new == old: continue
            s = s.replace(m.group(0), f"<title>{e(new)}</title>", 1)
            s = s.replace(f'<meta property="og:title" content="{m.group(1)}">', f'<meta property="og:title" content="{e(new)}">', 1)
            open(p, "w").write(s)



# 5. Per-page OG images: one card per firm (also used by its /legit/ and /crypto/ pages) and per compare page
try:
    exec(compile(open(os.path.join(ROOT, "scripts", "og_cards.py")).read(), "og_cards.py", "exec"), (QW_OG := {"__file__": os.path.join(ROOT, "scripts", "og_cards.py"), "__name__": "og_cards"}))
except Exception as _x:   # Pillow missing: keep the site-wide og.png
    print("og cards disabled:", _x); QW_OG = None
QW_OG_MAP = {}   # page path -> (image path, alt)
def qw_og_firm(f):
    rel = f"/og/firms/{f['slug']}.png"
    if rel not in QW_OG_MAP.values():
        f["_sub"] = "  ·  ".join(x for x in (CAT_LABEL.get(f.get("category"), "") + " prop firm" if f.get("category") else "", short_hq(f.get("hq") or ""), f"since {int(num(f['founded']))}" if num(f.get("founded")) else "") if x)
        QW_OG["firm_card"](f, OUT + rel, money(f["_fee"], f.get("fee_currency")) if f["_fee"] is not None else "Not published",
                           "Verified " + nice_date(f.get("last_verified") or TODAY), f"PA Score · ranked #{f['_rank']} of {len(FIRMS)}")
    return rel
def qw_og_build():
    if not QW_OG: return
    n = 0
    for f in FIRMS:
        rel = qw_og_firm(f); n += 1
        alt = f"{f['name']}: PA Score {f['_score']:.1f}/10, fees from {money(f['_fee'], f.get('fee_currency')) if f['_fee'] is not None else 'not published'}, split {f.get('profit_split') or 'not published'}"
        for p in (f"/firms/{f['slug']}/", f"/firms/{f['slug']}/legit/", f"/crypto/{f['slug']}/"): QW_OG_MAP[p] = (rel, alt)
    for a, b in PAIRS:
        A, B = BY[a], BY[b]; rel = f"/og/compare/{a}-vs-{b}.png"
        fa = money(A["_fee"], A.get("fee_currency")) if A["_fee"] is not None else "n/a"; fb = money(B["_fee"], B.get("fee_currency")) if B["_fee"] is not None else "n/a"
        QW_OG["compare_card"](A, B, OUT + rel, fa, fb, nice_date(TODAY)); n += 1
        QW_OG_MAP[f"/compare/{a}-vs-{b}/"] = (rel, f"{A['name']} vs {B['name']}: PA Score {A['_score']:.1f} vs {B['_score']:.1f}, fees from {fa} vs {fb}")
    print(f"og cards: {n}")

QW_OG_DEFAULT_ALT = "PropAnalyse: prop firms compared on the numbers"
def qw_og_tags(img, alt):
    return (f'<meta property="og:image" content="{ABS}{img}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">'
            f'<meta property="og:image:alt" content="{e(alt)}"><meta name="twitter:image" content="{ABS}{img}"><meta name="twitter:image:alt" content="{e(alt)}">')
_qw_prev_finalize3 = qw_finalize
def qw_finalize():
    qw_og_build()
    _qw_prev_finalize3()
    tag = f'<meta property="og:image" content="{ABS}/assets/og.png">'
    for root, _, files in os.walk(OUT):
        for fn in files:
            if fn != "index.html": continue
            p = os.path.join(root, fn); s = open(p).read()
            if tag not in s: continue
            path = "/" + os.path.relpath(root, OUT).replace(os.sep, "/").strip(".").strip("/") + "/"
            path = "/" if path == "//" else path
            img, alt = QW_OG_MAP.get(path) or globals().get("QW_OG_EXTRA", {}).get(path) or ("/assets/og.png", QW_OG_DEFAULT_ALT)
            s = s.replace(tag, qw_og_tags(img, alt), 1); open(p, "w").write(s)



# 7. Shareable calculator results: src/share.js keeps inputs in the URL; share / copy-link buttons; per-tool OG cards
QW_SHARE_HTML = ('<div class="qwshare"><h2>Share this result</h2><p class="small" id="qw-sum"></p>'
                 '<p class="qwbtns"><button type="button" class="btn sm" id="qw-share">Share result</button><button type="button" class="btn line sm" id="qw-copy">Copy link</button></p>'
                 '<p class="small" id="qw-msg" aria-live="polite">The link keeps every input, so it reopens this exact result.</p></div>')
QW_SHARE_CSS = "<style>.qwshare{margin-top:20px;padding-top:16px;border-top:1px solid var(--rule)}.qwshare h2,.qwshare h3{font-size:15px;margin:0 0 6px}.qwbtns{display:flex;gap:10px;flex-wrap:wrap;margin:10px 0 6px}</style>"
QW_TOOL_OG = {
    "true-cost": ("Free calculator", "What a prop firm challenge really costs you", [("Retries", "and resets counted"), ("Refunds", "when the firm pays them"), ("Break-even", "gross profit needed"), (str(len(FIRMS)) + " firms", "rules preloaded")]),
    "drawdown": ("Free calculator", "How much room before your prop account is breached", [("Static", "fixed floor"), ("Trailing", "follows your high"), ("EOD", "end-of-day trailing"), ("$ floors", "daily and overall")]),
    "profit-target": ("Free calculator", "Profit target in dollars, days and payout", [("Phase 1", "target in $"), ("Phase 2", "target in $"), ("Days", "at your daily return"), ("Payout", "after the split")]),
}
QW_OG_EXTRA = {}
def qw_tool_og():
    if not QW_OG: return
    for k, (kick, title, cols) in QW_TOOL_OG.items():
        rel = f"/og/tools/{k}.png"
        QW_OG["text_card"](kick, title, cols, OUT + rel, right="propanalyse.com/tools/" + k + "/")
        QW_OG_EXTRA[f"/tools/{k}/"] = (rel, title + " (PropAnalyse calculator)")
_qw_prev_page3 = page
def page(path, title, desc, body, jsonld=None, og_type="website", extra_head="", lang="en"):
    m = re.fullmatch(r"/tools/(true-cost|drawdown|profit-target)/", path)
    if m and "qwshare" not in body:
        body = body.replace('</div></div>\n<section class="block"><h2>How it works</h2>', QW_SHARE_HTML + '</div></div>\n<section class="block"><h2>How it works</h2>', 1)
        body = body + f'<script src="{url("/assets/share.js")}?v={ASSET_V}" defer></script>'
        extra_head = (extra_head or "") + QW_SHARE_CSS
    return _qw_prev_page3(path, title, desc, body, jsonld, og_type, extra_head, lang)
_qw_prev_og_build = qw_og_build
def qw_og_build():
    _qw_prev_og_build(); qw_tool_og()
    shutil.copy(os.path.join(ROOT, "src", "share.js"), os.path.join(OUT, "assets", "share.js"))



# 8. "Is my prop firm safe?" checker: /safe/ + /zh/safe/ hubs (indexable) and /safe/<slug>/ + /zh/safe/<slug>/ result cards (noindex, shareable, own OG card)
QW_SAFE_L = {
  "en": dict(h1="Is my prop firm safe?", lede="Type a prop firm's name to see its status on PropAnalyse (active, caution or closed), its PA Score and the evidence behind it, with sources. {n} firms checked, including {c} with a caution and {x} that have shut down.",
             ph="Firm name, e.g. FTMO", go="Check", active="Active", caution="Caution", closed="Closed", score="PA Score", notrated="Not rated (closed)",
             ev="Evidence", todo="What to do", full="Full review", legit="Evidence check", share="Share this result", copy="Copy link", sharebtn="Share",
             since="since", verified="Checked", lists=("Closed firms", "Firms with a caution", "Active firms"), notfound="No firm by that name in our list yet. Check the spelling, or ask us to add it.",
             another="Check another firm", src="source", tp="Trustpilot", norating="no rating shown", founded="founded", cp="verified complaints",
             a_todo="No warning signs at our last check. Before buying: read the firm's rules page, start with the smallest account, and keep screenshots of the rules and every payout request.",
             c_todo="Read the evidence below before buying. If you already hold an account, keep dated screenshots of the rules and of every payout request, and file a complaint with us if a payout is refused.",
             x_todo="This firm no longer operates. Do not buy anything sold under its name without checking the domain and company. If you are owed money, follow the official route in the sources.",
             note="Status follows a published rule and dated sources, not opinion; it is not a finding of fraud. A caution is re-checked at least every 30 days.", alt="Alternatives"),
  "zh": dict(h1="我的自营交易公司安全吗？", lede="输入公司名称，查看它在 PropAnalyse 上的状态（正常、警示或已关闭）、PA 评分及证据来源。共核查 {n} 家公司，其中 {c} 家被列为警示，{x} 家已关闭。",
             ph="公司名称，例如 FTMO", go="查询", active="正常", caution="警示", closed="已关闭", score="PA 评分", notrated="已关闭，不评分",
             ev="证据", todo="建议", full="完整评测", legit="证据核查", share="分享结果", copy="复制链接", sharebtn="分享",
             since="自", verified="核查日期", lists=("已关闭的公司", "警示公司", "正常运营的公司"), notfound="列表中暂无此公司。请检查拼写，或请我们收录。",
             another="查询其他公司", src="来源", tp="Trustpilot", norating="未显示评分", founded="成立于", cp="条已核实投诉",
             a_todo="上次核查未发现警示信号。购买前：阅读公司规则页面，从最小账户开始，并保存规则和每次出金申请的截图。",
             c_todo="购买前请先阅读下方证据。如已持有账户，请保存带日期的规则截图和每次出金申请记录；如出金被拒，可向我们投诉。",
             x_todo="该公司已停止运营。不要购买以其名义销售的任何产品，先核实域名和公司。如有欠款，请按来源中的官方途径处理。",
             note="状态依据公开规则和带日期的来源，而非主观意见；不代表欺诈认定。警示状态至少每 30 天复核一次。", alt="替代选择"),
}
def qw_safe_rows():
    rows = []
    for c in globals().get("ST_CLOSED", []):
        rows.append(dict(slug=c["slug"], name=c["name"], status="closed", score=None, rank="", site=c.get("site") or "", since=c.get("status_since"),
                         ev=[(c.get("status_reason") or "", None, c.get("status_since"))] + [((s.get("publisher") or "") + ": " + (s.get("title") or ""), s.get("url"), s.get("date")) for s in c.get("status_sources", [])[:4]],
                         ev_zh=[(c.get("status_reason_zh") or c.get("status_reason") or "", None, c.get("status_since"))], action=c.get("trader_action"), tp=None, founded=c.get("founded"), checked=c.get("checked")))
    for f in RANKED:
        caut = st_is_caution(f)
        tp = f.get("trustpilot") or {}
        if caut:
            stc = ST_CAUTION.get(f["slug"], {})
            ev = [(stc.get("status_reason") or "", None, stc.get("status_since"))] + [(x.get("text") or "", x.get("url"), x.get("date")) for x in stc.get("evidence", [])[:5]]
        else:
            lvl, pts, why = evidence(f)
            ev = [(f"Evidence level {lvl} ({pts}/6)" + (": " + "; ".join(why) if why else ""), url(f"/firms/{f['slug']}/legit/"), None)]
            for x in caution(f)[:3]: ev.append((x, None, None))
        rows.append(dict(slug=f["slug"], name=f["name"], status="caution" if caut else "active", score=f["_score"], rank=f"#{f['_rank']} of {len(FIRMS)}",
                         site=f.get("site") or "", since=f.get("status_since") if caut else None, ev=ev, ev_zh=None, action=None,
                         tp=(num(tp.get("score")), int(num(tp.get("count") or 0) or 0)), founded=f.get("founded"), checked=f.get("last_verified") or TODAY))
    return rows
def qw_stars(s):
    if s is None: return ""
    v = round(s / 2 * 2) / 2
    return '<span class="sfstars" aria-label="' + f"{s / 2:.1f} out of 5" + '">' + "★" * int(v) + ("½" if v % 1 else "") + '<span class="sfoff">' + "★" * (5 - int(v) - (1 if v % 1 else 0)) + "</span></span>"
def qw_dom(u): return re.sub(r"^https?://(www\.)?", "", u or "").split("/")[0]
def qw_safe_card(r, lang="en"):
    L = QW_SAFE_L[lang]; zh = lang == "zh"; fd = (zdate if zh else nice_date)
    lab = L[r["status"]]
    since = (f' {L["since"]} {fd(str(r["since"]))}' if r.get("since") and r["status"] != "active" else "")
    sc = (f'<p class="sfsc"><b class="n">{r["score"]:.1f}</b><small>/10 {L["score"]}</small> {qw_stars(r["score"])} <span class="small">{e(r["rank"])}</span></p>' if r["score"] is not None else f'<p class="sfsc"><span class="nil">{L["notrated"]}</span></p>')
    evs = r["ev_zh"] if zh and r.get("ev_zh") else r["ev"]
    lis = "".join(f'<li>{e(t)}' + (f' <a href="{e(u)}"' + (' rel="nofollow noopener" target="_blank"' if u.startswith("http") else "") + f'>{L["src"]}</a>' if u else "") + (f' <time class="small" datetime="{e(str(d))}">({fd(str(d))})</time>' if d else "") + "</li>" for t, u, d in evs if t)
    meta = []
    if r.get("tp") and r["tp"][0]: meta.append(f'{L["tp"]} <b class="n">{r["tp"][0]:.1f}</b> ({r["tp"][1]:,})')
    elif r.get("tp") and r["tp"][1]: meta.append(f'{L["tp"]}: {L["norating"]} ({r["tp"][1]:,})')
    if num(r.get("founded")): meta.append(f'{L["founded"]} <span class="n">{int(num(r["founded"]))}</span>')
    if r["status"] != "closed": meta.append(f'{len(cp_of(r["slug"]))} {L["cp"]}')
    meta.append(f'{L["verified"]} <time datetime="{e(str(r["checked"]))}">{fd(str(r["checked"]))}</time>')
    todo = r.get("action") if (r["status"] == "closed" and r.get("action") and not zh) else L[{"active": "a_todo", "caution": "c_todo", "closed": "x_todo"}[r["status"]]]
    links = f'<a href="{url("/firms/" + r["slug"] + "/")}">{L["full"]}</a>' + (f' · <a href="{url("/firms/" + r["slug"] + "/legit/")}">{L["legit"]}</a>' if r["status"] != "closed" else "") + (f' · <a href="{url("/best/")}">{L["alt"]}</a>' if r["status"] != "active" else "")
    ic_ = {"active": "✓", "caution": "!", "closed": "×"}[r["status"]]
    return (f'<article class="sfcard sf-{r["status"]}" id="result"><p class="sfst"><span class="sfic" aria-hidden="true">{ic_}</span>{e(lab)}{e(since)}</p>'
            f'<h2>{e(r["name"])} <small class="small">{e(qw_dom(r["site"]))}</small></h2>{sc}<p class="small sfmeta">{" · ".join(meta)}</p>'
            f'<h3>{L["ev"]}</h3><ul class="bul sfev">{lis}</ul><h3>{L["todo"]}</h3><p>{e(todo)}</p><p class="sflinks">{links}</p>'
            f'<div class="qwshare"><h3>{L["share"]}</h3><p class="qwbtns"><button type="button" class="btn sm" data-sfshare>{L["sharebtn"]}</button><button type="button" class="btn line sm" data-sfcopy>{L["copy"]}</button></p><p class="small" data-sfmsg aria-live="polite"></p></div>'
            f'<p class="small">{e(L["note"])}</p></article>')
QW_SAFE_CSS = """<style>.sfform{display:flex;gap:10px;flex-wrap:wrap;margin:18px 0 8px}.sfform input{flex:1 1 260px;min-width:0;font:inherit;font-size:17px;padding:12px 14px;border:1px solid var(--rule-2);border-radius:var(--r-box,8px);background:var(--bg-elev,#fff);color:var(--ink)}
.sfcard{border:1px solid var(--rule-2);border-left-width:6px;border-radius:var(--r-box,8px);padding:18px 20px;margin:20px 0;background:var(--bg-elev,#fff);max-width:760px}.sfcard h2{margin:4px 0 6px}.sfcard h3{font-size:15px;margin:16px 0 6px}
.sf-active{border-left-color:#107a46}.sf-caution{border-left-color:#b02020}.sf-closed{border-left-color:#5a6680}.sfst{font:600 14px/1.2 var(--f-ui);letter-spacing:.06em;text-transform:uppercase;margin:0;display:flex;align-items:center;gap:8px}
.sf-active .sfst{color:#107a46}.sf-caution .sfst{color:#b02020}.sf-closed .sfst{color:var(--mute)}.sfic{display:inline-grid;place-items:center;width:22px;height:22px;border-radius:50%;border:2px solid currentColor;font-size:13px}
.sfsc{display:flex;align-items:baseline;gap:8px;flex-wrap:wrap;margin:4px 0}.sfsc b{font-size:34px}.sfstars{color:var(--accent);letter-spacing:2px}.sf-caution .sfstars{color:#b02020}.sfoff{color:var(--rule-2)}
.sfmeta{color:var(--mute)}.sfcols{display:grid;gap:24px;margin-top:28px}@media(min-width:900px){.sfcols{grid-template-columns:repeat(3,minmax(0,1fr))}}.sfcols ul{list-style:none;padding:0;margin:0;border-top:1px solid var(--rule-2)}.sfcols li a{display:flex;justify-content:space-between;gap:10px;padding:9px 0;border-bottom:1px solid var(--rule);text-decoration:none}
.sfmiss{color:#b02020}@media (prefers-color-scheme:dark){.sf-active{border-left-color:#4fc98a}.sf-caution{border-left-color:#ff7b72}.sf-active .sfst{color:#4fc98a}.sf-caution .sfst,.sfmiss,.sf-caution .sfstars{color:#ff8f87}}</style>"""
def qw_safe_js(lang):
    L = QW_SAFE_L[lang]; base = url("/zh/safe/" if lang == "zh" else "/safe/")
    return ("<script>(function(){var F=document.getElementById('sfform');if(F){var I=F.querySelector('input'),D=JSON.parse(document.getElementById('sfdata').textContent),M=document.getElementById('sfmiss');"
            "function norm(s){return (s||'').toLowerCase().replace(/^https?:\\/\\/(www\\.)?/,'').replace(/[^a-z0-9]/g,'')}"
            "F.addEventListener('submit',function(ev){ev.preventDefault();var q=norm(I.value);if(!q)return;var hit=D.find(function(d){return norm(d[1])===q||d[0].replace(/-/g,'')===q||norm(d[2])===q||norm(d[2]).split('com')[0]===q})||D.find(function(d){return norm(d[1]).indexOf(q)===0})||D.find(function(d){return norm(d[1]).indexOf(q)>=0||norm(d[2]).indexOf(q)>=0});"
            "if(hit){location.href='" + base + "'+hit[0]+'/#result'}else{M.hidden=false}})}"
            "var S=document.querySelector('[data-sfshare]'),C=document.querySelector('[data-sfcopy]'),G=document.querySelector('[data-sfmsg]');function cp(t){if(navigator.clipboard)navigator.clipboard.writeText(t).then(function(){G.textContent='" + ("已复制" if lang == "zh" else "Copied.") + "'});else window.prompt('Copy',t)}"
            "var u=location.origin+location.pathname,t=document.title;if(S)S.addEventListener('click',function(){if(navigator.share){navigator.share({title:t,url:u}).catch(function(){})}else cp(t+' '+u)});if(C)C.addEventListener('click',function(){cp(u)})})();</script>")
def qw_safe_form(rows, lang):
    L = QW_SAFE_L[lang]
    data = json.dumps([[r["slug"], r["name"], qw_dom(r["site"])] for r in rows], ensure_ascii=False).replace("</", "<\\/")
    opts = "".join(f'<option value="{e(r["name"])}">' for r in rows)
    return (f'<form class="sfform" id="sfform" role="search"><label class="sr" for="sfq">{L["ph"]}</label><input id="sfq" list="sflist" autocomplete="off" placeholder="{e(L["ph"])}"><datalist id="sflist">{opts}</datalist>'
            f'<button class="btn" type="submit">{L["go"]}</button></form><p class="small sfmiss" id="sfmiss" hidden>{e(L["notfound"])} <a href="{url("/for-firms/")}">{"→"}</a></p><script type="application/json" id="sfdata">{data}</script>')
def qw_safe_pages():
    rows = qw_safe_rows()
    byst = {k: [r for r in rows if r["status"] == k] for k in ("closed", "caution", "active")}
    for lang in ("en", "zh"):
        L = QW_SAFE_L[lang]; zh = lang == "zh"; hub = "/zh/safe/" if zh else "/safe/"
        cols = "".join(f'<section><h2>{L["lists"][i]} <span class="n small">({len(byst[k])})</span></h2><ul>' + "".join(
            f'<li><a href="{url(hub + r["slug"] + "/")}#result"><span>{e(r["name"])}</span><span class="small n">{(f"{r[chr(115)+chr(99)+chr(111)+chr(114)+chr(101)]:.1f}" if r["score"] is not None else L["closed"])}</span></a></li>' for r in byst[k]) + "</ul></section>"
            for i, k in enumerate(("closed", "caution", "active")))
        lede = L["lede"].format(n=len(rows), c=len(byst["caution"]), x=len(byst["closed"]))
        c, bl = crumbs([("首页" if zh else "Home", "/zh/" if zh else "/"), (L["h1"], hub)])
        if zh:
            how = ("<h2>怎么判断</h2><p>状态来自 PropAnalyse 的公开规则：<b>正常</b> = 未触发任何警示条件；<b>警示</b> = 仍在销售，但有带日期的公开证据（如大量出金投诉、Trustpilot 被暂停）；<b>已关闭</b> = 已停止运营，有来源佐证。"
                   f"警示公司的评分上限为 4.0。详见 <a href=\"{url('/zh/methodology/')}\">方法论</a>。</p>")
            qa = [("怎么知道一家自营交易公司是否安全？", "看三件事：是否有大量近期出金投诉、是否有监管或法院记录、规则和费用是否公开透明。本页把这些证据集中列出并附来源。"),
                  ("警示是什么意思？", "公司仍在销售，但有带日期的公开证据显示风险，例如近期评论大量反映出金未付。警示至少每 30 天复核一次。")]
        else:
            how = ("<h2>How the check works</h2><p>Every firm gets one of three statuses under a <a href=\"" + url("/methodology/") + "#status\">published rule</a>: <b>active</b> (no trigger holds), <b>caution</b> (still selling, but dated public evidence such as a cluster of recent payout complaints or a suspended Trustpilot profile) or <b>closed</b> (stopped operating, with sources). "
                   "A caution caps the PA Score at 4.0 and removes the firm from offers and best-of lists. We never call a firm a scam unless a regulator or court has said so.</p>"
                   "<p>Safe is relative: no prop firm is risk-free. Evaluations are paid products, most traders do not pass, and a firm's rules can change after you buy. That is why every card shows the date of our last check and links to the sources.</p>")
            qa = [("How do I know if a prop firm is safe?", "Check three things: a recent cluster of payout complaints, any regulator or court record, and whether the firm publishes its rules, fees and payout terms in full. This page puts that evidence in one place, with sources and dates."),
                  ("What does caution mean on PropAnalyse?", "The firm still sells challenges, but dated public evidence shows risk, such as many recent reviews reporting unpaid payouts or a suspended Trustpilot profile. The score is capped at 4.0 and the caution is re-checked at least every 30 days."),
                  ("Which prop firms have shut down?", f"{len(byst['closed'])} firms in our list have stopped operating, including " + ", ".join(r["name"] for r in byst["closed"][:5]) + ". Each has a dated card with sources.")]
        faqh = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in qa)
        body = (f'<div class="wrap">{c}<header class="ph"><h1>{e(L["h1"])}</h1><p class="lede">{e(lede)}</p>{qw_safe_form(rows, lang)}</header>'
                f'<div class="sfcols">{cols}</div><section class="block prose">{how}</section><section class="block faq"><h2>FAQ</h2>{faqh}</section></div>{qw_safe_js(lang)}')
        ld = [bl, {"@context": "https://schema.org", "@type": "WebApplication", "name": L["h1"], "url": ABS + hub, "applicationCategory": "FinanceApplication", "operatingSystem": "Any", "isAccessibleForFree": True},
              {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]}]
        if zh: page(hub, "我的自营交易公司安全吗？状态查询（正常/警示/已关闭）", f"输入公司名称，查看 {len(rows)} 家自营交易公司的状态、PA 评分和证据来源：{len(byst['caution'])} 家警示，{len(byst['closed'])} 家已关闭。", body, ld, extra_head=QW_SAFE_CSS + QW_CSS, lang="zh")
        else: page(hub, "Is My Prop Firm Safe? Status Checker (Active/Caution/Closed)", f"Check any of {len(rows)} prop firms: active, caution or closed, with PA Score, evidence and sources. {len(byst['caution'])} firms carry a caution and {len(byst['closed'])} have shut down.", body, ld, extra_head=QW_SAFE_CSS + QW_CSS)
        for r in rows:
            p = hub + r["slug"] + "/"
            c2, bl2 = crumbs([("首页" if zh else "Home", "/zh/" if zh else "/"), (L["h1"], hub), (r["name"], p)])
            body = (f'<div class="wrap">{c2}<header class="ph"><h1>{e(("" if not zh else "") + (r["name"] + ("安全吗？" if zh else ": is it safe?")))}</h1></header>{qw_safe_card(r, lang)}'
                    f'<section class="block"><h2>{e(L["another"])}</h2>{qw_safe_form(rows, lang)}</section></div>{qw_safe_js(lang)}')
            st = L[r["status"]]
            t = (f"{r['name']}安全吗？状态：{st}" if zh else f"Is {r['name']} Safe? Status: {st}" + (f", PA Score {r['score']:.1f}" if r["score"] is not None else ""))
            d = (f"{r['name']} 在 PropAnalyse 的状态：{st}。证据与来源。" if zh else f"{r['name']} on PropAnalyse: {st.lower()}" + (f", PA Score {r['score']:.1f}/10" if r["score"] is not None else "") + ". Evidence and sources, checked " + nice_date(str(r["checked"])) + ".")
            page(p, t, d, body, [bl2], extra_head=QW_SAFE_CSS + QW_CSS + '<meta name="robots" content="noindex,follow">', lang=lang)
            if PAGES and PAGES[-1] == p: PAGES.pop()   # share cards stay out of the sitemap
            QW_OG_EXTRA[p] = (f"/og/safe/{r['slug']}.png", f"{r['name']}: {QW_SAFE_L['en'][r['status']]}")
        if not zh: ZH_ALT["/safe/"] = "/zh/safe/"
    if QW_OG:
        for r in rows:
            st = QW_SAFE_L["en"][r["status"]]
            title = {"active": f"{r['name']}: active, no warning signs at our last check", "caution": f"{r['name']}: caution. Read the evidence before you buy", "closed": f"{r['name']}: closed" + (f" since {st_date(r['since'])}" if r.get("since") else "")}[r["status"]]
            colsx = [(st, "Status"), (f"{r['score']:.1f}/10" if r["score"] is not None else "Not rated", "PA Score"),
                     ((f"{r['tp'][0]:.1f} / 5" if r.get("tp") and r["tp"][0] else "No rating") if r["status"] != "closed" else (str(int(num(r["founded"]))) if num(r.get("founded")) else "n/a"), "Trustpilot" if r["status"] != "closed" else "Founded"),
                     (nice_date(str(r["checked"])), "Checked")]
            QW_OG["text_card"]("Is my prop firm safe?", title, colsx, OUT + f"/og/safe/{r['slug']}.png", right="propanalyse.com/safe/", tone=None if r["status"] == "active" else "red")
    QW_OG_EXTRA["/safe/"] = QW_OG_EXTRA["/zh/safe/"] = ("/og/safe/_hub.png", "Is my prop firm safe? Status checker")
    if QW_OG: QW_OG["text_card"]("Free checker", "Is my prop firm safe?", [(str(len(byst["active"])), "active firms"), (str(len(byst["caution"])), "with a caution"), (str(len(byst["closed"])), "closed"), ("Sources", "dated, linked")], OUT + "/og/safe/_hub.png", right="propanalyse.com/safe/")

_qw_prev_pages = qw_pages
def qw_pages():
    _qw_prev_pages(); qw_safe_pages()
FOOT_EXTRA.insert(0, ("/safe/", "Is my prop firm safe?"))
if "ZH_FOOT" in globals(): ZH_FOOT.insert(0, ("/zh/safe/", "公司安全查询"))



# 9. Thin hubs (<250 words): real, data-driven guidance on /sizes/, /tools/, /platforms/, /best/
def qw_fee_at(f, size):
    v = [num(sf.get("fee")) for p in as_list(f.get("programs")) for sf in as_list(p.get("sizes_fees")) if num(sf.get("size")) == size and num(sf.get("fee")) and (f.get("fee_currency") or "USD") == "USD"]
    return min(v) if v else None
def qw_median(xs):
    xs = sorted(x for x in xs if x is not None)
    if not xs: return None
    m = len(xs) // 2
    return xs[m] if len(xs) % 2 else (xs[m - 1] + xs[m]) / 2
def qw_sizes_extra():
    act = [f for f in RANKED if not st_is_caution(f)]
    rows = []
    for sz in (5000, 10000, 25000, 50000, 100000, 200000):
        fees = [(qw_fee_at(f, sz), f) for f in act]; fees = [(v, f) for v, f in fees if v]
        if not fees: continue
        lo = min(fees, key=lambda x: x[0]); med = qw_median([v for v, _ in fees])
        rows.append(f'<tr><td class="n">{money(sz)}</td><td class="num n">{len(fees)}</td><td class="num n">{money(med)}</td><td class="num n">{money(med / sz * 1000)}</td><td><a href="{url("/firms/" + lo[1]["slug"] + "/")}">{e(lo[1]["name"])}</a> <span class="n">{money(lo[0])}</span></td><td class="num n">{money(sz * .08)}</td><td class="num n">{money(sz * .05)}</td></tr>')
    tbl = ('<div class="tablewrap"><table class="mini qwsizes"><thead><tr><th scope="col">Account</th><th scope="col" class="num">Firms (USD)</th><th scope="col" class="num">Median fee</th><th scope="col" class="num">Median per $1K</th><th scope="col">Cheapest</th><th scope="col" class="num">8% target</th><th scope="col" class="num">5% daily loss</th></tr></thead><tbody>' + "".join(rows) + "</tbody></table></div>")
    return (f'<section class="block prose" id="choose"><h2>How to choose an account size</h2>'
            f'<p>Most firms sell the same evaluation in several sizes, and the fee rises with the size. What changes for you is not the rules (the percentages are usually identical) but the dollar amounts: the profit target, the daily loss limit and the payout you can earn. The table uses the cheapest USD-priced program each active firm publishes at that size; firms pricing in EUR (FTMO) are left out so medians are comparable.</p>{tbl}'
            f'<p><b>Smaller accounts cost less per attempt, not per dollar of buying power.</b> The median fee per $1,000 of account usually falls as size goes up, so a $100K account is often better value than two $50K accounts, but only if you can trade it calmly. A 5% daily limit on $100K is $5,000; one oversized position can take it.</p>'
            f'<p><b>Size your risk, not your ego.</b> A common rule of thumb is to risk well under 1% of the account per trade, so a losing streak cannot reach the daily limit. If that feels too small to reach the target in a reasonable time, the account size is too big for your strategy rather than the target too high.</p>'
            f'<p><b>Count the retries.</b> Most traders need more than one attempt. Use the <a href="{url("/tools/true-cost/")}">true-cost calculator</a> to see what two or three attempts at each size really cost, including refunds and activation fees, and compare per-$1K cost across firms on each size page below.</p>'
            f'<p><b>Check the scaling plan.</b> Some firms grow a funded account after consistent payouts, so starting smaller and scaling can beat buying the largest account up front. Payout splits often rise with account size or after milestones; see each firm\'s program table.</p></section>')
def qw_tools_extra():
    f = BY.get("ftmo"); ex = ""
    if f:
        p = next((p for p in as_list(f.get("programs")) if "2-Step" in (p.get("name") or "")), None)
        sf = next((x for x in as_list((p or {}).get("sizes_fees")) if num(x.get("size")) == 100000), None)
        if sf: ex = (f'<p><b>Worked example.</b> The {e(p["name"])} at $100K lists €{num(sf["fee"]):,.0f}. If you pass on the second attempt with no retry discount, you spend €{2 * num(sf["fee"]):,.0f}; FTMO refunds the fee with the first reward, so the net cost is €{num(sf["fee"]):,.0f}. '
                     f'At a 90% split you break even after roughly €{num(sf["fee"]) / 0.9:,.0f} of gross profit. <a href="{url("/tools/true-cost/")}?firm=ftmo">Open this in the calculator</a> and change any input; the link updates so you can share the exact result.</p>')
    return (f'<section class="block prose"><h2>What each calculator answers</h2>'
            f'<p><b>True cost to first payout.</b> The sticker price of a challenge is only the first attempt. The calculator adds retries (at the firm\'s retry discount, if it publishes one), activation fees charged after passing, and subtracts refunds paid with the first payout. It then shows the gross profit you need before you are ahead, and what you keep from a first payout of a given size.</p>{ex}'
            f'<p><b>Drawdown in dollars.</b> Daily loss and maximum drawdown are published as percentages, but breaches happen in dollars. Enter your balance, day-start equity and highest balance, and it shows both floors, which one binds first, and how much room is left. It handles static, trailing and end-of-day trailing drawdown, including trailing floors that lock at the starting balance.</p>'
            f'<p><b>Profit target and timeline.</b> Turns the phase targets into dollars, estimates trading days at your average daily return (never fewer than the firm\'s minimum days) and shows what a payout at target is worth after the split. If the day count looks unrealistic, the target, not your discipline, is the problem.</p>'
            f'<p><b>Firm finder.</b> Seven questions (market, budget, evaluation style, account size, what matters most, must-have rules, country) filtered against every firm in the dataset.</p>'
            f'<h2>How they get their numbers</h2><p>Each calculator can load a firm\'s published fees and rules from our <a href="{url("/data/firms.json")}">open dataset</a>, the same data behind the firm pages, verified on the date shown on each firm page. Every prefilled value can be overwritten. Calculations run in your browser and nothing you type is sent anywhere. They do not model slippage, spreads, commissions or rule details such as consistency rules or news restrictions; read the firm\'s rules page before you buy.</p></section>')
def qw_platforms_extra():
    from collections import Counter
    act = [f for f in RANKED if not st_is_caution(f)]
    cnt = Counter(p for f in act for p in set(f["_platforms"]))
    top = cnt.most_common(12)
    lis = "".join(f'<li><b>{e(p)}</b>: {n} of {len(act)} active firms</li>' for p, n in top)
    return (f'<section class="block prose"><h2>Which platforms prop firms use</h2><p>Counted across the {len(act)} active firms we track, from each firm\'s own platform list:</p><ul class="bul">{lis}</ul>'
            f'<h2>Choosing a platform</h2><p><b>CFD and forex firms</b> mostly run MetaTrader 5, cTrader, Match-Trader or DXtrade. MT5 has the widest indicator and expert-advisor ecosystem; cTrader and Match-Trader are cleaner for manual trading and show depth of market. Many firms dropped MetaTrader after MetaQuotes tightened licensing for prop firms, so check that a MetaTrader offer is current.</p>'
            f'<p><b>Futures firms</b> route through a data and clearing stack (Rithmic, Tradovate, CQG) and let you trade on front ends such as NinjaTrader, Tradovate, Quantower or TradingView. Check which data feed the firm uses, because it decides which front ends work and whether there are monthly data fees.</p>'
            f'<p><b>Crypto exchange firms</b> give you an exchange account or an exchange-priced terminal (for example Bybit) with perpetual futures. Fills, funding rates and liquidation mechanics follow the exchange rather than a CFD broker\'s pricing, which matters for scalpers and for anyone holding positions over funding times.</p>'
            f'<p><b>Two checks before you buy.</b> First, whether the platform is available in your country: some firms block MT5 for US residents while allowing other platforms. Second, whether the platform supports your tools: expert advisors, copy trading and TradingView automation are allowed by some firms and banned by others. Each platform page below lists the firms and links to their rules.</p></section>')
def qw_best_extra():
    lis = "".join(f'<li><a href="{url("/best/" + s + "/")}">{e(BEST_H1.get(s, t))}</a>: {e(d)} <span class="n small">({sum(1 for f in RANKED if not st_is_caution(f) and fn(f))} firms)</span></li>' for s, t, d, fn in BEST)
    return (f'<section class="block prose"><h2>How the best-of lists are built</h2><p>Every list is a filter over the same dataset, then sorted by PA Score. A firm qualifies only on what it publishes on its own site; if a rule is not published, it does not count in the firm\'s favour. Firms with a <a href="{url("/caution/")}">caution</a> are left out of every list, and affiliate deals play no part in membership or order.</p>'
            f'<ul class="bul">{lis}</ul>'
            f'<h2>Reading a list well</h2><p>The top firm in a list is the best match on our published data, not a guarantee for your style. Two things are worth checking on the firm page before you buy: the rule that matters most to you (for example drawdown type for scalpers, or a consistency rule for swing traders), and the date the firm was last verified. Lists rebuild from the data every day, so a rule change moves a firm in or out without anyone deciding it.</p>'
            f'<p>Not sure which list fits? The <a href="{url("/quiz/")}">firm finder</a> asks seven questions and filters the full dataset, and the <a href="{url("/safe/")}">safety checker</a> shows any firm\'s status and evidence in one place.</p></section>')
QW_THIN = {"/sizes/": qw_sizes_extra, "/tools/": qw_tools_extra, "/platforms/": qw_platforms_extra, "/best/": qw_best_extra}
_qw_prev_page4 = page
def page(path, title, desc, body, jsonld=None, og_type="website", extra_head="", lang="en"):
    if path in QW_THIN and "qwthin" not in body:
        blk = QW_THIN[path]().replace('<section class="block prose"', '<section class="block prose qwthin"', 1)
        i = body.rfind("</div>")
        body = body[:i] + blk + body[i:] if i >= 0 else body + blk
    return _qw_prev_page4(path, title, desc, body, jsonld, og_type, extra_head, lang)

