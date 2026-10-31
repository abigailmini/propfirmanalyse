#!/usr/bin/env python3
"""Account-type taxonomy (2026-10-31). Idempotent: writes category / also_offers / category_basis / category_source
into data/raw/<slug>.json AND data/firms.json (firms.json is maintained after merge, so it is patched in place).

category    = the firm's main account type: "futures" | "cfd" | "crypto-exchange"
also_offers = other account types the same firm sells (list, may be empty)
segment     = the old asset-mix label (crypto / multi / forex-cfd / futures), kept for the /crypto/ hub split.
Each call is read from the firm's own pages (category_source)."""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

C = {  # slug: (category, also_offers, basis, source)
 "fundedxyz": ("crypto-exchange", [], "Crypto-only firm on its own crypto trading platform; perpetual pairs, USDT payouts.", "https://www.fundedxyz.com/faq"),
 "hyrotrader": ("crypto-exchange", [], "Trades run on Bybit or BloFin demo accounts connected by API, or on Hyro's terminal priced from live Bybit data.", "https://www.hyrotrader.com/faq/"),
 "breakout-prop": ("crypto-exchange", [], "Crypto-first firm: Breakout Terminal (and DXtrade) priced from exchanges and market makers; part of the Kraken (Payward) group.", "https://intercom.help/breakoutprop/en/collections/13572047-breakout-evaluation"),
 "crypto-fund-trader": ("crypto-exchange", ["cfd"], "Crypto-first firm and Bybit partner: trade from your own Bybit account via API; MT5 and Match-Trader CFD accounts are also sold.", "https://cryptofundtrader.com/faq/"),
 "bitfunded": ("crypto-exchange", [], "Crypto-first firm on its own platform, fed by live data from partner exchanges; 100+ crypto pairs plus a few TradFi pairs.", "https://www.bitfunded.com/frequently-asked-questions/"),
 "fundednext": ("cfd", ["futures"], "CFD challenges on MT4, MT5, cTrader and Match-Trader; a separate futures program runs on NinjaTrader and Tradovate.", "https://fundednext.com/trading-platforms"),
 "ftmo": ("cfd", ["futures"], "Simulated CFD accounts on MT4, MT5, cTrader and TradingView; FTMO also lists a futures product.", "https://ftmo.com/en/"),
 "the5ers": ("cfd", ["futures"], "CFD programs (High Stakes, Hyper Growth, Bootcamp) on MT5; a futures program is listed separately.", "https://the5ers.com/"),
 "fundingpips": ("cfd", [], "CFD challenges on MT5, cTrader and Match-Trader.", "https://fundingpips.com/"),
 "alpha-capital": ("cfd", [], "CFD challenges on MT5, cTrader, DXtrade and TradeLocker.", "https://alphacapitalgroup.uk/product"),
 "e8-markets": ("cfd", ["futures"], "Main products (E8 One, E8 Pro, E8 Signature) are CFD accounts on MT5, cTrader, Match-Trader and TradeLocker; E8 Zero is a futures product.", "https://help.e8markets.com/en/articles/13106558-all-product-overviews-e8-one-vs-e8-zero-vs-e8-pro-vs-e8-signature"),
 "maven-trading": ("cfd", [], "CFD challenges on MT5 and Match-Trader (Maven simulated server).", "https://maventrading.com/faqs"),
 "goat-funded-trader": ("cfd", ["futures"], "CFD challenges on MT5, cTrader, Match-Trader and TradeLocker; Volumetrica accounts cover futures.", "https://goatfundedtrader.com/"),
 "blue-guardian": ("cfd", ["futures"], "CFD challenges on MT5, Match-Trader and TradeLocker; separate futures plans on NinjaTrader, Tradovate and TradingView.", "https://blueguardian.com/"),
 "lark-funding": ("cfd", [], "CFD challenges on DXtrade, cTrader and Match-Trader.", "https://helpdesk.larkfunding.com/en/articles/11738989-what-trading-platform-does-lark-funding-offer"),
 "instant-funding": ("cfd", [], "CFD accounts on MT5, cTrader and Match-Trader.", "https://instantfunding.com/"),
 "apex-trader-funding": ("futures", [], "CME futures evaluations on Rithmic, Tradovate and NinjaTrader.", "https://apextraderfunding.com/"),
 "topstep": ("futures", [], "CME futures accounts on TopstepX.", "https://www.topstep.com/"),
 "myfundedfutures": ("futures", [], "Simulated CME Group futures (CME, CBOT, NYMEX, COMEX) on Tradovate, NinjaTrader, TradingView, Quantower and Volumetrica.", "https://myfundedfutures.com/"),
 "bulenox": ("futures", [], "CME Group futures data via Rithmic; R | Trader Pro, NinjaTrader and other Rithmic platforms.", "https://bulenox.com/faq"),
 "nova-funding": ("cfd", [], "Listed as a forex/CFD firm before it went offline (excluded from the site).", None),
}
# platform lists the firm publishes that our first pass left empty
PLATFORMS_FILL = {
 "myfundedfutures": (["Tradovate", "NinjaTrader", "TradingView", "Quantower", "Volumetrica"], "https://help.myfundedfutures.com/en/collections/5786939-trading-platforms"),
 "fundingpips": (["MT5", "cTrader", "Match-Trader"], None),  # venue in data/crypto/fundingpips.json, read from fundingpips.com
}

def patch(d, slug):
    if slug not in C: return False
    if "segment" not in d: d["segment"] = d.get("category")
    cat, also, basis, src = C[slug]
    d["category"], d["also_offers"], d["category_basis"] = cat, also, basis
    if src: d["category_source"] = src
    if slug in PLATFORMS_FILL and not d.get("platforms"):
        pl, psrc = PLATFORMS_FILL[slug]; d["platforms"] = pl
        if psrc and psrc not in d.get("source_urls", []): d.setdefault("source_urls", []).append(psrc)
    return True

if __name__ == "__main__":
    raw = os.path.join(ROOT, "data", "raw")
    for n in sorted(os.listdir(raw)):
        if not n.endswith(".json"): continue
        p = os.path.join(raw, n); txt = open(p).read(); d = json.loads(txt)
        ind = len(txt.split("\n")[1]) - len(txt.split("\n")[1].lstrip(" ")) if "\n" in txt else 2   # keep each file's own indent
        if patch(d, n[:-5]):
            with open(p, "w") as fh: fh.write(json.dumps(d, indent=ind or 2, ensure_ascii=False) + ("\n" if txt.endswith("\n") else ""))
    fp = os.path.join(ROOT, "data", "firms.json"); D = json.load(open(fp))
    for f in D["firms"]:
        if not patch(f, f["slug"]) and not f.get("category"): print("UNCLASSIFIED", f["slug"])   # 2026-10-31 additions carry category in raw
    with open(fp, "w") as fh: fh.write(json.dumps(D, indent=2, ensure_ascii=False))
    from collections import Counter
    print(Counter(f["category"] for f in D["firms"]))
