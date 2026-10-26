#!/usr/bin/env python3
"""Merge data/raw/<slug>.json files into data/firms.json in canonical (crypto-first) order."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORDER = ["fundedxyz","hyrotrader","breakout-prop","crypto-fund-trader","bitfunded","fundednext","ftmo","the5ers",
 "fundingpips","alpha-capital","e8-markets","maven-trading","goat-funded-trader","blue-guardian",
 "lark-funding","apex-trader-funding","topstep","myfundedfutures","bulenox","instant-funding","nova-funding"]
raw = os.path.join(ROOT, "data", "raw")
firms, missing = [], []
for slug in ORDER:
    p = os.path.join(raw, slug + ".json")
    if not os.path.exists(p):
        missing.append(slug); continue
    with open(p) as f: d = json.load(f)
    if d.get("excluded"):
        missing.append(slug + " (excluded)"); continue
    d["slug"] = slug
    d.setdefault("affiliate_url", "#")
    firms.append(d)
out = {"generated": "2026-10-26", "order_note": "Crypto-first listing order; ranking on site is by PA Score (same rules for every firm).", "firms": firms}
with open(os.path.join(ROOT, "data", "firms.json"), "w") as f: json.dump(out, f, indent=2, ensure_ascii=False)
print(f"merged {len(firms)} firms; missing: {missing}")
