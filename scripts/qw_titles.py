"""Title shortener (2026-10-31 audit): keep <title>/og:title <= 60 chars where possible, keyword-first.
Used by more_quickwins.py (post-pass); runnable standalone for a dry run: python3 scripts/qw_titles.py site"""
import re
QW_SUF = " | PropAnalyse"
QW_TITLE_OVERRIDE = {
    "/best/": "Best Prop Firms 2026 by Category: Cheapest, Crypto & More",
    "/caution/": "Prop Firms With Warnings (2026): Payout Complaints",
    "/cfd/": "Best CFD & Forex Prop Firms 2026, Ranked",
    "/futures/": "Best Futures Prop Firms 2026, Ranked",
    "/crypto/": "Best Crypto Prop Firms 2026: Rules Compared",
    "/crypto-exchange/": "Crypto Exchange Prop Firms 2026: Perps on Bybit & More",
    "/closed-prop-firms/": "Closed Prop Firms: Shut-Down List, Dates & What Happened",
    "/complaints/": "Report a Prop Firm: Denied Payouts, Rule Changes, Refunds",
    "/countries/": "Prop Firms by Country 2026: Who Accepts Your Country",
    "/faq/": "Prop Firm FAQ: Best, Cheapest, Payouts & Legitimacy",
    "/glossary/": "Prop Firm Glossary: Drawdown, Splits & Consistency Rules",
    "/legit/": "Are Prop Firms Legit? 2026 Evidence, Firm by Firm",
    "/methodology/": "Methodology: How PropAnalyse Scores Prop Firms",
    "/news/": "Prop Firm Rule Changes: Dated Log of Fees & Payouts",
    "/platforms/": "Prop Firms by Platform 2026: MT5, cTrader, TradingView",
    "/programs/": "Prop Firm Challenges Compared 2026: Fees & Rules",
    "/quiz/": "Which Prop Firm Is Right for Me? 7-Question Finder",
    "/sizes/": "Prop Firm Challenges by Account Size: $5K to $200K",
    "/tools/": "Prop Firm Calculators: True Cost, Drawdown, Target",
    "/tools/drawdown/": "Prop Firm Drawdown Calculator: Static, Trailing, EOD",
    "/updates/": "Prop Firm Verification Log & Dated Rule Changes",
    "/best/beginners/": "Best Prop Firms for Beginners 2026: 6-Point Checklist",
}
QW_REPL = [(": Rules, Fees, Payouts & Verdict", ": Rules, Fees & Payouts"), (": Rules, Fees & Payouts", ": Rules & Fees"),
           (" (2026): Fees, Rules & Payouts Compared", " 2026: Fees, Rules & Payouts"), (": Fees, Rules & Payouts", ": Fees & Rules"),
           (": Payouts, Track Record & Cautions", ": Payouts & Track Record"), (" 2026 Evidence: Payouts & Track Record", " 2026 Evidence"),
           (": Leverage, Weekend, Bots, Payouts", ": Leverage, Bots, Payouts"), (": Leverage, Bots, Payouts", ""),
           (" (2026)", " 2026"), (" Traders 2026", " 2026"), ("Prop Firm Challenge", "Prop Challenge")]

def qw_short_title(t, path=""):
    if path in QW_TITLE_OVERRIDE: return QW_TITLE_OVERRIDE[path]
    if len(t) <= 60: return t
    if t.endswith(QW_SUF): t = t[:-len(QW_SUF)]
    caution = t.endswith(" (Caution)")
    if caution: t = t[:-len(" (Caution)")]
    lim = 60 - (10 if caution else 0)
    for a, b in QW_REPL:
        if len(t) > lim and a in t: t = t.replace(a, b)
    while len(t) > lim and ":" in t and ", " in t.split(":", 1)[1]:
        h, tail = t.split(":", 1); t = h + ":" + tail.rsplit(", ", 1)[0]
    if len(t) > lim: t = re.sub(r" \([^)]*\)", "", t)
    if len(t) > lim and ":" in t and len(t.split(":")[0]) >= 20: t = t.split(":")[0]
    return t + (" (Caution)" if caution else "")

if __name__ == "__main__" and "FIRMS" not in globals():   # standalone only (build.py exec's this file)
    import os, sys, html, collections
    out = []
    for root, _, fs in os.walk(sys.argv[1]):
        for f in fs:
            if f != "index.html": continue
            s = open(os.path.join(root, f)).read(); m = re.search(r"<title>(.*?)</title>", s)
            p = root[len(sys.argv[1]):] + "/"
            if m: t = html.unescape(m.group(1)); out.append((p, t, qw_short_title(t, p)))
    print("pages", len(out), "still>60", sum(len(n) > 60 for _, _, n in out), "dups", [k for k, v in collections.Counter(n for _, _, n in out).items() if v > 1][:10])
    seen = set()
    for p, t, n in sorted(out):
        k = (p.strip("/").split("/")[0], p.count("/"))
        if (k in seen and len(n) <= 60) or t == n: continue
        seen.add(k); print(len(n), p, "|", n)
