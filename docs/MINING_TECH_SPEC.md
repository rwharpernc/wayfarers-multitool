# Mining technical specification

The standing reference for Mining mode: what it tracks, the rules and numbers behind its estimates, the
files it keeps, and the outside lookups it can make. For how to use it, see the
[README](guide/mining.md). For how the code is organized in general, see
[TECHNICAL.md](TECHNICAL.md).

- **Author:** R.W. Harper (CMDR Tiber Caelvox)

**Design principle.**

- Like all of WFMT, this is journal-first: a third-party tool only knows what the game writes to its journal files, and not everything is logged.
- Gaps are filled from Frontier's own data or from community services where those exist, and otherwise worked around.
- Each gap and its workaround is written down.
- See [the design principle in TECHNICAL.md](TECHNICAL.md).

## 1. Goals

- Track **Space Mining** (any ship) and **Surface Mining** (the Rhino SRV) runs live: what you've
  refined, how fast, and what's in the hold.
- Keep the commander's **own catalog of surface hotspots**, with an estimate of the tons left in
  each, and let it be found again later in the **Surface Mining Book**.
- Help on the ground: a "where have I driven" minimap. (The arrow to the nearest saved hotspot is now the Surface Compass.)
- Offer optional lookups (nearby ring hotspots, best prices, ring reserve levels) that are off until
  switched on.

## 2. Non-goals

- **No knowledge of what a surface deposit holds.** The journal never says. Everything about deposits
  comes from what the commander records, plus the in-game scanner readout they type in.
- **No shipped hotspot database.** WFMT carries no third-party deposit or hotspot data. The only
  prospecting figures are the commander's own saved hotspots (§6).
- **No real scan coverage.** The minimap records where the Rhino has *driven*, not what was scanned
  (§7).
- **No exact tons-remaining.** It's a range (§5).

## 3. Architecture

All modules live in `plugin/`; `PANEL_PLACEMENT = "mining"`.

```
mining_panel.py          Entry point (feature-module contract). Page navigation, buttons, Settings tab,
                         and the journal and Status.json dispatch.
mining_render.py         What goes on each page (Space or Surface), redrawn on events and once a second.
mining_pages.py          Page order (kept separate to avoid a circular import).
mining_space.py          Ship-mining runs and the shared ring state.
mining_surface.py        Rhino surface-mining runs and the current body and system.
mining_rate.py           The rate now (tons per hour over the last minute) and the run average (tons over mining time), shared by both pages.
mining_targets.py        The target commodities typed in Settings: parsing, per-name percentages, problems.
mining_methods.py        Commodity -> typical mining method(s). Static, community-sourced.
mining_hotspots.py       The saved-hotspot repository and its import and export formats.
mining_deposit.py        The tons-left estimate.
mining_ground.py         Kind-of-ground classification, and "your own rates" built from saved hotspots.
mining_body_survey.py    Landable bodies seen in the current system (Scan and SAASignalsFound).
mining_ring_book.py      The Space Mining Book window.   mining_rings_data.py / mining_rings.py: its data and the commander's notes.
mining_ledger.py         The Surface Mining Book window.   mining_ledger_data.py: its data shaping (pure).
mining_coverage.py       The driven-ground record.  mining_coverage_render.py: draws the minimap (PIL).
mining_live_position.py  The live surface position from Status.json.
mining_bearing.py        Distance and bearing between two surface points.
mining_overlay.py        The optional on-screen stats HUD (hold, rates, hold full in, limpets remaining).
mining_live_window.py    The LIVE window (Surface Live with the radar and the ground controls; Space Live with the page's lines).
mining_radar_view.py     The radar picture from the Mining data, one recipe for the Live window and the card over the game.
mining_radar_overlay.py  The Mining radar card over the game (built-in overlay, Windows).   mining_map_picture.py: the Save map picture.
mining_drive_rings.py    The rings to drive round a marked mining location.   mining_rigs.py: the rigs noted with Rig placed.
mining_stops.py          Stops: deposits one Rhino parking spot reaches; the nearest-deposit and rig-gap helpers.
mining_depletion.py      When a Depleted mark comes off, and the dated bookkeeping behind it.
mining_share.py          The WFMT-SPOT1 share line for one deposit.   mining_hotspot_import_export.py: the file import and export.
mining_hotspot_settings.py The Known Surface Hotspots list on the Settings page.
mining_simulation.py     The pretend Rhino for the Live window.   mining_sources.py: where the renderers read their data from.
mining_history.py        Every mining run read from the journals, per commander.   mining_history_data.py (pure) and mining_history_window.py: the DASHBOARD.
mining_alerts.py         Core, rich-rock, limpet and hold alerts for Flight Alerts; the rock reading shared with the Space page.
mining_market.py         What the open market pays against the galactic average.   mining_missions.py: the mission-needs lines.
mining_market_research*.py, mining_what_pays*.py   Market research and What pays: the plan (pure) and the windows.
mining_body_lookup.py, mining_body_cache.py   Get body info (EDSM and Spansh) and what it remembers.
mining_session_archive.py Optional JSON archive of finished runs.
mining_journal_backfill.py Replays today's journal on a mid-session EDMC start.
mining_location.py       The commander's current system.
mining_names.py          One spelling for a commodity or mineral name.   mining_bodies_data.py: the bodies the Rhino mined on, read from the journals.
mining_*_dialog.py       The Add/Edit Hotspot form and the three lookup dialogs.
mining_spansh_client.py  The Spansh lookups (hotspots, best price). edsm_client.py: ring reserves.
```

