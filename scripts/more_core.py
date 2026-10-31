# PropAnalyse: page types added 2026-10-26 (reviews, offers, crypto, news, tools, quiz, guides, glossary, FAQ).
# Exec'd into build.py's namespace, so every helper there (page, crumbs, e, money, ...) is available here.
import subprocess

ICONS["plus"] = '<path d="M224,128a8,8,0,0,1-8,8H136v80a8,8,0,0,1-16,0V136H40a8,8,0,0,1,0-16h80V40a8,8,0,0,1,16,0v80h80A8,8,0,0,1,224,128Z"/>'
ICONS["minus"] = '<path d="M224,128a8,8,0,0,1-8,8H40a8,8,0,0,1,0-16H216A8,8,0,0,1,224,128Z"/>'
ICONS["rss"] = '<path d="M106.91,149.09A71.53,71.53,0,0,1,128,200a8,8,0,0,1-16,0,56.06,56.06,0,0,0-56-56,8,8,0,0,1,0-16A71.53,71.53,0,0,1,106.91,149.09ZM56,80a8,8,0,0,0,0,16A104.11,104.11,0,0,1,160,200a8,8,0,0,0,16,0A120.13,120.13,0,0,0,56,80Zm118.79,1.21A166.9,166.9,0,0,0,56,32a8,8,0,0,0,0,16A151,151,0,0,1,163.48,92.52,151,151,0,0,1,208,200a8,8,0,0,0,16,0A166.9,166.9,0,0,0,174.79,81.21ZM60,184a12,12,0,1,0,12,12A12,12,0,0,0,60,184Z"/>'

T.update({"nav_crypto": "Crypto", "nav_offers": "Offers", "nav_tools": "Tools", "nav_news": "Rule changes", "nav_guides": "Guides"})
T["tagline"] = "The prop firm audit. Published scoring, dated rule changes, true cost to first payout."
NAV[:] = [("/firms/", "nav_firms"), ("/crypto/", "nav_crypto"), ("/compare/", "nav_compare"), ("/offers/", "nav_offers"), ("/tools/", "nav_tools"),
          ("/news/", "nav_news"), ("/guides/", "nav_guides"), ("/methodology/", "nav_method")]
FOOT_EXTRA = [("/quiz/", "Find your firm"), ("/faq/", "FAQ"), ("/glossary/", "Glossary"), ("/about/", "About"), ("/updates/", "Verification log"), ("/news/feed.xml", "RSS: rule changes")]
NOINDEX = set()

# ---------- overlays: data/extra/<slug>.json (costs, refunds, time limits) and data/crypto/<slug>.json ----------
def _load_dir(d):
    out = {}
    p = os.path.join(ROOT, "data", d)
    if os.path.isdir(p):
        for n in sorted(os.listdir(p)):
            if n.endswith(".json"):
                try: out[n[:-5]] = json.load(open(os.path.join(p, n)))
                except Exception as ex: print("skip overlay", d, n, ex)
    return out
EXTRA, CRYPTO = _load_dir("extra"), _load_dir("crypto")
for f in FIRMS:
    if f["slug"] in EXTRA: f["extra"] = EXTRA[f["slug"]]
    if f["slug"] in CRYPTO: f["crypto"] = CRYPTO[f["slug"]]
    f["_x"] = f.get("extra") or {}; f["_c"] = f.get("crypto") or {}
CRYPTO_FIRMS = [f for f in RANKED if "crypto" in f["_assets"]]
def is_native(f): return f.get("segment", f.get("category")) in ("crypto", "crypto-exchange") or f["_assets"] == ["crypto"]   # segment = pre-2026-10-31 asset-mix label

def pct_off(dc):
    m = re.search(r"(\d+(?:\.\d+)?)\s*%\s*off", str((dc or {}).get("value") or ""), re.I)
    return float(m.group(1)) if m else None

def first_num_pct(s):
    v = first_pct(s); return v

