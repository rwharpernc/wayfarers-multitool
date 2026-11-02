# Missions technical specification

This document specifies Mission mode: the journal data it reads, the rules it applies, and the limits of its figures. Usage is described in the [missions guide](guide/missions.md). The general code organization is described in [TECHNICAL.md](TECHNICAL.md).

- **Author:** R.W. Harper (CMDR Mactavious)

WFMT is journal-first: it uses the information the game writes to its journal files and fills gaps from Frontier data or community services where they exist. Each gap and its workaround is documented. See [the design principle in TECHNICAL.md](TECHNICAL.md).

## 1. Scope

- Show every mission on the commander's board in one place, sorted into pages by type.
- For kill-count missions (massacres and settlement raids), show stacked progress: the kills counted, the kills each mission-giving faction still requires, and the reward.
- Show Community Goals and the commander's contribution.
- Retain the picture across an EDMC restart and keep each commander's missions separate.

### 1.1 Not included

- **Exact kill counts.** The journal does not report per-mission kill progress, so progress is an estimate (section 5).
- **Network access for the missions themselves.** The panel, the Missions window and the overlay use only the journal. The one exception is the Source commodities window (section 10), which queries Spansh only when **Find sources** is pressed and only when the online lookups of Trade are switched on.
- **Mission planning.** The feature does not suggest missions or routes.
- **Colonization missions.** They are excluded from every page (section 4).

## 2. Architecture

All modules are in `plugin/`. `PANEL_PLACEMENT = "missions"`.

| Module | Role |
|---|---|
| `missions.py` | Entry point (feature-module contract). Reads settings, starts the backlog scan, routes each journal event to the modules below. |
| `journal_scan.py` | Reads the last two weeks of journals at start-up (backlog): accepted missions, kills, redirects, Community Goals, cargo progress and the active set the journals leave. |
| `active_missions.py` | Per-commander roster of accepted and active missions (`ActiveMissions`). |
| `kill_tracker.py` | Per-commander kill evidence: `Bounty` events, completed mission ids, new turn-in places, and the on-foot or ship kill test. |
| `kill_missions.py` | The kill-count missions among the active ones, and the progress estimate. |
| `all_missions.py` | Generic summary of every active mission (the "All Missions" view). |
| `mission_cargo.py` | Collect and delivery progress of cargo missions (`CargoDepot` events). |
| `community_goal_state.py` | Community Goal snapshots and the commander's contribution. |
| `mission_types.py` | The rules that determine the category of a mission. Pure, no dependencies. |
| `missions_ui.py` | The panel (a count for each type) and the drawing of the category pages. Opens the Missions window and the Mission description window. |
| `missions_types_window.py` | The Mission types window: the category pages, selected from a list with counts. |
| `missions_board.py` | Data of the Missions window: a `Row` per active mission, totals, grouping by place, detail lines. Pure. |
| `missions_window.py` | The Missions window (Active and By place tabs, detail strip, pinning). |
| `mission_detail_window.py` | The Mission description window, opened from a mission card. `sections()` joins the `Row`, the `MissionSummary` and the raw `MissionAccepted` event. |
| `mission_pins.py` | The commander's pinned mission ids (per commander, `mission_pins.json`). |
| `mission_sources.py` | The commodities the missions still require and the source lookups (section 10). |
| `mission_sources_window.py` | The Source commodities window. |
| `notifier.py` | Subscribe and notify helper that the views use to signal a change to the UI. |

Data flows in one direction. `ActiveMissions` announces the active set. `kill_missions` and `all_missions` subscribe and rebuild. The UI subscribes to those. The data layer does not import UI code.

### 2.1 Journal events used

