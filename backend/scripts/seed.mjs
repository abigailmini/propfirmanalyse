// Generates realistic sample data (30 days) as SQL for the LOCAL D1 only: npm run seed
import { readFileSync } from "node:fs";
const firms = Object.keys(JSON.parse(readFileSync(new URL("../src/firms.gen.json", import.meta.url))).firms);
const off = 480 * 60000, now = Date.now();
const day = (ts) => new Date(ts + off).toISOString().slice(0, 10);
let seed = 7; const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
const pick = (a, w) => { if (!w) return a[Math.floor(rnd() * a.length)]; let t = rnd() * w.reduce((x, y) => x + y, 0); for (let i = 0; i < a.length; i++) { if ((t -= w[i]) < 0) return a[i]; } return a[0]; };
const q = (s) => (s == null ? "NULL" : "'" + String(s).replace(/'/g, "''") + "'");
const hot = ["fundingpips", "ftmo", "the5ers", "fundednext", "hyrotrader", "breakout-prop", "fundedxyz", "topstep", "apex-trader-funding", "crypto-fund-trader"].filter((f) => firms.includes(f));
const pages = ["/", "/firms/", "/offers/", "/crypto/", "/compare/", "/best/", "/futures/", "/zh/", "/complaints/", "/methodology/", ...hot.map((f) => "/firms/" + f + "/"), "/compare/ftmo-vs-fundingpips/", "/compare/hyrotrader-vs-breakout-prop/"];
const pw = pages.map((p, i) => (p === "/" ? 30 : p.startsWith("/firms/") && p.length > 7 ? 8 : 10 - Math.min(i, 8)));
const refs = ["", "", "", "google.com", "google.com", "google.com.my", "bing.com", "duckduckgo.com", "chatgpt.com", "perplexity.ai", "reddit.com", "t.co", "youtube.com", "t.me", "baidu.com"];
const ctry = ["MY", "US", "GB", "SG", "IN", "NG", "DE", "AE", "CN", "AU", "PH", "VN", "ID", "CA"], cw = [18, 16, 9, 7, 9, 5, 4, 4, 6, 3, 4, 3, 4, 3];
const dev = ["mobile", "desktop", "tablet"], dw = [58, 38, 4];
const slots = ["table", "offer-card", "firm-page", "compare", "text"], sw = [45, 20, 22, 10, 3];
const codes = { fundingpips: "HALLOWEEN", ftmo: "", the5ers: "FIVERS5", fundednext: "NEXT10", hyrotrader: "HYRO20", "breakout-prop": "BRK15", fundedxyz: "PA10" };
const out = [];
const rows = { pv: [], ck: [], ev: [] };
for (let d = 29; d >= 0; d--) {
  const base = now - d * 86400000, n = Math.round((120 + (29 - d) * 9) * (0.8 + rnd() * 0.4));
  const vis = Array.from({ length: Math.round(n * 0.62) }, () => Math.floor(rnd() * 2 ** 52).toString(16).padStart(16, "0").slice(-16));
  for (let i = 0; i < n; i++) {
    const ts = base - Math.floor(rnd() * 86400000 * (d === 0 ? 0.4 : 1)), v = pick(vis), path = pick(pages, pw), ref = pick(refs);
    const us = rnd() < 0.06 ? pick(["newsletter", "telegram", "x"]) : "";
    rows.pv.push("(" + [ts, q(day(ts)), q(path), q(ref), q(us), q(us ? (us === "newsletter" ? "email" : "social") : ""), q(us ? "oct-launch" : ""), q(path.startsWith("/zh/") ? "zh-Hans" : "en"), q(pick(dev, dw)), q(pick(ctry, cw)), q(v)].join(",") + ")");
    if (rnd() < 0.11) {
      const firm = path.startsWith("/firms/") && path.length > 7 ? path.split("/")[2] : pick(hot.concat(firms.slice(0, 20)));
      const pos = path.startsWith("/firms/") && path.length > 7 ? "firm-page" : path.startsWith("/compare/") ? "compare" : path === "/offers/" ? "offer-card" : pick(slots, sw);
      rows.ck.push("(" + [ts + 9000, q(day(ts)), q(firm), q(rnd() < 0.3 ? "affiliate" : "site"), q(path), q(pos), q(pos === "offer-card" ? codes[firm] || "" : ""), q(pick(ctry, cw)), q(pick(dev, dw)), q("propanalyse.com"), q(v)].join(",") + ")");
    }
    if (rnd() < 0.035) { const f = pick(Object.keys(codes).filter((k) => codes[k] && firms.includes(k))); rows.ev.push("(" + [ts + 5000, q(day(ts)), q("copy"), q(f), q(codes[f]), q(path), q(""), q(pick(ctry, cw)), q(pick(dev, dw)), q(v)].join(",") + ")"); }
    if (rnd() < 0.02) rows.ev.push("(" + [ts + 4000, q(day(ts)), q("out"), q(""), q(""), q(path), q(pick(["trustpilot.com", "help.ftmo.com", "fundingpips.com", "intercom.help"])), q(pick(ctry, cw)), q(pick(dev, dw)), q(v)].join(",") + ")");
  }
  out.push("INSERT INTO bot_hits(day,kind,reason,n) VALUES(" + q(day(base)) + ",'click','ua'," + Math.round(20 + rnd() * 40) + "),(" + q(day(base)) + ",'click','head'," + Math.round(rnd() * 10) + "),(" + q(day(base)) + ",'beacon','ua'," + Math.round(rnd() * 8) + "),(" + q(day(base)) + ",'click','prefetch'," + Math.round(rnd() * 6) + ") ON CONFLICT DO NOTHING;");
}
const chunk = (t, cols, arr) => { for (let i = 0; i < arr.length; i += 200) out.push("INSERT INTO " + t + "(" + cols + ") VALUES " + arr.slice(i, i + 200).join(",") + ";"); };
chunk("pageviews", "ts,day,path,ref_host,utm_source,utm_medium,utm_campaign,lang,device,country,visitor", rows.pv);
chunk("clicks", "ts,day,firm,dest_kind,src,pos,code,country,device,ref_host,visitor", rows.ck);
chunk("events", "ts,day,kind,firm,code,path,target_host,country,device,visitor", rows.ev);
const subs = [
  ["complaint", "Alpha Futures", "trader.k@example.com", { type: "Payout denied", date: "2026-10-27", desc: "Second payout of $2,340 rejected citing 'consistency' 4 days after I requested it. Rule was not in the terms when I bought the account.", ev: "https://imgur.com/a/xxxx\nTicket #88231" }, "new"],
  ["correction", "FTMO", "", { type: "Data correction", field: "Max daily loss, 2-step 100K", value: "5% (was shown as 4%)", src: "https://ftmo.com/en/trading-objectives/" }, "new"],
  ["listing", "Nova Crypto Funded", "partners@novacf.example", { type: "New listing", notes: "Crypto prop on Bybit, launched Sept 2026, please list us.", src: "https://novacf.example" }, "reviewing"],
  ["complaint", "QT Funded", "m.lee@example.com", { type: "Account closed / breached", date: "2026-10-12", desc: "Account breached for 'hedging' across accounts I do not own." }, "resolved"],
];
subs.forEach(([k, f, e, p, s], i) => { const ts = now - (i * 2 + 0.3) * 86400000; out.push("INSERT INTO submissions(ts,day,kind,firm,email,payload,page,lang,country,visitor,status) VALUES(" + [ts, q(day(ts)), q(k), q(f), q(e), q(JSON.stringify(p)), q(k === "complaint" ? "/complaints/" : "/for-firms/"), q("en"), q(pick(ctry, cw)), q("seed" + i), q(s)].join(",") + ");"); });
process.stdout.write(out.join("\n") + "\n");