# ---------- changelog: every change to a tracked firm field is logged with a date ----------
SNAP_V = 2
TRACK = [("challenge_types", "Challenge types"), ("account_sizes", "Account sizes"), ("fee_from", "Fee from"), ("profit_target", "Profit target"),
         ("max_daily_loss", "Daily loss limit"), ("max_drawdown", "Max drawdown"), ("drawdown_type", "Drawdown type"), ("profit_split", "Profit split"),
         ("profit_split_scale", "Split scaling"), ("leverage", "Leverage"), ("platforms", "Platforms"), ("payout_frequency", "Payout frequency"),
         ("first_payout_days", "First payout (days)"), ("min_trading_days", "Min trading days"), ("consistency_rule", "Consistency rule"),
         ("news_trading", "News trading"), ("weekend_holding", "Weekend holding"), ("countries_restricted", "Restricted countries"), ("assets", "Markets")]
PTRACK = [("profit_target", "profit target"), ("max_daily_loss", "daily loss"), ("max_drawdown", "max drawdown"), ("drawdown_type", "drawdown type"),
          ("profit_split", "split"), ("min_trading_days", "min days")]
XTRACK = [("reset_fee", "Reset / retry"), ("refund_policy", "Fee refund"), ("time_limit", "Time limit"), ("activation_fee", "Activation fee"), ("min_payout", "Minimum payout")]
CTRACK = [("crypto_leverage", "Crypto leverage"), ("crypto_venue", "Crypto venue"), ("crypto_pairs", "Crypto pairs"), ("weekend_crypto", "Weekend crypto"), ("bots_allowed", "Bots")]
def _sv(v):
    if v in (None, "", [], {}): return None
    if isinstance(v, bool): return "Allowed" if v else "Not allowed"
    if isinstance(v, list): return ", ".join(money(num(x)) if isinstance(x, (int, float)) and x >= 1000 else str(x) for x in v)
    if isinstance(v, float) and v.is_integer(): v = int(v)
    return str(v)
def flat(f):
    o = {}
    for k, lab in TRACK: o[lab] = _sv(f.get(k))
    for p in as_list(f.get("programs")):
        pn = p.get("name") or p.get("type") or "Program"
        for k, lab in PTRACK: o[f"{pn}: {lab}"] = _sv(p.get(k))
        for sf in as_list(p.get("sizes_fees")):
            if num(sf.get("size")): o[f"{pn}: {money(num(sf['size']))} fee"] = _sv(sf.get("fee"))
    dc = f.get("discount_code") or {}
    o["Discount code"] = (dc.get("code") + (" (" + dc["value"] + ")" if dc.get("value") else "")) if dc.get("code") else None
    tp = f.get("trustpilot") or {}
    o["Trustpilot score"] = _sv(tp.get("score"))
    for k, lab in XTRACK: o["x:" + lab] = _sv((f.get("extra") or {}).get(k))
    for k, lab in CTRACK: o["c:" + lab] = _sv((f.get("crypto") or {}).get(k))
    return {k: v for k, v in o.items() if v is not None}
def kind_of(field):
    fl = field.lower()
    if "fee" in fl or "reset" in fl or "refund" in fl or "activation" in fl: return "Fees"
    if "split" in fl or "payout" in fl: return "Payouts"
    if "code" in fl: return "Offers"
    if "trustpilot" in fl: return "Reputation"
    if "listing" in fl: return "Listing"
    return "Rules"
def diff_sets(old, new, date, names, src=None):
    out = []
    for slug in sorted(set(old) | set(new)):
        nm = names.get(slug, slug)
        if slug not in old:
            out.append({"date": date, "slug": slug, "firm": nm, "field": "Listing", "old": None, "new": "Added to PropAnalyse", "kind": "Listing"}); continue
        if slug not in new:
            out.append({"date": date, "slug": slug, "firm": nm, "field": "Listing", "old": "Listed", "new": "Removed from PropAnalyse", "kind": "Listing"}); continue
        a, b = old[slug], new[slug]
        for k in sorted(set(a) | set(b)):
            if a.get(k) != b.get(k):
                if a.get(k) is None and k.startswith(("x:", "c:")): continue  # first capture of an overlay field is not a firm change
                out.append({"date": date, "slug": slug, "firm": nm, "field": k.split(":", 1)[1] if k[:2] in ("x:", "c:") else k,
                            "old": a.get(k), "new": b.get(k), "kind": kind_of(k)})
    return out
