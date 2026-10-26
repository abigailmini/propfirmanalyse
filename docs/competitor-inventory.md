# Competitor inventory: propfirmmatch.com (2026-10-26)

Method: their sitemap and pages are behind Cloudflare, so curl gets blocked. We used headless Chrome (`--dump-dom`) to pull the sitemap (18,928 URLs) plus 15 sample pages, one per page type. URLs were grouped by path pattern. This file records **structure, counts and slugs only**. None of their prose was copied.

## Totals
- **18,928 URLs**: 11,361 English, 7,567 Spanish (`/es/` mirror). No other languages, so **no Chinese and no Malay** (our lane).
- Four verticals with their own trees: forex/CFD (root), `/futures/`, `/crypto/`, `/perpetuals/`.
- About 75% of URLs are programmatic list pages (country × city × payout method).

## Page types (English)

| Page type | URL pattern | Count | Key sections (structure) | PropAnalyse equivalent |
|---|---|---|---|---|
| Firm hub (forex) | `/prop-firms/<firm>` | 39 | header stats, rating, rules summary, tabs | `/firms/<slug>/` (20) |
| Firm sub-tabs | `/prop-firms/<firm>/{challenges,reviews,offers,announcements,payouts,discussions}` | 234 (39 × 6) | challenge table per size, user reviews, codes, firm news, payout proofs, forum | review page sections; `/news/` per firm |
| Futures firm hub + tabs | `/futures/prop-firms/<firm>[/tab]` | 27 hubs | same as forex | futures firms in `/firms/` |
| Crypto firm hub + tabs | `/crypto/prop-firms/<firm>[/tab]` | 8 hubs, 48 tabs | same | `/crypto/<slug>/` (deeper) |
| Unlisted firms | `/unlisted-prop-firms/<firm>` | 358 | thin stub for firms with no partnership (HyroTrader is here) | n/a (every firm listed on merit) |
| Challenge pages | `/prop-firm-challenges/<firm-program-size>` | 1,114 (+368 futures, +188 crypto, +111 perps) | one program/size: price, target, DD, split, days | fee matrix on each review (size pages later) |
| Compare pairs | `/compare-firms/a-vs-b` | 741 (+351 futures, +52 crypto) | side-by-side table | `/compare/a-vs-b/` |
| Offers / codes | `/offers/<code>`, `/offers`, `/exclusive-offers` | 97 (+48 futures, +19 crypto) | code, % off, "match" exclusive codes | `/offers/` |
| Lists by country | `/prop-firm-lists/countries/<c>[/challenges,/payouts]` | 32 + 96 | firms allowed per country | planned |
| Lists by city | `.../countries/<c>/cities/<city>` | 2,439 (+1,555 futures, +1,472 crypto) | near-duplicate thin pages | skip (thin) |
| Restricted countries | `/prop-firm-lists/restricted-countries/<c>` | 237 | firms banning a country | planned |
| Payment / payout method lists | `/prop-firm-lists/{payment-methods,payout-methods}/<m>` | 80 + 35 | firms per method | crypto payout list in `/crypto/`; more planned |
| Broker / platform lists | `/prop-firm-lists/{brokers,platforms}/<x>` | 34 + 15 (+17 perps) | firms per broker/platform | `/best/mt5/` |
| Challenge-type / feature lists | `/prop-firm-lists/{challenge-types,challenges,assets,account-size}/<x>` | 33 + 11 + 8 + 28 | instant, 2-step, scaling, news, crypto, 100K | `/best/<x>/` |
| Rule changes | `/prop-firm-rule-changes` (+crypto) | 2 | editorial feed, **no dated field-level diffs** | `/news/` dated diffs + RSS |
| Firm announcements | `/prop-firm-announcements` | 2 | firm-posted notices | `/news/` |
| Industry news | `/industry-news/<slug>` | 72 | hand-written launch / retirement / wind-down posts | `/news/` (data-derived) |
| Blog | `/blog/<slug>` | 115 | guides, reviews, expo promos | `/guides/` |
| Payout proofs | `/payouts/<firm>`, `/payouts-leaderboard` | 34 + 1 | payout totals per firm | gap (needs data source) |
| Tools | `/trading-tools`, `/high-impact-news`, `/prop-firm-spreads`, `/challenge-finder`, `/ai` | 5 | news calendar, spreads, challenge filter, AI chat | `/tools/` calculators + `/quiz/` |
| Rules explainer | `/prop-firm-rules` (+crypto) | 2 | rules reference | `/glossary/` |
| Demo / EA-copy lists | `/prop-firm-demo-accounts`, `/prop-firm-ea-copy-trading-platforms` | 3 | lists | bots/copy fields in reviews |
| Trust / company | `/about-us`, `/transparency`, `/how-it-works`, `/press`, `/careers`, `/awards-2025` | 6 | company, review policy | `/about/`, `/methodology/` |
| Monetisation | loyalty, referral, affiliate, extra-account promo, review bounty, giveaways | about 8 | cashback points, promos | RebateYou later |
| FAQ / glossary | none standalone | 0 | | `/faq/`, `/glossary/` |

