# Powerplay technical specification

This document specifies Powerplay mode: how merits are attributed to an activity, how Control Points are estimated, how sessions and cycles work, and how the Rare Goods Finder is built. Usage is described in the [Powerplay guide](guide/powerplay.md). The general code organization is described in [TECHNICAL.md](TECHNICAL.md).

- **Author:** R.W. Harper (CMDR Mactavious)
- **Status:** work in progress. Feedback and bug reports: [open an issue](https://github.com/rwharpernc/wayfarers-multitool/issues).

WFMT is journal-first: it uses the information the game writes to its journal files and fills gaps from Frontier data or community services where they exist. Each gap and its workaround is documented. See [the design principle in TECHNICAL.md](TECHNICAL.md).

## 1. Scope

- Show the merits and estimated Control Points earned for the pledged Power, live, per session and per system.
- Keep a history of sessions. **Copy Progress** (`powerplay_clipboard.py`, which also builds the per-system rows), **Copy for Discord** and **Post to Discord** (`powerplay_discord.py`, `discord_share.py`; see [DISCORD_SHARING_RESEARCH.md](DISCORD_SHARING_RESEARCH.md)) export a session.
- Track each commander's activity per system, per numbered Powerplay cycle and per day, with each system's standing and its change, rebuilt from the journals as far back as needed (section 10).
- Credit income and the game mode (Open, Solo, Private Group) are not part of Powerplay. They are shown on the lines under the mode buttons (`session_credits.py`, `game_mode.py`). The "Merits this session" line that follows them (`session_merits.py`) is hidden while the Powerplay page is shown (`line_visible`), because the Session merits line of the page shows the same figure.
- Provide a Rare Goods Finder for Powerplay hauling.

### 1.1 Not included

- **Exact Control Points.** The journal does not report them (section 4).
- **Control Points for hand-ins.** Deliveries are not converted to Control Points (section 3.3).
- **Network access,** except the Power lookup of the Rare Goods Finder (section 7) and, only when its tick is on, the look-ahead lookup of the overlay card (section 11).

## 2. Activity attribution

### 2.1 Problem

The `PowerplayMerits` journal event reports the merits gained and the new total, after all game bonuses and penalties. It does not state which activity earned them. WFMT infers the activity from the location of the commander.

### 2.2 Inference

`FSDJump`, `Location` and `Docked` report the `PowerplayState` and the Power(s) involved whenever the system is Powerplay-relevant. Compared with the pledged Power, this indicates the most likely activity. `classify_current_activity` applies these rules in order:

1. A hand-in just happened: Delivery/Donation (section 2.3).
2. Not pledged: Unattributed.
3. The system context is stale (the commander has left the system in which it was captured): Unattributed. Data of another system is not used.
4. The system is controlled (state Exploited, Fortified, Stronghold, Controlled or Home system):
   - controlled by the pledged Power: Reinforcement;
   - controlled by another Power: Undermining;
   - controlled with no controller reported: Acquisition if the pledged Power is listed as active there, otherwise Unattributed.
5. Any other state (Unoccupied, Contested, Turmoil and similar, where no Power holds the system): Acquisition.
6. No state: Unattributed.

### 2.3 Deliveries

Powerplay 2.0 writes `PowerplayDeliver` (`Power`, `Type`, `Count`) for every commodity or data hand-in, immediately before the `PowerplayMerits` event it earns. In a real journal, usually one or two merit events followed within a second or two, occasionally minutes later. The event does not name the target (Acquisition, Reinforcement or Undermining).

WFMT marks as Delivery:

- the first merit event within 10 minutes of a `PowerplayDeliver` (`DELIVERY_FIRST_MERIT_S` = 600), and
- any merit event within 10 seconds of the last one marked (`DELIVERY_FOLLOW_ON_S` = 10).

Delivery merits are counted in merits only, never as Control Points. The same applies to Unattributed merits.

The older signals (`SearchAndRescue` with a Power commodity, `DeliverPowerMicroResources`) are used only while no `PowerplayDeliver` has been seen. In current journals they arrive after the merits and would claim the wrong event.

## 3. Control Points

Control Points depend on the activity and the conversion is not documented by Frontier. WFMT uses editable merits-per-Control-Point ratios (Settings tab of the Sessions window) instead of constants:

| Activity | Default merits per CP |
|---|---|
| Acquisition | 4.0 |
| Reinforcement | 2.5 |
| Undermining | 4.2 |

The defaults are community estimates (`formulas.DEFAULT_RATIOS`). CP is not stored. It is computed from the stored merits and the current ratios when displayed, so a change of a ratio also changes past sessions.

## 4. Pledge status

The journal states only that the commander is pledged: a `Powerplay` event is written at the first login of a game launch. There is no "not pledged" event. WFMT starts at unknown and concludes "not pledged" if no `Powerplay` event has arrived by the next `Location`. `PowerplayJoin`, `PowerplayLeave` and `PowerplayDefect` update the status when they occur.

If WFMT starts mid-session or after a relog, no new `Powerplay` event arrives. WFMT then reads the journal file backwards to recover the pledge from earlier in the same game launch (the method Auto-Honk uses for the binds file).

## 5. Sessions

A session covers one game login and is tied to the journal file in which it started.

- A logout to the menu and back, or restarting EDMC mid-game, continues the same session (same file, no replay).
- A "last merit" timestamp acts as a high-water mark, so **Rescan** can distinguish a gain already counted from one missed while EDMC was closed.

A session stores raw merits and event counts per activity, the same figures per system, the Power, and its commander.

- History is kept in `sessions.json` in the plugin folder: one list for every commander, because each record names its commander. The file is protected from updates.
- History is capped at 200 sessions per commander (`store.MAX_HISTORY`, applied by `store.trim`).
- A session is never shared. Starting a session for a different commander ends the previous one, even in the same journal file.
- The History tab of the Sessions window and its running total show only the sessions of the active commander (`store.sessions_of`). Sessions with no recorded commander cannot be assigned and are hidden (they remain in the file).
- **Copy** puts the current session on the clipboard using the format set on the Settings tab of the Sessions window.

## 6. Settings

The Settings tab of the Powerplay Sessions window (keys begin `wfmt_powerplay_`; **File → Settings → WFMT → Powerplay** refers to it) contains the three merits-per-CP ratios, the clipboard format, and the number of cycles the start-up journal scan covers (`wfmt_powerplay_backfill_cycles`, default 4, range 1 to 12). The tab is `powerplay_settings_tab.SettingsTab`. `powerplay.py` holds the savers (`set_ratio`, `set_clipboard_template`, `set_backfill_cycles`, each validating as the Settings tab does and returning the value now held) and the listeners (`add_settings_listener`). `PowerplayController._on_window_setting` redraws the panel, because the CP figures follow the ratios.

The two ticks of the overlay card are under Settings → Overlays → Powerplay (`wfmt_powerplay_overlay` and `wfmt_powerplay_overlay_lookahead`, both off; section 11).

## 7. Rare Goods Finder

A window listing the rare commodities nearest to the current system.

- **Bundled list** (`rare_goods.json`, 142 rare goods). Each entry contains the origin system and station, landing-pad size, cost, legality restrictions, Powerplay eligibility, the distance of the station from its arrival star (`distanceToStarLs`, light seconds, approximate), system coordinates, an Inara id and a Spansh system id. Rare goods do not move, so none of this is fetched at runtime. The coordinates and ids were looked up once when the list was compiled.
- **Nearest** is computed locally from the `StarPos` of the commander: straight-line distance in light years, nearest first, up to the selected number (1 to 141, remembered).
- **Controlling Power** is the one live lookup, because control changes weekly: the public system endpoint of Spansh, for each origin system. Results are cached for the session, failures included, at most 5 at a time. A "—" means unclaimed or unreachable. See [TECHNICAL.md](TECHNICAL.md#keeping-api-traffic-low).
- **Filters.**
  - **Large pads only** keeps the rare goods whose station has a large pad (20 of the 142).
  - **Only my Power** keeps those whose origin system is controlled by the pledged Power of the commander. The window queries Spansh (`powerplay_control_lookup`) for `POWER_BATCH` (10) origin systems at a time, nearest first, until it has as many matches as the number to show or has gone through the list. Each answer is cached for the session. The filter is unavailable until the Power is known.
  - Both filters apply before the number to show. The selections are remembered.
- **Position.** The list needs the `StarPos` of the commander. **Use last known location** takes it, with the allegiance and government of the system, from the commander's newest journals (`current_system.last_place`), for use while the game is closed.
- A double-click on a row opens the commodity on Inara, using the stored id. **Copy system** puts the origin system of the selected row on the clipboard.
- **Legality** is computed locally from `illegalInSuperpowers`, `illegalInGovs` and `illegalInSuperpowerGovs` of the table (`rare_goods.legality_text`).
  - Any one listed restriction (a superpower, a government type, or a superpower with a government type) makes the rare good illegal in a system.
  - The allegiance and government of the current system come from the `SystemAllegiance` and `SystemGovernment` fields of the latest event that carries `StarPos` (`powerplay.py` stores them), compared ignoring case and spaces.
  - With insufficient information, the column shows "Restricted".
  - The data is curated by hand and is on the data verification list (V-0357).

## 8. Tests

- `tests/test_rare_goods.py`: the Rare Goods lookup.
- `tests/test_powerplay_ledger.py` and `tests/test_powerplay_backfill.py` (section 10.8): the per-system ledger and the journal scan. The latter also holds the delivery-classification tests (`DeliveryClassificationTests`: the `PowerplayDeliver` windows and the legacy signals).
- `tests/test_powerplay_session.py`: the merit-to-CP conversion, session handling (continuing or starting a session, the resets, saving and reloading) and the clipboard line.
- `tests/test_powerplay_overlay.py`: the contents of the overlay card, the jump look-ahead and the parsing of the Spansh answer.
- `tests/test_per_commander_data.py`: the per-commander view and limit of the History tab.
- The panel and windows are not covered by an automated test.

## 9. Known gaps

- The activity is an inference from the system state. An unusual situation can be misattributed. The merit totals come directly from the journal.
- The merits-per-CP ratios are estimates.
- Deliveries and unattributed merits produce no Control Points.
- The Rare Goods list is a snapshot. A new rare good requires an update of the list.
- A megaship scanned without dropping out of supercruise at it first is not named by the journal and is not counted (section 10.6).
- The merits a sale earns are recorded (section 10.9) but not explained: no source gives the current rule.
- No daily, weekly or per-delivery merit cap has been found, and WFMT shows none. The evidence is in [POWERPLAY_MERIT_RESEARCH.md](POWERPLAY_MERIT_RESEARCH.md).
- The Systems tab (section 10) knows only what the commander's own client has seen. The standing of a system updates when the commander jumps in or logs in there. Cycles from before the feature was installed are rebuilt from the journals (section 10.4) only as far back as the journals exist and the scan depth allows.

## 10. Per-system tracking (Systems tab)

The **Systems** tab of the Sessions window is the Powerplay counterpart of the BGS report ([BGS_TECH_SPEC.md](BGS_TECH_SPEC.md)): per commander, per system, per cycle.

### 10.1 Cycle

Cycles are numbered. Cycle 101 began 2026-10-01 07:00 UTC and the number counts weeks from there (`powerplay_ledger.cycle_number`, anchored by `ANCHOR_CYCLE` and `ANCHOR_START`). The window labels them "Cycle 101".

- A cycle is the weekly Powerplay period, Thursday 07:00 UTC to the next (`powerplay_ledger.cycle_start_for`). This is an assumption about the schedule of Frontier and is one constant in the module.
- There is no network lookup (BGS requires one for its irregular tick; Powerplay does not).
- A cycle that ends while EDMC is closed is archived at the next start.
- `MAX_ARCHIVE` (52) closed cycles are kept.

### 10.2 Recorded data

- **Standing,** from `FSDJump`, `Location` and `CarrierJump` (`Docked` does not repeat the fields): `PowerplayState`, `ControllingPower`, `Powers`, `PowerplayStateControlProgress` (0 to 1, shown as a percentage), `PowerplayStateReinforcement`, `PowerplayStateUndermining`.
  - `before` is the baseline (the newest reading from an earlier cycle, otherwise the first reading of this cycle) and `now` the newest reading.
  - The change is `now - before`. It reflects the work of all players on the system and is blank until two readings exist.
  - At a rollover, the newest reading of each system becomes the next baseline.
  - Readings are applied in timestamp order, so a replayed older reading never overwrites a newer one.
- **Commander activity:** merits and event counts per activity per system, recorded from the same `_handle_merits` path (and **Rescan**) that fills the session, with the same attribution (section 2). CP is derived at display time from the current ratios (section 3) and is never stored. Merits timestamped before the cycle began are ignored.

The **Cycle N merits / Cycle N CP** lines of the main panel read the live cycle from this ledger (`PowerplayLedger.live_view().merit_totals()`, formatted by `_cycle_lines` in `powerplay.py`) with the same CP ratios as the session lines. `_tally_lines` omits the Session pair, and marks the Cycle merits "(all this session)", when the session has earned everything the cycle has, so the panel does not show the same figures twice. The session tallies (section 5) are per game login and the ledger is per cycle, so they can differ (a session can span a cycle boundary). **Reset Session** and **Reset Current System** act on sessions only.

### 10.3 Power and totals per cycle

The ledger records the Power(s) the commander is pledged to (`record_power`, called wherever the session is notified: `Powerplay`, join, defect, merits, pledge recovery).

- The list is stored with the cycle when it is archived and carried into the next cycle (pledged until changed). A defection mid-cycle gives that cycle two Powers.
- A commander who is not pledged records none and is shown as "not pledged". The standing readings are still kept, because system standing does not depend on a pledge.
- Leaving a Power does not erase it from the cycle in which it happened.
- `CycleView.merit_totals()` and `systems_worked()` provide the cycle-wide figures for the cycle total line on the Systems tab and for the rows of the **Cycles** tab (one row per cycle, newest first, live cycle first).
- All data is per commander: each has a ledger, Power and pins in `powerplay_state.json`.

### 10.4 Journal scan (back-fill)

`powerplay_backfill.py` rebuilds what EDMC missed from the `Journal*.log` files of the commander. `PowerplayLedger.plan_scan(now, depth)` plans it and returns a `ScanPlan`: the current cycle number and the day of it (1 to 7), the `missing_cycles` (wanted cycles older than `covered_from`), the mode, and `days_back`. The scan runs in `PowerplayController._switch_cmdr`, once when a commander is first seen in a session.

| Mode | Condition | Reads |
|---|---|---|
| rebuild | Never scanned (`covered_from` is None), or the history does not reach back `depth` cycles | From the start of the oldest wanted cycle, into a new ledger that is merged in (`adopt`) |
| incremental | Covered, and the journal was last seen more than 2 minutes ago (`UP_TO_DATE_WINDOW`) | From `seen_to` (the newest journal timestamp the ledger is current with; every live event moves it), never earlier than the start of the oldest wanted cycle |
| none | Covered and seen moments ago | Nothing |

`depth` is the setting `wfmt_powerplay_backfill_cycles` (default 4, range 1 to 12). A cycle is wanted if it is one of the last `depth`. After a rebuild, `covered_from` is the start of the oldest wanted cycle. Later starts are therefore incremental, a larger depth rebuilds only the new range, and journals that no longer exist are not retried at every start.

Correctness measures:

- **Worker thread, no shared state.** The worker reads files and returns a list of `Op`s (snapshot, merits, power). The main thread applies them in time order (`apply_ops`), so a cycle that ended during the gap is archived in its own place by the normal rollover of the ledger. Live events arriving during the scan are buffered and applied after it. The clock does not roll the cycle while a scan runs (`_tick_cycle`), only after.
- **No double counting.** The ledger keeps `last_merit_ts` and `last_merit_n` (the number of merit events sharing that second). A replayed merit older than it is skipped, and at that second only the first `last_merit_n` replayed events are. Standing readings are applied in timestamp order, so repeating one has no effect.
- **Per commander.**
  - Each file is read with the commander named by its `Commander` and `LoadGame` events. Events of a different commander are skipped. A new `PowerplayTracker` starts at each `Fileheader` and whenever the commander changes.
  - Everything of the commander feeds the tracker (the pledge and the system context come from events before the window). Only events inside the window become ops.
  - After a relog to a different commander in one launch there is no new `Powerplay` event, so the pledge is learned from the first `PowerplayMerits` (it names the Power).
- **No data loss.** For a cycle present in both the saved ledger and the rebuild, the one with more merits is kept.
- **Timing.** The cycle rolls on the clock whenever an event arrives or the window refreshes, not only at the next merit. `ledger.views()` lists covered cycles with no activity as empty rows, so the history has no gaps and is ordered newest first.
- If the journal folder is not set or not readable, nothing is learned and nothing is marked covered, so the scan is repeated at the next start.

The Cycles tab shows the plan or the result in one line (cycle, day of 7, days read, files, merit events). Files are selected by modification time and lines are pre-filtered before JSON parsing.

### 10.5 Daily breakdown

The ledger tallies merits per activity per cycle day (`daily`, keys "1" to "7"). Day = whole 24-hour periods since the cycle start + 1, so day 1 is Thursday 07:00 UTC to Friday 07:00 UTC.

- The tally is archived with its cycle and reset at a rollover.
- The **Daily** tab (`powerplay_systems_tab.DailyTab`, `daily_rows`) shows merits and estimated CP per day as whole numbers with a total. The live cycle stops at the current day.
- CP is derived from the current ratios (section 3) and is never stored. Delivery and unattributed merits count in merits only.

`SCHEMA` (currently 3; version 2 added the daily tally, version 3 the megaship list) marks the saved layout:

- A ledger saved before the daily tally existed (schema 1) is planned as a rebuild once, which fills in the days from the journals, and is then marked current.
- A cycle whose journals are gone, and which was kept because its saved merits were larger, has no per-day split. The tab states this.

### 10.6 Megaship scans

Powerplay 2.0 rewards scanning the datalink of a megaship. The journal writes `DataScanned` with `Type` `$Datascan_ShipUplink;` and does not name the ship. `megaship_scans.MegaShipTracker` (shared by the live feed and the back-fill, so both give the same result) names it from the preceding events:

- `SupercruiseDestinationDrop` `Type` is the destination dropped to, here the name of the megaship. It is cleared by `SupercruiseEntry` and by any jump or `Location` into another system.
- `FSSSignalDiscovered` with `SignalType` `Megaship` lists the megaships of the system. A destination in that list counts. Otherwise the name must contain the word "class" (every megaship class name does). Anything else (a station, a settlement, an ordinary ship) is not a megaship scan.
- `PowerplayMerits` within `MERIT_WINDOW_S` (6 seconds) of the scan are the merits of that scan (`MegaShipScan.merits`). `merit_at` is the newest merit timestamp counted, so a replay of the same events adds nothing.

The ledger keeps `megaships` for the live cycle (`record_megaship`: one per megaship name and `SystemAddress` per cycle, none from before the cycle, at most `MAX_MEGASHIPS` = 500) and writes it into each archived cycle as `"megaships"`.

- A ledger saved under a `SCHEMA` below 3 is rebuilt from the journals once.
- The back-fill adds `OP_MEGASHIP` and `OP_MEGASHIP_MERITS` and reads only the journal lines it needs (`"$Datascan_ShipUplink;"`, `"Megaship"`, the supercruise events).
- The Megaships tab is `powerplay_megaships_tab.py`. The main panel line is `powerplay._megaship_line`.

Check against real journals (39 uplink scans across four commanders): 37 resolved to a megaship in the correct system with the merits that followed. The other two were ordinary NPC ships and were correctly not counted.

### 10.7 Window responsiveness

The Sessions window consists of table widgets, and the controller requests a refresh on every journal event.

- `SessionWindow.refresh` records the new data and schedules one redraw 250 ms later (`REFRESH_DELAY_MS`), so many calls result in one pass.
- The redraw updates only the selected tab and marks the others stale; they are drawn when selected (`Tabs.on_select`).
- Tables are filled with `DataTable.set_rows`, which skips a table whose rows have not changed.
- The **Refresh** button redraws immediately.

### 10.8 Tabs, pins, persistence and tests

Tabs and pins follow the model of the BGS report (`powerplay_ledger.TabPrefs`, `CycleView.systems`):

- Pinned systems first (sorted, starred, always shown even with no data, in every cycle).
- Then the `RECENT_SYSTEMS` (6) most recently active other systems, with the current system first in the live cycle, minus hidden ones.
- **Close tab** hides and unpins. **Show a system** (type-ahead over every known system, free text accepted) pins and un-hides.
- Unlike the BGS report, pins are capped at `MAX_PINNED` (5). Pinning a sixth shows a message and changes nothing. Re-adding an already pinned system always works. The cap is re-applied when a state file is loaded.

Persistence: `powerplay_state.json` in the plugin folder, keyed per commander (case-insensitive match, written atomically, other commanders' entries preserved; `powerplay_state.py`, the same convention as `bgs_state.py`). It holds `ledger` (current cycle and archive), `pinned_systems` and `hidden_systems`. It is protected from updates (`update.py`). The controller switches ledger and pins whenever the commander changes.

Tests:

- `tests/test_powerplay_ledger.py`: cycle boundaries, snapshot parsing, standing changes, merit tallies, rollover and carried baselines, the archive cap, tab ordering, the pin cap, serialization and the per-commander state file.
- `tests/test_powerplay_backfill.py`: the replay (attribution, commanders kept apart, files and the window), applying ops twice, same-second merits, a gap across a cycle boundary, rebuild and adoption, the scan plan in every mode, empty-cycle rows, the per-day tally (boundaries, archiving, saving, the one-time rebuild), reading real files, and the delivery classification (a hand-in claiming the merit events that follow, a late first merit, the legacy signals ignored once `PowerplayDeliver` is seen).
- The widgets are not covered by an automated test.

### 10.9 Sale-merit log

Frontier does not publish how a sale earns merits, and the players' reports conflict ([POWERPLAY_MERIT_RESEARCH.md](POWERPLAY_MERIT_RESEARCH.md)). `sale_merits.py` records the data needed to work the rule out. It estimates nothing and shows nothing in the panel.

- **Pairing.** The journal does not link a sale to its merits, so they are paired by time, as for hand-ins and megaship scans. A `MarketSell` claims the first `PowerplayMerits` within `FIRST_MERIT_S` (6) seconds after it, and further merit events within `FOLLOW_ON_S` (3) seconds of the last one claimed. The next `MarketSell`, or any other event after the window, closes the sale. A merit event that a hand-in has claimed (section 2.3) is never taken. The window comes from the owner's journals: of the sales with exactly one merit event within 30 seconds, 97% had it 0 to 4 seconds after the sale.
- **What is recorded.** Only sales made while pledged, in a system with a Powerplay state (`context_of`). A sale that paid no merits is recorded with 0, because the zero-pay sales are part of the question. Each row has the time, commander, Power, the commander's Powerplay rank (`?` when the journal gave none), the Powerplay cycle number (from the time; 101 began 2026-10-01 07:00 UTC), system, station, the system's state and holder, what merits there count as, the commodity, tons, sell price, average price paid, total sale, profit, margin in percent (empty when the cost is 0), the merits and the number of merit events, the system where the commodity was last bought (`MarketBuy`), whether it was mined (a `MiningRefined` of the same commodity earlier in the journal) and whether it was a black-market sale.
- **File.** `sale_merits.csv` in the plugin folder, one row per sale, for every commander (a column names them). It is append only. A sale is never written twice: its key is commander, time, commodity, tons and total sale, so a live record, a rescan and a restart agree. It is listed in `update.py` `_OWN_DATA_FILES` so an update leaves it alone. A file that cannot be written is logged and skipped, and never interferes with the panel.
- **Live feed.** `PowerplayController.handle_event` feeds every event except `PowerplayMerits` to the `SaleTracker`; `_handle_merits` passes the merit event with its classification. `flush` and a change of commander write the sale still waiting.
- **Older files.** A log written before the rank and cycle columns is rewritten once, through a temporary file, with the new header; the cycle is filled from each sale's time and the rank is left blank. A blank rank makes the next catch-up read every journal (`SaleLog.missing_rank`); the rank found fills the row in place, and a rank still blank after that full read is marked `?` (`settle_rank`) so it is not looked for again.
- **Catch-up.** The first time a commander is seen in a launch (`_switch_cmdr`), a worker thread reads the journals written since two days before that commander's newest logged sale (`SaleLog.latest`), or all of them when the log has none, replays each through a fresh `PowerplayTracker` (`replay_sales`) and adds the sales not yet in the file. The live feed covers the rest of the launch. It runs only when the log is on. It shows `catchup_status` ("Sale merits") while it runs, skips every journal file that holds no `MarketSell` (most do) and sleeps briefly between files and every `YIELD_EVERY` lines so EDMC's window keeps the interpreter.
- **Rescan.** **Rescan journals for sales** (Settings tab) does the same for every journal. A full run over one commander's 255 sales took about 15 seconds.
- **Setting.** `wfmt_powerplay_record_sales`, on by default. When off, nothing is written; pairing still runs.
- **Rank.** The rank is the one the Powerplay tracker holds at the sale (the `Powerplay` login event, then `PowerplayRank`). In the owner's journals 350 of 1,115 sales read rank 0; the journal itself writes `Rank: 0` in some `Powerplay` events, and whether that is the true rank or a login-time value not yet refreshed was not determined, so treat rank 0 as uncertain.
- **Limits.** Merits from another source within the window (exploration data sold at the same station, for example) are counted as the sale's. The log shows a few such rows: sales at a loss with merits. Treat rows with a negative margin, and rows with several merit events, as doubtful when analyzing.
- **Tests.** `tests/test_sale_merits.py`: the pairing (window, chaining, next sale, hand-in claim, not pledged, no state), profit and margin, bought-in, mined and station, the CSV (header, no duplicates, an unwritable path) and the replay (state, commander, hand-in, folder scan). The setting is covered by `tests/powerplay_bgs_settings_smoke.py`.

## 11. The overlay card

A card on the game screen (`powerplay_overlay.py`; Settings → Overlays → Powerplay; one Overlay Placement slot, "Powerplay").

- **Content.** The pledged Power, rank and total merits, the merits of the cycle in progress, the state and holder of the system, what merits earned there currently count as, and the merits and estimated Control Points earned there in this session by activity (Delivery and Unattributed show merits only). The card reads the same tracker, session and ledger as the panel, and the CP use the same ratios.
- **Current system.** Taken from the arrival event (`FSDJump`, `CarrierJump`, `Location`). A system whose arrival named no Powerplay state shows **No Powerplay Detected in system**. Before any arrival has been seen (EDMC started mid-session), the card shows nothing.
- **Destination system.** Only with **Look up the system I am jumping to** ticked. A `StartJump` with `JumpType` `Hyperspace` names the destination and its system address. The card queries the system API of Spansh (`powerplay_system_lookup.py`, through `spansh_courtesy`) for its state, holder, Powers and control progress, and shows `Looking up Powerplay…`, the standing, **No Powerplay Detected in system** (Spansh has no state for it) or `Powerplay lookup unavailable`. Any other end to the jump (an arrival, `SupercruiseEntry`, `SupercruiseExit`, `Interdicted`, `Died`, a load or shutdown) returns the card to the current system. A jump that never ends is abandoned after two minutes (`NEXT_JUMP_TTL_S` = 120).
- **Request limits.** An answer is kept for an hour (`TTL_S` = 3600) and a failure for two minutes (`RETRY_S` = 120). A request already in progress is not repeated. An arrival event that carries a Powerplay state is stored in the same cache, so a loop route queries only systems it has not arrived in. An arrival that names no state stores nothing, because a missing field does not show that the system has none.
- **Stale progress.** The control percentage changes as players earn merits, so a cached standing gives it only for ten minutes (`PROGRESS_FRESH_S` = 600). After that the card shows the state and holder only. State, holder and Powers change at the weekly cycle.
- **Drawing.** The overlay stacks items in the order in which their ids were first drawn. A panel redrawn at a new size or place while the text of the heading is still alive could end up above the heading and hide it. `StackedLayout` therefore draws the card under new ids (`wfmt_powerplay_g<n>_...`, within the group prefix) whenever its rectangle or placement shift changes, panel first and text last, and clears the old ids. Redraws go through `LatestOnly` (one at a time, a waiting redraw replaced by the newest) and a render lock shared with Test Card, so two redraws never overlap. The log line `Powerplay card moved or resized` records each change.
- **Tests.** `tests/test_powerplay_overlay.py`: the card in each situation, the `overlay_info` of the controller, the jump handling, the Spansh parsing, the cache and its expiry, the new-ids-when-moved rule and the one-at-a-time drawing.