CL_PATH = os.path.join(ROOT, "data", "changelog.json"); SNAP_PATH = os.path.join(ROOT, "data", "snapshot.json")
def git_backfill():
    """First run: rebuild history from git commits of data/firms.json (first verified dataset = baseline)."""
    try:
        log = subprocess.run(["git", "-C", ROOT, "log", "--reverse", "--format=%h %ad", "--date=short", "--", "data/firms.json"], capture_output=True, text=True, check=True).stdout.split("\n")
    except Exception: return [], None
    commits = [l.split() for l in log if l.strip()]
    prev, out = None, []
    for h, d in commits:
        try: data = json.loads(subprocess.run(["git", "-C", ROOT, "show", f"{h}:data/firms.json"], capture_output=True, text=True, check=True).stdout)
        except Exception: continue
        if len(data.get("firms", [])) < 15: continue  # skip the partial seed commit
        cur = {x["slug"]: flat(x) for x in data["firms"]}; names = {x["slug"]: x["name"] for x in data["firms"]}
        if prev is not None: out += diff_sets(prev[0], cur, d, {**prev[1], **names})
        prev = (cur, names)
    return out, prev
def changelog():
    names = {f["slug"]: f["name"] for f in FIRMS}
    cur = {f["slug"]: flat(f) for f in FIRMS}
    cl = json.load(open(CL_PATH)) if os.path.exists(CL_PATH) else None
    snap = json.load(open(SNAP_PATH)) if os.path.exists(SNAP_PATH) else None
    if cl is None:
        cl, prev = git_backfill()
        snap = {"v": 1, "firms": prev[0]} if prev else {"v": SNAP_V, "firms": cur}
    if snap:
        new = diff_sets(snap["firms"], cur, TODAY, {**names}, "rebaseline" if snap.get("v") != SNAP_V else None)
        names_old = {}
        for x in new:
            if x["field"] == "Listing" and x["slug"] not in names: x["firm"] = x["slug"].replace("-", " ").title()
        cl += new
    json.dump(cl, open(CL_PATH, "w"), indent=1, ensure_ascii=False)
    json.dump({"v": SNAP_V, "date": TODAY, "firms": cur}, open(SNAP_PATH, "w"), indent=1, ensure_ascii=False)
    return sorted(cl, key=lambda x: (x["date"], x["firm"]), reverse=True)

