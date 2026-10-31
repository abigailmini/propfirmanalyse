#!/usr/bin/env python3
"""Merge data/raw/<slug>.json files into data/firms.json in canonical (crypto-first) order."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORDER = ["fundedxyz","hyrotrader","breakout-prop","crypto-fund-trader","bitfunded","fundednext","ftmo","the5ers",
 "fundingpips","alpha-capital","e8-markets","maven-trading","goat-funded-trader","blue-guardian",
 "lark-funding","apex-trader-funding","topstep","myfundedfutures","bulenox","instant-funding","nova-funding"]
# 2026-10-31 expansion (scripts/add_firms.py): crypto-exchange first, then futures, then CFD. Slugs without a raw file are skipped.
ORDER += ["propr", "fondeo", "mubite", "propw",
 "lucid-trading", "tradeify", "take-profit-trader", "earn2trade", "elite-trader-funding", "topone-futures", "tradeday", "daytraders",
 "fxify", "hola-prime", "fintokei", "the-trading-pit", "brightfunded", "city-traders-imperium", "atlas-funded", "ment-funding",
 "for-traders", "thinkcapital", "finotive-funding", "funded-trading-plus", "ftuk"]
# 2026-10-31 status pass: caution firms (still selling, documented warning signs; data/status.json). Closed firms are not merged.
ORDER += ["alpha-futures", "qt-funded", "aquafunded", "funding-traders", "phidias-propfirm", "audacity-capital", "funderpro"]
GENERATED = "2026-10-31"   # data date (build TODAY); bumped with the 2026-10-31 re-verification + expansion
raw = os.path.join(ROOT, "data", "raw")
STATUS = json.load(open(os.path.join(ROOT, "data", "status.json")))   # status: active | caution | closed (closed firms live only in status.json)
firms, missing = [], []
for slug in ORDER:
    p = os.path.join(raw, slug + ".json")
    if not os.path.exists(p):
        if slug in ORDER[:21]: missing.append(slug)
        continue
    with open(p) as f: d = json.load(f)
    if d.get("excluded"):
        missing.append(slug + " (excluded)"); continue
    d["slug"] = slug
    d.setdefault("affiliate_url", "#")
    st = STATUS.get("caution", {}).get(slug)
    d["status"] = "caution" if st else "active"
    if st:
        d["status_since"] = st.get("status_since"); d["status_reason"] = st.get("status_reason")
        d["status_sources"] = [{"url": x["url"], "date": x.get("date"), "text": x.get("text")} for x in st.get("evidence", []) if x.get("url")]
    firms.append(d)
out = {"generated": GENERATED, "order_note": "Crypto-first listing order; ranking on site is by PA Score (same rules for every firm).", "firms": firms}
with open(os.path.join(ROOT, "data", "firms.json"), "w") as f: json.dump(out, f, indent=2, ensure_ascii=False)
print(f"merged {len(firms)} firms; missing: {missing}")
