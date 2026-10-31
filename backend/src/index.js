// PropAnalyse go.propanalyse.com Worker: outbound click redirects, cookieless pageview beacon,
// form intake and a password-protected admin dashboard. Storage: Cloudflare D1 (binding DB).
import FIRMS_GEN from "./firms.gen.json";
import { botReason, deviceClass, country, dayOf, daysAgo, refHost, cleanHost, cleanPath, cleanSlug, cleanTok, cleanText, httpUrl, visitorId, bumpBot, optedOut } from "./lib.js";
import { admin } from "./admin.js";

let firmsCache = null;
export function firms(env) {
  if (firmsCache && firmsCache.key === (env.FIRMS_EXTRA || "")) return firmsCache.map;
  let map = { ...(FIRMS_GEN.firms || FIRMS_GEN) };
  if (env.FIRMS_EXTRA) { try { Object.assign(map, JSON.parse(env.FIRMS_EXTRA)); } catch {} }
  firmsCache = { key: env.FIRMS_EXTRA || "", map };
  return map;
}

const home = (env) => env.SITE_HOME || "https://propanalyse.com/";
const SUB_KINDS = new Set(["complaint", "listing", "correction", "review", "status-review", "other"]);

function origins(env) { return (env.SITE_ORIGINS || "https://propanalyse.com").split(",").map((s) => s.trim()).filter(Boolean); }
function cors(req, env) {
  const o = req.headers.get("origin");
  const h = { "Vary": "Origin" };
  if (o && origins(env).includes(o)) Object.assign(h, { "Access-Control-Allow-Origin": o, "Access-Control-Allow-Methods": "POST, OPTIONS", "Access-Control-Allow-Headers": "Content-Type", "Access-Control-Max-Age": "86400" });
  return h;
}
const json = (obj, status = 200, headers = {}) => new Response(JSON.stringify(obj), { status, headers: { "Content-Type": "application/json", "Cache-Control": "no-store", ...headers } });

function redirect(to) {
  return new Response(null, { status: 302, headers: { Location: to, "Cache-Control": "no-store, max-age=0", "X-Robots-Tag": "noindex, nofollow", "Referrer-Policy": "strict-origin-when-cross-origin" } });
}

async function readBody(req, max) {
  const len = parseInt(req.headers.get("content-length") || "0", 10);
  if (len > max) return { tooBig: true };
  const t = await req.text();
  if (t.length > max) return { tooBig: true };
  try { return { data: JSON.parse(t) }; } catch { return { bad: true }; }
}

// ---------- 1. outbound click: /<slug>?src=&pos=&code= ----------
async function click(req, env, ctx, slugRaw, url) {
  const slug = cleanSlug(slugRaw.toLowerCase());
  const f = slug ? firms(env)[slug] : null;
  let dest = home(env), kind = "home";
  if (f) {
    const aff = httpUrl(f.aff), site = httpUrl(f.site);
    if (aff) { dest = aff; kind = "affiliate"; } else if (site) { dest = site; kind = "site"; }
  }
  const now = Date.now(), day = dayOf(now, env);
  const job = (async () => {
    const bot = botReason(req, "click");
    if (bot) return bumpBot(env, day, "click", bot);
    const q = url.searchParams;
    const vis = await visitorId(req, env, day);
    await env.DB.prepare("INSERT INTO clicks(ts, day, firm, dest_kind, src, pos, code, country, device, ref_host, visitor) VALUES(?,?,?,?,?,?,?,?,?,?,?)")
      .bind(now, day, slug || cleanTok(slugRaw, 64) || "(none)", kind, cleanPath(q.get("src") || ""), cleanTok(q.get("pos") || "", 32).toLowerCase(), cleanTok(q.get("code") || "", 40),
        country(req), deviceClass(req.headers.get("user-agent") || ""), refHost(req.headers.get("referer")), vis).run();
  })().catch((e) => console.error("click log failed", e));
  ctx.waitUntil(job);
  return redirect(dest);
}

// ---------- 2. beacon: POST /e ----------
async function beacon(req, env) {
  const h = cors(req, env);
  const o = req.headers.get("origin");
  if (!o || !origins(env).includes(o)) return new Response(null, { status: 403, headers: h });
  const b = await readBody(req, 2048);
  if (b.tooBig) return new Response(null, { status: 413, headers: h });
  if (b.bad || !b.data || typeof b.data !== "object") return new Response(null, { status: 400, headers: h });
  if (optedOut(req)) return new Response(null, { status: 204, headers: h });            // DNT / GPC: store nothing
  const now = Date.now(), day = dayOf(now, env);
  const bot = botReason(req, "beacon");
  if (bot) { await bumpBot(env, day, "beacon", bot); return new Response(null, { status: 204, headers: h }); }
  const d = b.data, ua = req.headers.get("user-agent") || "", dev = deviceClass(ua), cc = country(req);
  const vis = await visitorId(req, env, day);
  const path = cleanPath(d.p) || "/";
  if (d.t === "pv") {
    await env.DB.prepare("INSERT INTO pageviews(ts, day, path, ref_host, utm_source, utm_medium, utm_campaign, lang, device, country, visitor) VALUES(?,?,?,?,?,?,?,?,?,?,?)")
      .bind(now, day, path, cleanHost(d.r), cleanTok(d.us).toLowerCase(), cleanTok(d.um).toLowerCase(), cleanTok(d.uc).toLowerCase(), cleanTok(d.l, 10), dev, cc, vis).run();
  } else if (d.t === "copy" || d.t === "out") {
    await env.DB.prepare("INSERT INTO events(ts, day, kind, firm, code, path, target_host, country, device, visitor) VALUES(?,?,?,?,?,?,?,?,?,?)")
      .bind(now, day, d.t, cleanSlug(d.f), cleanTok(d.c, 40), path, d.t === "out" ? cleanHost(d.h) : "", cc, dev, vis).run();
  } else return new Response(null, { status: 400, headers: h });
  return new Response(null, { status: 204, headers: h });
}