# ---------- review building blocks ----------
def pros_cons(f):
    P, C = [], []
    x = f["_x"]
    cpk = cost_per_k(f); cur = f.get("fee_currency")
    if f["_split"] and f["_split"] >= 90: P.append(f"Split can reach {f['_split']:.0f}%" + (" (see scaling terms)" if f.get("profit_split_scale") else ""))
    if cpk is not None and cpk <= 5: P.append(f"Low cost per $1K of buying power: {money(cpk, cur)}")
    elif cpk is not None and cpk >= 9: C.append(f"Expensive per $1K of account: {money(cpk, cur)} at best")
    if f["_bucket"] in ("daily", "weekly"): P.append(f"{BUCKET_LABEL[f['_bucket']]} payout cycle on the headline plan")
    elif f["_bucket"] == "monthly": C.append("Monthly payout cycle on the headline plan")
    fd = num(f.get("first_payout_days"))
    if fd is not None and fd <= 7: P.append(f"First payout possible after {int(fd)} days")
    elif fd is not None and fd >= 21: C.append(f"Wait {int(fd)} days for the first payout")
    nt = tri(f.get("news_trading")); wk = tri(f.get("weekend_holding"))
    if nt is True: P.append("News trading allowed")
    elif nt is False: C.append("No trading around high-impact news")
    elif nt == "restricted": C.append("News trading restricted on some programs")
    if wk is True: P.append("Positions can be held over the weekend")
    elif wk is False: C.append("Weekend holding not allowed")
    dt = (str(f.get("drawdown_type") or "")).lower()
    if "trail" in dt: C.append(f"Trailing drawdown ({f['drawdown_type']}) on the headline plan")
    elif "static" in dt: P.append("Static drawdown: the floor does not climb with your equity")
    dl = first_pct(f.get("max_daily_loss"))
    if dl is not None and dl <= 3: C.append(f"Tight daily loss limit: {f['max_daily_loss']}")
    cr = str(f.get("consistency_rule") or "").lower()
    if cr and cr not in ("none", "no", "false") and "none" not in cr[:6]: C.append("Has a consistency rule (check which phase it applies to)")
    elif f.get("consistency_rule") is False or cr in ("none", "no"): P.append("No consistency rule")
    tp = f.get("trustpilot") or {}
    if num(tp.get("score")) and num(tp.get("score")) >= 4.5 and num(tp.get("count") or 0) >= 1000: P.append(f"Strong Trustpilot record: {num(tp['score']):.1f} from {int(num(tp['count'])):,} reviews")
    elif not tp.get("score"): C.append("No usable Trustpilot rating")
    elif num(tp.get("score")) < 4: C.append(f"Trustpilot rating below 4 ({num(tp['score']):.1f})")
    fy = num(f.get("founded"))
    if fy and YEAR_NOW - fy >= 6: P.append(f"Operating since {int(fy)}")
    elif fy and YEAR_NOW - fy <= 2: C.append(f"Young firm, founded {int(fy)}")
    elif not fy: C.append("Founding year not published")
    if len(f["_platforms"]) >= 3: P.append(f"{len(f['_platforms'])} platforms to choose from")
    if x.get("fee_refundable") is True: P.append("Challenge fee refunded" + (f": {x['refund_policy']}" if x.get("refund_policy") else ""))
    if x.get("has_time_limit") is False: P.append("No time limit on the evaluation")
    elif x.get("has_time_limit") is True: C.append(f"Evaluation time limit: {x.get('time_limit')}")
    if num(x.get("activation_fee")): C.append(f"Activation fee after passing: {money(num(x['activation_fee']))}")
    if f["_complete"] < 80: C.append(f"Publishes less than most: data completeness {f['_complete']}%")
    return P[:7], C[:7]

COMP_WHY = {"trust": "Trustpilot score and review volume", "cost": "fee per $1K of account", "rules": "drawdown, news, weekend and consistency rules",
            "payout": "split, payout cycle and time to first payout", "history": "years in operation"}
def verdict(f):
    comp = f["_comp"]; ks = sorted(comp, key=lambda k: -comp[k])
    best, worst = ks[0], ks[-1]
    s = f"{f['name']} scores {f['_score']:.1f}/10, ranked #{f['_rank']} of {len(FIRMS)}. "
    s += f"Its strongest area is {COMP_LABEL[best][0].lower()} ({comp[best]:.1f}, driven by {COMP_WHY[best]}); the weakest is {COMP_LABEL[worst][0].lower()} ({comp[worst]:.1f}). "
    fits = []
    if is_native(f): fits.append("crypto traders who want an exchange-style setup")
    if comp["cost"] >= 8: fits.append("traders on a budget")
    if comp["payout"] >= 8: fits.append("traders who want frequent withdrawals")
    if tri(f.get("news_trading")) is True and tri(f.get("weekend_holding")) is True: fits.append("news and swing traders")
    if comp["trust"] >= 8 and comp["history"] >= 7: fits.append("traders who rank track record first")
    if "futures" in f["_assets"] and "forex" not in f["_assets"]: fits.append("futures traders")
    if fits: s += "Best fit: " + ", ".join(fits[:3]) + "."
    if f["_flags"]: s += " Missing inputs (" + ", ".join(COMP_LABEL[k][0].lower() for k in f["_flags"]) + ") score 4/10 by rule."
    return s

