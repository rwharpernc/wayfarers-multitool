# Powerplay

**Work in progress.** Powerplay is still being built, and I'd really appreciate your feedback. If something looks
wrong, or you have a suggestion, please [open an issue](https://github.com/rwharpernc/wayfarers-multitool/issues).

Powerplay mode tracks the **merits** and **Control Points (CP)** you earn for your pledged Power. You see them live
on the panel, and in the Sessions window per session, per system, per Powerplay cycle and per day.

Everything is kept **separately for each commander**. A commander pledged to another Power, or to none, has their
own numbers.

**On this page:** [Using it](#using-it) · [The Sessions window](#the-sessions-window) · [Cycles](#cycles) ·
[The Systems tab](#the-systems-tab) · [Catching up from your journals](#catching-up-from-your-journals) ·
[What the game does and doesn't tell us](#what-the-game-does-and-doesnt-tell-us-and-how-to-work-around-it) · [Rare Goods Finder](#rare-goods-finder) · [Settings](#settings)

**Where this comes from:**

- Merits come straight from the journal and are exact.
- The journal doesn't say which activity earned a merit, so WFMT infers the activity from the state of the system.
- The journal doesn't report Control Points at all, so WFMT estimates CP from ratios you can edit.
- Whole-system figures are only as fresh as your last visit.
- Spansh supplies the Rare Goods Power column.

See [How WFMT knows what it knows](README.md#how-wfmt-knows-what-it-knows).

## Using it

Just play. The panel shows:

- your current system's Powerplay state,
- what you've earned in that system,
- running merit totals and estimated CP for the session,
- running merit totals and estimated CP for the **whole Powerplay cycle** so far, across every system. These carry over
  between game sessions and reset when the cycle ends (Thursday 07:00 UTC); the Cycles tab shows the same numbers per cycle.

Your game mode and credits are on the two lines under the mode buttons.

Two buttons on the bottom row:

- **SES** opens the Sessions window. **RARES** opens the Rare Goods Finder (see below).
- **RESCAN** re-reads your journal from scratch. Use it if a session's numbers ever look wrong.

## The Sessions window

Click **SES**. It has six tabs.

| Tab | What it shows |
|---|---|
| **Current session** | This login: merits and estimated Control Points by system and by activity, and the Power context WFMT is using. |
| **Systems** | One tab per system for the cycle, with the system's standing and what you earned there. |
| **Cycles** | One row per Powerplay cycle, newest first: period, the Power you were pledged to, systems worked, merits, estimated CP, merits by activity. |
| **Daily** | Merits and estimated CP (whole numbers) for each day of a cycle, with a total. |
| **Megaships** | The megaships whose datalink you scanned, cycle by cycle: its name, the system, when, and the merits the scan earned. |
| **History** | Every past session of the commander you are playing, with their running total. Other commanders' sessions are kept but not shown, and each commander keeps their own last 200. |

### Cycles

A Powerplay cycle runs from **Thursday 07:00 UTC** to the next Thursday 07:00 UTC, and is numbered. For example,
cycle 101 began on 2026-10-01. Each day of a cycle also runs 07:00 to 07:00 UTC, so **day 1 is the Thursday**.

The Systems, Cycles and Daily tabs all have a drop-down to look at an earlier cycle.

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
- **Copy Progress** copies one line per system you have visited this session to the clipboard (format in Settings).
- **Reset Current System** zeroes the merits earned in the system you are in during this session, and takes them off the
  session totals too. It asks first and can't be undone.
- **Reset Session** zeroes this session's merit totals (every system and activity) without ending the session. It asks first
  and can't be undone. Use it to correct a bad count.

Both resets change the **session** only. The cycle totals on the panel and the Systems, Cycles and Daily tabs come from your
journal, so they are not affected; **RESCAN** is the way to rebuild a session from the journal.

### The Systems tab

A line above the tabs totals the cycle: merits, estimated CP and how many systems you worked. Then, one tab per
system:

- **Standing** compares a baseline with the latest reading. The baseline is the system's last reading before the
  cycle began, or your first reading this cycle. The table shows state, controlling Power, control progress,
  reinforcement and undermining, and the change.

  These are **whole-system figures from the journal**, everyone's work and not just yours. So if you're defending a
  system, you can see it gaining or losing ground. They only update when you jump into or log in at the system, so
  they are as fresh as your last visit.
- **What you did** shows your own merits there by activity, with estimated Control Points.

**Which systems get a tab?** Your last 6 systems, plus up to **5 you pin**.

- Click **☆ Pin** on a tab to keep it. Pinned tabs stay in every cycle, even with no data.
- Or type a name in **Show a system** (it suggests as you type) and press **Add system**.
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

1. Press **RARES**. The list needs your position, so it says "Awaiting system data" until your first jump or login after EDMC starts.
2. Choose how many to see with **Show nearest** (type a number, press Enter or **Apply**). The list holds 141 rare goods.
3. Narrow it with **Large pads only** and **Only my Power** if you want. Both apply *before* the number shown, so with "Show nearest: 10" you get the ten nearest that match.
4. Click a heading to sort by it (numbers sort as numbers; a second click reverses). Select a row to see where that rare is illegal.
5. Press **Copy system** to put the selected rare's origin system on the clipboard, then paste it into the galaxy map's search.

**Controls:**

| Control | What it does |
|---|---|
| **RARES** (Powerplay panel) | Opens the window |
| **Show nearest** and **Apply** | How many rows to show (remembered) |
| **Large pads only** | Keeps the rares sold at large-pad stations (20 of the 141), for a large ship |
| **Only my Power** | Keeps the rares whose origin system is controlled by the Power you are pledged to. Grayed out until WFMT knows your Power (the journal writes it at login when you are pledged). To find them WFMT asks Spansh which Power controls each origin system, nearest first and ten at a time, until it has enough (at most all 141, once per session) |
| **Copy system** | Puts the selected row's origin system on the clipboard |
| **Refresh** | Redraws the list |
| Click a heading | Sorts by that column |
| Double-click a row | Opens that commodity on Inara |

Both filter choices are remembered. A "—" in the Power column means unclaimed, or couldn't be checked.

**Legality.**

- *Legal* means the table lists no place the rare is illegal (128 of the 141).
- For the 13 that are restricted (liquors, the Onionhead and similar narcotics, Kamitra Cigars), the column says *Illegal here* or *Legal here* for the system you are in.
  - It uses that system's allegiance and government from the journal when you jump or log in.
  - It says *Restricted* until WFMT knows them.
  - It says nothing about the system you are heading for.
- **The table is community data, curated by hand, and has not yet been checked in the game.** Treat it as a guide, and check the station's Prohibited list on the system map before you carry a restricted rare.

To fill in the Power column, WFMT asks Spansh which Power controls each rare's origin system. Answers are kept until
you restart EDMC (a failed lookup is also kept, so it isn't retried until then). See
[what goes on the internet](internet-and-privacy.md).

## Settings

**Settings → WFMT → Powerplay**:

- The merit-per-Control-Point ratios. Only change these if Frontier changes them.
- The format of the lines **Copy Progress** copies. That button is in the Sessions window; it puts a summary on
  your clipboard to paste into Discord or a forum post. A **Reset to default** button restores the standard format.
- How many cycles the start-up journal scan covers.
