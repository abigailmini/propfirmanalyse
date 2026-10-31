# PropAnalyse score badge (2026-10-31): per-firm SVG badges generated from firms.json (light / dark / auto x standard / compact),
# a <5KB no-cookie JS widget, /badge/ + /zh/badge/ builders, /for-firms/ page, an "Embed this score" block on every firm page,
# and (BADGE_OUTREACH=1) data/badge-outreach.md. Exec'd last into build.py's namespace; wraps page() and seo_files() so it
# survives other modules redefining firm_page(). Stars are a straight mapping of the PA Score: stars = score / 2.
BADGE_V = "1"
BUILD_DAY = datetime.date.today()
STALE_DAYS = 90
PARTNERS = "partners@propanalyse.com"
GH_ISSUES = "https://github.com/abigailmini/propfirmanalyse/issues/new"
MARK_D = open(os.path.join(ROOT, "src", "badge", "mark.path")).read().strip()      # "pa" mark, traced from brand/logo-crop.png (potrace), 141x96 units
MARK_W = 141
STAR_D = re.sub(r"(\d+)\.(\d)\d*", lambda m: str(round(float(m.group(0)))), re.search(r'd="([^"]+)"', ICONS["star"]).group(1))   # Phosphor star (MIT), 256 box, integer coords
FONT = '"Instrument Sans",-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif'
THEMES = {
    "light": dict(bg="#ffffff", line="#d5dae3", ink="#0b1730", mute="#5a6680", acc="#3424f8", mark="#3424f8", off="#d5d9e2"),
    "dark": dict(bg="#18233a", line="#3a4968", ink="#eef1f8", mute="#a3adc4", acc="#9a94ff", mark="#8f88ff", off="#3a4968"),
}
BSIZES = {"standard": (300, 116), "compact": (240, 48)}
BVARIANTS = [(s, t) for s in ("standard", "compact") for t in ("light", "dark", "auto")]
BT3 = chr(96) * 3

def bslug(slug, size="standard", theme="light"):
    return slug + ("-compact" if size == "compact" else "") + ("" if theme == "light" else "-" + theme)
def bsrc(slug, size="standard", theme="light"): return f"{ABS}/badge/{bslug(slug, size, theme)}.svg"
def bhref(f): return f"{ABS}/firms/{f['slug']}/?ref=badge"
def stars_of(s): return round(s / 2, 2)
def bverified(f): return f.get("last_verified") or TODAY
def bstale(f):
    try: return (BUILD_DAY - datetime.date.fromisoformat(str(bverified(f)))).days > STALE_DAYS
    except Exception: return False
def balt(f): return f"{f['name']} on PropAnalyse: PA Score {f['_score']:.1f}/10"
def bcat(f): return CAT_NAME.get(f.get("category"), "") if "CAT_NAME" in globals() else ""

def _css(theme):
    def rules(c): return (f".b{{fill:{c['bg']};stroke:{c['line']}}}.i{{fill:{c['ink']}}}.m{{fill:{c['mute']}}}.a{{fill:{c['acc']}}}"
                          f".k{{fill:{c['mark']}}}.o{{fill:{c['off']}}}")
    base = f"text{{font-family:{FONT}}}"
    if theme == "auto": return base + rules(THEMES["light"]) + "@media (prefers-color-scheme:dark){" + rules(THEMES["dark"]) + "}"
    return base + rules(THEMES[theme])

def _stars(x, y, sz, gap, s):
    """5 empty stars + the same 5 clipped to (score / 10) of the star area (gaps excluded)."""
    k = s / 2; full = int(k); part = k - full
    fillw = full * (sz + gap) + part * sz
    sc = sz / 256
    one = "".join(f'<use href="#s" xlink:href="#s" transform="translate({x + i * (sz + gap):.2f} {y:.2f}) scale({sc:.5f})"/>' for i in range(5))
    return (f'<defs><path id="s" d="{STAR_D}"/><clipPath id="c"><rect x="{x:.2f}" y="{y - 1:.2f}" width="{fillw:.2f}" height="{sz + 2}"/></clipPath></defs>'
            f'<g class="o">{one}</g><g class="a" clip-path="url(#c)">{one}</g>')

