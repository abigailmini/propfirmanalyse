// Builds the static site twice into temp dirs (TRACK off / TRACK=1) and checks the link switch.
import { test } from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { mkdtempSync, readFileSync, readdirSync, statSync, rmSync, existsSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const walk = (d) => readdirSync(d).flatMap((f) => { const p = join(d, f); return statSync(p).isDirectory() ? walk(p) : p.endsWith(".html") ? [p] : []; });
function build(env) {
  const out = mkdtempSync(join(tmpdir(), "pa-site-"));
  execFileSync("python3", ["scripts/build.py"], { cwd: ROOT, env: { ...process.env, ...env, OUT_DIR: out }, stdio: "pipe" });
  return out;
}

test("default build: no tracking, links untouched, privacy page present", () => {
  const out = build({ TRACK: "" });
  try {
    const files = walk(out);
    assert.ok(files.length > 300);
    assert.ok(!files.some((f) => /(href|src|data-api)="https:\/\/go\.propanalyse\.com/.test(readFileSync(f, "utf8"))), "go links leaked into default build");
    assert.ok(!existsSync(join(out, "assets/a.js")));
    assert.match(readFileSync(join(out, "privacy/index.html"), "utf8"), /not switched on yet/);
  } finally { rmSync(out, { recursive: true, force: true }); }
});

test("TRACK=1 build: every firm button tracked, beacon everywhere, forms wired", () => {
  const out = build({ TRACK: "1", GO_URL: "https://go.propanalyse.com" });
  try {
    const js = readFileSync(join(out, "assets/a.js"), "utf8");
    assert.ok(Buffer.byteLength(js) < 1500, "beacon " + Buffer.byteLength(js) + " bytes");
    assert.ok(js.includes("https://go.propanalyse.com/e") && /doNotTrack/.test(js) && /globalPrivacyControl/.test(js) && !/document\.cookie|localStorage|sessionStorage/.test(js));
    let tracked = 0, untracked = 0, slots = new Set();
    for (const f of walk(out)) {
      const t = readFileSync(f, "utf8");
      if (t.includes("</body>")) assert.ok(t.includes("/assets/a.js"), "no beacon: " + f);
      for (const a of t.match(/<a\b[^>]*data-firm="[^"]*"[^>]*>/g) || []) {
        if (/href="https:\/\/go\.propanalyse\.com\/[a-z0-9-]+\?src=\//.test(a)) { tracked++; slots.add(a.match(/pos=([a-z-]+)/)[1]); assert.match(a, /rel="(sponsored )?nofollow noopener"/); }
        else if (/href="https?:/.test(a)) untracked++;
      }
    }
    assert.equal(untracked, 0); assert.ok(tracked > 500, "tracked " + tracked);
    for (const s of ["table", "offer-card", "firm-page", "compare"]) assert.ok(slots.has(s), "slot " + s);
    const home = readFileSync(join(out, "index.html"), "utf8");
    assert.match(home, /go\.propanalyse\.com\/[a-z0-9-]+\?src=\/&amp;pos=offer-card&amp;code=/);
    const cp = readFileSync(join(out, "complaints/index.html"), "utf8");
    assert.match(cp, /id="cpform" data-api="https:\/\/go\.propanalyse\.com\/f"/); assert.match(cp, /assets\/f\.js/); assert.match(cp, /mailto:/);
    assert.ok(!/not switched on yet/.test(readFileSync(join(out, "privacy/index.html"), "utf8")));
  } finally { rmSync(out, { recursive: true, force: true }); }
});
