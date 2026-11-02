# Boxel Survey technical specification

This document specifies Boxel Survey and its three sub-modes (Sequence, Region Sweep, Waypoint Route): the behavior of the system, the reasons for it, and the open gaps. Release history is in `CHANGELOG.md`.

- **Author:** R.W. Harper (CMDR Mactavious)
- **Status:** work in progress. Feedback and bug reports: [open an issue](https://github.com/rwharpernc/wayfarers-multitool/issues).

WFMT is journal-first: it uses the information the game writes to its journal files and fills gaps from Frontier data or community services where they exist. Each gap and its workaround is documented. See [the design principle in TECHNICAL.md](TECHNICAL.md).

## 1. Scope

Boxel Survey supports the systematic survey of a procedurally generated boxel (subsector) inside EDMC. Target advancement follows the live journal stream on each jump, and a clipboard function supplies names for the search of the in-game galaxy map.

## 2. Not included

- **In-game overlay.** Boxel Survey draws nothing on the game screen (unlike Landing Assist and Inventory, which use `overlay.py`).
- **id64 and coordinate decoding.** WFMT contains no id64 or coordinate decode math (section 4.3).
- **Prediction of promising unvisited boxels.** Not buildable against any public data source (section 6, Q6).
- **EDSM upload check for the walker.** The EDSM upload-status row of `exploration_value.py` covers whether the current navigation target is known to EDSM (via `FSDTarget`), independent of the boxel walk.

## 3. Architecture

All modules are in `plugin/`. `PANEL_PLACEMENT = "exploration"` for the top-level entry point.

| Module | Role |
|---|---|
| `boxel.py` | Pure procedural-name parsing and single-boxel sequence math (section 4). No EDMC imports. Tests: `tests/test_boxel.py`. |
| `boxel_walker.py` | `BoxelWalker`: advance, retreat and `on_jump` state machine for one boxel, with a locally visited set and the bound `MAX_SKIP_STEPS` (1000). Mode-independent: Region Sweep uses one instance per queued cube (section 3.2). |
| `boxel_state.py` | JSON persistence of the position and visited set of the Sequence walker, per commander (section 8). |
| `visited_systems.py` | The per-commander log of every system arrived at, and the start-up journal catch-up for jumps made while EDMC was closed (sections 4.4.1, 8). |
| `survey_log.py` | Log of notable finds (Earthlike, water, ammonia, terraformable, biological), keyed by system and rolled up by boxel. Pure. Tests: `tests/test_survey_log.py`. |
| `survey_catchup.py` | Replays recent journals into the survey log for scans made while EDMC was closed (section 4.4.1). Tests: `tests/test_survey_catchup.py`. |
| `undiscovered_nearby.py` | The Spansh lookup, list filtering and in-memory cache of the Random button (section 4.4.1). |
| `edsm_client.py` | Shared EDSM API client (also used by Mine mode): `nearby_systems` (cube-systems), `system_known` (Tier 2), `system_fully_scanned` (Tier 3), `system_bodies`, `systems_coords`. Does not raise; every failure degrades to an empty or None result (section 7). |
| `region_sweep_queue.py` | Pure logic of Region Sweep: `CubeEntry` and `RegionSweepQueue`, one `BoxelWalker` per queued cube, completion tracking, "mark empty" (section 3.2). Tests: `tests/test_region_sweep_queue.py`, which installs a fake `config` module into `sys.modules` because `boxel_walker.py` imports the EDMC `config` (section 6). |
| `region_sweep_state.py` | JSON persistence of the Region Sweep queue. |
| `region_sweep_spansh.py` | Wrapper for the Spansh systems typeahead (section 7). Raises on failure, unlike `edsm_client.py`. |
| `region_sweep_panel.py` | `RegionSweepController`: widgets, worker-thread, `queue.Queue` and `after()` EDSM and Spansh lookups, and its Settings section (the "Region Sweep" section of the Boxel Survey page). |
| `waypoint_route.py` | Pure logic of Waypoint Route: `Waypoint` and `WaypointRoute`, add, remove and manual move, greedy nearest-neighbor reordering, CSV import, and import of the plotted route (`parse_navroute`, `add_systems`, from `NavRoute.json`). Tests: `tests/test_waypoint_route.py`, using the same try/except ImportError fallback as `survey_log.py`. |
| `waypoint_route_state.py` | JSON persistence of the Waypoint Route list. |
| `waypoint_route_panel.py` | `WaypointRouteController`: widgets, worker-thread bulk EDSM coordinate lookup for reordering, and its Settings section (the "Waypoint Route" section of the Boxel Survey page). |
| `boxel_survey.py` | `BoxelSurveyController`: the entry point of the feature-module contract (`PANEL_PLACEMENT = "exploration"`). Owns the Sequence / Region Sweep / Waypoints toggle, passes journal events to all three sub-controllers unconditionally (only the active one acts, through its own `.active` flag), and builds the main-panel widgets and Settings tab for Sequence plus the shared Export Survey Log control. |

### 3.1 Threading

- `journal_entry` and UI callbacks run on the Tk main thread.
- Every EDSM or Spansh HTTP call runs on a daemon `threading.Thread`, which puts its result on a `queue.Queue`.
- A `parent.after(200, ...)` poll on the main thread drains the queue and updates widgets.
- No worker thread accesses a Tk widget.

`BoxelWalker` is not internally thread-safe. Every access goes through `BoxelSurveyController._walker_lock`, because the walker is changed from both the Tk main thread and the Tier 2 and 3 EDSM skip-check worker thread.

### 3.2 Sub-modes

Boxel Survey is one panel with a button-row toggle (`_SUBMODE_SEQUENCE`, `_SUBMODE_REGION_SWEEP`, `_SUBMODE_WAYPOINTS`, stored as `wfmt_boxel_submode`), using the same button-row and `grid_remove` pattern as the mode row of `ui.py`.

- All three sub-controllers receive every journal event (`handle_event` in `boxel_survey.py`).
- Only the `.active` flag of the active controller gates its side effects, so switching sub-modes mid-session does not start either of the other two.

**Sequence** walks the flat number sequence of one boxel (section 4). Functions: Set, Next, Prev, Copy; **Use Current** (seeds from the live journal `system`); **Find Nearby (EDSM)** (section 4.4); and an automatic EDSM fallback after 3 consecutive Next clicks without a confirmed jump (section 4.5).

**Region Sweep** tracks completion across a user-curated queue of cubes.

- Each `CubeEntry` (sector, cube_id, mass_code) owns one `BoxelWalker` for its within-cube advance and retreat, a `systems: {name: complete}` dictionary and an `empty` flag.
- A cube is `complete` when every known system in it is marked complete, or when it is explicitly marked empty.
- "Known" is bounded by what EDSM, Spansh and the visited set of the session have returned. It is never a true total, because WFMT has no id64 math to determine the real system count of a cube (section 4.3).
- Cubes are added only from external sources: a typed seed, an EDSM nearby-systems result, or the Spansh typeahead. The module does not generate a "next cube" itself, in line with the reverted `next_boxel` attempt of Sequence (section 4.3).

**Waypoint Route** is a general point-to-point route tool for arbitrary systems (named by hand or procedural), not specific to boxels. It is the one place in Boxel Survey that requires real coordinates, because nearest-neighbor reordering needs distances. The coordinates always come from a live `edsm_client.systems_coords()` bulk lookup, triggered by an explicit "Reorder" click. They are never computed locally and never requested automatically per jump.

### 3.3 EDMC integration points

- `handle_event(entry, cmdr, system, station, state)`:
  - `FSDJump` and `Location` go to `BoxelWalker.on_jump` (Sequence), to the walker of each active `CubeEntry` (Region Sweep), or to the route position (Waypoints).
  - `Scan`, `FSSBodySignals` and `SAASignalsFound` go to `survey_log.py` (recording of notable finds, all sub-modes), keyed by the boxel of the live system and not by the target of the walker, so the record stays accurate when the commander leaves the sequence.
  - The "require a full FSS scan" condition of Region Sweep is decided by `FSSAllBodiesFound` (journal only). EDSM is not queried after a scan.
- `build_panel(parent)` builds the main-panel widgets, per the feature-module contract.
- `build_settings(notebook)` and `save_settings()` build the "Boxel Survey" Settings page (the toggles of Sequence, Export Survey Log and the settings of the Random button). The settings of Region Sweep and Waypoint Route are sections of the same page, so there is no separate Region Sweep or Waypoint Route tab.

## 4. The procedural-name sequence

### 4.1 Name structure

Procedurally generated system names have this form:

```
<sector words> <LL-L> <mass-code><N1>[-<N2>]
```

Examples: `Nyeajaae ZE-A d106` and `Vegnue WK-E d12-329`.

- `<LL-L>` is a cube identifier within the sector.
- `<mass-code>` is a single letter from `a` to `h`.
- The trailing number is the index of the system within that boxel (cube and mass code): a plain integer (`<N1>`) or an `<N1>-<N2>` pair.

`<N1>` and `<N2>` are not a fixed-width counter pair. `<N2>` does not carry into `<N1>` at any small boundary. Real secondary values such as `d3-5660` and `c13-670` occur, so walking `<N2>` and moving to a different `<N1>` are unrelated actions. `next_in_sequence` and `previous_in_sequence` in `boxel.py` change only `<N2>` (when present) or `<N1>` (when the name has no `<N2>`), never both, and there is no carry.

The Sequence walker can run out of existing candidates after a few Next steps. Section 4.5 describes how this is detected and handled.

### 4.2 Limits of `boxel.py`

`boxel.py` does not decode names into galactic x/y/z coordinates and does not know how many systems a boxel contains. It parses the string shape and walks the trailing number, generating a candidate name. The in-game galaxy map confirms whether the candidate exists. This avoids the full id64 and coordinate decode problem for the "walk one boxel" use case.

### 4.3 The reverted `next_boxel` action

An early version of the walker (described in the module docstring of `boxel.py`) implemented an explicit "next boxel" action as a string operation: `<N1>+1` with `<N2>` dropped.

- Field test from a real position (seeded at `Sifi CH-Y b42-5`): the resulting candidates (`b43` to `b45`) had no matches near the commander's position.
- The spatially neighboring boxels visible on the galaxy map from that position had different cube IDs (`Sifi AV-G`, `Sifi BB-M`), not `Sifi CH-Y` with a changed number.
- The action was reverted.

The result shows that `<N1>` is not an axis of the same kind as `<N2>` at a coarser scale. Moving to a spatially adjacent boxel requires coordinate or id64 math, which a string increment cannot provide.

### 4.4 EDSM for spatial neighbors

Because a string increment cannot find a neighboring boxel (section 4.3), WFMT queries the public EDSM endpoint `https://www.edsm.net/api-v1/cube-systems?x=...&y=...&z=...&size=...`, centered on the `StarPos` from the journal, for real systems near the commander. No id64 or coordinate decode math is involved.

`edsm_client.nearby_systems()` and the **Find Nearby (EDSM)** button:

- Query a cube of 100 ly (`DEFAULT_CUBE_SIZE`) around the live `StarPos`.
- Filter to procedural-shaped names in a `cube_id` different from the current seed.
- Offer the nearest match.

### 4.4.1 The Random button

The button is labeled **Random** (tooltip "Random - find an undiscovered system near you ..."). It is outside the Boxel Survey panel and does not use `BoxelWalker`.

- `ui.py` adds it to the Exploration button row (Auto-Honk, Discovery Alerts, Neutron Star, White Dwarf, Random) through `build_random_button()`, with a gray status line below the row.
- It is visible when Boxel Survey is collapsed and is independent of the selected sub-mode.

One click:

- `undiscovered_nearby.fetch_nearby()` runs against the live `StarPos`: a Spansh `POST /api/systems/search` with `reference_coords` and a nearest-first distance sort. The number of systems requested is `wfmt_boxel_random_count` (default 25, clamped to 10 to 100 by `random_count()`).
- `unscanned()` keeps entries whose `body_count` is `None` or 0 and removes names in the visited-systems log and the current system.
- `pick_order()` shuffles the nearest 8 (`POOL_SIZE`) and leaves the rest nearest first.
- The worker then calls `edsm_client.system_bodies()` for each in turn (at most `RANDOM_MAX_CONFIRMATIONS`, 6) and takes the first with an empty bodies list.

Caching and failures:

- `undiscovered_nearby.NearbyCache` keeps the fetched list in memory (10 minutes, 5 ly from the fetch position, same request size). Names offered or found scanned are marked used. An exhausted list triggers a new fetch.
- The EDSM check is always made fresh.
- A `None` from EDSM (failed lookup) keeps the Spansh result, and the status line states that EDSM was unreachable.
- A Spansh failure copies nothing.
- The name is copied to the clipboard. Nothing is set as a seed or target.

Every offered name is a system that a service lists, so the string-guessing limits of sections 4.2 and 4.3 do not apply. The remaining limit is the meaning of "undiscovered": the Spansh `body_count` is empty when no scan was submitted, which does not show that nobody visited.

Names are not generated by offsetting the trailing numbers of nearby boxel names and keeping those unknown to EDSM. "Not in EDSM" cannot distinguish an unvisited system from a name that was never real. Only a list of real systems can.

**Visited-systems log (`visited_systems.py`).** A listing without scans cannot show whether this commander has already visited a candidate: a visit without a scan leaves no trace on Spansh or EDSM, and EDSM synchronization can lag by minutes.

- `BoxelSurveyController` records every arrival (`StarSystem` of `FSDJump` and `Location`) into a per-commander `Set[str]`, unconditionally. The internal `_visited` of `BoxelWalker` is filled only while Sequence is the active sub-mode and serves only the skip-visited advance of that walker.
- The set is stored in `visited_systems.json` (case-preserved, case-insensitive matching, atomic write per commander, same form as `boxel_state.py`), loaded and saved by the `_switch_cmdr()` and `stop()` hooks.
- The Random worker thread checks a candidate against an immutable `frozenset` snapshot of this log before making an EDSM call. A hit is skipped without a call.
- Settings → Boxel Survey shows a live count and a **Clear Visited Systems Log** button (confirmed through `dialogs.confirm`, the convention of `mining_hotspot_import_export.py`). Clearing removes the log per commander and does not affect the survey progress of any sub-mode.

**Catch-up after EDMC was closed.** EDMC does not replay jumps made while it was not running.

- The first time a commander is seen in a run, a worker thread reads the last `visited_systems.CATCH_UP_DAYS` (14) days of journals (`visited_systems.arrivals_since`, through the shared `journal_files.py`) for the `FSDJump` and `Location` arrivals of that commander.
- The Tk thread merges them into the set (`_poll_visited_catchup`). The merge is a set union, so no watermark is needed and running it at every start is harmless.
- Jumps older than the window, made while EDMC was closed, are not found.

The survey log (section 5a) is caught up by the same worker (`survey_catchup.read_since`, applied on the Tk thread in `_poll_visited_catchup` by `survey_catchup.apply`), with restrictions, because its `bodies_scanned` counter is not idempotent:

- Notable finds are keyed by body name and merge without effect on repetition, so they are recovered for every system.
- The scanned count is set only for a system the log did not have before the run (one count per distinct body, `record_scan(count=...)`). A system already in the log keeps its count.
- A second run adds nothing, because the systems of the first run are then already in the log.
- The system of a signal event (which names none) is taken from the `FSDJump`, `Location` or `CarrierJump` before it. A `Scan` names its own system.
- The first-seen time of a recovered system is the time of the journal event.
- The journals are only read.

### 4.5 Sequence mode running out of candidates

A boxel can have few existing systems, so Sequence mode can run out of reachable candidates after a few steps. A precomputed breadth-first queue of spatially neighboring boxels would require id64 math, which is not implemented (see the stride table below).

WFMT detects the symptom directly:

- `boxel_survey.py` counts consecutive manual Next clicks without a confirmed jump (`_consecutive_skips`, `AUTO_SUGGEST_SKIP_THRESHOLD = 3`). This is the only observable signal, because the journal has no event for "the galaxy map could not plot this" (section 6, E1 and E2).
- After 3 in a row, it runs the same EDSM `cube-systems` lookup as Find Nearby and places the nearest real system in the seed field with an explanatory status message. **Set** continues there.
- The counter is reset by a confirmed jump, an explicit seed set, Prev, or a commander switch.

### 4.6 Region Sweep auto-discover

`RegionSweepQueue.advance_cube()` continues to the next incomplete, non-empty cube when the current cube completes. This requires the queue not to run empty.

The option **Auto-discover more nearby cubes (EDSM) when the queue is running low** (Settings → Exploration → Boxel Survey, Region Sweep section, default off, `wfmt_boxel_sweep_auto_discover`) adds cubes:

- After every jump while Region Sweep is active, `RegionSweepController._maybe_auto_discover()` counts the queued cubes with incomplete work (`_AUTO_DISCOVER_LOW_WATER_MARK = 1`).
- At or below that count, it runs the same EDSM `cube-systems` lookup as **Discover Nearby Cubes (EDSM)** (section 3.2) and merges the new cubes into the queue.
- An in-flight guard (`_auto_discover_inflight`) prevents a second jump from starting a duplicate lookup before the first answer arrives.

The function uses EDSM spatial data and no id64 math (section 4.4). Limits:

- It adds 1 to 2 cubes at a time through live network calls, so a gap can occur at the completion of a cube if EDSM responds slowly.
- It uses the 100 ly search radius of `cube-systems`. It is not a targeted "next unexplored boxel" query.

### 4.7 Mass-code and id64 stride

The stride between adjacent `<N2>` values (`next_id64 = id64 + CurrentN2 * stride`) is recorded for two mass codes:

| Mass code | Stride | Basis |
|---|---|---|
| d | 34359738368 (2³⁵) | `tests/test_boxel.py`, `test_real_boxel_survey_data_matches_stride_arithmetic`: id64 10057927091 (d5-0) plus 24 steps equals 834691647923 |
| e | 4294967296 (2³²) | Recorded in the earlier version of this document. No test covers it. |

The strides of the other mass codes have not been determined.

## 5. Visited and skip filtering tiers

Three tiers, cheapest first. All are implemented.

1. **Locally visited:** systems arrived at this session (`BoxelWalker._visited`, fed from `FSDJump` and `Location`). No network call. Persisted across restarts (section 8).
2. **Visited by anyone (EDSM):** `edsm_client.system_known()`, a per-name lookup. Opt-in (default off). Adds a network call per candidate.
3. **Fully scanned in EDSM:** `edsm_client.system_fully_scanned()`, comparing the `bodyCount` field of the `api-system-v1/bodies` endpoint (total known bodies) with the `bodies` returned. Opt-in. More expensive than Tier 2. Tier 2 runs first and ends Tier 3 once it confirms a skip (`_edsm_skip_check()`).

Both EDSM tiers use one convention: `None` means "could not be determined" (network or parse failure, EDSM unavailable, or no data on file) and is never treated as "not visited" or "not scanned". A temporary outage therefore does not withhold a valid candidate. The settings of Region Sweep (`wfmt_boxel_sweep_*`) mirror tiers 1 and 2 of Sequence and add a "require full FSS" option.

## 5a. Survey log (notable finds)

The survey log records what was found. It is separate from visited and skip filtering.

- `survey_log.py` `SurveyLog`, keyed by system name, one log per commander in `survey_log.json` (`commander_data.py`; `load_log(plugin_dir, cmdr)` and `save_log(plugin_dir, cmdr, log)`).
- The controller loads the log of the active commander in `_switch_cmdr` and saves the previous one first.
- A log in the earlier single shared shape is claimed by the first commander seen. The claim is saved immediately, so a second commander cannot claim it.
- The CSV export contains the rows of the active commander.
- The log holds `bodies_scanned` (every `Scan` event counts, regardless of notability) and a dictionary of notable bodies only. It is a list of highlights and not a full per-body log.
- A notable body has a `tags` list (`elw`, `ww`, `aw`, `terraformable`, `bio`; several can apply) plus `planet_class`, `distance_ls` and `bio_signal_count`.
- Classification: `PlanetClass` of `"Earthlike body"`, `"Water world"` or `"Ammonia world"` gives `elw`, `ww` or `aw`. `TerraformState == "Terraformable"` gives `terraformable` (independent of class). Any `FSSBodySignals` or `SAASignalsFound` signal with `Type == "$SAA_SignalType_Biological;"` and `Count > 0` gives `bio` and the count.
- `boxel_stats(key)` aggregates on demand from the stored rows. No cached totals are kept.

The stats line of the main panel reflects the boxel of the live journal `system`, not the current target of the walker, so it stays accurate when the commander is off-sequence. **Export Survey Log** (Settings → Boxel Survey) writes every notable-body row to the fixed-path CSV `boxel_survey_export.csv` in the plugin directory.

## 6. Known gaps

- **No precomputed multi-boxel queue.**
  - The auto-suggest of Sequence (section 4.5) and the auto-discover of Region Sweep (section 4.6) use live EDSM lookups.
  - `advance_cube()` (section 3.2) gives Region Sweep multi-cube continuity once its queue is populated.
  - Precomputing many boxels would require the id64 stride table (section 4.7) or a live breadth-first EDSM or Spansh search.
- **E1: no visibility into whether a candidate resolves in-game.** Boxel Survey learns about the game only through the EDMC journal feed, which has no event for "the galaxy map could not plot this". Closing the gap would require OCR or pixel reading (outside the scope) or checking every candidate against EDSM before display. EDSM confirms visited systems only, so that check would not close the gap.
- **E2: a dead candidate leaves the walker parked** until the commander steps past it with Next or Prev (or the auto-suggest of section 4.5 fires after 3 in a row). The cause is E1.
- **E3: a resolved candidate can be displayed under a different name in the game.** The procedural string still resolves for search and plot, so sequence walking is not affected. The cause has not been determined. It matters for any feature that verifies a candidate against EDSM by display name.
- **E4: arrival at a renamed candidate may not trigger auto-advance.**
  - `on_jump()` advances only when the `StarSystem` string of the journal matches the stored procedural candidate. WFMT has no `SystemAddress` tracking to match on instead.
  - The option **Confirm off-sequence arrivals against EDSM** (Settings → Boxel Survey, default off, `wfmt_boxel_confirm_alias_arrival`) treats a non-matching arrival as a possible E3 case.
  - `BoxelSurveyController._maybe_confirm_alias_arrival()` resolves the real coordinates of the pending target through `edsm_client.systems_coords()` and compares them with the `StarPos` of the arrival.
  - A match within `ALIAS_ARRIVAL_COORD_TOLERANCE_LY` (0.5 ly) is treated as arrival at the target under a different name. The walker advances and a status message names both systems.
  - The option is opt-in because it sends an EDSM lookup on every off-sequence jump while a target is pending, including jumps unrelated to the boxel.
  - The function has not been verified in the game with a renamed candidate.
- **Q6: suggesting a promising unsurveyed boxel is not buildable.** Systems are generated on demand from the address, and no published method predicts body composition before an in-game scan. EDSM coverage density as a proxy for "unexplored" has not been attempted.
- **Q5: no documented public API for DSSA or IGAU fleet-carrier locations.** A "nearest carrier" feature was ruled out.
- **Test coverage.**
  - `tests/test_region_sweep_queue.py` covers the queue of Region Sweep: cube add and remove, reseeding, completion tracking, `advance_cube()` skip, wrap and exhaustion, `on_jump()` including the multi-cube path, stats, and snapshot and restore round trips. It installs a minimal fake `config` module before importing, because `boxel_walker.py` imports the EDMC `config` at the top.
  - `boxel_walker.py` has no standalone test, only indirect coverage through that file and `test_boxel.py`.

## 7. External APIs

| Service | Use | Notes |
|---|---|---|
| EDSM `cube-systems` | Spatial query of nearby systems by x/y/z (sections 4.4, 4.5) | `edsm_client.nearby_systems()`. The server caps the cube edge at 200 ly. WFMT queries 100 ly. |
| EDSM `system` | Tier 2 visited-by-anyone check | `edsm_client.system_known()`. Tri-state `True`, `False`, `None`. |
| EDSM `api-system-v1/bodies` | Tier 3 fully-scanned check of Sequence; shared with the ring-reserve lookup of Mining | `edsm_client.system_fully_scanned()` and `system_bodies()`. The "require a full FSS scan" condition of Region Sweep does not use it; that comes from `FSSAllBodiesFound` in the journal. |
| EDSM `systems` (bulk) | Coordinates for the nearest-neighbor reordering of Waypoint Route | `edsm_client.systems_coords()`. One request for the whole list. |
| Spansh systems typeahead | Cube-completion discovery of Region Sweep | `region_sweep_spansh.py`. Undocumented endpoint, confirmed empirically. Raises on failure, unlike `edsm_client`. |

Every call identifies WFMT in its `User-Agent` (see `http_identity.py`). The EDSM client sends the `config.user_agent` of EDMC followed by that of WFMT, because EDSM rejects the default User-Agent of `requests` with a 403. Call volume is described in [TECHNICAL.md](TECHNICAL.md#keeping-api-traffic-low).

## 8. Persistence

Per-commander JSON files in the plugin directory (not the EDMC `config` store, which is intended for small scalars):

- `boxel_state.py`: seed, current position and visited set of the Sequence walker.
- `region_sweep_state.py`: the Region Sweep queue (all `CubeEntry` rows).
- `waypoint_route_state.py`: the Waypoint Route list.
- `visited_systems.py`: every system the commander has arrived at (`visited_systems.json`), caught up from the journals at start-up (section 4.4.1).
- `survey_log.py` `save_log` and `load_log`: the notable-finds log, per commander (`commander_data.py`). It is saved after every recorded finding and not only at `plugin_stop`, so scan findings are not lost in an ungraceful shutdown.

All files use the same atomic write (temporary file and `os.replace`), so a crash during a write cannot corrupt them. Small scalar preferences (autocopy, skip-visited toggles, sub-mode selection, collapsed state) use the EDMC `config` store through `wfmt_boxel_*` keys.

## 9. Testing

- `boxel.py`: unit tests against known system-name data (`tests/test_boxel.py`, including `test_real_boxel_survey_data_matches_stride_arithmetic`, which cross-checks the no-carry behavior of section 4.1).
- `survey_log.py`: classification, multi-tag merging, boxel aggregation, JSON round trip (`tests/test_survey_log.py`).
- `survey_catchup.py`: reading the scans of a commander from journals, the no-double-count rules (a system the log had, a repeated run, a body scanned twice), the system followed for signal events (`tests/test_survey_catchup.py`).
- `waypoint_route.py`: nearest-neighbor ordering against a known answer, CSV parsing edge cases, jump and target sequencing, mixed resolved, unresolved and visited reordering (`tests/test_waypoint_route.py`).
- `region_sweep_queue.py`: cube management, completion tracking, `advance_cube()` and `on_jump()` behavior including multi-cube continuity, stats and persistence round trips (`tests/test_region_sweep_queue.py`). The test installs a fake `config` module into `sys.modules` before the import. `boxel_walker.py` has no standalone unit test, only indirect coverage through this file and `test_boxel.py`.
- `visited_systems.py` catch-up: arrivals for the correct commander only (case-insensitive, `Commander` and `LoadGame`), old files skipped, missing folder (`tests/test_visited_catchup.py`).
- API clients (`edsm_client.py`, `region_sweep_spansh.py`): mocked, never live. A failed lookup gives `None` or empty and not a definite "no". The answer shapes (found, empty, unexpected) are distinguished. Every request carries the WFMT User-Agent and a timeout (`tests/test_boxel_clients.py`).
- UI (`boxel_survey.py`, `region_sweep_panel.py`, `waypoint_route_panel.py`): not covered by an automated test.
