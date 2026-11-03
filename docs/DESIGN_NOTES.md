# Design notes

Record of the design decisions behind WFMT, the facts that led to each, and the approaches that were considered and not implemented. The page is intended for contributors and is not a user guide.

- [TECHNICAL.md](TECHNICAL.md) describes how the code works.
- [ATTRIBUTIONS.md](ATTRIBUTIONS.md) records the origin of ideas and data.
- [CHANGELOG.md](../CHANGELOG.md) lists the contents of each release.

Each decision record uses these fields:

- Decision: what was implemented.
- Why: the facts that led to the decision.
- Not done: approaches that were considered and not implemented.
- Where to look: the code, test or document that holds the detail.

**Contents**

1. [Principles](#1-principles-that-shaped-everything)
2. [Credits and licenses](#2-credits-and-licenses)
3. [Decision records](#3-decision-records)
4. [Deliberately not built](#4-deliberately-not-built)
5. [Lessons that keep coming back](#5-lessons-that-keep-coming-back)

---

## 1. Principles that shaped everything

### Journal first; values that cannot be known are not invented

- A third-party tool knows only what the game writes to its journal.
- Where the journal is silent, WFMT adds data in a fixed order: Frontier's CAPI, then data players share, then labeled workarounds. The source is stated.
- A value that cannot be known is omitted, shown as unknown or reported.
- Examples:
  - The Route Planner reports a frame shift drive for which it has no figures (3.7).
  - The jump range is not estimated from fuel and cargo (3.7).
  - The Dashboard shows `-` for a body that has not been scanned.
- Where to look: the design principle at the top of [TECHNICAL.md](TECHNICAL.md); the "what the game does and doesn't tell us" table ending each guide.

### Estimates are labeled as estimates

- The scan-value formulas approximate the game's payout.
- The exobiology odds are an even split among the species the body allows, because the data states which species are possible and not how likely each is.
- The interface states that these values are estimates.
- Where to look: the Exploration Value and Biology card text; `organic_scan.GenusView.odds`.

### Saved play data is per commander

- Two commanders on one installation must not see or change each other's data.
- A commander name in a file name is not portable (Windows file names are case-insensitive and reject some characters; Linux file names are case-sensitive). A commander is therefore only a JSON key inside a file.
- Exception: `exo_observations.json` holds facts about bodies, pooled to check the species prediction. It holds no commander.
- Where to look: `commander_data.py`; `tests/test_data_files_per_commander.py` (a new data file fails until it is classified); [DEVELOPMENT.md](DEVELOPMENT.md).

### Network access is opt-in

- A plugin runs inside another program on the user's computer.
- Every lookup is either a switch that starts off or a button that acts only when pressed. Each is listed with what it sends.
- Where to look: [internet-and-privacy.md](guide/internet-and-privacy.md); `settings_online.py` (the Online lookups page; `tests/test_settings_online.py` fails when an entry names a setting that does not exist).

### Pure logic is separate from the screen; tests read the sources

- A function that takes plain data and returns plain data is testable without Tk, on both operating systems.
- Several tests read the code instead of running it, so that lists stay in step:
  - Every data file must be in the updater's protected list (`tests/test_own_data_files.py`).
  - Every module must have a row in [MODULES.md](MODULES.md) (`tests/test_docs_modules.py`).
  - The Dashboard's overlay prefixes must be real card prefixes (`tests/test_overlay_group_hide.py`).
- Where to look: [TECHNICAL.md](TECHNICAL.md) sections 6 and 14.

### Live state changes at a safe moment

- WFMT holds its data in memory and rewrites the files, and Python cannot replace modules that are already imported.
- An update is staged and takes effect at the next EDMC start.
- A restore from a backup is staged and applied at the next start, before any feature reads a file (3.4).
- Applying either immediately would be overwritten by the running plugin's next save.

### Files that WFMT did not write are not deleted

- A live plugin folder, a backup folder and a deploy target hold files that are not part of the build.
- Deploy merges instead of deleting and re-copying.
- The updater writes only files that are in the release zip.
- Automatic backups use a distinct name so that pruning reaches only backups WFMT made itself.

### Writes are atomic and portable

- Files are written to a temporary file and then moved with `os.replace`, in UTF-8 with LF line endings. Operating-system specifics are placed behind `platform_support`.
- Anything tried on one operating system only is recorded in [LINUX_TESTING.md](LINUX_TESTING.md).
- The repository is developed on one Windows and one Linux machine; Git is the only link between them.

### EDMC's appearance is not changed

- The window kit uses classic widgets and its own buttons and tables. `style.skin(window)` colors a window by name and never touches the ttk theme.
- ttk styles are application-wide, so changing one would recolor EDMC's main window and every other plugin. `tests/test_ui_kit.py` fails if the kit does so.
- Nothing in the main panel may let external data widen it: EDMC sizes its window to the widest row of any plugin, so one unbounded widget widens the window for all plugins.
- See [WINDOW_FRAMEWORK_SPEC.md](WINDOW_FRAMEWORK_SPEC.md).

### One word for an overview page: Dashboard

- "Dashboard" is the label for a page that gathers everything about a mode in one place (Colonization and Exploration each have one).
- The label may appear on buttons in different modes, because the mode identifies which one is meant. No mode has two.
- The Button names table in [getting-started.md](guide/getting-started.md) lists each.

---

## 2. Credits and licenses

Acknowledgements are in [ATTRIBUTIONS.md](ATTRIBUTIONS.md). The license notices for the data shipped with WFMT are in [THIRD-PARTY-NOTICES.md](../THIRD-PARTY-NOTICES.md).

---

## 3. Decision records

### 3.1 The built-in overlay

- Decision: WFMT can draw its own overlay on Windows, in a window laid over Elite. EDMCModernOverlay remains in use on Linux and for other plugins. Both can run at once.
- Why: a separate overlay program has its own font, scaling and lifetime, shared by every plugin that draws through it. Drawing in WFMT's own window gives WFMT control of these.
  - WFMT chooses the font for its own cards.
  - The window is created and closed with WFMT, so no window from an earlier session remains to draw a second copy of every card.
  - The window's size and position are known, so placement at the right-hand edge needs no workaround.
- Unchanged: every feature sends payloads through `overlay.OverlayClient`. The built-in overlay is another destination for the same payloads (`overlay_native.py`). The hide-everything switch applies to both.
- Verified beforehand: `scripts/native_overlay_test.py` draws a transparent, click-through, layered window over Elite.
- Where to look: [NATIVE_OVERLAY_SPEC.md](NATIVE_OVERLAY_SPEC.md).

### 3.2 Right-hand overlay cards on Linux with a Flatpak EDMC

- Decision: when Elite's `DisplaySettings.xml` cannot be read:
  - The overlay window's size is taken from EDMCModernOverlay's log.
  - A fifth Flatpak permission (the Graphics folder, read-only) restores the normal path.
  - The user is still told to set Display scaling by hand.
- Why:
  - A Flatpak EDMC cannot access the Proton prefix that holds the file. Without the log, WFMT would assume a 1920 x 1080 screen, which places right-hand cards incorrectly on other screens.
  - The overlay's log states its window size.
- Not done: estimating scaling. Linux provides no portable way to read it.
- Where to look: `overlay_layout.parse_window_size`, `overlay_placement.screen_for`, [linux.md](guide/linux.md).

### 3.3 Hiding groups of overlay cards (the Dashboard's two switches)

- Decision: cards are hidden by id prefix in the overlay layer (`overlay.set_group_hidden`). The state is not saved and is not in Settings.
- Why:
  - The overlay layer already holds every payload for the global hide.
  - A prefix filter there is a single implementation that applies to both overlays.
  - Showing a group replays the payloads that have not expired.
- Not done: switching each card's enable setting off and on.
  - The settings are saved in the commander's overlay profile, so a switched-off setting would persist to the next start and restoring would require recording which settings were on.
  - A suppress flag in every feature module would change a dozen files.
- Where to look: `overlay.py` (the group functions), `tests/test_overlay_group_hide.py`.

### 3.4 Back up my data, restore and automatic backup

- Decision:
  - One zip of every file in the updater's protected list plus the mining run archive, to a folder chosen by the user.
  - A restore that is staged and applied at the next start.
  - An optional automatic backup.
  - Keys and caches left out.
- Why, by part:
  - The file list is the updater's `_OWN_DATA_FILES`, so a new data file is included in the backup when it is added to that list. `tests/test_own_data_files.py` keeps the list complete.
  - `rcc_keys.json` (Raven Colonial keys) and `discord_webhooks.json` (Discord webhook links) are left out (`LEFT_OUT`) because an archive may be copied or stored in cloud folders. The `star_index` folder is left out (`LEFT_OUT_DIRS`) because it is built from a public download and can be rebuilt. The Codex catalog cache is left out because it is downloaded again.
  - The destination folder may not be inside the plugin folder, which an update or reinstall can clear.
  - The zip is written under a temporary name and renamed, so a failure leaves no partial archive. An existing zip is not overwritten.
  - A restore cannot overwrite live files because the running plugin would write its memory back over them.
    - The archive is unpacked into a staging folder, marked complete last, and applied before any feature reads a file.
    - The files it replaces are zipped first so that the restore can be undone.
    - A zip that contains anything other than WFMT data files is refused as a whole.
  - Automatic backups use their own name (`WFMT-data-auto-...`) and the newest ten are kept (`AUTO_KEEP`). A manual backup is never deleted.
  - When automatic backup is on, a backup is also made before an update, because the updater's own backups leave data out.
  - Automatic backup is off by default.
- Not done: restoring in place, and restoring one commander at a time (a data file holds every commander, so the file is the unit).
- Where to look: `data_backup.py`, [getting-started.md](guide/getting-started.md#backing-up-your-data), `tests/test_data_backup.py`.

### 3.5 Compact data files

- Decision: per-commander files are written without indentation. Indented files are still read.
- Why: the code comment in `commander_data.write` records that the indented form was 35 to 60 percent larger. The largest files are rewritten whole on every save.
- Not done: a database for the largest file, and less frequent writes. A database would make the files unreadable to other tools.
- Consequence: the files are harder to read by hand; an editor's format command restores indentation.
- Where to look: `commander_data.write`.

### 3.6 The Exploration Dashboard

- Decision: a window, opened from the Dashboard button on the Exploration panel, that reads what other features hold and presents it in four tabs (Overview, Orbit, Surface, Exploration).
- Why a window: the overlays draw on the game; the window presents the same facts without occupying the game screen.
- Why it holds no data of its own: it reads the system survey, Organic Scanning, the Expedition Log and the Route, so it agrees with the cards. The values come from a pure module (`explore_dashboard_data.py`), which is tested without a screen; the window only draws.
- Why Orbit and Surface: they answer different questions (the whole system from space; the body under the ship on the ground). The window opens on the one that fits, follows a landing and a lift-off, and leaves a tab the user has chosen unchanged.
- The header switches are runtime-only (see 3.3).

### 3.7 The Route Planner

- Decision: routes are plotted with Spansh's exact plotter, built from the ship's actual figures. The jump range is not estimated. Three approaches were evaluated.

1. Spansh's neutron router with a typed jump range.
   - It requires a range that the game does not write for the current load. The user would read it from the ship statistics panel and retype it whenever the load changes.
   - This router is not used.
2. An estimated laden range, from the loadout's maximum, the unladen mass, and the fuel and cargo on board.
   - Not done: the estimate changes with the fuel used by each jump, cannot be checked against the game, and ignores that the ship becomes lighter as fuel burns. A value WFMT cannot know is not produced.
3. Spansh's exact plotter (implemented).
   - The plotter takes the ship's actual figures. Its optimal mass equals the engineered `FSDOptimalMass` in the journal's `Loadout`.
   - Spansh's page script builds the request from a mass, the fuel tanks, the drive's optimal mass, maximum fuel and fuel formula, the supercharge multiplier and any booster.
   - WFMT builds the same request from the journal and from the cargo in `Status.json`.
   - Spansh computes the range jump by jump and reports where to refuel.

**Data and WFMT's own parts**

- The request has the shape that Spansh's exact plotter takes.
- The drive table (`fsd_data.py`, 66 drives) is published drive data used as game facts (source and license: see [ATTRIBUTIONS.md](ATTRIBUTIONS.md) and [THIRD-PARTY-NOTICES.md](../THIRD-PARTY-NOTICES.md)).
  - It is on the data verification list as V-0351 to V-0353. V-0351 (the 6x supercharge of the Mk II overcharge drive) is verified against the journals. V-0352 and V-0353 are marked "Needs verification" in `docs/data_verification/verification_checklist.csv`.
  - A drive missing from the table is reported, not estimated.
- Additional features:
  - The next system is copied to the clipboard after every jump, with one setting shared by the panel and the window.
  - The plotted route replaces the Route overlay card's route (with the overlay's EDSM mark for systems EDSM does not know).
  - A fuel column.
  - The neutron stars, the destination and the refuel stops can be turned into an expedition.
  - The options are remembered.
  - The ship block does not change while flying; fuel is not shown, only cargo.

**Entry point and white dwarfs**

- The Expedition window's **Neutron route** button opens the Route Planner.
- A white dwarf supercharges the drive (`route_plan.py` classes both neutron stars and white dwarfs as supercharge stars). The exact plotter's request does not include white dwarfs. The Route Planner therefore cannot request a route through them.
- The option *Mark white dwarfs the route passes* asks EDSM for the main star of each system on the finished route and marks the white dwarfs. Planning through white dwarfs would require a router of WFMT's own, which the window does not offer.
- The ship block states whether a fuel scoop is fitted, because the refuel stops of a route require one and Spansh cannot be instructed to plan without refueling.
- The option label states what the code does and no more. A label such as "Also mark white dwarfs" would imply that the route uses them.

**One window with three tabs**

- The Expedition window, the Route Planner and the Expedition Log were three windows, each with its own size and position. They are the Plan, Route and Log tabs of one window (`expedition_hub.py`).
- Implementation:
  - The windows keep their own code and tests. Each takes its shell as an argument.
  - `uikit.shell.TabShell` gives a tab the same interface as `WindowShell` (header buttons, Help, subtitle, status line and body).
  - The panels register how to build their tab with the hub, which imports no panel, so the dependency runs in one direction.
  - A tab is built when first shown and is built again if its window was closed.
- Consequences:
  - The three views share one window size and position.
  - The per-window geometry settings are no longer read by the panels.
  - The standalone windows remain in the code as the path used by the tests and by `host=None`.
- The panel's two rows are one section:
  - The Log has no section of its own (`expedition_log_panel.PANEL_PLACEMENT` is `None`).
  - The section has no Start, Pause or Stop; expeditions are started, paused and stopped in the Expedition window (`build_into` connects the section to the Log).
  - The section words the Log's extra figures under the expedition's own lines.
  - A Log run without a plan is shown as the Log words it.
  - The archive is a tab of the window; there is no Log button.
  - The section's folded state is the Expedition section's.
  - With a planned expedition, Start, Pause and Stop act on it through the link; with none, they start a Log run only.
- **Start expedition** does not switch tabs. Pressed on the Route tab of an open window, it remains there and reports in the status line. **Review expedition** opens the Plan tab.

**One linked start for an expedition**

- Problem: a trip has two records, the Expedition planner's list of stops and the Expedition Log's run of figures. They were started, paused and stopped separately. Starting a planned expedition left the Log, the Dashboard and the overlay card stating that none was running. **Pause** had two meanings (the Log stopped its clock; the planner changed a word).
- Decision: starting an expedition also starts a Log run.
  - The expedition stores the run (`log_run_id`).
  - Start, Pause and Stop on either side apply to the other, in one module (`expedition_link.py`) that both panels call.
  - The expedition's time is the run's clock, which excludes paused time.
  - The Log run is on by default; a setting turns it off (Settings > WFMT > Exploration > Expedition).
- Route Planner behavior:
  - **Start expedition** completes the operation in one press and reports it in the status line.
  - **Review expedition** opens the Expedition window on the same expedition.
  - A second press for the same plot selects the expedition created the first time and does not create "(2)".
  - An expedition made from a route is a snapshot of the stops and notes at that moment. Plotting again or clearing the route does not change a running expedition.
  - The term for ending is **Stop**, as in the Log.
- Consequence: the Log keeps one run running at a time. Starting a second expedition sets the first aside: its run is paused with it, or stopped when the new expedition gets its own run. An expedition that was set aside and is started again reopens its run as the Log's Resume does; the clock continues from the time the run stopped, so the interval in between is not counted.

### 3.8 When a relog skips the journals

- Case: a system scanned while EDMC is closed must not be empty after the commander logs in again.
  - A rule that decides whether to rebuild a survey by asking whether the commander has been there before, and counting visits, fails here. A relog is not a second visit, so a first visit played with EDMC closed appears new and receives a record that holds only the honk, which prevents any later rebuild.
- Decision: rebuild whenever the visit history states that the commander scanned there and no scanned bodies are saved (`system_survey.needs_backfill`).
  - This also repairs a record that holds only the honk.
  - A first visit played live needs no rebuild because the live events carry the data.
- Why not always rebuild: a rebuild reads journals, and most arrivals do not require one.
- Principle: a counter that stands in for a fact ("been here before") fails where the two differ. The rule uses the fact that the history records.

### 3.9 Engineering data

- Decision: a published recipe table is the data source, corrected from the game's own records.
- Why:
  - The imported data was last changed on 2024-03-07 (`blueprints_data.py` docstring), so it lacks later game changes.
  - The journal records what the game charges now. A second data set differs from the first in five synthesis recipes, which were corrected.
  - Where sources differ, the more recently maintained source is used. The choice is recorded in the module docstring, and `tests/test_blueprints.py` pins each change so that a re-import cannot undo it.
- A frame shift drive synthesis recipe whose cost appears two ways in the journal (V-0350) is recorded in the verification checklist and is not resolved by assumption.

### 3.10 Clearing a line or a circle on the overlay

- Problem: the Bio radar clears every slot it does not use on each redraw.
  - EDMCModernOverlay rejects a line sent with no points (`Dropping vect payload with insufficient points`), so each redraw would log a warning per slot and the clear would not take effect (a stale pointer would remain until its ttl expired).
  - A one-point line is rejected also.
- Decision: send a removal for the id (the id and a ttl of 0), which the overlay treats as a removal, and only for items that are on the screen.
- Determination: the installed overlay's `normalise_legacy_payload` was run on candidate payloads.
  - The empty line and the one-point line are dropped.
  - A circle clear is returned as a visible white circle (a circle with no color is given white).
  - The removal is returned as `legacy_clear`.
- Placement: four features clear lines and one clears circles. The overlay layer implements the clear once. Callers keep their calls (`send_vector(id, [], ...)`, `send_circle(id, "", "", ...)`).
- Sending nothing when nothing is drawn also prevents the log entries at their source.

### 3.11 Random: real systems

- Problem: a name made by shifting both numbers of a nearby real name does not plot on the galaxy map.
  - In a procedural name `<sector> <LL-L> <mass><N1>-<N2>`, N1 is part of the boxel's identity and N2 is the index inside it.
  - Shifted names fall in boxels that do not exist, or beyond the last index of one that does.
  - "EDSM has no record" is then read as "undiscovered", but it is equally true of a name that never existed.
- Decision: request the systems that exist around the commander from Spansh (`systems/search`, nearest first), keep those whose `body_count` is empty, and confirm one with EDSM's bodies list before offering it. No name is composed from a pattern.
- Why Spansh first: it sorts by distance from a position, which EDSM's cube query cannot do for scan state.
- Limit (stated in the guide): absence of scan data does not prove that no one has visited.
  - The Sequence mode keeps the boxel identity and steps only N2, so its names are valid up to the boxel's unknown last index.
  - Region Sweep and Find Nearby use only listed systems.
- Request size and cache:
  - The page size is a Settings entry (`RANDOM_COUNT_MIN` to `RANDOM_COUNT_MAX`, default `undiscovered_nearby.PAGE_SIZE`, 25).
  - The list is cached in memory for 10 minutes within 5 ly for the same request size (`CACHE_TTL_S`, `CACHE_RADIUS_LY`). Repeated requests run only the EDSM check, which is always fresh.
  - The cache is not written to disk.
- Principle: a negative lookup is evidence only when the looked-up item is known to be real, so the search starts from a list of real systems.

### 3.12 Bio radar text stays inside its card

- Problem: the lines under the radar plot are laid out left to right, while the card is only as wide as the plot. A long plant name, or three distances on one line, would overrun it.
- Decision: one function (`lay_out_rows`) places the rows for both the card height and the drawing.
  - Items wrap to a new line, and the card grows by the lines used.
  - An item wider than a line is cut with an ellipsis.
  - The ship and SRV row above the plot does not wrap, because the plot sits below it; it is cut.
- The rule is the same as for EDMC panels: content from outside requires an explicit bound.

### 3.13 POI Reference and the section order

- Decision: GEC Nearby POI and Canonn Nearby POI are one section, POI Reference, with one Find POI.
  - The controllers are separate modules (`gec_poi_panel.py`, `canonn_poi_panel.py`) because the sources differ: one downloads a single list and caches it (`CACHE_SECONDS` in `gec_poi_edastro.py`, six hours); the other uses two Google-hosted sheets cached for the session. Their settings differ.
  - `poi_reference_panel.py` owns the buttons and the frame.
  - A `Collector` waits for both lookups and names the nearer system. It contains no Tk, so a test can drive it.
- The clipboard receives the nearer result. With two sources, the last result to arrive would not be the nearest.
- Section order: sections within a mode are alphabetical by visible name.
  - The order is the order of `FEATURES`. `tests/test_panel_order.py` fails when a new section is out of order.
  - Consequence: Random is added to the Auto-Honk row before Boxel Survey's panel exists (Boxel Survey sorts after it), so the button creates its own status variable and does not depend on build order.

### 3.14 Cards that leave in one step

- Problem: when a card goes away, its text can clear first and the empty panel can remain for several seconds.
- Cause: `overlay_card.PANEL_TTL_FACTOR` (2) gives a panel twice the lifetime of its text.
  - The overlay stacks items in the order they were first drawn. A panel that lapsed a moment before a refresh would be redrawn above the text and dim it.
  - A card that stops being redrawn without an explicit clear shows a bare panel for the second half of the panel lifetime.
- Decision: handle it in the overlay layer.
  - A sweep every half second (`REAP_INTERVAL_S`) examines what WFMT has drawn (`overlay._last`).
  - It removes a panel that has carried live text before and has none now, together with the shapes drawn over it (`overlay.orphaned`, a pure function with tests).
- Not done:
  - Shortening the panel lifetime, which restores the dimming.
  - A timer per card. There are more than a dozen card types and radar-style drawings, each with its own code; one rule over the remembered drawings covers all of them, including later additions.
- Limits:
  - A panel that never had text keeps its own lifetime.
  - Text from another card lying over a panel keeps that panel until the text expires.

### 3.15 My Codex

- Decision: the Codex Completionist section keeps its summary line and has one button, My Codex.
  - "Dashboard" is not used because Exploration already has one and a label is not used twice in a mode.
  - The window has an Overview tab and a Where to look column. The backfill is in the window.
- Why an overview: the Found and Not found lists show what is held but not what remains to be found, and a long list does not show that one genus is nearly complete. Ranking started types by entries left gives a first answer.
- Why the hint uses existing data:
  - The catalog lists every biological entry as a species plus a color.
  - WFMT holds the conditions each species requires and what decides each color for the Bio predictions.
  - A missing entry can therefore state which planet type to look for, with no new data and no network use.
- Limits (stated in the guide):
  - The hint shows only the first set of conditions.
  - It states where an entry can appear, not where one is.
  - It has nothing for Thargoid, Guardian or stellar-body entries; POI Reference covers those.
- Not done: finding the nearest planet that fits a missing entry. That requires a search of scanned bodies (Spansh).

### 3.16 Wrapped text beside a button

- Problem: the main EDMC window can become wider without any change by the user.
- Cause: a label whose `wraplength` is the full width of the plugin frame is correct on its own row and incorrect when it shares a row with a button.
  - The row (button plus a label as wide as the frame) is wider than the frame.
  - EDMC sizes its window to the widest row, the frame's next resize is larger, and the label receives that larger width in turn.
  - Any text change in such a label can start the growth. Example: the route summary beside Neutron route changes when a window closes and the route state is refreshed.
- Decision: `panelkit.wrap_label` gives a label the room left of its starting position (`available_wrap`) and subtracts the widths of the other widgets in its row, which are known.
  - A label's position is not settled when a hidden panel is shown. The width is recomputed when a hidden panel is mapped; until then a label in a hidden panel receives a modest width.
- Verification:
  - A test places a long label beside a button in a frame of fixed width and fails if the label extends past the frame.
  - A log line records which widgets request room whenever the panel widens by 40 px or more (`GROWTH_LOG_PX`).
- Principle: a bound applies to the space available to a widget, not to the space of the whole frame. This is the rule for anything that can size the main window.

### 3.17 Nested tabs in the Dashboard

- The Orbit tab has a second set of tabs (Worth mapping, Life to analyze, Found by others) beside the Body panel.
- With the page-level `Tabs` style, a second large uppercase bar with the window's dark background sits inside a lighter pane.
- `Tabs(compact=True)` keeps the behavior and changes only the appearance for a set nested in a pane. The Dashboard's Orbit tabs use it.

### 3.18 Switching overlays off and on

- Problem: hiding and showing by simple methods produces two defects.
  - Off: hiding by sending each item a replacement that draws nothing (an empty text, a zero-size panel) with a `ttl` of 1 makes EDMCModernOverlay drop the empty text at once and keep the replaced panel for a time. The overlay treats a payload with only an id and `ttl: 0` as a removal (`legacy_clear`), which is how lines and circles are cleared (3.10).
  - On: restoring only items that still have time left on their `ttl` restores nothing, because a card's `ttl` is four to eight seconds. A card in a quiet cockpit would not be drawn again until an event occurred.
- Decision:
  - Every clear is a removal, sent only for items on the screen, so the overlay has nothing to log.
  - Showing restores what was on the screen at switch-off plus anything drawn since, with its full `ttl`.
  - Features keep drawing into the remembered set while hidden, so the restored card is current.
- Limits:
  - A banner that ended while the overlays were off returns for one `ttl`, because "ended" and "not yet redrawn" cannot be distinguished at this layer.
  - The overlay hides its own window whenever Elite is not in front. This is separate from WFMT's hide.
  - Cards that stop being redrawn are covered by 3.14.

### 3.19 Organic Scanning after EDMC was closed

- Problem: EDMC is closed while the last Sample and the Analyze of a species are taken.
  - The survey (rebuilt from the journals, 3.8) counts the species as complete.
  - The organism tracker is fed only by the events EDMC passes in, so it keeps its saved stage (2 of 3) and shows it on the Bio status card and the Dashboard.
  - A body scanned entirely with EDMC closed has no saved progress.
- Decision: the same catch-up pattern as the visited log and the survey.
  - On a worker thread, read the commander's `ScanOrganic` events from the last 14 days (`CATCH_UP_DAYS`).
  - Merge them into the saved per-body progress on the Tk thread.
- Naming and merging:
  - A `ScanOrganic` names its body only by number. `organic_catchup` takes the name from the `Scan`, `FSSBodySignals`, `SAASignalsFound` and `ApproachBody` events for the same body in the same system. A sample that cannot be named is skipped.
  - The merge only raises a stage, so it can run at every start and needs no watermark.
  - `OrganicTracker.restore_organism` never lowers a stage, because a saved stage older than the live one would undo live progress.
- Also recovered, for a body scanned with EDMC closed: the data the prediction reads.
  - Conditions come from its `Scan`, genera from `FSSBodySignals` or `SAASignalsFound`, plus the first-footfall flag.
  - A shared pure builder, `organic_scan.conditions_from_scan`, is used by both the live handler and the catch-up.
  - These values are added only where nothing is saved for the body, never over what the live tracker saved.
  - A species left part-way is shown as the active scan again when a body's progress is restored.
- Limit: `ScanOrganic` carries no position, so a caught-up sample adds none. The distance to the last sample on that body is the saved value.

### 3.20 Mining History

- Why: the Mining pages show only the run in progress, held in memory. A run across an EDMC restart, a relog or a closed EDMC is lost, and nothing totals the runs.
- Decision: build it from the journals on the pattern of the system history (3.8, `system_history.py`).
  - Read every finished journal once in the background.
  - Save one record of runs per commander.
  - Read only newer journals afterward.
  - Read the newest journal afresh each time instead of saving it, so a growing file is never counted twice.
  - This also covers the live page's own catch-up, which replays only the current journal when EDMC starts with the game running.
- Definitions:
  - A run is undocking to docking, the same boundary as the live page.
    - Mining with no preceding undocking starts a run of its own.
    - Sales after docking belong to the run that just ended.
  - Mining time is first to last mining event, so travel does not reduce the rate.
  - Earned is the sales after the run. It is not profit, and the window states this.
- Reuse: the table and block widgets come from the Exploration Dashboard, so the two windows look and sort alike.
- Not done: a verdict on a single asteroid against a chosen commodity, and earnings on the live page.

### 3.21 The Route overlay is a plain copy of the route

- Decision: the card is a copy of the route and contains nothing else.
  - **You are navigating to:**, the destination, **You will be there in N jumps.**, a rule, the systems still to visit, a rule, **N LY left to jump.**
  - A system is removed as it is reached.
  - Each system shows its star in a color with one meaning: green (fuel can be scooped), yellow (it cannot), blue (neutron), red (white dwarf).
  - At the end the card states that the route has ended and is being reset, then closes.
- Why: the card previously also carried fuel, range, last jump, the next supercharge, refuel stops, an EDSM line, the running expedition, numbered rows and a star column. It now has one source (the Route Planner's route, else the game's `NavRoute.json`) and one function (follow the route).
  - The fuel, range and supercharge figures are in the Exploration Dashboard. The expedition lines are not on the card.
- Consequence: the fuel line requires opening the Dashboard. The card is shorter and fits the available room more easily.
- Limit: the end of the route is detected only for a route the overlay has already shown (`_seen`), so a finished route left in `NavRoute.json` from an earlier session produces no message.

### 3.22 Exploration Value lives inside the Dashboard section

- Decision: the Exploration Value readouts and the Dashboard window show the same figures (the Dashboard's Panel readouts are Exploration Value's lines), so they share one panel section.
  - The readout lines are drawn under the Dashboard button (`exploration_value.build_rows`).
  - Exploration Value has no section of its own (`PANEL_PLACEMENT = None`).
  - Its Settings tab, switches and two online extras remain.
- Why: two sections would use two lines of the panel to show one set of figures. The Dashboard and the Route Planner sections fold like the others.

### 3.23 One considerate way to call Spansh

- Problem: if each feature that queries Spansh makes its own requests with its own timeouts, nothing limits how many run at once or what happens when Spansh reports that it is busy. The Route Planner's star lookups increase the request count.
- Decision: one module (`spansh_courtesy.py`) through which Spansh requests pass:
  - at most two requests in flight (`MAX_CONCURRENT`)
  - at least 0.25 seconds between request starts (`MIN_GAP_S`)
  - retries with growing waits on a busy answer (429, 502, 503, 504), honoring `Retry-After`
  - a pause of 300 seconds after five consecutive failures (`BREAKER_S`, `BREAKER_FAILURES`)
  - a count in the diagnostics
  - with the separate diagnostic log on (Settings → WFMT → Help), a line for each request with its outcome and time
- Why a module and not a setting: the limits are identical for every feature and belong in one reviewed place; a user setting would only allow higher limits.
- Why POST requests are not retried after a timeout: a submitted job may have been accepted.
- Consequence: long polling loops (route jobs poll every 5 seconds) are unchanged. The star lookups for the next dozen neutron stops take a few seconds instead of arriving at once.
- `docs/SPANSH_USAGE.md` records every endpoint.
- Where Spansh publishes a data dump that covers a need (the neutron-star list), a local copy is read in preference to a request. WFMT offers this as an option for the neutron-star list (the local star index, described in [SPANSH_USAGE.md](SPANSH_USAGE.md); open work is in [TODO.md](TODO.md)).

### 3.24 What "Acquire" means in Colonization (formerly "Remaining")

- Problem: the column, then named Remaining, was the site's need (required less delivered). A commodity already bought and stored on the fleet carrier remained outstanding until unloaded at the depot, so the column did not decrease as the commander worked, and the overlay card needed a second column (To buy) to show what remained to be acquired.
- Decision: the column (renamed Acquire after 1.0.0) is the amount still to get: the site's need less the cargo in the ship and on the fleet carrier. It reaches 0 once the whole amount is acquired wherever it is stored. The window, its category totals and sort, and the overlay card show it. Required, Delivered and Haul Trips keep the site's own figures, so the number of trips to carry everything to the site remains correct.
- Why: it answers the question asked while shopping, and the window and the card agree.
- The ship's hold is read from `Cargo.json`. The journal's `Cargo` event carries only a count, and EDMC's cargo state was observed not to follow a purchase. The file is read again shortly after any event that can change the hold. EDMC's state is the fallback when the file is missing or describes the SRV.
- Filter change after 1.0.0: once everything is bought and stored on the carrier, the earlier *hide covered* filter hid every row. It became a three-way choice: All, To buy (the earlier behavior) and To haul. To haul keeps the rows that the ship and carrier cover but the ship does not yet hold in full, so a row leaves the list as it is loaded and the site drops it once delivered. One function (`colonization_view.shown`) decides for the window and the overlay card.
- Not done: counting a commodity on the carrier as delivered. It is not delivered until unloaded at the depot, and the carrier column shows where it is.

### 3.25 The navy theme for WFMT's own windows

- Problem: the pop-out windows were near-black with gray text. Headings, table headers and status messages were the same muted gray.
- Decision: the fixed look (`WINDOW_FRAMEWORK_SPEC.md` section 4) uses navy surfaces and gives three roles their own color in `uikit/palette.py`: `TITLE` (gold) for a window title, `HEADING` (cyan) for section labels, field labels and table column headers, and `STATUS` for the footer message. Success, caution and failure keep green, yellow and red.
- Change on 2026-10-28: `STATUS` had been a pale tint of the accent, which blended into the window on every theme. It has its own bright color per theme, and a test keeps it separated from the accent, headings and text.
- Why: color separates the structure of a window (where a section starts, what a column is) from its data, without a setting. All windows read the palette tokens.
- Not done: a light variant. The in-game overlay cards (which have their own schemes in Settings → Overlays) and the main panel (which follows EDMC) are unchanged.

### 3.26 Text size and column fit for WFMT's own windows

- Problem: the text of the dashboards was small and fixed, and every table gave each column a declared minimum width and shared spare width equally, so short columns were wide and long ones were cut.
- Decision: one text size for all pop-out windows (-2 to +6 points, remembered), changed from a window's footer (A− and A+) or Settings. Fonts are resized in place, so open windows follow at once. Columns that do not stretch take the width their content needs, and spare width is distributed in proportion to that.
- Why in the footer: the narrow-window checks need the header's width for the title.
- Not done: a size for the EDMC panel or the overlay cards (EDMC and Settings → Overlays → Appearance control those), and dragging a column border.

### 3.27 Color themes for WFMT's own windows

- Problem: one fixed palette did not suit all commanders.
- Decision: four themes (Navy, the default, and Cyan, Amber and Green), one choice for every pop-out window, from Settings or the window's bottom line. Open windows are recolored by mapping each old color to the new one, because the windows are built from the palette's attributes and keep what they were given.
- Why a color map and not a rebuild: windows hold state (selections, scroll positions, a search in progress) that a rebuild would lose.
- Required rule: palette colors are read when a widget is built. A color fixed at import time or as a default argument would remain in the old theme, so the kit uses `None` defaults and token names.
- Not done: a light theme, themes for the overlay cards (Settings → Overlays → Appearance has its own schemes) and anything in EDMC's own window.

### 3.28 Pages are windows, and a window's settings are set there (1.5.0)

- Decision: Trade, Mining and Missions no longer page the main panel with ◀ ▶ arrows. The panel is a short summary with a button for each page, and each button opens that page as a window. The display and tuning settings that belong to a window are set in it and nowhere else. File → Settings → WFMT keeps the permissions and states where the other settings moved.
- Why: EDMC's main window is small and is sized by the widest row of every plugin. The arrows had already been enlarged once because they were too small to see. A window can be large, can be placed on a second screen and updates alongside the panel. A setting in both Settings and a window gives two places to find it; a single place, saved on change, avoids this.
- Compatibility: the saved values and config keys did not change, so nothing is migrated or lost. A window cannot turn on a permission (the Raven master switch, the lookups that contact Spansh or EDSM), so granting one remains a deliberate action in Settings.
- Supersedes: the page arrows (`panelkit.nav_arrow`, no longer present in the code) and the earlier notes about Mining, Trade and Missions pages on the panel.
- Type-ahead in name boxes belongs to the same release: a box that takes a name that WFMT already holds (bodies, rings, ships, commodity lists) suggests it while typing, from local data only.

### 3.29 The Combat Record, and one table of ship names (1.5.1)

- Decision: kills and deaths are counted per ship and per session in a record of their own (`combat_record.py`), kept per commander. A session is one game login, identified by the journal file it was played in, which is the rule `session_credits.py` already uses. Totals are kept apart from the sessions, so the limit on listed sessions never changes them.
- Why the journal file: it is the same whether the event arrives live or is read back later, so one session is one record whichever way it was seen. A time gap or a `LoadGame` count would give a live session and a rebuilt one different boundaries.
- Why `through` and `seen`: the journals are read once at start-up, and EDMC delivers the live events of the same file. The newest counted timestamp plus the fingerprints of the events at that second counts an event once however it arrives, and still counts two different events of one second.
- Ships: a ship is its type and the game's number for it, so a rename does not split a row. The SRV and on foot are rows of their own, because a kill in them is not the ship's. The vessel is followed from the events that change it; a login made on foot is not reported by the game, so that case is an estimate (stated in the guide).
- Not counted: a kill that pays no bounty or bond and is not a PvP kill is not in the journal. `CapShipBond` is left out so a capital ship is not counted twice.
- Ship names: the journal gives `Ship_Localised` for only some ships, and a newer ship can have only a codename (`smallcombat01_nx`). `ship_names.py` uses the game's own name when given, then one table built from a long-time player's journals, then the internal name tidied into words. The Combat Record, the Expedition Log and Trade use it, replacing three tables that disagreed on what they covered. A landing pad is still never guessed for a ship the pad table lacks.
- Materials this session: counted from `MaterialCollected` only (a pick-up from the world), kept per commander with the journal file's name, and filled once from that file when WFMT meets a login it has not seen, so pick-ups made before EDMC started count. A trade, a reward or a craft is not collecting.
- Presentation: short figures that belong side by side (this session against all time, held against picked up) are shown in aligned rows (`panelkit.StatRows`), not in one wrapped sentence. The rows hold only the plugin's own short labels, so they cannot widen EDMC's window.

---

## 4. Deliberately not built

Each item was considered and not implemented. They are in the "Not planned" list of [TODO.md](TODO.md).

- Guardian ruin and structure surveying.
- Landing-pad layouts that the journal cannot supply.
  - The journal gives a facility type, an economy, the pad counts and a pad number, but no layout variant, orientation or pad positions.
  - A diagram of the pad positions of a particular station would therefore be invented. Landing Assist draws the diagrams it can from the data the journal provides.
- An FSS spectrum guide.
  - The journal does not record where a signal sits on the scanner's band.
  - The ranges would have to be measured in the game.
- Estimating the jump range for the current load (3.7), and assuming a screen size where it cannot be read (3.2), under the first principle: a value WFMT cannot know is not produced.

---

## 5. Lessons that keep coming back

- Examine the actual source before building a model of it.
  - Reading how Spansh's page builds its request removed the need for an approximate range (3.7).
  - The survey rebuild rule (3.8) comes from real saved files and journals.
- Use the record, not a counter. The visit count, the saved-record-exists check and the "scanned" flag are three different answers to the same question; the one that mirrors a fact is the one used.
- Keep one source of truth and let the views share it. The Dashboard, the cards and the panel read the same survey and the same Organic Scanning view.
- The restore is as careful as the backup. A restore applied while the program is running is overwritten by it.
- A rejected idea is recorded with its reason. The compact-data note (3.5) states why a database was deferred; the Not planned list states why an item is excluded.
- A test is written so that it fails without the rule it guards. The relog test and the group-hide tests follow this.
- Tests are deterministic. A helper based on Python's randomized `hash()` makes a test fail intermittently, so ids in tests are assigned and not hashed.
