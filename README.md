# PropAnalyse

Static, data-first prop firm comparison site. Every page is generated from `data/firms.json`.

## Build
```
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
PA Score (0–10) = Trust 30% + Cost 20% + Rules 20% + Payout 20% + Track record 10%. Missing inputs score 4/10. Formula in `scripts/build.py` → `score()`. FundedXYZ (same operator) is scored identically.

## i18n
`i18n/en.json` is live; `i18n/zh.json` is a key-mirrored stub for a future /zh/ build.
