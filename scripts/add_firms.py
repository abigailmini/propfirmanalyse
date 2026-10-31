#!/usr/bin/env python3
"""Firm expansion 20 -> ~45 (2026-10-31). Converts staged research (tmp/expand/, each firm's OWN pages, checked 2026-10-31)
into the repo schema and writes data/raw/<slug>.json, data/extra/<slug>.json, data/crypto/<slug>.json and data/payout_claims.json.
Then run scripts/merge.py (raw -> firms.json) and scripts/build.py.

usage: python3 scripts/add_firms.py <slug> [<slug> ...]   (idempotent: re-running overwrites the same files)

Conversions vs the staging format (same shape as scripts/enrich_home.py output):
  hq_country "GB"        -> {"code","source","quote"}
  founded + field_sources -> founded + founded_source
  max_allocation (int)   -> max_allocation_usd / max_allocation_text / max_allocation_source
  discount_code "CODE"   -> {"code","value","percent","source","verified","expires"[,"also"]} from PROMOS below
                            (only codes posted publicly on the firm's own site on 2026-10-31; expiry only when the site states one)
  trustpilot             -> TP overrides below where the staged value was missing (read from trustpilot.com, 2026-10-31)
Blank stays blank: nothing is guessed."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STAGE = os.environ.get("EXPAND_DIR", os.path.join(ROOT, "..", "tmp", "expand"))
CHECKED = "2026-10-31"

# code, value text, percent, expires (ISO, only if stated), also-codes
PROMOS = {
 "fxify": ("AGHHH35", "35% off (Halloween; not valid on Instant Lite)", 35, "2026-11-02",
           [("ONESTEP35", "35% off One Phase for new traders", 35), ("FUNDED40", "40% off Instant Funding", 40)]),
 "lucid-trading": ("VAULT", "About 30% off plan prices (e.g. Pro 25K $108 -> $75.60)", 30, None, []),
 "tradeify": ("GEMS", "30% off (Halloween, ends 31 Oct 2026 11:59 PM EST)", 30, "2026-10-31", []),
 "take-profit-trader": ("NOFEE40", "40% off the Test subscription for life + no PRO activation fee", 40, None, []),
 "propr": ("SPOOKY", "20% off all challenges (Halloween, ends Sunday 00:00 UTC)", 20, "2026-11-01", []),
 "hola-prime": ("SPOOKY40", "40% off forex accounts for new users (Halloween; not on $2K)", 40, None, [("SPOOKY20", "20% off", 20)]),
 "fintokei": ("NEW20", "20% off your first challenge", 20, None, [("COMBOTRADER", "10% off ProTrader $50K + free $5K ProTrader", 10)]),
 "atlas-funded": ("SPOOKY", "45% off CFD accounts (40% futures, 25% Atlas Daily)", 45, None, [("NEW", "50% off first purchase", 50)]),
 "brightfunded": ("HW30", "30% off (Halloween)", 30, None, []),
 "earn2trade": ("60PLUS50", "60% off evaluations + 50% off resets (Halloween flash sale)", 60, None, []),
 "finotive-funding": ("FIRST25", "25% off your first purchase", 25, None,
                      [("BOO50", "50% off (Halloween, ends ~1 Nov)", 50), ("FINCRYPTO", "15% off when paying with crypto", 15)]),
 "for-traders": ("HALLOWEEN25", "25% off all accounts (Halloween)", 25, None, [("BOO6K", "Forex Fast $6K for $9.99", None)]),
 "funded-trading-plus": ("SIZE30", "30% off $5K-$10K accounts", 30, None,
                         [("SIZE25", "25% off $25K-$50K accounts", 25), ("SIZE20", "20% off $100K-$200K accounts", 20)]),
 "funderpro": ("OCT30", "30% off all challenges (October promo)", 30, None, []),
 "tradeday": ("TDNEW", "Up to 55% off (Quick Pay 55%, Fast Pass 50% shown at checkout prices)", 55, None, []),
 "ftuk": ("FTUK30", "30% off your first purchase (new customers)", 30, None, [("WEALTHCHARTS", "50% off all Futures challenges", 50)]),
 "topone-futures": ("BOO", "50% off Elite Daily and Ignite, 45% off Instant (Halloween)", 50, None, [("BOGO", "Buy one get one on Elite Access", None)]),
}

# Pay-later programs: the listed price is only an entry fee; an activation / funded fee follows if you pass.
# The entry ticket moves to sizes_fees[].entry_fee and fee becomes null, so cost_per_k(), fee_at() and the price tables
# (which all skip null fees) are not set by a $4-$9 ticket; the program keeps its sizes and a fee_note.
DEFERRED = {"atlas-funded": ["Access"], "for-traders": ["Pay After Pass"], "funded-trading-plus": ["Activation Accounts"],
            "mubite": ["Nitro"], "topone-futures": ["Elite Access"]}
DEFERRED_NOTE = "Entry fee only: an activation / funded-account fee is charged after you pass"

# Trustpilot where staging had none. score None + count = profile exists but Trustpilot shows no rating (suspended).
SUSP = "Rating unavailable: Trustpilot says it removed fake reviews for this company (breach of its guidelines)"
TP = {
 "for-traders": {"score": None, "count": 1821, "note": SUSP, "checked": CHECKED, "source": "https://www.trustpilot.com/review/fortraders.com"},
 "thinkcapital": {"score": None, "count": 605, "note": SUSP, "checked": CHECKED, "source": "https://www.trustpilot.com/review/thinkcapital.com"},
 "finotive-funding": {"score": None, "count": 1077, "note": SUSP, "checked": CHECKED, "source": "https://www.trustpilot.com/review/finotivefunding.com"},
}
_tpx = os.path.join(STAGE, "tp_overrides.json")
if os.path.exists(_tpx): TP.update(json.load(open(_tpx)))

ORDER_KEYS = ["name", "slug", "site", "category", "assets", "challenge_types", "account_sizes", "fee_currency", "programs", "fee_from",
              "profit_split", "profit_split_scale", "max_daily_loss", "max_drawdown", "drawdown_type", "profit_target", "leverage", "platforms",
              "payout_frequency", "first_payout_days", "payout_speed", "min_trading_days", "consistency_rule", "news_trading", "weekend_holding",
              "countries_restricted", "founded", "hq", "discount_code", "affiliate_url", "trustpilot", "last_verified", "source_urls", "notes",
              "segment", "also_offers", "category_basis", "category_source", "founded_source", "hq_country",
              "max_allocation_usd", "max_allocation_text", "max_allocation_source", "field_sources"]

def convert(s):
    d = json.load(open(os.path.join(STAGE, "raw", s + ".json")))
    fs = d.get("field_sources") or {}
    o = dict(d)
    o["slug"] = s
    o["affiliate_url"] = d.get("affiliate_url") or "#"
    o["last_verified"] = CHECKED
    hq = d.get("hq_country")
    if isinstance(hq, str) and hq:
        o["hq_country"] = {"code": hq.upper(), "source": fs.get("hq_country") or fs.get("hq") or d.get("site"), "quote": d.get("hq")}
    elif not hq: o.pop("hq_country", None)
    if d.get("founded"):
        o["founded"] = int(d["founded"]); o["founded_source"] = fs.get("founded") or d.get("site")
    ma = o.pop("max_allocation", None)
    if ma: o["max_allocation_usd"] = int(ma)
    if ma or d.get("max_allocation_text"):
        o["max_allocation_text"] = d.get("max_allocation_text")
        o["max_allocation_source"] = fs.get("max_allocation") or fs.get("max_allocation_text") or d.get("site")
    else: o.pop("max_allocation_text", None)
    p = PROMOS.get(s)
    if p and d.get("discount_code"):
        code, val, pct, exp, also = p
        dc = {"code": code, "value": val, "percent": pct, "source": fs.get("discount_code") or d.get("site"), "verified": CHECKED, "expires": exp}
        if also: dc["also"] = [{"code": c, "value": v, "percent": q} for c, v, q in also]
        o["discount_code"] = dc
    else:
        if d.get("discount_code"): print(f"  ! {s}: staged code {d['discount_code']} has no PROMOS entry -> dropped")
        o["discount_code"] = None
    if s in TP: o["trustpilot"] = TP[s]
    for p in o.get("programs") or []:
        if any(k.lower() in (p.get("name") or "").lower() for k in DEFERRED.get(s, [])):
            p["deferred_fee"] = True; p.setdefault("fee_note", DEFERRED_NOTE)
            for sf in p.get("sizes_fees") or []:
                if sf.get("fee") is not None: sf["entry_fee"] = sf["fee"]; sf["fee"] = None
    tp = o.get("trustpilot")
    if tp:
        u = fs.get("trustpilot") or next((x for x in d.get("source_urls", []) if "trustpilot.com" in x), None) or tp.get("source")
        if u and u not in o.setdefault("source_urls", []): o["source_urls"].append(u)
    for k in ("founded_source", "max_allocation_source"):
        v = o.get(k)
        if v and v not in o.setdefault("source_urls", []): o["source_urls"].append(v)
    out = {k: o[k] for k in ORDER_KEYS if k in o}
    out.update({k: v for k, v in o.items() if k not in out})
    return out

def main(slugs):
    pcp = os.path.join(ROOT, "data", "payout_claims.json"); PC = json.load(open(pcp))
    for s in slugs:
        meta = json.load(open(os.path.join(STAGE, "meta", s + ".json")))
        if meta.get("status") != "active" or meta.get("override_excluded"):
            print(f"skip {s}: {meta.get('status')} ({(meta.get('reason') or meta.get('override_excluded') or '')[:80]})"); continue
        r = convert(s)
        json.dump(r, open(os.path.join(ROOT, "data", "raw", s + ".json"), "w"), indent=2, ensure_ascii=False)
        for sub in ("extra", "crypto"):
            sp = os.path.join(STAGE, sub, s + ".json")
            if os.path.exists(sp):
                x = json.load(open(sp)); x.setdefault("checked", CHECKED)
                json.dump(x, open(os.path.join(ROOT, "data", sub, s + ".json"), "w"), indent=2, ensure_ascii=False)
        c = meta.get("payout_claim")
        if c and c.get("text") and c.get("source"):
            PC["firms"][s] = {"text": c["text"], "value_usd": c.get("value_usd"), "source": c["source"], "proof": c.get("proof")}
        else: PC["firms"].pop(s, None)
        print(f"ok {s}: {r['category']}, fee {r.get('fee_from')}, code {(r.get('discount_code') or {}).get('code')}, tp {r.get('trustpilot')}")
    json.dump(PC, open(pcp, "w"), indent=1, ensure_ascii=False)

if __name__ == "__main__":
    main(sys.argv[1:])
