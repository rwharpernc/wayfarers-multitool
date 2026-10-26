# BGS

**Work in progress.** BGS tracking is still being built, and I'd really appreciate your feedback. If something
looks wrong, or you have a suggestion, please [open an issue](https://github.com/rwharpernc/wayfarers-multitool/issues).

The **Background Simulation (BGS)** is the game's behind-the-scenes model of factions and their influence. BGS mode
tracks faction states, and the effect of your own missions, bounties, trade, exploration and crimes on them.

There is nothing to set up: it records wherever you act. BGS is on by default (**Settings → WFMT → BGS**); with it turned off the panel says `BGS tracking is disabled — see Settings.`

**On this page:** [The panel](#the-panel) · [What it counts](#what-it-counts) ·
[The BGS Report window](#the-bgs-report-window) · [Resets and history](#resets-and-history) ·
[Tick detection](#tick-detection-and-the-internet) · [Settings](#settings)

**Where this comes from:**

- The journal records what *you* do (missions, bounties and bonds, trade, exploration data, crimes). It does not record what any of it did to a faction's influence.
- So the effects BGS shows are WFMT's own bookkeeping of your activity. Trade, for example, is an approximation.
- The one outside source is a community tick-time service, used to learn when the tick happens.

See [How WFMT knows what it knows](README.md#how-wfmt-knows-what-it-knows).

## The panel

Press **BGS** in the mode bar to open the page. It has a heading, the system block, a small gray tick line and a **REPORT** button.

The system block shows **only the system you're in**:

- a title line: the system's name (a ★ before it when you have pinned that system), then `— N faction(s):`,
- one line per faction present, controller first and then alphabetical (★ marks the controller; at most 8 are listed and `…and N more` follows),
- on each line the faction's state and influence, for example `Boom, 45.0% (+5.0)`,
- under a faction you have acted on, a `↳` line of what you did to it **since the last server tick** (missions done with `INF +2/-0`, failed and abandoned missions, bounty and combat bond credits, trade profit or loss, exploration data, crimes),
- `Nothing done here yet this tick.` when you have not acted in the system this tick.

State and influence show how far they moved since before the tick: the figures as the journal last reported them, compared with the figures from before the tick, for example `45.0% (+5.0)` for influence and `None → Boom` for a state that changed. The change is left off when WFMT has no figure from before the tick.

Other messages you can see in the block:

- `Current system: (unknown — jump somewhere first)` until WFMT has seen a jump or login,
- `<system> — waiting on faction data...` until a jump into the system (or a login there) brings its faction list,
- `<system> — no factions present (uninhabited system).`

**The tick line** under the block says where tick detection stands: `Tick check: not yet run.`, `Last tick: 2026-10-25 14:03 UTC`, `New tick at ... — totals reset, previous tick archived.`, or `Tick check failed (will retry): ...`. The first check runs about three seconds after EDMC starts, then once a minute.

**When the faction figures update.** The game puts a system's faction list (state, influence, and the pending, recovering and active states) into the journal only when you jump into the system, log in there, or arrive on a carrier jump. So the figures on the panel are as of your last arrival, not live: staying in a system through a tick does not change them until you leave and come back.

## What it counts

Increases and decreases from:

- **Missions completed** (influence pips gained or lost). Each effect is counted in the system the game names for it, which is not always where you hand the mission in. If the game names no system, the effect is counted in the system where you accepted the mission, and failing that where you handed it in. The pips are a count of the `+` signs the game shows (`+2/-0`), not a percentage.
- **Missions failed or abandoned.** Counted against the faction that issued the mission, in the system where you accepted it. A mission WFMT never saw you accept (for example one accepted before the journals it re-reads begin) is not counted.
- **Bounty voucher and combat bond redemptions**, for the faction named on the voucher, in the system where you redeem it. A bounty voucher can name several factions at once.
- **Trade profit or loss.** What you sell minus what you buy at a station, credited to that station's controlling faction. It needs WFMT to know the station's faction (you have docked at it, or you were at it on login). It is an approximation.
- **Exploration data sold**, credited to the station's controlling faction.
- **Crimes committed** against a faction, with the fines or bounties they cost. Each crime counts as a decrease.

A completed conflict mission that the game reports no influence for (seen on war and civil war missions) counts as `++` when the faction is in a war and `+` when it is in an election. These are assumptions, not values from the game.

Only play from the start of the current tick counts; the totals reset at each tick (see below).

## The BGS Report window

Click **REPORT** (view BGS report) on the BGS page.

- The **TICK** drop-down at the top picks the period: `Current tick — since <time>`, or an earlier one from the archive (`<start> → <end>`). The subtitle reads `N tab(s) — last 6 systems plus N pinned`.
- There is **one tab per system** (see below). The tabs wrap onto more than one row when there are many.
- Each tab has a **FACTIONS** table and a **WHAT YOU DID** table.
- A **help** button in the header explains the tabs and every column.
- **Copy Summary** copies every tick and system as plain text, ignoring the tab limit (the button changes to a confirmation for a moment). Paste it into a note or chat.
- The window stays open and updates as you play, and it remembers its size and position. It needs to be at least 1000 pixels wide so the columns fit.

**FACTIONS** has the columns **Faction** (★ before the controller), **State** (`Boom`, or `None → Boom` when it changed since before the tick), **Influence (change)** (`45.2% (+1.3)`), and **Pending**, **Recovering** and **Active** (the state names the game lists for that faction). A faction you acted on but have no faction list for is shown by name only.

**WHAT YOU DID** has one row per faction you acted on, with the columns:

| Column | Meaning |
|---|---|
| **Missions** | Missions completed |
| **INF pips +/-** | Influence pips gained and lost, such as `+3/-0` |
| **Failed**, **Abandoned** | Missions that cost the issuing faction influence |
| **Bounties (cr)**, **Combat bonds (cr)** | The voucher value redeemed |
| **Trade (cr)** | Sold minus bought, with a sign. Negative is a loss |
| **Exploration (cr)** | Exploration data sold |
| **Crimes** | Crimes committed against that faction |

Empty cells mean none.

### Which systems get a tab?

Tabs show the last 6 systems you've been in (the one you're in first), each with its full system name.

- **☆ Pin** (top right of a tab) keeps it, and the button then reads **★ Unpin**. A pinned system (marked ★) stays in the tab row however long ago you were there, and shows a ★ on the panel when you're in it.
- **× Close tab** hides one you don't want. A closed tab stays closed (and is unpinned) until you bring it back with **Add system**.
- **SHOW A SYSTEM** box: click its arrow to pick from every system you've been in, or just start typing and the list
  narrows as you type (names starting with what you typed come first). Press Enter or click **Add system**. That
  pins it, and it's also how you bring back a closed tab. Any name can be typed, not only ones from the list (up to 60 characters).
- With no tab to show the window says `No systems to show yet — use "Show a system" above to add one.`
- Pins and closed tabs are kept per commander.

## Resets and history

- The totals **reset at each tick**, and the closed tick is archived: the panel starts over and the closed tick moves into the TICK drop-down.
- The archive keeps **7 days** of closed ticks by default (1 to 90 in Settings); older ones are dropped.
- When EDMC starts, WFMT re-reads your last few journals, so the totals are cumulative since the tick even if EDMC
  wasn't running the whole time.
- **Play made while EDMC was closed still reaches the history.**
  - When a tick closes a period, WFMT rebuilds that period from your journals.
  - It files the rebuilt version over the one it saw live, keeping any faction only the live one had.
  - It reads back up to 14 days. An older period stays as it was filed.
  - If several ticks passed while EDMC was closed, WFMT cannot tell them apart, so everything you did across them is in the one period that closed.
- While the journals are re-read in the background, the panel's catch-up note shows `BGS`.
- On Linux the re-read needs EDMC's journal folder to be set; the BGS settings page warns when it is not.
- Everything is kept separately for each commander.

## Tick detection and the internet

WFMT checks a community tick-time service **once a minute** to notice the real tick. That is the only internet
connection BGS makes, and you can turn it off in Settings. It is a request for the latest tick time; nothing about you or your play is sent.

Without it, the totals never reset on their own and the journals can't be replayed, because WFMT doesn't know when
the tick was.

## What the game does and doesn't tell us, and how to work around it

WFMT, like every third-party tool, only knows what Elite Dangerous writes to its journal files.

- It adds the BGS tick time from a community tick-time service and works around the rest.
- Where it can't be sure, WFMT says so rather than guess quietly.

See [How WFMT knows what it knows](README.md#how-wfmt-knows-what-it-knows).

| What you might expect | What the game gives | What to do |
|---|---|---|
| Exact influence caused by your trade | Trade is counted as net credits traded at the station's controlling faction. It is an **approximation**, not the game's real supply-and-demand rules. | Use it to compare your own effort, not as a precise influence figure. |
| Several ticks of play, if EDMC was closed over them | The journal does not say which tick a thing belongs to once they have passed, only when it happened, and WFMT learns ticks from a third-party service while it runs. | Nothing: the play across the missed ticks is filed in the one period that closed. |
| Missions shown as an exact percentage | Frontier gives influence **pips** and a mission count, never a percentage. | Read the pips as strength, not a number. |
| Every crime and kill attributed to a victim faction | Only what `CommitCrime` reports is counted. Kills have no victim-faction attribution. | Don't rely on BGS for the effects of murder. |
| Combat zones as their own signal | Only the resulting bounty or combat-bond **redemption** is counted, not zone presence or wins. | Redeem your vouchers and bonds in the system you fought in. |
| Thargoid war states | Not tracked. | Use the game's galaxy map for those. |
| Ticks from before you installed WFMT | The tick service only reports the **latest** tick, so earlier periods cannot be rebuilt from old journals. | The archive starts at the first tick WFMT sees roll over. Keep tick detection on. |
| Tick detection to always work | It uses a third-party service over plain HTTP, with no guarantee it is up. When it is down the tally just doesn't roll over. | Turn tick detection off in Settings if you prefer. Without it, totals never reset on their own. |

## Settings

**Settings → WFMT → BGS**:

- **Show BGS faction states and activity**: BGS on or off (on by default),
- **Detect BGS ticks (polls tick.infomancer.uk every 60s)**: tick detection on or off (on by default). Without it the totals never reset on their own and the journals are not replayed,
- **Keep previous ticks for N days (1-90)**: how long closed ticks stay in the archive (default 7).

Settings take effect when you close the Settings window.

More detail: [BGS specification](../BGS_TECH_SPEC.md).
