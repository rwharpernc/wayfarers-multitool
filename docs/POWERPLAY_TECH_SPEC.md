# Powerplay technical specification

The standing reference for Powerplay mode: how merits are attributed to an activity, how Control Points
are estimated, how sessions work, and how the Rare Goods Finder fits in. For how to use it, see the
[README](guide/powerplay.md). For how the code is organized in general, see
[TECHNICAL.md](TECHNICAL.md).

- **Author:** R.W. Harper (CMDR Mactavious)
- **Status:** work in progress. Feedback, bug reports and suggestions are welcome: [open an issue](https://github.com/rwharpernc/wayfarers-multitool/issues).

**Design principle.**

- Like all of WFMT, this is journal-first: a third-party tool only knows what the game writes to its journal files, and not everything is logged.
- Gaps are filled from Frontier's own data or from community services where those exist, and otherwise worked around.
- Each gap and its workaround is written down.
- See [the design principle in TECHNICAL.md](TECHNICAL.md).

## 1. Goals

- Show the merits (and estimated Control Points) you earn for your pledged Power, live, per session and
  per system.
- Keep a history of sessions and make one easy to copy into Discord or a forum post. Built: plain **Copy Progress** (`powerplay_clipboard.py`, which also builds the per-system rows), and **Copy for Discord** and **Post to Discord** (`powerplay_discord.py`, `discord_share.py`; see [DISCORD_SHARING_RESEARCH.md](DISCORD_SHARING_RESEARCH.md)).
- Track each commander's activity **per system, per numbered Powerplay cycle and per day**, with each system's
  standing and how it moved, rebuilt from the journals as far back as needed (section 11).
- Credit income and the game mode (Open / Solo / Private Group) are **not** part of Powerplay. They are
  shown on the always-visible lines under the mode buttons (`session_credits.py`, `game_mode.py`).
  The "Merits this session" line that follows them (`session_merits.py`) is hidden while the Powerplay page is up (`line_visible`), because the page's own Session merits line shows the same figure.
- Offer a Rare Goods Finder for Powerplay hauling.

## 2. Non-goals

- **No exact Control Points.** The journal never reports them (see §4).
- **No guessing for hand-ins.** Deliveries aren't turned into Control Points (see §3.3).
- **No network access** except the Rare Goods Finder's Power lookup (see §7).

## 3. How an activity is decided

### 3.1 The problem
The journal's `PowerplayMerits` event reports the merits you gained and your new total, after every game
bonus and penalty. It does **not** say which activity earned them. WFMT infers it from **where you are**.

### 3.2 The inference
`FSDJump`, `Location` and `Docked` report the current system's **PowerplayState** and the **Power(s)**
involved whenever the system is Powerplay-relevant. Compared with the Power you're pledged to, that tells
WFMT what kind of activity merits earned there are most likely to be. `classify_current_activity` applies
these rules in order:

1. **A hand-in just happened:** *Delivery/Donation* (see §3.3).
2. **Not pledged:** *Unattributed*.
3. **The system context is stale** (you've moved on from the system it was captured in): *Unattributed*.
   WFMT prefers to say it doesn't know over using another system's data.
4. **The system is controlled** (state Exploited, Fortified, Stronghold, Controlled or Home system):
   - controlled by **your** Power → **Reinforcement**;
   - controlled by **another** Power → **Undermining**;
   - controlled but no controller reported → **Acquisition** if your Power is listed as active there,
     otherwise *Unattributed*.
5. **Any other state** (Unoccupied, Contested, Turmoil and so on, where nobody holds it yet) →
   **Acquisition**.
6. **No state at all:** *Unattributed*.

### 3.3 Deliveries
Powerplay 2.0 writes `PowerplayDeliver` (`Power`, `Type`, `Count`) for every commodity or data hand-in,
just before the `PowerplayMerits` it earns (checked against a real journal: usually one or two merit
events within a second or two, occasionally minutes later). It doesn't name the target (Acquisition,
Reinforcement or Undermining).

So WFMT marks as *Delivery*:

- the **first merit event within 10 minutes** of a `PowerplayDeliver`, and
- any merit event within 10 seconds of the last one it marked.

Delivery merits are counted in merits only, never Control Points. The same goes for *Unattributed*.

The older signals (`SearchAndRescue` with a Power commodity, `DeliverPowerMicroResources`) are used only
while no `PowerplayDeliver` has been seen: in current journals they arrive after the merits, so they
would claim the wrong event. The windows are `DELIVERY_FIRST_MERIT_S` and `DELIVERY_FOLLOW_ON_S` in
`powerplay.py`.

## 4. Control Points

Control Points depend on the activity, and Frontier hasn't documented the conversion. WFMT therefore uses
**merits-per-Control-Point ratios that you can edit** in Settings, not constants:

| Activity | Default merits per CP |
|---|---|
| Acquisition | 4.0 |
| Reinforcement | 2.5 |
| Undermining | 4.2 |

These are community estimates (Undermining is the least certain), and Frontier retunes Powerplay between
updates, so correct them if your in-game totals don't line up. CP is **not stored**: it is worked out from
the stored merits and the current ratios when displayed, so fixing a ratio corrects past sessions too.

## 5. Pledge status

The journal only says when you **are** pledged: a `Powerplay` event is written at the first login of a
game launch. There's no "not pledged" event, so WFMT starts at *unknown* and, if no `Powerplay` event has
arrived by the next `Location`, concludes *not pledged*. `PowerplayJoin`, `PowerplayLeave` and
`PowerplayDefect` update it as they happen.

If WFMT starts mid-session or after a relog, no new `Powerplay` event is coming, so it **reads the journal
file backwards** to recover the pledge from earlier in the same game launch, the same approach Auto-Honk
uses for the binds file.

## 6. Sessions

A session covers one **game login**, tied to the journal file it started in. This means:
- A logout to the menu and back, or restarting EDMC mid-game, **continues the same session** instead of
  splitting it (same file, no replay).
- A "last merit" timestamp acts as a high-water mark, so a **Rescan** can tell a gain that's already
  counted from one missed while EDMC was closed.

Each session stores raw merits and event counts per activity, the same broken out **per system**, the
Power, and its **commander**.

- History is kept in `sessions.json` in the plugin folder (one list for every commander, because each
  record names its own), and is protected from updates.
- It is **capped at 200 sessions per commander** (`store.trim`) so it can't grow forever.
- A session is never shared: starting one for a different commander ends the previous one (even in the
  same journal file).
- The **Sessions** window's History tab and its running total show only the active commander's sessions
  (`store.sessions_of`). Sessions with no recorded commander can't be given to anyone and are hidden
  (kept in the file).
- **Copy** puts the current session on the clipboard using a format you can edit in Settings.

## 7. Rare Goods Finder

A window listing the rare commodities closest to your current system.

- **The list is bundled** (`rare_goods.json`, 141 rare goods): each has its origin system and station,
  landing-pad size, cost, legality restrictions, Powerplay eligibility, the station's distance from its arrival star (`distanceToStarLs`, light
  seconds, approximate), system coordinates, an Inara id and a Spansh system id. Rare goods never move, so none of this is fetched at runtime. The coordinates and ids
  were looked up once when the list was compiled.