Pure logic (`mining_hotspots`, `mining_deposit`, `mining_ground`, `mining_ledger_data`,
`mining_body_survey`, `mining_coverage`, `mining_bearing`, `mining_rate`, `mining_targets`) has no screen code and is
unit-tested.

## 4. Runs

### 4.1 Space Mining
A run is one **undock-to-dock trip**: `Undocked` starts a fresh run; `Docked` leaves the finished numbers
on screen until the next undock. This is coarser than "from the first prospector to the next jump", but
more reliable: a finer boundary would split one stop at a ring into several runs whenever you hop in
supercruise. While in supercruise mid-trip the panel shows a "paused" hint. It does not reset anything.

Events used: `ProspectedAsteroid` (content grade, composition, with duplicate-asteroid detection),
`LaunchDrone` and `BuyDrones` (limpets used, and a rough "on board" figure that can't tell an unused
timed-out limpet from one still deployed), `MiningRefined` (the actual output), `AsteroidCracked`
(core mining), `Cargo` and `Loadout` (hold and `CargoCapacity`), and `SupercruiseEntry` / `SupercruiseExit`. The hold is also read live from `Status.json` (below).

`ProspectedAsteroid` also carries `Remaining` and, for a core (motherlode) asteroid, `MotherlodeMaterial`
(seen in a real journal).

- `mining_alerts.rock_finding` reads each event into a `RockFinding` (materials richest first, grade,
  remaining, core mineral, and which of the commodities chosen in Settings are at or over their
  percentages).
- The run keeps the latest one (`last_rock`) and counts cores (`cores_found`, once per distinct rock like
  the other counts).
- The limpets aboard are exact: EDMC's `state["Cargo"]` (by name, `drones`) goes to
  `SpaceMiningRun.limpets_aboard`. The page and the HUD overlay (one function,
  `mining_render.limpets_on_board`) fall back to bought-less-launched only when it is unknown.
- A rock is counted once by one key (`mining_alerts.prospect_key`: the materials' names and proportions
  to a tenth of a percent) in the run, in Mining History and in the rock alerts. A rock with no usable
  materials is never a repeat.
- History keeps a grade it cannot read (`ungraded`) apart from Low and out of the High and Low shares.
- `mining_missions.needs` totals the active mining missions' remaining tons by commodity and applies the
  hold (`current_cargo.held()`), for the page's "Mission needs" lines. The panel redraws when the
  missions change.

The Flight Alerts card carries the transient alerts (a core or target rock for `ROCK_ALERT_S` = 30 s) and
the conditions (limpets at or under a number, the hold at or over a percentage, only within `ACTIVE_S` =
30 minutes of a mining event): see `mining_alerts.MiningWatcher` and `flight_alerts.py`.

- **Limpet alert:** applies only when the latest `Loadout` has a prospector or collector controller
  (`Modules[].Item` starting `int_dronecontrol_prospector` or `int_dronecontrol_collection`) or limpets
  have been seen aboard since it, and never while a Rhino is out (`LaunchSRV` to `DockSRV`, or `Cargo`
  for the SRV).
- **Target rock alert:** not raised when `Remaining` is under `MIN_REMAINING_PERCENT` = 25.
- **Once per composition:** a core and each target a rock hits are alerted once per composition per run,
  by the pair (rock key, `core` or the target's canonical name; reset at `Undocked`). A rock seen again
  raises nothing new, and a target added to the settings in between raises its own card.
- **Card limit:** at most `MAX_TARGET_CARDS` = 3 target cards (the richest) are raised for one rock.
- **Sound:** keyed on the alert's kind (and the rock's composition for a rock alert), not on its text.
- **Name matching:** the target commodities are compared with the rock's materials by
  `mining_names.normalize`, and `mining_methods.methods_for` normalizes its argument, so every spelling
  of a commodity finds the same entry.
- **Current ring:** a `Location` in a planetary ring sets the current ring, like a `SupercruiseExit`.

**Target commodities.** The Settings box (`wfmt_mining_target_commodity`, still one text key, with
`wfmt_mining_target_percent` as the default percentage) takes one or several names separated by commas or
semicolons, each optionally followed by its own percentage (`Painite 30, Platinum 25, Void Opals`).