| Event | Use |
|---|---|
| `Commander`, and the commander name supplied by EDMC | Determines whose roster an event belongs to |
| `MissionAccepted` | Adds the mission to the roster and marks it active |
| `Missions` (sent at login) | Lists the active ids and the ids already complete |
| `CargoDepot` | Cargo mission progress: collected, delivered and total (also when a wing-mate hands in cargo) |
| `MissionRedirected` | The objective of the mission is done; may carry a new turn-in station or system |
| `MissionCompleted`, `MissionAbandoned`, `MissionFailed` | Removes the mission |
| `Bounty` | One kill; `VictimFaction` names the faction |
| `FactionKillBond` | A combat-zone kill, counted like a `Bounty` (it names `VictimFaction` but no ship type) |
| `CommunityGoal` | Community Goal snapshots (may list several goals) |
| `CommunityGoalReward` | The credits a finished Community Goal paid the commander (`CGID`, `Name`, `System`, `Reward`) |

## 3. Persistence

Every roster, kill list and goal set is keyed by commander. Switching commander in EDMC shows that commander's data only.

- The mission picture is not written to disk. It is rebuilt at each start from the two-week backlog. The saved items are the commander's pinned mission ids (`mission_pins.json`, section 8), the window positions and the settings.
- The active set comes from the login `Missions` event when one arrives.
- Otherwise (EDMC restarted mid-game) it is derived from the journals: the newest `Missions` list plus every `MissionAccepted` after it, minus every `MissionCompleted`, `MissionAbandoned` and `MissionFailed`.
- Besides the checkboxes, the saved settings are the position and last type of the Mission types window (`wfmt_missions_types_window_geometry`, `wfmt_missions_types_window_category`) and the options of the overlay card (rows, red limit, next jump, on or off).

## 4. Classification

Frontier does not document mission types. The internal `Name` of each mission contains underscore-separated tags (for example `Mission_Massacre_Onslaught`, `Mission_Delivery_Illegal_MB`). `mission_types.classify()` assigns a `MissionAccepted` event to a category. The first matching rule applies:

1. Massacre-shaped (below): Massacre (Space) or Settlement Raids (Ground).
2. The name contains a combat hint (`assassinate`, `assassination`, `disable`, `skimmer`, `conflict`, `blops`, `piracy`, `scout`, `thargoid`, `terminalprosecution`, `tacticaltakedown`, `reclamationpoint`, `biohazardtakedown`, `rapidresponse`): **Combat**.
3. The name contains a trade hint (`delivery`, `courier`, `collect`, `mining`, `salvage`, `communitygoal`, `smuggle`): **Trade & Mining**.
4. The name contains a passenger hint (`passenger`, `sightseeing`, `vip`, `bulk`, `evacuation`, `polprisoner`): **Passenger**.
5. The name contains a covert hint (`hack`, `covert`, `heist`, `sabotage`, `reboot`, `download`, `upload`, `poi`, `productionheist`, `theft`, `power`, `production`, `ncd`), or the mission is on foot: **Covert / On-Foot Ops**.
6. Otherwise: **Other**.

Definitions:

- **Massacre-shaped:** the event has both a `KillCount` and a `TargetFaction`, or the name contains `massacre`, `onslaught` or `raid`. Testing the shape first recognizes kill missions with an unfamiliar name.
- **On foot or ground:** `OnFoot` in the name, or a `DestinationSettlement` on the event.
- **Illegal:** `illegal` or `smuggle` in the name. The card shows a "⚠ Illegal" badge.
- **Mining missions:** `mining` in the name. This is narrower than "has a `Commodity` field", because Collect and Delivery missions also carry one but their cargo is bought or collected.
- **Colonization missions:** `colonization` or `colonisation` in the name (the game spelling). They are excluded from every page.

Mission names that match no rule are classified as Other. The name hints are community knowledge and are extended when Frontier adds mission types.

## 5. Kill-progress estimate

The game does not report the kills of a mission to plugins. The journal provides `Bounty` and `FactionKillBond` events, each naming the faction of the victim. WFMT replays these against the active kill missions using the stacking rules of the game.

