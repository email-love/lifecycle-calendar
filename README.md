# Competitive Lifecycle Calendar

An open-source AI skill that builds a year of campaign moments in **Notion**, with
competitive evidence from real marketing emails behind every moment that matters.

Built and maintained by [Email Love](https://www.emaillove.com). Works in **Claude** and **ChatGPT**.

> **Beta.** Tested end to end in two categories (non-alcoholic beverage and prestige
> skincare). The Notion build is the part most likely to need a nudge, because the
> connector cannot do a few things the layout wants. Use it, and tell us what breaks.

## The problem it solves

Most marketing calendars are a list of holidays and a guess. Someone opens last
year's spreadsheet, moves the dates, and argues about whether the brand should do
anything for Father's Day.

The arguments are unresolvable because nobody has the receipts. When did competitors
actually start sending for Black Friday? Did any of them discount at Valentine's, or
did they all run gifting with full price held? Is there a moment the whole category
is ignoring?

This skill answers those questions from evidence: nearly 500,000 real marketing
emails in the Email Love library, with about 1,000 more captured every day.

## What you get

One Notion page holding:

1. **A moments database.** One row per moment, stack ranked Core, Optional or
   Stretch for your brand specifically, with dates computed for the target year and
   anything genuinely unsettled flagged as Approximate rather than quietly guessed.
2. **A campaigns database.** Where you plan sends, each linked back to its moment,
   with a pre-filled template row to duplicate.
3. **Competitive evidence in the body of every Core moment.** What competitor brands
   actually sent, the send date, the subject line, the offer and its depth, and a
   link to the email itself on emaillove.com.
4. **An offer guardrails summary.** Synthesized across the whole competitive set:
   the deepest discount observed and at which moment, the standard promo range, and
   which occasions carry no discount at all. This is usually the most quotable
   output of the build.

Two rules keep it honest. Evidence is quoted from the library and never invented.
A moment no competitor is claiming gets an open-lane note saying exactly that, which
is often the most interesting row on the page.

Campaign ideas are not pre-written. Ask for them per moment when you are planning
that moment, and they are generated against that moment's evidence: a send window
taken from the observed lead time, an offer guardrail taken from the observed range,
and only mechanics your brand actually has.

## Requirements

This skill is not pure knowledge. It drives two connectors, and it will stop and
tell you if either is missing:

| Requirement | What it is |
|---|---|
| **The Notion connector** | Where the calendar gets built. Share one parent page with it rather than your whole workspace. |
| **The Email Love Inspiration MCP** | Free and read-only. `https://chat.emaillove.com/mcp`. [Setup instructions](https://help.emaillove.com/plugin/ai/email-inspiration-mcp). |

Both are available in Claude and in ChatGPT, but connector support differs by plan
and by client. If your assistant cannot add custom connectors, this skill has
nothing to work with.

## Install

### Claude Code

```bash
claude plugin marketplace add email-love/lifecycle-calendar
claude plugin install competitive-lifecycle-calendar@email-love-lifecycle-calendar
```

Update with `claude plugin marketplace update email-love-lifecycle-calendar`, then
reinstall. Remove with `claude plugin uninstall competitive-lifecycle-calendar@email-love-lifecycle-calendar`.

### Claude apps (web, desktop, Cowork)

Add this repository as a marketplace: **Customize → Plugins → Add → Add
marketplace**, enter `email-love/lifecycle-calendar`, then install **Competitive
Lifecycle Calendar** from it. **Check for updates** on the marketplace pulls new
versions, or turn on **Sync automatically**.

To install without a marketplace, upload the skill instead. Download
`competitive-lifecycle-calendar.skill` from [Releases](../../releases), or build it
yourself with `bash scripts/build.sh`. Then **Customize → Skills → + → Create
skill → Upload a skill**.

An uploaded skill is a snapshot, not a subscription. It does not update itself. To
move to a new version, download the new `.skill` and upload it again; the same name
replaces the old one.

### ChatGPT

This follows the [Agent Skills open standard](https://help.openai.com/en/articles/20001066-skills-in-chatgpt),
so the same folder works unmodified. Take the `.skill` from [Releases](../../releases)
or build it, then **Skills → Create → Upload from your computer**. Requires a
Business, Enterprise, Healthcare or Edu plan.

`agents/openai.yaml` supplies the display name, blurb and default prompt ChatGPT
shows. Claude ignores that file.

### Codex

```bash
git clone https://github.com/email-love/lifecycle-calendar.git
cp -r lifecycle-calendar/skills/competitive-lifecycle-calendar ~/.codex/skills/
```

### Manually, into Claude Code

```bash
git clone https://github.com/email-love/lifecycle-calendar.git
cp -r lifecycle-calendar/skills/competitive-lifecycle-calendar ~/.claude/skills/
```

Once installed, the skill triggers on its own. Ask for a campaign calendar, a
moments calendar, or "what should we plan around next year, and what do competitors
actually do", and it loads.

### Verifying a download

Every release ships `SHA256SUMS`. From the directory holding the downloaded files:

```bash
sha256sum -c SHA256SUMS        # Linux
shasum -a 256 -c SHA256SUMS    # macOS
```

## How to run it

Give it a brand and, if it is not obvious from the brand, an industry. It will ask
for a region, a year and three to six competitors, then check how much history the
library actually holds for each competitor before promising anything.

```
Build a lifecycle calendar for a US non-alcoholic beverage brand.
Competitors: Athletic Brewing, Ghia, De Soi, Recess.
```

Thin coverage is reported in a line, not hidden. Coverage windows vary too: a brand
can have deep history that stops before the season you need, and the skill says so
rather than presenting a partial picture as a full one.

## One skill, both platforms

There is no Claude version and no ChatGPT version. Both products read the same
`SKILL.md` frontmatter and the same `references/` folder.

```
skills/competitive-lifecycle-calendar/
├── SKILL.md                      # frontmatter (name, description) + the workflow
├── LICENSE                       # every archive is independently licensed
├── references/                   # loaded on demand, not upfront
│   ├── notion-build.md           # schemas, build order, connector gotchas
│   └── idea-prompt.md            # the per-moment campaign idea framework
└── agents/openai.yaml            # ChatGPT display metadata; Claude ignores it
```

The reference files carry the weight on purpose. Both platforms load them only when
the skill reaches that step, so depth there is close to free, while depth in
`SKILL.md` is paid on every trigger.

For Claude's marketplace installs, the repository root doubles as the plugin.
`.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` point Claude Code
and the Claude apps at the same `skills/` folder, so there is still one copy of the
skill.

## Contributing

The most useful contribution is a report from a category we have not tried. Open an
issue with the industry, the competitor set, and what the build got wrong.

```bash
python3 -m pip install pyyaml==6.0.2
python3 scripts/validate.py     # frontmatter, metadata, versions, hygiene
bash scripts/build.sh           # package the skill into dist/*.skill
bash scripts/verify_dist.sh     # zip integrity, inventory, licence, checksums
```

Changing the version means editing `VERSION`, the `version` in both
`.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`, and adding a
matching `## [x.y.z]` section to `CHANGELOG.md`. The validator checks that all four
agree, and that the plugin still has the layout the Claude apps require.

## Credit

The calendar structure is adapted, with credit and thanks, from Luke Kline's
lifecycle-calendar skill, built for the Lifecycle Leaders community. The schemas are
deliberately kept compatible, so calendars from either skill work together. What
this version adds is the competitive evidence layer.

## Also from Email Love

[**email-love/claude-skills**](https://github.com/email-love/claude-skills) - skills
for building production emails in Figma with the Email Love plugin: design system
migration, audits, and export-ready email assembly.

[**email-love/esp-skills**](https://github.com/email-love/esp-skills) - skills for
the personalization languages inside ten email service providers.

[**emaillove.com**](https://www.emaillove.com) - curated email design inspiration,
and the Figma plugin that turns your designs into production code.

## License

MIT
