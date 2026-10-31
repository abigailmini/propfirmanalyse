"""Home v2 enrichment (2026-10-31): promo codes, founded year, HQ country and max allocation read from each firm's OWN pages.
Input: tmp/home-v2/facts.json (collected 2026-10-31, every value with source_url). Patches data/raw/<slug>.json and data/firms.json in place,
keeping each file's indent (same approach as scripts/categorize.py). Idempotent. Blank stays blank: nothing is guessed.
fundedxyz 'founded' is NOT taken: the only evidence is a copyright start year."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "..", "tmp", "home-v2", "facts.json")
F = json.load(open(SRC))
SKIP_FOUNDED = {"fundedxyz"}
log = []

def patch(d, slug):
    x = F.get(slug)
    if not x: return False
    p = x.get("promo")
    old = (d.get("discount_code") or {}).get("code")
    if p and p.get("code"):
        dc = {"code": p["code"], "value": p.get("value_text") or "", "percent": p.get("percent"), "source": p.get("source_url"),
              "verified": p.get("checked") or "2026-10-31", "expires": (p.get("expires") or "")[:10] or None}
        if p.get("alt"): dc["also"] = [{"code": a["code"], "value": a.get("value_text"), "percent": a.get("percent")} for a in p["alt"]]
        d["discount_code"] = dc
    else:
        d["discount_code"] = None
    if x.get("promo_note"): d["promo_note"] = x["promo_note"]
    new = (d.get("discount_code") or {}).get("code")
    if old != new: log.append(f"{slug}: code {old} -> {new}")
    fo = x.get("founded") or {}
    if fo.get("year") and slug not in SKIP_FOUNDED:
        if d.get("founded") and int(d["founded"]) != int(fo["year"]): log.append(f"{slug}: founded {d['founded']} -> {fo['year']}")
        d["founded"] = int(fo["year"]); d["founded_source"] = fo.get("source_url")
    hq = x.get("hq_country") or {}
    if hq.get("code"): d["hq_country"] = {"code": hq["code"].upper(), "source": hq.get("source_url"), "quote": hq.get("quote")}
    ma = x.get("max_allocation") or {}
    if ma.get("usd"):
        d["max_allocation_usd"] = ma["usd"]; d["max_allocation_text"] = ma.get("text"); d["max_allocation_source"] = ma.get("source_url")
    elif ma.get("text"):
        d.pop("max_allocation_usd", None); d["max_allocation_text"] = ma["text"]; d["max_allocation_source"] = ma.get("source_url")
    srcs = d.setdefault("source_urls", [])
    for v in (p or {}).get("source_url"), fo.get("source_url"), hq.get("source_url"), ma.get("source_url"):
        if v and v not in srcs and slug not in SKIP_FOUNDED | set(): srcs.append(v)
    return True

def dump(path, d, txt):
    ind = len(txt.split("\n")[1]) - len(txt.split("\n")[1].lstrip(" ")) if "\n" in txt else 2
    open(path, "w").write(json.dumps(d, indent=ind or 2, ensure_ascii=False) + ("\n" if txt.endswith("\n") else ""))

raw = os.path.join(ROOT, "data", "raw")
for n in sorted(os.listdir(raw)):
    if n.endswith(".json"):
        p = os.path.join(raw, n); t = open(p).read(); d = json.loads(t)
        if patch(d, n[:-5]): dump(p, d, t)
log.clear()
fp = os.path.join(ROOT, "data", "firms.json"); t = open(fp).read(); D = json.loads(t)
for f in D["firms"]: patch(f, f["slug"])
dump(fp, D, t)
print("\n".join(log))
