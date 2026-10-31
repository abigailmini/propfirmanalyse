#!/usr/bin/env python3
"""Promo-code hygiene (2026-10-31). Daily, cron-able.

Rules per code (primary discount_code and each entry in discount_code.also):
  expires    = last valid day published by the firm (YYYY-MM-DD). Hidden from expires+1.
  review_by  = for time-limited codes with no published end (e.g. Halloween banners): hidden after this
               day unless the code was re-verified on/after it (discount_code.verified >= review_by).
  seasonal   = label only (e.g. "halloween").
Build: scripts/build.py calls hide_codes(FIRMS, today) so expired/stale codes never render (pages, offers,
open JSON). Raw data keeps them for the record. If the primary code is hidden, the first live "also" code
is promoted.

CLI:  python3 scripts/check_codes.py [--date YYYY-MM-DD] [--soon N] [--json]
      exit 0 = nothing to do, 1 = codes expired/stale or expiring within N days (default 2).
Cron (Mac mini, 09:05 MYT):  5 9 * * * cd ~/.openclaw/workspace-rex/propfirmanalyse && python3 scripts/check_codes.py >> ../tmp/check_codes.log
CI rebuilds the site daily (pages.yml schedule), so hidden codes drop off the live site without a commit.
"""
import json, os, sys, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _d(s):
    try: return datetime.date.fromisoformat(str(s)[:10])
    except Exception: return None

def code_state(c, today, verified=None, soon=2):
    """-> ("live"|"expiring"|"expired"|"stale", reason)"""
    exp, rb = _d(c.get("expires")), _d(c.get("review_by"))
    ver = _d(c.get("verified") or verified)
    if exp and today > exp: return "expired", f"ended {exp.isoformat()}"
    if rb and today > rb and not (ver and ver >= rb): return "stale", f"time-limited, not re-verified since {ver.isoformat() if ver else '?'} (review by {rb.isoformat()})"
    if exp and (exp - today).days <= soon: return "expiring", f"ends {exp.isoformat()}"
    if rb and (rb - today).days <= soon and not (ver and ver >= rb): return "expiring", f"re-check by {rb.isoformat()}"
    return "live", ""

def hide_codes(firms, today=None):
    """Mutates firms in place; returns list of (slug, code, state, reason) that were hidden."""
    today = today or datetime.datetime.now(datetime.timezone.utc).date()
    hidden = []
    for f in firms:
        dc = f.get("discount_code")
        if not dc: continue
        ver = dc.get("verified")
        also = []
        for a in dc.get("also") or []:
            st, why = code_state(a, today, ver)
            if st in ("expired", "stale"): hidden.append((f["slug"], a.get("code"), st, why))
            else: also.append(a)
        st, why = code_state(dc, today, ver)
        if st in ("expired", "stale"):
            hidden.append((f["slug"], dc.get("code"), st, why))
            if also:
                p = dict(also[0]); p.setdefault("source", dc.get("source")); p.setdefault("verified", ver); p.setdefault("expires", None)
                if also[1:]: p["also"] = also[1:]
                f["discount_code"] = p
            else:
                f["discount_code"] = None
        else:
            if dc.get("also") is not None: dc["also"] = also
    return hidden

def report(firms, today, soon=2):
    rows = []
    for f in firms:
        dc = f.get("discount_code")
        if not dc: continue
        for i, c in enumerate([dc] + list(dc.get("also") or [])):
            st, why = code_state(c, today, dc.get("verified"), soon)
            if st != "live": rows.append({"firm": f["slug"], "code": c.get("code"), "slot": "primary" if i == 0 else "also", "state": st, "why": why, "source": c.get("source") or dc.get("source")})
    return rows

if __name__ == "__main__":
    a = sys.argv[1:]
    today = _d(a[a.index("--date") + 1]) if "--date" in a else datetime.datetime.now(datetime.timezone.utc).date()
    soon = int(a[a.index("--soon") + 1]) if "--soon" in a else 2
    firms = json.load(open(os.path.join(ROOT, "data", "firms.json")))["firms"]
    rows = report(firms, today, soon)
    if "--json" in a: print(json.dumps({"date": today.isoformat(), "flags": rows}, indent=1))
    else:
        print(f"check_codes {today.isoformat()}: {sum(r['state'] in ('expired','stale') for r in rows)} hidden at build, {sum(r['state']=='expiring' for r in rows)} expiring/re-check within {soon}d")
        for r in sorted(rows, key=lambda r: (r["state"], r["firm"])):
            print(f"  {r['state']:9} {r['firm']:22} {r['code']:14} {r['why']}  <{r['source']}>")
    sys.exit(1 if rows else 0)
