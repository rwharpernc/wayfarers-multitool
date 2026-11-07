# Mining technical specification

This document specifies Mine mode: what it tracks, the rules and figures behind its estimates, the files it keeps, and the external lookups it can make. Usage is described in the [mining guide](guide/mining.md). The general code organization is described in [TECHNICAL.md](TECHNICAL.md).

- **Author:** R.W. Harper (CMDR Mactavious)

WFMT is journal-first: it uses the information the game writes to its journal files and fills gaps from Frontier data or community services where they exist. Each gap and its workaround is documented. See [the design principle in TECHNICAL.md](TECHNICAL.md).

## 1. Scope

- Track Space Mining (any ship) and Surface Mining (the Rhino SRV) runs live: refined output, rate and hold contents.
- Keep the commander's own catalog of surface hotspots, with an estimate of the tons remaining in each, retrievable in the Surface Mining Book.
- Provide a minimap of the ground driven on a body. (The arrow to the nearest saved hotspot is part of the Surface Compass.)
- Provide optional lookups (nearby ring hotspots, best prices, ring reserve levels), which are off until switched on.

## 2. Not included

- **Contents of a surface deposit.** The journal does not report them. Deposit data comes from what the commander records and the scanner readout the commander enters.
- **A shipped hotspot database.** WFMT carries no third-party deposit or hotspot data. The only prospecting figures are the commander's own saved hotspots (section 6).
- **Real scan coverage.** The minimap records where the Rhino has driven, not what was scanned (section 7).
- **Exact tons remaining.** The estimate is a range (section 5).

## 3. Architecture

All modules are in `plugin/`. `PANEL_PLACEMENT = "mining"`.

| Module | Role |
|---|---|
| `mining_panel.py` | Entry point (feature-module contract). The summary panel, its buttons, the Settings tab, and the dispatch of journal and `Status.json` events. |
| `mining_render.py` | The summary of the panel (`render_summary`) and the lines of each page (Space or Surface), redrawn on events and once a second. |
| `mining_pages.py` | The two pages and their order (separate to avoid a circular import). |
| `mining_window_settings.py` | The Settings card at the top of the Space Mining and Surface Mining windows. |
| `mining_space.py` | Ship-mining runs and the shared ring state. |
| `mining_surface.py` | Rhino surface-mining runs and the current body and system. |
| `mining_rate.py` | The current rate (tons per hour over the last minute) and the run average (tons over mining time), shared by both pages. |
| `mining_targets.py` | The target commodities entered in Settings: parsing, per-name percentages, problems. |
| `mining_methods.py` | Commodity to typical mining method(s). Static, community-sourced. |
| `mining_hotspots.py` | The saved-hotspot repository and its import and export formats. |
| `mining_deposit.py` | The tons-remaining estimate. |
| `mining_ground.py` | Classification of the kind of ground, and the commander's own rates built from saved hotspots. |
| `mining_body_survey.py` | Landable bodies seen in the current system (`Scan` and `SAASignalsFound`). |
| `mining_ring_book.py` | The Space Mining Book window. `mining_rings_data.py` and `mining_rings.py`: its data and the commander's notes. |
| `mining_ledger.py` | The Surface Mining Book window. `mining_ledger_data.py`: its data shaping (pure). |
| `mining_coverage.py` | The driven-ground record. `mining_coverage_render.py` draws the minimap (PIL). |
| `mining_live_position.py` | The live surface position from `Status.json`. |
| `mining_bearing.py` | Distance and bearing between two surface points. |
| `mining_overlay.py` | The optional on-screen stats HUD (hold, rates, hold full in, limpets remaining). |
| `mining_live_window.py` | The Live window (Surface Live with the radar and the ground controls; Space Live with the lines of the page). |
| `mining_radar_view.py` | The radar picture from the Mining data: one recipe for the Live window and the card over the game. |
| `mining_radar_overlay.py` | The Mining radar card over the game (built-in overlay, Windows). `mining_map_picture.py`: **Save map**. |
| `mining_drive_rings.py` | The rings to drive round a marked mining location. `mining_rigs.py`: the rigs noted with **Rig placed**. |
| `mining_stops.py` | Stops: the deposits that one Rhino parking spot reaches; the nearest-deposit and rig-gap helpers. |
| `mining_depletion.py` | When a Depleted mark is removed, and the dated bookkeeping behind it. |
| `mining_share.py` | The `WFMT-SPOT1` share line for one deposit. `mining_hotspot_import_export.py`: the file import and export. |
| `mining_hotspot_settings.py` | The Known Surface Hotspots list on the Settings page. |
| `mining_simulation.py` | The simulated Rhino for the Live window. `mining_sources.py`: where the renderers read their data. |
| `mining_history.py` | Every mining run read from the journals, per commander. `mining_history_data.py` (pure) and `mining_history_window.py`: the Dashboard. |
| `mining_alerts.py` | Core, rich-rock, limpet and hold alerts for Flight Alerts; the rock reading shared with the Space page. |
| `mining_market.py` | What the open market pays against the galactic average. `mining_missions.py`: the mission-needs lines. |
| `mining_market_research*.py`, `mining_what_pays*.py` | Market research and What pays: the plan (pure) and the windows. |
| `mining_body_lookup.py`, `mining_body_cache.py` | Get body info (EDSM and Spansh) and its cache. |
| `mining_session_archive.py` | Optional JSON archive of finished runs. |
| `mining_journal_backfill.py` | Replays the journal of the day when EDMC starts mid-session. |
| `mining_location.py` | The commander's current system. |
| `mining_names.py` | One spelling for a commodity or mineral name. `mining_bodies_data.py`: the bodies the Rhino mined on, read from the journals. |
| `mining_*_dialog.py` | The Add/Edit Hotspot form and the three lookup dialogs. |
| `mining_spansh_client.py` | The Spansh lookups (hotspots, best price). `edsm_client.py`: ring reserves. |

