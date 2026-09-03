# Notion build recipe

Follow in order. Uses the Notion connector tools: create-pages, create-database, create-view, update-view, update-page, fetch. Schemas intentionally match the Lifecycle Leaders lifecycle-calendar skill so calendars from either skill stay compatible.

## 0. Connector gotchas (read first)

- The connector cannot delete a view, set a page to full width, or turn on wrap text. Do not pretend it can; tell the user the one-click steps at hand-off.
- Every view ships unsorted, including the auto-created Default view. Apply `SORT BY "Date" ASC` to the Default view of both databases and to any view you create.
- Blank Date confidence means exact. Only tag Approximate on genuinely unsettled dates so the orange flags stand out.
- The two-way relation is created from the Campaigns side: `RELATION('<moments_data_source_id>', DUAL 'Campaigns')`. This auto-creates the Campaigns column on the moments side.
- Page icons: common single emojis only. Composite sequences and some flags fail the whole batch with an invalid icon error. If a batch fails, swap the icon and resubmit.
- Dates use the expanded properties: `date:Date:start`, `date:Date:end` (ranges only, such as Dry January or Oktoberfest), `date:Date:is_datetime: 0`.
- Keep create-pages batches to roughly 10 to 13 pages.
- When replacing the home page content, the new content must include both database tags or the connector will try to delete the databases.

## 1. Create the page

create-pages with the title "[Brand] Lifecycle Calendar" and a plain emoji icon. If the brand is fictional or a demo, say so in the page intro callout.

## 2. Create the moments database, titled "Calendar view"

```sql
CREATE TABLE (
  "Name" TITLE,
  "Date" DATE,
  "Date confidence" SELECT('Exact':gray, 'Approximate':orange),
  "Relevance" SELECT('Core':green, 'Optional':yellow, 'Stretch':gray),
  "Overview" RICH_TEXT
)
```

Capture the returned data source id and database id.

## 3. Create the campaigns database, titled "Campaign view"

```sql
CREATE TABLE (
  "Name" TITLE,
  "Date" DATE,
  "Channel" MULTI_SELECT('Email':blue, 'SMS':green, 'Push':purple, 'App':pink, 'Triggered':orange),
  "Status" SELECT('Idea':gray, 'Planned':yellow, 'Scheduled':green, 'Sent':blue),
  "Audience" RICH_TEXT,
  "Owner" RICH_TEXT,
  "Success metric" SELECT('Revenue per recipient':green, 'Conversion rate':blue, 'Reactivation rate':orange, 'Repeat purchase rate':purple, 'Retention rate':pink, 'Open / click rate':yellow, 'New signups':gray),
  "Moment" RELATION('<MOMENTS_DATA_SOURCE_ID>', DUAL 'Campaigns')
)
```

## 4. Create the moment rows

create-pages into the moments data source in batches. Each row gets its properties, a plain emoji icon, and:

- **Core moments**: the Competitive evidence section as the page body, written at creation time:

```
## Competitive evidence

**Lead time:** [earliest competitor send versus the moment date, with the example].
**Offers seen:** [range and types observed].

- [Brand]: "[subject line]" ([date], [offer]) - [emaillove.com link]
- ...
```

- **Moments with no evidence found**: an honest note instead, for example "No captured sends in the dataset name this moment. Treat it as an open lane: the moment fits the category but competitors are not visibly claiming it in email." Never invent evidence.
- **Optional and Stretch moments with a single strong example**: one evidence line is fine. Otherwise leave the body empty.

## 5. Create the Campaign template row

One pre-filled row in the campaigns database: Name "Campaign template", Audience "Who it's for", Channel Email and Push, Owner "Who owns this send", Status Idea, Success metric Conversion rate, Date blank. Body:

```
## The idea
The hook or offer, plus anything worth noting: creative direction, dependencies, who's involved.
```

Optionally add one or two example campaigns linked to Core moments, with dates and offers taken from the evidence (for example, early access opening on the date a competitor opened it last year).

## 6. Views and sorting

- Moments database: create a calendar view, `CALENDAR BY "Date"`, showing Name and Relevance.
- Campaigns database: create a calendar view, `CALENDAR BY "Date"`, showing Name, Moment, and Status.
- Fetch each database to get its Default view id, then update-view each: moments Default sorted by Date ascending showing Name, Date, Date confidence, Relevance, Overview; campaigns Default sorted by Date ascending.

## 7. Home page layout

update-page with replace_content. Structure: an intro callout (what this calendar is, and the fictional-brand note if it applies), then a two-column layout, then the evidence callout.

```
<columns>
	<column ratio="50">
		<callout icon="🗓️" color="blue_bg">
			**Calendar**
			Every moment in the year that matters for this brand, stack ranked by relevance.
			<empty-block/>
			<span color="green">**Green**</span> is Core, build around it. <span color="gray">**Gray**</span> is a stretch. <span color="orange">**Orange**</span> dates can still move.
		</callout>
		<database url="<MOMENTS_DB_URL>" inline="false" color="blue_bg" data-source-url="<MOMENTS_DATA_SOURCE_URL>">Calendar view</database>
	</column>
	<column ratio="50">
		<callout icon="✏️" color="purple_bg">
			**Campaigns**
			Plan every send here, each one mapped to its moment.
			<empty-block/>
			Duplicate the template row, then fill in the <span color="blue">**audience**</span>, <span color="pink">**channel**</span>, <span color="orange">**date**</span>, and <span color="green">**idea**</span>.
		</callout>
		<database url="<CAMPAIGNS_DB_URL>" inline="false" color="purple_bg" data-source-url="<CAMPAIGNS_DATA_SOURCE_URL>">Campaign view</database>
	</column>
</columns>

<callout icon="🔍" color="green_bg">
	**Competitive evidence**
	Every Core moment carries a Competitive evidence section in its page body: what competitor brands actually sent, when they started, and what they offered, pulled from the Email Love library via the Email Love MCP.
</callout>

<callout icon="⚖️" color="yellow_bg">
	**Offer guardrails, from the evidence**
	[Synthesize across the whole competitive set: the deepest discount observed and at which moment, the standard promo range, any brand-specific posture worth naming, and which occasions carry no discount at all in the dataset.]
</callout>
```

The guardrails callout is required, not optional. It is the single most quotable output of the build: it tells the brand how deep the market goes, when, and where discounting is simply not done.

## 8. Hand-off checklist

- The one-click UI steps: toggle full width from the page menu, turn on wrap text for the Overview column if it clips, delete any stray view tab.
- Which dates are Approximate.
- Which competitors had thin or missing coverage, and which dates are capture dates rather than send dates.
- That evidence shows what competitors did, not what performed.
- The scoped campaign idea offer.
