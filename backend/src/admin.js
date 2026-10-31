// /admin: basic-auth dashboard (password = Worker secret ADMIN_TOKEN), CSV export, submissions inbox.
import { esc, safeEqual, daysAgo, dayOf } from "./lib.js";

const STATUSES = ["new", "reviewing", "resolved", "rejected", "spam"];
const SEARCH = /(^|\.)(google\.|bing\.com|duckduckgo\.com|yahoo\.|baidu\.com|yandex\.|ecosia\.org|brave\.com|naver\.com|sogou\.com|so\.com|qwant\.com|startpage\.com|perplexity\.ai|chatgpt\.com|copilot\.microsoft\.com)/;
const SOCIAL = /(^|\.)(t\.co|x\.com|twitter\.com|facebook\.com|fb\.com|instagram\.com|reddit\.com|youtube\.com|tiktok\.com|t\.me|telegram\.org|discord\.com|linkedin\.com|whatsapp\.com|weibo\.com|xiaohongshu\.com)$/;
const refType = (h) => (SEARCH.test(h) ? (/perplexity|chatgpt|copilot/.test(h) ? "AI" : "search") : SOCIAL.test(h) ? "social" : "link");

async function authed(req, env) {
  const h = req.headers.get("authorization") || "";
  if (!h.startsWith("Basic ")) return false;
  let dec = ""; try { dec = atob(h.slice(6)); } catch { return false; }
  const pass = dec.slice(dec.indexOf(":") + 1);
  return safeEqual(pass, env.ADMIN_TOKEN);
}
const deny = () => new Response("Authentication required", { status: 401, headers: { "WWW-Authenticate": 'Basic realm="PropAnalyse admin", charset="UTF-8"', "Cache-Control": "no-store" } });
const SEC = { "Cache-Control": "no-store", "X-Robots-Tag": "noindex, nofollow", "X-Frame-Options": "DENY", "Referrer-Policy": "no-referrer",
  "Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'; img-src data:; font-src https://propanalyse.com; form-action 'self'; frame-ancestors 'none'; base-uri 'none'" };

export async function admin(req, env, url) {
  if (!env.ADMIN_TOKEN) return new Response("Admin disabled: set the ADMIN_TOKEN secret (wrangler secret put ADMIN_TOKEN).", { status: 503 });
  if (!(await authed(req, env))) return deny();
  const p = url.pathname;
  if (req.method === "POST") {
    const o = req.headers.get("origin");
    if (o !== url.origin) return new Response("Bad origin", { status: 403 });     // CSRF guard (basic auth is sent cross-site)
    const m = p.match(/^\/admin\/sub\/(\d+)$/);
    if (!m) return new Response("Not found", { status: 404 });
    const f = await req.formData();
    const st = String(f.get("status") || "");
    if (!STATUSES.includes(st)) return new Response("Bad status", { status: 400 });
    await env.DB.prepare("UPDATE submissions SET status=?, note=? WHERE id=?").bind(st, String(f.get("note") || "").slice(0, 2000), +m[1]).run();
    return new Response(null, { status: 303, headers: { Location: "/admin" + (url.search || "") + "#sub-" + m[1] } });
  }
  if (p === "/admin/export.csv") return csv(env, url);
  if (p === "/admin" || p === "/admin/") return dashboard(env, url);
  return new Response("Not found", { status: 404 });
}

const RANGES = { 1: "Today", 7: "7 days", 30: "30 days", 90: "90 days" };
const rng = (url) => { const r = parseInt(url.searchParams.get("r") || "7", 10); return RANGES[r] ? r : 7; };

