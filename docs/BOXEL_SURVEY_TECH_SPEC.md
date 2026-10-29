# Boxel Survey technical specification

The standing reference for Boxel Survey across all three sub-modes (Sequence, Region Sweep, Waypoint
Route): what's true about the system right now, why, and what's still unknown. Release history is in
`CHANGELOG.md`.

- **Author:** R.W. Harper (CMDR Tiber Caelvox)
- **Status:** work in progress. Feedback, bug reports and suggestions are welcome: [open an issue](https://github.com/rwharpernc/wayfarers-multitool/issues).

**Design principle.**

- Like all of WFMT, this is journal-first: a third-party tool only knows what the game writes to its journal files, and not everything is logged.
- Gaps are filled from Frontier's own data or from community services where those exist, and otherwise worked around.
- Each gap and its workaround is written down.
- See [the design principle in TECHNICAL.md](TECHNICAL.md).

## 1. Goals

Help an explorer systematically survey a procedurally-generated boxel (subsector) without requiring a
separate application — integrated with EDMC's live journal stream so target advancement happens
automatically on jump, with clipboard automation for pasting into the in-game galaxy map search.

## 2. Non-goals

- No in-game screen overlay: WFMT's Boxel Survey draws nothing on the game screen (unlike Landing
  Assist and Inventory, which use `overlay.py`).
