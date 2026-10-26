# Recon: propfirmmatch.com (2026-10-26)

Method: their site blocks plain HTTP fetches (Cloudflare 403), so pages were opened in a real browser and inspected for **structure only** (headings, table columns, filter controls, link map, JSON-LD types). No PFM prose, logos, images or CSS were copied into PropAnalyse. The raw structural dumps are in `docs/recon/*.json` for reference only and are **not** shipped with the site.

## Global layout
- Top strip: live-stream promo + giveaway banner.
- Header: logo, product switcher (Forex / Futures / Crypto / Perps — each a separate vertical home with its own table), search, language switch (EN/ES), log in / sign up.
- Secondary tab nav (same on most pages): Home · Offers · Challenges · Trading Tools · Best Sellers · Reviews · Favorite Firms · Prop Firm Rules · Spreads · Payouts.
- Hero: H1 + trust counters (firms, challenges, reviews, monthly views).
- Offer carousel above the table: per-firm card with rating, "X% OFF", one-click copy code (their codes are house-branded, e.g. MATCH, MATCH30, MATCHPERP — exclusive affiliate codes).

## Page types found
| Type | URL pattern | Notes |
|---|---|---|
| Vertical home (table) | `/`, `/futures`, `/crypto`, `/perpetuals` | Firm table + sub-tabs (Firms / Challenges / Offers / Reviews), "Popular / Favorite / New / All" toggles, "How we verify and rank" link, "Live data updated N min ago" badge |
| All firms | `/all-prop-firms?tab=all` | Same table, all ~39 forex firms (60+ total across verticals) |
| Challenge comparison | `/prop-firm-challenges` | Row = one challenge (firm × size × steps). Default filters shown as pills: Assets: FX, Size: $100K, Steps: 2 Steps + "Customize" |
| Firm profile | `/prop-firms/<slug>` | Tabs: Overview · Challenges · Reviews · Offers · Announcements · Payouts · Discussions |
| Offers / discount codes | `/exclusive-offers` (+ all offers, extra-account offers) | Card per firm: % off, code, "More N" offers |
| Rules hub | `/prop-firm-rules` | Per-firm rules summary cards with code CTA |
| Payout tracker | `/payouts`, `/payouts-leaderboard` | Columns: total payouts, # payouts, largest single, average size, median time, denials reported; 30-day/all-time toggle |
| Reviews | `/prop-firm-reviews` | Own review system (≈10k reviews). Columns: # reviews, trading conditions, customer care, user friendliness, payout process, payouts, denials, rank |
| Spreads | `/prop-firm-spreads` | Spread comparison per instrument |
| Announcements / news | `/prop-firm-announcements`, `/industry-news`, `/blog`, `/high-impact-news` | Rule-change feed + editorial |
| Best sellers / favourites | `/best-sellers`, `/favorite-firms` | Popularity-based lists (they use purchase/click data) |
| Tools | `/trading-tools`, growth calculators, Chrome extension | |
| Programs | `/loyalty-program`, `/join-affiliate-program`, bug bounty, review bounty | Loyalty points for buying via them (upload order confirmation) |
| Company | `/how-it-works`, about, transparency & methodology, careers, press, contact, help centre | |

## Firm table columns (vertical home / all firms)
Popularity/Firm · Rank/Reviews · Country/Years · Assets · Platforms · (Exchange — crypto vertical only) · Max allocation · Promo (code) · Actions (Buy / details).

## Challenge table columns
Firm/Rank · Account size · Steps · Profit target · Daily loss · Max loss · Max loss type · "ROI index" · PT:DD ratio · Profit split · Payout frequency · Loyalty points · Popularity · Price.

## Filters
Assets (FX, crypto sub-types: Altcoins, BTC/ETH, DeFi, Majors, Meme), account size, steps (instant/1/2/3), platform, plus a "Customize" panel. Search box in header. Favourite toggle (needs login).

## Firm profile sections
Header (logo, name, CEO, country, Trustpilot score, date founded, years in operation, own review score + distribution, "no payout delays" style badge, current offer, Buy). Content blocks: Firm overview (broker/LP, platforms, payment methods), Instruments & assets, Leverage, Commissions, Consistency rules, Firm rules, Challenges (matrix: Instant / 1-step / 2-step / 3-step), Payout policy, Restricted countries, auto-generated "AI summary". JSON-LD: BreadcrumbList + Product.

## Monetisation / CTA pattern
- Every row and card has an exclusive affiliate code + "Buy" button that routes via their tracked link.
- Loyalty points for purchases made through them; giveaways ($200K account).
- Business portal for firms (paid placement/analytics), "Popularity" ranking driven by their own traffic.

## Trust display
Trustpilot score + their own verified-review score and count, years in operation, payout-tracker stats, "denials reported", live-data timestamp.

## SEO
Homepage FAQPage JSON-LD ("best prop firm / best futures / best crypto / instant funding / legal in India" questions), firm pages Product + Breadcrumb, multilingual (/es).

## Footer
Large mega-footer link groups: Find & Compare · Reviews & Rankings · Payouts · Offers · News & Insights · Tools & Resources · Programs & Rewards · About. Newsletter subscribe, cookie preferences.

## What PropAnalyse does differently (deliberate)
- Navy/amber palette, our own logo/monogram avatars (no firm logos yet), filters as a sticky top bar (not side panel), table-first home.
- Transparent, published scoring formula (PA Score) instead of opaque popularity rank; data-completeness % per firm; source URLs on every profile.
- Crypto-first ordering of the dataset; compare pages generated for crypto pairs first.
- Ownership disclosure (FundedXYZ) on About, Methodology and any compare page involving FundedXYZ.
- Codes shown are only those publicly published on each firm's own site (until David's own affiliate codes exist).

## Not built yet (PFM features worth considering later)
User reviews, payout tracker (needs data source), spreads table, loyalty points, rule-change feed (stub at /updates/), challenge-level table (one row per firm×size), ES/CN language versions (CN strings stub exists).