Pure logic (`mining_hotspots`, `mining_deposit`, `mining_ground`, `mining_ledger_data`, `mining_body_survey`, `mining_coverage`, `mining_bearing`, `mining_rate`, `mining_targets`) has no screen code and is unit-tested.

## 4. Runs

### 4.1 Space Mining

A run is one undock-to-dock trip. `Undocked` starts a new run. `Docked` leaves the finished figures on screen until the next undock. A finer boundary would split one stop at a ring into several runs whenever the commander enters supercruise. In supercruise mid-trip the panel shows a "paused" hint and resets nothing.

Events used:

| Event | Use |
|---|---|
| `ProspectedAsteroid` | Content grade, composition, with duplicate-asteroid detection |
| `LaunchDrone`, `BuyDrones` | Limpets used, and an approximate "on board" figure that cannot distinguish an unused timed-out limpet from one still deployed |
| `MiningRefined` | The refined output |
| `AsteroidCracked` | Core mining |
| `Cargo`, `Loadout` | Hold, and `CargoCapacity` |
| `SupercruiseEntry`, `SupercruiseExit` | Run pause and current ring |
| `Location` in a planetary ring | Sets the current ring, like a `SupercruiseExit` |

The hold is also read live from `Status.json` (below).

`ProspectedAsteroid` also carries `Remaining` and, for a core (motherlode) asteroid, `MotherlodeMaterial`.

- `mining_alerts.rock_finding` reads each event into a `RockFinding`: materials richest first, grade, remaining, core mineral, and which of the commodities chosen in Settings are at or above their percentages.
- The run keeps the latest one (`last_rock`) and counts cores (`cores_found`, once per distinct rock like the other counts).
- The limpets aboard are exact: `state["Cargo"]` of EDMC (by name, `drones`) goes to `SpaceMiningRun.limpets_aboard`. The page and the HUD overlay (one function, `mining_render.limpets_on_board`) fall back to bought minus launched only when the figure is unknown.
- A rock is counted once by one key (`mining_alerts.prospect_key`: the names and proportions of the materials to a tenth of a percent) in the run, in Mining History and in the rock alerts. A rock without usable materials is never a repeat.
- History keeps a grade it cannot read (`ungraded`) apart from Low and outside the High and Low shares.
- `mining_missions.needs` totals the remaining tons of the active mining missions by commodity and applies the hold (`current_cargo.held()`), for the "Mission needs" lines of the page. The panel redraws when the missions change.

The Flight Alerts card carries transient alerts (a core or target rock for `ROCK_ALERT_S` = 30 s) and conditions (limpets at or under a number, the hold at or over a percentage, only within `ACTIVE_S` = 30 minutes of a mining event). See `mining_alerts.MiningWatcher` and `flight_alerts.py`.

- **Limpet alert:** applies only when the latest `Loadout` has a prospector or collector controller (`Modules[].Item` starting `int_dronecontrol_prospector` or `int_dronecontrol_collection`) or limpets have been seen aboard since then. It is never raised while a Rhino is out (`LaunchSRV` to `DockSRV`, or `Cargo` for the SRV).
- **Target rock alert:** not raised when `Remaining` is under `MIN_REMAINING_PERCENT` = 25.
- **Once per composition:** a core and each target that a rock matches are alerted once per composition per run, by the pair (rock key, `core` or the canonical name of the target), reset at `Undocked`. A rock seen again raises nothing new. A target added to the settings in between raises its own card.
- **Card limit:** at most `MAX_TARGET_CARDS` = 3 target cards (the richest) for one rock.
- **Sound:** keyed on the kind of the alert (and the composition of the rock for a rock alert), not on its text.
- **Name matching:** the target commodities are compared with the materials of the rock by `mining_names.normalize`. `mining_methods.methods_for` normalizes its argument, so every spelling of a commodity finds the same entry.

**Target commodities.** The Settings box (`wfmt_mining_target_commodity`, one text key, with `wfmt_mining_target_percent` as the default percentage) accepts one or several names separated by commas or semicolons, each optionally followed by its own percentage (`Painite 30, Platinum 25, Void Opals`).

- `mining_targets.parse_targets` reads it into `Target(name, percent)` items:
  - at most `MAX_TARGETS` = 8;
  - a name without a number takes the default percentage;
  - names are keyed by `mining_names.normalize`, so spelling variants and a name listed twice form one target;
  - an unknown name is kept.
