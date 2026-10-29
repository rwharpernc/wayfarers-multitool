# Powerplay

**Work in progress.** Powerplay is still being built, and I'd really appreciate your feedback. If something looks
wrong, or you have a suggestion, please [open an issue](https://github.com/rwharpernc/wayfarers-multitool/issues).

Powerplay mode tracks the **merits** and **Control Points (CP)** you earn for your pledged Power. You see them live
on the panel, and in the Sessions window per session, per system, per Powerplay cycle and per day.

Everything is kept **separately for each commander**. A commander pledged to another Power, or to none, has their
own numbers.

**On this page:** [How to](#how-to) · [Using it](#using-it) · [The Sessions window](#the-sessions-window) · [Cycles](#cycles) ·
[The Systems tab](#the-systems-tab) · [Catching up from your journals](#catching-up-from-your-journals) ·
[What the game does and doesn't tell us](#what-the-game-does-and-doesnt-tell-us-and-how-to-work-around-it) · [Rare Goods Finder](#rare-goods-finder) · [Settings](#settings)

**Where this comes from:**

- Merits come straight from the journal and are exact.
- The journal doesn't say which activity earned a merit, so WFMT infers the activity from the state of the system.
- The journal doesn't report Control Points at all, so WFMT estimates CP from ratios you can edit.
- Whole-system figures are only as fresh as your last visit.
- Spansh supplies the Rare Goods Power column.

See [How WFMT knows what it knows](README.md#how-wfmt-knows-what-it-knows).

## How to

### See your merits for this session and this cycle

1. Press **P.P.** in the mode bar.
2. Read `Session merits` and `Session CP` for this login, and `Cycle N merits` and `Cycle N CP` for the whole cycle.
3. Read `Here: N merits` for what you have earned in the system you are in.

**Example.** You hand in merits in Nervi, then jump to another system and do more. The panel shows `Here:` for the new
system only, `Session merits` for both together, and the `Cycle` lines for everything since Thursday 07:00 UTC, including
earlier game sessions.

### See which systems earned you the most

1. Press **P.P.**, then **REPORT**.
2. On the **Current session** tab, read **By System**: the **Merits**, **Est. CP** and **Activity breakdown** columns
   list each system you worked this login.
3. For a whole cycle, open the **Systems** tab, or the **Cycles** tab for one row per cycle.

### Check a system you are defending

1. Open **REPORT**, then the **Systems** tab.
2. Find the system's tab (your last 6 systems get one). If it is missing, type its name in **SHOW A SYSTEM** and press
   **Add system**.
3. Compare **Baseline** and **Latest** in the **STANDING** table. The **Change** column shows whether it is gaining or
   losing ground.
4. Click **☆ Pin** to keep the tab in every cycle.

**Example.** You pledge to defend a system and want to see whether it is holding. Add it with **SHOW A SYSTEM**, pin it,
and jump in again whenever you want a fresh reading: the figures only update when you jump into or log in at the system.

### Fix a session count that looks wrong

1. If you only want to remove a mistaken count, open **REPORT** and press **Reset Current System** (this system) or
   **Reset Session** (everything this login). Both ask first and cannot be undone.
2. If merits were missed after restarting EDMC, press **RESCAN** on the Powerplay panel instead. It re-reads the current
   journal from scratch.

Resets change the session only. Cycle totals come from your journal and are not affected.

### Share your progress

1. Open **REPORT** and press **Copy Progress**. The button changes to a confirmation for a moment.
2. Paste into Discord or a forum post. With the default format each system is one line, for example
   `[Nervi](link) - 120 merits (~48 CP) - Exploited`.
3. To change the layout, edit the **Clipboard** format under **Settings → WFMT → Powerplay**.

**Share to Discord.** Above the tabs in the same window are **Copy for Discord** and **Post to Discord**.

1. **Copy for Discord** puts this session's progress on the clipboard with Discord's formatting (each system links to Inara; the estimated CP is marked `~`), followed by the cycle's total line. Paste it into Discord yourself.
2. **Post to Discord** sends the same text to the webhook you saved on **Settings → WFMT → Discord**. Press it again later in the same session and the earlier post is edited; a new login is a new post.
3. **Customize…** changes how the Discord post looks (presets, which parts appear, saved templates). The editable clipboard format above applies to **Copy Progress** only. Set up Discord, with examples, in [Sharing reports to Discord](discord.md).

### Find a rare good to haul

1. Press **RARES**, then set **Show nearest** (type a number and press Enter or **Apply**).
2. Tick **Large pads only** if you fly a large ship, and **Only my Power** to keep rares from systems your Power controls.
3. Select a row, then press **Copy system** and paste the name into the galaxy map's search.

**Example.** You fly a large ship and are pledged. Tick both boxes and leave **Show nearest** at 10: you get the ten
nearest rares that sell at a large-pad station in a system your Power controls, because the filters apply before the
number shown.

### Work out Control Points from merits

CP is an estimate: merits divided by the ratio for the activity (defaults: Acquisition 4.0, Reinforcement 2.5,
Undermining 4.2).

**Example.** 500 Reinforcement merits are about 200 CP (500 / 2.5). 400 Acquisition merits are about 100 CP (400 / 4.0).
Delivery and Unattributed merits add merits but no CP.

## Using it

Just play. Press **P.P.** in the mode bar to open the page. Top to bottom it shows:

- a status line (`Awaiting PowerPlay activity…` until the game reports your pledge, then `Pledged to <Power>`, `Left PowerPlay`, `Defected to <Power>` or `CMDR <name>: not a PP Pledge`),
- the current system in bold, as `<system> — <state> (<controller>)` (for example `Nervi — Exploited (Zachary Hudson)`); the part in brackets is the controlling Power, `contested` when several Powers are in the system, or `uncontested`; with no Powerplay data the state reads `no PP data`,
- `Here: N merits` and a `CP:` line, what you've earned in that system this session,
- `Session merits` and `Session CP`, the running totals for this login,
- `Cycle N merits` and `Cycle N CP`, running totals for the **whole Powerplay cycle** so far, across every system. These carry over
  between game sessions and reset when the cycle ends (Thursday 07:00 UTC); the Cycles tab shows the same numbers per cycle,
- `Cycle N megaships: 5 (2,340 merits)`,
- the last merit event (`No merit events yet this session.` until one arrives).

The CP lines list the estimated Control Points by activity, for example Acquisition, Reinforcement and Undermining. Delivery and unattributed merits add merits but no CP (see the table at the end of this page).

Your game mode and credits are on the two lines under the mode buttons, and a line such as `Merits this session: +1,234 (+567 merits/hr)` follows them (the rate appears after about three minutes).

Three buttons on the bottom row:

- **REPORT** opens the Sessions window.
- **RARES** opens the Rare Goods Finder (see below).
- **RESCAN** re-reads the current journal from scratch to recover merits missed after an EDMC restart. Use it if a session's numbers ever look wrong. Hover over a button for a one-line reminder.

## The Sessions window

Click **REPORT**. It has six tabs.

| Tab | What it shows |
|---|---|
| **Current session** | This login. **By System** lists what you earned in each system (columns **System**, **Merits**, **Est. CP**, **Activity breakdown**; the current system is marked and stays first). **By Activity (session total)** has the columns **Activity**, **Merits**, **Merits/CP**, **Est. CP** and **CP/hr**. **Current PowerPlay Context** shows what WFMT is using to attribute merits: the system, its state, its controller and the rival Powers. A heading above shows the commander, Power, start time and duration. |
| **Systems** | One tab per system for the cycle, with the system's standing and what you earned there. |
| **Cycles** | One row per Powerplay cycle, newest first: **Cycle**, **Period (UTC)**, **Power** you were pledged to, **Systems** worked, **Merits**, **Est. CP** and **Merits by activity**. |
| **Daily** | **Day**, **Date (UTC, from 07:00)**, **Merits** and **Est. CP** (whole numbers) for each day of a cycle, with a total. |
| **Megaships** | The megaships whose datalink you scanned: **Cycle**, **Megaship**, **System**, **Scanned (UTC)** and **Merits**. |
| **History** | Every past session of the commander you are playing (**Started**, **Commander**, **Power**, **Duration**, **Merits**, **Est. CP**) with their running total under **All Sessions**. Other commanders' sessions are kept but not shown, and each commander keeps their own last 200. |

A help button in the window's header repeats the notes for each tab. The window keeps its size and position.

### Cycles

A Powerplay cycle runs from **Thursday 07:00 UTC** to the next Thursday 07:00 UTC, and is numbered. For example,
cycle 101 began on 2026-10-01. Each day of a cycle also runs 07:00 to 07:00 UTC, so **day 1 is the Thursday**.

The Systems and Daily tabs have a **CYCLE** drop-down to look at an earlier cycle; the Cycles tab already lists them all.

### Megaships

Powerplay rewards scanning the datalink of a megaship (the activity is called *Scan datalinks at Megaships*). WFMT keeps a list of the megaships you
scan, and counts them for the cycle.

- The **Megaships** tab has one row per megaship: its name, the system, when you scanned it and the merits that scan earned. The live cycle is first.
- The main panel has a line under the cycle tally, for example `Cycle 103 megaships: 5 (2,340 merits)`.

- **How it knows which megaship.** The game's journal does not name the ship in the scan. WFMT takes the name from the megaship you **dropped out of
  supercruise at** just before the scan (the journal writes it when you drop), and checks that it really is a megaship: it is one the FSS listed in
  that system, or its name has "class" in it ("Aquarius-class Tanker"). A scan at a station, a settlement or an ordinary ship is not counted.
- **One per megaship per system per cycle.** Scanning the same megaship again the same cycle changes nothing.
- **Merits** are those of the `PowerplayMerits` event that follows the scan within a few seconds. They can be blank: when you are not pledged, or the
  game gave none. WFMT counts the scan either way.
- **A scan without the drop.** If you approach a megaship some other way (for example from a different supercruise destination) and scan it, the
  journal never named it, so WFMT cannot count it. Drop out of supercruise at the megaship first.
- **Old cycles.** The first time WFMT starts, it reads your journals back as far as the Settings scan depth (4 cycles by
  default) and fills in the earlier cycles too. Each commander has their own list.

### The buttons at the top

- **Refresh** redraws the window.
- **Copy Progress** copies one line per system you have visited this session to the clipboard (format in Settings; the default is `[system](link) - N merits (~N CP) - state`, with a link to the system on Inara; the button changes to a confirmation for a moment).
- **Reset Current System** zeroes the merits earned in the system you are in during this session, and takes them off the
  session totals too. It asks first and can't be undone (with no current system it says so).
- **Reset Session** zeroes this session's merit totals (every system and activity) without ending the session. It asks first
  and can't be undone. Use it to correct a bad count.

Both resets change the **session** only. The cycle totals on the panel and the Systems, Cycles and Daily tabs come from your
journal, so they are not affected; **RESCAN** is the way to rebuild a session from the journal.

### The Systems tab

A line above the tabs names the commander and Power and how many tabs show (`N tab(s): last 6 systems plus N/5 pinned`). A second line totals the cycle: merits, estimated CP and how many systems you worked. Then, one tab per
system, each with two tables, **STANDING** and **WHAT YOU DID**:

- **Standing** compares a baseline with the latest reading. The baseline is the system's last reading before the
  cycle began, or your first reading this cycle. The table shows state, controlling Power, control progress,
  reinforcement and undermining, and the change. The columns are **Standing**, **Baseline**, **Latest** and **Change**. With no reading yet the table says to jump in or log in there.

  These are **whole-system figures from the journal**, everyone's work and not just yours. So if you're defending a
  system, you can see it gaining or losing ground. They only update when you jump into or log in at the system, so
  they are as fresh as your last visit.
- **What you did** shows your own merits there by activity (columns **What you did**, **Merits**, **Events**, **Est. CP**).

**Which systems get a tab?** Your last 6 systems, plus up to **5 you pin**.

- Click **☆ Pin** on a tab to keep it (the button then reads **★ Unpin**). Pinned tabs stay in every cycle, even with no data. At the limit of 5 pins WFMT says `You can pin up to 5 systems. Unpin one first.`
- Or type a name in **SHOW A SYSTEM** (it suggests as you type) and press **Add system**, which pins it and brings a closed tab back.
- **× Close tab** hides a system.

Pins and hidden tabs are remembered for each commander.

## Catching up from your journals

The first time WFMT sees a commander, it reads their journals to fill in the last few cycles (4 by default; change
it under **Settings → WFMT → Powerplay → Journal scan**, from 1 to 12). After that it reads only what happened while EDMC
was closed, so **playing without EDMC running doesn't lose a cycle**.

It works out what cycle it is, which cycles aren't in that commander's history yet and how many days back to read,
and does nothing when there's nothing new. The **Cycles** tab shows what it did.

It can't read journals you've deleted, and your own totals are never replaced by smaller ones.

## What the game does and doesn't tell us, and how to work around it

WFMT, like every third-party tool, only knows what Elite Dangerous writes to its journal files.

- It adds what Spansh reports (for the Rare Goods Power column) and works around the rest.
- Where it can't be sure, WFMT says so rather than guess quietly.
- Your merit totals always come straight from the journal and are exact.

See [How WFMT knows what it knows](README.md#how-wfmt-knows-what-it-knows).

| What you might expect | What the game gives | What to do |
|---|---|---|
| Each merit tagged with the activity that earned it | The journal does not say. WFMT **infers** the activity from the state of the system you are in; an unusual situation can be misattributed. This also applies to the per-system and daily numbers. | Trust the merit totals. Treat the activity split as a good guess. |
| Control Points reported | The game reports merits only. CP is **estimated** with ratios you can edit in Settings. | Only change the ratios if Frontier changes them. |
| The name of a megaship you scanned | The scan event does not name it. WFMT uses the megaship you dropped to just before ([Megaships](#megaships)). | Drop out of supercruise at the megaship, then scan. |
| Deliveries counted as CP | The game writes a `PowerplayDeliver` event (what and how many) just before the merits a hand-in earns, but it does not say which kind you chose (Acquisition, Reinforcement or Undermining). WFMT labels the merit events that follow a hand-in *Delivery*: the first one within 10 minutes, and any within 10 seconds of the last. It counts **merits only**. Unattributed merits are the same. A merit from something else that lands inside that window can be mislabeled. | Expect Delivery and Unattributed to add merits but no CP. Hand in as a separate step, away from other merit work, if the split matters. |
| Live standing for any system | Whole-system figures update only when you **jump into or log in** at that system, so they are as fresh as your last visit. | Visit the system again for a fresh reading. |
| Old cycles from before WFMT | They are rebuilt from journals only as far back as the files still exist and the scan depth allows (1 to 12 cycles, 4 by default). | Raise the depth in Settings, and keep your journal files. |
| The Rare Goods list to include new rares | The list is a snapshot (141 rare goods). A new rare needs a WFMT update. | Update WFMT. The Power column also needs Spansh and shows "—" when it can't be checked. |

- The detail is in the [Powerplay specification](../POWERPLAY_TECH_SPEC.md).

## Rare Goods Finder

Click **RARES** to see the rare commodities closest to where you are. Each row shows:

- the origin system and its **Distance** in light years from the system you are in,
- the station and its **Arrival** distance, how far it is from the arrival star in light seconds (approximate: the figures were compiled once and some may be off by a little),
- the landing-pad size,
- its **Legality** (see below),
- which Power currently controls that system, which is handy for Powerplay hauling.

**How to use it:**

1. Press **RARES**. The list needs your position, so it says "Awaiting system data" until your first jump or login after EDMC starts. If the game is closed, press **Use last known location** to take your commander's last position from the journals.
2. Choose how many to see with **Show nearest** (type a number, press Enter or **Apply**; 10 by default, at most 141). The list holds 141 rare goods.
3. Narrow it with **Large pads only** and **Only my Power** if you want. Both apply *before* the number shown, so with "Show nearest: 10" you get the ten nearest that match.
4. Click a heading to sort by it (numbers sort as numbers; a second click reverses). Select a row to see where that rare is illegal.
5. Press **Copy system** to put the selected rare's origin system on the clipboard, then paste it into the galaxy map's search. With no row selected it asks you to select one.

The table has the columns **Rare Good**, **Origin System**, **Distance**, **Station**, **Arrival**, **Pad**, **Legality** and **Controlling Power**. The window's subtitle names your current system (and the Power when **Only my Power** is on), and a help button explains the columns.

**Controls:**

| Control | What it does |
|---|---|
| **RARES** (Powerplay panel) | Opens the window |
| **Show nearest** and **Apply** | How many rows to show (remembered) |
| **Large pads only** | Keeps the rares sold at large-pad stations (20 of the 141), for a large ship |
| **Only my Power** (shown as **Only my Power (Your Power)**) | Keeps the rares whose origin system is controlled by the Power you are pledged to. Grayed out, and labeled `(not pledged or not known yet)`, until WFMT knows your Power (the journal writes it at login when you are pledged). To find them WFMT asks Spansh which Power controls each origin system, nearest first and ten at a time, until it has enough (at most all 141, once per session) |
| **Copy system** | Puts the selected row's origin system on the clipboard |
| **Use last known location** | Takes your commander's last position from the journals, for when the game is closed or no jump or login has been seen yet |
| **Refresh** | Redraws the list |
| Click a heading | Sorts by that column |
| Double-click a row | Opens that commodity on Inara |

Both filter choices and the number to show are remembered. In the Power column "…" means the lookup is still running, and "—" means unclaimed or couldn't be checked.

**Legality.**

- *Legal* means the table lists no place the rare is illegal (128 of the 141).
- For the 13 that are restricted (liquors, the Onionhead family and similar narcotics, Kamitra Cigars, Lyrae Weed and a few others), the column says *Illegal here* or *Legal here* for the system you are in.
  - It uses that system's allegiance and government from the journal when you jump or log in.
  - It says *Restricted* until WFMT knows them.
  - It says nothing about the system you are heading for.
- **The table is community data, curated by hand, and has not yet been checked in the game.** Treat it as a guide, and check the station's Prohibited list on the system map before you carry a restricted rare.

To fill in the Power column, WFMT asks Spansh which Power controls each rare's origin system. Answers are kept until
you restart EDMC (a failed lookup is also kept, so it isn't retried until then). See
[what goes on the internet](internet-and-privacy.md).

## Settings

**Settings → WFMT → Powerplay**:

- **CP Ratios**: the merits needed for 1 Control Point, per activity. The defaults are Acquisition 4.0, Reinforcement 2.5 and Undermining 4.2, community-sourced estimates. Only change these if Frontier changes them or your in-game totals disagree. System strength, ethos and squadron bonuses are already inside the merits the journal reports, so there is nothing separate to enter for them. Delivery and Unattributed have no ratio.
- **Clipboard**: the format of the lines **Copy Progress** copies. That button is in the Sessions window; it puts a summary on
  your clipboard to paste into Discord or a forum post. The placeholders are `{system}`, `{system_url}`, `{merits}`, `{cp}` and `{state}`. A **Reset to default** button restores the standard format.
- **Journal scan**: **Cycles to scan**, how many cycles back (this one included, 1 to 12; default 4) the start-up scan covers for a commander WFMT has not seen before.

Ratios, clipboard format and scan depth are saved when you close Settings.