def badge_svg(f, size="standard", theme="light"):
    W, H = BSIZES[size]; s = f["_score"]; vd = nice_date(bverified(f))
    title = f"{f['name']} on PropAnalyse: PA Score {s:.1f} out of 10 ({stars_of(s):g} of 5 stars), verified {vd}"
    head = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t">'
            f'<title id="t">{e(title)}</title><style>{_css(theme)}</style>'
            f'<rect class="b" x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="10"/>')
    ver = f"Verified {vd}" + (" \u00b7 re-check due" if bstale(f) else "")
    if size == "compact":
        mk = f'<path class="k" transform="translate(12 13) scale(.225)" d="{MARK_D}"/>'
        body = (f'<text x="52" y="22" class="i" font-size="15" font-weight="700">{s:.1f}<tspan class="m" font-size="11" font-weight="500">/10</tspan></text>'
                + _stars(102, 10.5, 13, 2.5, s) +
                f'<text x="52" y="37" class="m" font-size="10">PropAnalyse \u00b7 {e(ver)}</text>')
        return head + mk + body + "</svg>"
    name = f["name"] if len(f["name"]) <= 26 else f["name"][:25] + "\u2026"
    cat = bcat(f)
    mk = f'<path class="k" transform="translate(16 14) scale(.1875)" d="{MARK_D}"/>'
    body = (f'<text x="47" y="28" class="i" font-size="12.5" font-weight="700" letter-spacing=".1">PropAnalyse</text>'
            + (f'<text x="{W - 16}" y="28" class="m" font-size="11" text-anchor="end">{e(cat)}</text>' if cat else "") +
            f'<text x="16" y="57" class="i" font-size="15.5" font-weight="600">{e(name)}</text>'
            f'<text x="16" y="88" class="i" font-size="28" font-weight="700" letter-spacing="-.4">{s:.1f}<tspan class="m" font-size="13" font-weight="500" letter-spacing="0" dx="2">/10</tspan></text>'
            + _stars(W - 16 - (5 * 17 + 4 * 2.5), 72, 17, 2.5, s) +
            f'<text x="16" y="104" class="m" font-size="10.5">PA Score \u00b7 {e(ver)}</text>')
    return head + mk + body + "</svg>"

def snippet_html(f, size="standard", theme="light"):
    W, H = BSIZES[size]
    return (f'<a href="{bhref(f)}" title="{e(f["name"])} on PropAnalyse"><img src="{bsrc(f["slug"], size, theme)}" width="{W}" height="{H}" '
            f'alt="{e(balt(f))}" loading="lazy" style="border:0;max-width:100%;height:auto"></a>')
def snippet_js(f, size="standard", theme="light"):
    return (f'<a class="propanalyse-badge" data-theme="{theme}" data-size="{size}" href="{bhref(f)}">{e(f["name"])} on PropAnalyse</a>\n'
            f'<script async src="{ABS}/badge/widget.js"></script>')

def badge_data():
    return {"v": 1, "generated": TODAY, "formula": "stars = pa_score / 2", "firms": {f["slug"]: {
        "n": f["name"], "s": f["_score"], "c": bcat(f), "v": bverified(f), "vd": nice_date(bverified(f)), "x": bstale(f), "r": f["_rank"]} for f in FIRMS}}

# ---------------- page pieces ----------------
def _bcss(): return f'<link rel="stylesheet" href="{url("/assets/badge.css")}?v={BADGE_V}">'
def _bjs(): return f'<script src="{url("/assets/badge-page.js")}?v={BADGE_V}" defer></script>'
def codebox(code, label, cid, zh=False):
    btn = "复制代码" if zh else "Copy code"
    return (f'<div class="bcode"><div class="bcode-h"><span id="{cid}-l">{e(label)}</span><button type="button" class="btn line bcopy" data-target="{cid}" data-done="{"已复制" if zh else "Copied"}">'
            f'{ic("copy")}<span>{btn}</span></button></div><pre tabindex="0" aria-labelledby="{cid}-l"><code id="{cid}">{e(code)}</code></pre></div>')

