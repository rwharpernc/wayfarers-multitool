# BGS tracking technical specification

This document specifies BGS tracking: which journal data is recorded, how actions are attributed to factions and systems, how a tick is detected, and the limits of the figures. Usage is described in the [BGS guide](guide/bgs.md). The general code organization is described in [TECHNICAL.md](TECHNICAL.md).

- **Author:** R.W. Harper (CMDR Mactavious)
- **Status:** work in progress. Feedback and bug reports: [open an issue](https://github.com/rwharpernc/wayfarers-multitool/issues).

WFMT is journal-first: it uses the information the game writes to its journal files and fills gaps from Frontier data or community services where they exist. Each gap and its workaround is documented. See [the design principle in TECHNICAL.md](TECHNICAL.md).

## 1. Scope

BGS tracking records what the commander does to the Background Simulation (BGS). Powerplay and Colonization are outside its scope.

- **Panel:** shows only the current system. For each faction it shows state and influence, with the change since before the tick, and the commander's actions against that faction in the current tick.
- **BGS Report window:** shows every other system in which the commander acted in the tick, one tab per system, and earlier ticks through a drop-down (the archive).
- **Recorded effects (increases and decreases):** missions completed (+/- INF pips), failed and abandoned missions, bounty and combat-bond redemptions, trade profit or loss, exploration data sold, and crimes committed against a faction. The faction's influence and state change since before the tick is also shown.
- **Per tick:** totals reset at each tick. The closed tick is archived for a configurable number of days (`wfmt_bgs_archive_days`, default 7, range 1 to 90). At start, the current period is rebuilt from the commander's recent journals, so it is cumulative since the tick even if EDMC was not running.
- **Report tabs:**
  - The last `RECENT_SYSTEMS` (6) systems visited (any system present in the period's faction data or with activity; the current system first), plus the commander's pinned systems (shown first, starred, in every period).
  - **Close tab** adds a system to `hidden_systems` and unpins it.
  - **Add system** (the "Show a system" box, a `SuggestEntry` with a drop-down of all known systems and type-ahead filtering; free text is accepted) pins the system and removes it from `hidden_systems`.
  - `pinned_systems` and `hidden_systems` are stored per commander in `bgs_state.json`.
  - Archived periods hold faction data only for systems with activity, so their recent list consists of those systems.
  - **Copy Summary** ignores the tab limit and the hidden list.
- **Persistence:** per commander, across a relog and an EDMC restart.
- Activity is recorded in whichever system the commander acts. There are no lists of tracked systems or factions.

### 1.1 Not included

- Discord posting was outside the original BGS feature. Since 2026-10-29 it is part of the shared Discord feature of WFMT (see [DISCORD_SHARING_RESEARCH.md](DISCORD_SHARING_RESEARCH.md)): **Copy for Discord** and **Post to Discord** operate on the tick shown in the report window (`bgs_discord.py`, `discord_share.py`). **Copy Summary** is separate plain text.
- Combat-zone participation as a signal of its own, and Thargoid war states (section 5).

## 2. Architecture

`PANEL_PLACEMENT = "bgs"`: BGS has its own top-level mode button (`PANEL_MODES` in `ui.py`, next to Powerplay).

| Module | Role |
|---|---|
| `bgs_tracker.py` | Pure parsing: `FactionSnapshot` / `parse_faction_entry()`, `FactionActivity`, `parse_mission_faction_effects()`, `parse_bounty_voucher()`, `parse_combat_bond()`, `parse_crime()`, `market_*()`, `exploration_sale_value()`. |
| `bgs_ledger.py` | Pure engine. `TickLedger` is one tick period for one commander: activity per system and faction; a `FactionTrack` per system and faction (`before` = last snapshot before the tick, `now` = newest since); open missions (`MissionID` to issuing faction, for scoring failed and abandoned missions); the commander's location and the faction of the station docked at. `process(entry)` accepts a live or replayed journal entry. Entries older than `tick_start` update context and `before` but never count as activity. `roll()` closes the period into an archive record and starts the next (each faction's newest snapshot becomes the next `before`). Also `PeriodView` (read-only view for the window), `prune_archive()`, `rebuild()` and `fingerprint()`. |
| `bgs_journal.py` | Reads the commander's recent `Journal*.log` files, starting `LOOKBACK_DAYS` (3) before the tick, and returns the relevant events, filtered by the `Commander` event of each file. |
| `bgs_format.py` | Shared wording (panel, window, Copy Summary). Clips every journal-sourced name. |
| `bgs_state.py` | Per-commander JSON (`bgs_state.json`): `ledger` (current period) and `archive` (closed periods, newest first). Written to a temporary file and moved with `os.replace`. |
| `bgs_tick_client.py` | Synchronous HTTP client, the only network call: `fetch_latest_tick()`. |
| `bgs_panel.py` | Controller, main-panel widgets and the Settings tab (a note pointing to the Online tab, where tick detection is switched). Feeds live events to the ledger, polls the tick (`queue.Queue`, generation counter, `threading.Thread`, `after()`), runs the journal replay on a worker thread, and archives on a new tick. |
| `bgs_settings.py` | The Settings card of the Report window and the config keys and readers for the display switch and the days of ticks kept (see "Settings in the report window"). |
| `bgs_window.py` | Report window (`uikit`): a tick drop-down and one tab per system, each with a table of factions and a table of the commander's actions. Tabs are the last 6 systems plus the pinned ones. |

### 2.1 Tick lifecycle

1. A journal event identifies the commander (`_switch_cmdr` loads the saved ledger and archive).
2. The tick poll returns the latest galaxy tick `T`. When both are known, `_reconcile_tick()` runs:
   - If the stored `tick_start` is older than `T` (a tick passed, possibly while EDMC was closed), the stored period is archived, a new period starts at `T`, and a repair is queued (`_repair`: the closing period's start, `T`, and the missions open at that time).
   - If no `tick_start` is stored, `T` is adopted.
3. `_start_backfill()` (once per commander and tick per session) replays the journals on a worker thread into a new `TickLedger`. Live events arriving during the replay are buffered. When the replay finishes they are applied on top, skipping events the replay already saw (matched by `fingerprint()`). If no journal events are found (folder unset or unreadable), the live ledger is kept unchanged.

   **Repair.** The same worker read serves the repair:
   - It reads from the start of the closing period.
   - `bgs_ledger.repair_record(events, old_start, T, open_missions)` replays only the events before `T` into that period (events before its start establish state but never count) and returns an archive record. It returns None if the journals show no activity, if the times cannot be read, or if the period began more than `REPAIR_MAX_DAYS` (14) days ago.
   - `_apply_repair` merges the record into the live record with the same start and end through `bgs_ledger.merge_records` (the rebuilt activity and tracks win per faction; a faction present only in the live record is kept), or adds the record when none was filed live.
   - The repair is applied regardless of the outcome of the replay of the current period, but only if the commander is still the one it was built for.
   - Ticks missed entirely cannot be separated; the activity of those ticks is stored in one record.
4. At later ticks while running, step 2 is repeated, followed by a new replay.

If tick detection is off or unreachable and no tick was ever stored, there is no period boundary: the ledger accumulates live events and no replay occurs.

Archive limits: ledgers keep `before` baselines for factions seen within the archive-days window (`prune_tracks`). Archived periods keep faction tracks only for systems with activity.

## 3. Journal fields

### 3.1 Faction-state snapshot

`FSDJump`, `Location` and `CarrierJump` events contain:

- `StarSystem` (string): used in preference to the `system` argument that EDMC passes to `handle_event`, which is the fallback.
- `SystemFaction: {Name, FactionState}`: the system's current controller, used only to set `is_controlling` on the matching faction's snapshot.
- `Factions: [...]`: one entry per minor faction present, with `Name`, `FactionState`, `Government`, `Allegiance`, `Influence` (a fraction from 0.0 to 1.0, displayed ×100 as a percentage), `Happiness` / `Happiness_Localised`, `PendingStates: [{State, Trend}]`, `RecoveringStates: [...]` and `ActiveStates: [{State}]`.

Every faction present is stored on the ledger as a `FactionTrack`:

- A sighting before the tick replaces `before`. A sighting since the tick replaces `now`.
- Snapshots are overwritten completely, never merged field by field, because the journal always sends the complete current state of a faction.
- The influence change shown is `now - before` in percentage points. It is blank when either end is unknown (for example a system first seen after the tick with no earlier journal record).

### 3.2 Mission influence

`MissionCompleted` contains `FactionEffects[]`. Each entry has `Faction` and `Influence[]`, an array of `{Trend, Influence}`. `Influence` is a string of `+` or `-` characters; the journal contains no exact percentage. `Trend` is one of `UpGood`, `DownGood`, `UpBad`, `DownBad`.

Trend to direction, as observed in journal entries:

- `UpGood` and `DownGood`: +INF.
- `UpBad` and `DownBad`: -INF.
- The pip count is the length of the `Influence` string (`"++"` is 2 pips).

Totals are kept per faction as `inf_plus` and `inf_minus` pip counts and a mission count.

System attribution:

- Each `Influence[]` entry carries a `SystemAddress`, resolved to a name through the addresses seen in `FSDJump`, `Location`, `CarrierJump` and `Docked` events.
- If it cannot be resolved, the influence of the issuing faction is attributed to the system in which the mission was accepted.
- If that is also unknown, the system in which the mission was handed in is used.
- Handing in a mission elsewhere therefore does not move its influence.

Conflict missions without `Influence[]`:

- The entry of the issuing faction is sometimes empty (observed on `Mission_Massacre_Conflict_CivilWar`).
- If the mission name contains a conflict word (`War`, `CivilWar`, `Conflict`, `Election`, `Elections`) and the last seen state of the faction in that system is `War` or `CivilWar` (assumed 2 pips) or `Election` (assumed 1 pip), the ledger credits that number of pips to `inf_plus`.
- These pip counts are assumptions, not journal values. Any other mission with an empty entry stays at zero.
- Squadron perks are not in the journal, so a squadron influence bonus is not visible.

### 3.3 Failed and abandoned missions

`MissionFailed` and `MissionAbandoned` contain only a `MissionID`. The ledger records the `Faction` and the system of each `MissionAccepted` and scores the failure or abandonment against that faction in that system as an influence decrease. Missions accepted before the replay window are unknown and skipped. The open-mission map is persisted (`MAX_OPEN_MISSIONS` = 400) so that missions that outlive a restart are covered.

### 3.4 Bounty vouchers and combat bonds

`RedeemVoucher` is the source of BGS credit. The effect applies at redemption, so no correlation with `Bounty` or `FactionKillBond` events is needed.

- `Type == "bounty"`: contains `Factions: [{Faction, Amount}]`. One redemption can cover bounties against several factions.
- `Type == "CombatBond"`: contains a single top-level `Faction` and `Amount`, not a `Factions[]` array.

The two shapes differ in real journal entries.

### 3.5 Trade profit or loss and exploration data

`MarketBuy` and `MarketSell` (`TotalCost`, `TotalSale`), `SellExplorationData` (legacy) and `MultiSellExplorationData` (`TotalEarnings`; the legacy event has no `TotalEarnings` field, so `BaseValue + Bonus` is used) are attributed to the controlling faction of the current station. That faction is taken from the `StationFaction.Name` field of the preceding `Docked` event, not from the system's overall controller.

Trade profit is `trade_sell_credits - trade_buy_credits`. It is net credits transacted and is not an exact model of the BGS supply and demand rules. The Settings tab describes it as an approximation.

### 3.6 Crimes

`CommitCrime` contains `Faction` (the faction the crime was committed against) and `Fine` or `Bounty`. It is counted per faction as one crime plus the credits incurred, shown as an influence decrease, and attributed to the current system.

### 3.7 Tick detection

`bgs_tick_client.fetch_latest_tick()` sends an HTTP GET to `http://tick.infomancer.uk/galtick.json` (`TICK_URL`), reads the `lastGalaxyTick` field and parses it with `%Y-%m-%dT%H:%M:%S.%fZ`.

- The endpoint is operated by a third party (the community).
- `bgs_panel.py` polls every 60 seconds (`_TICK_POLL_INTERVAL_MS` = 60000) with its own `queue.Queue`, generation counter, `threading.Thread` and `after()` loop. The Tk main thread is not blocked. A failure is treated as "tick unknown for now".
- Detection is switched independently (`wfmt_bgs_tick_enabled`, on by default), because it is the only network call of this mode.
- Section 2.1 describes what a new or first-seen tick triggers.

## 4. Settings in the report window

The switch that shows faction states and activity, and the number of days of ticks to keep, are set only on the **Settings** card at the top of the BGS Report window (`bgs_settings.SettingsCard`). The Settings → WFMT → BGS tab only refers to the card and to the Online tab, where tick detection is switched. The config keys and readers are in `bgs_settings` (`bgs_panel` imports them). `set_enabled` and `set_archive_days` save with the same clamping as the Settings tab (1 to 90 days). Every change is announced to listeners: a card follows a change made in another card, and `BgsController._on_window_setting` applies it (prunes the archive, saves, redraws, reconciles the tick poll). Tick detection (`wfmt_bgs_tick_enabled`, on by default) is set only on the Online tab of Settings, and the tick line shows `online_lookups.needs` while it is off.

## 5. Known gaps

- Crimes beyond what `CommitCrime` reports (no victim-faction attribution for kills).
- Ticks before the feature was installed: the tick API returns only the latest tick, so earlier periods cannot be reconstructed from earlier journals. The archive fills from the first tick that WFMT sees roll.
- Combat-zone participation (ground and space) as a signal of its own. Only the resulting bounty or combat-bond redemption is tracked.
- Thargoid war states.
- Discord export covers the selected tick. Posting every tick at once is not offered.