- No Frontier id64/coordinate decode math (see §4.3 — deliberately, not for lack of trying).
- No prediction of "which unvisited boxel is likely to have good finds" — checked and ruled out as
  unbuildable against any public data source (§6's carried-forward Q6).
- No galaxy-map-selection EDSM-upload check for the walker itself — `exploration_value.py`'s EDSM
  upload-status row already covers "is my current nav target known to EDSM" via `FSDTarget`,
  independent of the boxel walk.

## 3. Architecture

All modules live in `plugin/`, `PANEL_PLACEMENT = "exploration"` for the top-level entry point:

```
boxel.py                 Pure procedural-name parsing + single-boxel sequence math (§4). No EDMC
                          imports — unit-tested (tests/test_boxel.py).
boxel_walker.py           BoxelWalker: advance/retreat/on_jump state machine for one boxel, with a
                          locally-visited set and MAX_SKIP_STEPS bound. Mode-agnostic — Region Sweep
                          reuses one instance per queued cube (§3.2) rather than reimplementing it.
boxel_state.py            JSON persistence for the Sequence walker's position/visited set, per
                          commander (see §8).
visited_systems.py        The per-commander log of every system arrived at, plus the start-up journal
                          catch-up for jumps made while EDMC was closed (§4.4.1, §8).
survey_log.py             Notable-finds log (Earthlike/water/ammonia/terraformable/bio), keyed by
                          system and rolled up by boxel. Pure, unit-tested (tests/test_survey_log.py).
survey_catchup.py         Replays recent journals into the survey log for scans made while EDMC was
                          closed (§4.4.1). Unit-tested (tests/test_survey_catchup.py).
undiscovered_nearby.py    The RND button's Spansh lookup, list filtering and in-memory cache (§4.4.1).
edsm_client.py            Shared EDSM API client (also used by Mining mode) — nearby_systems
                          (cube-systems), system_known (Tier 2), system_fully_scanned (Tier 3),
                          system_bodies, systems_coords. Never raises; every failure degrades to an
                          empty/None result (§7).
region_sweep_queue.py     Pure logic for Region Sweep: CubeEntry/RegionSweepQueue, one BoxelWalker
                          per queued cube, completion tracking, "mark empty" (§3.2). Unit-tested
                          (tests/test_region_sweep_queue.py) via a fake config module
                          installed into sys.modules, working around the same config-import blocker
                          boxel_walker.py still has (§9).
region_sweep_state.py     JSON persistence for the Region Sweep queue.
region_sweep_spansh.py    Spansh systems-typeahead wrapper (§7) — raises on failure, unlike
                          edsm_client.py's convention.
region_sweep_panel.py     RegionSweepController — widgets, worker-thread/queue.Queue/after() EDSM+
                          Spansh lookups, its own Settings section (the "Region Sweep" section of the Boxel Survey page).
waypoint_route.py         Pure logic for Waypoint Route: Waypoint/WaypointRoute, add/remove/manual
                          move, greedy nearest-neighbor reordering, CSV import, the plotted-route import (`parse_navroute`, `add_systems`, from `NavRoute.json`). Unit-tested
                          (tests/test_waypoint_route.py) via the same try/except ImportError
                          fallback survey_log.py uses, so it doesn't need a live EDMC to import.
waypoint_route_state.py   JSON persistence for the Waypoint Route list.
waypoint_route_panel.py   WaypointRouteController — widgets, worker-thread bulk EDSM coordinate
                          lookup for reordering, its own Settings section (the "Waypoint Route" section of the Boxel Survey page).
boxel_survey.py           BoxelSurveyController — the feature-module contract entry point
                          (PANEL_PLACEMENT = "exploration"). Owns the Sequence/Region Sweep/Waypoints
                          toggle, fans journal events to all three sub-controllers unconditionally
                          (only the active one's controller acts, via its own `.active` flag), builds
                          the main-panel widgets and Settings tab for Sequence + the shared
                          Export-Survey-Log control.
```

### 3.1 Threading

Same rule everywhere in this project:

- `journal_entry`/UI callbacks run on the Tk main thread.
- Any EDSM/Spansh HTTP call is dispatched to a daemon `threading.Thread`, which puts its result on a
  `queue.Queue`.
- A `parent.after(200, ...)` poll on the main thread drains the queue and touches widgets.
- No worker thread ever touches a Tk widget directly.

`BoxelWalker` itself isn't internally thread-safe — every access goes through
`BoxelSurveyController._walker_lock` (mutated from both the Tk main thread and the Tier 2/3 EDSM
skip-check worker thread).

### 3.2 The three sub-modes

Boxel Survey is one panel with a button-row toggle (`_SUBMODE_SEQUENCE` / `_SUBMODE_REGION_SWEEP` /
`_SUBMODE_WAYPOINTS`, persisted as `wfmt_boxel_submode`), same button-row-plus-`grid_remove` pattern
`ui.py` itself uses for the Powerplay/Exploration/Mining/... mode row.

- All three sub-controllers receive every journal event unconditionally (`boxel_survey.py`'s
  `handle_event`).
- Only the active one's own `.active` flag gates its side effects, so switching sub-modes mid-session
  never starts either of the other two from nothing.

- **Sequence** — walks one boxel's flat number sequence (§4). Manual Set/Next/Prev/Copy, "Use
  Current" (seeds from the live journal `system`), "Find Nearby (EDSM)" (§4.4), and an automatic
  EDSM fallback after 3 consecutive Next clicks with no confirmed jump in between (§4.5).
- **Region Sweep** — tracks *completion* across a user-curated queue of cubes instead of one flat
  sequence.
  - Each `CubeEntry` (sector + cube_id + mass_code) owns one `BoxelWalker` for its own within-cube
    advance/retreat, plus a `systems: {name: complete}` dict and an `empty` flag.
  - A cube counts `complete` once every *known* system in it is marked complete, or once explicitly
    marked empty.
  - "Known" is bounded by whatever EDSM/Spansh/the session's own visited set have actually surfaced,
    never a true total (§4.3 applies here too: no id64 math means no way to know a cube's real system
    count).
  - Cubes are only ever added from real external sources (typed seed, EDSM nearby-systems result,
    Spansh typeahead). This module never invents a "next cube" itself, same principle as Sequence's own
    reverted `next_boxel` attempt (§4.3).
- **Waypoint Route** — a general point-to-point route tool for arbitrary systems (hand-named or
  procedural), not boxel-specific. The one place in Boxel Survey that genuinely needs real
  coordinates (nearest-neighbor reordering can't avoid distance math) — always from a live
  `edsm_client.systems_coords()` bulk lookup, triggered by an explicit "Reorder" click, never
  computed/guessed locally or run automatically per-jump.

### 3.3 EDMC integration points

- `handle_event(entry, cmdr, system, station, state)`:
  - `FSDJump`/`Location` → `BoxelWalker.on_jump` (Sequence) / each active `CubeEntry`'s own walker
    (Region Sweep) / route position (Waypoints).
  - `Scan`/`FSSBodySignals`/`SAASignalsFound` → `survey_log.py` (notable-finds recording, all
    sub-modes, keyed by whatever boxel the *live* system is in — not the walker's target, so it stays
    accurate even when the commander wanders off-sequence).
  - Region Sweep's "require a full FSS scan" is decided by `FSSAllBodiesFound` (journal only); it does
    not ask EDSM after a scan.
- `build_panel(parent)` → main-panel widgets, per the feature-module contract every WFMT mode module
  follows.
- `build_settings(notebook)` / `save_settings()` → the "Boxel Survey" Settings page (Sequence's own
  toggles + Export Survey Log + the Random button's settings). Region Sweep's and Waypoint Route's
  settings are built into the same page as sections under it (the Exploration tabs stack what one
  feature adds to a page), so there is no separate Region Sweep or Waypoint Route tab.

## 4. The procedural-name sequence algorithm

### 4.1 Confirmed structure

Elite's procedurally-generated system names follow:

```
<sector words> <LL-L> <mass-code><N1>[-<N2>]
```

e.g. `Nyeajaae ZE-A d106` or `Vegnue WK-E d12-329`. `<LL-L>` is a two-letter/one-letter cube
identifier within the sector; `<mass-code>` is a single letter `a`–`h`; the trailing number is the
system's index within that specific (cube, mass-code) boxel — either a plain integer (`<N1>`) or an
`<N1>-<N2>` pair.

**Boxel sizes by mass code** (confirmed by community decoding of the system and corroborating summaries; the
primary source text could not be fetched directly, so this doc gives the corroborated numbers):

| mass code | a | b | c | d | e | f | g | h |
|---|---|---|---|---|---|---|---|---|
| boxel size (ly) | 10 | 20 | 40 | 80 | 160 | 320 | 640 | 1280 |

Each proc-gen **sector** is a fixed 1280×1280×1280 ly cube.

- Mass code `h` boxels *are* the sector — exactly one `h` boxel per sector.
- Smaller mass codes subdivide that same volume more finely: many small `a` boxels tile the same space
  one huge `h` boxel covers, each with its own independent `<N1>[-<N2>]` numbering.

**This is the single most important fact for understanding why Sequence mode can "run dry" after only
a few hits**: a small mass-code boxel is a small volume, and correspondingly has few real systems in
it — reaching the end of its populated indices after 2-4 hits is normal, expected behavior for a boxel
that size, not a bug.

`<N1>` and `<N2>` are **not** a fixed-width counter pair — `<N2>` never carries into `<N1>` at any
small boundary. Real secondary values such as `d3-5660` and `c13-670` occur in practice, so walking
`<N2>` and moving to a different `<N1>` are unrelated actions. `boxel.py`'s `next_in_sequence`/`previous_in_sequence`
only ever move `<N2>` (when present) or `<N1>` (when the name has no `<N2>` at all) — never both, no
carry.

### 4.2 What `boxel.py` deliberately does NOT do

It does not decode names into galactic x/y/z coordinates, and does not know how many real systems a
given boxel actually contains. It only parses the string shape and walks the trailing number,
generating a candidate name and letting the in-game galaxy map confirm existence — not
computing coordinates itself (§4.4). This sidesteps the much
harder full id64/coordinate-decode problem entirely for the "walk one boxel" use case.

### 4.3 The reverted `next_boxel` attempt, and what it proved

An early version of the walker (still described in `boxel.py`'s own module docstring) implemented an
explicit "next boxel" action as a plain string move: `<N1>+1` with `<N2>` dropped.

- Field-tested from a real position (seeded at `Sifi CH-Y b42-5`): the resulting candidates
  (`b43`–`b45`) had no matches anywhere near the commander's actual location.
- The real neighboring boxels visible on the galaxy map from that exact position had entirely different
  cube IDs (`Sifi AV-G`, `Sifi BB-M`) — not `Sifi CH-Y` with a bumped number.
- **It was reverted.**

This falsifies the theory that `<N1>` is "the same kind of axis as `<N2>`, just coarser" — moving to a
real spatially-adjacent boxel needs actual coordinate/id64 math, which a string increment structurally
cannot provide.

### 4.4 Using EDSM for real spatial neighbors

Since a string increment can't find a real neighboring boxel (§4.3), WFMT asks EDSM which real systems
exist near the commander's actual position instead: its public
`https://www.edsm.net/api-v1/cube-systems?x=...&y=...&z=...&size=...` endpoint, centered on the
`StarPos` from the journal. No id64/coordinate-decode math is involved.

`edsm_client.nearby_systems()` + the "Find Nearby (EDSM)" button:

- Query a 100 ly cube (`DEFAULT_CUBE_SIZE`) around the live `StarPos`.
- Filter to procedural-shaped names in a different `cube_id` than the current seed.
- Offer the nearest match.

### 4.4.1 The "Random" button (RND)

Labeled **RND** (tooltip "Random"). It sits outside the Boxel Survey panel and never touches
`BoxelWalker`.

- `ui.py` adds it to the Exploration button row (A.H., D.A., N.S., W.D., RND) via
  `build_random_button()`, with its gray status line below that row.
- It is visible even when Boxel Survey is collapsed and independent of which of the three sub-modes is
  selected.

How one click works:

- It runs `undiscovered_nearby.fetch_nearby()` against the commander's live `StarPos`: a Spansh
  `POST /api/systems/search` with `reference_coords` and a nearest-first distance sort
  (`wfmt_boxel_random_count`, default 25, clamped to 10-100 by `random_count()`).
- `unscanned()` keeps entries whose `body_count` is `None` or 0 and drops names in the visited-systems
  log and the current system.
- `pick_order()` shuffles the nearest 8 and leaves the rest nearest first.
- The worker then asks `edsm_client.system_bodies()` for each in turn (at most
  `RANDOM_MAX_CONFIRMATIONS`, 6) and takes the first with an empty bodies list.

Caching and failures:

- `undiscovered_nearby.NearbyCache` keeps the fetched list in memory (10 minutes, 5 ly from the fetch
  position, same request size). Names offered or found scanned are marked used, and an exhausted list
  triggers a new fetch.
- The EDSM check always runs fresh.
- A `None` from EDSM (lookup failed) keeps the Spansh result and the status line says EDSM was
  unreachable.
- A Spansh failure copies nothing.
- The name goes to the clipboard; nothing is set as a seed or target.

Every offered name is a system a service lists, so the string-guessing limits of §4.2/4.3 do not apply
to RND. The limit that remains is the meaning of "undiscovered": Spansh's `body_count` is empty when
no scan was submitted, which is not proof that nobody visited.

Names are not made by offsetting the trailing numbers of a nearby boxel's names and keeping those EDSM
does not know, because the boxel number is part of a system's identity, so such names almost never
exist. *Why:* "not in EDSM" cannot distinguish an unvisited system from a name that was never real;
only a list of real systems can.

**The visited-systems log (`visited_systems.py`)** closes a second false-positive gap:

- A scan-less listing alone can't tell whether *this commander* has already been to a candidate — a
  visit without a scan leaves no trace on Spansh or EDSM, and EDSM sync can lag by minutes — so a
  system genuinely visited could still come back with no scans and get suggested again as if new.
- `BoxelSurveyController` records every real arrival (`FSDJump`/`Location`'s `StarSystem`) into a
  per-commander `Set[str]`, unconditionally — unlike `BoxelWalker`'s own internal `_visited` (only
  populated while Sequence is the active sub-mode, and scoped to driving that walker's own
  skip-visited advance).
- The set is persisted to `visited_systems.json` (same case-preserved/case-insensitive,
  atomic-write-per-commander shape as `boxel_state.py`, loaded/saved on the same `_switch_cmdr()`/
  `stop()` hooks).
- The Random worker thread checks a candidate against an immutable `frozenset` snapshot of this log
  *before* spending an EDSM call on it — a hit skips for free.
- Settings → Boxel Survey shows a live count and a "Clear Visited Systems Log" button (confirmed via
  `dialogs.confirm`, the same confirmation convention `mining_hotspot_import_export.py` already uses)
  for wiping it per-commander without affecting any sub-mode's own survey progress.

**Catching up after EDMC was closed.** EDMC does not replay jumps made while it was not running.

- The first time a commander is seen in a run, a worker thread reads the last
  `visited_systems.CATCH_UP_DAYS` (14) days of journals (`visited_systems.arrivals_since`, via the
  shared `journal_files.py`) for that commander's `FSDJump`/`Location` arrivals.
- The Tk thread merges them into the set (`_poll_visited_catchup`).
- It is a set union, so it needs no watermark and running it every start is harmless.
- Jumps older than the window, made with EDMC closed, are not found.

The survey log (§5a) is caught up by the same worker (`survey_catchup.read_since`, applied on the Tk
thread in `_poll_visited_catchup` by `survey_catchup.apply`), but conservatively, because its
`bodies_scanned` counter is not idempotent:

- The notable finds are keyed by body name and merge harmlessly, so they are recovered for every
  system.
- The scanned count is set only for a system the log did not have before the run (one count per
  distinct body, `record_scan(count=...)`), and a system already in the log keeps its count.
- A second run adds nothing, since the first run's systems are then "already in the log".
- The system of a signal event (which names none) is followed from the `FSDJump` / `Location` /
  `CarrierJump` before it; a `Scan` names its own.
- The first-seen time of a recovered system is the journal event's time.
- The journals are only read.

### 4.5 Sequence mode running dry, and how it is handled

A small mass-code boxel has few real systems in it (§4.1), so Sequence mode can run out of reachable
candidates after only a few hits. A fuller fix would precompute a breadth-first queue of spatially
neighboring boxels via id64 math, which this project has never derived (the mass-code→id64-stride
table below is only 2 of 8 letters confirmed).

WFMT instead **detects the symptom directly**:

- `boxel_survey.py` tracks consecutive manual Next clicks with no confirmed jump in between
  (`_consecutive_skips`, `AUTO_SUGGEST_SKIP_THRESHOLD = 3`) — the only observable signal available,
  since there's no journal event for "the galaxy map couldn't plot this" (see §6 E1/E2).
- After 3 in a row, it automatically runs the same EDSM `cube-systems` lookup "Find Nearby" already
  does and drops the nearest real system into the seed field with an explanatory status message — one
  click on **Set** to continue there.
- Reset on any confirmed jump, explicit seed set, Prev, or commander switch.

This treats the *symptom* (small boxel ran dry) rather than precomputing a queue — see §6 for what a
fuller fix would need.

### 4.6 Region Sweep's auto-discover

§4.5's Sequence-mode fix treats the symptom one boxel at a time; it never builds a *queue*. Region Sweep
(§3.2) has the missing piece structurally: `RegionSweepQueue.advance_cube()` auto-continues to the
next incomplete, non-empty cube once the current one completes — it just needed the queue to never run
empty.

**"Auto-discover more nearby cubes (EDSM) when the queue is running low"** (Settings → Exploration → Boxel Survey, Region Sweep section,
opt-in/default off, `wfmt_boxel_sweep_auto_discover`) closes that:

- After every jump while Region Sweep is active, `RegionSweepController._maybe_auto_discover()` checks
  how many queued cubes still have incomplete work (`_AUTO_DISCOVER_LOW_WATER_MARK = 1`).
- Once at or below that, it fires the exact same EDSM `cube-systems` lookup "Discover Nearby Cubes"
  already does (§3.2), merging any newly-found cubes straight into the queue.
- An in-flight guard (`_auto_discover_inflight`) stops a second jump from firing a duplicate lookup
  before the first one's response lands.

This is built entirely from real EDSM spatial data rather than id64 math, same principle as every other
spatial feature in this project (§4.4). Its limits:

- It reactively tops up 1-2 cubes at a time via live network calls, so there can be a brief gap right
  at a cube's completion if EDSM is slow to respond.
- It inherits `cube-systems`' 100 ly search radius rather than a targeted "next unexplored boxel"
  query.

Good enough to stop the queue from going empty during normal play; not a precomputed breadth-first
expansion.

### Mass-code → id64-stride table (still open)

Two data points are confirmed from real system names paired with their id64s: the stride between
adjacent `<N2>` values, computed as `next_id64 = id64 + CurrentN2 * stride`, is mass-code `d` →
`34359738368` (2³⁵) and mass-code `e` → `4294967296` (2³²). Both exact powers of two, 2³ apart for
adjacent mass-code letters — consistent with "3 bits of the 64-bit id64 reserved per mass-code step," but
only 2 of 8 letters are actually confirmed:

| mass code | a | b | c | d | e | f | g | h |
|---|---|---|---|---|---|---|---|---|
| predicted stride | 2⁴⁴ | 2⁴¹ | 2³⁸ | **2³⁵ (confirmed)** | **2³² (confirmed)** | 2²⁹ | 2²⁶ | 2²³ |

If this table is ever completed and trusted, it would let a future version track exact candidate id64s
(not just name strings) — the prerequisite for a real "next spatially-adjacent boxel" feature and for a
precomputed breadth-first queue instead of the reactive EDSM-fallback workaround in §4.5.

## 5. Visited/skip filtering tiers

Cheapest first — all three are implemented:

1. **Locally visited** — systems arrived at this session (`BoxelWalker._visited`, fed from
   `FSDJump`/`Location`). Free, no network call. Persisted across restarts (§8).
2. **Visited by anyone (EDSM)** — `edsm_client.system_known()`, a per-name lookup. Opt-in (default
   off) — adds a network call per candidate.
3. **Fully scanned in EDSM** — `edsm_client.system_fully_scanned()`, reusing the `api-system-v1/
   bodies` endpoint's `bodyCount` field (total known bodies) vs. the `bodies` actually returned.
   Opt-in, more expensive than Tier 2 (a heavier fetch) — Tier 2 runs first and short-circuits Tier 3
   once it already confirms a skip (`_edsm_skip_check()`).

Both EDSM tiers share one convention: `None` means "couldn't determine" (network/parse failure, EDSM
down, or EDSM has no data on file) and must **never** be treated as "not visited/not scanned" — a
temporary outage must never silently withhold a valid candidate. Region Sweep's own equivalent
settings (`wfmt_boxel_sweep_*`) mirror Sequence's tiers 1-2 plus its own "require full FSS" option.

## 5a. Survey log (notable finds)

Separate concern from visited/skip filtering — this is about *recording what was found*, not deciding
what to skip.

- `survey_log.py`'s `SurveyLog`, keyed by system name, **one log per commander** in `survey_log.json`
  (`commander_data.py`; `load_log(plugin_dir, cmdr)` / `save_log(plugin_dir, cmdr, log)`).
- The controller loads the active commander's log in `_switch_cmdr` and saves the previous one first.
- A log in the pre-per-commander (single shared) shape, if one is found, is claimed by the first
  commander seen (the claim is saved at once, so a second commander cannot claim it too).
- The CSV export holds the active commander's rows.

- `bodies_scanned` (every `Scan` event counts, regardless of notability) and a dict of **notable
  bodies only** — deliberately not a full per-body log, to stay a readable highlights list.
- A notable body carries a `tags` list (`elw`/`ww`/`aw`/`terraformable`/`bio`, can hold several at
  once) plus `planet_class`, `distance_ls`, `bio_signal_count`.
- Classification: `PlanetClass` of `"Earthlike body"`/`"Water world"`/`"Ammonia world"` →
  `elw`/`ww`/`aw`; `TerraformState == "Terraformable"` → `terraformable` (independent of class); any
  `FSSBodySignals`/`SAASignalsFound` signal with `Type == "$SAA_SignalType_Biological;"` and
  `Count > 0` → `bio` + count.
- `boxel_stats(key)` aggregates on demand from the stored rows — no cached totals to drift.

The main panel's stats line reflects whatever boxel the *live* journal `system` is in, not the
walker's current target — so it stays accurate even when the commander is off-sequence. **Export
Survey Log** (in Settings → Boxel Survey) writes every notable-body row to a fixed-path CSV
(`boxel_survey_export.csv`) in the plugin directory.

## 6. Known gaps / open questions

Assessed against the code.

- **A precomputed multi-boxel queue is still not built, only reactively approximated.**
  - Sequence mode's auto-suggest (§4.5) and Region Sweep's auto-discover (§4.6) close the practical
    "ran out of targets" complaint using live EDSM lookups.
  - `advance_cube()` (§3.2) already gives Region Sweep genuine multi-cube continuity once its queue is
    populated.
  - What's still missing is precomputing hundreds of boxels up front via id64 math, rather than
    reactively topping up 1-2 cubes at a time over the network right as they're needed.
  - Closing that gap for real needs either the completed id64-stride table above, or a heavier live
    breadth-first EDSM/Spansh search — lower priority because the reactive version works.
- **E1 — no visibility into whether a candidate actually resolves in-game.** Structural: Boxel
  Survey only learns about the world through EDMC's journal feed, which never fires for "the galaxy
  map couldn't plot this." No fix without OCR/pixel-scraping (out of scope) or cross-checking every
  candidate against EDSM before display (which only confirms *visited* systems, not unvisited-but-
  valid ones — doesn't fully close the gap either).
- **E2 — a dead candidate leaves the walker parked with no self-correction**, until the commander
  manually Next/Prevs past it (or, as of §4.5, the auto-suggest fires after 3 in a row). Not a bug —
  the only honest behavior available given E1.
- **E3 — a resolved candidate can display under a different "real" name in-game** (Kickstarter-
  backer naming rights, likely mechanism, unconfirmed for any specific observed case). Doesn't affect
  sequence-walking (the procedural string still round-trips correctly for search/plot), but matters
  if a future feature ever tries to verify a candidate against EDSM by display name.
- **E4 — arriving at a renamed candidate may not trigger auto-advance (opt-in fix available).**
  - `on_jump()` still only advances when the journal's `StarSystem` string-matches the stored
    procedural candidate exactly (unchanged — no id64/`SystemAddress` tracking exists to match on
    instead, per E3/§4.3).
  - Rather than requiring that, **"Confirm off-sequence arrivals against EDSM"** (Settings → Boxel
    Survey, opt-in/default off, `wfmt_boxel_confirm_alias_arrival`) treats a non-matching arrival as a
    possible E3 case.
  - `BoxelSurveyController._maybe_confirm_alias_arrival()` resolves the pending target's real
    coordinates via `edsm_client.systems_coords()` and compares them against the arrival's actual
    `StarPos` (already in every journal event).
  - A match within `ALIAS_ARRIVAL_COORD_TOLERANCE_LY` (0.5 ly — real neighboring procedural systems
    are practically always much further apart) is treated as "arrived at the target under a different
    name," advancing the walker and showing a status message identifying both names.
  - Opt-in because it fires an EDSM lookup on every off-sequence jump while a target is pending, not
    just genuine boxel candidates — a commander doing unrelated travel with Sequence mode still
    selected would otherwise generate background EDSM traffic they didn't ask for.
  - Still not re-confirmed against a live E3 case in-game (no real renamed-candidate arrival has been
    watched end to end) — the mechanism is sound given what §4.4 already establishes about EDSM
    coordinate data, but hasn't been field-verified end to end.
- **Q6 — "suggest a promising unsurveyed boxel" is not buildable.** Checked: Elite's systems are
  generated on demand by Stellar Forge from the address, with no published/reverse-engineered way to
  predict body composition before an in-game scan. The closest real signal (EDSM coverage density as
  a proxy for "unexplored") is unattempted and would need its own query design.
- **Q5 — no documented public API for DSSA/IGAU fleet-carrier locations**; a "nearest carrier" feature
  was checked and ruled out as not worth building against undocumented/scraped sources.
- **Test coverage.**
  - `tests/test_region_sweep_queue.py` covers Region Sweep's queue (cube add and remove, reseeding,
    completion tracking, `advance_cube()` skip, wrap and exhaustion, `on_jump()` including the
    multi-cube path, stats, and snapshot and restore round-trips).
  - It installs a minimal fake `config` module before importing, because `boxel_walker.py` imports
    EDMC's `config` at the top.
  - `boxel_walker.py` itself has no standalone test, only indirect coverage through that file and
    `test_boxel.py`.

## 7. External APIs

| Service | Use | Notes |
|---|---|---|
| EDSM `cube-systems` | spatial nearby-system query by x/y/z (§4.4, §4.5) | `edsm_client.nearby_systems()`; 200 ly server-side cap, WFMT queries 100 ly |
| EDSM `system` | Tier 2 visited-by-anyone check | `edsm_client.system_known()`; tri-state `True`/`False`/`None` |
| EDSM `api-system-v1/bodies` | Sequence's Tier 3 fully-scanned check, shared with Mining's ring-reserve lookup | `edsm_client.system_fully_scanned()`/`system_bodies()`. Region Sweep's "require a full FSS scan" does not use it: that comes from the journal's `FSSAllBodiesFound` |
| EDSM `systems` (bulk) | Waypoint Route's nearest-neighbor reordering coordinates | `edsm_client.systems_coords()`; one request for the whole list |
| Spansh systems typeahead | Region Sweep's cube-completion discovery | `region_sweep_spansh.py`; undocumented endpoint, confirmed empirically, raises on failure (unlike edsm_client's convention) |

Every call identifies WFMT in its `User-Agent` (see `http_identity.py`). EDSM's client sends EDMC's own
`config.user_agent` followed by WFMT's, because EDSM rejects `requests`' default UA with a 403. For how
call volume is kept down, see [TECHNICAL.md](TECHNICAL.md#keeping-api-traffic-low).

## 8. Persistence

Per-commander JSON files in the plugin's own directory (not EDMC's `config` store, which is meant for
small scalars):

- `boxel_state.py` — Sequence walker's seed/current/visited set.
- `region_sweep_state.py` — the Region Sweep queue (all `CubeEntry` rows).
- `waypoint_route_state.py` — the Waypoint Route list.
- `visited_systems.py` — every system the commander has arrived at (`visited_systems.json`), caught up from the
  journals at start-up (§4.4.1).
- `survey_log.py`'s `save_log`/`load_log` — the notable-finds log, per commander (`commander_data.py`), saved after every recorded finding
  (not just at `plugin_stop`), since scan findings are worth more than walker position and shouldn't
  be lost to an ungraceful shutdown.

All of them follow the same atomic-write pattern (temp file + `os.replace`) so a crash mid-write can't
corrupt them. Small scalar preferences (autocopy, skip-visited toggles, submode selection, collapsed
state) use EDMC's `config` store instead, via `wfmt_boxel_*` keys.

## 9. Testing strategy

- `boxel.py` — unit tests against known real system-name data (`tests/test_boxel.py`, includes
  `test_real_boxel_survey_data_matches_stride_arithmetic` cross-validating §4.1's no-carry finding).
- `survey_log.py` — classification, multi-tag merging, boxel aggregation, JSON round-trip
  (`tests/test_survey_log.py`).
- `survey_catchup.py` — reading a commander's scans from journals, the no-double-count rules (a system the log had, a repeated run,
  a body scanned twice), the system followed for signal events (`tests/test_survey_catchup.py`).
- `waypoint_route.py` — nearest-neighbor ordering against a known-correct answer, CSV parsing edge
  cases, jump/target sequencing, mixed resolved/unresolved/visited reordering
  (`tests/test_waypoint_route.py`).
- `region_sweep_queue.py` — cube management, completion tracking, `advance_cube()`/`on_jump()`
  behavior including multi-cube continuity, stats, and persistence round-trips
  (`tests/test_region_sweep_queue.py`) — works around the `config` import blocker via a
  fake `config` module installed into `sys.modules` before import, rather than changing production
  code (§6). `boxel_walker.py` itself still has no standalone unit test, only indirect coverage
  through this file and `test_boxel.py`.
- `visited_systems.py` catch-up — arrivals for the right commander only (case-insensitive, `Commander`/`LoadGame`),
  old files skipped, missing folder (`tests/test_visited_catchup.py`).
- API clients (`edsm_client.py`, `region_sweep_spansh.py`) — mocked, never live: a failed lookup gives `None`/empty rather
  than a confident "no", the answer shapes (found, empty, surprising) are told apart, and every request carries the WFMT
  User-Agent and a timeout (`tests/test_boxel_clients.py`). No test should hit live EDSM/Spansh.
- UI (`boxel_survey.py`, `region_sweep_panel.py`, `waypoint_route_panel.py`) — manual/live-EDMC
  testing only, same as every other WFMT feature module.