def fee_matrix(f):
    progs = [p for p in as_list(f.get("programs")) if as_list(p.get("sizes_fees"))]
    if not progs: return ""
    szs = sorted({num(sf.get("size")) for p in progs for sf in as_list(p.get("sizes_fees")) if num(sf.get("size"))})
    cur = f.get("fee_currency")
    head = "".join(f'<th scope="col" class="num">{e(p.get("name") or p.get("type"))}</th>' for p in progs)
    rows = ""
    for s in szs:
        cells = ""
        fees = [next((num(sf.get("fee")) for sf in as_list(p.get("sizes_fees")) if num(sf.get("size")) == s), None) for p in progs]
        lo = min([x for x in fees if x], default=None)
        for v in fees:
            cells += f'<td class="num n{" lo" if v and v == lo and len([x for x in fees if x]) > 1 else ""}">{money(v, cur) if v else "<span class=nil>-</span>"}</td>'
        rows += f'<tr><th scope="row" class="num n">{money(s)}</th>{cells}</tr>'
    return (f'<section class="block"><h2>Fees by account size</h2><p class="small">One-time evaluation fee per program, as listed by the firm. The cheapest option at each size is marked.</p>'
            f'<div class="tablewrap"><table class="mini matrix"><thead><tr><th scope="col" class="num">Account</th>{head}</tr></thead><tbody>{rows}</tbody></table></div></section>')

def xrow(k, v): return (k, v) if v not in (None, "", []) else (k, NIL)
def costs_block(f):
    x = f["_x"]
    if not x: return ('<section class="block"><h2>Costs beyond the fee</h2><p class="small">Reset, refund, time-limit and activation terms are not yet in our dataset for this firm. '
                      f'Use the <a href="{url("/tools/true-cost/")}">true-cost calculator</a> with your own figures.</p></section>')
    rows = [xrow("Reset / retry", show(x.get("reset_fee"))), xrow("Fee refund", show(x.get("refund_policy"))), xrow("Time limit", show(x.get("time_limit"))),
            xrow("Activation fee", mh(num(x.get("activation_fee"))) if num(x.get("activation_fee")) else (show("None") if x.get("activation_fee") == 0 else NIL)),
            xrow("Minimum payout", show(x.get("min_payout"))), xrow("Scaling plan", show(x.get("scaling_plan")))]
    return spec("Costs beyond the fee", rows).replace('<section class="spec">', '<section class="spec">', 1) + \
        f'<p class="small calc-link">Plug these into the <a href="{url("/tools/true-cost/?firm=" + f["slug"])}">true-cost calculator</a> to see the cost to your first payout.</p>'

def payout_block(f):
    x, c = f["_x"], f["_c"]
    methods = as_list(x.get("payout_methods")) or as_list(c.get("payout_methods"))
    kyc = x.get("kyc_before_payout") if x.get("kyc_before_payout") is not None else c.get("kyc_before_payout")
    return spec("Payout policy", [("Profit split", show(f.get("profit_split"))), ("Split scaling", show(f.get("profit_split_scale"))),
        ("Payout cycle", show(f.get("payout_frequency"))), ("First payout (days)", show(f.get("first_payout_days"))),
        ("Payout methods", show(methods) if methods else NIL), ("KYC before payout", {True: "Required", False: "Not required", None: NIL}.get(kyc, NIL))])

