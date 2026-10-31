# PropAnalyse analytics + outbound click tracking (exec'd last by build.py).
# Always: writes backend/src/firms.gen.json (slug -> official site / affiliate URL for the Worker) and /privacy/.
# Only with TRACK=1 (set once the Worker answers on GO_URL with 302s):
#   - every firm "Visit" / affiliate / promo link and firm-homepage link -> GO_URL/<slug>?src=<page>&pos=<slot>[&code=]
#     rel="sponsored nofollow noopener" when the firm has an affiliate_url, else "nofollow noopener"
#   - cookieless beacon /assets/a.js on every page (pageviews, promo copies, other outbound clicks)
#   - complaint / correction forms POST to GO_URL/f first, keeping the e-mail / GitHub fallback
import urllib.parse as _up
PA_TRACK = os.environ.get("TRACK", "") in ("1", "true", "yes")
GO_URL = os.environ.get("GO_URL", "https://go.propanalyse.com").rstrip("/")
PA_TRACK_V = "1"
FOOT_EXTRA.append(("/privacy/", "Privacy"))

def _aff(f):
    a = f.get("affiliate_url")
    return a if a and a != "#" and str(a).startswith("http") else None

def _host(u):
    try: return _up.urlsplit(u).hostname.lower().removeprefix("www.")
    except Exception: return None