// ---------- CSV ----------
const TABLES = {
  pageviews: "id, ts, day, path, ref_host, utm_source, utm_medium, utm_campaign, lang, device, country, visitor",
  clicks: "id, ts, day, firm, dest_kind, src, pos, code, country, device, ref_host, visitor",
  events: "id, ts, day, kind, firm, code, path, target_host, country, device, visitor",
  submissions: "id, ts, day, kind, firm, email, status, note, page, lang, country, payload",
};
async function csv(env, url) {
  const t = url.searchParams.get("t") || "clicks";
  if (!TABLES[t]) return new Response("t must be one of " + Object.keys(TABLES).join(", "), { status: 400 });
  const r = rng(url), since = daysAgo(r - 1, env);
  const { results } = await env.DB.prepare("SELECT " + TABLES[t] + " FROM " + t + " WHERE day >= ? ORDER BY ts LIMIT 100000").bind(since).all();
  const cols = TABLES[t].split(", ");
  const cell = (v) => { let s = v == null ? "" : String(v); if (/^[=+\-@\t\r]/.test(s)) s = "'" + s; return /[",\n\r]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s; };
  const body = [cols.join(","), ...results.map((row) => cols.map((c) => cell(c === "ts" ? new Date(row.ts).toISOString() : row[c])).join(","))].join("\r\n") + "\r\n";
  return new Response(body, { headers: { ...SEC, "Content-Type": "text/csv; charset=utf-8", "Content-Disposition": 'attachment; filename="propanalyse-' + t + "-" + since + '.csv"' } });
}

// ---------- dashboard ----------
const n0 = (x) => (x || 0).toLocaleString("en-US");
const pct = (a, b) => (b ? ((100 * a) / b).toFixed(a / b < 0.1 ? 1 : 0) + "%" : "-");

function table(title, cols, rows, opt = {}) {
  const max = Math.max(1, ...rows.map((r) => +r[opt.bar ?? 1] || 0));
  const head = cols.map((c, i) => '<th' + (i ? ' class="n"' : "") + ">" + esc(c) + "</th>").join("");
  const body = rows.length ? rows.map((r) => "<tr>" + r.map((v, i) => i === 0
    ? '<td class="k"><span class="bar" style="width:' + (((+r[opt.bar ?? 1] || 0) / max) * 100).toFixed(1) + '%"></span><span class="lbl">' + (opt.raw0 ? v : esc(v || "(none)")) + "</span></td>"
    : '<td class="n">' + (typeof v === "number" ? n0(v) : esc(v)) + "</td>").join("") + "</tr>").join("")
    : '<tr><td colspan="' + cols.length + '" class="empty">No data in this range yet</td></tr>';
  return '<section class="card' + (opt.wide ? " wide" : "") + '"' + (opt.id ? ' id="' + opt.id + '"' : "") + "><h2>" + esc(title) + (opt.note ? ' <small>' + esc(opt.note) + "</small>" : "") + "</h2><table><thead><tr>" + head + "</tr></thead><tbody>" + body + "</tbody></table></section>";
}

function chart(days, pv, ck) {
  const W = 1000, H = 150, n = days.length, bw = W / n, max = Math.max(1, ...days.map((d) => pv[d] || 0));
  let bars = "";
  days.forEach((d, i) => {
    const h1 = ((pv[d] || 0) / max) * (H - 20), h2 = ((ck[d] || 0) / max) * (H - 20);
    bars += '<g><title>' + d + ": " + (pv[d] || 0) + " views, " + (ck[d] || 0) + ' clicks</title><rect x="' + (i * bw + bw * 0.12).toFixed(1) + '" y="' + (H - h1).toFixed(1) + '" width="' + (bw * 0.76).toFixed(1) + '" height="' + h1.toFixed(1) + '" class="pv"/><rect x="' + (i * bw + bw * 0.3).toFixed(1) + '" y="' + (H - h2).toFixed(1) + '" width="' + (bw * 0.4).toFixed(1) + '" height="' + h2.toFixed(1) + '" class="ck"/></g>';
  });
  const lab = n > 1 ? '<div class="axis"><span>' + days[0] + "</span><span>" + days[n - 1] + "</span></div>" : "";
  return '<section class="card wide"><h2>Daily <small><i class="sw pv"></i>page views <i class="sw ck"></i>outbound clicks</small></h2><svg viewBox="0 0 ' + W + " " + H + '" preserveAspectRatio="none" class="chart" role="img" aria-label="Daily page views and clicks">' + bars + "</svg>" + lab + "</section>";
}

async function dashboard(env, url) {
  const DB = env.DB, r = rng(url), since = daysAgo(r - 1, env), d7 = daysAgo(6, env), d30 = daysAgo(29, env), today = dayOf(Date.now(), env);
  const sf = STATUSES.includes(url.searchParams.get("s")) ? url.searchParams.get("s") : "";
  const U = "COUNT(DISTINCT day||'|'||visitor)";
  const kq = (s) => [
    DB.prepare("SELECT COUNT(*) n, " + U + " u FROM pageviews WHERE day >= ?").bind(s),
    DB.prepare("SELECT COUNT(*) n, " + U + " u FROM clicks WHERE day >= ? AND dest_kind != 'home'").bind(s),
    DB.prepare("SELECT COUNT(*) n FROM events WHERE kind='copy' AND day >= ?").bind(s),
    DB.prepare("SELECT COUNT(*) n FROM submissions WHERE day >= ?").bind(s),
  ];
  const q = [
    ...kq(today), ...kq(d7), ...kq(d30),
    DB.prepare("SELECT day, COUNT(*) n FROM pageviews WHERE day >= ? GROUP BY day").bind(since),
    DB.prepare("SELECT day, COUNT(*) n FROM clicks WHERE day >= ? GROUP BY day").bind(since),
    DB.prepare("SELECT path, COUNT(*) n, " + U + " u FROM pageviews WHERE day >= ? GROUP BY path ORDER BY n DESC LIMIT 25").bind(since),
    DB.prepare("SELECT ref_host, COUNT(*) n, " + U + " u FROM pageviews WHERE day >= ? AND ref_host != '' GROUP BY ref_host ORDER BY n DESC LIMIT 20").bind(since),
    DB.prepare("SELECT utm_source||' / '||utm_medium||' / '||utm_campaign k, COUNT(*) n, " + U + " u FROM pageviews WHERE day >= ? AND utm_source != '' GROUP BY k ORDER BY n DESC LIMIT 15").bind(since),
    DB.prepare("SELECT country, COUNT(*) n, " + U + " u FROM pageviews WHERE day >= ? GROUP BY country ORDER BY n DESC LIMIT 20").bind(since),
    DB.prepare("SELECT device, COUNT(*) n, " + U + " u FROM pageviews WHERE day >= ? GROUP BY device ORDER BY n DESC").bind(since),
    DB.prepare("SELECT lang, COUNT(*) n FROM pageviews WHERE day >= ? GROUP BY lang ORDER BY n DESC LIMIT 8").bind(since),
    DB.prepare("SELECT firm, COUNT(*) n, " + U + " u, MAX(dest_kind) k, SUM(code != '') c FROM clicks WHERE day >= ? GROUP BY firm ORDER BY n DESC LIMIT 60").bind(since),
    DB.prepare("SELECT src, COUNT(*) n, " + U + " u FROM clicks WHERE day >= ? GROUP BY src ORDER BY n DESC LIMIT 25").bind(since),
    DB.prepare("SELECT pos, COUNT(*) n, " + U + " u FROM clicks WHERE day >= ? GROUP BY pos ORDER BY n DESC").bind(since),
    DB.prepare("WITH v AS (SELECT path, COUNT(*) n, " + U + " u FROM pageviews WHERE day >= ?1 AND path LIKE '/firms/_%/' GROUP BY path), c AS (SELECT src, COUNT(*) n, " + U + " u FROM clicks WHERE day >= ?1 AND src LIKE '/firms/_%/' GROUP BY src) SELECT v.path, v.n vn, v.u vu, COALESCE(c.n,0) cn, COALESCE(c.u,0) cu FROM v LEFT JOIN c ON c.src = v.path ORDER BY v.n DESC LIMIT 40").bind(since),
    DB.prepare("SELECT firm, code, COUNT(*) n, " + U + " u FROM events WHERE kind='copy' AND day >= ? GROUP BY firm, code ORDER BY n DESC LIMIT 25").bind(since),
    DB.prepare("SELECT target_host, COUNT(*) n FROM events WHERE kind='out' AND day >= ? GROUP BY target_host ORDER BY n DESC LIMIT 15").bind(since),
    DB.prepare("SELECT kind||' / '||reason k, SUM(n) n FROM bot_hits WHERE day >= ? GROUP BY k ORDER BY n DESC").bind(since),
    DB.prepare("SELECT status, COUNT(*) n FROM submissions GROUP BY status").bind(),
    DB.prepare("SELECT id, ts, kind, firm, email, status, note, payload, page, country, notified FROM submissions " + (sf ? "WHERE status = ? " : "WHERE status NOT IN ('spam') ") + "ORDER BY ts DESC LIMIT 60").bind(...(sf ? [sf] : [])),
  ];
  const res = (await DB.batch(q)).map((x) => x.results);
  const k = (i) => ({ pv: res[i][0], ck: res[i + 1][0], cp: res[i + 2][0].n, sb: res[i + 3][0].n });
  const K = [["Today", k(0)], ["7 days", k(4)], ["30 days", k(8)]];
  let i = 12;
  const take = () => res[i++];
  const pvDay = Object.fromEntries(take().map((x) => [x.day, x.n])), ckDay = Object.fromEntries(take().map((x) => [x.day, x.n]));
  const [pages, refs, utm, ctry, dev, lang, byFirm, bySrc, byPos, ctr, copies, outs, bots, stCount, subs] = Array.from({ length: 15 }, take);
  const days = []; for (let j = r - 1; j >= 0; j--) days.push(daysAgo(j, env));
  const firmName = (s) => s;
  const totPv = Object.values(pvDay).reduce((a, b) => a + b, 0) || 1, totCk = byFirm.reduce((a, b) => a + b.n, 0) || 1;
  const sel = K[r === 1 ? 0 : r === 30 ? 2 : 1][1];

  const kpi = '<section class="card wide kpis"><table><thead><tr><th></th><th class="n">Page views</th><th class="n">Visitors<sup>*</sup></th><th class="n">Outbound clicks</th><th class="n">Clicking visitors</th><th class="n">Click-through</th><th class="n">Promo copies</th><th class="n">Submissions</th></tr></thead><tbody>' +
    K.map(([l, x]) => "<tr><th>" + l + '</th><td class="n big">' + n0(x.pv.n) + '</td><td class="n big">' + n0(x.pv.u) + '</td><td class="n big">' + n0(x.ck.n) + '</td><td class="n">' + n0(x.ck.u) + '</td><td class="n">' + pct(x.ck.u, x.pv.u) + '</td><td class="n">' + n0(x.cp) + '</td><td class="n">' + n0(x.sb) + "</td></tr>").join("") +
    '</tbody></table><p class="foot">* Visitors are counted per day (the anonymous hash changes daily), so 7/30-day figures are the sum of daily uniques. Click-through = clicking visitors / visitors. Bot and DNT/GPC traffic excluded from visitor counts.</p></section>';

  const sc = Object.fromEntries(stCount.map((x) => [x.status, x.n]));
  const inbox = '<section class="card wide" id="inbox"><h2>Submissions inbox <small>' + STATUSES.map((s) => '<a href="?r=' + r + "&s=" + s + '#inbox"' + (sf === s ? ' class="on"' : "") + ">" + s + " " + n0(sc[s]) + "</a>").join(" ") + ' <a href="?r=' + r + '#inbox"' + (!sf ? ' class="on"' : "") + ">all open</a></small></h2>" +
    (subs.length ? subs.map((s) => {
      let pl = {}; try { pl = JSON.parse(s.payload); } catch {}
      const fields = Object.entries(pl).map(([a, b]) => "<dt>" + esc(a) + "</dt><dd>" + esc(b) + "</dd>").join("");
      return '<details class="sub st-' + esc(s.status) + '" id="sub-' + s.id + '"' + (s.status === "new" ? " open" : "") + "><summary><b>#" + s.id + "</b> <span class=\"tag\">" + esc(s.kind) + "</span> " + esc(s.firm || "(no firm)") + ' <span class="mute">' + esc(new Date(s.ts).toISOString().slice(0, 16).replace("T", " ")) + " UTC" + (s.country ? " · " + esc(s.country) : "") + (s.notified ? " · emailed" : "") + '</span><span class="st">' + esc(s.status) + "</span></summary>" +
        '<dl>' + (s.email ? '<dt>email</dt><dd><a href="mailto:' + esc(s.email) + '">' + esc(s.email) + "</a></dd>" : "") + fields + (s.page ? "<dt>page</dt><dd>" + esc(s.page) + "</dd>" : "") + "</dl>" +
        '<form method="post" action="/admin/sub/' + s.id + "?r=" + r + (sf ? "&s=" + sf : "") + '" class="stf"><select name="status">' + STATUSES.map((x) => "<option" + (x === s.status ? " selected" : "") + ">" + x + "</option>").join("") + '</select><input name="note" placeholder="Internal note" value="' + esc(s.note) + '"><button>Save</button></form></details>';
    }).join("") : '<p class="empty">Nothing here.</p>') + "</section>";

  const body = [
    kpi, chart(days, pvDay, ckDay),
    table("Outbound clicks by firm", ["Firm", "Clicks", "Visitors", "Goes to", "With code", "Share"], byFirm.map((x) => [firmName(x.firm), x.n, x.u, x.k, x.c, pct(x.n, totCk)])),
    table("Click-through per firm page", ["Firm page", "Views", "Clicks", "CTR (clicks/views)", "CTR (visitors)"], ctr.map((x) => [x.path.replace(/^\/firms\/|\/$/g, ""), x.vn, x.cn, pct(x.cn, x.vn), pct(x.cu, x.vu)]), { note: "clicks whose src is that firm page" }),
    table("Clicks by source page", ["Page", "Clicks", "Visitors"], bySrc.map((x) => [x.src, x.n, x.u])),
    table("Clicks by slot", ["Slot", "Clicks", "Visitors", "Share"], byPos.map((x) => [x.pos, x.n, x.u, pct(x.n, totCk)])),
    table("Promo codes copied", ["Firm / code", "Copies", "Visitors"], copies.map((x) => [(x.firm || "?") + " · " + x.code, x.n, x.u])),
    table("Top pages", ["Page", "Views", "Visitors", "Share"], pages.map((x) => [x.path, x.n, x.u, pct(x.n, totPv)])),
    table("Top referrers", ["Site", "Type", "Views", "Visitors"], refs.map((x) => [x.ref_host, refType(x.ref_host), x.n, x.u]), { bar: 2 }),
    table("Campaigns (utm)", ["source / medium / campaign", "Views", "Visitors"], utm.map((x) => [x.k, x.n, x.u])),
    table("Countries", ["Country", "Views", "Visitors", "Share"], ctry.map((x) => [x.country || "??", x.n, x.u, pct(x.n, totPv)])),
    table("Devices", ["Device", "Views", "Visitors", "Share"], dev.map((x) => [x.device, x.n, x.u, pct(x.n, totPv)])),
    table("Languages", ["Page lang", "Views"], lang.map((x) => [x.lang || "?", x.n])),
    table("Other outbound links", ["Host", "Clicks"], outs.map((x) => [x.target_host, x.n]), { note: "non-firm links, via beacon" }),
    table("Bot / prefetch hits filtered", ["Kind / reason", "Hits"], bots.map((x) => [x.k, x.n])),
    inbox,
  ].join("");

  const tabs = Object.entries(RANGES).map(([v, l]) => '<a href="?r=' + v + '"' + (+v === r ? ' class="on" aria-current="page"' : "") + ">" + l + "</a>").join("");
  const exp = Object.keys(TABLES).map((t) => '<a href="/admin/export.csv?t=' + t + "&r=" + r + '">' + t + ".csv</a>").join("");
  const html = '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>PropAnalyse admin · ' + RANGES[r] + "</title><style>" + CSS + "</style></head><body>" +
    '<header><div class="brand"><span class="logo">P</span><b>PropAnalyse</b> <span class="mute">analytics</span></div><nav class="tabs">' + tabs + '</nav><div class="exp"><span class="mute">CSV:</span>' + exp + "</div></header><main>" +
    '<p class="meta">Range: <b>' + RANGES[r] + "</b> (" + esc(since) + " → " + esc(today) + ', MYT). ' + n0(sel.pv.n) + " views · " + n0(sel.ck.n) + " clicks</p>" + body +
    '</main><footer class="mute">Cookieless, no raw IPs. Data: Cloudflare D1. <a href="https://propanalyse.com/privacy/">Privacy notice</a></footer></body></html>';
  return new Response(html, { headers: { ...SEC, "Content-Type": "text/html; charset=utf-8" } });
}

const CSS = String.raw`@font-face{font-family:IS;src:url(https://propanalyse.com/assets/fonts/instrument-sans.woff2) format("woff2");font-display:swap}
:root{--bg:#f5f6f8;--card:#fff;--ink:#0b1730;--ink2:#34415e;--mute:#5a6680;--rule:#e3e6ec;--acc:#3424f8;--tint:#efeeff;--ck:#f2a23a;--good:#1a8a4a}
@media (prefers-color-scheme:dark){:root{--bg:#121b2e;--card:#18233a;--ink:#eef1f8;--ink2:#c8cfdf;--mute:#a3adc4;--rule:#2a3754;--acc:#9a94ff;--tint:rgba(154,148,255,.16)}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.45 IS,system-ui,-apple-system,"Segoe UI",sans-serif}
a{color:var(--acc)}header{display:flex;flex-wrap:wrap;gap:12px 24px;align-items:center;padding:12px 24px;background:var(--card);border-bottom:1px solid var(--rule);position:sticky;top:0;z-index:2}
.brand{display:flex;gap:8px;align-items:center;font-size:16px}.logo{display:inline-grid;place-items:center;width:28px;height:28px;border-radius:7px;background:var(--acc);color:#fff;font-weight:700}
.tabs{display:flex;gap:4px}.tabs a,.inbox a,h2 small a{padding:4px 10px;border-radius:999px;text-decoration:none;color:var(--ink2);border:1px solid var(--rule)}.tabs a.on,h2 small a.on{background:var(--acc);color:#fff;border-color:var(--acc)}
.exp{margin-left:auto;display:flex;gap:10px;font-size:13px}main{display:grid;grid-template-columns:repeat(auto-fill,minmax(420px,1fr));gap:16px;padding:16px 24px;max-width:1500px;margin:0 auto}
.meta{grid-column:1/-1;margin:0;color:var(--mute)}.card{background:var(--card);border:1px solid var(--rule);border-radius:10px;padding:14px 16px;min-width:0;box-shadow:0 1px 2px rgba(11,23,48,.05)}.wide{grid-column:1/-1}
h2{font-size:14px;margin:0 0 10px;letter-spacing:.01em}h2 small{font-weight:400;color:var(--mute);font-size:12px;margin-left:6px}table{width:100%;border-collapse:collapse}
th,td{padding:5px 6px;border-bottom:1px solid var(--rule);text-align:left;vertical-align:top}th{font-size:12px;color:var(--mute);font-weight:600}.n{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
td.k{position:relative;max-width:0;width:55%}td.k .lbl{position:relative;display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.bar{position:absolute;left:0;top:3px;bottom:3px;background:var(--tint);border-radius:3px}
.kpis td.big{font-size:22px;font-weight:700}.kpis th{font-size:13px}.foot{color:var(--mute);font-size:12px;margin:8px 0 0}.empty{color:var(--mute);text-align:center;padding:14px}
.chart{width:100%;height:150px;display:block}.chart .pv{fill:var(--acc);opacity:.85}.chart .ck{fill:var(--ck)}.axis{display:flex;justify-content:space-between;color:var(--mute);font-size:12px}.sw{display:inline-block;width:10px;height:10px;border-radius:2px;margin:0 4px 0 10px;vertical-align:-1px}.sw.pv{background:var(--acc)}.sw.ck{background:var(--ck)}
.sub{border:1px solid var(--rule);border-radius:8px;margin:8px 0;padding:8px 12px}.sub summary{cursor:pointer;display:flex;gap:8px;align-items:center;flex-wrap:wrap}.tag{background:var(--tint);color:var(--acc);border-radius:4px;padding:1px 6px;font-size:12px}
.st{margin-left:auto;font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:.04em}.st-new .st{color:#d23}.st-resolved .st{color:var(--good)}.mute{color:var(--mute)}
dl{display:grid;grid-template-columns:140px 1fr;gap:4px 12px;margin:10px 0}dt{color:var(--mute)}dd{margin:0;white-space:pre-wrap;word-break:break-word}.stf{display:flex;gap:8px}.stf input{flex:1}
select,input,button{font:inherit;padding:5px 8px;border:1px solid var(--rule);border-radius:6px;background:var(--card);color:var(--ink)}button{background:var(--acc);color:#fff;border-color:var(--acc);cursor:pointer}
footer{padding:16px 24px 32px;text-align:center;font-size:12px}@media (max-width:520px){main{grid-template-columns:1fr;padding:12px}header{padding:10px 12px}.kpis{overflow-x:auto}.kpis td.big{font-size:17px}}`;