def conduct_block(f):
    x, c = f["_x"], f["_c"]
    def tl(v): return {True: "Allowed", False: "Not allowed", "restricted": "Restricted"}.get(v, NIL) if not isinstance(v, str) or v == "restricted" else e(v)
    bots = x.get("ea_bots") if x.get("ea_bots") is not None else c.get("bots_allowed")
    rows = [("News trading", tri_label(f.get("news_trading"))), ("Weekend holding", tri_label(f.get("weekend_holding"))), ("EAs / bots", tl(bots)),
            ("Copy trading", tl(x.get("copy_trading") if x.get("copy_trading") is not None else c.get("copy_trading"))), ("Hedging", tl(x.get("hedging"))),
            ("Max risk per trade", show(x.get("max_risk_per_trade") or c.get("max_position_or_risk_rule"))), ("Inactivity rule", show(x.get("inactivity_rule")))]
    return spec("Trading conduct", rows)

def history_block(f, CL):
    rows = [x for x in CL if x["slug"] == f["slug"]][:12]
    if not rows: body = f'<p class="small">No changes recorded since we started tracking this firm. Every future change to its rules, fees or payout terms will appear here with the date.</p>'
    else: body = change_table(rows, firm_col=False)
    return f'<section class="block" id="history"><h2>Rule history</h2>{body}<p class="small"><a href="{url("/news/")}">All rule changes</a> · <a href="{url("/news/feed.xml")}">RSS</a></p></section>'

def change_table(rows, firm_col=True):
    def cell(v): return e(v) if v is not None else '<span class="nil">none</span>'
    tr = "".join(f'<tr data-s="{e(x["slug"])}" data-k="{e(x["kind"])}"><td class="n nowrap"><time datetime="{e(x["date"])}">{nice_date(x["date"])}</time></td>'
                 + (f'<td><a href="{url("/firms/" + x["slug"] + "/")}">{e(x["firm"])}</a></td>' if firm_col and x["slug"] in BY else (f'<td>{e(x["firm"])}</td>' if firm_col else ""))
                 + f'<td>{e(x["field"])}<small class="kind">{e(x["kind"])}</small></td><td class="was">{cell(x["old"])}</td><td class="now">{cell(x["new"])}</td></tr>' for x in rows)
    return (f'<div class="tablewrap"><table class="mini changes"><thead><tr><th scope="col">Date</th>{"<th scope=col>Firm</th>" if firm_col else ""}<th scope="col">Field</th>'
            f'<th scope="col">Was</th><th scope="col">Now</th></tr></thead><tbody>{tr}</tbody></table></div>')

def firm_faq(f):
    qa = faq(f)
    x, c = f["_x"], f["_c"]
    if x.get("refund_policy"): qa.append((f"Does {f['name']} refund the challenge fee?", f"{x['refund_policy']}."))
    if x.get("time_limit"): qa.append((f"Is there a time limit on {f['name']} challenges?", f"{x['time_limit']}."))
    if x.get("reset_fee"): qa.append((f"Can you reset or retry a failed {f['name']} challenge?", f"{x['reset_fee']}."))
    if "crypto" in f["_assets"]:
        bits = [b for b in (c.get("crypto_venue") and f"execution on {c['crypto_venue']}", c.get("crypto_leverage") and f"leverage {c['crypto_leverage']}",
                            c.get("crypto_pairs") and f"{c['crypto_pairs']} crypto instruments") if b]
        qa.append((f"Can you trade crypto with {f['name']}?", "Yes" + ((": " + "; ".join(bits)) if bits else ", crypto is in its instrument list") + f". Full crypto terms: propanalyse.com/crypto/{f['slug']}/."))
    qa.append((f"Is {f['name']} legit?", f"We score firms on published data, not opinions. {f['name']} has a PA Score of {f['_score']:.1f}/10" +
               (f" and a Trustpilot rating of {num((f.get('trustpilot') or {}).get('score')):.1f}" if (f.get('trustpilot') or {}).get('score') else "") +
               (f"; it was founded in {int(num(f['founded']))}" if num(f.get('founded')) else "") + ". Check the rule history on this page for recent changes."))
    return qa