- **Nearest** is computed locally from your `StarPos`: straight-line distance in light years, nearest
  first, up to the number you choose (1 to 141, remembered).
- **Controlling Power** is the one live lookup: Spansh's public system endpoint, for each origin system,
  because control changes weekly. Results are cached for the session, failures included, at most 5 at a
  time. A "—" means unclaimed or unreachable. See
  [TECHNICAL.md](TECHNICAL.md#keeping-api-traffic-low).
- **Filters.** *Large pads only* keeps the rares whose station has a large pad (20 of the 141). *Only my Power* keeps those whose origin system
  the commander's pledged Power controls: the window asks Spansh (`powerplay_control_lookup`) about `POWER_BATCH` (10) origin systems at a time,
  nearest first, until it has as many matches as the number to show or has gone through the list, and caches each answer for the session. The
  filter is grayed out until the Power is known. Both filters apply before the number to show, and the choices are remembered.
- **Position.** The list needs the commander's `StarPos`. *Use last known location* takes it, with the system's allegiance and government,
  from the commander's newest journals (`current_system.last_place`) for when the game is closed.
- Double-click a row to open the commodity on Inara, using the stored id. **Copy system** puts the selected row's origin system on the clipboard.
- **Legality** is worked out locally from the table's `illegalInSuperpowers`, `illegalInGovs` and
  `illegalInSuperpowerGovs` (`rare_goods.legality_text`).
  - Any one listed restriction (a superpower, a government type, or a superpower with a government type)
    makes the rare illegal in a system.
  - The current system's allegiance and government come from the `SystemAllegiance` and
    `SystemGovernment` fields of the latest event that carries `StarPos` (`powerplay.py` keeps them),
    compared ignoring case and spaces.
  - With too little to decide, the column says *Restricted*.
  - The data is curated by hand and is on the data verification list (V-0357).

## 8. Settings

**File → Settings → WFMT → Powerplay** (keys start `wfmt_powerplay_`): the three merits-per-CP ratios,
the clipboard format, and how many cycles the start-up journal scan covers (`wfmt_powerplay_backfill_cycles`,
default 4, 1-12). Sessions, cycles and history need no setting. The overlay card's two ticks are on **Settings → Overlays → Powerplay**
(`wfmt_powerplay_overlay` and `wfmt_powerplay_overlay_lookahead`, both off; section 12).

## 9. Testing

The Rare Goods lookup has unit tests (`tests/test_rare_goods.py`).

- The per-system ledger and the journal scan are covered by `tests/test_powerplay_ledger.py` and
  `tests/test_powerplay_backfill.py` (section 11.5), which also holds the delivery-classification tests
  (`DeliveryClassificationTests`: the `PowerplayDeliver` windows and the legacy signals).
- The merit-to-CP conversion, session handling (continuing or starting a session, the resets, saving
  and reloading) and the clipboard line are covered by `tests/test_powerplay_session.py`.
- The overlay card's contents, the jump look-ahead and the Spansh answer parsing are covered by `tests/test_powerplay_overlay.py`.
- The panel and windows are exercised by hand in EDMC.

## 10. Known gaps

- Activity is an **inference** from system state; an unusual situation can be misattributed. The merit
  totals are always right, since they come straight from the journal.
- The merits-per-CP ratios are estimates.
- Deliveries and unattributed merits don't produce Control Points.
- The Rare Goods list is a snapshot; a new rare good needs the list updated.
- A megaship scanned without dropping out of supercruise at it first is not named by the journal, so it is not counted (section 11.2f).
- No daily, weekly or per-delivery merit cap has been found, so WFMT shows none. The evidence and the open items are in [POWERPLAY_MERIT_RESEARCH.md](POWERPLAY_MERIT_RESEARCH.md).

- The Systems tab (section 11) only knows what the commander's own client has seen: a system's standing
  updates when they jump in or log in there. Cycles from before the feature was installed are rebuilt from the
  journals (section 11.2c), but only as far back as the journals still exist and the scan depth allows.

## 11. Per-system tracking (Systems tab)

The Sessions window's **Systems** tab is the Powerplay counterpart of the BGS report
([BGS_TECH_SPEC.md](BGS_TECH_SPEC.md)): per commander, per system, per cycle.

### 11.1 Cycle
Cycles are numbered: **cycle 101 began 2026-10-01 07:00 UTC** and the number counts weeks from there
(`powerplay_ledger.cycle_number`, anchored by `ANCHOR_CYCLE`/`ANCHOR_START`). The window labels them
"Cycle 101".

- A cycle is the weekly Powerplay period, **Thursday 07:00 UTC to the next**
  (`powerplay_ledger.cycle_start_for`).
- This is an assumption about Frontier's schedule; it is one constant in the module if it ever moves.
- There is no network lookup (BGS needs one for its irregular tick; this does not).
- A cycle that ends while EDMC is closed is archived on the next start.
- `MAX_ARCHIVE` (52) closed cycles are kept.

### 11.2 What is recorded
- **Standing** - from `FSDJump`, `Location` and `CarrierJump` (`Docked` doesn't repeat the fields):
  `PowerplayState`, `ControllingPower`, `Powers`, `PowerplayStateControlProgress` (0-1, shown as %),
  `PowerplayStateReinforcement`, `PowerplayStateUndermining`.
  - `before` is the baseline - the newest reading from an earlier cycle, else the first reading this
    cycle - and `now` the newest.
  - The change is `now - before`, so it reflects **everyone's** work on the system, and it is blank
    until two readings exist.
  - At a rollover each system's newest reading becomes the next baseline.
  - Readings are applied in timestamp order, so a replayed older one never overwrites a newer one.
- **What you did** - merits and event counts per activity per system, recorded from the same
  `_handle_merits` path (and **Rescan**) that fills the session, using the same activity attribution
  (section 3). CP is derived at display time from the current ratios, as in section 4, and is never stored.
  Merits timestamped before the cycle began are ignored.

The main panel's **Cycle N merits / Cycle N CP** lines read the live cycle straight from this ledger
(`PowerplayLedger.live_view().merit_totals()`, formatted by `_cycle_lines` in `powerplay.py`), using the same CP ratios as the
session lines. `_tally_lines` drops the Session pair, and marks the Cycle merits "(all this session)", when the session has earned everything the cycle has, so the panel does not show the same figures twice.
The session tallies in section 6 are untouched and remain per game login; the ledger is per **cycle**, so
they can differ (a session can straddle a cycle boundary). Reset Session / Reset Current System act on
sessions only.

### 11.2b Power and totals per cycle
The ledger notes the Power(s) the commander is pledged to (`record_power`, called wherever the session is
told: `Powerplay`, join, defect, merits, pledge recovery).

- The list is stored with the cycle when it is archived and carried into the next cycle (still pledged
  until told otherwise); a defection mid-cycle gives that cycle two Powers.
- A commander who is not pledged records none and shows "not pledged" - their standing readings are
  still kept, since system standing doesn't depend on a pledge.
- Leaving a Power doesn't erase it from the cycle it happened in.
- `CycleView.merit_totals()` and `systems_worked()` give the cycle-wide figures behind the cycle total
  line on the Systems tab and the rows of the **Cycles** tab (one row per cycle, newest first, live
  cycle first).
- Everything is per commander: each has their own ledger, Power and pins in `powerplay_state.json`.

### 11.2c Journal scan (back-fill)
`powerplay_backfill.py` rebuilds what EDMC missed from the commander's `Journal*.log` files, planned by
`PowerplayLedger.plan_scan(now, depth)` which returns a `ScanPlan`: the current cycle number and the day of it
(1-7), the `missing_cycles` (wanted cycles older than `covered_from`), the mode, and `days_back`. It runs in
`PowerplayController._switch_cmdr`, i.e. once when a commander is first seen in a session.

| Mode | When | Reads |
|---|---|---|
| **rebuild** | never scanned (`covered_from` is None), or the history doesn't reach back `depth` cycles | from the oldest wanted cycle start, into a fresh ledger that is merged in (`adopt`) |
| **incremental** | covered, and the journal was last seen more than 2 minutes ago | from `seen_to` (the newest journal timestamp the ledger is current with; every live event moves it), never earlier than the oldest wanted cycle |
| **none** | covered and seen moments ago | nothing |

`depth` is the setting `wfmt_powerplay_backfill_cycles` (default 4, 1-12). A cycle is wanted if it is one
of the last `depth`. After a rebuild `covered_from` is the oldest wanted cycle's start, so later starts are
incremental, a bigger depth rebuilds only the new range, and journals that no longer exist are not retried every start.

How it stays correct:
- **Worker thread, no shared state.** The worker only reads files and returns a list of `Op`s (snapshot, merits, power);
  the main thread applies them in time order (`apply_ops`) - so a cycle that ended during the gap is archived in
  its own place by the ledger's normal rollover. Live events that arrive during the scan are buffered and applied after it.
  The cycle is not rolled by the clock while a scan runs (`_tick_cycle`), only after.
- **No double counting.** The ledger keeps `last_merit_ts` and `last_merit_n` (how many merit events share that
  second): a replayed merit older than it is skipped, and at that second only the first `last_merit_n` replayed events are.
  Standing readings are applied in timestamp order, so repeating one is harmless.
- **Per commander.**
  - Each file is read with the commander named by its `Commander`/`LoadGame` events; a different
    commander's events are skipped, and a fresh `PowerplayTracker` starts at each `Fileheader` and
    whenever the commander changes.
  - Everything of the commander's feeds the tracker (the pledge and the system context come from events
    before the window); only events inside the window become ops.
  - After a relog to a *different* commander in one launch there is no new `Powerplay` event, so the
    pledge is learned from the first `PowerplayMerits` (it names the Power).
- **Never lose data.** For a cycle both the saved ledger and the rebuild have, the one with more merits wins.
- **On time.** The cycle rolls on the clock whenever an event arrives or the window refreshes, not only at the next
  merit; `ledger.views()` lists covered cycles with no activity as empty rows, so the history is gap-free and newest first.
- If the journal folder isn't set or readable nothing is learned and nothing is marked covered, so it is tried again next start.

The Cycles tab shows the plan or the result in one line (cycle, day of 7, days read, files, merit events). Reading
28 days of journals took about 0.3 s per commander on a 1.6 GB journal folder (files are chosen by modification
time and lines are pre-filtered before JSON parsing).

### 11.2d Daily breakdown
The ledger tallies merits per activity per **cycle day** (`daily`, keys "1" to "7"): day = whole 24-hour
periods since the cycle start + 1, so day 1 is Thursday 07:00 UTC to Friday 07:00 UTC.

- It is archived with its cycle and reset at a rollover.
- The **Daily** tab (`powerplay_systems_tab.DailyTab`, `daily_rows`) shows merits and estimated CP per
  day as whole numbers with a total; the live cycle stops at today.
- CP is derived from the current ratios (section 4), never stored, and the delivery and unattributed
  merits count in merits only, as everywhere else.

`SCHEMA` (2) marks the saved layout:

- A ledger saved before the daily tally existed (schema 1) is planned as a **rebuild** once, which fills
  the days in from the journals, then marked current.
- A cycle whose journals are gone and which was kept because its saved merits were larger has no per-day
  split; the tab says so.

### 11.2f Megaship scans
Powerplay 2.0 rewards scanning a megaship's datalink. The journal writes `DataScanned` with `Type` `$Datascan_ShipUplink;` and does not name the ship;
`megaship_scans.MegaShipTracker` (shared by the live feed and the back-fill, so both give the same answer) names it from the event before:

- `SupercruiseDestinationDrop` `Type` is the destination dropped to, here the megaship's name (cleared by `SupercruiseEntry` and by any jump or
  `Location` into another system).