// ---------- 3. forms: POST /f ----------
async function form(req, env, ctx) {
  const h = cors(req, env);
  const o = req.headers.get("origin");
  if (!o || !origins(env).includes(o)) return json({ ok: false, error: "origin" }, 403, h);
  const b = await readBody(req, 16384);
  if (b.tooBig) return json({ ok: false, error: "too_large" }, 413, h);
  if (b.bad || !b.data || typeof b.data !== "object") return json({ ok: false, error: "bad_json" }, 400, h);
  const d = b.data;
  if (d.hp) return json({ ok: true, id: 0 }, 200, h);                          // honeypot: pretend success
  const kind = SUB_KINDS.has(d.kind) ? d.kind : null;
  const email = cleanText(d.email, 200);
  const fields = {};
  if (d.fields && typeof d.fields === "object") for (const [k, v] of Object.entries(d.fields).slice(0, 30)) fields[cleanTok(k, 40)] = cleanText(v);
  const text = Object.values(fields).join("").trim();
  const missing = [];
  if (!kind) missing.push("kind");
  if (!text) missing.push("fields");
  if (kind === "complaint" && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) missing.push("email");
  if (email && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) missing.push("email");
  if (missing.length) return json({ ok: false, error: "missing", fields: [...new Set(missing)] }, 400, h);
  const now = Date.now(), day = dayOf(now, env);
  const vis = await visitorId({ headers: new Headers([...req.headers].filter(([k]) => k !== "dnt" && k !== "sec-gpc")) }, env, day); // rate-limit key only
  const n = await env.DB.prepare("SELECT COUNT(*) AS n FROM submissions WHERE day=? AND visitor=?").bind(day, vis).first();
  if (n && n.n >= 8) return json({ ok: false, error: "rate_limited" }, 429, h);
  const firm = cleanTok(d.firm, 80);
  const r = await env.DB.prepare("INSERT INTO submissions(ts, day, kind, firm, email, payload, page, lang, country, visitor) VALUES(?,?,?,?,?,?,?,?,?,?) RETURNING id")
    .bind(now, day, kind, firm, email, JSON.stringify(fields), cleanPath(d.page), cleanTok(d.lang, 10), country(req), vis).first();
  if (env.RESEND_API_KEY && env.NOTIFY_TO) ctx.waitUntil(notify(env, r.id, kind, firm, email, fields).catch((e) => console.error("notify failed", e)));
  return json({ ok: true, id: r.id }, 200, h);
}

async function notify(env, id, kind, firm, email, fields) {
  const lines = [kind + " #" + id + (firm ? " - " + firm : ""), email ? "From: " + email : "", "", ...Object.entries(fields).map(([k, v]) => k + ": " + v), "", "Inbox: https://go.propanalyse.com/admin#inbox"];
  const res = await fetch("https://api.resend.com/emails", {
    method: "POST", headers: { Authorization: "Bearer " + env.RESEND_API_KEY, "Content-Type": "application/json" },
    body: JSON.stringify({ from: env.NOTIFY_FROM || "PropAnalyse <forms@propanalyse.com>", to: env.NOTIFY_TO.split(","), reply_to: email || undefined, subject: "[PropAnalyse] New " + kind + (firm ? ": " + firm : ""), text: lines.join("\n") }),
  });
  if (res.ok) await env.DB.prepare("UPDATE submissions SET notified=1 WHERE id=?").bind(id).run();
}

async function purge(env) {
  const keep = parseInt(env.RETENTION_DAYS || "400", 10);
  const cut = daysAgo(keep, env);
  await env.DB.batch(["pageviews", "clicks", "events", "bot_hits"].map((t) => env.DB.prepare("DELETE FROM " + t + " WHERE day < ?").bind(cut)).concat([env.DB.prepare("DELETE FROM salts WHERE day < ?").bind(daysAgo(2, env))]));
}

export default {
  async fetch(req, env, ctx) {
    const url = new URL(req.url);
    const p = url.pathname;
    try {
      if (p === "/e") return req.method === "OPTIONS" ? new Response(null, { status: 204, headers: cors(req, env) }) : req.method === "POST" ? await beacon(req, env) : new Response("POST only", { status: 405 });
      if (p === "/f") return req.method === "OPTIONS" ? new Response(null, { status: 204, headers: cors(req, env) }) : req.method === "POST" ? await form(req, env, ctx) : new Response("POST only", { status: 405 });
      if (p === "/admin" || p.startsWith("/admin/")) return await admin(req, env, url);
      if (p === "/health") return json({ ok: true, firms: Object.keys(firms(env)).length });
      if (p === "/robots.txt") return new Response("User-agent: *\nDisallow: /\n", { headers: { "Content-Type": "text/plain" } });
      if (p === "/favicon.ico") return Response.redirect(home(env) + "favicon.ico", 301);
      if (req.method !== "GET" && req.method !== "HEAD") return new Response("Method not allowed", { status: 405 });
      const seg = p.slice(1).replace(/\/+$/, "");
      if (!seg || seg.includes("/")) return redirect(home(env));
      let slug = seg; try { slug = decodeURIComponent(seg); } catch {}
      return await click(req, env, ctx, slug, url);
    } catch (e) {
      console.error(e);
      if (req.method === "GET" && !p.startsWith("/admin")) return redirect(home(env));   // never strand a visitor
      return new Response("Server error", { status: 500 });
    }
  },
  async scheduled(_ev, env, ctx) { ctx.waitUntil(purge(env)); },
};
