# PropAnalyse

Static, data-first prop firm comparison site. Every page is generated from `data/firms.json`.

## Build
```
python3 scripts/add_firms.py <slug>...   # (new firms) staged research in ../tmp/expand -> data/raw, extra, crypto, payout_claims
python3 scripts/merge.py      # data/raw/<slug>.json -> data/firms.json (canonical crypto-first order)
python3 scripts/build.py      # data/firms.json -> site/
```
Page modules: `scripts/more_core.py` (overlays, changelog, reviews), `more_pages_a.py` (offers, crypto, news), `more_pages_b.py` (tools, quiz, glossary, FAQ, methodology, SEO), `more_guides.py`. Overlays: `data/extra/<slug>.json` (resets, refunds, time limits) and `data/crypto/<slug>.json` (crypto rules).
Rule-change log: every local build diffs firms vs `data/snapshot.json` and appends to `data/changelog.json`. **Always build locally after a data change and commit both files**; CI only renders them.

Env: `BASE_PATH` (default empty; site is served from the domain root) and `SITE_URL` (default `https://propanalyse.com`).
Pushing to `main` runs `.github/workflows/pages.yml`, which builds and deploys to GitHub Pages at https://propanalyse.com (custom domain set in Pages settings; build also writes `site/CNAME`).

## Data rules
- Facts only, collected from each firm's own website (+ Trustpilot for ratings). Unknown = `null`, never estimated.
- `source_urls` + `last_verified` per firm. `affiliate_url` is `#` until real links exist.
- No third-party (e.g. PropFirmMatch) prose, logos, images or CSS. See `docs/recon.md` for the structural recon.

## Scoring
PA Score (0–10) = Trust 30% + Cost 20% + Rules 20% + Payout 20% + Track record 10%. Missing inputs score 4/10. Formula in `scripts/build.py` → `score()`. FundedXyz (same operator) is scored identically.

## i18n
`i18n/en.json` is live; `i18n/zh.json` is a key-mirrored stub for a future /zh/ build.

## Account types (2026-10-31)
Primary taxonomy is the account type, one per firm: `category` = `futures` | `cfd` | `crypto-exchange`, plus `also_offers`, `category_basis` and `category_source` (the firm page it was read from). Set by `scripts/categorize.py` (idempotent, patches data/raw and data/firms.json); the old asset-mix label lives on as `segment`. Hub pages /futures/, /cfd/, /crypto-exchange/ and /zh/ equivalents are built by `scripts/more_categories.py`, which also owns the ranking filter bar (account-type tabs + multi-select facets: plat, mkt, type, pay, split, pm, country; comma-separated URL params; old single-select links still resolve).

## Firm status (2026-10-31)
Every firm is `active`, `caution` or `closed`, from `data/status.json` (rule: triggers, `caution_cap` 4.0, `review_days` 30; `caution` = per-firm evidence with URLs + dates; `closed` = firms that stopped operating, with sources, regulator record and trader action). `scripts/merge.py` adds `status`/`status_since`/`status_reason`/`status_sources` to caution firms; closed firms are not merged (no rule data) and get pages from `scripts/more_status.py` (exec'd last): caution banner + score cap (formula score kept as `pa_score_formula`), no offers/codes/best-of, "Visit (caution)", caution badge, `/caution/`, `/closed-prop-firms/` + `/zh/`, `/methodology/#status`, `/for-firms/#status-review`. Language: report sources and attribute them; never "scam"/"fraud" unless a regulator or court said so.

## Analytics + click tracking (2026-10-31)
Cookieless analytics, outbound click redirects, form intake and an admin dashboard live in `backend/` (Cloudflare Worker + D1, see `backend/README.md`). Site side: `scripts/more_track.py` always writes `backend/src/firms.gen.json` and `/privacy/`; with `TRACK=1` (repo variable, flipped by `backend/scripts/go-live.sh`) it routes every firm Visit/offer link through `go.propanalyse.com/<slug>?src=&pos=&code=`, adds the 1.3 KB beacon to every page and wires the forms to the Worker (mail/GitHub fallback kept). `OUT_DIR` env builds to another folder (used by tests).


## Audit quick wins (2026-10-31)
`scripts/more_quickwins.py` (exec'd after more_status.py) holds the 2026-10-31 audit fixes: trust pages (/about/, /disclosure/, /terms/, /contact/, /corrections/), mobile table cards (`qwstack`), the /safe/ checker (+ /zh/safe/ and noindexed /safe/<slug>/ share cards), shareable calculators (`src/share.js`), thin-hub content, and post-build passes (`qw_finalize`): footer disclosure link, titles <= 60 chars (`scripts/qw_titles.py`), per-page OG images (`scripts/og_cards.py`, Pillow, fonts in `src/og-fonts/`; without Pillow the site falls back to og.png).
Promo codes: `discount_code.expires` = last valid day; `review_by` = time-limited code with no published end (hidden after that day unless re-verified); build hides both via `scripts/check_codes.py` (also a CLI: `python3 scripts/check_codes.py [--date D]`, exit 1 when anything is expired/stale/expiring). CI rebuilds daily at 00:10 UTC.