- `FSSSignalDiscovered` with `SignalType` `Megaship` lists the system's megaships; a destination in that list counts. Failing that the name must contain
  the word "class" (every megaship class name does). Anything else (a station, a settlement, an ordinary ship) is not a megaship scan.
- `PowerplayMerits` within `MERIT_WINDOW_S` (6 s) of the scan is that scan's merits (`MegaShipScan.merits`); `merit_at` is the newest merit timestamp counted,
  so a replay of the same events adds nothing.

The ledger keeps `megaships` for the live cycle (`record_megaship`: one per megaship name and
`SystemAddress` per cycle, none from before the cycle, at most `MAX_MEGASHIPS` = 500) and writes it into
each archived cycle as `"megaships"`.

- A ledger saved under a `SCHEMA` below 3 is rebuilt from the journals once.
- The back-fill adds `OP_MEGASHIP` and `OP_MEGASHIP_MERITS` and reads only the journal lines it needs
  (`"$Datascan_ShipUplink;"`, `"Megaship"`, the supercruise events).
- The Megaships tab is `powerplay_megaships_tab.py`; the main panel line is `powerplay._megaship_line`.

Checked against real journals (39 uplink scans across four commanders): 37 resolved to a megaship in the right system, with the merits that followed;
the other two were ordinary NPC ships and are correctly not counted.