def firm_embed_block(f):
    n = e(f["name"])
    return (f'<section class="block bembed" id="badge"><h2>Embed {n}\u2019s PA Score</h2>'
            f'<p class="small">Run {n}? Put this badge on your site. It is generated from our dataset, so it updates by itself whenever we re-verify, and it always shows the verification date. '
            f'Embedding it, or not, never changes the score. Stars are the score divided by two.</p>'
            f'<div class="bprev duo"><figure class="lt"><img src="{url("/badge/" + f["slug"] + ".svg")}" width="300" height="116" alt="{e(balt(f))}" loading="lazy" decoding="async"><figcaption>Light</figcaption></figure>'
            f'<figure class="dk"><img src="{url("/badge/" + f["slug"] + "-dark.svg")}" width="300" height="116" alt="{e(balt(f))}, dark theme" loading="lazy" decoding="async"><figcaption>Dark</figcaption></figure></div>'
            + codebox(snippet_html(f), "HTML (no JavaScript)", "bc-" + f["slug"]) +
            f'<p class="small blinks"><a href="{url("/badge/")}?firm={f["slug"]}">Compact size, dark theme and JS widget</a><span aria-hidden="true">\u00b7</span>'
            f'<a href="{url("/for-firms/")}">For prop firms: corrections and listings</a></p></section>{_bjs()}')

_badge_prev_page = page
def page(path, title, desc, body, jsonld=None, og_type="website", extra_head="", lang="en"):
    m = re.fullmatch(r"/firms/([^/]+)/", path)
    if m and m.group(1) in BY and 'id="badge"' not in body:
        blk = firm_embed_block(BY[m.group(1)])
        anchor = '<section class="block" id="sources">'
        if anchor in body: body = body.replace(anchor, blk + anchor, 1)
        else:
            i = body.rfind("</div></div></div>")
            body = (body[:i] + blk + body[i:]) if i >= 0 else body + blk
        extra_head = (extra_head or "") + _bcss()
    return _badge_prev_page(path, title, desc, body, jsonld, og_type, extra_head, lang)

# ---------------- /badge/ builder ----------------
L_EN = dict(firm="Firm", theme="Theme", size="Size", kind="Embed type", light="Light", dark="Dark", auto="Auto",
            standard="Standard", compact="Compact", html="HTML image", js="JS widget", preview="Live preview",
            code_html="HTML (no JavaScript, recommended)", code_js="JS widget (optional, under 5 KB, no cookies)", bg="Preview on", bgl="Light page", bgd="Dark page")
L_ZH = dict(firm="交易公司", theme="主题", size="尺寸", kind="嵌入方式", light="浅色", dark="深色", auto="自动",
            standard="标准", compact="紧凑", html="HTML 图片", js="JS 小部件", preview="实时预览",
            code_html="HTML（无需 JavaScript，推荐）", code_js="JS 小部件（可选，小于 5 KB，无 Cookie）", bg="预览背景", bgl="浅色页面", bgd="深色页面")

def _seg(name, opts, cur):
    return '<div class="segs">' + "".join(
        f'<label class="seg"><input type="radio" name="{name}" value="{v}"{" checked" if v == cur else ""}><span>{e(t)}</span></label>' for v, t in opts) + "</div>"

def builder(L, zh=False):
    f0 = BY.get("fundedxyz") or RANKED[0]
    sel = '<select id="b-firm">' + "".join(f'<option value="{f["slug"]}"{" selected" if f is f0 else ""}>{e(f["name"])}</option>' for f in sorted(FIRMS, key=lambda x: x["name"].lower())) + "</select>"
    return f"""<div class="bbuild" id="bbuild" data-abs="{ABS}" data-base="{BASE}">
<form class="bopts" onsubmit="return false">
<label class="fl" for="b-firm"><span>{e(L['firm'])}</span>{sel}</label>
<fieldset><legend>{e(L['theme'])}</legend>{_seg("theme", [("light", L["light"]), ("dark", L["dark"]), ("auto", L["auto"])], "light")}</fieldset>
<fieldset><legend>{e(L['size'])}</legend>{_seg("size", [("standard", L["standard"]), ("compact", L["compact"])], "standard")}</fieldset>
<fieldset><legend>{e(L['kind'])}</legend>{_seg("kind", [("html", L["html"]), ("js", L["js"])], "html")}</fieldset>
<fieldset><legend>{e(L['bg'])}</legend>{_seg("bg", [("l", L["bgl"]), ("d", L["bgd"])], "l")}</fieldset>
</form>
<div class="bout"><p class="blabel">{e(L['preview'])}</p><div class="bstage" id="b-stage" data-bg="l"><a id="b-prev-a" href="{bhref(f0)}"><img id="b-prev" src="{url('/badge/' + f0['slug'] + '.svg')}" width="300" height="116" alt="{e(balt(f0))}"></a></div>
{codebox(snippet_html(f0), L['code_html'], "b-code", zh)}</div></div>
<script>window.PA_BADGES={json.dumps({f['slug']: [f['name'], round(f['_score'], 1)] for f in FIRMS}, ensure_ascii=False, separators=(',', ':'))};window.PA_L={json.dumps({'code_html': L['code_html'], 'code_js': L['code_js']}, ensure_ascii=False)}</script>"""