- `mining_targets.parse_targets` reads it into `Target(name, percent)` items:
  - at most `MAX_TARGETS` = 8;
  - a name with no number takes the default percentage;
  - names are keyed by `mining_names.normalize`, so spellings and a name listed twice are one target;
  - an unknown name is kept.
- It also returns a list of problems for the Settings page: a percentage that is not a number from 1 to
  100 (which leaves that entry out), a duplicate, or more than the maximum.
- A box holding one plain name reads exactly as it did when the box held one.
- `RockFinding.hits` holds every target at or over its percentage, richest first, and
  `RockFinding.target` the first.
- The Last rock line names them (`target: Painite`, three names at most, then a count).
- The type-ahead in the box is attached through `mining_targets.LastItemVar`, which gives it the item
  after the last comma and writes a taken name back into only that item.
- The radar's target material and What pays take the first target (`mining_alerts.primary_target`).

**The hold.**

- `Status.json`'s `Cargo` (tons carried) arrives through EDMC's dashboard hook
  (`mining_panel.dashboard_status`, `flight_alerts.dashboard_status`) about once a second.
- `mining_alerts.status_hold` takes it only while the entry's `Flags` say the commander is in the main
  ship (bit 24) and not in an SRV (bit 26) and the journal does not say a Rhino is out. In any other
  state the live figure is forgotten and the `Cargo` events speak, because what `Cargo` counts in
  `Status.json` while in an SRV could not be checked.
- The figure is kept per commander in `SpaceMiningRepository.live_cargo` (not run-scoped, like the
  capacity) and in `MiningWatcher.live_cargo`. A `Cargo` event for the ship clears it until the next
  `Status.json` update.
- The capacity is `CargoCapacity` of the last `Loadout`.
- `mining_render.format_ship_cargo` draws `Hold: 64 of 200 t` from them (`Ship hold:` beside the SRV line
  on the Surface page, `SRV hold: 40 of 72 t`).
- The Hold nearly full alert (`MiningWatcher.held`) uses the live figure, else the event's.