def write_firm_map():
    m = {f["slug"]: {"name": f["name"], "site": f.get("site") or None, "aff": _aff(f)} for f in FIRMS}
    d = os.path.join(ROOT, "backend", "src"); os.makedirs(d, exist_ok=True)
    s = json.dumps({"generated": TODAY, "firms": m}, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    p = os.path.join(d, "firms.gen.json")
    if not os.path.exists(p) or open(p).read() != s: open(p, "w").write(s)

def privacy():
    c, bl = crumbs([("Home", "/"), ("Privacy", "/privacy/")])
    state = ("" if PA_TRACK else '<p class="note"><b>Status:</b> the analytics described here are being set up and are not switched on yet. Until they are, the site collects nothing at all.</p>')
    body = f"""<div class="wrap">{c}<article class="prose"><h1>Privacy notice</h1>
<p class="lede">PropAnalyse uses no cookies, no advertising trackers, no Google Analytics and no fingerprinting. We count visits and outbound clicks with our own small, cookieless analytics so we know which pages are useful and which firm links readers use.</p>{state}
<h2>What we count</h2><ul class="bul">
<li><b>Page views:</b> the page address, the referring website's domain (not the full URL), any utm campaign tags in the link, page language, device class (mobile, tablet or desktop, worked out from your browser's user-agent) and country (from Cloudflare's network, never anything finer than country).</li>
<li><b>Outbound clicks:</b> when you use a "Visit" or offer link, it passes through <code>go.propanalyse.com</code>, which records the firm, the page and the spot on the page the click came from, the promo code shown next to the link (if any), country and device class, then sends you straight on to the firm's site. Affiliate links are marked <code>rel="sponsored"</code>.</li>
<li><b>Promo code copies</b> and clicks on other external links (for example a firm's rule page we cite): the firm, the code and the destination domain.</li></ul>
<h2>What we do not collect</h2><ul class="bul"><li>No cookies, local storage or any identifier stored on your device.</li><li>No IP addresses: your IP address and browser user-agent are combined with a random value that changes every day and is deleted after 48 hours, then hashed. The result can tell "same visitor today" apart from "new visitor today" but cannot be reversed or linked across days.</li><li>No names, e-mail addresses, account numbers or anything you type, except in forms you choose to submit.</li><li>No data is sold or shared with advertisers. Prop firms do not get our analytics.</li></ul>
<h2>Do Not Track and Global Privacy Control</h2><p>If your browser sends Do Not Track or Global Privacy Control, the page-view script does not run at all. Outbound clicks still redirect you, but are counted without the daily visitor hash.</p>
<h2>Forms</h2><p>If you submit a complaint, a data correction or a listing request, we store what you typed (including your e-mail if you give it) so we can follow up, and may forward it to our inbox by e-mail. Complaints are never published with your e-mail or account ID. You can instead send any form by e-mail or as a GitHub issue. To have a submission deleted, e-mail us with its subject line.</p>
<h2>Where it is stored</h2><p>On Cloudflare (Workers and the D1 database). Raw analytics rows are deleted after about 13 months; only totals are kept after that.</p>
<h2>Contact</h2><p>Questions or deletion requests: see <a href="{url('/about/')}">About</a> or use the <a href="{url('/for-firms/')}">contact form</a>.</p>
<p class="small">Last updated <time datetime="2026-10-31">31 October 2026</time>.</p></article></div>"""
    page("/privacy/", "Privacy Notice: Cookieless Analytics | PropAnalyse", "PropAnalyse uses cookieless analytics with no IP storage: what we count, what we do not, and how Do Not Track is respected.", body, [bl])

BEACON_JS = r"""/* PropAnalyse cookieless analytics: no cookies, no storage, skips DNT/GPC. See /privacy/ */
(function(){var n=navigator,w=window,d=document,E="__GO__/e";if(n.doNotTrack=="1"||w.doNotTrack=="1"||n.globalPrivacyControl)return;
function s(o){o.p=location.pathname;o.l=d.documentElement.lang||"";var b=JSON.stringify(o);try{if(!(n.sendBeacon&&n.sendBeacon(E,b)))fetch(E,{method:"POST",body:b,keepalive:true,credentials:"omit"})}catch(e){}}
var r="";try{r=d.referrer?new URL(d.referrer).hostname:""}catch(e){}if(r==location.hostname)r="";
var q=new URLSearchParams(location.search);s({t:"pv",r:r,us:q.get("utm_source")||q.get("ref")||"",um:q.get("utm_medium")||"",uc:q.get("utm_campaign")||""});
d.addEventListener("click",function(e){var a=e.target.closest&&e.target.closest("[data-copy],a[href]");if(!a)return;
if(a.dataset.copy!=null){var c=a.closest("[data-firm],article,tr,li,section"),f=c&&(c.dataset.firm||(c.querySelector("[data-firm]")||{dataset:{}}).dataset.firm);
if(!f&&c){var h=c.querySelector('a[href*="/firms/"]'),m=h&&h.getAttribute("href").match(/\/firms\/([a-z0-9-]+)/);f=m?m[1]:""}s({t:"copy",f:f||"",c:a.dataset.copy});return}
if(/^https?:$/.test(a.protocol)&&a.hostname!=location.hostname&&E.indexOf("//"+a.hostname+"/")<0)s({t:"out",h:a.hostname,f:a.dataset.firm||""})},true)})();
"""

FORMS_JS = r"""/* PropAnalyse forms: send straight to PropAnalyse; e-mail / GitHub stay as fallback. */
(function(){var $=function(s,r){return(r||document).querySelector(s)};
function go(F,cfg){var api=F.dataset.api;if(!api)return;var act=$(cfg.act,F),zh=F.dataset.lang=="zh";
var b=document.createElement("button");b.type="button";b.className="btn";b.textContent=zh?"直接提交":"Send to PropAnalyse";act.insertBefore(b,act.firstChild);
var m=document.createElement("p");m.className="small";m.setAttribute("aria-live","polite");act.parentNode.insertBefore(m,act.nextSibling);
var hp=document.createElement("input");hp.name="website";hp.tabIndex=-1;hp.autocomplete="off";hp.style.cssText="position:absolute;left:-9999px";hp.setAttribute("aria-hidden","true");F.appendChild(hp);
var v=function(i){var e=$("#"+i);return e?(e.value||"").trim():""};
b.addEventListener("click",function(){var miss=cfg.req.filter(function(i){var e=$("#"+i);if(!e)return false;var bad=e.type=="checkbox"?!e.checked:!v(i)||(e.type=="email"&&!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(v(i)));e.setAttribute("aria-invalid",bad?"true":"false");return bad});
if(miss.length){m.textContent=zh?"请填写标记的必填项。":"Please fill in the highlighted required fields.";$("#"+miss[0]).focus();return}
var fl={};cfg.ids.forEach(function(i){var e=$("#"+i);if(!e)return;var o=e.options&&e.selectedIndex>=0?e.options[e.selectedIndex]:null;fl[i.replace(/^[a-z]+-/,"")]=o?(o.dataset.en||o.textContent)+(e.value&&e.value!=o.textContent?" ("+e.value+")":""):e.type=="checkbox"?(e.checked?"yes":"no"):v(i)});
var body={kind:cfg.kind(),firm:v(cfg.firm),email:v(cfg.email||""),fields:fl,page:location.pathname,lang:document.documentElement.lang,hp:hp.value};
b.disabled=true;m.textContent=zh?"发送中…":"Sending…";
fetch(api,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body),credentials:"omit"}).then(function(r){return r.json().then(function(j){if(!r.ok||!j.ok)throw j;return j})})
.then(function(j){m.textContent=(zh?"已收到，编号 #":"Received, reference #")+j.id+(zh?"。我们会尽快核实。":". We will check it and follow up.");b.textContent=zh?"已发送":"Sent"})
.catch(function(){b.disabled=false;m.textContent=zh?"暂时无法连接服务器，请改用下面的邮件或 GitHub。":"Could not reach our server. Please use the e-mail or GitHub option instead."})})}
var C=$("#cpform");if(C)go(C,{act:".cpact",req:["cp-firm","cp-type","cp-email","cp-desc","cp-ok"],ids:["cp-firm","cp-type","cp-acct","cp-date","cp-desc","cp-ev","cp-ok"],firm:"cp-firm",email:"cp-email",kind:function(){return"complaint"}});
var G=$("#ffform");if(G)go(G,{act:".ffact",req:["ff-firm"],ids:["ff-type","ff-firm","ff-field","ff-value","ff-src","ff-notes"],firm:"ff-firm",kind:function(){var t=(($("#ff-type")||{}).value||"").toLowerCase();return/listing/.test(t)?"listing":/status/.test(t)?"status-review":/correction/.test(t)?"correction":"other"}})})();
"""

_A_RE = re.compile(r"<a\b[^>]*>")
def _attr(tag, name):
    m = re.search(r'\s' + name + r'="([^"]*)"', tag); return html.unescape(m.group(1)) if m else None
def _set_attr(tag, name, val):
    v = html.escape(val, quote=True)
    if re.search(r'\s' + name + r'="', tag): return re.sub(r'(\s' + name + r')="[^"]*"', lambda m: m.group(1) + '="' + v + '"', tag, count=1)
    return tag[:-1] + f' {name}="{v}">'

def _slot(t, i, path, cls):
    pre = t[max(0, i - 6000):i]
    def inside(op, cl):
        a = pre.rfind(op); return a >= 0 and a > pre.rfind(cl)
    if path.startswith("/compare/") or path.startswith("/zh/compare/"): return "compare"
    if inside('class="ocard', "</article>"): return "offer-card"
    if inside("<tr", "</tr>"): return "table"
    if re.match(r"^/(zh/)?(firms|crypto)/[a-z0-9-]+/$", path) and "btn" in cls: return "firm-page"
    if "visit" in cls: return "list"
    if "btn" in cls: return "cta"
    return "text"

def _code(t, i):
    pre = t[max(0, i - 6000):i]
    for op, cl in (('class="ocard', "</article>"), ("<tr", "</tr>")):
        a = pre.rfind(op)
        if a >= 0 and a > pre.rfind(cl):
            start = i - len(pre) + a; end = t.find(cl, i)
            m = re.search(r'data-copy="([^"]+)"', t[start:end if end > 0 else i + 3000])
            return html.unescape(m.group(1)) if m else ""
    return ""

def track_rewrite():
    by_host = {}
    for f in FIRMS:
        h = _host(f.get("site") or "")
        if h: by_host.setdefault(h, f["slug"])
    BYS = {f["slug"]: f for f in FIRMS}
    open(os.path.join(OUT, "assets", "a.js"), "w").write(BEACON_JS.replace("__GO__", GO_URL))
    open(os.path.join(OUT, "assets", "f.js"), "w").write(FORMS_JS)
    tag_a = f'<script src="{url("/assets/a.js")}?v={PA_TRACK_V}" defer></script>'
    tag_f = f'<script src="{url("/assets/f.js")}?v={PA_TRACK_V}" defer></script>'
    stats = {"pages": 0, "links": 0}
    for dp, _, fs in os.walk(OUT):
        for fn in fs:
            if not fn.endswith(".html"): continue
            fp = os.path.join(dp, fn); rel = os.path.relpath(fp, OUT).replace(os.sep, "/")
            path = "/" + (rel[:-len("index.html")] if rel.endswith("index.html") else rel)
            t = open(fp).read()
            if "</body>" not in t: continue
            def sub(m):
                tag = m.group(); href = _attr(tag, "href") or ""
                if not href.startswith("http"): return tag
                slug = _attr(tag, "data-firm")
                if not slug:
                    sp = _up.urlsplit(href); h = (sp.hostname or "").lower().removeprefix("www.")
                    if h in by_host and sp.path in ("", "/") and not sp.query: slug = by_host[h]
                if not slug or slug not in BYS: return tag
                cls = _attr(tag, "class") or ""
                q = {"src": path, "pos": _slot(t, m.start(), path, cls)}
                code = _code(t, m.start())
                if code: q["code"] = code
                tag = _set_attr(tag, "href", f"{GO_URL}/{slug}?" + _up.urlencode(q, safe="/"))
                tag = _set_attr(tag, "rel", "sponsored nofollow noopener" if _aff(BYS[slug]) else "nofollow noopener")
                if not _attr(tag, "data-firm"): tag = _set_attr(tag, "data-firm", slug)
                stats["links"] += 1
                return tag
            t = _A_RE.sub(sub, t)
            extra = tag_a
            if 'id="cpform"' in t or 'id="ffform"' in t:
                t = t.replace('id="cpform"', f'id="cpform" data-api="{GO_URL}/f"').replace('id="ffform"', f'id="ffform" data-api="{GO_URL}/f"'); extra += tag_f
            t = t.replace("</body>", extra + "</body>", 1)
            open(fp, "w").write(t); stats["pages"] += 1
    print(f"TRACK=1: {stats['links']} outbound firm links -> {GO_URL}, beacon on {stats['pages']} pages")

def track_finalize():
    write_firm_map()
    if PA_TRACK: track_rewrite()