def _mini_stars(s):
    w = (s / 2) / 5 * 100
    one = ic("star") * 5
    return f'<span class="mstars" role="img" aria-label="{s / 2:g} of 5"><span class="off">{one}</span><span class="on" style="width:{w:.0f}%">{one}</span></span>'
def star_table(zh=False):
    rows = "".join(f'<tr><td class="num n">{s:.1f}</td><td class="num n">{s / 2:g}</td><td>{_mini_stars(s)}</td></tr>' for s in (10, 8.4, 7.5, 6.1, 5.0))
    h = ("PA 评分", "星级", "显示") if zh else ("PA Score", "Stars", "Shown as")
    return f'<table class="mini bstars"><thead><tr><th scope="col" class="num">{h[0]}</th><th scope="col" class="num">{h[1]}</th><th scope="col">{h[2]}</th></tr></thead><tbody>{rows}</tbody></table>'

def gallery(zh=False):
    items = "".join(f'<li><a href="{url("/firms/" + f["slug"] + "/")}#badge"><img src="{url("/badge/" + f["slug"] + ".svg")}" width="300" height="116" alt="{e(balt(f))}" loading="lazy" decoding="async"></a></li>' for f in RANKED)
    return f'<ul class="bgal">{items}</ul>'

def badge_page():
    c, bl = crumbs([("Home", "/"), ("For prop firms", "/for-firms/"), ("Score badge", "/badge/")])
    qa = [("Does embedding the badge change a firm's score or ranking?", "No. The score is computed by the same build script for every firm from published data. Whether a firm embeds the badge, links to us, or has an affiliate deal has no input into the formula."),
          ("How do the stars relate to the PA Score?", "Stars are the PA Score divided by two, drawn to the exact decimal: a score of 8.4 fills 4.2 of 5 stars. There is no rounding up and no separate star rating."),
          ("Does the badge update automatically?", "Yes. The image is regenerated from our dataset on every site build. If a firm's score changes after re-verification, the badge changes too. The verification date is printed on the badge, and badges older than 90 days add \"re-check due\"."),
          ("Does the widget track visitors?", "No. There are no cookies, no analytics and no fingerprinting. The only signal is ?ref=badge on the link, which tells us a click came from a badge."),
          ("Can a firm remove the date or restyle the badge?", "Please don't edit the image. The date is there so visitors can see how fresh the score is. Use the light, dark, auto or compact variants instead.")]
    faqh = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in qa)
    body = f"""<div class="wrap">{c}<header class="ph"><h1>PropAnalyse score badge</h1>
<p class="lede">A free badge prop firms can put on their own site: firm name, PA Score, stars and the date we last verified the data. It links back to the firm's PropAnalyse review and updates itself when we re-check.</p></header>
{builder(L_EN)}
<section class="block prose"><h2>How the stars are calculated</h2>
<p><b>Stars = PA Score \u00f7 2</b>, filled to the exact decimal. Nothing else feeds the stars: no reviews we collect, no payments, no extra weighting. The PA Score itself is explained on the <a href="{url('/methodology/')}">methodology page</a>.</p>{star_table()}</section>
<section class="block prose"><h2>House rules</h2><ul>
<li>Scores and rankings are identical whether or not a firm embeds the badge, links to us or pays us anything.</li>
<li>Every badge prints its verification date. Past 90 days it adds \u201cre-check due\u201d, so a stale score is visible.</li>
<li>The badge is our editorial score, not customer reviews, and we do not publish it as review markup on our own pages.</li>
<li>Prefer the HTML image: no JavaScript, nothing to break. The optional widget is under 5 KB, sets no cookies and loads nothing else.</li>
<li>Found a wrong number? <a href="{url('/for-firms/')}#correct">Send a correction</a> with a link to your own page and we re-verify.</li></ul></section>
<section class="block"><h2>All badges</h2><p class="small">Current light badges for every firm we cover, by PA Score. Click one to open the firm's embed block.</p>{gallery()}</section>
<section class="block faq"><h2>FAQ</h2>{faqh}</section></div>{_bjs()}"""
    ld = [bl, {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]}]
    page("/badge/", "Prop Firm Score Badge: Embed Your PA Score | PropAnalyse", "Free embeddable PropAnalyse score badge for prop firms: PA Score, stars (score \u00f7 2) and verification date. HTML image or a tiny no-cookie widget.", body, ld, extra_head=_bcss())