### 4.2 Surface Mining
A run is one **Rhino deployment**: `LaunchSRV` with `SRVType == "mev_rhino"` starts it and the matching
`DockSRV` ends it. The Rhino reuses the ordinary `MiningRefined` event, so WFMT only routes it to the
Surface page while a Rhino is deployed. It also tracks the SRV hold (capacity 72), cargo handed to the
ship mid-run (`CargoTransfer`, so it isn't mistaken for a loss), and materials collected. Docking the
Rhino moves whatever is left in its hold to the ship.

### 4.2.1 Sales in the history

`mining_history.runs_from` attributes each `MarketSell` (`Type`/`Type_Localised`, `Count`, `TotalSale`) to
the runs that mined the commodity, at whichever station it is made.

**The unsold list**

- Every finished run appends `[run key, tons]` per refined commodity to a list of unsold mined tons
  (`unsold`, by normalized commodity name, oldest first; the run key is `file|start`,
  `mining_history.run_key`).
- The list is carried through the journals in order and saved with the runs (`unsold` in the commander's
  payload; a file without it loads as empty, and `MiningHistory._payload` drops a malformed one).

**How a sale is split**

- A sale takes `min(Count, tons waiting)` off the front of that commodity's list, run by run.
- Each run gets the tons and `TotalSale * tons so far // Count` less what earlier runs of the same sale
  already got, so the shares add up exactly.
- Tons beyond the list are ignored, so a sale never creates credit.
- The run's `sold` entry (`{commodity: [tons, credits]}`) is updated in place, also for a run saved from
  an earlier journal.

**Replay and rebuild**

- The newest journal is never saved: it is replayed on copies of the saved list and of the runs it
  touches (`_live_unsold`, `_live_patch`), so reading it again changes nothing.
- **Rebuild from journals** (`clear`) empties `unsold` with the runs and replays every journal through
  the same code.

**Limits**

- The journal does not say what a jettisoned, destroyed or transferred ton was, so those stay on the
  list until a sale of that commodity uses them up.
- Bought cargo of a commodity that is also waiting is credited to the oldest run that mined it.
- Cargo mined while EDMC was closed is only known once its journal is read.

### 4.3 Rate
One `MiningRefined` event is one ton (the hold's `Cargo` count rises by one for each in a real journal), so event counts are tons.

- **Refining now** (`mining_rate.current_rate`): the tons refined in the last `RATE_WINDOW_SECONDS` = 60, scaled to tons per hour. A run younger than the window divides by its age, never by less than
  `MIN_RATE_SPAN_SECONDS` = 10. The refined timestamps list is pruned in place to the window. It is recomputed on each refinement and on the page's timer, so the figure falls to zero within a minute of a lull instead of freezing.
- **Run average** (`mining_rate.MiningClock`, `run.clock` on both kinds of run): tons refined this run
  (the sum of `refined`) over the mining time.
  - The mining time is the sum of the gaps between consecutive mining events that are at most
    `MAX_GAP_SECONDS` = 600; longer gaps are left out.
  - The mining events are the ones the history calls mining events: `ProspectedAsteroid`,
    `MiningRefined`, `LaunchDrone`, `AsteroidCracked`; for the Rhino only `MiningRefined`.
  - The clock keeps the first and last event times and the time mined, since the timestamps list is
    pruned.
  - The average is shown once the run has `MIN_AVERAGE_SECONDS` = 60 of mining time (`none yet` with no
    events, `needs a minute of mining` before).
  - Events carry the journal's own time (`mining_rate.event_time`), so a journal replayed at start-up
    (§4.4) gives the real mining time and no rate spike.
- The panel, the HUD and the live window word them alike through `mining_render.format_rate_now`
  (`Refining now: 840 t/h`) and `format_run_average` (`Run average: 720 t/h over 41 min`).
- `format_time_to_full` (`Hold full in about 14 min`) divides the room left in the hold (capacity less
  tons, from `ship_hold` or the Rhino's fixed 72 t) by the run average, or by the rate now while there
  is no average yet. `mining_rate.minutes_to_fill` and `full_in_text` hold the arithmetic and the
  wording.
- It returns nothing when the capacity is not known or nothing is being refined, `Hold is full` once the
  room is gone, and nothing for a stowed Rhino.
- **The station's price against the average.**
  - `mining_panel` passes the journal's `Market` event to `mining_market.on_market`, which reads
    `Market.json` through `trade_market.read_market_file` (waiting out a file that is still the previous
    station's) and keeps that one market until `Undocked`.
  - `trade_market.MarketItem` carries `mean_price` (`MeanPrice`, the galactic average) and
    `demand_bracket` (`DemandBracket`).
  - A station lists a `SellPrice` for goods it does not buy, with no demand, so `mining_market.buys`
    needs a price, demand, a bracket above zero and an average.
  - A commodity is found by its localized name first (`Low Temperature Diamonds`; the game's internal
    name is the singular `lowtemperaturediamond`), then by the canonical name.
  - `mining_market.lines` words up to three lines, the most tons refined first, and
    `render_space_mining` shows them under the rate lines.
  - Nothing is fetched.
- **Mining History's limpet cost.**
  - `runs_from` also reads `BuyDrones` (`BuyPrice`, else `TotalCost` over `Count`, field names as in the
    trade ledger, checked against a real journal) into a price held in `prices["unit"]`, carried from
    journal to journal and saved as `limpet_price` in the history file.
  - It charges each `LaunchDrone` at that price: `limpet_cost` on the run, and `limpet_unpriced` for
    launches made before any price was seen.
  - `mining_history_data.net` is the run's earned less `limpet_cost`; the overview tile, the Sales block
    and the Runs column are built on it.
  - `RUNS_VERSION` 5 makes runs saved without it be read from the journals once more.
  - Not subtracted: fuel, repairs, ammunition, limpets sold back.
- **Mining History** reads a run's mining time the same way:
  - `mining_history.runs_from` adds the gaps of more than ten minutes to the run's `idle` (seconds;
    present only when there was one), and `mining_history_data.mining_hours` subtracts it from the
    first-to-last span.
  - `RUNS_VERSION` 4 makes runs saved without it be read from the journals once more.
  - Small differences from the live figure remain: the page counts from when WFMT saw an event, the
    history from the journal's time stamps, and the page waits a minute before showing an average.

### 4.4 Mid-session start
If EDMC starts while you are already out mining, WFMT replays **today's journal file** through the same
handlers so the current run is picked up. Older files are ignored: a run never outlives its undock or
deployment.

## 5. The tons-left estimate

The journal reports neither a deposit's size nor how much of it is left. The in-game mining scanner shows
two readings, **Amount** (High, Medium, Low, Depleted) and **Density** (High, Medium, Low), which the
commander enters on a hotspot. Nothing here is exact, so the answer is a **range**.

The model (`mining_deposit.reserve_range`), from measured depletion of real deposits (credited in
`THIRD-PARTY-NOTICES.md`):
- A full deposit holds a fixed number of tons **per rig position**, set by Density. A *lower* Density
  label means a *larger* reserve: roughly 125–175 t per position at High, 250–350 at Medium and 375–525
  at Low.
- The Amount label then gives the **share still left** (High about 57–100%, Medium 27–67%, Low 0–34%,
  Depleted 0).
- Range = rigs × tons per position × share left, rounded to the nearest 10 t. With no Density, the
  range spans the smallest low end to the largest high end.

At most **7 rigs** can be recorded (six can be worked at once; a seventh can be placed but not run).
When the Rhino is out, each refined ton is credited to the nearest saved hotspot within **200 m**, so a
depleted deposit reads "depleted (612 t)". Tons are counted in memory and written at most every 5
seconds. These figures are measurements and may need refitting as more deposits are mined.

## 6. Hotspots, the Surface Mining Book and "your own rates"

### 6.1 The hotspot file
`mining_hotspots.json` (in the plugin folder, never part of a release) holds **one list of hotspots per
commander** (`commander_data.py`: `{"version": 2, "commanders": {key: {"name", "data": [...]}}, "legacy":
...}`), so a hotspot, its notes, tons mined and depleted mark belong to the commander who saved it.

- `HotspotRepository.set_commander` switches the list when the active commander changes (the mining panel
  calls it on every event that names one).
- Until one is known the list is empty and anything added waits for the first commander.
- A file from before this was a single flat list; the first commander seen claims it and the rest start
  empty.
- Import and Export work on the active commander's list, which is how to copy hotspots to another
  commander.

What a hotspot holds:

- A system, body and material, plus optional notes, latitude and longitude, a folder label, rigs, a
  signal number, the Amount and Density readings, the tons mined so far, and the kind of ground (§6.3).
- Material, rigs, signal number, Amount and Density are entered by the commander on trust; only the
  mined tons are derived from the journal.
- Saving a hotspot within **100 m** of an existing one on the same body updates it instead of adding a
  duplicate.

Depletion bookkeeping lives on the hotspot too (`depleted_at`, `regrown_at`, `tons_at_regrow`,
`rechecks`; a record without them loads with defaults).

- `mining_depletion.apply` is called by `HotspotRepository.add` and `update`, so the dialogs, which build
  a hotspot without these fields, cannot lose them.
- `settle` runs when a commander's list loads and when the Surface Mining Book refreshes.
- A Depleted mark is taken off `wfmt_mining_refill_days` days after it was set (default 0 = unknown:
  never taken off, the card says how long ago it was set; up to `MAX_REGEN_DAYS`, 90; the repository's
  `refill_days` holds it).
- Mark depleted on a hotspot that refilled with no ton refined since is a recheck (first date kept, the
  mark comes off `RECHECK_DAYS` (7) after the look).
- A Depleted mark with no date is dated on first sight.

### 6.2 Import and export
WFMT exports and re-imports its own file format, with a merge or replace choice (the **I/E** button, and the buttons
in Settings).

### 6.3 The Surface Mining Book
A three-pane window: bodies (the current system's scanned landable bodies plus every saved hotspot,
anywhere), a body's hotspots grouped by location, and a detail card with a zoomable map. Filters are by
material and by rig count; the card offers Edit, Mark depleted, Copy coordinates and Delete.

**Stops.**

- `mining_stops.find_stops` groups a body's active, positioned deposits that have a rig count: greedily,
  the one with the most rigs (ties by how many others are within reach) leads, and every remaining
  deposit within the stop radius (`wfmt_mining_stop_radius_m`, 500 to 2500 in steps of 250, default 1250)
  joins it.
- `best_stops` keeps up to three whose lead has 5 or more rigs, else 4 or more. They need the body's
  radius, known only for the body the Rhino is on.
- The Book lists them, tags each deposit's row, and the map draws a dashed ring (`MapCircle`) around each
  lead.

**You are here:** `mining_ledger_data.deposit_here` finds the positioned hotspot (depleted included)
within 175 m of the live position, which the Book marks and selects when no deposit was already
selected.

**Market research.**

- `mining_market_research.plan` lists the commodities worth checking in a system, each with its reasons:
  deposits saved in that system (most first), then the commander's own rates (`OwnRates`) on the grounds
  of the system's scanned bodies (highest share first), then names typed by hand.
- Names are resolved with `trade_commodities.resolve`; unknown ones are reported, not searched.
- There is no commodity-to-planet-type table, by decision: the game publishes none and community testing
  treats planet class as a screening hint.
- `mining_spansh_client.search_system_stations` makes one `/api/stations/search` request with a distance
  of at most 0.01 ly from the system (checked live on Sol: 44 stations, each with its whole `market` and
  `market_updated_at`), keeps those in the system with a market that are not fleet carriers, and sends
  only the system name.
- `match` lists the buyers (demand and sell price above zero) per commodity, best price first.
- It shares the price finder's switch (`wfmt_mining_spansh_price_finder_enabled`).

**Fleet carriers and the demand floor in the price searches.**

- The price finder and What pays leave carriers out, as `search_system_stations` does.
- `search_best_price_stations` takes `exclude_carriers` (a result whose `type` contains "carrier" is
  skipped) and the `station_types` filter (`filters.type`, Spansh's own names), because skipping on the
  response alone would still let carrier markets fill the page ahead of real stations (see
  `_MARKET_DAYS_OLD_DEFAULT`).
- `mining_what_pays.NO_CARRIERS` bundles the two with `trade_prices.station_types(True)`; a kind of
  station that list lacks is not found.
- Pad size and a market's age inside the 30 days are not filtered.
- `min_quantity` (`filters.market[].demand`, selling) is set per search. `mining_what_pays.minimum_for`
  returns the tons of the commodity in the hold, else 1 (`current_cargo.held()`, EDMC's
  `state["Cargo"]`, matched by `trade_commodities.resolve`).
- The price finder's box starts there when selling and takes a whole number of 1 to `MAX_MINIMUM` tons
  (`parse_minimum`); What pays uses the figure for each commodity.
- Every call still goes through `spansh_courtesy.call`.

**Sharing.**

- `mining_share.encode` writes `WFMT-SPOT1:<base64url JSON>:<CRC-32 hex>`: system, body, material,
  position (5 decimals), and when present rigs, location number, Amount, Density, ground and the body's
  radius; never notes, folder, tons, dates or a commander.
- `decode` strips chat decoration, checks the prefix, the CRC and every field (text 80 characters, no
  control characters; latitude, longitude, rigs 1 to 7, Amount and Density from the game's own lists,
  radius) and raises `ShareError` with a message for the commander.
- `find_duplicate` refuses a spot within `SAME_SPOT_M` of one saved on the same body (the receiver's own
  body radius if known, else the sender's, else an assumed one).
- The Book's **Paste spot** asks before `HotspotRepository.add`.

**Your own rates.** For a scanned body, the Surface Mining Book shows what *you* have found so far on that
kind of ground: the share of your saved deposits, per material, with the sample size.

- `mining_ground.classify` turns the journal's `PlanetClass` and `Volcanism` into a ground (for example
  "Rocky body, silicate magma").
- A new hotspot is stamped with its ground when saved; one saved without a ground, or imported, counts
  while its body is in the current survey.
- These are tallies of **your recorded deposits only**, not a statement about what any body holds, and
  the section stays empty until you record something.

### 6.4 The Space Mining Book

The BOOK button opens the book for the page it is on: `mining_ring_book.py` on the Space Mining page,
`mining_ledger.py` (the Surface Mining Book above) on the Surface Mining page.

**The Space Mining Book** is a catalog of **rings**, built from the journals instead of typed in.

- `mining_history.py` reads every journal once in the background. The same pass also keeps, per ring,
  what `SAASignalsFound` says on a ring body (each mineral with its hotspot count) and what a body's
  `Scan` says about its rings (`Rings[].RingClass` and `ReserveLevel`).
- They are kept in the history's payload (`rings`, `bodies` and `scan_files` beside `runs`, `files` and
  `unsold` (see below)). A saved file that lacks them (`extras`) is read once more for them, and its runs
  are not counted twice. The newest journal is read afresh, like the runs.
- `mining_rings_data.build_rows` joins them with the runs (tons refined and the last run per ring) and
  the commander's own entries.
- The journal records only a hotspot **count** per mineral for a ring: there is no position and no
  overlap information.

**For the Surface Mining Book**, the same pass keeps the bodies the Rhino mined on
(`mining_bodies_data.py`):

- `SAASignalsFound`'s `$PlanetaryMiningLocation_Name;` count per non-ring body.
- The planet class from a landable `Scan`.
- The tons refined while a Rhino was deployed (`LaunchSRV` with `SRVType` `mev_rhino`, until `DockSRV`,
  `SRVDestroyed` or `Died`) on the body last approached (`ApproachBody`, or `Location` on a planet).
- The book lists them in a `From your journals` group (`mining_ledger_data.build_body_groups(journal=...)`)
  and adds the tons to the bodies it already lists.
- The journal has no deposit positions, so deposits stay the commander's hotspots.

The commander's notes, favorites and rings added by hand are in `mining_ring_notes.json`
(`mining_rings.py`, one record per commander, never in a release).

## 7. On the ground

### 7.1 Live position
Latitude, longitude and heading come from `Status.json` through EDMC's dashboard hook (about once a
second), and are only valid on a landable body's surface. The body radius also comes from `Status.json`,
with the radius from the body's `Scan` event as a fallback.

### 7.2 The coverage minimap
While a Rhino is deployed and a radius is known, a point is recorded as you drive (at least **250 m** from
the last one), and the map paints a **2,000 m** disc at each.

- This records where the Rhino has *driven*, because nothing in the journal or `Status.json` says a scan
  happened, so it can't claim real scan coverage.
- The map is a fixed 220 px square, 12 km across, north up, with hotspots (a pale filled dot for live, a
  hollow gray ring for depleted, so shape carries the meaning for color-blind players) and your position.
- Without a Rhino deployed it only shows below 2 km altitude.
- It uses a flat-earth projection, accurate enough at this scale.

**Marked mining locations.** The journal gives neither the position nor the size of a mining location, so
the commander marks them:

- **CTR** stores the live position as a site's center (within **100 m** of an existing center it moves
  that center).
- **BRD** stores the border on the nearest site, and the radius is the distance between the two.
- Up to 12 sites are kept per body, in the coverage file (per commander).
- The minimap draws a cross and a circle for each, and the page reports how much of the border circle
  (72 sample points) lies within 2,000 m of a recorded point.
- That figure is *driven*, not *scanned*, and the 2,000 m reach is the same community figure the map
  uses.

### 7.3 The Live window and the radar
The **LIVE** button opens one window for each page (`mining_live_window.py`): geometry is saved per page, it redraws
once a second, and the page's lines are drawn by the same code as the panel (`mining_render`, with no button bar), so
the two cannot disagree.

- **Surface Live** has the radar (`mining_radar_view.render`, drawn by `mining_coverage_render.render_radar`): the Rhino
  in the middle, north up, range rings, the driven ground (a 2,000 m disc at each recorded point), marked locations,
  saved deposits, a line to the nearest one, the stops, the drive rings and the rig markers and bands. The range steps
  through `RADAR_RANGES_M` = 50, 250, 500, 1,000 and 2,000 m (default 2,000, `wfmt_mining_live_radar_range_m`, shared
  with the card over the game).
- **Drive rings** (`mining_drive_rings.ring_radii`): the first sits one scanner reach (2,000 m) from the center, each next
  one 90% of a scanner diameter (3,600 m) further, at most 12, the last on the border; with no border they reach as far
  as the ground driven. They come from the one community figure for the reach and are a guide only.
- **Rigs** (`mining_rigs.py`): the journal never says where a rig went, so **Rig placed** (button, Ctrl+Alt+Shift+R or
  `!wf rig`) notes the Rhino's position. A second press within 5 m adds nothing; at most 40 are kept; they are not saved
  and are forgotten on launch, stow, destruction or a change of body. With the rig gap setting
  (`wfmt_mining_rig_gap_m`, 0 to 2,000 m in steps of 5, 0 = off) the radar draws a band of that radius round each rig.
- **Save map** (`mining_map_picture.py`) draws the same marks once, centered on the marked location, with a title and a
  legend, to a PNG the commander chooses. It holds no commander name or date.
- **The card over the game** (`mining_radar_overlay.py`): the same picture laid over the game as one image by the
  built-in overlay (Windows); EDMCModernOverlay cannot draw a picture. Drawn while a Rhino is deployed and the
  position and body size are known, at most once a second, with a translucent background (`wfmt_mining_radar_enabled`,
  `wfmt_mining_radar_size` 240 to 560, default 340; `wfmt_mining_radar_opacity` 30 to 100, default 70). The slot is
  Overlay Placement's `mining_radar`.
- **Shortcuts.** CTR, BRD, Rig placed, the radar range and opening the window are shortcut actions
  (`shortcut_actions.py`, `shortcuts.py`; see the [Shortcuts guide](guide/shortcuts.md)).
- **Simulation** (`mining_simulation.py`): Settings → Mining → Simulation opens Surface Live on made-up data. It builds
  its own repositories, never given a plugin folder or a commander, so none can write a file; the window has no I/E.

### 7.4 The waypoint arrow (the Surface Compass)
The arrow is part of the **Surface Compass** (`surface_compass.py`; see [TECHNICAL.md](TECHNICAL.md) and
the [Exploration guide](guide/exploration.md#compass)).

- By default it points to the **nearest saved hotspot with a position on the current body**, using
  great-circle distance and initial bearing between your live position and the hotspot
  (`mining_bearing.py`, `mining_live_position.py`).
- It can instead point at a mark the commander made or at nothing.
- It does not need the Surface Mining page to be open.

## 8. Optional lookups

All are **off until switched on** in the Mining Settings tab. See
[TECHNICAL.md](TECHNICAL.md#keeping-api-traffic-low) for how call volume is kept down.

| Lookup | Service | Trigger |
|---|---|---|
| Find Nearby Hotspots (rings with a confirmed hotspot for a commodity, nearest first) | Spansh | Button |
| Find Best Price (best-price stations for a commodity) | Spansh | Button |
| Check Ring Reserve Level | EDSM | Button; and automatically on dropping into a ring, if enabled |
| Market research (Surface Mining Book) | Spansh | Button; shares the Find Best Price switch |
| What pays (Surface Mining Book) | Spansh | Button; shares the Find Best Price switch |
| Get body info (Surface Mining Book) | EDSM, and Spansh when the system's id is known | Button; its own switch (`wfmt_mining_edsm_body_lookup_enabled`) |

The automatic ring check runs only when enabled, never while replaying the journal at start-up, and the
answer is remembered for the session for each ring. A non-Metallic ring shows a laser-mining caution.
Spansh does not publish the request shape used for its ring and station searches; it was worked out from
live calls and checked against independent callers, and `mining_spansh_client.py` is the one place to fix
if Spansh changes it.

Two details shared with [Trade mode](TRADE_TECH_SPEC.md):

- Spansh's market search is **case-sensitive and exact** ("Liquid oxygen" finds markets, "Liquid Oxygen"
  finds none), so the price finder resolves whatever is typed through `trade_commodities.resolve` to the
  game's exact name before searching.
- `search_best_price_stations` accepts `max_distance_ly=None` for "no distance limit", which Trade's
  Galaxy search uses (the Mining dialog still always passes a distance).

The page arrows on the Mining panel are the shared `panelkit.nav_arrow`.

## 9. Optional extras

- **On-screen stats panel** (overlay). It registers a plugin group (EDMCModernOverlay needs one for its background to draw; the built-in overlay uses the same prefix to place the display as one piece).
- **Archive completed runs.** Off by default. When a run that has data ends, a JSON file is written to
  `mining_sessions/` for analysis outside WFMT. Empty trips write nothing.

## 10. Settings

Under **File → Settings → WFMT → Mining** (keys start `wfmt_mining_`):

- Session totals, cargo bar, prospector hints (`wfmt_mining_display_session_totals`, `_cargo_bar`, `_prospector_hints`; on),
  the three lookups (`wfmt_mining_spansh_hotspot_finder_enabled`, `wfmt_mining_spansh_price_finder_enabled`,
  `wfmt_mining_edsm_reserve_lookup_enabled`), body lookup (`wfmt_mining_edsm_body_lookup_enabled`), the coverage minimap
  (`wfmt_mining_display_coverage_minimap`), run archiving (`wfmt_mining_archive_sessions`); the lookups, minimap and
  archiving are off.
- `wfmt_mining_stop_radius_m` (500 to 2,500 in steps of 250, default 1,250), `wfmt_mining_rig_gap_m` (0 to 2,000, 0 =
  off) and `wfmt_mining_refill_days` (0 to 90, 0 = unknown).
- The Known Surface Hotspots list (add, edit, delete, import, export) at the bottom of the tab.
- The two overlays (the HUD overlay and the radar) are on Settings → WFMT → Overlays → Mining.
- The target commodities and the default percentage (`wfmt_mining_target_commodity`,
  `wfmt_mining_target_percent`; a line under the box lists problems in what is typed).
- The mining alerts' own switches (`wfmt_flight_mining`, `wfmt_flight_limpets_low`,
  `wfmt_flight_hold_percent`) are on Settings → Overlays → Flight Alerts.
- The last page you viewed is remembered.

## 11. Files

| File | What | Notes |
|---|---|---|
| `mining_hotspots.json` | Saved hotspots (the Surface Mining Book) | One list per commander; never in a release |
| `mining_ring_notes.json` | The Space Mining Book's notes, favorites and rings added by hand | One record per commander; never in a release |
| `mining_coverage.json` | Driven-ground record per body | One map per commander (same layout and legacy rule as the hotspot file) |
| `mining_history.json` | The Mining History window's runs, built from the journals | One record per commander; never in a release |
| `mining_body_cache.json` | What the Surface Mining Book's Get body info found for each system | One record per commander; never in a release |
| `mining_sessions/` | Archived runs | Only if archiving is on |

All are listed in the updater's protected set so an update never overwrites them (see TECHNICAL.md §13).

## 12. Testing

`tests/test_mining_deposit.py`, `test_mining_hotspots.py`, `test_mining_ground.py`,
`test_mining_ledger_data.py`, `test_mining_body_survey.py` and `test_mining_coverage.py` cover the pure
logic. `test_mining_rates.py`, `test_mining_targets.py`, `test_mining_hold.py` and `test_mining_alerts.py` cover the rate, the run average and its wording, the target text and the live hold.
`test_mining_history.py`, `test_mining_net.py`, `test_mining_rings.py`, `test_mining_stops.py`, `test_mining_depletion.py`, `test_mining_share.py`, `test_mining_market.py`,
`test_mining_market_research.py`, `test_mining_what_pays.py`, `test_mining_missions.py`, `test_mining_body_lookup.py`, `test_mining_radar_extras.py` and `test_mining_simulation.py` cover the
history and its sales, the books' data, the lookups' plans and the simulation. The `*_smoke.py` tests (for example `test_mining_page_smoke.py` and `test_mining_live_window_smoke.py`) build the
panel and the windows. The overlays and the look of the map are still checked by hand in EDMC.

## 13. Known gaps

- Amount and Density are typed in by hand; a wrong reading gives a wrong range.
- The deposit figures are measurements from a handful of deposits, so the ranges are wide.
- Coverage means "driven", not "scanned".
- Limpets "on board" is approximate.
- Commodity-to-method hints (`mining_methods.py`) are community-sourced and need occasional upkeep.