- It also returns a list of problems for the Settings page: a percentage that is not a number from 1 to 100 (the entry is left out), a duplicate, or more than the maximum.
- A box holding one plain name reads as it did when the box held one name.
- `RockFinding.hits` holds every target at or above its percentage, richest first. `RockFinding.target` is the first.
- The Last rock line names them (`target: Painite`; three names at most, then a count).
- The type-ahead in the box is attached through `mining_targets.LastItemVar`, which provides the item after the last comma and writes a selected name back into that item only.
- The target material of the radar and What pays use the first target (`mining_alerts.primary_target`).

**The hold.**

- The `Cargo` field (tons carried) of `Status.json` arrives through the dashboard hook of EDMC (`mining_panel.dashboard_status`, `flight_alerts.dashboard_status`) about once a second.
- `mining_alerts.status_hold` takes it only while the `Flags` of the entry say the commander is in the main ship (bit 24) and not in an SRV (bit 26) and the journal does not say a Rhino is out. In any other state the live figure is discarded and the `Cargo` events are used, because what `Cargo` counts in `Status.json` while in an SRV could not be checked.
- The figure is kept per commander in `SpaceMiningRepository.live_cargo` (not run-scoped, like the capacity) and in `MiningWatcher.live_cargo`. A `Cargo` event for the ship clears it until the next `Status.json` update.
- The capacity is `CargoCapacity` of the last `Loadout`.
- `mining_render.format_ship_cargo` draws `Hold: 64 of 200 t` from them (`Ship hold:` beside the SRV line on the Surface page, `SRV hold: 40 of 72 t`).
- The Hold nearly full alert (`MiningWatcher.held`) uses the live figure, otherwise the figure of the event.

### 4.2 Surface Mining

A run is one Rhino deployment. `LaunchSRV` with `SRVType == "mev_rhino"` starts it and the matching `DockSRV` ends it. The Rhino uses the ordinary `MiningRefined` event, so WFMT routes it to the Surface page only while a Rhino is deployed. WFMT also tracks the SRV hold (capacity 72, `RHINO_CARGO_CAPACITY`), cargo handed to the ship mid-run (`CargoTransfer`, so that it is not counted as a loss), and materials collected. Docking the Rhino moves whatever remains in its hold to the ship.

### 4.2.1 Sales in the history

`mining_history.runs_from` attributes each `MarketSell` (`Type` / `Type_Localised`, `Count`, `TotalSale`) to the runs that mined the commodity, at whichever station the sale is made.

**Unsold list**

