# Powerplay

Powerplay mode tracks the **merits** and **Control Points (CP)** earned for the pledged Power. The figures are shown on the panel, and in the Sessions window per session, per system, per Powerplay cycle and per day.

Powerplay tracking is a work in progress. Report problems or suggestions through the [issue tracker](https://github.com/rwharpernc/wayfarers-multitool/issues).

All data is stored separately for each commander. A commander pledged to another Power, or to none, has separate figures.

**On this page:** [How to](#how-to) · [Using it](#using-it) · [The overlay card](#the-overlay-card) · [The Sessions window](#the-sessions-window) · [Cycles](#cycles) · [The Systems tab](#the-systems-tab) · [Catching up from your journals](#catching-up-from-your-journals) · [What the game does and doesn't tell us](#what-the-game-does-and-doesnt-tell-us-and-how-to-work-around-it) · [Rare Goods Finder](#rare-goods-finder) · [Settings](#settings)

**Data sources**

- Merits come directly from the journal and are exact.
- The journal does not state which activity earned a merit. WFMT infers the activity from the state of the system.
- The journal does not report Control Points. WFMT estimates CP from editable ratios.
- Whole-system figures are as current as the last visit to the system.
- Spansh supplies the Power column of the Rare Goods Finder.

See [How WFMT knows what it knows](README.md#how-wfmt-knows-what-it-knows).

## How to

### View merits for the session and cycle

1. Press **Powerplay** in the mode bar.
2. Read `Session merits` and `Session CP` for the current login, and `Cycle N merits` and `Cycle N CP` for the whole cycle. When both pairs would show the same figures, only the Cycle pair is shown, with `(all this session)` after the merits.
3. Read `Here: N merits` for the merits earned in the current system.

**Example.** Merits are handed in at Nervi, then more merits are earned in another system. The panel shows `Here:` for the new system only, `Session merits` for both systems together, and the `Cycle` lines for everything since Thursday 07:00 UTC, including earlier game sessions.

### See which systems earned the most

1. Press **Powerplay**, then **Report**.
2. On the **Current session** tab, read **By System**. The **Merits**, **Est. CP** and **Activity breakdown** columns list each system worked in the current login.
3. For a whole cycle, open the **Systems** tab. For one row per cycle, open the **Cycles** tab.

### Check a system being defended

1. Open **Report**, then the **Systems** tab.
2. Find the system's tab (the last 6 systems visited each have one). If it is missing, type its name in **SHOW A SYSTEM** and press **Add system**.
3. Compare **Baseline** and **Latest** in the **STANDING** table. The **Change** column shows the difference.
4. Press **☆ Pin** to keep the tab.

The figures update only on a jump into the system or a login there.

### Fix a session count that looks wrong

1. To remove a mistaken count, open **Report** and press **Reset Current System** (current system) or **Reset Session** (everything in this login). Both ask for confirmation and cannot be undone.
2. If merits were missed after restarting EDMC, press **Rescan** on the Powerplay panel. It re-reads the current journal from scratch.

Resets change the session only. Cycle totals come from the journal and are not affected.

### Share progress

1. Open **Report** and press **Copy Progress**. The button text changes to `Copied!` for 1.5 seconds.
2. Paste the text into Discord or a forum post. With the default format each system is one line, for example `[Nervi](link) - 120 merits (~48 CP) - Exploited`.
3. To change the layout, edit the **Copy Progress** format on the **Settings** tab of the Powerplay Sessions window.

**Share to Discord.** The buttons are above the tabs in the same window.

1. **Copy for Discord** places the session's progress on the clipboard with Discord formatting (each system links to Inara; the estimated CP is marked `~`), followed by the cycle's total line.
2. **Post to Discord** sends the same text to the webhook saved on **Settings → WFMT → Discord**. Posting again in the same session edits the earlier post.
3. **Customize…** changes the appearance of the Discord post (presets, parts shown, saved templates). The editable clipboard format applies to **Copy Progress** only.
4. Webhook setup is described in [Sharing reports to Discord](discord.md).

### Find a rare good to haul

1. Press **Rares**, then set **Show nearest** (type a number and press Enter or **Apply**).
2. Tick **Large pads only** to keep rares sold at large-pad stations. Tick **Only my Power** to keep rares from systems controlled by the pledged Power.
3. Select a row, press **Copy system** and paste the name into the galaxy map search.

Both filters apply before the number shown. With **Show nearest** at 10 and both boxes ticked, the list shows the ten nearest rares sold at a large-pad station in a system controlled by the pledged Power.

### Work out Control Points from merits

CP is an estimate: merits divided by the ratio for the activity. The defaults are Acquisition 4.0, Reinforcement 2.5 and Undermining 4.2.

- 500 Reinforcement merits = 200 CP (500 / 2.5).
- 400 Acquisition merits = 100 CP (400 / 4.0).
- Delivery and Unattributed merits add merits but no CP.

## Using it

Press **Powerplay** in the mode bar to open the page. From top to bottom the page shows:

- A status line: `Awaiting PowerPlay activity…` until the game reports the pledge, then `Pledged to <Power>`, `Left PowerPlay`, `Defected to <Power>` or `CMDR <name>: not a PP Pledge`.
- The current system in bold, as `<system> — <state> (<controller>)`, for example `Nervi — Exploited (Zachary Hudson)`. The text in brackets is the controlling Power, `contested` when several Powers are in the system, or `uncontested`. With no Powerplay data the state reads `no PP data`. Before a system is known the line reads `Awaiting system data…`.
- `Here: N merits` and a `CP:` line: the merits earned in that system this session. Before a system is known the line reads `Here: awaiting system data…`.
- `Session merits: N` and `Session CP: ...`: running totals for the current login. These lines are omitted when the Cycle pair would show the same figures.
- `Cycle N merits: N` and `Cycle N CP: ...`: running totals for the whole Powerplay cycle so far, across every system. When the current login has earned everything the cycle has (the first session of a cycle), only the Cycle pair is shown, with `(all this session)` after the merits. The cycle totals persist between game sessions and reset when the cycle ends (Thursday 07:00 UTC). The Cycles tab shows the same numbers per cycle.
- `Cycle N megaships: 5 (2,340 merits)`.
- The last merit event. Until one arrives the line reads `No merit events yet this session.`

The CP lines list the estimated Control Points by activity (Acquisition, Reinforcement, Undermining). Delivery and unattributed merits add merits but no CP.

The game mode and credits are on the two lines under the mode buttons. In every other mode, a line such as `Merits this session: +1,234 (+567 merits/hr)` follows them. The rate appears after about three minutes. This line is not shown on the Powerplay page, where `Session merits` shows the same figure.

Buttons on the bottom row:

| Button | Function |
|---|---|
| **Report** | Opens the Sessions window. |
| **Rares** | Opens the Rare Goods Finder. |
| **Rescan** | Re-reads the current journal from scratch to recover merits missed after an EDMC restart. |

## The overlay card

**Settings → WFMT → Overlays → Powerplay** controls a small card on the game screen showing Powerplay standing in the current system. The card is off until the **Enable the Powerplay card** checkbox is ticked. In a system with no Powerplay data the card shows **No Powerplay Detected in system**.

| Row | Content |
|---|---|
| Heading | The system, with the commander's rank beside it. |
| **Your Power**, **Total merits**, `Cycle N merits` | The same figures as the Powerplay page. If the commander is not pledged, the card states so and omits the figures. |
| **System** | The system's state. |
| **Held by** | The Power that holds the system. |
| **Merits here count as** | The activity merits earned in this system would be filed as: Acquisition, Reinforcement or Undermining. The attribution is inferred from the state and the holder, as on the page. |
| Merit rows | One row per type of merit earned in this system this session, with the merits and, except for Delivery and Unattributed, the estimated Control Points (from the ratios on the Sessions window's Settings tab). |

**Look-ahead.** The checkbox **Look up the system I am jumping to (asks Spansh)** is off until ticked. See [What goes on the internet](internet-and-privacy.md).

- When the journal reports that a jump has started, the card shows the destination, with `jumping` beside its name.
- The destination view shows the state, the holder and what merits there would count as (**Merits there count as**).
- The control progress (`Stronghold · 66%`) is shown while the figure is under ten minutes old. An older figure shows the state alone.
- While Spansh answers, the card shows `Looking up Powerplay…`. If Spansh has no Powerplay data for the system the card shows `No Powerplay Detected in system`. If Spansh cannot be reached the card shows `Powerplay lookup unavailable`.
- A system arrived in recently is remembered from the journal, so a loop route asks Spansh about each Powerplay system only on its first lap.
- When the jump ends, the card shows the system arrived in, from the journal.
- With the look-ahead off, the card shows only the current system.

**Test Card** on the same tab draws a sample card, including while the card is switched off.

Placement is set on **Overlay Placement** ("Powerplay (your standing in this system)"). The default position is the top right.

## The Sessions window

Press **Report** to open the window. It has six tabs plus the Settings tab.

| Tab | Content |
|---|---|
| **Current session** | The current login. **By System** lists the earnings per system (columns **System**, **Merits**, **Est. CP**, **Activity breakdown**; the current system is marked and stays first). **By Activity (session total)** has the columns **Activity**, **Merits**, **Merits/CP**, **Est. CP** and **CP/hr**. **Current PowerPlay Context** shows what WFMT uses to attribute merits: the system, its state, its controller and the rival Powers. A heading above shows the commander, Power, start time and duration. |
| **Systems** | One tab per system for the cycle, with the system's standing and the merits earned there. |
| **Cycles** | One row per Powerplay cycle, newest first: **Cycle**, **Period (UTC)**, **Power** pledged to, **Systems** worked, **Merits**, **Est. CP** and **Merits by activity**. |
| **Daily** | **Day**, **Date (UTC, from 07:00)**, **Merits** and **Est. CP** for each day of a cycle, with a total. |
| **Megaships** | The megaships whose datalink was scanned: **Cycle**, **Megaship**, **System**, **Scanned (UTC)** and **Merits**. |
| **History** | Every past session of the commander being played (**Started**, **Commander**, **Power**, **Duration**, **Merits**, **Est. CP**), with the running total under **All Sessions**. Other commanders' sessions are kept but not shown. Each commander keeps the newest 200 sessions. |
| **Settings** | See [Settings](#settings). |

A help button in the window header repeats the notes for each tab. The window stores its size and position.

### Cycles

A Powerplay cycle runs from Thursday 07:00 UTC to the next Thursday 07:00 UTC and is numbered. Cycle 101 began on 2026-10-01 at 07:00 UTC. Each day of a cycle also runs from 07:00 to 07:00 UTC; day 1 is the Thursday.

The Systems and Daily tabs have a **CYCLE** drop-down for selecting an earlier cycle. The Cycles tab lists all cycles.

### Megaships

Scanning the datalink of a megaship is a Powerplay activity (*Scan datalinks at Megaships*). WFMT records the megaships scanned and counts them per cycle.

- The **Megaships** tab has one row per megaship: name, system, scan time and the merits the scan earned. The live cycle is listed first.
- The main panel shows a line under the cycle tally, for example `Cycle 103 megaships: 5 (2,340 merits)`.

Rules:

- **Identification.** The scan event does not name the ship. WFMT takes the name from the megaship at which the commander dropped out of supercruise just before the scan (the journal records it on the drop). The name must be a megaship: either one the FSS listed in that system, or a name containing the word "class" (for example "Aquarius-class Tanker"). A scan at a station, a settlement or an ordinary ship is not counted.
- **One scan per megaship per system per cycle.** Scanning the same megaship again in the same cycle changes nothing.
- **Merits** are those of the `PowerplayMerits` event that follows the scan within 6 seconds. The value can be blank, for example when the commander is not pledged or the game reported none. The scan is counted either way.
- **A scan without the drop.** If the megaship is approached another way (for example from a different supercruise destination), the journal does not name it and the scan is not counted. Drop out of supercruise at the megaship before scanning.
- **Earlier cycles.** On first start, WFMT reads the journals back as far as the scan depth on the Sessions window's Settings tab (4 cycles by default) and fills in earlier cycles. Each commander has a separate list.

### The buttons at the top

| Button | Function |
|---|---|
| **Refresh** | Redraws the tab being shown with the latest merit counts. |
| **Copy Progress** | Copies one line per system visited this session to the clipboard. The format is set on the Settings tab; the default is `[system](link) - N merits (~N CP) - state`, with a link to the system on Inara. |
| **Reset Current System** | Zeroes the merits earned in the current system during this session and subtracts them from the session totals. It asks for confirmation and cannot be undone. With no current system it reports that there is none. |
| **Reset Session** | Zeroes this session's merit totals (every system and activity) without ending the session. It asks for confirmation and cannot be undone. |

Both resets change the session only. The cycle totals on the panel and on the Systems, Cycles and Daily tabs come from the journal and are not affected. **Rescan** rebuilds a session from the journal.

### The Systems tab

A line above the tabs names the commander and Power and the number of tabs (`N tab(s): last 6 systems plus N/5 pinned`). A second line totals the cycle: merits, estimated CP and the number of systems worked. Each system has one tab with two tables, **STANDING** and **WHAT YOU DID**.

- **STANDING** compares a baseline with the latest reading. The baseline is the system's last reading before the cycle began, or the first reading of the cycle. The table shows state, controlling Power, control progress, reinforcement and undermining, and the change. The columns are **Standing**, **Baseline**, **Latest** and **Change**. With no reading yet, the table reads `No Powerplay reading for this system yet - jump in or log in there.`
  - The figures are whole-system figures from the journal, covering the work of all players. They update only on a jump into the system or a login there.
- **WHAT YOU DID** shows the commander's own merits in the system by activity (columns **What you did**, **Merits**, **Events**, **Est. CP**).

**Which systems get a tab.** The last 6 systems visited, plus up to 5 pinned systems.

- **☆ Pin** on a tab keeps it. The button then reads **★ Unpin**. Pinned tabs remain in every cycle, even with no data. At the limit of 5 pins, WFMT displays `You can pin up to 5 systems. Unpin one first.`
- A name typed in **SHOW A SYSTEM** (suggestions appear while typing) followed by **Add system** pins the system and restores a closed tab.
- **× Close tab** hides a system.
- Pins and hidden tabs are stored per commander.

## Catching up from your journals

The first time WFMT sees a commander, it reads that commander's journals to fill in the most recent cycles (4 by default; **Cycles to scan** on the Sessions window's Settings tab, 1 to 12). After that it reads only the activity that occurred while EDMC was closed.

WFMT determines the current cycle, which cycles are missing from the commander's history and how many days back to read. It does nothing when there is nothing new. The **Cycles** tab shows the result of the scan.

Journals that have been deleted cannot be read. A commander's own totals are never replaced by smaller ones.

## What the game does and doesn't tell us, and how to work around it

WFMT knows only what Elite Dangerous writes to its journal files, plus what Spansh reports (for the Rare Goods Power column). Merit totals come directly from the journal and are exact. See [How WFMT knows what it knows](README.md#how-wfmt-knows-what-it-knows).

| Item | What the game provides | Result in WFMT |
|---|---|---|
| Activity for each merit | The journal does not state it. WFMT infers the activity from the state of the current system: Acquisition when the system is uncontrolled, Reinforcement when controlled by the commander's Power, Undermining when controlled by a rival Power. An unusual situation can be misattributed. This applies to the per-system and daily figures as well. | Merit totals are exact. The split by activity is inferred. |
| Control Points | The game reports merits only. | CP is estimated with ratios editable on the Sessions window's Settings tab. |
| Name of a scanned megaship | The scan event does not name it. | WFMT uses the megaship at which the commander dropped out of supercruise just before the scan ([Megaships](#megaships)). |
| Deliveries | The game writes a `PowerplayDeliver` event (what and how many) just before the merits a hand-in earns. It does not state whether the hand-in counted as Acquisition, Reinforcement or Undermining. | WFMT labels the merit events following a hand-in *Delivery*: the first one within 10 minutes, and any within 10 seconds of the last one labeled. Only merits are counted, not CP. Unattributed merits are handled the same way. A merit from other activity inside that window can be mislabeled. |
| Live standing for any system | Whole-system figures are written only on a jump into or a login at the system. | The figures are as current as the last visit. |
| Cycles before WFMT | Available only as far back as the journal files still exist and the scan depth allows (1 to 12 cycles, 4 by default). | Older cycles are absent. The depth is set on the Sessions window's Settings tab. |
| New rare goods | The rare goods list is a snapshot (142 rare goods). | A new rare requires a WFMT update. The Power column also requires Spansh and shows "—" when it cannot be checked. |

Further detail: [Powerplay specification](../POWERPLAY_TECH_SPEC.md).

## Rare Goods Finder

Press **Rares** to list the rare commodities closest to the current position. Each row shows:

- The origin system and its **Distance** in light years from the current system.
- The station and its **Arrival** distance from the arrival star in light seconds (approximate).
- The landing-pad size.
- The **Legality** (see below).
- The Power that currently controls the origin system.

**Procedure**

1. Press **Rares**. The list requires the current position. Until the first jump or login after EDMC starts, the list shows `(waiting for a system jump or login; or press Use last known location)`. If the game is closed, press **Use last known location** to take the commander's last position from the journals.
2. Set the number of rows with **Show nearest** (type a number and press Enter or **Apply**; the default is 10, the maximum is 141, the size of the list).
3. Optionally narrow the list with **Large pads only** and **Only my Power**. Both apply before the number shown.
4. Click a column heading to sort by it (numbers sort as numbers; a second click reverses). Select a row to see where that rare is illegal.
5. Press **Copy system** to place the selected rare's origin system on the clipboard, then paste it into the galaxy map search. With no row selected, the window asks for a selection.

The table columns are **Rare Good**, **Origin System**, **Distance**, **Station**, **Arrival**, **Pad**, **Legality** and **Controlling Power**. The window subtitle names the current system (and the Power when **Only my Power** is on). A help button explains the columns.

| Control | Function |
|---|---|
| **Rares** (Powerplay panel) | Opens the window. |
| **Show nearest** and **Apply** | Number of rows shown. The value is stored. |
| **Large pads only** | Keeps the rares sold at large-pad stations (20 of the 142). The setting is stored. |
| **Only my Power** (shown as **Only my Power (Your Power)**) | Keeps the rares whose origin system is controlled by the pledged Power. The box is disabled and labeled `(not pledged or not known yet)` until WFMT knows the Power (the journal writes it at login when pledged). To find the matches, WFMT asks Spansh which Power controls each origin system, nearest first and ten at a time, until it has enough (at most all 142 systems, once per session). The setting is stored. |
| **Copy system** | Places the selected row's origin system on the clipboard. |
| **Use last known location** | Takes the commander's last position from the journals, for when the game is closed or no jump or login has been seen. |
| **Refresh** | Rebuilds the list from the current location. |
| Column heading | Sorts by the column. |
| Double-click a row | Opens the commodity on Inara. |

In the Power column, "…" indicates that the lookup is in progress, and "—" indicates an unclaimed system or a failed lookup.

**Legality**

- *Legal* means the table lists no place where the rare is illegal (129 of the 142).
- For the 13 restricted rares, the column shows *Illegal here* or *Legal here* for the current system.
  - The decision uses the allegiance and government of the current system from the journal at a jump or login.
  - The column shows *Restricted* until WFMT knows them.
  - The column does not evaluate the system being travelled to.
- The legality table is community data and has not been checked in the game. Check the station's Prohibited list on the system map before carrying a restricted rare.

To fill the Power column, WFMT asks Spansh which Power controls each rare's origin system. Answers are kept until EDMC restarts. A failed lookup is also kept, and is not retried until then. See [what goes on the internet](internet-and-privacy.md).

## Settings

The Powerplay settings are on the **Settings** tab of the **Powerplay Sessions** window (press **Report** on the Powerplay panel). The Settings → WFMT → Powerplay tab only points to this location. A box saves when Enter is pressed or the box loses focus.

| Setting | Default | Description |
|---|---|---|
| Section **Control Points: merits per 1 CP** (Acquisition, Reinforcement, Undermining) | 4.0, 2.5, 4.2 | Merits required for 1 Control Point per activity. The defaults are community estimates. A ratio must be above 0; any other value leaves the saved ratio unchanged. |
| **Copy Progress** format | `[system](link) - N merits (~N CP) - state` | Format of each line copied by **Copy Progress**. Placeholders: `{system}`, `{system_url}`, `{merits}`, `{cp}`, `{state}`. **Reset to default** restores the standard format. A blank format is the default. |
| **Cycles to scan** | 4 | Number of cycles back (current cycle included, 1 to 12) that the start-up scan covers for a commander not seen before. |