Schema seen on samples: Organization, BreadcrumbList, FAQPage on some lists, Review/AggregateRating on firm hubs.

## Blog topics by intent (top 30, our /guides keyword targets)
- **Best-of (money):** best-crypto-prop-firms, best-crypto-funded-accounts, best-futures-funded-accounts, best-futures-prop-firms-to-compare, best-forex-funded-trading-accounts, best-funded-stock-trading-accounts, best-instant-funding-prop-firms, best-funded-programs-for-small-budgets, best-funded-trading-firms-in-the-usa, best-funded-trading-accounts-top-10-list, top-funded-accounts-for-beginners, the-5-best-futures-prop-trading-firms-for-100k-accounts-based-on-affordability.
- **How it works:** how-much-do-funded-trading-programs-cost, how-do-funded-trader-accounts-work, what-is-a-prop-firm-basics-explained, understanding-the-prop-trading-evaluation-process, understanding-profit-splits-in-prop-trading, understanding-drawdown-limitations-in-prop-trading, how-to-pass-prop-firm-challenge-ultimate-guide.
- **Model comparisons:** instant-funding-programs-vs-evaluation-programs, instant vs 1-step vs 2-step, mt4-vs-mt5-for-funded-trading, funded-trading-vs-trading-your-own-money.
- **Style:** funded-accounts-for-day-trading, funded-accounts-for-swing-trading, understanding-ea-expert-advisors, trade-copiers-explained.
- **Crypto:** what-are-perpetual-futures, the-5-best-crypto-prop-trading-firms-based-on-trustpilot-ratings.
- **Firm reviews:** FTMO, The5ers, FundedNext, FundingPips, Blue Guardian, Crypto Fund Trader, Lark Funding.

About 25 of their 115 posts are expo promos or thin 2023–24 listicles. Their 72 news posts are hand-written; none of them is a machine diff of rule fields with dates.

## What they lack (our openings)
1. **No dated field-level rule history.** Ours is generated from data diffs: old → new value, date, source, plus RSS and JSON feeds.
2. **Crypto is shallow:** 8 crypto firm hubs, and HyroTrader is only an "unlisted" stub. They have no per-firm crypto rule sheet (venue, perps vs CFD, leverage, weekend, bots, USDT payout).
3. **No true-cost maths** (fee + resets + activation − refund → cost to first payout).
4. **Ranking is tied to partnerships:** firms without a deal sit in "unlisted". We publish our scoring and don't take payment for rank.
5. **No zh or ms**, and no standalone glossary or FAQ.

## Where we still trail them (to schedule)
- Firm count: 20 vs about 74 listed (+358 unlisted stubs).
- Programmatic challenge pages (1,700+) and country/payment lists (about 500 excluding city pages).
- Payout proofs / leaderboard (needs our own data source).
- User reviews / discussions (needs accounts and moderation).
- Spanish mirror.
