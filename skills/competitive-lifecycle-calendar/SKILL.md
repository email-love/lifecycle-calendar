---
name: competitive-lifecycle-calendar
description: Build a ranked year-of-moments lifecycle calendar in Notion with competitive evidence pulled from the Email Love MCP. Every cultural moment and commerce peak that matters for a brand, stack ranked Core / Optional / Stretch, and every Core moment backed by what competitor brands actually sent last year, including dates, offers, discount depths, and linked real emails. Use whenever someone asks to build a campaign calendar, marketing calendar, moments calendar, or lifecycle planning calendar backed by competitor data, or says things like "build me a calendar for [brand] with competitive evidence" or "what should [brand] plan around, and what do competitors do". Requires the Notion connector and the Email Love Inspiration MCP.
---

# Competitive Lifecycle Calendar

_By Email Love (emaillove.com). The calendar structure is adapted, with credit and thanks, from Luke Kline's lifecycle-calendar skill, built for the Lifecycle Leaders community. This version adds a competitive evidence layer from the Email Love library: nearly 500,000 real marketing emails, with 1,000 more captured daily._

A moments calendar answers which moments matter for a brand. The evidence layer answers what the market actually did at each one: when competitors started sending, what they offered, and how deep they discounted. The result is a plan built on receipts instead of guesses.

## Requirements

Both must be connected before building anything. If either is missing, stop and tell the user which one.

- The Notion connector.
- The Email Love Inspiration MCP: chat.emaillove.com/mcp.

## What you're building

One Notion page holding:

1. **Calendar view** (the moments database). One row per moment: Name, Date, Date confidence (Exact or Approximate), Relevance (Core, Optional, Stretch), Overview, plus a two-way relation to Campaigns.
2. **Campaign view** (the campaigns database). Where the user plans sends, each linked to a moment. Ships with one pre-filled Campaign template row and, when useful, one or two example campaigns grounded in the evidence.
3. A two-column colored home page that explains both databases at a glance, plus an evidence callout and an offer guardrails callout that synthesizes discount depth across the whole competitive set (the deepest discount observed and where, the standard promo range, and which occasions carry no discount at all).
4. **Competitive evidence sections** written into every Core moment's page body.

Exact schemas, build order, and connector gotchas are in `references/notion-build.md`. Read that file before touching Notion.

## Workflow

### 1. Gather inputs (one short round, only what is missing)

Read the user's opening message first and extract anything already given. Never re-ask something they already said.

- **Brand** is required and can never be assumed. If it is missing, ask before doing anything else.
- **Industry**: ask if not obvious from the brand. It drives the moment set, the ranking, and the competitor discovery.
- **Region**: default to US, confirm in the same round if asking anything else.
- **Year**: default to the current calendar year. If it is late in the year, confirm whether they want what is left of it or the coming twelve months.
- **Competitor set**: 3 to 6 brands. If the user does not name them, offer to find candidates with search_brands and confirm the list before pulling.

### 2. Check coverage before promising anything

For each competitor, call search_brands and read the email count. Under about 15 emails means thin history; say so and suggest a swap. Coverage windows vary too: a brand can have deep history that stops before the season you need. Never present thin coverage as a full picture, and tell the user which competitors have usable history in one line.

### 3. Build and date the moment set

Lay down the baseline cultural and commerce moments for the region (the major holidays, BFCM and Cyber Week, the seasonal transitions, the big shared occasions), then adapt for the industry: drop moments with no plausible angle, add category-specific ones (Dry January and Sober October for NA beverage, the tax cycle for fintech, back to school for the relevant verticals, competitor tentpoles like Prime Day). Keep distinct dated moments as separate rows.

Compute dates for the target year: fixed dates stay put, rule-based floating dates compute by rule (Thanksgiving is the fourth Thursday of November, Memorial Day the last Monday of May, Mothers Day the second Sunday of May), and announced or lunar dates get verified with web search or flagged Date confidence = Approximate. Blank confidence means exact, so only the orange flags stand out.

### 4. Pull the evidence (Core moments first)

For each Core-candidate moment, find competitor sends near that moment last year:

- search_emails with the brand filter plus a query for the moment name and natural variants.
- Also pull each brand's general list (search_emails with the brand filter, limit 25) and scan sent or captured dates for the 4 to 6 weeks before the moment. Many seasonal sends never name the holiday in the subject line.
- Record for each send: date, subject line, offer type and depth, the emaillove.com URL.
- Prefer sent_date; fall back to captured_date, which is usually within a day or two of send.

Derive per moment: lead time (earliest competitor send versus the moment date) and the offer range seen.

### 5. Rank with the evidence

Assign Core, Optional, or Stretch for this specific brand, and keep Core scarce: 8 to 12 across the year. Let the evidence inform the call. A moment most competitors visibly send for is Core-grade. A moment no competitor claims gets an honest open-lane note, never invented evidence; an unclaimed moment that fits the brand can still be Core, and the note is the reason why it is interesting.

### 6. Build it in Notion

Follow `references/notion-build.md` exactly: page, both databases with the two-way relation, moment rows (evidence written into Core moment bodies at creation time), the Campaign template row, calendar views, sorted default views, and the colored home page with the evidence callout.

### 7. Offer the benchmarks layer (optional, once per calendar)

Ask if the user wants send-timing and subject line benchmarks. If yes, call get_brand_insights for each competitor and summarize on a child page: sends per week, busiest days, peak send windows (as relative patterns, recorded hours are not local-time exact), subject line length and emoji rate, and anything striking such as ESP mix or dark mode optimization.

### 8. Hand off

Keep the summary to about five lines: done plus the link; the one or two standout evidence findings (an open lane, a surprising lead time); caveats (which dates are Approximate, which competitors had thin coverage, capture dates versus send dates, and that evidence shows what competitors did, not what worked); the one-click UI steps the connector cannot do (full width, wrap text, deleting stray view tabs); and the scoped idea offer.

The idea offer is one question: "Want campaign ideas written in? I'd start with your Core moments, or name specific ones." Generate per `references/idea-prompt.md`, grounded in each moment's evidence block. Only chosen moments get ideas.

## Voice

Plain, matter-of-fact English. No em dashes. Overviews are factual one-liners about the customer occasion, never tactics. Evidence is quoted from the library, never invented, and gaps are stated honestly.
