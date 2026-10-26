# PropAnalyse design audit (2026-10-26)

## Honest critique of the current build (mobile screenshot, 390px)

1. It looks like every AI-built "dark dashboard": navy `#0b1426` + amber `#f5a623`, system/Inter type, a glow gradient behind the hero. Nothing says *this* product.
2. The logo is a gradient "PF/A" badge that wraps onto two lines; it reads as a placeholder, not a mark.
3. The hero explains ("Compare prop firms on the numbers that matter") instead of asserting a point of view, and the sub-line repeats it.
4. Four identical bordered stat boxes (19 / 56 / 11 / date) are the hero-metric template. They push the actual product, the table, below the fold on every device.
5. Ten "Best for" pills are a wall of equal-weight chips with no hierarchy and no counts; the eye has nowhere to land.
6. Typography has no scale: H1, card titles, labels and values sit within a few px of each other. Numbers are proportional, so columns never align.
7. On mobile the table collapses into a label/value card grid: 12 uppercase micro-labels per firm, so 19 firms become a ten-screen scroll of form fields.
8. Everything is a rounded bordered box (filters, stats, cards, kv grids, aside, FAQ): boxes inside boxes, no rules, no whitespace doing the grouping.
9. The PFA score is a coloured pill (green/amber/red) you have to read; it is not scannable as a quantity, and colour is the only cue.
10. Missing data is rendered three ways ("—", "n/a", "Not published"), and the em-dash doubles as both "unknown" and punctuation.

## Design read

Reading this as: a data/reference product (Impeccable "Operate" mode) for prop traders comparing rule sets, with an editorial-terminal language (a printed spec sheet that behaves like a terminal), leaning toward native CSS + self-hosted type + restrained CSS motion.

design-taste scopes out data tables and dashboards. Its anti-slop rules (palette, type, em-dash, eyebrows, cards, CTAs, copy) are applied to every surface; its landing-page rules (hero imagery, bento, marquees) are deliberately not, because the table *is* the product.

Mode: redesign, overhaul. Visuals treated as greenfield; routes, data, JSON-LD, i18n keys, filter IDs / URL params and the build pipeline preserved.

Dials: DESIGN_VARIANCE 4 (data needs alignment; asymmetry only in page furniture), MOTION_INTENSITY 3 (feedback + one load moment), VISUAL_DENSITY 8 (cockpit: 1px rules, no card boxes, tabular numerals everywhere).

## Direction

- **Paper and ink, one marker.** Cool off-white paper / ink; dark mode is near-black / bone, following `prefers-color-scheme`. The single accent is a highlighter lime used only as *marking*: the logomark, the active filter, the stronger value on compare pages, the top score. Never as text on paper (it would fail contrast), so links are ink with an offset underline.
- **Type:** Bricolage Grotesque (display, narrowed width axis) for headings and firm names; Geist for UI/body; Geist Mono with tabular figures for every number. Self-hosted woff2, `font-display: swap`, latin subset.
- **Structure:** 1px rules instead of boxes, square corners everywhere (shape lock). The table is the hero on desktop. Profile = spec sheet in grouped sections with a sticky score column. Compare = two columns, the stronger figure marked per row, plus a tally.
- **Score:** number + a trackless 10-tick bar (ticks filled to the score, fractional last tick). Scannable as length, readable as a number, no traffic-light colour.
- **Missing data:** one treatment everywhere: a short CSS hairline with visually hidden "Not published" text, and a legend under each table.
- **Motion (Emil):** row hover tint (120ms ease, hover-capable pointers only), press scale 0.97 on chips/buttons (160ms ease-out), score ticks fill once on load (30ms stagger, 420ms cubic-bezier(0.23,1,0.32,1)). Movement removed under `prefers-reduced-motion`.

## Pre-flight results (live, 2026-10-26)

| Check | Result |
|---|---|
| No default blue/purple gradients, no glows | Pass: zero gradients except the CSS tick pattern; one accent (lime) used only as marking |
| No 3-column feature cards / card grids | Pass: compare pairs, shortlists, discounts are ruled lists; no card boxes anywhere |
| No emoji / unicode-as-icon | Pass: Phosphor icons inlined (menu, close, search, sliders, copy, external, arrow, star); "☰" removed |
| Em/en dashes visible | Pass: 0 across all 52 generated pages (source-note dashes normalised at render) |
| Eyebrows | Pass: none above headings (table column labels and footer group labels only) |
| 4/8px rhythm | Pass: spacing tokens 4/8/12/16/20/24/32/40/48/64/96 (12/20 = 4px steps) |
| Contrast AA | Pass: body 16.4:1, secondary 9.5:1, muted 5.75:1 (5.2:1 on hover tint), ink on lime 13.8:1, input borders 3.6:1; dark mode muted 6.7:1 |
| Focus states | Pass: 2px ink (light) / lime (dark) focus ring on every control, chips show ring on the visual span |
| Layout shift | Pass: Lighthouse CLS 0 on home, /firms/, profile, compare |
| Tabular numbers | Pass: tabular-nums on body; Geist Mono for stacked figures (fees, sizes, ranks, scores, ratings, codes, ladders) |
| One accent | Pass: lime only (logomark top bar, active nav/filter, copied state, stronger compare value, selection) |
| Shape lock | Pass: radius 0 everywhere |
| prefers-reduced-motion | Pass: tick fill animation removed, press scales disabled |
| Hover gated to fine pointers | Pass: `@media (hover:hover)` on all hover effects |
| Mobile 390px | Pass: no horizontal overflow on any page; table collapses to a ranked list |
| Dark mode | Pass: full token swap via prefers-color-scheme, checked on home, profile, compare |

Lighthouse mobile (local Lighthouse 12 against the live Pages URL; PageSpeed API daily quota was exhausted):
home 98 / 100 / 100 / 100, /firms/ 100 / 100 / 100 / 100, /firms/ftmo/ 100 / 100 / 100 / 100, compare 100 / 100 / 100 / 100 (perf / a11y / best practices / SEO). LCP 1.4 to 1.8 s, TBT 0 ms.