### 11.2e Keeping the window responsive
The Sessions window is a set of table widgets, and the controller asks it to refresh on every journal
event. So:

- `SessionWindow.refresh` only records the new data and schedules one redraw 250 ms later (many calls =
  one pass).
- The redraw updates just the selected tab and marks the others stale, to be drawn when selected
  (`Tabs.on_select`).
- Tables are filled with `DataTable.set_rows`, which skips a table whose rows haven't changed.

Before this a refresh cost 0.6 to 1.2 s on a real history, and a burst of events froze EDMC. The
**Refresh** button redraws immediately.

### 11.3 Tabs and pins
Same model as the BGS report (`powerplay_ledger.TabPrefs`, `CycleView.systems`):

- Pinned systems first (sorted, starred, always shown even with no data, in every cycle).
- Then the `RECENT_SYSTEMS` (6) most recently active others with the current system leading in the live
  cycle, minus hidden ones.
- **Close tab** hides and unpins; **Show a system** (type-ahead over every known system, free text
  allowed) pins and un-hides.

Unlike the BGS report, pins are **capped at `MAX_PINNED` (5)**: pinning a sixth, or adding one, shows a
message and changes nothing; re-adding an already pinned system always works. The cap is re-applied when
a state file is loaded.

### 11.4 Persistence
`powerplay_state.json` in the plugin folder, keyed per commander (case-insensitive match, written
atomically, other commanders' entries preserved; `powerplay_state.py`, same convention as `bgs_state.py`).
Holds `ledger` (current cycle + archive), `pinned_systems` and `hidden_systems`. It is protected from
updates (`update.py`). The controller switches ledger and pins whenever the commander changes.

### 11.5 Tests
- `tests/test_powerplay_ledger.py` covers cycle boundaries, snapshot parsing, standing changes, merit
  tallies, rollover and carried baselines, the archive cap, tab ordering, the pin cap, serialization and
  the per-commander state file.
- `tests/test_per_commander_data.py` covers the History tab's per-commander view and limit.
- `tests/test_powerplay_backfill.py` covers the replay (attribution, commanders kept apart, files and
  the window), applying ops twice, same-second merits, a gap across a cycle boundary, rebuild and
  adoption, the scan plan in every mode, empty-cycle rows, the per-day tally (boundaries, archiving,
  saving, the one-time rebuild), reading real files and the delivery classification (a hand-in claiming
  the merit events that follow, a late first merit, the legacy signals ignored once `PowerplayDeliver`
  is seen).
- The widgets are exercised by hand in EDMC.

## 12. The overlay card

A small card on the game screen (`powerplay_overlay.py`; Settings → Overlays → Powerplay; one Overlay Placement slot, "Powerplay").

- **What it shows.** Your pledged Power, rank and total merits, the merits of the cycle in progress, the system's state and holder, what merits earned there now count as, and the merits and estimated Control Points earned there this session by activity (Delivery and Unattributed show merits only). It reads the same tracker, session and ledger as the panel, and the CP use the same ratios.
- **The system you are in.** From the arrival event (`FSDJump`, `CarrierJump`, `Location`). A system whose arrival named no Powerplay state shows **No Powerplay Detected in system**. Before any arrival has been seen (EDMC started mid-session) the card says nothing rather than guess.
- **The system you are jumping to.** Only with *Look up the system I am jumping to* ticked. A `StartJump` with `JumpType` `Hyperspace` names the destination and its system address; the card asks Spansh's system API (`powerplay_system_lookup.py`, through `spansh_courtesy`) for its state, holder, Powers and control progress, and shows `Looking up Powerplay…`, the standing, **No Powerplay Detected in system** (Spansh has no state for it) or `Powerplay lookup unavailable`. Any other end to the jump (an arrival, `SupercruiseEntry`, `SupercruiseExit`, `Interdicted`, `Died`, a load or shutdown) puts the card back on the system you are in, and a jump that never ends gives up after two minutes.
- **Keeping the calls down.** An answer is kept for an hour (a failure for two minutes), a request already on its way is not repeated, and an arrival event that carries a Powerplay state is stored in the same cache, so a loop route asks only about systems it has not arrived in. An arrival that names no state stores nothing, because a missing field does not prove the system has none.
- **Stale progress.** The control percentage moves as players earn merits, so a cached standing gives it out only for ten minutes (`PROGRESS_FRESH_S`); after that the card shows the state and holder alone. State, holder and Powers change at the weekly cycle, not within the hour.
- **Tests.** `tests/test_powerplay_overlay.py` (the card in each situation, the controller's `overlay_info`, the jump handling, the Spansh parsing, the cache and its expiry).