def zh_badge_page():
    c, bl = crumbs([("首页", "/zh/"), ("评分徽章", "/zh/badge/")])
    qa = [("嵌入徽章会影响评分或排名吗？", "不会。所有公司的评分都由同一个构建脚本根据公开数据计算。是否嵌入徽章、是否链接我们、是否有联盟合作，都不会进入公式。"),
          ("星级和 PA 评分是什么关系？", "星级 = PA 评分 ÷ 2，按精确小数填充：8.4 分即 5 颗星中填满 4.2 颗。没有四舍五入，也没有单独的星级评分。"),
          ("徽章会自动更新吗？", "会。徽章图片在每次网站构建时根据数据集重新生成。重新核实后评分变化，徽章随之变化。徽章上印有核实日期，超过 90 天会加注 \u201cre-check due\u201d（待复核）。"),
          ("小部件会追踪访客吗？", "不会。没有 Cookie、没有统计、没有指纹识别。唯一的信号是链接上的 ?ref=badge，用于知道点击来自徽章。")]
    faqh = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in qa)
    body = f"""<div class="wrap">{c}<header class="ph"><h1>PropAnalyse 评分徽章</h1>
<p class="lede">自营交易公司可以免费放在自己网站上的徽章：公司名称、PA 评分、星级和我们最近一次核实数据的日期。徽章链接回该公司在 PropAnalyse 的评测页，并在我们重新核实后自动更新。徽章图片为英文。</p></header>
{builder(L_ZH, True)}
<section class="block prose"><h2>星级如何计算</h2><p><b>星级 = PA 评分 ÷ 2</b>，按精确小数填充。星级不受任何其他因素影响：没有我们收集的评论、没有付费、没有额外加权。PA 评分本身的算法见<a href="{url('/zh/methodology/')}">评分方法</a>。</p>{star_table(True)}</section>
<section class="block prose"><h2>规则</h2><ul><li>无论公司是否嵌入徽章、链接我们或向我们付费，评分和排名完全相同。</li>
<li>每个徽章都印有核实日期；超过 90 天会显示 \u201cre-check due\u201d，过期评分一目了然。</li>
<li>徽章是我们的编辑评分，不是用户评价，我们不会在自己的页面上把它标记为评价结构化数据。</li>
<li>推荐使用 HTML 图片：无需 JavaScript。可选小部件小于 5 KB，不设置 Cookie，不加载任何其他资源。</li>
<li>发现数据有误？<a href="{url('/for-firms/')}#correct">提交更正</a>（英文页面），附上贵公司官网页面链接，我们会重新核实。</li></ul></section>
<section class="block"><h2>全部徽章</h2>{gallery(True)}</section>
<section class="block faq"><h2>常见问题</h2>{faqh}</section></div>{_bjs()}"""
    ld = [bl, {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]}]
    page("/zh/badge/", "自营交易公司评分徽章：嵌入 PA 评分 | PropAnalyse", "PropAnalyse 免费评分徽章：PA 评分、星级（评分 ÷ 2）和核实日期。HTML 图片或无 Cookie 小部件。", body, ld, extra_head=_bcss(), lang="zh")

