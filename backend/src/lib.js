// Shared helpers: bot filter, device class, privacy-preserving visitor hash, sanitisers.

export const BOT_RE = /bot\b|bot\/|crawl|spider|slurp|scrape|curl|wget|python|httpx|aiohttp|go-http|java\/|okhttp|axios|node-fetch|undici|libwww|headless|phantom|puppeteer|playwright|selenium|lighthouse|pagespeed|gtmetrix|pingdom|uptime|monitor|preview|facebookexternalhit|meta-externalagent|whatsapp|telegram|discord|slack|skype|linkedinbot|embedly|pinterest|vkshare|validator|bingpreview|yandex|baiduspider|semrush|ahrefs|mj12|dotbot|petalbot|bytespider|gptbot|chatgpt|oai-searchbot|claude|anthropic|perplexity|ccbot|google-extended|googleother|feedfetcher|rss|okhttp|postman|insomnia/i;

/** Reason string if the request looks automated, else null. */
export function botReason(req, kind = "click") {
  const ua = req.headers.get("user-agent") || "";
  if (kind === "click" && req.method === "HEAD") return "head";
  if (ua.length < 20) return "noua";
  if (BOT_RE.test(ua)) return "ua";
  const al = (req.headers.get("accept-language") || "").trim();
  if (!al || al === "*") return "nolang";                            // every real browser sends a real one (undici/scripts send "*")
  const purpose = (req.headers.get("sec-purpose") || req.headers.get("purpose") || "").toLowerCase();
  if (purpose.includes("prefetch") || purpose.includes("prerender")) return "prefetch";
  return null;
}

export function deviceClass(ua = "") {
  if (/ipad|tablet|playbook|silk|kindle|(android(?!.*mobile))/i.test(ua)) return "tablet";
  if (/mobi|iphone|ipod|android|phone|blackberry|opera mini/i.test(ua)) return "mobile";
  return "desktop";
}

export const optedOut = (req) => req.headers.get("dnt") === "1" || req.headers.get("sec-gpc") === "1";

export function country(req) {
  const c = (req.cf && req.cf.country) || req.headers.get("cf-ipcountry") || "";
  return /^[A-Z0-9]{2}$/.test(c) ? c : "";
}

export function dayOf(ts, env) {
  const off = parseInt(env.TZ_OFFSET_MIN || "0", 10) || 0;
  return new Date(ts + off * 60000).toISOString().slice(0, 10);
}
export const daysAgo = (n, env, now = Date.now()) => dayOf(now - n * 86400000, env);

export function refHost(v) {
  if (!v) return "";
  try { return new URL(v).hostname.toLowerCase().replace(/^www\./, "").slice(0, 100); } catch { return ""; }
}
export const cleanHost = (s) => (typeof s === "string" ? s.toLowerCase().replace(/^www\./, "").replace(/[^a-z0-9.\-]/g, "").slice(0, 100) : "");
export const cleanPath = (s) => (typeof s === "string" && s.startsWith("/") ? s.split(/[?#]/)[0].replace(/[^\w\-./~%@]/g, "").slice(0, 200) : "");
export const cleanSlug = (s) => (typeof s === "string" && /^[a-z0-9][a-z0-9-]{0,63}$/.test(s) ? s : "");
export const cleanTok = (s, n = 60) => (typeof s === "string" ? s.replace(/[^\w\-.+ ]/g, "").trim().slice(0, n) : "");
export const cleanText = (s, n = 4000) => (typeof s === "string" || typeof s === "number" ? String(s).replace(/[\u0000-\u0008\u000b\u000c\u000e-\u001f]/g, "").trim().slice(0, n) : "");

export function httpUrl(u) {
  if (!u || typeof u !== "string" || u === "#") return null;
  try { const x = new URL(u); return x.protocol === "https:" || x.protocol === "http:" ? x.toString() : null; } catch { return null; }
}

const hex = (buf) => [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
const saltCache = new Map();

/** Daily random salt, kept in D1 for ~48h then deleted (cron + opportunistic). */
export async function dailySalt(env, day) {
  if (saltCache.has(day)) return saltCache.get(day);
  let row = await env.DB.prepare("SELECT salt FROM salts WHERE day=?").bind(day).first();
  if (!row) {
    const s = hex(crypto.getRandomValues(new Uint8Array(16)));
    await env.DB.prepare("INSERT OR IGNORE INTO salts(day, salt) VALUES(?, ?)").bind(day, s).run();
    row = await env.DB.prepare("SELECT salt FROM salts WHERE day=?").bind(day).first();
    await env.DB.prepare("DELETE FROM salts WHERE day < ?").bind(daysAgo(2, env)).run();
  }
  if (saltCache.size > 4) saltCache.clear();
  saltCache.set(day, row.salt);
  return row.salt;
}

/** 16-hex visitor id for one day; null if the browser opted out (DNT / GPC). Raw IP never stored. */
export async function visitorId(req, env, day) {
  if (optedOut(req)) return null;
  const ip = req.headers.get("cf-connecting-ip") || req.headers.get("x-real-ip") || "";
  const ua = req.headers.get("user-agent") || "";
  const salt = await dailySalt(env, day);
  const d = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(salt + "|" + ip + "|" + ua));
  return hex(d).slice(0, 16);
}

export async function bumpBot(env, day, kind, reason) {
  await env.DB.prepare("INSERT INTO bot_hits(day, kind, reason, n) VALUES(?, ?, ?, 1) ON CONFLICT(day, kind, reason) DO UPDATE SET n = n + 1")
    .bind(day, kind, reason).run();
}

export function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

export async function safeEqual(a, b) {
  const enc = new TextEncoder();
  const [x, y] = await Promise.all([crypto.subtle.digest("SHA-256", enc.encode(a)), crypto.subtle.digest("SHA-256", enc.encode(b))]);
  const u = new Uint8Array(x), v = new Uint8Array(y);
  let diff = 0;
  for (let i = 0; i < u.length; i++) diff |= u[i] ^ v[i];
  return diff === 0;
}