- Every finished run appends `[run key, tons]` per refined commodity to a list of unsold mined tons (`unsold`, by normalized commodity name, oldest first; the run key is `file|start`, `mining_history.run_key`).
- The list is carried through the journals in order and saved with the runs (`unsold` in the commander's payload). A file without it loads as empty, and `MiningHistory._payload` drops a malformed one.

**Splitting a sale**

- A sale takes `min(Count, tons waiting)` from the front of the list of that commodity, run by run.
- Each run gets the tons and `TotalSale * tons so far // Count` less what earlier runs of the same sale already received, so the shares add up exactly.
- Tons beyond the list are ignored, so a sale never creates credit.
- The `sold` entry of the run (`{commodity: [tons, credits]}`) is updated in place, also for a run saved from an earlier journal.

**Replay and rebuild**

- The newest journal is never saved. It is replayed on copies of the saved list and of the runs it touches (`_live_unsold`, `_live_patch`), so reading it again changes nothing.
- **Rebuild from journals** (`clear`) empties `unsold` together with the runs and replays every journal through the same code.

**Limits**

- The journal does not state what a jettisoned, destroyed or transferred ton was, so those tons remain on the list until a sale of that commodity uses them.
- Bought cargo of a commodity that is also waiting is credited to the oldest run that mined it.
- Cargo mined while EDMC was closed is known only after its journal is read.

### 4.3 Rate

One `MiningRefined` event is one ton (the `Cargo` count of the hold rises by one per event in a real journal), so event counts are tons.

- **Refining now** (`mining_rate.current_rate`): the tons refined in the last `RATE_WINDOW_SECONDS` = 60, scaled to tons per hour. A run younger than the window divides by its age, never by less than `MIN_RATE_SPAN_SECONDS` = 10. The list of refined timestamps is pruned in place to the window. The figure is recomputed on each refinement and on the timer of the page, so it falls to zero within a minute of a pause.
- **Run average** (`mining_rate.MiningClock`, `run.clock` on both kinds of run): the tons refined in the run (the sum of `refined`) over the mining time.
  - The mining time is the sum of the gaps between consecutive mining events that are at most `MAX_GAP_SECONDS` = 600. Longer gaps are excluded.
  - The mining events are those the history counts as mining events: `ProspectedAsteroid`, `MiningRefined`, `LaunchDrone`, `AsteroidCracked`; for the Rhino only `MiningRefined`.
  - The clock keeps the first and last event times and the time mined, because the timestamp list is pruned.
  - The average is shown once the run has `MIN_AVERAGE_SECONDS` = 60 of mining time (`none yet` with no events, `needs a minute of mining` before).
  - Events carry the time of the journal (`mining_rate.event_time`), so a journal replayed at start-up (section 4.4) gives the real mining time and no rate spike.
- The panel, the HUD and the Live window use the same wording through `mining_render.format_rate_now` (`Refining now: 840 t/h`) and `format_run_average` (`Run average: 720 t/h over 41 min`).
- `format_time_to_full` (`Hold full in about 14 min`) divides the room left in the hold (capacity less tons, from `ship_hold` or the fixed 72 t of the Rhino) by the run average, or by the current rate while there is no average. `mining_rate.minutes_to_fill` and `full_in_text` hold the arithmetic and the wording.
  - It returns nothing when the capacity is unknown or nothing is being refined, `Hold is full` once the room is gone (omitted, through `hold_shown`, where the hold line of the panel is on), and nothing for a stowed Rhino.
- **Station price against the average.**
  - `mining_panel` passes the `Market` journal event to `mining_market.on_market`, which reads `Market.json` through `trade_market.read_market_file` (waiting while the file still belongs to the previous station) and keeps that one market until `Undocked`.
  - `trade_market.MarketItem` carries `mean_price` (`MeanPrice`, the galactic average) and `demand_bracket` (`DemandBracket`).
  - A station lists a `SellPrice` for goods it does not buy, with no demand, so `mining_market.buys` requires a price, demand, a bracket above zero and an average.
  - A commodity is found by its localized name first (`Low Temperature Diamonds`; the internal name of the game is the singular `lowtemperaturediamond`), then by the canonical name.
  - `mining_market.lines` produces up to three lines, the most tons refined first. `render_space_mining` shows them under the rate lines.
  - Nothing is fetched.
- **Limpet cost in Mining History.**
  - `runs_from` also reads `BuyDrones` (`BuyPrice`, otherwise `TotalCost` over `Count`, field names as in the trade ledger) into a price held in `prices["unit"]`, carried from journal to journal and saved as `limpet_price` in the history file.
  - It charges each `LaunchDrone` at that price: `limpet_cost` on the run, and `limpet_unpriced` for launches made before any price was seen.
  - `mining_history_data.net` is the earned amount of the run less `limpet_cost`. The overview tile, the Sales block and the Runs column use it.
  - `RUNS_VERSION` 5 causes runs saved without it to be read from the journals again.
  - Not subtracted: fuel, repairs, ammunition, limpets sold back.
- **Mining time in Mining History:**
  - `mining_history.runs_from` adds the gaps of more than ten minutes to the `idle` of the run (seconds; present only when there was one), and `mining_history_data.mining_hours` subtracts it from the first-to-last span.
  - `RUNS_VERSION` 4 causes runs saved without it to be read from the journals again.
  - Small differences from the live figure remain: the page counts from when WFMT saw an event, the history counts from the journal timestamps, and the page waits a minute before showing an average.

### 4.4 Mid-session start

If EDMC starts while the commander is mining, WFMT replays the journal file of the day through the same handlers so that the current run is picked up. Older files are ignored, because a run does not outlive its undock or deployment.

## 5. Tons-remaining estimate

The journal reports neither the size of a deposit nor how much of it remains. The in-game mining scanner shows two readings, Amount (High, Medium, Low, Depleted) and Density (High, Medium, Low), which the commander enters on a hotspot. The result is a range.

The model (`mining_deposit.reserve_range`) is based on measured depletion of real deposits (credited in `THIRD-PARTY-NOTICES.md`):

- A full deposit holds a fixed number of tons per rig position, set by Density. A lower Density label means a larger reserve: 125 to 175 t per position at High, 250 to 350 at Medium and 375 to 525 at Low.
- The Amount label gives the share still remaining: High 56.6% to 100%, Medium 26.7% to 66.5%, Low 0% to 34.2%, Depleted 0.
- Range = rigs × tons per position × share remaining, rounded to the nearest 10 t. With no Density, the range spans the smallest low end (125) to the largest high end (525).

At most 7 rigs can be recorded (`MAX_RIGS`; six can be worked at once and a seventh can be placed but not run). While the Rhino is out, each refined ton is credited to the nearest saved hotspot within 200 m (`MINED_ATTRIBUTION_M`), so a depleted deposit reads "depleted (612 t)". Tons are counted in memory and written at most every 5 seconds (`_MINED_SAVE_INTERVAL_S`). The figures are measurements and are refitted as more deposits are mined.

## 6. Hotspots, the Surface Mining Book and own rates

### 6.1 The hotspot file

`mining_hotspots.json` (in the plugin folder, never part of a release) holds one list of hotspots per commander (`commander_data.py`: `{"version": 2, "commanders": {key: {"name", "data": [...]}}, "legacy": ...}`). A hotspot, its notes, tons mined and depleted mark belong to the commander who saved it.

- `HotspotRepository.set_commander` switches the list when the active commander changes (the mining panel calls it on every event that names a commander).
- Until a commander is known the list is empty, and anything added waits for the first commander.
- A file from before this was a single flat list. The first commander seen claims it, and the others start empty.
- Import and Export operate on the list of the active commander, which is the method for copying hotspots to another commander.

A hotspot holds:

- A system, body and material, plus optional notes, latitude and longitude, a folder label, rigs, a signal number, the Amount and Density readings, the tons mined so far, and the kind of ground (section 6.3).
- Material, rigs, signal number, Amount and Density are entered by the commander. Only the mined tons are derived from the journal.
- Saving a hotspot within 100 m (`SAME_SPOT_M`) of an existing one on the same body updates it instead of adding a duplicate.

Depletion bookkeeping is stored on the hotspot (`depleted_at`, `regrown_at`, `tons_at_regrow`, `rechecks`; a record without them loads with defaults).

- `mining_depletion.apply` is called by `HotspotRepository.add` and `update`, so the dialogs, which build a hotspot without these fields, cannot lose them.
- `settle` runs when the list of a commander loads and when the Surface Mining Book refreshes.
- A Depleted mark is removed `wfmt_mining_refill_days` days after it was set (default 0 = unknown: never removed, the card states how long ago it was set; maximum `MAX_REGEN_DAYS`, 90; the repository property `refill_days` holds it).
- Mark depleted on a hotspot that has refilled with no ton refined since is a recheck (the first date is kept; the mark is removed `RECHECK_DAYS` (7) after the check).
- A Depleted mark without a date is dated on first sight.

### 6.2 Import and export

WFMT exports and re-imports its own file format, with a merge or replace choice (the **Import/export** button and the buttons in Settings).

### 6.3 The Surface Mining Book

A three-pane window: bodies (the scanned landable bodies of the current system plus every saved hotspot, anywhere), the hotspots of a body grouped by location, and a detail card with a zoomable map. Filters are by material and by rig count. The card offers Edit, Mark depleted, Copy coordinates and Delete.

**Stops.**

- `mining_stops.find_stops` groups the active, positioned deposits of a body that have a rig count. The deposit with the most rigs leads (ties by the number of other deposits within reach), and every remaining deposit within the stop radius joins it. The stop radius is `wfmt_mining_stop_radius_m` (500 to 2500 in steps of 250, default 1250).
- `best_stops` keeps up to three whose lead has 5 or more rigs, otherwise 4 or more. It needs the radius of the body, which is known only for the body the Rhino is on.
- The Book lists them, tags the row of each deposit, and the map draws a dashed ring (`MapCircle`) around each lead.

**Current position:** `mining_ledger_data.deposit_here` finds the positioned hotspot (depleted included) within 175 m (`YOU_ARE_HERE_M`) of the live position. The Book marks and selects it when no deposit was already selected.

**Market research.**

- `mining_market_research.plan` lists the commodities worth checking in a system, each with its reasons: deposits saved in that system (most first), then the commander's own rates (`OwnRates`) on the ground of the scanned bodies of the system (highest share first), then names typed by hand.
- Names are resolved with `trade_commodities.resolve`. Unknown names are reported and not searched.
- There is no commodity-to-planet-type table: the game publishes none, and community testing treats planet class as a screening hint.
- `mining_spansh_client.search_system_stations` makes one `/api/stations/search` request with a distance of at most 0.01 ly from the system (checked live on Sol: 44 stations, each with its whole `market` and `market_updated_at`), keeps those in the system that have a market and are not fleet carriers, and sends only the system name.
- `match` lists the buyers (demand and sell price above zero) per commodity, best price first.
- It shares the switch of the price finder (`wfmt_mining_spansh_price_finder_enabled`).

**Fleet carriers and the demand floor in the price searches.**

- The price finder and What pays exclude carriers, as `search_system_stations` does.
- `search_best_price_stations` takes `exclude_carriers` (a result whose `type` contains "carrier" is skipped) and the `station_types` filter (`filters.type`, the names of Spansh). Filtering on the response alone would let carrier markets fill the page ahead of stations (see `_MARKET_DAYS_OLD_DEFAULT`).
- `mining_what_pays.NO_CARRIERS` combines the two with `trade_prices.station_types(True)`. A kind of station that this list lacks is not found.
- Pad size and a market age inside the 30 days are not filtered.
- `min_quantity` (`filters.market[].demand`, selling) is set per search. `mining_what_pays.minimum_for` returns the tons of the commodity in the hold, otherwise 1 (`current_cargo.held()`, `state["Cargo"]` of EDMC, matched by `trade_commodities.resolve`).
- The box of the price finder starts at that value when selling and accepts a whole number from 1 to `MAX_MINIMUM` tons (`parse_minimum`). What pays uses the figure for each commodity.
- Every call goes through `spansh_courtesy.call`, which writes the endpoint (without its query), outcome and time of each request to the separate diagnostic log while it is on (Settings → WFMT → General → Help).

**Sharing.**

- `mining_share.encode` writes `WFMT-SPOT1:<base64url JSON>:<CRC-32 hex>`: system, body, material, position (5 decimals) and, when present, rigs, location number, Amount, Density, ground and the radius of the body. It never includes notes, folder, tons, dates or a commander.
- `decode` strips chat decoration, checks the prefix, the CRC and every field (text 80 characters, no control characters; latitude, longitude, rigs 1 to 7, Amount and Density from the lists of the game, radius) and raises `ShareError` with a message for the commander.
- `find_duplicate` refuses a spot within `SAME_SPOT_M` of one saved on the same body (using the body radius of the receiver if known, otherwise that of the sender, otherwise an assumed one).
- **Paste spot** in the Book asks before `HotspotRepository.add`.

**Own rates.** For a scanned body, the Surface Mining Book shows what the commander has found on that kind of ground: the share of the saved deposits per material, with the sample size.

- `mining_ground.classify` converts the `PlanetClass` and `Volcanism` of the journal into a ground (for example "Rocky body, silicate magma").
- A new hotspot is stamped with its ground when saved. A hotspot saved without a ground, or imported, counts while its body is in the current survey.
- The figures are tallies of the commander's recorded deposits only. They are not a statement about what any body holds, and the section is empty until the commander records something.

### 6.4 The Space Mining Book

The **Book** button in the header of each window opens the book for that page: `mining_ring_book.py` from the Space Mining window and `mining_ledger.py` (the Surface Mining Book above) from the Surface Mining window.

The Space Mining Book is a catalog of rings built from the journals.

- `mining_history.py` reads every journal once in the background. The same pass keeps, per ring, what `SAASignalsFound` reports on a ring body (each mineral with its hotspot count) and what the `Scan` of a body reports about its rings (`Rings[].RingClass` and `ReserveLevel`).
- They are kept in the payload of the history (`rings`, `bodies` and `scan_files` beside `runs`, `files` and `unsold`). A saved file that lacks them (`extras`) is read once more for them, and its runs are not counted twice. The newest journal is read afresh, like the runs.
- `mining_rings_data.build_rows` joins them with the runs (tons refined and the last run per ring) and the commander's own entries.
- The journal records only a hotspot count per mineral for a ring. It contains no position and no overlap information.

For the Surface Mining Book, the same pass keeps the bodies the Rhino mined on (`mining_bodies_data.py`):

- The `$PlanetaryMiningLocation_Name;` count of `SAASignalsFound` per non-ring body.
- The planet class from a landable `Scan`.
- The tons refined while a Rhino was deployed (`LaunchSRV` with `SRVType` `mev_rhino`, until `DockSRV`, `SRVDestroyed` or `Died`) on the body last approached (`ApproachBody`, or `Location` on a planet).
- The book lists them in a `From your journals` group (`mining_ledger_data.build_body_groups(journal=...)`) and adds the tons to the bodies it already lists.
- The journal has no deposit positions, so deposits remain the hotspots of the commander.

The notes, favorites and rings added by hand are in `mining_ring_notes.json` (`mining_rings.py`, one record per commander, never in a release).

## 7. On the ground

### 7.1 Live position

Latitude, longitude and heading come from `Status.json` through the dashboard hook of EDMC (about once a second) and are valid only on the surface of a landable body. The radius of the body also comes from `Status.json`, with the radius from the `Scan` event of the body as a fallback.

### 7.2 Coverage minimap

While a Rhino is deployed and a radius is known, a point is recorded as the commander drives (at least 250 m, `STAMP_M`, from the previous one), and the map paints a 2,000 m disc (`SCAN_RADIUS_M`) at each.

- This records where the Rhino has driven. Nothing in the journal or `Status.json` states that a scan happened, so the map cannot show real scan coverage.
- The map is a fixed 220 px square (`MAP_SIZE_PX`), 12 km across, north up, with hotspots (a pale filled dot for live, a hollow gray ring for depleted, so that shape carries the meaning for color-blind users) and the position of the commander.
- Without a Rhino deployed it is shown only below 2 km altitude.
- It uses a flat-earth projection.

**Marked mining locations.** The journal gives neither the position nor the size of a mining location, so the commander marks them:

- **Mark center** stores the live position as the center of a site (within 100 m, `SAME_SITE_M`, of an existing center it moves that center).
- **Mark border** stores the border on the nearest site. The radius is the distance between the two.
- Up to 12 sites are kept per body (`MAX_SITES_PER_BODY`), in the coverage file (per commander).
- The minimap draws a cross and a circle for each site. The page reports how much of the border circle (72 sample points, `EDGE_SAMPLES`) lies within 2,000 m of a recorded point.
- That figure is driven ground and not scanned ground. The 2,000 m reach is the same community figure that the map uses.

### 7.3 The Live window and the radar

The **Space Mining** and **Surface Mining** buttons open one window for each page (`mining_live_window.py`; the Ctrl+Alt+Shift+L shortcut and `!wf live` open the Surface one). Geometry is saved per page. The window redraws once a second. The lines of the page are drawn by the same code as the panel (`mining_render`, without the button bar), so the two cannot disagree. The window does not shrink below `MIN_SIZE` (1120 by 600 pixels on the Surface page, 600 by 560 on the Space page), so the header buttons keep their room.

- **Surface Live** has the radar (`mining_radar_view.render`, drawn by `mining_coverage_render.render_radar`): the Rhino in the middle, north up, range rings, the driven ground (a 2,000 m disc at each recorded point), marked locations, saved deposits, a line to the nearest deposit, the stops, the drive rings, and the rig markers and bands. The range steps through `RADAR_RANGES_M` = 50, 250, 500, 1,000 and 2,000 m (default 2,000, `wfmt_mining_live_radar_range_m`, shared with the card over the game).
- **Drive rings** (`mining_drive_rings.ring_radii`): the first ring is one scanner reach (2,000 m) from the center. Each next ring is 90% of a scanner diameter (3,600 m) further (`OVERLAP` = 0.9), at most 12 (`MAX_RINGS`), with the last on the border. With no border, the rings reach as far as the ground driven. They derive from the one community figure for the reach and are a guide.
- **Rigs** (`mining_rigs.py`): the journal does not state where a rig was placed, so **Rig placed** (button, Ctrl+Alt+Shift+R or `!wf rig`) notes the position of the Rhino. A second press within 5 m adds nothing. At most 40 are kept (`MAX_RIGS`). They are not saved and are discarded on launch, stow, destruction or a change of body. With the rig gap setting (`wfmt_mining_rig_gap_m`, 0 to 2,000 m in steps of 5, 0 = off) the radar draws a band of that radius round each rig.
- **Save map** (`mining_map_picture.py`) draws the same marks once, centered on the marked location, with a title and a legend, to a PNG chosen by the commander. It contains no commander name or date.
- **The card over the game** (`mining_radar_overlay.py`): the same picture laid over the game as one image by the built-in overlay (Windows). EDMCModernOverlay cannot draw a picture. It is drawn while a Rhino is deployed and the position and body size are known, at most once a second, with a translucent background (`wfmt_mining_radar_enabled`; `wfmt_mining_radar_size` 240 to 560, default 340; `wfmt_mining_radar_opacity` 30 to 100, default 70). The slot is `mining_radar` in Overlay Placement.
- **Shortcuts.** Mark center, Mark border, Rig placed, the radar range and opening the window are shortcut actions (`shortcut_actions.py`, `shortcuts.py`; see the [Shortcuts guide](guide/shortcuts.md)).
- **Simulation** (`mining_simulation.py`): Settings → Mining → Simulation opens Surface Live on simulated data. It builds its own repositories, never given a plugin folder or a commander, so none can write a file. The window has no Import/export.

### 7.4 Waypoint arrow (Surface Compass)

The arrow is part of the Surface Compass (`surface_compass.py`; see [TECHNICAL.md](TECHNICAL.md) and the [Exploration guide](guide/exploration.md#compass)).

- By default it points to the nearest saved hotspot with a position on the current body, using great-circle distance and initial bearing between the live position and the hotspot (`mining_bearing.py`, `mining_live_position.py`).
- It can instead point at a mark made by the commander or at nothing.
- It does not require the Surface Mining page to be open.

## 8. Optional lookups

All are off until switched on in the Mining Settings tab. See [TECHNICAL.md](TECHNICAL.md#keeping-api-traffic-low) for how call volume is limited.

| Lookup | Service | Trigger |
|---|---|---|
| Find Nearby Hotspots (rings with a confirmed hotspot for a commodity, nearest first) | Spansh | Button |
| Find Best Price (best-price stations for a commodity) | Spansh | Button |
| Check Ring Reserve Level | EDSM | Button; and automatically on dropping into a ring, if enabled |
| Market research (Surface Mining Book) | Spansh | Button; shares the Find Best Price switch |
| What pays (Surface Mining Book) | Spansh | Button; shares the Find Best Price switch |
| Get body info (Surface Mining Book) | EDSM, and Spansh when the id of the system is known | Button; its own switch (`wfmt_mining_edsm_body_lookup_enabled`) |

The automatic ring check runs only when enabled, never while the journal is replayed at start-up, and the answer is remembered for the session for each ring. A non-Metallic ring shows a laser-mining caution. Spansh does not publish the request shape used for its ring and station searches. The shape was determined from live calls and checked against independent callers. `mining_spansh_client.py` is the one place to change if Spansh changes it.

Two details shared with [Trade mode](TRADE_TECH_SPEC.md):

- The market search of Spansh is case-sensitive and exact ("Liquid oxygen" finds markets, "Liquid Oxygen" finds none), so the price finder resolves the typed text through `trade_commodities.resolve` to the exact name of the game before searching.
- `search_best_price_stations` accepts `max_distance_ly=None` for "no distance limit", which the Galaxy search of Trade uses. The Mining dialog always passes a distance.

**Window settings.** The display and tuning settings are set only on the **Settings** card at the top of the Space Mining and Surface Mining windows (`mining_window_settings.SettingsCard`, which `mining_live_window` builds unless the window is a simulation).

- The config keys are in `mining_window_settings` (the panel imports them).
- `value` and `set_value` read and save a field with the same clamping as the Settings tab (`mining_stops.clamp_radius`, `clamp_rig_gap`, `clamp_refill_days`). `set_target` and `target_status` do the same for the target commodities.
- Every change is announced to listeners: each open card updates itself, and the listener of the panel (`_on_window_setting`) redraws.
- The lookup switches and the body lookup are on the Online tab of Settings; the archive option and the simulation remain on the Mining tab, which states where the rest of the settings are.

**Panel.** The Mining panel has no pages and no arrows. `mining_render.render_summary` draws a few lines for the ring run and a few for the Rhino, both at once, then the buttons. A button for each page (`mining_pages.PAGE_ORDER`) opens the Live window of that page (`mining_live_window`, which also takes `actions`: the Book and Dashboard buttons of the page). `_page_for_panel` (Surface Mining while the surface repository is active or an SRV is out, otherwise Space Mining) selects which side the overlay and the Prices suggestions follow.

The buttons of the panel (`mining_render.BUTTON_ORDER`: Space Mining, Surface Mining, Hotspots, Prices, Reserves) carry their full names and are laid out by `panelkit.flow_buttons`, which wraps them onto a second line instead of widening the window. Every button on the panel and in the windows has a hover tip in the form "Name - what it does".

## 9. Optional extras

- **On-screen stats panel** (overlay). It registers a plugin group (EDMCModernOverlay needs one for its background to be drawn; the built-in overlay uses the same prefix to place the display as one piece).
- **Archive completed runs.** Off by default. When a run that has data ends, a JSON file is written to `mining_sessions/` for analysis outside WFMT. Empty trips write nothing.

## 10. Settings

Set on the **Settings** card of the windows only (keys begin `wfmt_mining_`; see section 8):

- Session totals, cargo bar, prospector hints (`wfmt_mining_display_session_totals`, `_cargo_bar`, `_prospector_hints`; on), in both windows.
- Space Mining: the target commodities and the default percentage (`wfmt_mining_target_commodity`, `wfmt_mining_target_percent`). A line under the box lists problems in the entered text.
- Surface Mining: the coverage minimap (`wfmt_mining_display_coverage_minimap`; off), `wfmt_mining_stop_radius_m` (500 to 2,500 in steps of 250, default 1,250), `wfmt_mining_rig_gap_m` (0 to 2,000, 0 = off) and `wfmt_mining_refill_days` (0 to 90, 0 = unknown).

Under **File → Settings → WFMT → Mining**:

- Run archiving (`wfmt_mining_archive_sessions`; off). The three lookups (`wfmt_mining_spansh_hotspot_finder_enabled`, `wfmt_mining_spansh_price_finder_enabled`, `wfmt_mining_edsm_reserve_lookup_enabled`) and the body lookup (`wfmt_mining_edsm_body_lookup_enabled`) contact other services, so they are switched only on the Online tab (Settings → WFMT → Online); the Mining tab shows a note pointing there, and each dialog shows `online_lookups.needs` while its lookup is off.
- The Known Surface Hotspots list (add, edit, delete, import, export) at the bottom of the tab, and the Simulation button.

Elsewhere:

- The two overlays (the HUD overlay and the radar) are under Settings → WFMT → Overlays → Mining.
- The switches of the mining alerts (`wfmt_flight_mining`, `wfmt_flight_limpets_low`, `wfmt_flight_hold_percent`) are under Settings → Overlays → Flight Alerts.
- No page is remembered: the panel always shows both sides.

## 11. Files

| File | Content | Notes |
|---|---|---|
| `mining_hotspots.json` | Saved hotspots (the Surface Mining Book) | One list per commander; never in a release |
| `mining_ring_notes.json` | The notes, favorites and rings added by hand of the Space Mining Book | One record per commander; never in a release |
| `mining_coverage.json` | Driven-ground record per body | One map per commander (same layout and legacy rule as the hotspot file) |
| `mining_history.json` | The runs of the Mining History window, built from the journals | One record per commander; never in a release |
| `mining_body_cache.json` | What Get body info of the Surface Mining Book found for each system | One record per commander; never in a release |
| `mining_sessions/` | Archived runs | Only if archiving is on |

All are listed in the protected set of the updater, so an update never overwrites them (see TECHNICAL.md section 13).

## 12. Tests

- `tests/test_mining_deposit.py`, `test_mining_hotspots.py`, `test_mining_ground.py`, `test_mining_ledger_data.py`, `test_mining_body_survey.py` and `test_mining_coverage.py`: the pure logic.
- `test_mining_rates.py`, `test_mining_targets.py`, `test_mining_hold.py` and `test_mining_alerts.py`: the rate, the run average and its wording, the target text and the live hold.
- `test_mining_history.py`, `test_mining_net.py`, `test_mining_rings.py`, `test_mining_stops.py`, `test_mining_depletion.py`, `test_mining_share.py`, `test_mining_market.py`, `test_mining_market_research.py`, `test_mining_what_pays.py`, `test_mining_missions.py`, `test_mining_body_lookup.py`, `test_mining_radar_extras.py` and `test_mining_simulation.py`: the history and its sales, the data of the books, the plans of the lookups and the simulation.
- The `*_smoke.py` tests (for example `test_mining_page_smoke.py` and `test_mining_live_window_smoke.py`) build the panel and the windows.
- The overlays and the appearance of the map are not covered by an automated test.

## 13. Known gaps

- Amount and Density are entered by hand. A wrong reading gives a wrong range.
- The deposit figures are measurements from a small number of deposits, so the ranges are wide.
- Coverage means driven ground, not scanned ground.
- The limpets "on board" figure is approximate.
- The commodity-to-method hints (`mining_methods.py`) are community-sourced and require maintenance.