# ---------------- /for-firms/ ----------------
def for_firms_page():
    c, bl = crumbs([("Home", "/"), ("For prop firms", "/for-firms/")])
    f0 = RANKED[0]
    opts = "".join(f'<option value="{e(f["name"])}"></option>' for f in sorted(FIRMS, key=lambda x: x["name"].lower()))
    body = f"""<div class="wrap">{c}<header class="ph"><h1>For prop firms</h1>
<p class="lede">How your firm is listed on PropAnalyse, how to show your score on your own site, and how to fix a number we have wrong. No account, no fees.</p></header>
<div class="ffgrid">
<section class="block prose"><h2>How you are listed</h2><p>Every figure on your page is read from your own website: pricing, rules, FAQ and help-centre pages. Each firm page lists the pages it came from and the date we checked them. If you do not publish something, we show \u201cNot published\u201d rather than guess.</p>
<p>The PA Score is one formula applied to every firm by our build script (<a href="{url('/methodology/')}">methodology</a>). You cannot pay to change it, and affiliate deals have no input into it. PropAnalyse is run by the team behind FundedXyz, which is scored by the same rules.</p></section>
<section class="block prose"><h2>Show your score</h2><p>Copy a badge for your site from your firm page or the <a href="{url('/badge/')}">badge builder</a>. It shows your PA Score, stars (score \u00f7 2) and our verification date, and it updates by itself.</p>
<p class="bsample"><img src="{url('/badge/' + f0['slug'] + '.svg')}" width="300" height="116" alt="Example badge: {e(balt(f0))}" loading="lazy"></p>
<p><a class="btn" href="{url('/badge/')}">Get your badge</a></p></section></div>
<section class="block" id="correct"><h2>Correct your data or request a listing</h2>
<p class="small">Fill this in and send it by email or as a public GitHub issue. Nothing is stored on our side; the form only prepares the message. Include a link to the page on your site that shows the correct figure: we only change data we can see on the firm's own pages.</p>
<form class="cform ffform" id="ffform" onsubmit="return false" data-to="{PARTNERS}" data-gh="{GH_ISSUES}">
<label class="fl" for="ff-type"><span>Request</span><select id="ff-type"><option value="Data correction">Correct existing data</option><option value="New listing">List a new firm</option><option value="Badge help">Badge help</option><option value="Other">Other</option></select></label>
<label class="fl" for="ff-firm"><span>Firm</span><input id="ff-firm" list="ff-firms" autocomplete="organization" placeholder="Firm name"><datalist id="ff-firms">{opts}</datalist></label>
<label class="fl" for="ff-field"><span>What is wrong or missing</span><input id="ff-field" placeholder="e.g. Max drawdown, 2-step 100K"></label>
<label class="fl" for="ff-value"><span>Correct value</span><input id="ff-value" placeholder="e.g. 10% static"></label>
<label class="fl wide" for="ff-src"><span>Source URL on your site</span><input id="ff-src" type="url" inputmode="url" placeholder="https://"></label>
<label class="fl wide" for="ff-notes"><span>Notes</span><textarea id="ff-notes" rows="3" placeholder="Anything else we should check"></textarea></label>
<div class="ffact wide"><a class="btn" id="ff-mail" href="mailto:{PARTNERS}">Send by email</a><a class="btn line" id="ff-gh" href="{GH_ISSUES}" rel="noopener" target="_blank">Open a GitHub issue</a></div>
</form><p class="small">Or write to <a href="mailto:{PARTNERS}">{PARTNERS}</a> directly. Corrections that check out go into the next build and show up in the <a href="{url('/updates/')}">verification log</a>.</p></section>
<section class="block prose"><h2>Request a listing</h2><p>We list firms that publish their rules and pricing publicly. Send your rules page, pricing page and payout policy with the form above (choose \u201cList a new firm\u201d). We read everything ourselves and add the firm once the core fields can be verified from your site.</p></section>
<section class="block prose"><h2>Partnerships</h2><p>Affiliate links and partnerships: <a href="mailto:{PARTNERS}">{PARTNERS}</a>. They are disclosed, they never touch scores or ordering, and outbound firm links are marked sponsored.</p></section></div>{_bjs()}"""
    page("/for-firms/", "For Prop Firms: Badge, Corrections & Listings | PropAnalyse", "Prop firms: embed your PropAnalyse score badge, correct your data with a source link, or request a listing. Scores cannot be bought.", body, [bl], extra_head=_bcss())

