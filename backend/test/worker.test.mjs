// End-to-end tests against a real local Worker (wrangler dev --local, D1 in a temp dir).
// Run: cd backend && npm test   (needs wrangler on PATH or in node_modules; no Cloudflare login)
import { test, before, after } from "node:test";
import assert from "node:assert/strict";
import { spawn, execFileSync } from "node:child_process";
import { mkdtempSync, rmSync, existsSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const DIR = join(dirname(fileURLToPath(import.meta.url)), "..");
const WR = existsSync(join(DIR, "node_modules/.bin/wrangler")) ? join(DIR, "node_modules/.bin/wrangler") : "wrangler";
const PORT = 8799 + Math.floor(Math.random() * 100), BASE = "http://127.0.0.1:" + PORT, TOKEN = "test-token-" + Math.random().toString(36).slice(2);
const ORIGIN = "https://propanalyse.com";
const STATE = mkdtempSync(join(tmpdir(), "pa-d1-"));
const ENV = { ...process.env, CI: "1", WRANGLER_SEND_METRICS: "false", NO_COLOR: "1" };
const EXTRA = JSON.stringify({ "test-aff": { name: "Aff Firm", site: "https://aff-firm.example/", aff: "https://aff-firm.example/?ref=propanalyse" }, "bad-aff": { name: "Bad", site: "https://bad.example/", aff: "javascript:alert(1)" } });
const BROWSER = { "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1", "accept-language": "en-MY,en;q=0.9", referer: "https://propanalyse.com/firms/ftmo/", "cf-connecting-ip": "203.0.113.77" };
const DESKTOP = { ...BROWSER, "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0 Safari/537.36" };
const AUTH = { authorization: "Basic " + Buffer.from("admin:" + TOKEN).toString("base64") };
let proc, logs = "";

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const get = (p, headers = {}, method = "GET") => fetch(BASE + p, { method, headers, redirect: "manual" });
async function csv(t) { const r = await get("/admin/export.csv?t=" + t + "&r=1", AUTH); assert.equal(r.status, 200); const lines = (await r.text()).trim().split(/\r\n/); const cols = lines[0].split(","); return lines.slice(1).map((l) => Object.fromEntries(l.split(",").map((v, i) => [cols[i], v]))); }
async function until(fn, ms = 4000) { const t0 = Date.now(); let v; while (Date.now() - t0 < ms) { v = await fn(); if (v) return v; await sleep(150); } return v; }

before(async () => {
  execFileSync(WR, ["d1", "migrations", "apply", "DB", "--local", "--persist-to", STATE], { cwd: DIR, env: ENV, stdio: "pipe" });
  proc = spawn(WR, ["dev", "--local", "--ip", "127.0.0.1", "--port", String(PORT), "--persist-to", STATE, "--var", "ADMIN_TOKEN:" + TOKEN, "--var", "FIRMS_EXTRA:" + EXTRA, "--show-interactive-dev-session=false"], { cwd: DIR, env: ENV });
  proc.stdout.on("data", (d) => (logs += d)); proc.stderr.on("data", (d) => (logs += d));
  const ok = await until(async () => { try { return (await fetch(BASE + "/health")).ok; } catch { return false; } }, 60000);
  if (!ok) throw new Error("wrangler dev did not start:\n" + logs);
});
after(() => { proc && proc.kill("SIGTERM"); rmSync(STATE, { recursive: true, force: true }); });

// ---- redirects ----
test("known firm without affiliate -> 302 to official site, no-store", async () => {
  const r = await get("/ftmo?src=/firms/ftmo/&pos=firm-page", BROWSER);
  assert.equal(r.status, 302);
  assert.equal(r.headers.get("location"), "https://ftmo.com/");
  assert.match(r.headers.get("cache-control"), /no-store/);
  assert.match(r.headers.get("x-robots-tag"), /noindex/);
});
test("affiliate_url wins over site", async () => {
  const r = await get("/test-aff?src=/&pos=table", DESKTOP);
  assert.equal(r.status, 302); assert.equal(r.headers.get("location"), "https://aff-firm.example/?ref=propanalyse");
});
test("non-http affiliate url is ignored (falls back to site)", async () => {
  const r = await get("/bad-aff", DESKTOP); assert.equal(r.headers.get("location"), "https://bad.example/");
});
test("unknown / malformed slug and root -> home", async () => {
  for (const p of ["/no-such-firm", "/FTMO%3Cscript%3E", "/", "/a/b", "/..%2f"]) {
    const r = await get(p, DESKTOP); assert.equal(r.status, 302, p); assert.equal(r.headers.get("location"), "https://propanalyse.com/", p);
  }
});
test("slug is case-insensitive", async () => { assert.equal((await get("/FTMO", DESKTOP)).headers.get("location"), "https://ftmo.com/"); });

// ---- click logging ----
test("click is logged with src, pos, code, device, ref host, hashed visitor and no raw IP", async () => {
  await get("/fundingpips?src=/offers/&pos=offer-card&code=HALLOWEEN", BROWSER);
  const row = await until(async () => (await csv("clicks")).find((c) => c.firm === "fundingpips"));
  assert.ok(row, "click row missing");
  assert.equal(row.src, "/offers/"); assert.equal(row.pos, "offer-card"); assert.equal(row.code, "HALLOWEEN");
  assert.equal(row.dest_kind, "site"); assert.equal(row.device, "mobile"); assert.equal(row.ref_host, "propanalyse.com");
  assert.match(row.visitor, /^[0-9a-f]{16}$/);
  const all = await (await get("/admin/export.csv?t=clicks&r=1", AUTH)).text();
  assert.ok(!all.includes("203.0.113.77"), "raw IP leaked");
});
test("same browser same day -> same visitor hash; different UA -> different", async () => {
  await get("/the5ers?src=/&pos=table", BROWSER); await get("/the5ers?src=/&pos=table", BROWSER); await get("/the5ers?src=/&pos=table", DESKTOP);
  const rows = await until(async () => { const r = (await csv("clicks")).filter((c) => c.firm === "the5ers"); return r.length >= 3 && r; });
  assert.equal(rows.length, 3);
  assert.equal(rows[0].visitor, rows[1].visitor); assert.notEqual(rows[0].visitor, rows[2].visitor);
});
test("DNT / GPC click: still redirects, logged without visitor hash", async () => {
  const r = await get("/hyrotrader?src=/crypto/&pos=table", { ...DESKTOP, dnt: "1" });
  assert.equal(r.status, 302);
  const row = await until(async () => (await csv("clicks")).find((c) => c.firm === "hyrotrader"));
  assert.ok(row); assert.equal(row.visitor, "");
});
test("junk query params are sanitised", async () => {
  await get("/breakout-prop?src=javascript:alert(1)&pos=%3Cb%3E&code=" + "X".repeat(200), DESKTOP);
  const row = await until(async () => (await csv("clicks")).find((c) => c.firm === "breakout-prop"));
  assert.equal(row.src, ""); assert.equal(row.pos, "b"); assert.equal(row.code.length, 40);
});

// ---- bot filter ----
test("bots, HEAD, prefetch and header-less clients redirect but are not logged", async () => {
  const bots = [
    [{ "user-agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)", "accept-language": "en" }, "GET"],
    [{ "user-agent": "curl/8.7.1" }, "GET"],
    [{ "user-agent": "WhatsApp/2.23.20.0 A", "accept-language": "en" }, "GET"],
    [{ "user-agent": "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)", "accept-language": "en" }, "GET"],
    [{ "user-agent": DESKTOP["user-agent"] }, "GET"],                                   // no Accept-Language
    [DESKTOP, "HEAD"],
    [{ ...DESKTOP, "sec-purpose": "prefetch" }, "GET"],
    [{ "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 HeadlessChrome/120.0 Safari/537.36", "accept-language": "en" }, "GET"],
  ];
  for (const [h, m] of bots) { const r = await get("/fundednext?src=/&pos=table", h, m); assert.equal(r.status, 302); assert.equal(r.headers.get("location"), "https://fundednext.com/"); }
  await sleep(800);
  assert.equal((await csv("clicks")).filter((c) => c.firm === "fundednext").length, 0, "bot click logged");
  const dash = await (await get("/admin?r=1", AUTH)).text();
  for (const reason of ["click / ua", "click / head", "click / nolang", "click / prefetch", "click / noua"]) assert.ok(dash.includes(reason), "bot reason missing: " + reason);
});

// ---- beacon ----
const beacon = (body, h = {}) => fetch(BASE + "/e", { method: "POST", headers: { ...DESKTOP, origin: ORIGIN, "content-type": "text/plain;charset=UTF-8", ...h }, body: typeof body === "string" ? body : JSON.stringify(body) });
test("beacon pageview is stored (path, ref host, utm, lang, device)", async () => {
  const r = await beacon({ t: "pv", p: "/firms/ftmo/?x=1", r: "www.Google.com", us: "newsletter", um: "email", uc: "oct", l: "en" });
  assert.equal(r.status, 204); assert.equal(r.headers.get("access-control-allow-origin"), ORIGIN);
  const row = (await csv("pageviews")).find((p) => p.path === "/firms/ftmo/");
  assert.ok(row); assert.equal(row.ref_host, "google.com"); assert.equal(row.utm_source, "newsletter"); assert.equal(row.utm_campaign, "oct"); assert.equal(row.lang, "en"); assert.equal(row.device, "desktop"); assert.match(row.visitor, /^[0-9a-f]{16}$/);
});
test("beacon copy + out events", async () => {
  assert.equal((await beacon({ t: "copy", p: "/offers/", f: "fundingpips", c: "HALLOWEEN" })).status, 204);
  assert.equal((await beacon({ t: "out", p: "/firms/ftmo/", h: "ftmo.com", f: "ftmo" })).status, 204);
  const ev = await csv("events");
  assert.ok(ev.find((e) => e.kind === "copy" && e.firm === "fundingpips" && e.code === "HALLOWEEN"));
  assert.ok(ev.find((e) => e.kind === "out" && e.target_host === "ftmo.com"));
});
test("beacon rejects: foreign origin 403, no origin 403, oversized 413, bad json 400, unknown type 400", async () => {
  assert.equal((await beacon({ t: "pv", p: "/" }, { origin: "https://evil.example" })).status, 403);
  assert.equal((await fetch(BASE + "/e", { method: "POST", headers: DESKTOP, body: "{}" })).status, 403);
  assert.equal((await beacon("x".repeat(5000))).status, 413);
  assert.equal((await beacon("not json")).status, 400);
  assert.equal((await beacon({ t: "zzz", p: "/" })).status, 400);
});
test("beacon drops DNT/GPC and bots silently", async () => {
  await beacon({ t: "pv", p: "/dnt-test/" }, { dnt: "1" });
  await beacon({ t: "pv", p: "/gpc-test/" }, { "sec-gpc": "1" });
  await beacon({ t: "pv", p: "/bot-test/" }, { "user-agent": "Mozilla/5.0 (compatible; bingbot/2.0)" });
  const pv = await csv("pageviews");
  assert.ok(!pv.some((p) => /dnt-test|gpc-test|bot-test/.test(p.path)));
});
test("beacon CORS preflight", async () => {
  const r = await fetch(BASE + "/e", { method: "OPTIONS", headers: { origin: ORIGIN, "access-control-request-method": "POST" } });
  assert.equal(r.status, 204); assert.equal(r.headers.get("access-control-allow-origin"), ORIGIN);
});

// ---- forms ----
const form = (body, h = {}) => fetch(BASE + "/f", { method: "POST", headers: { ...DESKTOP, origin: ORIGIN, "content-type": "application/json", ...h }, body: JSON.stringify(body) });
let subId;
test("complaint submission stored and returns id", async () => {
  const r = await form({ kind: "complaint", firm: "ftmo", email: "trader@example.com", fields: { type: "Payout denied", desc: "Payout of $1,200 refused after 3 weeks <script>x</script>", date: "2026-10-20" }, page: "/complaints/", lang: "en" });
  assert.equal(r.status, 200); const j = await r.json(); assert.equal(j.ok, true); assert.ok(j.id > 0); subId = j.id;
  const s = (await csv("submissions")).find((x) => +x.id === subId); assert.equal(s.kind, "complaint"); assert.equal(s.status, "new"); assert.equal(s.email, "trader@example.com");
});
test("form validation: missing email on complaint, bad kind, empty fields -> 400; honeypot -> fake ok, not stored", async () => {
  assert.equal((await form({ kind: "complaint", firm: "ftmo", fields: { desc: "x" } })).status, 400);
  assert.equal((await form({ kind: "hack", fields: { a: "b" } })).status, 400);
  assert.equal((await form({ kind: "correction", fields: {} })).status, 400);
  const before = (await csv("submissions")).length;
  const hp = await form({ kind: "correction", firm: "x", fields: { a: "spam" }, hp: "http://spam" }); assert.equal(hp.status, 200);
  assert.equal((await csv("submissions")).length, before);
  assert.equal((await form({ kind: "correction", fields: { a: "b" } }, { origin: "https://evil.example" })).status, 403);
});
test("listing + correction submissions accepted without email", async () => {
  assert.equal((await form({ kind: "listing", firm: "New Firm Ltd", fields: { notes: "Please list us", src: "https://newfirm.example" } })).status, 200);
  assert.equal((await form({ kind: "correction", firm: "FTMO", fields: { field: "Max drawdown", value: "10%" } })).status, 200);
});

// ---- admin ----
test("admin requires basic auth; wrong token rejected", async () => {
  const a = await get("/admin"); assert.equal(a.status, 401); assert.match(a.headers.get("www-authenticate"), /Basic/);
  const b = await get("/admin", { authorization: "Basic " + Buffer.from("admin:wrong").toString("base64") }); assert.equal(b.status, 401);
  const c = await get("/admin/export.csv?t=clicks"); assert.equal(c.status, 401);
});
test("admin dashboard renders sections with data and escapes user content", async () => {
  const r = await get("/admin?r=7", AUTH); assert.equal(r.status, 200);
  assert.match(r.headers.get("cache-control"), /no-store/); assert.match(r.headers.get("content-security-policy"), /default-src 'none'/);
  const h = await r.text();
  for (const s of ["Outbound clicks by firm", "Click-through per firm page", "Clicks by slot", "Promo codes copied", "Top pages", "Top referrers", "Countries", "Devices", "Submissions inbox", "fundingpips", "offer-card", "HALLOWEEN"]) assert.ok(h.includes(s), "missing " + s);
  assert.ok(!h.includes("<script>x</script>")); assert.ok(h.includes("&lt;script&gt;x&lt;/script&gt;"));
});
test("admin CSV export", async () => {
  const r = await get("/admin/export.csv?t=pageviews&r=30", AUTH);
  assert.match(r.headers.get("content-type"), /text\/csv/); assert.match(r.headers.get("content-disposition"), /attachment/);
  assert.match((await r.text()).split("\r\n")[0], /^id,ts,day,path/);
  assert.equal((await get("/admin/export.csv?t=salts", AUTH)).status, 400);
});
test("admin status update needs same-origin POST", async () => {
  const body = new URLSearchParams({ status: "resolved", note: "Firm paid" });
  const bad = await fetch(BASE + "/admin/sub/" + subId, { method: "POST", headers: { ...AUTH, origin: "https://evil.example", "content-type": "application/x-www-form-urlencoded" }, body, redirect: "manual" });
  assert.equal(bad.status, 403);
  const ok = await fetch(BASE + "/admin/sub/" + subId, { method: "POST", headers: { ...AUTH, origin: BASE, "content-type": "application/x-www-form-urlencoded" }, body, redirect: "manual" });
  assert.equal(ok.status, 303);
  const s = (await csv("submissions")).find((x) => +x.id === subId); assert.equal(s.status, "resolved"); assert.equal(s.note, "Firm paid");
});
test("robots.txt disallows everything; health ok", async () => {
  assert.match(await (await get("/robots.txt")).text(), /Disallow: \//);
  const j = await (await get("/health")).json(); assert.equal(j.ok, true); assert.ok(j.firms >= 40);
});