def firm_page(f):
    CL = CHANGES
    c, bl = crumbs([("Home", "/"), ("All firms", "/firms/"), (f["name"] + " review", f"/firms/{f['slug']}/")])
    progs = "".join(program_html(p, f) for p in as_list(f.get("programs")))
    comps = "".join(f'<div><dt>{COMP_LABEL[k][0]} <span class="n">{COMP_LABEL[k][1]}%</span></dt><dd>{ticks(v, i + 3, "sm")}<b class="n">{v:.1f}</b></dd></div>' for i, (k, v) in enumerate(f["_comp"].items()))
    dc = f.get("discount_code")
    dch = (f'<div class="deal"><span>Public code</span>{code_html(f)}</div>' if dc and dc.get("code") else '<p class="deal none">No public discount code on the firm\'s site at last check.</p>')
    srcs = "".join(f'<li><a href="{e(s)}" rel="nofollow noopener" target="_blank">{e(s)}</a></li>' for s in as_list(f.get("source_urls")) + as_list(f["_x"].get("sources")) + as_list(f["_c"].get("sources")))
    others = "".join(f'<li><a href="{url("/compare/" + a + "-vs-" + b + "/")}"><i>vs</i> {e(BY[b if a == f["slug"] else a]["name"])}</a></li>' for a, b in PAIRS if f["slug"] in (a, b))
    qa = firm_faq(f)
    faqh = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in qa)
    P, C = pros_cons(f)
    pc = (f'<div class="pc"><div><h3>For</h3><ul class="pros">{"".join("<li>" + ic("plus") + "<span>" + e(x) + "</span></li>" for x in P) or "<li><span>Nothing stands out above the field.</span></li>"}</ul></div>'
          f'<div><h3>Against</h3><ul class="cons">{"".join("<li>" + ic("minus") + "<span>" + e(x) + "</span></li>" for x in C) or "<li><span>No red flags in the published data.</span></li>"}</ul></div></div>')
    restricted = as_list(f.get("countries_restricted"))
    tp = f.get("trustpilot") or {}
    tps = ((f'<span class="n">{num(tp["score"]):.1f}</span> / 5 from <span class="n">{int(num(tp.get("count") or 0)):,}</span> reviews') if tp.get("score")
           else (f'<span class="nil">No rating shown ({int(num(tp["count"])):,} reviews)</span>' if tp.get("count") else '<span class="nil">Not available</span>'))
    cpk = cost_per_k(f)
    lv = f.get("last_verified") or TODAY
    meta = [x for x in (cat_badge(f), e(short_hq(f.get("hq") or "")), f'Founded <span class="n">{int(num(f["founded"]))}</span>' if num(f.get("founded")) else "",
                        f'{T["last_verified"]} <time class="n" datetime="{e(lv)}">{nice_date(lv)}</time>',
                        f'<a href="#sources"><span class="n">{len(as_list(f.get("source_urls")) + as_list(f["_x"].get("sources")) + as_list(f["_c"].get("sources")))}</span> source pages</a>',
                        f'<a href="{url("/methodology/")}">Methodology</a>') if x]
    sheet = "".join([
        spec("Rules at a glance", [("Challenge types", show(f.get("challenge_types"))), ("Fees from", mh(f["_fee"], f.get("fee_currency")).replace(NA, NIL)),
             ("Cheapest per $1K", mh(cpk, f.get("fee_currency")).replace(NA, NIL)), ("Account sizes", ('<span class="n">' + e(", ".join(money(s) for s in f["_sizes"])) + "</span>") if f["_sizes"] else NIL),
             ("Profit target", show(f.get("profit_target"))), ("Daily loss limit", show(f.get("max_daily_loss"))), ("Max drawdown", show(f.get("max_drawdown"))),
             ("Drawdown type", show(f.get("drawdown_type"))), ("Min trading days", show(f.get("min_trading_days"))), ("Consistency rule", show(f.get("consistency_rule"))),
             ("Account type", acct_type_html(f)), ("Markets", show([ASSET_LABEL.get(a, a) for a in f["_assets"]])), ("Platforms", plat_chips(f)), ("Leverage", show(f.get("leverage"))),
             ("Restricted countries", show(restricted) if restricted else '<span class="nil">Not listed</span>'), ("Trustpilot", tps)]),
    ])
    crypto_link = (f'<p class="clink"><a class="more" href="{url("/crypto/" + f["slug"] + "/")}">Crypto rules for {e(f["name"])}{ic("arrow")}</a></p>') if "crypto" in f["_assets"] else ""
    s = f["_score"]
    disc = ('<p class="note"><b>Disclosure.</b> PropAnalyse is run by the team behind FundedXYZ. This review uses the same fields and the same scoring formula as every other firm.</p>' if f["slug"] == "fundedxyz" else "")
    body = f"""<div class="wrap">{c}<header class="phead"><h1>{e(f['name'])} review</h1><p class="meta">{''.join('<span>' + m + '</span>' for m in meta)}</p>
<p class="lede">{e(firm_summary(f))}</p><div class="ctas">{visit(f, cls="btn")}{dch}</div>{disc}</header>
<div class="pgrid"><aside class="side" aria-label="PA Score"><div class="scorebox"><p class="big n">{s:.1f}<small>/10</small></p>{ticks(s, 0, "lg")}
<p class="rk">PA Score, ranked <b class="n">#{f['_rank']}</b> of <span class="n">{len(FIRMS)}</span></p><dl class="comp">{comps}</dl>
<p class="small">Data completeness <b class="n">{f['_complete']}%</b>. Missing inputs score 4/10 by rule. <a href="{url('/methodology/')}">How scoring works</a></p></div>
{crypto_link}{('<div class="cmpl"><h2>Compare</h2><ul>' + others + '</ul></div>') if others else ''}</aside>
<div class="pmain"><section class="spec verdict-box"><h2>Verdict</h2><div class="vwrap"><p class="vtext">{e(verdict(f))}</p>{pc}</div></section>{sheet}
{fee_matrix(f)}{costs_block(f)}{payout_block(f)}{conduct_block(f)}
{('<section class="block"><h2>Programs</h2>' + progs + '</section>') if progs else ''}
{history_block(f, CL)}
{('<section class="block faq"><h2>FAQ</h2>' + faqh + '</section>') if faqh else ''}
<section class="block" id="sources"><h2>{T['sources']}</h2><p class="small">Every figure above was read from these pages on <time datetime="{e(lv)}">{nice_date(lv)}</time>. Firms change rules often, so confirm before you buy.</p><ol class="src">{srcs}</ol>
{('<p class="small notes"><b>Data notes.</b> ' + e(f['notes']) + '</p>') if f.get('notes') else ''}</section></div></div></div>"""
    org = {"@type": ["FinancialService", "Organization"], "name": f["name"], "url": f.get("site")}
    if num(f.get("founded")): org["foundingDate"] = str(int(num(f["founded"])))
    review = {"@context": "https://schema.org", "@type": "Review", "name": f"{f['name']} review", "itemReviewed": org,
              "reviewRating": {"@type": "Rating", "ratingValue": s, "bestRating": 10, "worstRating": 0},
              "author": {"@type": "Organization", "name": "PropAnalyse", "url": ABS + "/"}, "publisher": {"@type": "Organization", "name": "PropAnalyse"},
              "datePublished": lv, "dateModified": lv, "reviewBody": verdict(f),
              "positiveNotes": {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": x} for i, x in enumerate(P)]},
              "negativeNotes": {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": x} for i, x in enumerate(C)]}}
    lds = [review, bl, {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]}]
    desc = f"{f['name']} review: PA Score {s:.1f}/10, fees" + (f" from {money(f['_fee'], f.get('fee_currency'))}" if f['_fee'] is not None else "") + (f", {f['profit_split']} split" if f.get('profit_split') else "") + ", drawdown rules, payout policy, pros and cons. Verified " + str(lv) + "."
    page(f"/firms/{f['slug']}/", f"{f['name']} Review {YEAR_NOW}: Rules, Fees, Payouts & Verdict | PropAnalyse", desc, body, lds, "article")
