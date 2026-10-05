# Changelog

User-visible changes to the Competitive Lifecycle Calendar skill, newest first.
Every release attaches the `.skill` bundle and a `SHA256SUMS` file.

## [1.0.1] - 2026-10-05

A packaging fix. The skill itself is unchanged, and the `.skill` bundle is
byte-identical to 1.0.0.

- Adding this repository as a marketplace in the Claude apps (**Customize →
  Plugins → Add marketplace** in Cowork, the desktop app or claude.ai) failed with
  "Marketplace sync failed". Those apps require a `.claude-plugin/plugin.json`
  manifest in the plugin folder, and the plugin folder had none. Claude Code never
  required one, so installs there were unaffected.
- The repository root is now the plugin. It carries `.claude-plugin/plugin.json`,
  and the skill stays where it was, at `skills/competitive-lifecycle-calendar/`.
- The Claude Code plugin id is unchanged:
  `competitive-lifecycle-calendar@email-love-lifecycle-calendar`.

## [1.0.0] - 2026-09-02

First release, split out of [email-love/claude-skills](https://github.com/email-love/claude-skills)
into its own repository so it can be installed on its own, in either Claude or ChatGPT.

- Builds a ranked year-of-moments lifecycle calendar in Notion: one moments database,
  one campaigns database, a two-way relation between them, calendar views, and a
  two-column home page.
- Puts competitive evidence in the body of every Core moment: what competitor brands
  actually sent last year, when they started, what they offered, how deep they
  discounted, and a link to each cited email.
- Ends the build with an offer guardrails summary across the whole competitive set:
  the deepest discount observed and where, the standard promo range, and which
  occasions carry no discount at all.
- Moments no competitor claims get an honest open-lane note rather than invented
  evidence. Thin competitor coverage is reported, not papered over.
- Campaign ideas are generated on demand per moment, grounded in that moment's
  evidence, rather than pre-written into the calendar.

Calendar structure adapted, with credit and thanks, from Luke Kline's
lifecycle-calendar skill for the Lifecycle Leaders community.