# ---------------- files ----------------
def write_badges():
    d = os.path.join(OUT, "badge"); os.makedirs(d, exist_ok=True)
    for f in FIRMS:
        for size, theme in BVARIANTS:
            open(os.path.join(d, bslug(f["slug"], size, theme) + ".svg"), "w").write(badge_svg(f, size, theme))
    json.dump(badge_data(), open(os.path.join(d, "badges.json"), "w"), ensure_ascii=False, separators=(",", ":"))
    w = open(os.path.join(ROOT, "src", "badge", "widget.js")).read().replace("__ABS__", ABS).replace("__MARK__", MARK_D).replace("__STAR__", STAR_D)
    open(os.path.join(d, "widget.js"), "w").write(w)
    open(os.path.join(d, "mark.svg"), "w").write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {MARK_W} 96"><path fill="#3424f8" d="{MARK_D}"/></svg>')
    for n in ("badge.css", "badge-page.js"):
        shutil.copy(os.path.join(ROOT, "src", "badge", n), os.path.join(OUT, "assets", n))

def outreach_md():
    N = len(FIRMS); out = ["# PropAnalyse badge outreach kit", "",
        f"Generated {BUILD_DAY.isoformat()} from data/firms.json (scores as of the {TODAY} dataset). Regenerate with: BADGE_OUTREACH=1 python3 scripts/build.py",
        f"Send from {PARTNERS}. Find each firm's partnerships/support address on their contact page. Never promise a score change; corrections need a source link on their own site.", ""]
    for f in RANKED:
        comp = max(f["_comp"].items(), key=lambda kv: kv[1]); cname = COMP_LABEL[comp[0]][0].lower()
        P, _ = pros_cons(f)
        hook = (P[0][0].lower() + P[0][1:]) if P else f"{cname} is your strongest area"
        own = f["slug"] == "fundedxyz"
        out += [f"## {f['name']} (PA {f['_score']:.1f}/10, #{f['_rank']} of {N}, {bcat(f) or 'n/a'})", ""]
        if own: out += ["> Own firm (disclosed on the site). No email needed: hand the snippet to whoever runs fundedxyz.com. Same score rules apply.", ""]
        out += [f"**To:** partnerships / support contact on {f.get('site') or 'their site'}", "",
                f"**Subject:** {f['name']}: PA Score {f['_score']:.1f}/10 on PropAnalyse (free badge for your site)", "",
                f"Hi {f['name']} team, PropAnalyse covers {f['name']} in our {CAT_LOW.get(f.get('category'), 'prop firm') if 'CAT_LOW' in globals() else 'prop firm'} prop firm comparison: PA Score {f['_score']:.1f}/10, #{f['_rank']} of {N} firms, every figure sourced from your own pages (last verified {nice_date(bverified(f))}).",
                f"Your strongest component is {cname} ({comp[1]:.1f}/10), and one thing traders notice: {hook}.",
                f"If you'd like to show it, the badge below is free and updates automatically when we re-verify; embedding it never affects the score, and if any figure is out of date just reply with a link to your page and we'll re-check.", "",
                f"Review: {ABS}/firms/{f['slug']}/  |  Sizes/themes: {ABS}/badge/?firm={f['slug']}", "", BT3 + "html", snippet_html(f), BT3, "",
                f"PropAnalyse team, {PARTNERS}", "", "---", ""]
    open(os.path.join(ROOT, "data", "badge-outreach.md"), "w").write("\n".join(out))

FOOT_EXTRA.append(("/for-firms/", "For prop firms"))
FOOT_EXTRA.append(("/badge/", "Score badge"))
ZH_FOOT.append(("/zh/badge/", "评分徽章"))
ZH_ALT["/badge/"] = "/zh/badge/"

_badge_prev_seo = seo_files
def seo_files():
    write_badges(); badge_page(); zh_badge_page(); for_firms_page()
    if os.environ.get("BADGE_OUTREACH") == "1": outreach_md()
    _badge_prev_seo()
    p = os.path.join(OUT, "llms.txt")
    if os.path.exists(p):
        open(p, "a").write(f"\n## For prop firms\n- [Score badge]({ABS}/badge/): embeddable PA Score badge per firm (SVG at {ABS}/badge/<slug>.svg; stars = PA Score / 2; shows verification date)\n"
                           f"- [For prop firms]({ABS}/for-firms/): corrections (source link required), listing requests, partnerships ({PARTNERS})\n- [Badge data (JSON)]({ABS}/badge/badges.json)\n")