Rules (`kill_missions.estimate_progress`), per commander:

1. A mission whose id is in the completed set (from `MissionRedirected` or the login `Missions` event) counts as fully done.
2. The remaining missions are queued per mission-giving faction, oldest first.
3. Each `Bounty` or `FactionKillBond` counts as one kill if all of these hold: the faction of the victim matches the target faction of the mission; the kill is in the same arena (on foot or in a ship, determined from the type of the victim); the kill happened after the mission was accepted.
4. A qualifying kill is credited to the oldest unfinished mission of every giver that fits. One kill therefore advances several missions of different factions, but only one mission per faction.

Display for a stack:

- **Progress `done/required`** per giver faction, with a bar. A `~` prefix marks an estimate (shown for any wing or on-foot mission).
- **Δ (remaining-kills column).** For a faction's stack, the number of kills needed to reach the tallest stack. For the tallest stack, the gap to the next-tallest.
- **Sum row.** Total progress against the tallest stack (the effective kill target when stacking). Shown only with two or more faction rows.
- **Reward:** the total, with the share from wing-shareable missions in brackets.
- **Warnings** appear when the missions have several target factions or systems, and a standing note that wing and on-foot kills are often unreported until the mission completes.

Limits:

- Wing and on-foot kills are frequently missing from the journal, so those counts are low until the game reports completion. They are marked `~`.
- Only the last two weeks of journals are read at start-up. Earlier kills are not counted. A mission that is still active but was accepted earlier is not found; the log records "active but not found in the scanned journals" and the mission is not shown.
- Kills made while EDMC was not running are found by the backlog scan only if they are in the last two weeks of files.
- Combat-bond kills count. In a check against real journals, 4 of 53 redirected massacre missions reached their kill count only with the bonds included, and 17 of the 53 fell short even with both.
- When the game reports a mission redirected or complete, that report replaces the estimate.

## 6. Completion and drop-off

A mission is Complete once its id appears in the completed set, which two events feed: `MissionRedirected` as it happens, and the `Complete[]` list in the login `Missions` event. When the redirect names a new station or system, that becomes the drop-off shown on the card. The completion state is dropped when the mission is handed in, abandoned or failed.

## 7. Community Goals

`CommunityGoal` events list `CurrentGoals`, which can include goals in several systems. The journal does not report that a goal has ended, and finished goals reappear for a while. The state is therefore additive: every goal id seen is kept and the newest snapshot wins. The panel shows only goals that have not expired. Each card shows the title, system, market, expiry, the tier reached by the community, the commander's contribution and rank, and the bonus. The tier shown is the community's.

`CommunityGoalReward` is the payout. Payouts are kept per commander in `community_goal_state.py` (the newest 20, each once, by goal id and time) and are read back from the last two weeks of journals at start-up, like the goals. The page lists the latest three under **Paid out**, below the goal cards. A finished goal is past its expiry and is no longer shown as a card, so its payout appears there.

## 8. Missions window, overlay card and pinning

### 8.1 The Missions window

`missions_board.rows_from` converts the active missions (`all_missions.MissionSummary`) into `Row`s:

- A row is ready if the mission is in `kill_tracker.get_redirected`. Its place is then the redirect destination (`get_redirect_destination`).
- Cargo progress comes from `MissionSummary.cargo`.
- Kill progress comes from `kill_missions.estimate_progress` (an estimate for wing and on-foot missions, shown with `~`).
- Rows are sorted ready first, then soonest to expire.

Further elements:

- `totals` is the summary line, `by_place` groups by system (here, next jump, then urgency) and `detail` provides the lines of the selected mission.
- `missions_window.MissionsWindow` shows them in two `DataTable`s. A table is rebuilt only when its rows changed, so selection and scroll position are kept. The window refreshes from `MissionsUI.redraw` and every 30 seconds (`_TICK_MS`).
- `MissionsUI.__live_rows` supplies the live data.
- A mission card on a Mission types page calls `MissionsUI.__show_mission_detail`, which opens (or re-points) `mission_detail_window.MissionDetailWindow`. `sections(row, summary, event, now)` builds its content from the `Row`, the `MissionSummary` and the raw `MissionAccepted` event (`active_missions.tracker.snapshot()`). Journal keys without a label are listed under "Other journal fields". Tests: `tests/test_mission_detail_window.py`.
- The three buttons of the panel (Missions window, Mission types, Find sources) are built once in `build_panel` in grid row 1 below the canvas and laid out by `panelkit.flow_buttons`.
- The six display switches are set only on the **Display** card at the top of the Mission types window (`missions_display_settings.DisplayCard`). The Settings → WFMT → Missions tab refers to the card. The config keys are in `missions_display_settings` (`missions.py` imports them). `set_value` saves a switch and notifies listeners, and `MissionsController._on_display_setting` calls `apply_display_settings`, which redraws the panel and the window.
- The panel has no category paging. `missions_ui._display_category_summary` lists each type that holds missions with its count; a click opens the Mission types window on that type. `MissionsUI.render_category` draws the page of a type into the frame of a window, using the background and wrap width of that window (the module values `_content_bg`, `_WRAP` and `_WRAP_NAME` are restored afterwards) and without the EDMC theme.

### 8.2 Pins

- `mission_pins.PinBook` keeps a set of mission ids per commander in `mission_pins.json` (`commander_data`), written at every change.
- `missions_overlay._live_entries` removes pins whose mission no longer exists, but only once the roster is known (`all_missions.view.missions` is not None).
- `Entry.pinned` makes `stack` keep the mission as its own `Item`.
- `build_lines` places pinned items first under PINNED, before HERE, NEXT and the rest. Overflow is counted in the `+N more` line.
- Tests: `tests/test_missions_board.py`, `tests/test_missions_overlay.py` (`PinnedTests`).

### 8.3 The overlay card

`missions_overlay.py` draws the Missions card on the in-game overlay. Settings are in Settings → Overlays → Missions. The card is off by default and uses the "Missions list" placement slot.

Building the lines:

- `entries_from` converts the active missions (`all_missions.view.missions`) into `Entry`s. A redirected mission (`kill_tracker.get_redirected`) is ready and goes to its new hand-in place (`get_redirect_destination`). The label is the title of the mission (a massacre is "Massacre", a cargo mission "40 Gold").
- `stack` creates one `Item` from the entries with the same category, label, place and ready flag (for a massacre, also the same faction). An entry with cargo progress stays alone. The soonest expiry is kept.
- `build_lines` sorts the items into HERE (the current system, from `FSDJump`, `Location` and `CarrierJump`), NEXT (the system named by `FSDTarget`, cleared on arrival and by `NavRouteClear`) and the rest. Within each group, ready items come first, then the soonest to expire.
- At most the row limit (`MIN_ROWS` 3 to `MAX_ROWS` 14) of items is shown, in that order, and the hidden items are counted.

Drawing:

- Each line is `title > place  time left`, clipped to `LINE_CHARS` (46) with the time always kept. The title and the place share the remaining space.
- Red: time left under the urgent limit (`DEFAULT_URGENT_MINUTES` 60, adjustable from 5 to 720 minutes). Amber: under six hours (`SOON_SECONDS`). Green: ready.
- The card has one fixed width and is drawn at its placement slot.
- The overlay is redrawn when the lines change, and every 45 seconds (`RESEND_S`) so that it does not expire. A 30-second tick keeps the times left current.
- Tests: `tests/test_missions_overlay.py`. The look smoke test draws the widest card at every text size.

### 8.4 Progress and colors

`mission_progress.compute` gives each mission a `Progress` (text, fraction, done, required). The source, in order:

1. The `CargoDepot` count of the game, when there is one.
2. The kill estimate.
3. For a source-and-return mission (`MissionSummary.commodity_key` is the internal commodity name): the tons of that commodity in the hold (`current_cargo.held()`), shared among the missions for that commodity, soonest-expiring first.

Cargo and tiers:

- `current_cargo` takes `state["Cargo"]` from EDMC on every journal event (`missions.handle_event`) and notifies the window and the overlay when the hold changes.
- `tier` maps a fraction to ready, high (at least half), low or none.

Display:

- The window tags rows `ready`, `soon`, `warn`, then `high` and `low`, and draws a six-cell bar (`_BAR` = 6).
- The `_role` of the overlay card is ready, red, amber, then high and low, drawn in the fixed colors `GREEN`, `RED`, `LIME` and `BLUE`.
- An overlay `Item` carries the summed done and required values of the missions stacked into it.
- Tests: `tests/test_mission_progress.py`.

## 9. Settings

The six display switches are set on the **Display** card of the Mission types window only (config keys begin `wfmt_missions_`): kill progress, the remaining-kills column, the totals row, mission count, target settlement (for ground missions), and the commodities-needed summary on the Trade & Mining page. All default to on. **File → Settings → WFMT → Missions** states where the switches are. The options of the overlay card are under Settings → WFMT → Overlays → Missions.

## 10. Source commodities

A Delivery mission (`mission_types.is_pickup_delivery`: `delivery` in the name, with a commodity and count, and not on foot, colonization, wing, rank or cooperative) is not bought. The faction supplies the cargo, which is collected at the station that gave the mission (a `CargoDepot` `Collect` event, within seconds or much later).

- `MissionSummary` carries `pickup_commodity`, `pickup_count` (less the amount `CargoDepot` shows collected), `pickup_station` and `pickup_pad`.
- The pad is the largest pad of the station (from `LandingPads` of the `Docked` event, `mission_types.largest_pad_of`) that WFMT recorded when the mission was accepted.
- It is recorded through `mission_types.ACCEPTED_AT` and `ACCEPTED_PAD`, which `missions.py` adds to the stored event live and `journal_scan.read_backlog` adds from `Docked`, `Location`, `Undocked` and jump events. They are empty when not docked.
- `needs_from` lists these after the market needs as `Need`s with `pickup` set, and `lookup` skips them.

`mission_sources.needs_from` sums `needed_commodity_count` per commodity over the active missions (largest first, at most `MAX_NEEDS` = 12), with the system where most of them are handed in. `lookup` runs `source_picks.find` (buying) for each in turn from the commander's system or that turn-in system. `mission_sources_window.py` shows the rows (`rows_for`), runs the lookup on a worker thread polled every 400 ms and gates it on the lookups switch of Trade. Tests: `tests/test_mission_sources.py`.

## 11. Tests

`tests/test_missions_data.py` covers the active-missions roster (commander separation, login sync, accept and finish), the kill-progress rules (stacking, oldest-first, arena and timing, redirected missions), the journal backlog reader (per-commander collection, malformed lines, age cut-off, missing folder, the derived active set, combat bonds, cargo progress) and `mission_cargo.py`. The category rules and the panel are not covered by an automated test.

## 12. Known gaps

- The NEXT section of the overlay follows the targeted system only, not the whole route.
- Mission names that match no rule are classified as Other. The hint lists require maintenance.
- Kill counts for wing and on-foot missions are estimates and can lag.
- Nothing older than two weeks is read at start-up.
- Without a login `Missions` event (EDMC restarted mid-game), the active set is derived from the journals. An expiry with no journal entry is not detected until the next login list replaces the derived set.
- Cargo mission progress comes only from `CargoDepot`. Nothing before the two-week window or between events is known.
- `FactionKillBond` carries no ship type, so an on-foot combat-zone kill is counted as a ship kill.
- Community Goals have no "gone" signal, so the panel uses the expiry date of each goal.
