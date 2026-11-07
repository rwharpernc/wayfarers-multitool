# WFMT Technical Guide

This document is the technical reference for Wayfarer's Multitool (WFMT): how the plugin is built, the reasons for the structure, and the rules that apply when modifying it.

Related documents:

- Feature descriptions for users: [README](../README.md).
- Feature specifications: [Missions](MISSIONS_TECH_SPEC.md), [Mining](MINING_TECH_SPEC.md), [Trade](TRADE_TECH_SPEC.md), [Boxel Survey](BOXEL_SURVEY_TECH_SPEC.md), [BGS](BGS_TECH_SPEC.md), [Organic Scanning](ORGANIC_SCANNING_TECH_SPEC.md), [Powerplay](POWERPLAY_TECH_SPEC.md) and [Screenshots and input automation](SCREENSHOTS_AND_INPUT_TECH_SPEC.md).
- Overlay setup: [OVERLAY_SETUP.md](OVERLAY_SETUP.md).
- Design rationale and discarded approaches: [DESIGN_NOTES.md](DESIGN_NOTES.md).
- Acknowledgements: [ATTRIBUTIONS.md](ATTRIBUTIONS.md).
- License notices: [THIRD-PARTY-NOTICES.md](../THIRD-PARTY-NOTICES.md).

**Contents**

1. [Where WFMT runs](#1-where-wfmt-runs)
2. [Repository layout, build and deploy](#2-repository-layout-build-and-deploy)
3. [Startup and event flow](#3-startup-and-event-flow)
4. [The feature-module contract](#4-the-feature-module-contract)
5. [Keeping the main window from growing](#5-keeping-the-main-window-from-growing)
6. [Pure logic versus UI](#6-pure-logic-versus-ui)
7. [Threading and network calls](#7-threading-and-network-calls)
8. [Persistence](#8-persistence)
9. [Journal, Status.json and CAPI](#9-journal-statusjson-and-capi)
10. [The overlay](#10-the-overlay)
11. [External services](#11-external-services)
12. [Feature notes](#12-feature-notes)
13. [Self-update](#13-self-update)
14. [Testing](#14-testing)
15. [Gotchas](#15-gotchas)
16. [Adding a feature](#16-adding-a-feature)
17. [Known gaps](#17-known-gaps)
18. [Platform support: Windows and Linux](#18-platform-support-windows-and-linux)

---

## Data-source principle

The game writes journal files and the live `Status.json`. Not every game state is logged. WFMT is journal-first: each feature starts from events the game writes. Where the journal has no data, WFMT adds sources in this order:

1. Frontier's data when EDMC is signed in (CAPI: a carrier's cargo, the Carrier Locker).
2. Data reported by players and communities (Spansh, EDSM, Canonn, edastro, Raven Colonial; section 11).
3. Its own bookkeeping, estimates and user steps (for example opening Carrier Management so the game writes `CarrierStats`), each labeled as such.

Each gap and its workaround is recorded in the matching user guide (the "What the game does and doesn't tell us" table) and, where it affects the code, in the sections below.

## 1. Where WFMT runs

WFMT is a plugin loaded into **EDMC** (Elite Dangerous Market Connector), a Python/Tkinter desktop application that reads the game's journal files and calls plugin hooks. Consequences:

- EDMC owns the process, the window and the event loop. WFMT does not create a Tk root or a main loop. It receives a parent frame and fills it.
- EDMC calls WFMT; WFMT does not poll for journal events. Status.json and CAPI data arrive through separate hooks (section 9).
- The main window is shared by every installed plugin (section 5).

EDMC discovers a plugin by finding `load.py` in a folder under its `plugins` directory, and calls a fixed set of module-level functions when they exist.

## 2. Repository layout, build and deploy

```
plugin/           everything that ships; becomes the Wayfarers-Multitool folder
  load.py         EDMC entry point (the hooks)
  ui.py           main panel, mode buttons, Settings tab: orchestration only
  panelkit.py     shared Tk helpers (wrapping, separators, toggles, tooltips, collapsible sections, theming)
  overlay.py      the shared overlay client
  update.py       the self-updater
  <feature>*.py   one or more modules per feature (every module is listed in MODULES.md)
tests/            unittest suites
.github/          ISSUE_TEMPLATE/bug_report.yml and game_data.yml, the forms opened by the Report an issue and Report game data buttons (not shipped in the zip)
.githooks/        commit-msg (enforces the commit message form) and pre-commit (runs scripts/check_docs.py); enabled with core.hooksPath
docker/           Dockerfile and run-tests.sh for the headless test run (`npm run test:docker`, via scripts/docker-test.mjs)
scripts/          development only, not shipped:
  build.mjs, package.mjs, env.mjs     build, zip and install the plugin (env.mjs finds EDMC's plugins folder)
  gen_journal_blueprints.py           regenerates plugin/journal_blueprints.py from public lists (needs the network)
  gen_organic_variants.py             builds plugin/organic_variant_data.py from published color-variant rules
  verify_organic_variants.py          checks the color predictions against local journals
  analyze_exo_observations.py         checks the species prediction against the recorded finds
  native_overlay_test.py              draws overlay cards over Elite (Windows only)
  check_docs.py                       checks the docs against the code (links, screen labels, Settings paths, file names, code references, version)
  docker-test.mjs                     runs the tests in the container (`npm run test:docker`)
docs/             this file, the development guide, the feature specifications, the overlay guide, acknowledgements
```

[MODULES.md](MODULES.md) lists every module with a one-line description; `tests/test_docs_modules.py` keeps it complete.

Build and packaging:

- `npm run build` copies `plugin/` to `dist/Wayfarers-Multitool`, skipping `__pycache__` and `.pyc`, and copies `LICENSE` and `THIRD-PARTY-NOTICES.md` into it.
- `npm run package` zips that folder with `Wayfarers-Multitool/` as the top level of the zip.
- The scripts copy files and call a zip tool; `package.json` provides the `npm run` entry points. No Python packaging step exists because EDMC loads plugin source directly.
- WFMT is GPL-3.0 and carries third-party data whose notices must accompany it. Copying the notices at build time places them in every installed copy.

Deploying a build to EDMC:

1. Copy `dist/Wayfarers-Multitool` into EDMC's plugins folder as a merge. Do not delete the folder first: a live plugin folder holds per-commander data files that are not in the build (section 8).
2. `npm run deploy` performs the merge for the current OS.
3. Restart EDMC to load the new code.

See [DEVELOPMENT.md](DEVELOPMENT.md).

## 3. Startup and event flow

`load.py` implements EDMC's hooks:

| Hook | When EDMC calls it | What WFMT does |
|---|---|---|
| `plugin_start3(plugin_dir)` | Once, at load | Starts stateful features, wires the shared overlay client into each overlay feature, registers overlay groups, starts the update check |
| `plugin_app(parent)` | When building the main window | `ui.create_plugin_app(parent)` builds the panel |
| `plugin_prefs(parent, cmdr, is_beta)` | When Settings opens | Builds the WFMT Settings tab |
| `prefs_changed(cmdr, is_beta)` | When Settings is saved | Each feature persists its settings |
| `journal_entry(...)` | For every journal event | Forwards to every feature (below) |
| `dashboard_entry(cmdr, is_beta, entry)` | Whenever Status.json changes | Forwards flags and position to the features that need them |
| `capi_fleetcarrier(data)` | When fleet carrier CAPI data arrives | Inventory (the Carrier Locker) and Colonization (the carrier's cargo hold) |
| `plugin_stop()` | EDMC closing | Flushes state, closes the overlay connection |

### Forward unconditionally, gate inside

`journal_entry` calls:

```python
feature_dispatch.dispatch(_FEATURES, entry, cmdr, system, station, state, logger)
```

- Every feature receives every event and decides whether the event is relevant and whether the feature is enabled.
- `feature_dispatch.dispatch` calls the features one at a time. An exception in one feature is logged with its traceback and the event name, and the remaining features still receive the event.
- `tests/test_feature_dispatch.py` also fails if a plugin module uses a name it never defines.
- Handlers only read `entry` and `state`; none mutates them, so handler order does not affect results.
- Routing by event type in `load.py` is not used: `load.py` would need to know which events each feature reads, and adding a feature would require editing the central file. Each handler returns after one or two dictionary lookups.

### Catching up after an EDMC restart

EDMC replays nothing to plugins. A feature that must not miss play while EDMC is closed reads the journals itself.

- `journal_files.py` is the shared part: the folder, the files changed since a given moment, and a filtered event reader.
- The rule that prevents counting an event twice belongs to each feature and is a watermark or an idempotent merge:
  - Trade: `trade_journal_scan.py`, timestamps per fact
  - Powerplay: `powerplay_backfill.py`
  - BGS: `bgs_journal.py`
  - Missions: `journal_scan.py`
  - Colonization: `colonization_catchup.py`, per-site `journal_at`
  - Codex: `CodexTally.last_event_at`
  - Boxel Survey visited systems: a set union

## 4. The feature-module contract

Every feature module exposes the interface that `ui.py` and `load.py` use:

| Name | Purpose |
|---|---|
| `PANEL_PLACEMENT` | A mode key (`"exploration"`, `"mining"`, ...) to build inside that mode's frame; `"always"` to build once outside any mode; or `None` for a Settings-only feature |
| `build_panel(parent)` | Builds the main-window widgets (skipped when the placement is `None`) |
| `build_settings(notebook)` / `save_settings()` | Builds and persists the feature's Settings tab |
| `handle_event(entry, cmdr, system, station, state)` | Reacts to journal events |

Larger features add `start(plugin_dir)` and `stop()` for loading and flushing state, and optionally `set_overlay_client(client)`.

With this contract, `ui.py` walks the `FEATURES` tuple, builds each feature into its own child frame with a separator between, and does not depend on feature internals. Adding a feature requires one module and an entry in two tuples: `FEATURES` in `ui.py` and `_FEATURES` in `load.py`.

### panelkit.py

- Feature modules import `panelkit`, never `ui`. Importing helpers back out of `ui.py` from a popup window would create a circular dependency; `panelkit` holds the shared, content-independent helpers so both sides import it.
- `panelkit.accent_color()` returns the accent orange for headings, warnings and the page buttons on the main panel. EDMC's Dark and Transparent themes use `ACCENT_ON_DARK` (contrast 8 to 9:1). EDMC's light Default theme uses `ACCENT_ON_LIGHT` (4.5:1 or better), because `ACCENT_ON_DARK` has 1.7 to 2.3:1 there. `tests/test_panel_accent.py` checks the ratios.

### Stacking and pairing

- `ui._stack_features` gives each feature its own frame and inserts a separator between consecutive frames. Features do not choose their own grid rows.
- A `_SIDE_BY_SIDE_PAIRS` table places two narrow features (Auto-Honk and Discovery Alerts) in one row.
- That row also carries the Neutron Star and White Dwarf buttons (built by `discovery.py`) and Boxel Survey's Random button (`boxel_survey.build_random_button`, called from `ui.py` with `discovery.controller.button_row`, so it remains usable while Boxel Survey is collapsed).
- Every button in the row is packed with the same 6 px gap as the mode buttons.
- The Neutron Star / White Dwarf result line and Random's status line are below the row.

### Button names and tooltips

- Every button, on the main panel and in the pop-out windows, has a tooltip in the form "Name - what it does". `panelkit.add_tooltip` provides it. A window button passes the text as `tip=` to `FlatButton`, `shell.add_action` or `shell.add_menu`. The tip may be a function, evaluated each time the tooltip opens, for a button whose caption changes with its state. The user guide's "Button names" lists the panel's buttons.
- The tooltip is a borderless `Toplevel` (`uikit/tooltip.py`, re-exported by `panelkit`). It appears after `TOOLTIP_DELAY_MS` (500 ms) and wraps at `TOOLTIP_WRAP` (280 px), so it cannot affect the main window's size.
- The mode buttons carry the `PANEL_MODES` labels as written. Their tooltips are in `ui._MODE_TOOLTIPS`.
- EDMC sizes its window to the widest row across all plugins, and the mode row is WFMT's widest. A row that could pass that width wraps (`panelkit.flow_buttons`). The width is held at the size measured from a row of full-label buttons (`ui._mode_row_full_label_size`), which the panel buttons match.
- A thin spacer widget in the same grid cell must not be used to hold the width: it draws a line across the buttons.

### Settings layout

- `ui._build_settings_tabs` builds eleven top-level Settings tabs, sorted alphabetically by label (`_sort_tabs`): BGS, Colonization, Discord, Exploration, General, Mining, Missions, Operations, Overlays, Powerplay and Trade.
  - General holds the tabs Window, Updates, Backup, Help, Online lookups and Shortcuts.
- A group is a plain tab holding its own `nb.Notebook` (`_settings_group`). Everything is placed with `grid`.
- A feature with settings that is not listed lands in an "Other" group.
- Every page is wrapped by `settings_scroll.scrolled_page`, which caps its visible height (between 260 and 640 px, derived from the screen height less 530 px for the window chrome) and adds a scrollbar beyond it, so a long page cannot push EDMC's Settings window and its OK button off the screen.

**Settings that live in a window**

From 1.5.0 the display and tuning settings of a feature that has windows are set in those windows only. The Settings tab of such a feature keeps its permissions (the switches that allow WFMT to contact Spansh, EDSM or Raven Colonial, the master switch and the key) and a line stating where the remaining settings are.

- Each window builds a Settings card, tab or strip from a field list. Every box or tick saves immediately (a box saves when Enter is pressed or focus leaves it). Saved values and config keys are unchanged; no migration is performed.
- A feature's settings module owns the config keys, readers and savers (`exploration_settings.py`, `colonization_settings.py`, `inventory_settings.py`, `bgs_settings.py`, `mining_window_settings.py`, `missions_display_settings.py`) and provides `add_listener`, so the panel, the Settings tab's variables and every open window redraw when one changes. These modules import nothing from the panel, which avoids a circular import.
- The cards are drawn by `mining_window_settings.py` (Space Mining and Surface Mining windows), `missions_display_settings.py` (the Display card of the Mission types window), `powerplay_settings_tab.py` (the Settings tab of the Powerplay Sessions window), `inventory_settings_tab.py` (the Settings tab of the Inventory window) and the Trade windows (`trade_windows.py`).
- A permission is never set from a window. The Colonization strip shows what is reported and holds the progress and carrier-cargo ticks, but cannot turn the master switch on; the ticks are disabled while it is off.

**Overlays group**

The Overlays group holds every overlay setting and toggle:

- Overlay Connection, Appearance, Overlay Placement and Hide overlays, then one tab per feature that draws on the overlay (Colonization, Discovery, Inventory, Interdiction Warning, Flight Alerts, Route, System targets, Body info, Exobiology, Expedition Log, Powerplay, Missions, Landing, Surface Compass, Mining, Notable Bodies, Screenshots).
- Interdiction, Landing, Discovery and Notable Bodies are entirely overlay features, so their whole `build_settings` is listed in the group.
- Colonization, Inventory, Mining and Screenshots keep their other settings in their own tabs (Colonization, Operations, Mining) and expose a second builder, `build_overlay_settings`, for the Overlays group. It shares the controller's variables, so `save_settings` is unchanged (it skips a variable whose tab was not built).

**Exploration group**

POI Reference (GEC and Canonn) and Codex share one "POI Reference" page. `_SectionStack` is an `nb.Frame` whose `add()` grids each feature's frame under the previous one. Features still call `notebook.add(frame, text=...)`.

### Height fitting

- Once a window has an explicit size, Tk stops fitting it to its content.
- `ui._sync_mode_holder_height` is the single place the panel's height changes (mode switch, startup, a section expanding). It schedules `ui._fit_window_height` once at idle.
- `ui._fit_window_height` sets the top-level window's geometry to its current width and the height its content requests (`winfo_reqheight`). It is skipped when the window is maximized, minimized or not yet visible, and it keeps the width and position.
- The Settings > Window tab has a checkbox (`wfmt_fit_window_height`, default on) that turns the behavior off. The tab is built with `grid` only (see section 15).

### Collapsible sections

- `panelkit.collapsible_section` provides the collapsible panel sections (POI Reference, Codex Completionist, Organic Scanning, Expedition and others): a clickable title with a ▸/▾ marker over a body frame.
- Every section starts folded each time EDMC starts. Opening a section lasts for the session and is not stored.
- Boxel Survey has its own equivalent, which also starts folded.

### Modes

`PANEL_MODES` in `ui.py` is the ordered list of mode buttons. Each mode has its own frame. Switching modes shows one frame and hides the others with `grid_remove`; no widget is destroyed or rebuilt. Hidden modes keep receiving journal events (section 3).

## 5. Keeping the main window from growing

EDMC sizes its main window to the widest row among all loaded plugins. A plugin that lets external content set a widget's width widens the window for the whole application. For example, a thumbnail capped by height only produces a very wide image from an ultrawide screenshot.

Rule: any widget in the main window whose size comes from variable data must have a hard upper bound on every dimension that affects layout.

### Session strip

Directly under the mode buttons (a frame at row 2 of the main frame, with a separator at row 3) are the lines shown in every mode: the plugin version, the game mode, credits, merits (once there is one, and not on the Powerplay page, which shows the session's merits itself), the Overlays shown line, and a catch-up line while one is running. The game mode and credits lines are feature modules independent of Powerplay and of each other. The other lines come from `session_merits.py`, `overlay_visibility.py` and `catchup_status.py`.

- `game_mode.py` shows the mode, for example "You are in Solo mode." (Open, Solo or Private Group with its name).
  - It is set from `LoadGame`'s `GameMode` and `Group`.
  - On `StartUp` (EDMC attached to a running game, no journal replay) it is recovered by reading the `LoadGame` line from the top of the current journal file.
  - It is cleared on `Shutdown`.
- `session_credits.py` shows "Credits this session: +N cr earned (+R cr/hr)" or "-N cr lost".
  - It keeps its own record of the current session (login balance, balance now, journal file, commander) in `session_credits.json`, read from `LoadGame`'s `Credits` and EDMC's `state["Credits"]` on every event.
  - The same journal file and commander form one session (a logout to the menu and back, or an EDMC restart, continues it). Any other combination starts a new session.
  - Writes are throttled to one per 30 s, plus start and stop.
  - `session_credits.json` is on the updater's keep-list. Powerplay's session store has no credit fields.
- Both modules are registered in `load.py`'s `_FEATURES` for journal events (`session_credits` also in start and stop) and built into the strip by `ui.py`.
- Text builders and session logic are pure functions with tests (`tests/test_game_mode.py`, `tests/test_session_credits.py`).
- The labels are `panelkit.wrap_label`s, so a long number or private-group name wraps instead of widening EDMC's window.

### Switching modes does not change the width

- Every mode's content sits in one holder in `ui.py`. The holder's width is pinned to the width of the mode-button row, and its height follows the mode being shown.
- Content wraps to that width instead of requesting more.
- A bare `tk.Canvas` requests 10 cm (about 378 px) of width, so scrolling panels (Mining, Missions) set `width=1` and stretch.
- The panel's feature frames place spare space in their second column, so a panel with a scrollbar column gives that column weight 0.
- `tests/test_panel_width.py` checks both.

### Sizing rules for variable content

- **Text from the game or journal** (station, system and faction names) is unbounded. `panelkit.wrap_label` creates a label whose `wraplength` tracks the room left of it in its container (the frame's width less where the label starts, `panelkit.available_wrap`), with a floor of `min_wrap` (`MIN_WRAP`, 300 px, unless the caller passes less).
  - A label beside a button receives only the rest of the row (the narrower of its position and the widths of its row neighbors, `panelkit.row_room`).
  - A label that has not been shown yet is re-wrapped when it is mapped.
  - The top-level frame's `<Configure>` event calls `panelkit.on_frame_configure` to update all wrapping labels.
  - When the panel widens by 40 px or more, `panelkit._note_growth` writes the widest widgets to EDMC's log.
  - A section that must not be the widest row in a narrow window (Expedition, Expedition Log, Materials, Nearest place to land, Notes, the Trade watch list) passes `min_wrap=200`. It wraps at 200 px in a narrow window and at the full width in a wide one.
- **Character limits are safety caps, not the means of fitting text.** A name is shortened with an ellipsis only beyond a cap: 64 characters for a station, system or site name, 40 for a commodity or material. The wrapping label determines how much is shown.
- **Images** are resized into a fixed box on both axes before display. `screenshots.py` defines maximum width and height constants for the inline thumbnail, the history thumbnails and the preview popup, and passes them to `screenshot_convert.thumbnail_photo_data`. Bounding one axis only is the failure this rule prevents.
- **Entry boxes and button rows** depend on the font. An Entry's `width` counts characters, so the same width requests about 190 px in one font and 266 px in another.
  - `panelkit.fit_entry(entry, max_px)` lowers the character count until the box requests no more than the cap.
  - `panelkit.fit_button_row(buttons, max_px)` lowers the buttons' inner padding and then the font (never below 7 pt) until the row fits.
  - The Notes and Surface Compass quick-add rows use both, capped at 190 px.
  - `panelkit.flow_buttons(container, buttons)` wraps a row of buttons onto a second line when the next button would pass the width EDMC's window is held at (the mode-button row, set once by `panelkit.set_row_cap`; the pure `flow_positions` decides where). The Mining button bar, Region Sweep's Discover row and the Waypoints list row use it.
- **Name boxes** (bodies, rings, ships, comma-separated commodities) receive type-ahead from `name_suggestions.py`, using the same list as the system and commodity boxes. The names are local; nothing is fetched (see "Name type-ahead" in section 9).
- **Trade pages** measure their number columns with the real font. When the figures would leave the title column under 110 px (a wide font), the cells use the small font. The title column never goes under 60 px; the title wraps instead of widening the window.
- **Windows with tables** (the Trade History window) size their minimum width from the widest table (`_fit_width`), capped at the screen width less 40 px.
- **Overlay-drawn or canvas content** uses fixed sizes set in code and not derived from data (for example, the Rhino coverage minimap is a fixed square).

For each new widget, the worst-case content size and the cap must be defined.

### External windows (`plugin/uikit/`)

Every external (Toplevel) window uses WFMT's own navy look instead of EDMC's theme (gold titles, cyan section labels and table headings, a bright footer message that is yellow, or cyan on Amber, and green for success). Main-window panels follow EDMC's theme. See `docs/WINDOW_FRAMEWORK_SPEC.md`. Rules for modifying these windows:

- **ttk is not changed globally.** ttk themes and stock styles (`TButton`, `Treeview`, ...) are application-wide, so `theme_use()` or restyling them would recolor EDMC's main window and every other plugin.
  - The kit uses classic tk widgets plus its own `FlatButton`, `Combobox`, `SlimScrollbar`, `Tabs`, `ProgressBar` and `DataTable` (a Label grid, not a Treeview).
  - `tests/test_ui_kit.py` fails if `plugin/uikit` touches the ttk theme or styles.
- **Themes.** `uikit/palette.py` holds the colors as module attributes (`P.BG`, `P.TEXT`, ...) and four themes in `THEMES`: Navy (default), Cyan, Amber and Green. `_from_variables` builds each from a few base colors (the theme's own color becomes `ACCENT`; `TITLE` is its amber). `palette.apply(name)` sets the attributes and returns a map of old color to new color.
  - `style.set_theme` applies the theme, re-skins and recolors every window `skin()` has seen (`_recolor`: color options, canvas items, text tags and the color strings a kit widget keeps), and calls the theme listeners (`DataTable` remaps its tag colors).
  - The theme is saved as `wfmt_window_theme` by `ui.restore_text_size`.
  - Palette colors are read when a widget is built, never at import time or as a default argument (use `None` and `x or P.TOKEN`). A table that maps a role to a color stores the token name and calls `getattr(P, name)` when it draws.
- **Text size.** `uikit/style.py` keeps one setting (`set_text_delta`, -2 to +6 points, saved as `wfmt_window_text_delta` by `ui.restore_text_size`).
  - `style.font` resizes its cached fonts in place. `scaled=False` gives a font that ignores the setting (used by the stat tiles and the status chips).
  - `skin()` gives plain widgets the same body font. `DataTable` listens (`add_text_listener`) and measures its columns again.
  - The A- and A+ labels are in the shells' footers (`_make_text_size_buttons`).
- **Table columns.** `DataTable._sync_widths` sizes a column that does not stretch to its content (the declared width is the minimum for an empty table) and distributes spare width in proportion.
- **Shell.** `uikit.shell.WindowShell` gives a Toplevel a header (title, subtitle, action buttons), a body, a wrapping status footer, a minimum size and saved geometry.
  - `uikit/placement.py` chooses the position: the saved one while it is on a connected monitor, otherwise centered over EDMC's window (`root._root()`) inside the monitor EDMC is on. With `wfmt_windows_always_on_edmc_monitor` the window is always placed there.
  - `place` is pure. Monitors come from `EnumDisplayMonitors` on Windows (work areas) and from the Tk virtual screen elsewhere. A minimized EDMC changes nothing.
  - The position is written as `WxH+x+y` with an explicit plus sign (`geometry_for`), because a bare `-2000` means 2000 px in from the right edge of the screen to Tk, which restored a window saved on a monitor left of the primary to the wrong place.
  - The shell does not touch EDMC config; the window passes `load_geometry` and `save_geometry` callables.
  - Windows are built hidden and shown once, after the content is laid out (`_present`), so they do not appear at a default size first.
  - Windows keep the module-level `show`, `refresh` and `close` singleton convention.
- **Skinning.** `uikit.style.skin(window)` colors the classic widgets created inside a Toplevel through Tk's option database, scoped by the window's own name (option patterns match names, not full paths).
  - Call it immediately after creating the Toplevel, before adding widgets.
  - Explicit `fg=` and `bg=` take precedence; status colors use this.
  - `theme.update()` is not called on these windows.
- **Tables.** `DataTable` implements the part of the Treeview interface the windows use (`insert`, `append`, `set`, `exists`, `clear`, `selection`, double-click) and adds sorting, `group=True` collapsible headings, and `visible_rows` (fit to content up to N rows). A bare `tk.Canvas` requests 7 cm of height, which props up its container; canvases are given an explicit height.
- **Display scaling.** Default and minimum window sizes are written in 96-dpi pixels and multiplied by `uikit.style.dpi_factor` inside `WindowShell`. New layouts are expressed the same way.
- **Width discipline.** Displayed text passes through `uikit.widgets.clip` or per-column `max_chars`. A `DataTable` column marked `stretch` is clipped to the width it receives (with an ellipsis, up to 300 characters), so its text does not widen the table.

## 6. Pure logic versus UI

Most features are split into layers:

```
xxx.py / xxx_tracker.py    pure logic, no Tk, no network        -> unit-testable
xxx_state.py               JSON load/save
xxx_client.py              network calls, no Tk
xxx_panel.py               Tk widgets, wiring
xxx_window.py / _dialog.py popups
```

Examples: `bgs_tracker.py` (parsing and tallying) and `bgs_panel.py` (widgets and polling); `organic_scan.py` and `organic_scan_panel.py`; `boxel.py` and `boxel_walker.py` and `boxel_survey.py`.

Tk code cannot run in a plain test, and EDMC-only imports (`config`, `theme`, `myNotebook`) do not exist outside EDMC. Logic modules that avoid both can be tested with `unittest` without launching anything.

Where a logic module needs only EDMC's `appname` for a logger, it uses a fallback so tests can import it:

```python
try:
    from config import appname
except ImportError:
    appname = "EDMarketConnector"
```

## 7. Threading and network calls

Tkinter is not thread-safe. Only the main thread may touch widgets, and slow work (HTTP) must not run on the main thread, because EDMC freezes while it waits. Network features use one pattern (see `canonn_poi_panel.py`, `boxel_survey.py`, `bgs_panel.py`):

1. A button click increments a generation counter and starts a daemon `threading.Thread`.
2. The worker performs the network call and puts `(generation, result)` on a `queue.Queue`.
3. The main thread polls the queue with `widget.after(200, ...)`.
4. For each result, the poller compares the generation with the current one and drops stale results.

- The generation counter makes the latest request win. A result from an earlier lookup (after a second click, or a change of commander or system) would otherwise overwrite newer state. Each new request invalidates all earlier ones.
- `after()` polling is used because a callback from the worker would run on the worker thread, and touching Tk from there can crash or corrupt the UI. The queue passes data across the thread boundary; `after()` runs the consumer on the main thread.
- The updater follows the same rule: it works in a thread, calls back with a plain version string, and `load.py` schedules the UI change with `frame.after(0, ...)`.

Trade mode (`trade_panel.py`) uses two simpler variants, because each has exactly one consumer:

- A lookup is a `_Job`: a daemon thread that fills in `result` or `error` and sets `done`, which an `after(500)` poller on the Tk thread reads. Only one job runs at a time. **Cancel** sets a `threading.Event` that the worker checks while it waits.
- The startup journal read for carrier cargo puts one result on a `queue.Queue` that the Tk thread merges.
- Neither touches a widget from the worker. There is no generation counter because a second request cannot start while one is running. A feature that can have several requests in flight uses the generation counter.

## 8. Persistence

### Two kinds of storage

- **EDMC's `config`** holds small settings and toggles: booleans, ints and strings.
  - Every key is prefixed `wfmt_<feature>_...`, which avoids collisions with EDMC and other plugins.
  - A key is read under its current name only. The few defensive readers (a one-time overlay reset, the placement keys of a slot, the Surface Compass's copy of the Mining waypoint's settings) are described where they apply.
- **JSON files in the plugin folder** hold data: sessions, hotspot catalog, survey log, BGS tallies, visited systems, ship builds.
  - Files include: `sessions.json`, `boxel_state.json`, `region_sweep_state.json`, `waypoint_route_state.json`, `visited_systems.json`, `survey_log.json`, `organic_scan_state.json`, `system_surveys.json`, `system_history.json`, `codex_completionist_state.json`, `bgs_state.json`, `powerplay_state.json`, `mining_hotspots.json`, `mining_ring_notes.json`, `mining_coverage.json`, `mining_body_cache.json`, `ship_builds.json`, `combat_record.json`, `stored_modules.json`, `colonization_sites.json`, `colonization_carrier.json`, `colonization_history.json`, `notes.json`, `materials.json`, `blueprint_wishlist.json`, `route_planner_route.json`, `carrier_route.json`, `mission_pins.json`, `engineers.json`, `trade_watch.json`, `surface_marks.json`, `expeditions.json`, `trade_ledger.json`, `trade_carrier.json`, `trade_stock.json`, `trade_history.json`, `trade_journal_scan.json`, `trade_route_start.json`, `overlay_settings.json`, `boxel_survey_export.csv`, `exo_observations.json`, `expedition_log.json`, `income_ledger.json`, `session_credits.json`, `mining_history.json`, `codex_catalog.json`, `rcc_keys.json`, `discord_webhooks.json`, `discord_templates.json`.
  - The complete set is `_OWN_DATA_FILES` in `update.py`, which every update, backup and restore protects.
  - `exo_observations.json` is the one data file that is global rather than per commander (facts about bodies and the species found there, pooled to check the prediction; no commander name is stored).
  - `codex_catalog.json` is a cache of a downloaded list, not commander data, and is protected from updates in the same way.

Files are used for structured and growing data because `config` is intended for settings. JSON files can be inspected, backed up and repaired by hand. Data lives beside the code, so deleting the plugin folder deletes it; section 13 describes how updates avoid that.

### Overlay settings are per commander

- Per commander: which overlay cards run, their options, every display's placement and Show tick, the screen scaling and mode, and the look (scheme, text size, opacity, font, corners, keep-showing).
- Shared, because they describe the machine: the overlay connection (which overlay draws, host and port), the shortcut keys and the layout picture's size.
- The overlay modules read EDMC's `config` directly. `overlay_profile.py` keeps the active commander's choices there and files every commander's choices in `overlay_settings.json` (the `commander_data.py` shape).
- `activate(cmdr)` runs at the top of `journal_entry` and when the last commander is restored at start-up.
  - It files the outgoing commander's choices, then loads the incoming commander's into the config.
  - For a commander seen for the first time, it files a copy of what the config holds, so nothing changes on screen.
- `save_current` runs when Settings are saved and when EDMC closes.
- A key a commander never saved is deleted from the config on a switch, so it falls back to its default.
- Choices saved before any commander is known go to the first commander seen.
- The keys swapped are `overlay_profile._FIXED` plus the per-display keys that `overlay_placement` registers.
- `tests/test_overlay_profile.py` fails on any new `wfmt_*enabled*` or `*overlay*` key that is not classified as swapped or as shared.
- A switch calls `overlay_placement.refresh` and re-sends the group offsets.
- A module that caches an overlay setting at start-up keeps the value until restart.

### Per-commander data

- Data that belongs to a commander is stored as `{ "<commander>": {...} }` in one file. Nothing about a commander's play is shared between commanders.
- The commander name is matched case-insensitively (`casefold`), which avoids a duplicate entry when the journal reports the same name with different casing.
- `commander_data.py` is the shared helper for new files.
  - The shape is `{"version": 2, "commanders": {key: {"name", "data"}}, "legacy": ..., "meta": ...}`.
  - The key is the trimmed, case-folded name. It is only a JSON key and never part of a file name, so nothing depends on case rules or forbidden characters of the operating system.
  - A reader handles a data file in the earlier non-per-commander shape: its content lands in `legacy`. The first commander seen claims it (hotspots, coverage, survey log). Where it mixes several commanders and cannot be split (the Codex tally), it is kept untouched while each commander is rebuilt from their own journals, and the untouched copy is removed after 60 days (`OLD_TALLY_KEEP_DAYS`, `codex_completionist_state.py`).
- Some per-commander files (`boxel_state.py`, `region_sweep_state.py`, `waypoint_route_state.py`, `bgs_state.py`, ...) use their own equivalent layout.
- When the active commander changes, a feature resets anything it kept in memory about the previous commander (Trade does this in `_reset_for_commander`; Exploration Value forgets the last data sales).
- `tests/test_data_files_per_commander.py` lists every protected data file and how it keeps commanders apart (or why it holds none) and fails for a new, unclassified file. `tests/test_per_commander_data.py` saves for one commander and loads for another for each converted store.

Trade's carrier records and per-commander carrier choice are keyed by the casefolded name (`trade_carrier.key_for`), because a journal can write `EXAMPLECMDR` where EDMC supplies `Examplecmdr`. The list of commanders seen is kept in one config key (`wfmt_trade_commanders`, "|"-separated) so the Settings tab can offer a choice for each commander.

### Atomic writes

- State is written to `path.tmp`, then `os.replace(tmp, path)`. `os.replace` is atomic on the same volume, so after an interruption (EDMC killed, power loss) the file is the old version or the new one, never a truncated one.
- Loads treat an unreadable or wrong-shaped file as "nothing saved" and log a warning.

### Bounded growth

- Data that would otherwise grow without limit is capped (for example, `sessions.json` keeps each commander's most recent 200 sessions).
- Derived numbers are not stored when they can be recomputed. Powerplay stores raw merits per activity and computes Control Points at display time from the current ratio settings, so a corrected ratio applies to old sessions.

## 9. Journal, Status.json and CAPI

Three data sources reach WFMT through three hooks. The journal is the only source that records the commander's play; what it omits is supplied from other sources (sections 11 and 17).

- **Journal events** (`journal_entry`): discrete events such as `FSDJump`, `Scan`, `Docked` and `MissionCompleted`. Most features run on these.
- **Status.json** (`dashboard_entry`): a live snapshot that the game rewrites about once a second. It is the only source of continuous position (latitude and longitude, used for Mining's surface bearing and coverage map) and of the flags bitmask (used for the earliest interdiction signal). Features that need position or flags cannot be driven by the journal alone.
- **CAPI** (`capi_fleetcarrier`): Frontier's authenticated web API, delivered by EDMC on a throttle. It supplies the fleet carrier's locker (Inventory) and its cargo hold (Colonization's carrier tally, which it replaces with the carrier's cargo when that is safe; see "Fleet carrier column" in section 12).

Status.json and the journal arrive through independent callbacks; no order between them is assumed.

### Saved-name migration (`legacy_names.py`)

British spellings in saved names were replaced with American ones. `legacy_names.migrate` converts existing user data.

- It runs in `plugin_start3`, after a pending restore, because an old backup restores the old names.
- It renames the three data files from their old names (`colonisation_sites.json`, `colonisation_history.json`, `colonisation_carrier.json`). If both names exist, the more recently saved file is used.
- It renames the `wfmt_colonisation_*` settings, the Colonization overlay slot keys, the saved mode key and the hidden-mode flag. A setting already saved under the new key is never overwritten.
- It renames the saved field names from their old names, `tonnes` and `analysed`, to `tons` and `analyzed` in every saved JSON file that has one.
  - Only a whole word in a key is renamed (the start or end of the key, or between underscores: `cargo_tonnes` becomes `cargo_tons`; the old spelling is matched only as a whole word). A key that merely contains the letters, such as a body named after a place, is not changed. Every old word in a key is renamed.
  - A rewrite that fails removes its temporary file.
- It reads a file's bytes first and rewrites only a file that holds an old name, so later start-ups only read.
- `data_backup.data_file_names` also lists the old file names, so an old backup still restores.

The game's own names are not renamed. The journal's `ColonisationContribution` and similar events, the `ColonisationShip` station type and the `Mission_Colonisation...` names keep the game's spelling, and the matching code accepts both.

### Catching up on state EDMC missed

A feature can start with an incomplete picture in these situations:

- **EDMC starts while the game is running.** EDMC synthesizes a `StartUp` event. Features that need current state (current system, region, active mining run) read the current journal file backward for the last `FSDJump` or `Location`.
- **EDMC starts while the game is not running.** No event arrives, so no feature knows the commander until the next login.
  - About four seconds after the panel is built, if no live event has arrived, `load.py` calls `restore.dispatch`.
  - The commander is read from the newest journal (`restore.latest_commander`, falling back to EDMC's own value), and every feature receives one `WFMTRestoreCommander` event with that `cmdr`.
  - The event is not `StartUp` or `LoadGame`, which mean a game is running (Game Mode, Powerplay and Credits would act on those). Features treat it as an unknown event and only learn the commander and load that commander's saved data.
  - A real login later behaves as before, for the same or another commander.
  - A feature that fails is logged and the others still receive the event.
- **The player relogs.** A relog creates a new journal file that does not replay earlier `FSSBodySignals`, `Scan` or `ScanOrganic` events. Organic Scanning therefore persists per-body state to disk (`organic_scan_state.json`).
- **A job that spans play sessions.** Trade's working session belongs to a commander and lasts until Reset, across logins, journal files and EDMC runs.
  - When EDMC next sees the commander, it catches the session up from the journal files written since the last event it counted (`trade_ledger.catch_up`), through the same code the live events use, and only adds.
  - Every event is idempotent (`already_counted`, by time and fingerprint), so replays and live repeats cannot double count.
- **A baseline event that is written only on request.** `CarrierStats` (the fleet or squadron carrier's cargo space) is written only when the Carrier Management screen is opened, and EDMC does not replay it at start.
  - Trade mode therefore replays the newest 40 journal files (`trade_carrier.BACKFILL_FILES`) on a background thread at startup, parsing only the event names it needs, to find the last baseline and the transfers after it.
  - See the [Trade spec](TRADE_TECH_SPEC.md#7-fleet-and-squadron-carrier-cargo-space).

**Features whose state is rebuilt from recent journals at start-up**, each with its own rule against counting an event twice (`journal_files.py` provides the shared file finding and reading):

- Missions (`journal_scan.py`, two weeks): accepted missions, kills (`Bounty` and `FactionKillBond`), redirects, Community Goals and `CargoDepot` progress.
  - The active set is normally the login `Missions` event, which EDMC never replays, so it is also derived from the journals: the newest `Missions` list, plus each `MissionAccepted` after it, less each `MissionCompleted`, `MissionAbandoned` and `MissionFailed`. The next real login list replaces it.
- Colonization (`colonization_catchup.py`, 14 to 30 days): depot snapshots (idempotent) and contributions (additions).
  - Each site carries `journal_at`, and only a newer event is applied. A site saved before that field existed uses its `updated` time. The live path uses the same guard.
- Colonization fleet carrier transfers (`colonization_carrier.py`, same 14 to 30 day window, oldest watermark): a `CargoTransfer` made while docked at a `FleetCarrier` station adds or removes tons for that commodity (floor zero).
  - Transfers are additions, so each commander's record keeps `journal_at`, and only a newer transfer is applied. The live path uses the same guard.
  - Market purchases, sales, trade orders and other players' moves are not transfers. The figure is the amount seen transferred, not the carrier's hold.
- Codex Completionist (`scan_since`): the active commander's tally only.
  - It reads the files written since its `last_event_at` watermark and counts each newer `CodexEntry` once (a file states whose events follow).
  - A new install only sets the watermark.
  - A commander first seen after the tally became per commander is rebuilt once from all their journals.
- Boxel Survey's visited systems (`visited_systems.arrivals_since`, 14 days): a set union, so no watermark is needed.
- Trade's route start (`trade_route_start.py`), with the time of each dock so that an older file read later cannot override a newer one.
- Inventory has no journal pass: on `StartUp` it syncs from EDMC's own state, which EDMC rebuilds from the journal.
- Exploration Value replays the current journal file for the system's scan progress and the last data sales.

Not automatic:

- Codex Completionist's full backfill ("Backfill Journals" in the My Codex window) is started by a button, because reading years of journal files is substantial I/O.
- Boxel Survey's survey log is not caught up, because its `bodies_scanned` counter is not idempotent and a replay would double-count.

### Reading journals defensively

Fields the game documents poorly are handled conservatively.

**Interdiction Warning**

- It combines three signals: the Status.json flag, NPC `ReceiveText` messages restricted to `Channel == "npc"`, and the `Interdicted` and `EscapeInterdiction` events. The three arrive through independent callbacks with no ordering guarantee.
- The channel restriction exists because squadron and system chat contain words such as "pirate" with no interdiction occurring.
- `is_threat(raw, localised)` classifies an NPC line in this order:
  1. The raw `Message` key (`is_hostile_key`): `startinterdiction`, `hunterhostilesc_relevant` and `hunterhostile_relevant` for Pirate, Hitman, CargoHunter and BountyHunter, `hitmanmissionfailure_onenemydetect`, `onstartscancargo`.
  2. `is_benign_key`: `$distresscall`, `$ambushedpilot`, `$escort_`, `$minerenemy`, `$contactcovert`, `$station_`, `$comms_`, `$cruiseliner_`. These are never a threat regardless of wording.
  3. Only for a key known in neither list, the wording (`CHAT_THREAT_PATTERNS`).
- The key lists were derived from 291 interdictions in a commander's journals (`plugin/interdiction.py`). `tests/test_interdiction_messages.py` uses real keys.
- The tracker keeps the NPC lines of the last 75 s (`_RECENT_NPC_S`). An `Interdicted` or `EscapeInterdiction` that arrives with no earlier warning logs them at INFO (`_note_if_unannounced`) and clears them.

**Surface Compass** (`surface_compass.py`, `surface_marks.py`, `surface_marks_window.py`)

- Live position (`Latitude`, `Longitude`, `Heading`, `PlanetRadius`, `BodyName`, `Flags` bit 21 `HasLatLong`) comes from `Status.json` through EDMC's `dashboard_entry`, in `load.py` after Mining has refreshed `mining_live_position` from the same entry.
- Great-circle distance and initial bearing are computed by `mining_bearing.py` on a sphere of the body's radius (the body's `Scan` radius when `Status.json` has none).
- The target is the book's choice: `auto` (the nearest recorded hotspot with a position for the journal's current system and body), `none`, or a mark's id. A mark is pointed at only when its body name, trimmed and case-folded, matches the body the commander is on.
- Marks and the choice are per commander in `surface_marks.json` (`commander_data.py`; 500 marks, names of 60 characters, body names of 100).
- The overlay card (an arrow vector, a backing panel and one line of text; group `wfmt_compass`, placement slot `surface_compass`) is drawn on every `Status.json` update while enabled and cleared once when there is no reading.
- `migrate_old_waypoint_settings` (recorded by `wfmt_compass_migrated_v1`) copies the settings of a Mining waypoint overlay (enabled flag, placement, hidden flag), when present, to the compass's own keys once.
- The panel row's summary label wraps at 200 px. The quick-name box starts at 26 characters and is lowered until it requests no more than 190 px (`panelkit.fit_entry`).

**Materials and Engineering** (`materials.py`, `materials_panel.py`, `materials_window.py`, `blueprints*.py`, `engineers.py`, `material_traders.py`)

The Operations section is titled Engineering (its collapsed-state key is `wfmt_materials_collapsed`). It is listed first in Operations because the sections are in alphabetical order. Its buttons are laid out by `panelkit.flow_buttons`, and `blueprints_window.show(..., tab=)` opens the window on a given tab.

- The commander's Raw, Manufactured and Encoded counts are kept in `materials.json` (`MaterialBook`, per commander).
  - The login `Materials` list sets them, then each journal event that changes a count adjusts it, within the grade limits (300 to 100).
  - EDMC's own totals fill in a mid-session start.
- Static data:
  - The blueprint table: `blueprints_data.py`, trimmed from a public table and corrected (source and license: docs/ATTRIBUTIONS.md and THIRD-PARTY-NOTICES.md).
  - Yi Shen's unlock: `blueprints_extra.py`.
  - The engineer location table: `engineers_data.py`, read through `engineers.info`, which also gives the region (Bubble, or within 500 ly of Colonia). The Engineers tab's Show choice is kept in `wfmt_engineers_region`.
- Per commander: `blueprint_wishlist.py` (`blueprint_wishlist.json`) and `engineers.py` (`engineers.json`, from `EngineerProgress`).
- The Engineers tab (`blueprints_window.py`):
  - `engineer_path.build` produces the numbered path to one engineer, with the engineers to deal with first. `next_action` is the Next step column.
  - `engineer_requirements` compares a rank or lifetime figure in an invitation requirement with the commander's `Rank`, `Promotion` and `Statistics`. These are kept per commander in `engineers.json` and read once from the newest journals if EDMC started after the login.
  - `_engineer_tag` colors the row: `unlocked` (green), `progress` for Known or Invited (yellow), `unavailable` for an engineer the game has not listed or has barred (red). No tag is applied until the game has listed any engineers. The colors are `palette.ENGINEER_UNLOCKED`, `ENGINEER_PROGRESS` and `ENGINEER_UNAVAILABLE`, fixed rather than theme tokens, because the Amber and Green themes' own green and yellow are close. `tests/test_window_themes.py` checks their contrast on every theme and their hue and lightness gaps.
  - `_render_engineer` writes the selected engineer's details into a `uikit.richtext.RichText` pane: a read-only `tk.Text` with tags for a title, subtitle, headings, bold labelled rows, hanging-indent steps and bullets. It is sized to its text and follows the text size setting. A link is a tag that calls `webbrowser.open`. The pane takes focus on a click so that Ctrl+C, Ctrl+A and a right-click menu copy from it; `copy_all` is behind the Copy details button. The engineer's system links to `powerplay_clipboard.inara_system_url`.
  - `engineer_path.describe_step` splits a step into its label and detail.
  - `_render_items` lists the unlock items (`blueprint_needs.needs_for`), each classified by `ingredient_sources.classify` (kind and `found` hints), with the finders of `blueprints_window.Tools` (supplied by `materials_panel`: `mission_sources_window.show_for`, `material_trader_window.show`, `canonn_poi_panel.controller.start_lookup`), then the guide from `engineer_guides_data.GUIDES` when one exists.
  - It adds `VERIFY_TEXT` ("Verification needed") for an engineer whose requirement `engineers.requirement_checkable` reports as not checkable.
  - The **Report engineer data** button calls `issue_report.open_feedback("Engineers", <engineer>, "Standing in WFMT: ...")`, which opens the Game data form (see "Report an issue and Copy diagnostics" in section 12).
- `blueprint_needs.py` computes what a blueprint or the wishlist needs against what is held (ship materials and the Odyssey ship locker).
- The material trader finder is the only online part. When **Find** is pressed, it passes the system and the trader type to Spansh's station search on a worker thread, with a two-minute cache. Nothing else is sent.

**Expedition planner** (`expedition.py`, `expedition_window.py`, `expedition_panel.py`)

- Named expeditions of ordered stops are kept in `expeditions.json` (`ExpeditionBook`, per commander), one active at a time.
- The panel feeds arrivals from the journal and ticks the stop whose system matches, counting jumps and distance.
- Two online operations exist, both started by a button press.

*Spelling and names*

- Adding or changing a stop respells it without a network call where possible: first the system the commander is in, then any stop already spelled that way (`expedition_window._spelling`).
- While the box under the editor is ticked (`wfmt_expedition_lookup_names`, on unless turned off), the names just added are looked up in EDSM in the background (`_look_up`, 50 per request).
  - `ExpeditionBook.canonical_names` takes EDSM's spelling for stops whose names match ignoring case and spacing.
  - `set_coords` gives them a position.
- **Locate and reorder (EDSM)** sends system names to EDSM for their positions and orders the stops by nearest neighbor.

*Spansh planners*

- **Road to Riches** and **Exomastery** (`spansh_planners.py`, `expedition_plan_dialog.py`) post the start system, the optional end and the chosen numbers to Spansh's `/api/riches/route` or `/api/exobiology/route`.
- They poll `/api/results/<job>` on a worker thread and turn the systems of the answer into a new expedition.
- Each stop is a system with its best body, a note of what the bodies are worth, and Spansh's position for the system.
- The jump range offered is the last `Loadout`'s `MaxJumpRange`.
- The endpoints are undocumented. The request and result shapes were taken from Spansh's own page and a live answer (see the module's docstring).
- The **Neutron route** button opens the Route Planner window.

**System-name type-ahead**

- System-name boxes receive type-ahead from `system_autocomplete.attach(entry, var)`.
  - It places its own bindtag ahead of the box's, so Enter, Up, Down and Escape are seen first (consumed with "break" only when a suggestion is highlighted or the list is open). The box's own Enter handling still runs otherwise.
- The list is a borderless Toplevel under the box, colored from the box itself so that it fits both WFMT's dark windows and the themed EDMC panel.
- Suggestions are `system_names.local()` from two letters: the systems seen by `load.journal_entry`, then sources such as the expedition stops and notes registered with `add_source`.
- Spansh's `/api/systems/field_values/system_names?q=` answers are added from three letters when `wfmt_system_suggest_spansh` is on (off by default). The call is debounced by 350 ms, runs on a worker thread and is cached by typed start for the session.

**Name type-ahead** (`name_suggestions.py`)

- Systems use `system_autocomplete` and a single commodity uses `commodity_autocomplete`. `name_suggestions` covers the rest, on the same popup list and keys.
- The entry points are `attach_bodies` (the bodies and rings of the system typed beside the box: the system survey, the system's saved hotspots and an earlier body lookup), `attach_ships` (the ship names the game uses) and `attach_commodity_list` (a comma-separated box; suggestions are for the entry being typed). `FormDialog` fields of type body, ship and commodity use them.
- It is local only: the names come from data WFMT already holds, and nothing is fetched.
- Boxes that use it: the Body boxes (Add hotspot, Expedition stops, Surface marks, Notes), the Ring and Body or ring boxes, the Ship box of a ship build, the Also check boxes of the mining price lookups, the Hotspots box of Add a ring, the Add a ring and Expedition Log location system boxes, and the Carry only this commodity box in Routes.
- `tests/test_name_suggestions.py` (with `tests/name_suggestions_smoke.py`) covers the matching and the attached boxes. A Body field in a form looks up its System field when the box is used, so the order of the two fields does not matter.
- Boxes in a window that save a setting (`commit_entry.bind_commit`) commit on Return or on leaving the box only when the text differs from what it held on entering. Tabbing through unedited boxes, or Return followed by leaving, therefore saves at most once (`tests/test_commit_entry.py`).
- A window that redraws on a journal event or the timer (Mission types) keeps its scroll position when the same type is redrawn (`ScrollFrame.position` and `restore_position`).

**Missions card** (`missions_overlay.py`)

- A small text card with pure layout (`build_lines`, in the Missions specification section 10b) apart from drawing.
- One fixed width, with lines clipped to `LINE_CHARS` (46). It is drawn through the shared overlay client at the "Missions list" placement slot (`overlay_placement.SLOTS`, group `wfmt_missions`, registered in `load.py` with the other groups).
- It follows the commander's system and `FSDTarget` from the journal and rereads the Mission mode's active missions on every change and every 30 s.
- Nothing is stored.

**Chemistry** (`chemistry.py`)

- It is the single place that writes a substance in short form (element symbols, formulas for the gases and compounds of an atmosphere and volcanism; `element`, `gas`, `shorten`, `label`).
- The style is saved under `wfmt_chemistry_style` (symbols by default).
- The Body info card is its only user. Other displays that name chemicals (Engineering, Materials) use full names.

**Expedition Log** (`expedition_log.py` model, `expedition_log_panel.py` journal hook and the Log lines in the panel's Expedition section, `expedition_log_window.py` archive window, `expedition_log_overlay.py` card)

- Per-commander `Run`s are kept in `expedition_log.json` (`commander_data.py`).
- A `Tally` adds each journal event to the running expedition:
  - `FSDJump`, `CarrierJump` and `Location` for systems, jumps and light-years
  - `Scan` for bodies, first discoveries and the scan-value estimate
  - `SAAScanComplete` for mapping
  - the exploration and exobiology sale events for earned credits
  - `ScanOrganic` for samples and species
  - `CodexEntry`, `Touchdown`, and `Loadout` for ships
- Bodies are kept in per-run lists so that a body is counted once.
- `rescan` replays the commander's journals (each begins with their `LoadGame`) between the run's start and end through a fresh `Tally`, leaving out the events inside the run's `gaps`.
- The clock and `gaps`:
  - `Run.elapsed` is the end (or now) minus the start minus `paused_for`.
  - A pause adds its length to `paused_for` when it ends (`_unpause`). A stopped run that is resumed adds the time since it stopped (`_skip_stopped_time`).
  - Each of these records a `[from, to]` pair in `Run.gaps` (at most `MAX_GAPS`, 50), saved with the run. The live `Tally` ignores events while a run is not running, so skipping the same spans in `rescan` keeps a rescan equal to the live count.
  - A run saved before `gaps` existed has none, so a rescan still counts its earlier pauses. The first version saved the field as `stopped_gaps`; `run_from_raw` still reads that name.
- A rescan runs on a worker thread and only reads files; the log is changed on the main thread.

**Exobiology cards** (`exobiology_overlay.py`, `exo_radar.py`)

- They read `organic_scan_panel.overlay_view()`, which builds an `organic_scan.BodyView` from the controller's per-body state without widgets.
- The view holds:
  - each genus (`GenusView`) with its predicted candidates, the confirmed species and color variant (`ScanOrganic` `Variant_Localised`), its stage, the (latitude, longitude) of each Log or Sample taken (from `Status.json` at the time, persisted in `organic_scan_state.py`) and the commander's distance from the last one
  - the body's first-footfall flag (`Scan` `WasFootfalled`) and the biological signal count
  - the commander's position and heading
  - the ship (`Touchdown`, `Liftoff`) and SRV (`LaunchSRV`, `Disembark`, `DockSRV`, `Embark`) positions
- Four `_Display` objects (status, list, radar, popup) each have a `LiveCard`, a placement slot and a settings switch. `Status.json` changes and the relevant journal events refresh them.
- The Bio status card is one wide strip (`STATUS_CHARS`, 108 characters, `WideCardLayout`) that folds the distance line into the headline row when it fits.
- The radar (`exo_radar.build_plan`) converts the positions to pixels with a flat-earth offset rotated to the heading, and chooses the scale so every circle fits (the overlay cannot clip).
- `RadarLayout` draws the radar with circle shapes (`OverlayClient.send_circle`).

**System targets and Body info cards** (`targets_overlay.py`, `body_info_overlay.py`)

- They read one shared model of the current system, `system_survey.py`, which `load.journal_entry` feeds first (it precedes both cards in `_FEATURES`).
- A new survey starts on `FSDJump`, `CarrierJump` or a `Location` in a different system, and is hidden on `StartJump` (hyperspace).
- Events taken:
  - `FSSDiscoveryScan`, `FSSAllBodiesFound`
  - `Scan` (bodies with a `PlanetClass` or `StarType`; belt clusters and events from another system are skipped)
  - `FSSBodySignals` and `SAASignalsFound` (biological and geological counts, and the genera)
  - `SAAScanComplete` (mapped)
  - `ScanOrganic` (an `Analyse` marks a genus done; a body's life is done when its analyzed genera reach its biological signal count, which equals the number of genera in the real journals checked)
- On `StartUp` or the restore event the survey is rebuilt from the newest journal, from the last arrival.
- The value is `scan_value.py`'s estimate (the pure formula behind the Exploration Value readout).
- Body info picks the body from `Status.json`: `Destination.Body` (when `Destination.System` is this system), else `BodyName`.

*Saving surveys between sessions* (`system_survey_store.py`)

- Each commander's surveys are saved in `system_surveys.json` (one payload per commander through `commander_data.py`; the 60 most recently visited systems are kept).
- After a change to the survey it is written after a short delay. On arrival in a system, or on restore, the saved data is merged back (`SurveyStore.merge_into`): bodies the live survey lacks are added, and for bodies it has, the saved copy supplies what the live one does not know, with the live data winning.
- When a system has no saved bodies (`_has_saved_bodies`: a record holding only the honk counts as none) and the commander's journal history shows a visit or a scan there, `rebuild_system` replays every visit to it from their journals.
  - The history test is `needs_backfill`: two visits or more, or `Visit.scanned`. EDMC starting in the system forces it.
  - It reads only the commander's own journals (each journal begins with their `LoadGame`; at most 80 files) in a background thread, and `SurveyStore.absorb` adds the result to the saved record.
  - The merge into the live survey is applied on the main thread (`apply_pending`, from the journal and Status.json hooks), so the survey is never changed from two threads.
  - The rule examines `scanned` because a system scanned while EDMC was closed has one visit (a relog into it is not another), so the visit count alone would classify it as new and the journals would not be read.

*When the cards may show*

- The survey also carries `playing`, `docked` and `cmdr`.
- `Shutdown`, a new journal (`Fileheader` part 1) and `Music` `MainMenu` stop it.
- `LoadGame` or an arrival starts it, and a `LoadGame` for a different commander clears it.
- `Docked` and `Undocked` (or `Docked` on a `Location` or `CarrierJump`) hide it while docked.

*Card drawing*

- Both cards draw through `overlay_card.CardLayout`: a plain dark panel with no outline and no edge bar, the same layout as the Route card (a fixed top and width, every line at the left padding).
- `CardLayout` builds a plan of every shape and text from the `Card` (title, badge, progress bar, header lines wrapped to the card width, rows with a muted tab column and right-aligned or column values, footer) before sending anything, so the height derives from the content.
- They redraw through `LiveCard` when the card changes or every 3 seconds.
- They share no state with each other except the survey.

**Expedition survey tracking**

- `ExpeditionBook.on_survey` receives these from `expedition_panel.handle_event`: `FSSDiscoveryScan` (`BodyCount`), `FSSAllBodiesFound` (`Count`), `Scan` (`BodyName`, `WasDiscovered`) and `SAAScanComplete` (`BodyName`).
- It counts them against the most recently reached stop whose system matches the event's `StarSystem` or `SystemName` (or the system the commander is in, for events that carry none).
- Body names are stored per stop (`scanned`, `mapped`, `firsts`, at most `MAX_SURVEY_NAMES` each) so a repeat scan counts once. Belt clusters are skipped.
- The Route overlay card shows the route only; an expedition's stops are not drawn on it.

**Link between an expedition and its Expedition Log run** (`expedition_link.py`)

- `Expedition.log_run_id` (written only when set) names the run, and `ExpeditionBook.set_log_run` sets it.
- One controller applies Start, Pause, Resume and Stop to both, in either direction (a Log Stop stops the linked expedition, a Log Resume of a stopped run reopens it).
- A linked expedition shows the run's elapsed time, which excludes paused time.
- An unlinked one (the setting `wfmt_expedition_start_log` off, or no Log commander) keeps wall-clock time, and its Pause only changes status.
- The link is built in `expedition_panel` and takes the two books and the "start a run" function as arguments, so the module imports neither panel.

**Route overlay** (`route_overlay.py`, over the pure `route_plan.py`)

- It draws one overlay card (`navigation_card`): three header lines (`You are navigating to:`, the destination, the jump count), a rule, the names of the systems still to jump to (the next `rows` of them), a rule and the light years left.
- `status_lines` (fuel, range, jumps left, next supercharge) is kept for the Exploration Dashboard and is not on the card.
- The Route Planner's route, when it has a jump left, is used in place of the game's.
- The route is `NavRoute.json` in the journal folder. It is read when a `NavRoute` event arrives and on `LoadGame`, `StartUp` and the restore event; `NavRouteClear` empties it.
  - The journal can announce a route before the game rewrites the file, or while the file is partly written. `sync_file` (called from the one-second tick) therefore reads it again when its `(modified time, size)` stamp (`route_file_stamp`) differs from the last good read. It does nothing until the first journal event (`_live`, so a leftover file is not shown) or while the overlay is off. A stamp that could not be read is not tried again until it changes (`_failed_stamp`).
  - With the diagnostic log on, each read (`NavRoute.json read` with the count, first and last system, the ship's system and whether it is on the route, or `could not be read`) and each card drawn or cleared is logged under `route`.
- Progress is the system the ship is in (`FSDJump`, `Location`, `CarrierJump`, or EDMC's current system). A route is shown only while the ship is in one of its systems (or its position is not yet known), so a diversion or a stale file shows nothing.
- Star kinds come from `StarClass` (`N` neutron, `D*` white dwarf, the rest by `fuel_alerts.is_scoopable`).
- Fuel comes from `fuel_alerts.FuelWatcher`, the range from `Loadout.MaxJumpRange`, and the last jump's fuel from `FSDJump.FuelUsed`.
- The card has a fixed top and width, grows downward, and is redrawn when it changes or every 3 seconds, with a one-second tick while a route applies.
- Its group is `wfmt_route`.

**Flight Alerts** (`flight_alerts.py`, over the pure `carrier_jump_timer.py`, `fuel_alerts.py` and `mining_alerts.py`) draws one overlay card.

- Mining alerts come from `ProspectedAsteroid`'s `MotherlodeMaterial`, the `Cargo` and `Loadout` events and EDMC's cargo by name (`state["Cargo"]["drones"]`); they are described in docs/MINING_TECH_SPEC.md.
  - A core asteroid, or a rock rich in the target commodity, alerts for 30 seconds.
  - Low limpets and a nearly full hold alert while a mining event is under 30 minutes old.
- The carrier countdown comes from `CarrierJumpRequest` (`SystemName`, `Body`, `DepartureTime`, parsed as UTC), and is cleared by `CarrierJumpCancelled` or `CarrierJump`.
  - A request whose departure is already more than 90 s past is ignored (an old journal line).
  - One alert is given as the time left falls to 600, 300, 60 and 0 s (only the nearest when several are crossed at once).
  - On `LoadGame`, `StartUp` or WFMT's restore event, the journals modified in the last 3 hours are read once for a request still in the future.
- Fuel comes from `Status.json` (`Fuel.FuelMain`, via EDMC's `dashboard_entry`), the tank size from `Loadout.FuelCapacity.Main`, and the plotted star from `FSDTarget.StarClass`.
  - Scoopable means exactly one of O, B, A, F, G, K, M. `MS`, `AeBe` and the white-dwarf `D*` classes are not scoopable.
  - The flags `InMainShip` (1<<24), `Docked`, `Landed` and `ScoopingFuel` decide when a warning applies.
  - The journal gives no per-jump fuel cost, so the warnings are percentage thresholds.
- A one-second ticker thread runs only while a jump is planned.
- Each draw lasts 4 s on the overlay, so a stalled WFMT cannot leave the card displayed. An unchanged card is redrawn every 3 s.
- The card has one fixed width (30 characters at 1.6 times the overlay font estimate; 1.3 cut text off), wraps every message to it (at sentence ends, then spaces, at most 10 card lines) and grows downward. Its top and right edge, which Overlay Placement anchors, therefore do not move with the message.

## 10. The overlay

Overlay features (every card and alert) draw over the game window through one of two overlays, selected by `wfmt_overlay_backend` (`overlay_native.py`, Settings > Overlays > Overlay Connection):

- **EDMCModernOverlay** (default; Windows and Linux): a separate helper application that listens on a local TCP port. WFMT is a client.
- **WFMT's built-in overlay** (Windows only, opt-in): a transparent window that WFMT draws itself (see "The built-in overlay").

Every feature draws through `overlay.OverlayClient` (`send_message`, `send_shape`, `send_circle`, `send_vector`) regardless of the selected overlay. `OverlayClient._send_raw` passes the payload to the built-in overlay's scene when it is selected and to the socket otherwise.

**Overlay switches default to off.**

- A one-time reset, `load._reset_overlays_once`, sets every switch in `_OVERLAY_ENABLE_KEYS` to off before any feature reads its settings. It is recorded by the `wfmt_overlay_reset_v2` config key.
  - It runs after `overlay_profile.profiles.configure` and clears the switches in every commander's saved choices (`OverlayProfiles.switch_off`) as well as in the config.
  - Changing the marker's suffix forces the reset again.
- A new overlay switch must be added to `_OVERLAY_ENABLE_KEYS` and default to off.

**Protocol**

- The client connects and sends one JSON object plus a newline per graphic, for example `{"id": "x", "text": "hi", "color": "red", "x": 200, "y": 100, "ttl": 4}`.
- Nothing is read back; sends are fire-and-forget.
- The protocol description is based on observed behavior of EDMCModernOverlay.
- The default port is 5010 (`overlay.DEFAULT_PORT`).

### One shared, persistent connection

`overlay.OverlayClient` holds one connection open for the plugin's lifetime and reconnects lazily if it drops.

- The overlay server tags every graphic with the ID of the connection that sent it and removes all of a connection's graphics when it disconnects, regardless of each graphic's `ttl`. A connect-send-close pattern would make every graphic disappear immediately, so the connection stays open as long as its graphics should be visible.
- One connection serves all features; a connection per mode would duplicate the work and the reconnect logic.
- The connect timeout is 1 second (`CONNECT_TIMEOUT_S`). The connection is loopback to an application that is either running or not, and a long timeout would stall journal processing.

**When no overlay is running**

- After a failed connection, the client fails new sends immediately for 30 seconds (`COOLOFF_S`) instead of retrying. With no overlay program present, no thread waits on a connection per pickup, screenshot or Mining update.
- The failure is logged once at INFO. A changed host or port is applied immediately.
- The Settings test buttons build their own client and always attempt a connection.
- The Overlay Connection tab (Settings > Overlays) has a **Check connection** button.

### Placement (`overlay_layout.py`, `overlay_placement.py`, `overlay_grid.py`)

EDMCModernOverlay maps a fixed 1280 x 960 canvas onto the game window. Measurements (3840 x 2160 at 125% display scaling, fill mode, using probe shapes photographed on screen) show that positions and sizes are treated differently:

- A **position** is a fraction of the screen: x / 1280 across, y / 960 down. In fill mode the canvas is stretched over the whole window (non-uniformly when the window is not 4:3), so none of it is cut off. In fit mode it keeps its shape with bars.
- A **size** (a shape's w and h, and the offsets between the pieces of a registered display) is in logical screen pixels, that is, device pixels divided by the operating system's display scaling. A 360-wide card is 360 / 3072 = 12% of the width, which is 150 canvas units.
- On the axis the overlay does not stretch (across, on a wide screen; both axes in fit mode), it clamps a shape's x + w to 1280, mixing a canvas position with a pixel width, and squashes whatever passes it. A display must therefore start at or before `1280 - its pixel width` there (`Screen.clamped`).
- A **group offset** (`offsetX` of an overlay group) is added after that clamp, in canvas units. It is the overlay's own mechanism for moving a group (the Overlay Controller edits it). A plugin can set it through `overlay_plugin.overlay_api.define_plugin_group(plugin_group_offset_x=...)`, which merges per field into the overlay's groupings file. The anchor does not help on the clamped axis (the overlay pivots on cached bounds there).

Placement is therefore relative to the screen and aware of display size.

**Model** (`overlay_layout.py`, pure)

- `Screen` (window size, mode, display scaling), `units_per_px`, `block_units`.
- `Placement` (a horizontal anchor, a vertical anchor and offsets in screen pixels, or an exact canvas x/y).
- `block_origin` (where a display of a given pixel size goes; kept on the canvas and before the overlay's clamp).
- `plan_origin` (the same, for a display whose group can be offset: where to draw it, which is as far right as the clamp allows for its largest size, and the group offset that carries it the rest of the way).
- `ShiftedClient`.

**Application**

- Features keep their own layout. Each draws at its fixed origin and reports the rectangle it occupies (`block_rect()`: left and top on the canvas, width and height in pixels).
- `overlay_placement.client_for(slot, client, block)` returns the client wrapped so that every `send_message`, `send_shape` and `send_vector` is moved by the same canvas offset, which moves the whole display as a unit.
- A feature that positions itself from an origin (Inventory) uses `origin_for(slot, size)`.
- A slot with an overlay `group` (all but the two Mining slots, which share a group) also gets a group offset.
  - `overlay_placement.apply_group_offsets()` computes the offsets for every slot from the slot's largest size, so an offset is one fixed number regardless of the display's content width.
  - `overlay.set_group_offsets` sends the changed offsets through the overlay's API at start-up, when Settings is saved, when the screen is re-detected or changes, and around the preview (typed values, then the saved ones again).
  - Clearing is by id, so a clear needs no matching shift.
- `ShiftedClient` and `HiddenClient` move or clear circles (`send_circle`) as well as text, rectangles and vectors.
- A card that grows is placed from the size it is drawn at. `overlay_placement.client_for_measured(slot, client, block, look)` takes the card's actual block (so a bottom or middle anchor sits on the actual edge), records its size for the group offset, and re-applies the offsets when it changes.
- Placement is applied at the call sites, never inside a `render()`, so render functions stay pure and testable.
- A saved exact position that would leave the display off the canvas is ignored. The test is `overlay_layout.on_canvas`: at least 40 x 20 canvas units must lie on the canvas, so a leftover `x = 1280` fails. `placement_for` returns the slot's default and logs a warning once per slot; the saved text is not changed.

**Layout editor** (`overlay_grid.py`, on the Placement tab)

- It is a to-scale canvas of the screen in logical pixels with a grid and a draggable box per slot (sized by `slot_size`).
- The pure conversions are `placement_from_rect` and `rect_from_placement`. In `placement_from_rect`, the spot (`_spot`) is the edge a box is within `EDGE_SNAP` pixels of, otherwise the third of the screen containing the box's center. The offset is inward from that edge or from the center line, snapping to 0 within `EDGE_SNAP` pixels and otherwise to the grid.
- It reads and writes the same row variables as the table.
- The picture size is saved immediately under `wfmt_overlay_editor_size`.

**The screen** (`overlay_placement.py`), determined in this order:

1. The overlay's own log (`parse_scaling_line`): the newest "Overlay scaling updated" line gives the window, mode and display scaling (scale_x / base_scale). It is ignored if the game's `DisplaySettings.xml` is newer.
2. `DisplaySettings.xml` (`platform_support.elite_graphics_dir`, which also finds it inside a Proton prefix), with Windows' scale factor (`shcore.GetScaleFactorForDevice`) and the mode from `EDMCModernOverlay/overlay_settings.json`.
3. If that file cannot be read (for example, a Flatpak EDMC without the Graphics folder permission), the window size comes from the overlay log's `(size=WxHpx scale_x=...)` line (`parse_window_size`, `read_overlay_window_size`), which the overlay writes at normal log level. That line has no display scaling, so the scaling is the chosen one, else Windows', else 100%.
4. With neither source, the primary monitor's size is read from the operating system (`platform_support.primary_display_size`).
   - Windows: `GetDeviceCaps` with `DESKTOPHORZRES` and `DESKTOPVERTRES`, which returns the hardware resolution even for a process that is not DPI aware (`GetSystemMetrics` would return a scaled size, 3072 x 1728 on a 3840 x 2160 screen at 125%).
   - Linux: the primary output of `xrandr --current` (`parse_xrandr`), through `flatpak-spawn --host` from a Flatpak.
   - A multi-monitor desktop is not summed; only the primary output counts.
5. If that also fails, the screen is assumed to be 1920 x 1080.

The result is cached for 30 seconds. The mode and the scaling can be overridden. Without EDMCModernOverlay installed, sizes are assumed to be canvas units (`pixel_sizes = False`) and nothing is rescaled.

**Settings**

- `wfmt_overlay_place_<slot>` holds `h,v,dx,dy` or `custom,x,y`.
- `wfmt_overlay_display_scaling` and `wfmt_overlay_scale_mode` hold the overrides.
- A slot with no saved value reads its `legacy_x` and `legacy_y` settings, if it has any, and keeps a hand-set position as an exact one (`layout.migrated_placement`).

**Adding an overlay**

1. Add a `Slot` to `SLOTS` (key, label, default spot, pixel size, legacy keys).
2. Wrap its client with `client_for`.
3. Give its settings a tab in the Overlays group in `ui.py`.
4. Register its ids as an EDMCModernOverlay Plugin Group so its pieces scale together.

### Appearance (`overlay_style.py`, `overlay_appearance.py`)

Every overlay draws with one `Look` (`overlay_appearance.current_look()`, read from `wfmt_overlay_scheme` and `wfmt_overlay_text_size`; padding and line spacing are fixed). A `Look` holds:

- A `Palette` of color roles (border, fill, title, header, text, muted, ok, warn, info, danger, three accents, four chart series).
- A text level (0 or 1 as offered, Default or Larger, which steps each display's text token along small / normal / large / huge and stops at the ends).
- Extra padding and line height.

**Sizing cards from estimates**

- The overlay cannot measure text for a plugin, so the look carries estimates: `CHAR_PX` (character width per size) and `LINE_PX` (line height per size).
- Each display builds its card from them (`look.text_width`, `pad_x`, `pad_y`, `line_px`), so text at any size sits inside its border.
- `LEGACY` is the fixed geometry and colors used as the default argument of every pure layout function, so those functions can be tested without a look.
- Each display exposes `block_rect(..., look)` so placement uses the size the card actually has. `Placement` and `slot_size` scale a slot's nominal size by the look.
- `tests/overlay_look_smoke.py` draws every display at 144 looks (scheme x text size x padding x spacing) and checks that every text lies inside its card and that `block_rect` equals what was drawn.

**Widths**

- `text_width` pads every estimate by `WIDTH_PAD` (1.10, that is 10%), because the overlay's font sizing differs between screens, and a box slightly too wide is acceptable where text past its edge is not.
- `measured_width` is the stricter measure for the Discovery and Notable Bodies cards, whose text is capitals and catalog names. It counts capitals, digits and wide letters (M, W) as wider and spaces and narrow marks as narrower, and is never less than `text_width`.
- The Notable Bodies text limits (60, 56 and 70 characters) guard against a runaway value; the card widens to fit.

**Text size and padding**

- The text size is a setting (`wfmt_overlay_text_size`: Default or Larger; the starting value is Larger).
- No larger step exists, because text runs past its box at that size.
- Interdiction keeps fixed red alert colors.
- `Look.size` never returns less than `MIN_SIZE` ("normal"), so the overlay's "small" is not used (a saved -1 clamps to Default).
- Every card pads its text by the same `CARD_PAD_X` and `CARD_PAD_Y` (plus the fixed extra), with no per-card minimum width.
- Every display draws its text left-justified at its card's padding (Discovery and Notable Bodies included).

### The built-in overlay (`overlay_native.py`, `overlay_scene.py`, `overlay_raster.py`, `overlay_window.py`)

Design and status: [NATIVE_OVERLAY_SPEC.md](NATIVE_OVERLAY_SPEC.md).

- **Scene** (`overlay_scene.py`, pure): the payloads the features send, kept by id with the time each expires (`ttl`).
  - A resend replaces the item.
  - A payload that draws nothing removes the id: empty text, a zero-size rectangle, a circle with no color, an empty vector, or an id with a ttl of 0 (what clearing a line or circle sends).
  - Items are returned in drawing order: rectangles, then circles and lines, then text, each in the order its id first appeared. Text is therefore always above a panel regardless of send order.
- **Picture** (`overlay_raster.py`, Pillow, which EDMC ships): draws the scene on a transparent image the size of the game window. It follows EDMCModernOverlay's conventions, which the features were written for:
  - A group (the ids sharing a registered prefix, `overlay_native.set_groups`) is placed at the canvas position of its top left item (a 1280 x 960 canvas stretched over the window).
  - Distances inside the group are logical pixels times the display scaling.
  - A size (width, height, radius, font) is in logical pixels.
  - An item in no group is placed in canvas units.
- **Window** (`overlay_window.py`, ctypes and Win32): a thread inside EDMC owns a layered, topmost, click-through, no-activate window.
  - Every 50 ms it finds Elite's window (class `FrontierDevelopmentsAppWinClass`) and takes its client area and display scaling (`GetDpiForWindow`; the thread is per-monitor DPI aware).
  - It redraws when the scene or the geometry changed, and pushes the bitmap with `UpdateLayeredWindow` (per-pixel alpha).
  - It shows only while Elite is the foreground window, or Windows' own capture tool is (`CAPTURE_TOOLS`, by the program's file name), or *Keep showing* (`wfmt_overlay_keep_showing`) is ticked.
  - While shown, it re-asserts `HWND_TOPMOST` every half second (Elite, when brought back, takes its place above other topmost windows).
  - A frame that fails is logged and skipped.
  - It is a thread of EDMC and ends with EDMC.
- **Rounded corners:** when the built-in overlay is selected, `OverlayClient.send_shape` adds a `radius` (logical pixels) to a rectangle at least 24 px wide and tall.
  - The value comes from `overlay_native.panel_radius`, setting `wfmt_overlay_corners`: square 0, slight 6, rounded 10, very 16.
  - Thinner rectangles are dividers and bars and stay square.
  - The scene keeps the radius on the item and the raster draws a rounded rectangle, with the radius held to half the panel.
  - EDMCModernOverlay receives no extra key.
- **Placement** reads the window's actual size and scaling (`overlay_native.screen()`, `Screen.native`: no right-hand clamp, no group offsets).
- **Fonts:** the font file is `overlay_native._font_path()`.
  - It is `wfmt_overlay_builtin_font` in WFMT's own `fonts` folder (`overlay_fonts.own_dir`; the bundled Source Sans 3 and any font the player adds, which an update does not remove), else the bundled font, else a system font.
  - The window re-reads it every two seconds, so a change applies without a restart.
  - A text measurer (`overlay_style.set_text_measurer`, `overlay_native.measure`, Pillow's `getlength` at eight times the size) replaces the character-width estimates, so cards are sized from the actual text (`Look.text_width`, `measured_width`, and `Look.extent` for right-aligned text).
- **Screenshots:** `overlay_native.snapshot(width, height)` draws the current scene at a screenshot's size. `screenshot_convert.convert_to_png` places it over the converted copy when `wfmt_screenshot_include_overlay` is on.

**EDMCModernOverlay's font** is separate. `overlay_fonts.py` edits `overlay_client/fonts/preferred_fonts.txt` in its folder (the first entry that loads is used; the default is `Eurocaps.ttf`, capitals only) and keeps a `.bak` once.

**Hiding every overlay** (`overlay.set_all_hidden`, `overlay_visibility.py`)

- `_send` records the last payload per id (`_last`, with the time) and sends nothing while hidden.
- Hiding sends a clear for every id drawn so far. Showing resends what had not expired, with its remaining ttl.
- The keyboard shortcut and the `!wf overlays` chat command are in `shortcuts.py`. The panel line and the Settings button work on every platform.

**Duplicate EDMCModernOverlay windows** (`overlay_processes.py`): it counts `overlay_client` processes (psutil, `/proc`, or PowerShell), treating a launcher and its child as one window, so that Check connection and Copy diagnostics can warn.

### Plugin Groups (EDMCModernOverlay)

EDMCModernOverlay groups a feature's shapes and text so they scale and anchor as one unit.

- `overlay.register_modern_overlay_groups` takes `(group_name, id_prefix)` pairs, so each feature supplies its own and `overlay.py` names no feature.
- Registration is best-effort: it does nothing if ModernOverlay is not installed and swallows errors, so that a cosmetic step cannot break startup.
- Every card-style overlay registers a group, because without a group a card's background rectangle can render invisibly under ModernOverlay.
- When overlay rendering appears wrong, ModernOverlay's own payload and debug log are checked before a rule is changed.
- Overlay message IDs use `wfmt_<feature>_*`, so a group's prefix matches exactly its own shapes.

**Clearing a line or a circle**

- A single drawn item is removed by a payload consisting of its id and `ttl: 0` (`overlay.removal_payload`). EDMCModernOverlay reads that as `legacy_clear` and drops the item, and the built-in scene drops the id.
- Other forms fail against the installed overlay's normalizer (`normalise_legacy_payload`):
  - A `vect` with no points, or one point and no marker or text, is discarded ("insufficient points": it needs two points, or one with a marker or text), and a warning is logged each time, so the clear never takes effect.
  - A circle sent with no color is given the color white, so a clear would draw a dot where the circle was.
- Callers write `send_vector(id, [], ...)` and `send_circle(id, "", "", ...)` to clear. `OverlayClient` converts these into the removal and sends it only when the item is on the screen (`_last` records what was drawn and not yet expired). A card may therefore clear every slot it is not using on each draw at no cost.
- Text and rectangles are cleared with the same removal, not with empty text or a zero-size rectangle with a `ttl` of 1. EDMCModernOverlay accepts those forms but keeps the replaced panel for a few seconds, so turning overlays off would remove the text first and the empty panel a few seconds later.
  - `OverlayClient._send` converts those forms (`overlay.is_clear_form`) into the removal and sends it only for something on the screen.
  - Hiding (everything, or a group) sends the removal for what is on the screen.
- `tests/test_overlay_clear.py` and `tests/test_overlay_hide.py` hold the rules.

**Showing again**

- Switching overlays back on restores what was on the screen when they were switched off, and anything drawn since, each with its full `ttl` (`overlay._restore_payload`). Items that had already expired before the switch stay gone.
- Restoring only the items that still had time left would leave a card missing until its feature next drew it, because a card's `ttl` is a few seconds.
- Features keep drawing into the remembered set while hidden, so what is restored is current.

**Retrying a draw (Landing)**

- `LandingController._render_overlay_async` keeps only the newest request, and one worker thread sends it, so an event and the heartbeat cannot interleave sends.
- If a draw fails with `OSError` (the overlay can take a minute or more to start on Linux), the worker calls `OverlayClient.retry_now()` and retries every 5 s for up to 180 s (`_RENDER_RETRY_EVERY_S`, `_RENDER_RETRY_FOR_S`), unless a newer request replaces it.
- A failed clear is not retried.

## 11. External services

These services supply community and Frontier-side data that supplements the journal. They do not override the journal, and none is required for the journal-driven core of a mode.

| Service | Used for | Trigger |
|---|---|---|
| EDSM | Nearby systems, "does EDSM know this system", bodies, ring reserves | Buttons; some opt-in automatic checks |
| Spansh | Mining price finder and Market research, hotspot and boxel lookups, expedition planners (Road to Riches, Exomastery), ELW rarity, rare-goods origin Power, nearest neutron star and white dwarf (the Neutron Star and White Dwarf buttons), Trade routes and best-price searches, Colonization's Where to Buy, the material trader finder, the Carrier Route and Route Planner plotters, the Powerplay overlay's look-ahead | Buttons; opt-in; the Rares window looks up on open |
| edastro.com (GEC) | Nearest exploration POI: the whole list (`/gec/json/all`) is downloaded and the nearest is computed locally | Button only; kept in memory for 6 hours |
| Canonn sheets | Thargoid and Guardian site lists | Button; downloaded once per session |
| tick.infomancer.uk | BGS tick time | 60-second poll; can be turned off |
| Raven Colonial | Planned Builds, My Projects, and (with the commander's own key) creating, updating and completing projects | Buttons; writes only after a press, with `wfmt_rcc_enabled` on and a saved key |
| Discord | Post to Discord (a webhook the commander sets up) | A button press for every post |
| GitHub Releases | Update check | Opt-in, once per EDMC run |

Rules that apply to all services:

- **API endpoints only.** Every call goes to an API or a published data file; no HTML pages are scraped.
- **Failure returns no result.** `edsm_client.py` states in its docstring that any failure (offline, service down, unexpected shape) returns an empty result, so a failing network feature does not break journal handling. The BGS tick client is the exception: it raises, and the caller decides, because a guessed or stale tick would corrupt the tally. It never returns a guessed value.
- **Every request identifies WFMT.** Each call sends a User-Agent naming WFMT, its version and the project's address (`http_identity.py`, for example `WFMT/1.5.3 (rare-goods; +https://github.com/...)`). EDSM returns HTTP 403 to the default `python-requests` agent, so its client sends EDMC's `config.user_agent` followed by WFMT's.
- **Documented limits are respected.** EDSM's `cube-systems` caps edge length at 200 ly; WFMT uses 100 ly.
- **Opt-in by default.** A lookup that runs without a button press is off until enabled, except the three listed under Background activity below. The user guide lists which features make network calls.
- **No service data is bundled.** Live queries are used, so nothing in the release goes stale and no service's content is redistributed. The exceptions are static game facts (section 12).
- **The tick API uses plain HTTP.** That is the only address the service offers. It carries a public timestamp.

### Keeping API traffic low

The measures below are implemented in the code.

**Shared courtesy layer for Spansh** (`spansh_courtesy.py`). Requests to Spansh pass through one function that applies the same limits to every caller:

- At most 2 requests in flight (a semaphore).
- At least 0.25 s (`MIN_GAP_S`) between the starts of two requests (a shared gate that sleeps outside its lock).
- Retries on 429, 502, 503 and 504: 3 retries, with waits of 2, 6 and 15 s plus up to 25% jitter, or the `Retry-After` header, capped at 60 s.
- A timeout is retried for a GET only. A POST that timed out may have been accepted, and repeating it could start a second job, so a POST is retried only on an explicit busy answer.
- After 5 failed requests in a row (`BREAKER_FAILURES`, each already retried), a breaker refuses further requests for 300 s with `SpanshBusy`, whose message the callers show. Any answer, including a 400, 404 or 422, counts as Spansh being up and resets the count.
- `cancel` (a `threading.Event`) ends a wait before a retry.
- The clock, sleep, jitter and opener are injectable (`tests/test_spansh_courtesy.py`).
- The counters (`requests`, `retries`, `refused`) are included in **Copy diagnostics**.
- Every Spansh request uses the layer. `tests/test_spansh_through_courtesy.py` fails if a module names a Spansh API address and does not.
- `retries=0` skips the retry waits for a caller answering a keystroke (the system-name suggestions); the breaker and the spacing still apply.
- `stream_to_file` applies the same gate, concurrency cap, breaker and GET retry rules to a download too large to hold in memory. It writes to a file and resumes a dropped stream with a Range request (restarting from the start if the server ignores Range). It returns "not modified" on a 304, refuses past a byte cap, and does not count a local disk error against Spansh.
- `docs/SPANSH_USAGE.md` records every Spansh endpoint WFMT calls and must be updated whenever a request is added, removed or changed.

**Optional local neutron-star index** (`star_index*.py`)

*Download and file format*

- The user starts a download of Spansh's `systems_neutron.json.gz` (one gzip of one JSON array, one system per line, about 173 MiB). The file also lists some black holes and B/O stars, which the builder drops by keeping only `mainStar == "Neutron Star"`.
- The index is built into `star_index/neutron.wfsi` in the plugin folder, and the dump is then deleted.
- The file contains:
  - a header of 2,064 bytes (`HEADER_BYTES`): 12 bytes of header, then a JSON block with the counts, section offsets, source URL, ETag, Last-Modified and build date, padded with spaces
  - 13-byte records (`RECORD_BYTES`) sorted by 256 ly grid cell and then by id64: the id64 (8 bytes) and the position inside the cell as three 13-bit numbers (5 bytes, in 1/32 ly from the cell's corner)
  - a cell table
  - a sparse name index (every 64th name, `NAME_BLOCK`)
  - compactly coded names

*Querying and building*

- A query keeps no file open. It reads the cell table once, caches it, and seeks only to the cells near the position, doubling the search from 256 ly out to 5,000 ly.
- The build is two-pass and streaming (32 temporary bucket files), written to a temporary name and renamed, with progress and cancel.

*Location and use*

- The folder is global rather than per commander (it holds facts about stars). It is protected from the updater (`update._OWN_DIRS`) and left out of Back up my data (`data_backup.LEFT_OUT_DIRS`).
- Neutron Star uses the index when it is installed and enabled. It falls back to the Spansh search when the index is missing, damaged, of another format version, or has no entry within 5,000 ly. White Dwarf always asks Spansh.

*Update* is a top-up when possible (`star_index_download.choose_update`, `star_index_job._topup`, `star_index_build.build(topup_from=...)`):

- Spansh's `systems_1day.json.gz` and `systems_1week.json.gz` list every system changed since midnight (UTC) 1 or 7 days before the file was made, in the dump's layout.
- The smaller file whose start is at or before the index's date is fetched with `If-Modified-Since`. The index's date is the Last-Modified of what it is current to, kept in the header with the original dump's, a count of top-ups and the file's ETag.
- `StarIndex.records()` streams the old records through the same bucket pass as a full build, dropping each system the file mentions and adding the file's neutron stars. A system whose main star is no longer a neutron star leaves the index.
- The builder checks the file's oldest `updateTime` against the index's date (`TopupGap`). The job then downloads the full dump instead, as it does when the index is more than a week behind, after `MAX_TOPUPS` (20) top-ups, or after `MAX_LINEAGE_DAYS` (60) days.

**Background activity.** Every lookup is started by a button or is opt-in (off until enabled in Settings). This covers the Mining lookups, the Exploration Value extras (Spansh and EDSM), the Boxel Survey skip checks and alias confirmation, Region Sweep's auto-discover, and the update check. Three exceptions run without a button press:

- The BGS tick poll: one small request a minute to the tick service while BGS is on (it can be switched off).
- The Codex Completionist catalog, downloaded when its details window is opened and the saved copy is missing or older than 14 days.
- The Rare Goods window, which looks up each origin system the first time it is opened.

**Caching of answers**

- Rare Goods: a system's controlling Power is cached for the EDMC session, and failed lookups are cached as well, so a dead network is not contacted on every redraw. At most 5 lookups run at a time.
- Canonn site lists are downloaded once per session. The Codex catalog is saved on disk (`codex_catalog.json`) and reused for 14 days.
- The automatic ring-reserve check (opt-in) is remembered per ring for the session and is never run while the journal is being replayed at start-up.
- Source picks (`source_picks.find`, used by Trade's Best picks button and by the Missions Source commodities window) run one Spansh station search per pick.
  - The picks are cheapest, local, closest, then the 10% band sorted by distance, with a carrier search fifth.
  - They run one after another with a 0.4 s pause, each asking for 25 stations of market data at most 7 days old.
  - The search asks Spansh for a minimum supply (or demand) and, for the band, a `buy_price` or `sell_price` range (`mining_spansh_client.search_best_price_stations(min_quantity=, price_range=)`).
  - The band is the cheapest price up to 110% of it (selling: 90% of the highest price up to it).
  - `mission_sources.lookup` runs it for each commodity in turn on a worker thread.
  - Nothing is cached or stored.
- The Where to Buy window (`colonization_buy_window.py`, opened by the Sites window's **Where to Buy** button) holds the search. It knows the Sites window only through a `Host` of four callbacks (the picked commodity, the rows still to buy, the selected site's system and the commander's system). The Sites window notifies it when the pick or the site changes (`set_wanted`, `follow_site`). The search choices keep their old settings key, and the window has its own geometry key.
- The Colonization window's Where to buy search remembers an identical search (same system, commodity, radius, pad size, carriers, sort, current system, exclusions and tons wanted) for 2 minutes. It runs only when Find nearest or Find all is pressed, asking for at most 25 stations and 10 carriers per commodity.
  - Find all (`colonization_sources.find_whole_list`) is the same search once per outstanding commodity, in order, on one worker thread.
    - It pauses 0.4 s before each request that is actually sent (answers from memory cost no pause; the cache key is shared with Find nearest).
    - It records a failed commodity and continues, and checks for a Stop between commodities.
  - With two or more commodities and no failure, one more request asks for the 5 nearest stations that have every one in stock.
    - It is `mining_spansh_client.search_stations_selling_all`, which sends several `market` filters.
    - Each station is added to every commodity's sources unless already listed, with that commodity's price and supply from the market Spansh returns.
    - A failure of that request is ignored.
  - When the window passes `needs` (tons still to get), that request goes first.
    - A commodity that one returned station can supply in full is skipped (no per-commodity search).
    - After the searches, if `plan_route` still leaves two or more commodities uncovered, one more request (`also=` the other listed commodities) asks for stations selling all the uncovered ones, and their whole markets are merged the same way.
  - The window keeps the closest 5 stations and 2 carriers of each.
  - `plan_route` builds a shopping route from the full answers.
    - It is greedy by tons a station can supply of what is still outstanding (a station selling several commodities counts for each), with ties going to the nearer and then the cheaper, and at most 6 stops.
    - `_fly_order` orders the chosen stops as a trip: every permutation is tried (at most 6! = 720) and the shortest wins. The first leg is the stop's own `distance_ly` from the search system; later legs are the straight-line distance between systems.
    - Positions are Spansh's `system_x/y/z` on each station result (`StationPrice.position`, `Source.position`, `Stop.position`); no extra request is made. If any stop has no position, the legs are `None` and the order falls back to nearest first.
    - The Where to Buy window keeps `_trip_seen` (every stop the plan has had since the last Find all or filter change) and `_skipped`. A seen stop that is no longer in the plan is drawn as done. The next-stop card re-reads the current system every 3 s.
    - It reports what no returned station can supply and does not extrapolate beyond the stations searched.
- The Colonization window's search choices (preset, radius, pad, carriers, sort and the exclusions) are one JSON string in EDMC's config (`wfmt_colonization_search_prefs`, `colonization_sources.SearchPrefs`), written when a search starts and when the window closes. They are window preferences like its geometry and are shared by every commander; no play data is in them.
- "Only what [station] sells": on a `Market` event the Colonization controller reads `Market.json` (checked against the event's `MarketID`, and read again for up to 0.4 s if the game wrote it late) and keeps the commodities with stock and a buy price (`trade_market.sold_keys`).
  - It forgets them on `Undocked`, `FSDJump`, `SupercruiseEntry` and a `Location` without a station, because the file remains on disk after the commander leaves.
  - It is not saved; only the market opened this session is known.
- Earth-like-world rarity is remembered per system for the session, and EDSM upload status per system for 10 minutes, so re-selecting the same target costs no extra calls.
- Boxel Survey keeps a local log of visited systems, so the Random button does not spend an EDSM call on a system the log already contains. Region Sweep's "require a full FSS scan" uses the journal's `FSSAllBodiesFound` and makes no call.

**Hard limits on one action**

- A skip-check run (Sequence mode, or Region Sweep with *Skip systems already visited by anyone (EDSM)* on) makes at most 20 EDSM lookups.
- Random makes one Spansh search (kept in memory for 10 minutes and 5 ly, so repeat clicks make none) and at most 6 EDSM bodies lookups per click.
- Sequence's automatic "nearest real system" suggestion happens only in response to the user's own clicks, at most once per 3 **Next** clicks in a row with no jump.
- EDSM nearby-system queries use a 100 ly cube.
- Reordering a Waypoint Route uses one bulk coordinate request for the whole list.

**One request at a time, no retry loops**

- Each lookup carries a generation number, so a newer request supersedes an older one and a stale result is dropped. Region Sweep's auto-discover fires only when the queue is nearly empty, and only one lookup is in flight (so at most one per jump).
- A failed request returns "no result" and is not retried by the feature. Spansh calls receive only the courtesy layer's bounded retries of a busy answer. The only repeat is the BGS tick's next scheduled poll, a minute later.
- Every request has a timeout (8 to 60 seconds).
- Trade's route search is the one lookup that polls: Spansh queues a job and WFMT requests the result every 5 seconds (`POLL_INTERVAL_S`) for at most 4 minutes (`MAX_WAIT_S`, 240 s; about 48 requests), then gives up. **Cancel** stops it immediately.
- A Near me or Galaxy price search is two requests per press (stations, then fleet carriers; one if carriers are hidden), because carriers are priced so differently that in one list they could fill the page.

**Bundled data in place of calls**

- The Rare Goods list is bundled, with EDSM coordinates and Inara and Spansh ids resolved in advance, so they are not requested at runtime. The exobiology and region tables are bundled for the same reason.

**Adding a network call:** it must be opt-in or user-triggered, cache what it can, cap what one action can do, set a timeout, and identify WFMT with `http_identity.user_agent()`.

The services are funded by their authors and supporters; `docs/ATTRIBUTIONS.md` has links.

## 12. Feature notes

Design notes for each feature area. File names are in `plugin/`.

### Powerplay (`powerplay.py`, `session.py`, `store.py`, `formulas.py`, `powerplay_ledger.py`, `powerplay_state.py`, `powerplay_backfill.py`, `powerplay_systems_tab.py`, `powerplay_overlay.py`, `powerplay_system_lookup.py`)

The journal's `PowerplayMerits` event reports the merits earned after every game multiplier.

- It does not report the resulting Control Points; that depends on the activity and is not documented by Frontier.
- The merit-per-CP ratios are therefore user-editable settings and not constants.
- Sessions are tied to the journal file, so a logout to the menu and back, or an EDMC restart mid-game, continues the same session.
- A "last merit timestamp" high-water mark lets a journal rescan distinguish an already-counted gain from one missed during an EDMC restart.

**Rare Goods Finder** (`rare_goods.py`, `rare_goods_window.py`, `powerplay_control_lookup.py`, `rare_goods.json`)

- Rare-good origins do not move, so the dataset (142 entries, with coordinates, Inara id and Spansh id64) ships as a static file.
- "Nearest" is the plain 3D distance from the latest `StarPos` the Powerplay controller saw.
- Only the origin system's controlling Power changes, so only that is fetched live, from Spansh's `system/<id64>` endpoint on a small thread pool.
- Results are cached per process, including failures, so a redraw or a dead network does not re-request.
- The window marshals results back onto the Tk thread and drops any that belong to a superseded refresh.

The window's filters apply before the number shown:

- **Large pads only** keeps `pad == "L"` (`rare_goods.candidates`).
- **Only my Power** walks the candidates nearest first. It asks Spansh about `POWER_BATCH` (10) uncached origin systems at a time and re-evaluates from the cache after each batch. It stops when `limit` systems are controlled by the commander's pledged Power (`PowerplayTracker.my_power`, compared by `rare_goods.same_power`) or none are left.
- Both choices are remembered (`wfmt_rares_large_only`, `wfmt_rares_my_power`). The second is unavailable until a Power is known.

**The overlay card** (`powerplay_overlay.py`; spec section 12 in [POWERPLAY_TECH_SPEC.md](POWERPLAY_TECH_SPEC.md))

- `PowerplayController.overlay_info()` builds an `Info` from the tracker, the session and the cycle ledger. `powerplay_overlay.build_card` converts it to a `Card` (pure), and a `LiveCard` redraws it on every event and once a second.
- `PowerplayTracker.system_activity` and the module function `activity_for` give the Acquisition / Reinforcement / Undermining estimate without the side effects of `classify_current_activity`, so a display can call them at any rate.
- The card is drawn by `StackedLayout` (new ids when its geometry changes, so the panel stays under the heading text) through `LatestOnly` and a render lock, so redraws do not overlap.
- The controller records a `StartJump` to a hyperspace destination. Only with the `wfmt_powerplay_overlay_lookahead` tick on, the destination is looked up through `powerplay_system_lookup.py` (Spansh by system id, via `spansh_courtesy`).

### Boxel Survey (`boxel*.py`, `region_sweep_*.py`, `waypoint_route*.py`, `edsm_client.py`)

- Procedural system names have a fixed shape: sector words, a cube id, a mass letter and a sequence number.
- WFMT parses that string to step forward and back and to build the next candidate name; the galaxy map confirms whether the system exists.
- Names are not decoded into coordinates, which would require Frontier's id64 arithmetic. An "increment the cube number" shortcut was built and reverted because it produced candidates far from the player.

Spatial adjacency comes from external sources:

- EDSM's `cube-systems` query, centered on the journal's `StarPos`, supplies nearby real systems.
- Region Sweep's *Skip systems already visited by anyone (EDSM)* uses `region_sweep_edsm_skip.skip_known_candidates` on a worker thread. The panel polls a result queue, and a newer jump or **Next** press makes an older check stale through a generation number. It steps past candidates that `edsm_client.system_known` reports as known to EDSM, up to 20 per advance, keeps the candidate when a lookup fails, and caches answers (`KnownSystemCache`) for the session.
- Region Sweep does not generate a "next cube"; it tracks completion for cubes it was given by a typed seed, EDSM or Spansh.
- **Random** asks Spansh for the real systems nearest to the commander, keeps those with no scan data, and confirms one with EDSM. It first checks a local per-commander visited-systems log, because a visit without a scan leaves no trace in either service, so a visited system could otherwise be returned as new.

Details are in the [Boxel Survey spec](BOXEL_SURVEY_TECH_SPEC.md).

### Exploration Value (`exploration_value.py`, `elw_rarity_spansh.py`)

The scan payout is estimated by a formula in the pure module `scan_value.py`:

- Base value: k + k x 0.56591828 x mass^0.2 (`Q`), at least 500, with k from the planet class (plus the terraforming bonus; an Earth-like world always counts as terraformable).
- First-discovery multiplier: 2.6.
- For a mapped planet, the mapping multipliers: 3.699622554 for a first discovery and first map, 8.0956 for a first map of an already discovered body, 3.3333333 for an already mapped body.
- The Odyssey bonus (30% of the mapping part) and the efficiency bonus (1.25).

Readouts:

- The readout shows the scan value. The mapped value is on the Body info card and in the Expedition Log.
- System age needs no formula: a star's `Scan` event carries `Age_MY`.
- The region readout is a local lookup on `StarPos` against a coordinate grid, with no network call.

### Discovery Alerts (`discovery.py`)

- On arrival the game auto-scans the star (`ScanType: "AutoScan"`). Its `WasDiscovered` is `False` if nobody has scanned it.
- Any `Scan` has its own `WasDiscovered`.
- `SAAScanComplete` has no such flag, so whether the commander is first to map is taken from the previous `Scan` event's `WasMapped` for the same body. It is cached per body and cleared on system change.
- The feature produces no alert in the already-discovered case.

### Notable Bodies (`notable_rules.py`, `notable.py`)

**Rules** (`notable_rules.py`)

- The module is pure (no EDMC or Tk imports): a table of `Rule`s, each a function of one `Scan` event plus the other scans already seen in the system (`bodies`, by `BodyID`), returning a one-line detail or `None`.
- `evaluate()` runs the enabled rules and never raises on a malformed event.
- Units are the journal's own: meters, seconds, m/s^2.
- The rules and limits are fixed defaults (see `THIRD-PARTY-NOTICES.md`):
  - landable above 29.4 m/s^2 (about 3 g)
  - landable radius above 18,000 km
  - rotation or orbit under 8 h
  - eccentricity above 0.9
  - 5 of 6 premium FSD materials on a landable
  - ring wider than 5x the body's radius
  - orbit under 3x the parent's radius
  - a shepherd moon is one orbiting inside the outermost ring's outer edge
  - a close or colliding binary is a pair sharing a barycenter whose radius / semi-major-axis ratio is above 0.4 for both (colliding when their periapsis distances are less than their radii)
- A high-value body is any terraformable body or any Earth-like, water or ammonia world, landable or not. Its detail says "undiscovered" or "unmapped" from `WasDiscovered` and `WasMapped`.
- Fast rotation and fast orbit apply to planets only (a neutron star spins in milliseconds), and fast rotation skips tidally locked bodies.
- Green gas giants are matched on planet class plus a table of confirmed surface temperatures (+/-0.001 K), from community research credited in THIRD-PARTY-NOTICES.md.

**Tracker** (`notable.py`, follows `discovery.py`)

- `NotableTracker` keeps the current system's scans keyed by `BodyID` (reset on a new `SystemAddress`).
- When a body arrives, it also re-evaluates the already-scanned bodies that orbit it, because a moon is often scanned before its parent.
- `(BodyID, rule)` pairs alert once.
- One card is shown per body, with the first rule's label as the title and `+N` for more. A body matching several rules gets one card.
- A card shows for 6 s (`CARD_SHOW_S`). Three cards can wait (`MAX_QUEUED`); the rest are counted ("(N more)").
- Title and name are capped (60 and 56 characters, 70 for a name with the "(N more)" count), so a runaway value cannot make the card very wide. The card widens to fit what is shown.
- Rule choices are saved as a JSON dict in `wfmt_notable_rules`. A rule missing from it uses its default, so a later release can add rules without a migration.
- There are 15 rules; 7 are on by default.
- The feature has no panel widget, only a Settings page (Overlays > Notable Bodies).

### Nearest neutron star / white dwarf (`neutron_finder.py`, buttons in `discovery.py`)

The **Neutron Star** and **White Dwarf** buttons query Spansh's `bodies/search` for the nearest system whose primary star is a neutron star or a white dwarf.

- The filters are `subtype` (`Neutron Star`, or the 14 `White Dwarf (xx) Star` classes, which Spansh lists separately) and `is_main_star: true`, sorted by distance.
- The origin is given as `reference_coords` from the journal `StarPos`, so it works from a system Spansh has not seen.
- The request shape was derived from live calls (Spansh does not document it). `neutron_finder.py` is the single place to change if it changes.
- It requests two results so it can skip the commander's own system.
- The lookup runs on a worker thread with a result queue polled via `after()` (as in the GEC panel) and is manual only.
- It copies the full system name to the clipboard and truncates the displayed name (`MAX_NAME_CHARS`, 40) so a long name cannot widen the window.
- `tests/test_neutron_finder.py` covers the result picking against canned responses.

### Organic Scanning (`organic_scan*.py`, `organic_*_data.py`)

- It predicts species per body from atmosphere, gravity, temperature, pressure, region and other rules, and tracks the Log, Sample and Analyze progression and the distance required between samples.
- It shows estimated credits (a flat per-species value; there is no first-discovery bonus for exobiology).
- It is local and read-only and submits nothing.
- The two `*_data.py` files are generated and marked "do not hand-edit". A new species requires regeneration.
- Region lookup holds the game's 42 region boundaries as a coordinate grid indexed from an origin offset.
- See the [Organic Scanning spec](ORGANIC_SCANNING_TECH_SPEC.md).

### Mining (`mining_*.py`)

- **Runs** are bounded by `Undocked` and `Docked` (space) and `LaunchSRV` and `DockSRV` (surface). The alternative, from first prospector to next jump, splits one stop at a ring into several runs whenever the player supercruise-hops.
- **Deposit estimate** (`mining_deposit.py`) converts the Rigs count plus the HUD's Amount and Density readings into a range of tons.
  - The bands come from measured depletion traces and not from a documented formula (125-175 t per rig position x a Density factor of High 1, Medium 2, Low 3).
  - Density readings are entered by the user. Unknown values widen the range.
  - Rigs is capped at 7 in the hotspot dialog.
  - While the Rhino is out, each `MiningRefined` ton is credited to the nearest positioned hotspot within 200 m (`Hotspot.mined_tons`, written on a 5 s throttle and on shutdown), so a Depleted deposit reads "depleted (612 t)".
  - Saving a hotspot from the panel within 100 m of an existing one on the same body updates it instead of adding a second.
- **Panel and windows.** The Mine panel shows a few lines for the ring run and the Rhino (`mining_render.py`), with **Space Mining** and **Surface Mining** buttons that open the Live windows (`mining_live_window.py`).
  - Those windows carry **Book** and **Dashboard** in their header and a Settings card from `mining_window_settings.py`. The panel has no Book, Dashboard or Live buttons; the Live shortcut opens the windows with them.
  - `mining_pages.py` keeps the two page names as identifiers only.
- **Windows** (`plugin/uikit/`, `mining_ledger.py`) use WFMT's own navy look; see "External windows" in section 5.
  - The Surface Mining Book (`mining_ledger.py`, data in `mining_ledger_data.py`) is the browser for scanned bodies and saved hotspots.
  - Beyond the list and map, it holds the following, each documented in `MINING_TECH_SPEC.md` section 6:
    - dated Depleted marks with an optional assumed refill time (`mining_depletion.py`; the default is unknown and a mark remains)
    - Rhino stops (`mining_stops.py`; the map draws `MapCircle` rings)
    - the deposit within 175 m of the Rhino, selectable as "you are here"
    - Market research (`mining_market_research.py`, `mining_market_research_dialog.py`; one Spansh station search per system, behind the price finder's switch)
    - one-line sharing of a deposit (`mining_share.py`)
- **Own rates** (`mining_ground.py`): no third-party dataset is bundled or downloaded.
  - The journal does not report what a surface deposit holds, so `OwnRates` tallies the commander's saved hotspots per kind of ground: of the deposits recorded on this kind of body, the share that were a given material, with the sample size shown.
  - `classify(PlanetClass, Volcanism)` maps a scanned body to a ground key (rocky bodies are split on volcanism, tested before anything else; "silicate magma" before "silicate").
  - A hotspot saved from the panel is stamped with `Hotspot.ground` when its body is in the current system's survey. Older or imported hotspots count via the survey while their body is scanned and are skipped otherwise.
  - Only recorded deposits count; the figures describe what the commander has recorded, not what a body holds.
  - The Surface Mining Book hides the section until something is recorded.
- **Minimap markers** are color-blind-safe: pale filled dot = live hotspot, hollow gray ring = depleted, blue outlined dot = the commander. In the ship (no Rhino out), the map shows only under 2 km altitude, from Status.json's `Altitude`.
- **Coverage** (`mining_coverage.py`) paints a fixed-radius disc at each recorded point. It records where the Rhino has driven and not what has been scanned, because neither the journal nor Status.json reports a scan. The module states this, and the UI must not claim otherwise.
- **Bearing** (`mining_bearing.py`) computes the relative bearing to a saved hotspot from the live Status.json position and draws an overlay arrow.

### Trade (`trade_*.py`)

Full detail: [Trade spec](TRADE_TECH_SPEC.md). Design points:

- **Profit uses the game's number.** `MarketSell` carries `AvgPricePaid` (what the sold tons cost), so profit is `TotalSale - AvgPricePaid x Count` with no stock-lot bookkeeping. Stolen cargo has `AvgPricePaid` 0. Running costs (fuel, repairs, rearm, limpets) are summed from the journal's cost events and subtracted to give a net figure. Insurance rebuys and fines are not included.
- **Names pass through one resolver.** Spansh's market search is case-sensitive and exact, and the journal's plural ("Void Opals") finds nothing where the list's "Void Opal" works. `trade_commodities.resolve` maps typed text, journal names and internal symbols to Spansh's exact name from a generated table. Mining's price finder uses it as well.
- **Offers are ranked for the load**, not by price per ton: `price x min(tons, demand)`. A station paying more per ton but wanting 40 t is worth less to a 200 t hold.
- **Pad filtering is client-side.** Stations the ship cannot dock at are dropped after the search, so a filtered search asks for 40 stations instead of 20 (`_SELL_FETCH_PAD_FILTERED`). Unknown ship or missing pad data means no filtering. Carriers always fit and are listed apart because they can move.
- **History is saved on request, from a richer ledger.**
  - The live ledger keeps a bounded log of every trade and cost with its station, plus jumps and the starting balance.
  - **Save session** snapshots it (and the stock, hold and carrier) into `trade_history.json`. Re-saving the same session (however many logins it spans) updates the same record.
  - `trade_stats.py` computes every figure and table row, so the Trade History window (`trade_history_window.py`) only lays them out.
  - Totals are exact; the log can be shorter on a very long session.
- **Unsold stock is one book and an estimate** (kept for Trade History, not shown on the Session page).
  - `trade_stock.py` tracks cargo bought and not yet sold per commander across logins, with average cost.
  - A carrier-loading run and a station-to-station run are handled identically (buys add, sells remove, carrier transfers change nothing).
  - It applies each event once using the last-event time plus fingerprints of same-second events, and catches up at start by replaying recent journals synchronously before any live event.
- **A transfer goes to the carrier the commander is docked at.** `CargoTransfer` does not name a carrier. `Docked` and `Location` carry the station's `MarketID`, which equals the carrier's `CarrierID`. Docked at another player's carrier, nothing is counted. With two carriers and no dock information, the transfer is skipped.
- **Pages are blocks.** Each page is a list of typed blocks (`trade_blocks.py`) drawn by `BlockView` (`trade_view.py`), so headings, label/value rows and number columns are laid out and not padded with spaces. The builders are pure and testable, and an unchanged page is not redrawn. See the Trade spec for the sizing rules.
- **No page arrows.** Trade's pages are windows (`trade_windows.py`) opened from the **Session**, **Routes**, **Market** and **History** buttons (one row) under the panel's short summary. Mining's pages are its Live windows, and Missions' category pages are the Mission types window. The page-arrow helper (`panelkit.nav_arrow`) and the settings that remembered a page were removed. `trade_pages.py` keeps the page names as identifiers only.
  - The windows hold no trading state. A window asks `TradePanelController.page_content(page)` for the blocks and header buttons and is redrawn whenever the controller refreshes. Each page has its own saved geometry (`wfmt_trade_window_geometry_<page>`).
  - The Routes window holds the route requirements (hops, arrival distance, jump range, price age, the permit, carrier, ground and large-pad ticks, the Round trip settings), Market holds the Near me radius and ship size, and Session holds the count-fines switch, all on the keys they always used. The Hops button cycles 2 to 10 (`_HOP_CHOICES`); the Settings range is 1 to 10.
  - Routes lists every hop with its profit, the running total and the distance, then a Whole route row and a bold average-per-leg line (the average times the legs is the estimated total earnings). A Round trip pair ends with a both-legs total and the same kind of average.
  - Trade History shows the newest 200 trades (`PAGE_SIZE`), and a **Show older trades** button adds 200 more. There is no Earlier / Later paging.
  - `BlockView` can take the window theme's colors. The windows use a text hierarchy (large headings, muted labels, bright values, green gains, red losses, amber warnings).
- **A scrapped fleet carrier is forgotten.** A decommissioned carrier writes no last event, so `trade_carrier_ops.py` reads `CarrierDecommission` (its `ScrapTime`) and `CarrierCancelDecommission`. `is_scrapped` and the prune in `trade_carrier.py` drop the record once the carrier is scrapped. A Carrier Management report with `PendingDecommission` and no date counts `DECOMMISSION_DAYS` (7) from that report. `tests/test_trade_carrier_scrapped.py` covers it.
- **Round trip can carry one commodity.** The setting limits both legs to it (matched ignoring case; blank means any), a pair counts only when it pays both ways, and the result names the commodity (`tests/test_trade_roundtrip.py`).

### Missions (`missions*.py`, `mission_*.py`, `active_missions.py`, `kill_missions.py`, `all_missions.py`, `kill_tracker.py`)

Data-layer modules keep per-commander state and announce changes through `Notifier` objects (`notifier.py`). Derived views and the UI subscribe to them, so the data layer imports no UI code.

- The panel lists each mission type that holds something, with its count. The pages are a window: the **Mission types** button opens `missions_types_window.py` (the types on the left, the chosen page on the right, drawn by `missions_ui`). Its Display card (`missions_display_settings.py`) holds the six display switches on the keys they always used. The page arrows and the settings that remembered a page were removed.
- A bounded lookback journal scan (`journal_scan.py`, two weeks) restores missions on startup. The window covers any mission still active, and is short because missions expire.
- The scan also derives which missions the journals leave active, so a restart mid-game does not wait for the next login (see "Catching up on state EDMC missed").
- `mission_cargo.py` keeps the newest `CargoDepot` progress per mission.
- `FactionKillBond` kills count like bounties.

### BGS (`bgs_*.py`)

- `bgs_tracker.py` (pure) parses journal fields.
- `bgs_ledger.py` (`TickLedger`) holds one tick period's per-faction snapshots (pre-tick `before` and latest `now`) and activity. It runs identically on live events and on a replay of journal files (`bgs_journal.py`).
- Trade and exploration credit are attributed to the station's faction, which spans two events (`Docked`, then the market event), so the ledger carries that context.
- `bgs_format.py` holds the shared wording.
- The tick client polls every 60 seconds.
  - A new tick archives the closed period (kept for the "archive days" setting) and starts a new one.
  - The current period is rebuilt from the journals once per session.
  - The period that just closed is also rebuilt from the journals (`bgs_ledger.repair_record`, up to 14 days back) and filed over the live record, because play with EDMC closed is not in it.
- See the [BGS spec](BGS_TECH_SPEC.md).

### Operations (`screenshots*.py`, `screenshot_*.py`, `inventory*.py`, `ship_builds*.py`, `combat_*.py`) and Colonization (`colonization*.py`)

- Screenshots convert the game's raw file into a renamed PNG on the `Screenshot` event, with a crop chosen by which HUD panel had focus.
- Inventory determines the current vehicle (ship, on foot or SRV) from `Embark`, `Disembark`, `LaunchSRV` and `DockSRV`, because EDMC tracks only on-foot versus not. Micro-resource names resolve through a bundled table, then names learned from the journal, then a title-cased fallback.
- Ship Builds is a per-commander list of URLs to builds designed elsewhere. WFMT does not design loadouts.
- The Materials book keeps `session` (the journal file's name and `collected`, pieces by material) beside the counts, per commander. `MaterialCollected` adds to it; a different `monitor.logfile` name (checked on the first event, `LoadGame` and `StartUp`) starts a new tally, filled from that file's `MaterialCollected` events older than the event being handled, for this commander only.
- The Combat Record counts `Bounty` and `FactionKillBond` as kills, `PVPKill` as PvP kills and `Died` as deaths, and credits each to the vessel the commander was in.
  - `combat_record.Craft` follows the vessel from `LoadGame`, `Loadout`, `ShipyardSwap`, `SetUserShipName`, `Embark`, `Disembark`, `LaunchSRV`, `DockSRV` and `Resurrect`. A ship is keyed by its type and `ShipID` (`type#id`), so a rename does not split a row; the SRV and on foot are rows of their own. A `Bounty` on an on-foot target is always on foot. When no event has named the ship (EDMC started mid-session), the ship comes from EDMC's `state`.
  - A session is one journal file (the file's name; live, `monitor.logfile`), so a live session and the same session read back from the journal are one record. Totals are kept apart from the sessions, which are limited to 300 per commander (`MAX_SESSIONS`).
  - `combat_record.json` is per commander (`commander_data.py`). `through` is the timestamp of the newest event counted and `seen` the fingerprints of the events at that second, so an event read from the journal and received live is counted once, while two different events of one second are both counted.
  - At start-up (and when the commander changes) a worker thread reads the commander's journals: all of them the first time, afterwards the files changed since `scan`. Events that arrive meanwhile wait in order and are applied afterwards. The vessel at the end of the journal being written carries into live counting.
  - `combat_window.py` polls the record's `revision`, since the worker also changes the record.
- The Ranks section turns the journal's rank numbers into the game's names (`ranks.py`; no Tk). `Rank` gives each ladder's rank from 0, `Progress` the percent toward the next, and `Promotion` a new rank (which starts at 0%).
  - The Pilots Federation ladders have nine names (the last is `Elite`) and the prestige tiers `Elite I` to `Elite V` at 9 to 13 (a real journal holds a Trade rank of 13); the Federation and Empire navies have 15 names. The journal calls Exploration `Explore` and Mercenary `Soldier`. A number past a ladder's end reads `Rank <number>`.
  - The names come from community references and were checked against real journals. Where they differ the game's wording is used: the journal reference calls the fifth Exploration rank `Explorer`, the wiki, TrueAchievements and GamePur say `Trailblazer`.
  - `RankBook` holds one commander's ranks and a different commander starts empty. When EDMC started after the login, EDMC's own `state["Rank"]` fills the table: once, on a commander's first event and before that event is applied, and never after a switch from another commander, whose state may still be in it. Nothing is saved: the game sends `Rank` and `Progress` at every login. `engineer_requirements.py` reads its names from the same table.
  - The table takes the panel's full width (the body and the table are `sticky="ew"`, and the label column takes the spare room), so a long rank name such as `Lieutenant Commander` stays on one line.

**Build costs**

- `build_costs.py` reads the bundled `colonization_costs.json` once (55 entries, a copy of a community-compiled table; notice in THIRD-PARTY-NOTICES.md).
- A site's `buildType` is a layout name. An entry's own type takes precedence over another entry that lists it as a layout (`tellus`).
- A missing or damaged file gives an empty table, so a cost is not shown.
- The Planned Builds window shows the full cost for planned and building sites, totals the planned ones in its subtitle, and lists the five biggest commodities on a click.

**Planned builds (Raven Colonial)**

- `rcc_client.fetch_system` performs one `GET /api/v2/system/<name>` (public, no key; the answer carries the architect, an `open` flag and the `sites`) per press of the Sites window's Planned Builds button (`colonization_builds_window.py`, on a worker thread with a poll, as in Where to buy).
- The system name is percent-encoded into one path segment.
- The request carries `http_identity.user_agent("rcc-system")` and a 15 s timeout (`TIMEOUT_S`), and at most 2 MB is read (`MAX_BYTES`).
- Malformed entries are skipped and names are clipped.
- An answer (never a failure) is remembered for 60 s (`CACHE_SECONDS`), and a 404 means no sites.
- Nothing about the commander is sent.
- The planned sites exist only on that service (the journal does not report them). A site with a market id the commander tracks is marked.

**Raven Colonial writes, key check and links**

- Every write (`rcc_client.send_write`, `complete_project`) and the key check carry `rcc-key` plus `rcc-cmdr0` (the commander's name as base64 of its UTF-8 bytes). Raven's web app (read from its published script) sends both on every call to its API, and WFMT does the same.
- `rcc_sync` refuses to look anything up or send without a saved key (`_has_key`), because Raven's OpenAPI description declares no authentication, so which writes work without a key is unknown.
- `check_key` is `GET /api/Cmdr/_` (changes nothing). It runs on a worker thread from the Settings page's **Test key** button against the text in the box.
- A build in progress has a `buildId` but no `marketId` on the plan's sites.
  - `find_build_id` therefore falls back to the station's name (`station_part` strips the game's "Orbital Construction Site: " prefix; a build in progress takes precedence over a finished namesake).
  - `build_id_for` adds a second route when the plan names none: `fetch_project_by_market` performs `GET /api/system/<address>/<market id>` (public, 404 means none). The address is the plan's `id64` or the game state's `SystemAddress`. This finds a standalone project, one named "Primary port", and a station the game has renamed. A failed read raises `RccError`.
- `send_json` is `send_write` returning the parsed answer. Both share `_send_request`: one retry on 429 or 503, with 401 and 403 worded without the key.
- The page links are opened with `webbrowser.open`:
  - `home_page_url`
  - `key_page_url` = `/user`
  - `system_page_url` = `/#sys=<name>`
  - `build_page_url` = `/#build=<id>`
  - Only **Open Selected Build on Raven** first reads the system's plan to find the id.
- The Sites window's header uses `uikit.widgets.MenuButton` (a `FlatButton` that posts a `tk.Menu`; `WindowShell.add_menu`).

**Creating a project (Raven Colonial)**

- `rcc_create.py` (pure) and `colonization_create_dialog.py` (the dialog). The flow is `ColonizationWindow._on_create_rcc` -> `_poll_plan` -> dialog -> `rcc_create.create` on a worker thread.
- The plan is read first (cache cleared). If `build_id_for` finds a project, the run ends ("already has one") and `RccSync.note_created` is informed.
- The dialog collects: plan entry (an unbuilt, unlinked planned site, or none), name, location, building, layout, body, architect, notes, due date, primary port, make primary, attach carrier.
  - The building is chosen in three steps: location (`orbital` or `surface`), building (`BuildChoice`, by tier and name) and layout, the build type Raven knows it by (every key in the bundled table: `build_costs.table()` maps layout to building, and `layouts_of` lists them with the building's own first). The layout is sent as `buildType`.
  - Body choices are `RccSystem.bodies` (`num`, `name`, `subType`; numbers above 999 are belts and rings and are dropped).
  - A construction ship (`is_construction_ship`: either spelling of colonization ship in the raw name) defaults to the name "Primary port" and `isPrimaryPort`, unless the system already has a primary port (`primary_port_note`). Raven's `GET /api/v2/system/<name>` has no primary flag on the system or its sites. `isPrimaryPort` is on each project (`GET /api/project/<build id>`), and `GET /api/system/<address>` lists only the active projects. The dialog therefore infers it: the system's first station is its primary port, so any other site in the plan with a market, a project, or a status of building or complete, or any other non-failed construction site WFMT tracks in the system, means one exists. The tick is then off and disabled with that reason.
- `create`: `PUT /api/project` with the market id, system address and name, star position, name, `buildType`, `commodities` still needed (required minus provided), `maxNeed`, a rebuilt `colonisationConstructionDepot`, and the optional fields only when known. A chosen plan entry is sent as `systemSiteId`; if none is chosen the field is omitted, so the project stands alone and the plan is not edited. The answer's `buildId` is required.
- Then, each reporting its own failure without undoing the project: `PUT /api/project/<id>/link/<cmdr>`, `PUT /api/Cmdr/<cmdr>/primary/<id>`, `PUT /api/project/<id>/fc/<carrier market id>`.
- The system address and position come from the plan (`id64`, `pos`) first, then from EDMC's `monitor.state` when the commander is in that system (`rcc_create.locate`). The carrier id is the commander's own, from `CarrierStats` or `CarrierLocation` (`Feeder.own_market_id`).
- **Mark Plan Entry Demolished** sends `PUT /api/v2/system/<address>/sites` with the entry's fields and status `demolish`. This write has not been observed against the live service (docs/TODO.md).

**My Projects (Raven Colonial)**

- `colonization_projects_window.py` draws. `rcc_projects.py` (pure) builds the rows, progress, totals, trips and shopping text. `rcc_client` has the reads (`fetch_active`, `fetch_hidden`, `fetch_primary`: `GET /api/Cmdr/<cmdr>/active`, `/hiddenIDs`, `/primary`, public) and the writes (`save_hidden`: `POST .../hiddenIDs`; `set_primary`: `PUT .../primary/<id>`).
- The commander's name is lowercased and percent-encoded into the path. At most 200 projects and 1000 hidden ids are kept (`MAX_PROJECTS`, `MAX_HIDDEN`).
- "Counted" is the inverse of Raven's hidden list. Saving replaces the whole list, so the window asks first. An older answer is dropped (`_request_id`).

**Delivery history**

- The delivery history (and the claim / release / beacon counts beside it, `record["claims"]`, each with its own newest-only mark) is rebuilt once per commander from every journal they have.
- A record whose `backfilled` version is lower than the current one is rebuilt once more.
- On first sight, a worker thread runs `colonization_catchup.read_all_events`. A byte search skips the files with no deliveries.
- The Tk thread applies the result with `DeliveryLedger.rebuild`, which:
  - replaces the saved record only if the rebuilt tons and deliveries are at least as large (so deleted journals never shrink it)
  - folds in any live delivery that arrived meanwhile under the newest-only rule
  - marks the record `backfilled`
- **Rescan Journals** (the Sites window's button, `ColonizationWindow._on_rescan`) runs the same rebuild on demand. It also folds the last `colonization_catchup.MAX_DAYS` (30) days of site events through `colonization_catchup.apply_events` and, for a commander with a fleet carrier, rebuilds the carrier tally (`colonization_carrier.scan_journals`, applied with `replace_from_journals`). The files are read on a worker thread and the results are applied on the Tk thread. It needs a commander but not a carrier.

**The Colonization mode**

- `PANEL_PLACEMENT = "colonization"`, the Colony button; the mode key is `colonization`.
- It shows a page built by `colonization_panel.build_panel`: the current project and the commander's history, filled by `_refresh_summary` from the saved sites, the ship's hold and capacity, the carrier record and the delivery ledger.
- Figures and wording are in `colonization_stats.py` (pure; `project_for`, `history_for`, `coverage_text`, `trips_text`, `delivered_text`, `needed_text`, `recent_completed`, `completed_line`).
  - The page has no separate Progress line: Delivered reads `N of M t (P%)`.
  - The rows are in three sections (project, What you have, To finish the build). Each heading is drawn only while one of its rows is (`_PAGE_SECTIONS`, `_show_headings`).
  - Commodities and Trips left are hidden once nothing is left to deliver, and `needed_text` states whether the build is complete or waits for a final dock.
  - With no active site, the page lists `recent_completed` (the last `_RECENT` = 5 finished sites, newest first) in place of the project rows.
  - It branches on whether the commander has a fleet carrier: with no carrier there is no carrier row and one trips figure of whole-ship loads; with a carrier it shows trips to buy and to haul.
  - The Sites window follows the same rule (`_arrange_tiles`, one Trips column).
- `colonization_history.py` is the per-commander delivery ledger (`colonization_history.json`: totals by commodity, site and day, and a `journal_at` watermark so that the start-up catch-up and live events do not count a delivery twice).
  - `apply_events` feeds it from every `ColonisationContribution`, with or without a known site.
- A `Site` also records `first_seen` and `completed_at` for the average build time.
- The progress bar is a fixed-size canvas, so it cannot widen EDMC's main window.

**Colonization journal events**

Colonization (`colonization.py` is pure logic, `colonization_data.py` the repository, `colonization_panel.py` and `colonization_window.py` the UI) is built on two journal events:

- `ColonisationConstructionDepot` is an authoritative snapshot of a depot's `ResourcesRequired`, so it replaces the stored list.
- `ColonisationContribution` carries only the amounts just handed over, so it advances `provided` between snapshots (clamped to `required`).
- Neither event names the station, only a `MarketID`. The name is remembered from the latest `Docked` for that market and fills a blank only.
  - A `Docked` at a site already tracked is the game's own name for that market id, so `apply_dock_name` replaces the stored name (and system) with it, live and in the start-up catch-up. This is how a rename reaches WFMT.
- Names in these events are decorated (`$steel_name;`) while `state["Cargo"]` is plain (`steel`), so both pass through `commodity_key` before comparison.
- The repository saves only when a site changed, because re-docking re-sends an identical snapshot.
- At start-up `colonization_catchup.py` replays the recent journals into the repository (see "Catching up on state EDMC missed").

**The ship's hold**

- The In Cargo figures (Sites window, Colony page and overlay card) read the hold from the game's `Cargo.json` beside the journals (`journal_files.read_cargo_file`), because the journal's `Cargo` event carries only a count and EDMC's cargo state did not follow a purchase in observed cases.
- The file is ignored when it is missing, unreadable, or describes another vessel (the SRV); `state["Cargo"]` is then used.
- After any event that can change the hold (`Cargo`, `MarketBuy`, `MarketSell`, `CargoTransfer`, `CollectCargo`, `EjectCargo`, `MiningRefined`, the limpet events and `Loadout`), the hold is read again 1.5 s later, in case the game had not finished writing the file.

**The Sites window's Acquire column**

- `colonization_view` keeps two figures per commodity: `remaining` (the site's own need, required less delivered) and `to_get` (that less the hold and the carrier, never below zero).
- The window's Acquire column, its category totals and its sort show `to_get`. The buy trips divide `to_get` by the ship's capacity and the haul trips divide `remaining`, so haul trips count everything the site needs.
- The note under the buttons of the Where to Buy window is drawn in the status color while a search runs or a Stop is pending, and in the plain text color otherwise (one method sets every update, `colonization_buy_window.BuyWindow._say`). Find all makes no system check of its own.

**Fleet carrier column**

- `colonization_carrier.py` keeps the window's FC column: tons transferred to the commander's fleet carrier, per commander through `commander_data.py`.
- Whether a commander has a fleet carrier is asked of Trade first (`trade_panel.fleet_carrier`: the Settings choice, else a recorded fleet carrier; `None` means unknown), so the two features agree. It falls back to what this module has seen itself.
- It is fed live and caught up from `CargoTransfer` events in the same way.
- `apply_capi_cargo` takes the CAPI `cargo` list from `capi_fleetcarrier`. The CAPI copy can lag and has been seen unchanged for longer than the throttle, so applying every copy undid transfers made just before it arrived. The copy is applied only when it differs from the tally and neither of these holds:
  - **Recent transfer:** the newest transfer (`journal_at`) is under `CAPI_GRACE` (15 minutes) old.
  - **Repeated copy:** the list equals the one stored as `capi_ignored` (the last copy ignored) and `capi_ignored_at` is under `CAPI_REPEAT_EXPIRY` (1 hour) old. After that the copy is applied.
- An ignored copy is stored in `capi_ignored` with the time in `capi_ignored_at`. An applied copy clears both and sets `from_capi`. `replace_from_journals` (Rescan Journals) clears both.
- Each call logs one INFO line (applied, same, or ignored with the reason), which is used to diagnose a report of a wrong column.

**The diagnostic log** (`diag_log.py`, `uikit/trace.py`)

- Off by default (`wfmt_diag_log_enabled`, Settings > Help; a machine setting, listed as shared in `tests/test_overlay_profile.py`).
- `set_enabled(True)` opens a `RotatingFileHandler` (1 MB, 3 backups) at `<EDMC data>/logs/WFMT/wfmt-diagnostics.log` and attaches it to the plugin logger and to a non-propagating `...diagnostics` logger that `log()` writes through.
- The plugin logger is set to DEBUG while the log is on, so every `logger.debug` appears in the diagnostic file. `_KeepOutOfEdmc` is added to each handler up the logger's parents (EDMC's) and drops the plugin's records below the level EDMC already used, so EDMC's log is unchanged. `set_enabled(False)` removes the handler and the filters and restores the level.
- Lines are `time | LEVEL | thread | area message key=value ...`. A field is clipped to 200 characters and flattened to one line. `issue_report.redact` hides commander names (`note_commander`), the home folder and webhook links.
- Call sites: `route_overlay` (each `NavRoute.json` read, each card drawn or cleared), `load.py` (start, stop, each journal event's name, settings saved, Frontier data), `spansh_courtesy.Courtesy._note` (endpoint, outcome, ms, attempt, bytes), `colonization_buy_window` and `colonization_window` (`diag_log.timed` for searches and the rescan), `ui._on_panel_mode_click`, and, through `uikit.trace.emit`, `FlatButton` presses and `WindowShell` opening and closing (the kit imports nothing from the plugin; `load.py` sets `trace.listener`).
- `log()` does nothing and cannot raise while the log is off or on a failure. `tests/test_diag_log.py` covers it.

**Tooltips on window buttons** (`tests/test_window_button_tips.py`)

- `FlatButton` binds its hover highlight with `add="+"`. A plain `bind` replaces the tooltip's own `<Enter>` and `<Leave>` handlers (`add_tooltip` runs first), which left window tooltips attached and never shown.
- `tests/uikit_tooltip_smoke.py` hovers a button, a menu button, a window action and the footer's A-/A+. `tests/window_fit_check.py` fails any visible `FlatButton` without a tooltip (`add_tooltip` marks its widget `_has_tooltip`).
- `tests/test_window_button_tips.py` reads every plugin source file and fails on a `FlatButton`, `MenuButton`, `add_action` or `add_menu` call without a `tip` keyword, naming the file and line. The wording is `Name - what it does`.

**Overlay choices copied from another commander** (`overlay_profile.py`, `overlay_placement._build_copy_row`)

- `OverlayProfiles.others()` lists the other commanders with filed choices. `request_copy(name)` only records the request.
- `save_current` (run from `prefs_changed`, after the tabs have written their values) applies it: `apply()` the source's filed settings (removing keys the source never set), file them as the active commander's, then call `on_changed` to redraw.
- Applying at save time prevents the open Settings window from writing its stale values over the copy. The tab drops any earlier request when it is built, so a cancelled Settings leaves nothing pending.

**Where to Buy: own system first and presets** (`colonization_sources.py`, `colonization_buy_window.py`; used by Colonization only)

- `find(..., here=, filters=, needed_t=)`: for each pad size to try (`_pad_stages`: Large then Medium for `PAD_LARGE_FIRST`, else only the one chosen), it asks Spansh for the commander's system alone (`_in_system`: `this_system_only`, sorted by distance, then keeps stations whose system is `here`). If one passes `filters` (`LocalFilter`: no surface, arrival, shipyard, enough stock with `needed_t`), that is the answer (`SearchResult.local`). Otherwise it searches around the typed system, ordered by the chosen sort, and only if that finds nothing tries the next pad size (`SearchResult.note` = `MEDIUM_NOTE`, set only on a non-empty result). Large anywhere therefore ranks above Medium at home. The window passes the system from `Host.current_system()`, not the Around box. `filters`, `needed_t` and `here` are in the cache key.
- `find_whole_list(..., here=, filters=)`: the same per commodity (`needed_t` from `needs`). A commodity that a one-stop station in `here` supplies in full and that passes `filters` gets its answer directly from those stations (`_hit_source`, `local=True`) and is not searched. `_merge_hits` and `_check_orbital` skip `local` results. The one-stop requests use a Large pad when the choice is Large then Medium. `filter_found` shares `_wanted` with `LocalFilter` and keeps `local` and `note`.
- `PRESETS` (`Preset`: pad, carriers, surface, arrival, stock, shipyard, optional radius; every preset sorts closest first) with `DEFAULT_PRESET` = `large_then_medium`. `preset_for` names the preset the options match, else `custom`. The window shows it in the Preset list and saves it with `SearchPrefs.preset`. Choices saved before presets existed (no `preset` key) load as the new defaults, keeping only the radius.
- Pad, radius, carrier, sort and preset changes cannot redraw old results, so `_on_search_option_change` shows `Options changed: press Find nearest or Find all to search again.` (`_stale_note`) until the next search. The surface, arrival, stock and shipyard ticks still redraw immediately.

**Where to Buy: tabs, route order and sections** (`colonization_buy_window.py`, `colonization_sources.py`, `uikit/table.py`)

- The window's content is a `Tabs` (`uikit.widgets`): **Suggested route** (index 0, the route block: `_plan_frame` with the next-stop card and `_plan_table`, or `_plan_empty` until a route exists) and **Closest stations** (`_source_table`). `_show_plan(show)` shows or hides the route and selects the tab: a new route selects tab 0 once, and a render with no route (a Find nearest) selects tab 1. `_working` is a large label placed over the tabs' stage by `_set_working` between the start and end of a search (`_poll_search`, `_poll_whole`).
- `plan_route(..., order=)` takes `ROUTE_DEFAULT` (`_fly_order`, the shortest flight), `ROUTE_SMALL_FIRST`, `ROUTE_LARGE_FIRST` (by `Stop.tons`) or `ROUTE_FAR_FIRST` (by `distance_ly`, descending). The last three go through `_ordered`, which measures the legs stop to stop when every position is known and leaves them unset (total None) otherwise. An unknown order falls back to the default. `_on_route_order_change` replans from the kept answer and clears the route table so its sections start afresh. The choice is not saved.
- Sections: `DataTable.group_states()` and `set_all_open(bool)` (`uikit/table.py`) back the **Expand all** and **Minimize all** buttons. A render calls `_remember_open()` first and asks `_opened(table, iid, default)` for each group, so only the first commodity group and the first route stop default to open, and a redraw (sort, filter, purchase) keeps what the commander set. `_forget_open()` runs when a new answer arrives.
- `StationPrice.body_name` and `market_updated` (Spansh's `body_name` and `market_updated_at`) are carried through `Source` and `Stop` (`body_name`, `updated`). `short_body` drops the system's name and `data_age_text` words the age. Both are used by `_stop_notes` and `RoutePlan.lines`.

**Colony page: the body of the highlighted site** (`colonization_panel.py`, `colonization.py`)

- `Site.body_name` is saved with the site (`to_dict` and `from_dict`). The journal does not state which body a site is at, so `_look_up_body` runs once per site and session on a worker thread: it reads Raven Colonial's plan for the site's system through the cached `rcc_client.fetch_system`, matches the site by `market_id`, takes the plan's `body_num` and names it from the plan's bodies. `_poll_bodies` (on the Tk thread, from `_poll_offers`) saves the name, and the page refreshes. A failure is silent and the line is omitted.

**Where to Buy: surface ports and purchases** (`colonization_buy_window.py`, `colonization_sources.py`)

- `SearchPrefs.no_surface` (default false) and `no_carriers` (default true since 1.4.1: carriers are left out unless the commander clears the tick) back the Exclude surface ports and Exclude fleet carriers ticks. The raw Find all answer is kept, and `_found_view` filters it with `without_surface` at draw time, so toggling needs no request. `surface_only_labels` names the commodities (still to get) whose every source with stock is planetary. `plan_route(..., surface_only=)` marks their `Purchase.surface_only`, and `Stop.is_planetary` marks a surface stop.
- `filter_found` applies the display filters (`no_surface`, `max_arrival_ls`, `needs` for enough stock, `shipyard_only`) to the raw Find all answer at draw time and for the route. None changes what is asked of Spansh. `StationPrice.has_shipyard` and `Source.has_shipyard` come from Spansh's `has_shipyard` (absent when there is none).
- `_check_orbital` (end of `find_whole_list`): for each commodity still to get whose every source with stock is planetary, one `find(..., orbital_only=True)` (station types `ORBITAL_TYPES` only) is merged in, because the nearest sellers can all be on planets. Only a commodity still surface-only after that is named.
- `refresh_needs` is called by the Sites window at the end of `_refresh_detail`. It takes the Acquire tons (`to_buy` rows with `to_get` above zero, for the commodities searched) and, when they differ from the last, replans with `plan_route` and redraws quietly (no change to the note). No request is made. A commodity with no tons left is skipped when the groups are drawn.

**Shopping-list overlay card** (`colonization_overlay.py`)

- It draws the optional shopping-list card, laid out as a table (Commodity, Required, Acquire, FC (only with a carrier), Cargo).
- `build_card` (pure) converts the most recently updated active site, the hold, the carrier tons and the ship's `CargoCapacity` into a frozen `Card`.
  - Acquire is what is still to get: required less delivered, less the hold and the carrier (a zero is drawn as 0). `Row.need` keeps the site's own remaining need for the covered / surplus rules and the trips to haul.
  - Rows are alphabetical at a construction site and grouped under the market's categories elsewhere. The footer has tons remaining and trips.
  - `show` (the setting `wfmt_colonization_overlay_show`: `all`, `buy` or `haul`) selects the rows through `colonization_view.shown`. Until it is saved, the older tick box `wfmt_colonization_overlay_hide_covered` (on by default) decides, and on means `buy`. `buy` leaves out the rows the hold plus the carrier cover. `haul` keeps the covered rows the hold does not yet hold in full. The Sites window's Show dropdown uses the same function. The row limit and the `+N more` count apply to the rows left, and the footer still counts every commodity.
- `render` and `clear` send the card through the shared `OverlayClient` (ids `wfmt_colonization_s<line>_<column>`, registered as a Plugin Group in `load.py`).
- Columns are right-aligned from character counts, because the overlay has no text metrics.
- The controller redraws only when the card or position changes or half the 3600 s time to live has passed, sends on a short-lived daemon thread, and clears synchronously in `plugin_stop`.

*When the card is shown.* It is drawn only while `Visibility` allows it, in one of five cases:

1. `Status.json` `GuiFocus` is Station Services (5, from `dashboard_entry`) and the service opened last was the market, or the commander is docked at a carrier and the last service was not `Outfitting` or `Shipyard`.
   - The market is `Market`, or `CarrierStats` or `CargoTransfer`, or `Market.json` being rewritten. The controller compares its modified time on every `Status.json` update and every 500 ms, because the journal's `Market` event can reach EDMC several seconds late (observed under Proton), and counts it only while a station-services screen is open.
   - A carrier is covered separately because the game writes no `Market` event for a carrier's market.
   - `Outfitting`, `Shipyard` and `StoreCargo` mark another service as open. `Docked`, `Undocked`, `LoadGame`, `StartUp` and `Shutdown` reset it, and so does `GuiFocus` leaving 5.
2. The commander is docked at a `FleetCarrier` or `SquadronCarrier` and `GuiFocus` is 1, the right-hand cockpit panel where the cargo transfer to the carrier is done (the game writes no event for opening it, and `CargoTransfer` comes only after a transfer is made).
3. The commander is docked at a construction depot (station type `SpaceConstructionDepot`, `PlanetaryConstructionDepot` or `ColonisationShip`, a "Construction Site" station name, or a `ColonisationConstructionDepot` event) and `GuiFocus` is 0 or 5.
4. The `Music` event's track is `FleetCarrier_Managment` (Carrier Management; both opening and closing are announced).
5. Optionally (`wfmt_colonization_overlay_right_panel`) `GuiFocus` 1 anywhere.

A manual `forced` flag (the **Always show the shopping list** tick in Settings > Overlays > Colonization) overrides all of the above and the enabled setting.

Settings keys: `wfmt_colonization_overlay_enabled` and `wfmt_colonization_overlay_row_limit` (0 shows every row, at most 60). The position is set on Overlay Placement; the older `_x` and `_y` keys are read only as a starting point.

### Report an issue and Copy diagnostics (`issue_report.py`, `ui._create_help_tab`)

Three buttons are on Settings > General > Help (the diagnostic log's controls are on the same page; see "The diagnostic log").

- **Report game data** opens the Game data form (`issue_report.open_feedback`, `build_feedback_url`) with `webbrowser.open`.
  - The address is `.../issues/new?template=game_data.yml&labels=game-data&title=...` with the fields `area`, `subject`, `context` (clipped to 40, 80 and 80 characters) and `environment`. The names must match the `id`s in `.github/ISSUE_TEMPLATE/game_data.yml`.
  - It is general: any part of WFMT passes its own area, subject and view. The Engineers tab's **Report engineer data** button passes `Engineers`, the selected engineer and `Standing in WFMT: ...`. The Help page's button opens it blank. No commander name is included, and it falls back to the template alone past `MAX_URL_LENGTH`.
- **Report an issue** opens `.../issues/new?template=bug_report.yml&labels=bug&title=...&environment=...` with `webbrowser.open`.
  - GitHub prefills an issue-form field from a query parameter named after the field's `id`, so `ENVIRONMENT_FIELD` (`environment`) must match `id: environment` in `.github/ISSUE_TEMPLATE/bug_report.yml` (a test checks it).
  - If the address would exceed `MAX_URL_LENGTH` (2000), it falls back to the template alone.
- The Environment text is `environment_text()`: WFMT version, EDMC version (`config.appversion`, a function in current EDMC and a string in old ones), Python version and `platform_support.describe_system()` (Windows release and build, or Linux `PRETTY_NAME` + `XDG_SESSION_TYPE` + Flatpak flag).
- **Copy diagnostics** puts `environment_text()` and the newest WFMT log lines on the clipboard (`copy_diagnostics`):
  - The log file is the `baseFilename` of the file handler on EDMC's logger (else `<app_dir>/logs/EDMarketConnector-debug.log`). `read_log_tail` reads only the last `LOG_TAIL_BYTES` (400,000 bytes).
  - `wfmt_log_lines` keeps a record when its header line (one starting with a date) contains `.<plugin folder>.`, with its continuation lines, so a traceback stays with its record. The newest `MAX_LOG_LINES` (80) are kept, and `MAX_LOG_CHARS` (12,000) caps the text.
  - `redact` replaces each commander name, case-insensitively and longest first, with `<commander>`, and the home folder (both slash styles) with `~`. The names come from `commander_names()`: `restore.latest_commander()` and `monitor.cmdr`. A commander WFMT cannot identify is not redacted, which is why the guide instructs reviewing the text before posting.
  - The clipboard is written with `clipboard_clear`, `clipboard_append` and `update()` on the Settings frame. On failure the function returns False and the button shows *Could not copy to the clipboard*.

WFMT sends nothing itself: the browser and the user send the report. The feature is listed in [internet-and-privacy.md](guide/internet-and-privacy.md) but opens no connection of its own. The user how-to is [reporting-problems.md](guide/reporting-problems.md).

### Ship engineering planner (`ship_plan.py`, `ship_plan_tab.py`, `journal_blueprints.py`)

A ship loadout in the shape of the journal's `Loadout` event (EDSY and Coriolis export the same shape as SLEF, a list of `{header, data}`) becomes a list of blueprints and crafts for the wishlist.

- `ship_plan.parse` accepts a SLEF list, one SLEF object or a bare `Loadout`.
- `plan_module` takes one module's `Engineering` block (`BlueprintName`, `Level` 1 to 5, `ExperimentalEffect`, `EngineerID`).
- **Module type** comes from the item symbol by prefix (`ship_plan.MODULE_TYPES`; armour is `<ship>_armour_*`), because the same journal blueprint is a different table row per module type (`Weapon_LightWeight` is "Lightweight Mount" on a weapon, `Misc_LightWeight` is "Lightweight" on a utility).
- **Blueprint** comes from `journal_blueprints.BLUEPRINT_NAMES[journal name][module type]`. Grades 1 to `Level` are the table's rows of that type and name.
- **Experimental effect** comes from `SPECIAL_NAMES[journal effect]`, a list of candidate names because the table's spelling differs ("Drag Munition" and "Drag Munition (Seeker only)"). It is the grade 0 row of that module type; one craft.
- **Generated data.** `scripts/gen_journal_blueprints.py` (run by hand; needs the network) joins the public ship-module data's `modifications/blueprints.json` and `specials.json` to the table through the module-data UUID the table records per grade.
  - The table gives every blueprint that shares a name the same UUID regardless of module ("Lightweight", "Reinforced", "Shielded"). The join is therefore limited to the module types of the journal name's family (`FAMILY_TYPES` and `FDNAME_TYPES` in the script), and a link must also agree on the words.
  - What cannot be linked is printed, not guessed.
  - The diff is reviewed before committing. `tests/test_ship_plan.py` checks that every link points at rows the table has.
- **Generator overrides.** The family of a journal blueprint name decides which module types it can link to (`FAMILY_TYPES`), and `FDNAME_TYPES` overrides that for the names a real ship's `Loadout` events showed on other modules than the family implies: `Misc_LightWeight` and `Misc_Shielded` also apply to Life Support and the Refinery, `Sensor_LongRange` and `Sensor_FastScan` to the three scanners. `NAME_ALIASES` joins the one name pair that shares no whole word ("Fast scan" and "Fast Scanner"). A link is only written to a row the table has. The Mk II agile boost engine (`int_mkiiagileboost_engine`) is a Thrusters module: its blueprint IDs are the thruster blueprints'. `plugin/blueprints_edsy.py` (hand-maintained, from EDSY's data) holds the 18 blueprints the table lacked, as rows with materials only, and `EDSY_JOURNAL_NAMES`, which the generator adds to `journal_blueprints.py`. It includes the ordinary Long Range blueprint for the mining laser and the abrasion blaster, the Guardian `GuardianModule_Sturdy` (one grade, for the power plant and distributor, the hull and module reinforcements and the three Guardian weapons) and the new module types Cargo Rack, Module Reinforcement Package, Mining Laser, Abrasion Blaster and the Guardian Gauss cannon, Plasma Charger and Shard Cannon (`ship_plan.MODULE_TYPES`). A grade the source leaves empty is not written as free: the planner reports the blueprint as partly counted. Still not counted: `CargoRack_IncreasedCapacity` (no materials in the source), `Weapon_HighYieldEnzyme` (the flak and flechette launchers have no module type) and Force Impact.
- **Not counted.** No `Engineering` block: left out. `EngineerID` 399999 (Frontier's pre-engineered marker): listed, takes nothing. An item with no module type, a journal blueprint with no entry for that type, a level outside 1 to 5, or fewer grades in the table than the level: listed as not counted or partly counted, with the reason.
- **Current ship.** `ship_current.current_build` reads the last `Loadout` event of the newest of the last three journals that has one, on demand.
  - Nothing is stored. A `Loadout` has no commander name, so the newest file is the session being played.
  - `plan(build, current)` compares only when `Build.ship_id` (the journal's `Ship`, such as `federation_corvette`) matches. Modules are paired by `Slot`.
  - `_already_on` subtracts when the current module has the same journal blueprint, the same module type and is not pre-engineered: `min(current level, target level)` grades are done and a matching `ExperimentalEffect` is done.
  - A module that is fully done gets the status `already done`.
  - `Plan.compared` states what it was compared with, or why not.
- **In storage.** `stored_modules.match_plan(plan.modules, book.modules(cmdr), where)` reports, for each planned module, which stored module would do. It is informational: nothing is subtracted from the plan.
  - Only the stored list counts (`stored_modules.py`); a module fitted to any ship is not in it. A stored module matches on its `Item` (the same module, size and class).
  - `FULL`: it carries the planned journal blueprint (`PlannedModule.journal`) at the planned level or higher. `PARTIAL`: anything else, preferring the same blueprint at a lower level, and including a module swapped out of a ship whose engineering the game did not report.
  - The experimental effect is not compared, because `StoredModules` does not report one.
  - One stored module serves one planned module; full matches are assigned before partial ones. With no snapshot yet (`book.asof` is empty), no match is shown.
- **Rolls.** `Plan.entries(rolls)`: each grade is crafted `rolls` times (1 to 10), an effect once, and the same blueprint on several modules is added together. The `Quality` of the last roll is shown and not used in planning.
- **Wishlist.** `WishBook.add_many` validates every entry first and then applies them with one save and one redraw, or changes nothing and raises `WishError` (no commander, a blueprint not in the table, more than 100 blueprints, more than 99 crafts of one). Input is capped at 2 MB of text and 100 modules. Nothing is fetched from the network, and every table cell is length-capped.

### Odyssey upgrade planner (`odyssey_upgrade_plan.py`, `odyssey_plan_tab.py`)

**Costs and credits**

- The suit and weapon upgrade rows of the blueprint table (type Suit or Weapon, named for the item, engineer Merchant, grades 2 to 5) take their costs from recorded `UpgradeSuit` and `UpgradeWeapon` journal events.
- The events record the `Class` reached, the `Cost` and the `Resources` spent:
  - 1, 2, 4 and 5 for the schematic, the family item and Manufacturing Instructions (or Health Monitor)
  - 2, 5, 9 and 12 for the item's other two materials, for every item and kind seen
- `tests/test_odyssey_upgrade_plan.py` holds the transcribed events and checks the table and the credit formula against them.
- The credits are not in the table. `CREDIT_UNIT` holds the cost of class 2 for the eight items seen, and class n costs `CLASS_FACTOR[n]` times that (1, 3, 6, 10 for classes 2 to 5; confirmed across several items and classes).
  - An unseen item has unknown credits (`None`) and the plan states this.
- To add an item's credits, add its `UpgradeSuit` or `UpgradeWeapon` journal line to `CREDIT_UNIT` (cost divided by the class factor) and to the test.

**Planning**

- `modifications_for` lists a suit's or weapon's grade 0 rows, leaving out the upgrade rows and, for a weapon, the modifications marked for another family.
- `Plan.entries()` is each class step and each modification once, for `WishBook.add_many`.
- `plan(..., fitted=)` counts the fitted modifications against the four slots and does not plan them again.

**Owned gear** (`odyssey_gear.owned_gear`)

- It reads the commander's gear on demand. It goes back through the newest journals of the newest journal's commander (up to 80 files, `MAX_FILES`) until two have `SuitLoadout`, `SwitchSuitLoadout` or `CreateSuitLoadout` events.
- `from_loadouts` keeps the newest sighting of each suit (`SuitID`; `SuitName` ends in `_classN`) and weapon (`SuitModuleID`; `ModuleName`, `Class`, `WeaponMods`), raised by any later `UpgradeSuit` or `UpgradeWeapon`.
- The journal's modification ids map to the planner's names in `SUIT_MODS` and `WEAPON_MODS` (range, headshot damage and hip-fire accuracy are one id for all weapons, spelled with the weapon's family).

### Megaship scans (`megaship_scans.py`, `powerplay_megaships_tab.py`)

The Powerplay activity *Scan datalinks at Megaships* is recorded per cycle in the Powerplay ledger (section 11.2f of the [Powerplay specification](POWERPLAY_TECH_SPEC.md)).

- `MegaShipTracker` follows the journal (jumps, the FSS megaship list, `SupercruiseDestinationDrop`, the `$Datascan_ShipUplink;` scan, and the `PowerplayMerits` that follows).
- It is fed by both the live controller (`PowerplayController.handle_event`) and the back-fill (`powerplay_backfill.replay_entries`), so the two agree.
- The ledger de-duplicates by megaship and system, and a merit event is counted once (`MegaShipScan.merit_at`).
- It is held back during a journal scan like any other live operation.
- Tests: `tests/test_megaship_scans.py`.

### Auto-Honk (`autohonk.py`)

It reads the commander's active Elite binds file to find which physical key the chosen fire button is bound to, then simulates that key held for a configurable time. On Windows this uses `user32.keybd_event` through `ctypes`, which avoids an additional dependency. On Linux it uses `xdotool` (section 18). Each platform's calls are behind an explicit platform check because EDMC runs on more than Windows.

## 13. Self-update

`update.py` is the single updater for the whole plugin: one version number and one GitHub Releases target.

Flow (all off the main thread):

1. Fetch the latest release from the GitHub Releases API (`releases/latest`) and ignore a draft or prerelease.
2. Compare versions numerically (padded to equal length so that `1.2` and `1.2.0` compare equal). A release that is not newer ends the flow.
3. Download the first `.zip` asset of the release to `updates/`.
4. Run the configured data backup (`data_backup.run_configured_backup`, forced) when it is switched on.
5. Back up the current install (code only) to `backups/<date>-<time>.zip`.
6. Unpack the release over the install.
7. Tell the UI to show "restart to apply".

Properties:

- **Opt-in.** Auto-update is off unless enabled in Settings (`wfmt_auto_update`). A `disable-auto-update.txt` file (`DISABLE_SENTINEL`) in the plugin folder disables it.
- **Staged.** Files are replaced on disk and take effect at the next EDMC start. Nothing reloads running code.
- **Data files are skipped.** During unpacking, an entry whose path inside the zip is a name in `_OWN_DATA_FILES` is not written. `_OWN_DATA_FILES` and `_OWN_DIRS` also keep listed data out of the pre-update backup. A new data file is added to `_OWN_DATA_FILES` (section 16).
- **Backups.** The last three (`BACKUPS_KEEP`) update backups are kept as `<date>-<time>.zip`. Only files matching that name are trimmed by the updater; the `pre-restore-` safety zips that share the folder are trimmed by `data_backup.py` (`SAFETY_KEEP`, 5). A backup excludes `_OWN_DATA_FILES`, the folders in `_OWN_DIRS` and `.pyc` / `.pyo` files.
- **Failures are logged.** A failed check or download is logged (the check at debug level, the download and staging at warning level) and returns.
- **Unsafe zip entries are skipped.** An entry that would be written outside the plugin folder (`..`, an absolute path, another drive) is skipped and a warning is logged.

### Other feature design notes

This subsection collects design notes that are not about self-update.

- **Exploration Dashboard.** (Rationale: [DESIGN_NOTES.md](DESIGN_NOTES.md#36-the-exploration-dashboard).)
  - `explore_dashboard.py` owns the window (`explore_dashboard_window.py`) and supplies `snapshot()`, which gathers:
    - the shared `system_survey.survey`
    - `exobiology_overlay.current_view()` (Organic Scanning's view of the body, with the first footfall flag merged from the survey)
    - the newest Status.json (`dashboard_status`, with the position part of the window following at most once a second)
    - `expedition_log_panel.book.running()`
    - the Route overlay's `status_lines`
    - `exploration_value.readouts()`
  - `explore_dashboard_data.py` converts these to rows with no Tk, so it is tested without a screen.
  - Each source is read inside its own try block, so one failing feature leaves a blank block and not a blank window.
  - Journal events redraw once, 150 ms after the latest.
  - Blocks and tables compare against what they last drew and rebuild nothing that did not change.
- **Carrier Route.** A separate window (`carrier_route_window.py`, opened from the Route Planner) over `carrier_route.py` (pure), `carrier_route_panel.py` (the owner), `carrier_route_spansh.py` (network) and `carrier_route_state.py` (`carrier_route.json`, one route per commander).
  - It uses Spansh's fleet carrier router (`POST /api/fleetcarrier/route`; the form and the answer are described in the module docstring, read from Spansh's page script).
  - It uses the same `spansh_planners.fetch_job` as the other plotters (a list in the form is sent as repeated fields, as Spansh's page does).
  - The carrier comes from the journal: `CarrierStats` (`CarrierType`, `Callsign`, `FuelLevel`, `SpaceUsage`), `CarrierLocation`, and `CarrierJump` or `Location` docked at the carrier's own callsign (a visit to another carrier never moves the commander's).
  - The recent journals are read once per commander when the window first opens.
  - Spansh's carrier constants are capacity 25,000 and mass 25,000 for a fleet carrier, and 60,000 and 15,000 for a squadron carrier.
  - `route_planner_panel` feeds it the journal events.
  - The route follows the carrier by system name, as the ship route does.
- **Route Planner.** (Rationale and alternatives: [DESIGN_NOTES.md](DESIGN_NOTES.md#37-the-route-planner).)
  - **Plotter.** It uses Spansh's exact plotter (`POST /api/generic/route`) and not the neutron router (`/api/route`, which requires a jump range that the game does not write for the current load). WFMT contains no code for the neutron router. The Expedition window's Neutron route button opens this planner.
  - **Request.** `route_planner.params_from_loadout` builds what Spansh's own page builds from a ship (read from its script):
    - `base_mass` = `UnladenMass` + `FuelCapacity.Reserve`
    - `tank_size` = `FuelCapacity.Main`
    - `internal_tank_size` = the reserve
    - the drive's `optimal_mass` and `max_fuel_per_jump` (`fsd_data.FSD`, replaced by the drive module's `FSDOptimalMass` and `MaxFuelPerJump` engineering modifiers), its `fuel_multiplier` and `fuel_power`
    - `supercharge_multiplier` (6 for the Mk II overcharge drive, else 4)
    - `injection_multiplier` 2
    - `range_boost` from a Guardian booster
    - `cargo` is Status.json's `Cargo` at the moment of plotting
  - **Systems** go by `id64`. The source is the arrival event's `SystemAddress` when the start is the current system, else `spansh_exact.lookup_system` (`/api/systems/field_values/system_names`); the destination is resolved the same way.
  - **Answer.** `spansh_planners.fetch_job` submits and polls (it also serves the older planners).
    - The answer's `result.jumps` lists every system with `distance`, `distance_to_destination`, `fuel_in_tank`, `fuel_used`, `has_neutron`, `must_refuel`, `must_inject` and `is_scoopable`, which become `Leg`s.
    - Spansh assumes a full tank at the start.
    - A drive missing from `fsd_data` raises `PlotterError` (shown in the ship block and when plotting).
  - **Saving the route.** The plotted route is saved per commander in `route_planner_route.json` (`route_planner_state.py`, over `commander_data.py`).
    - It is written when a route is set, on each arrival at a leg and when it is cleared.
    - It is restored by `PlotterController._follow_commander` when the first event with a commander arrives after a restart.
    - A route that was already finished is not restored. A route plotted before the commander was known is kept and saved for them.
    - The last choices are in `wfmt_neutron_plotter_options`.
  - **Auto-copy** (`wfmt_neutron_plotter_auto_copy`, on by default) is one setting shared by the panel's tick box and the window's (`PlotterController.set_auto_copy`). `copy_next` runs when a route is set, on each arrival at a leg, and on request.
  - **Status line.** The window's status line states what happened. `overlay_note` adds "Sent to the Route overlay." when `route_overlay.load_config().enabled`. `route_planner_window.announce` reports at each arrival and at the end of the route.
  - **Fuel scoop.** `ShipInfo.has_fuel_scoop` (an `int_fuelscoop_*` module in the `Loadout`) fills the ship block's Fuel scoop row and the warning after Generate route when there is none and the route has refuel stops.
  - **White dwarfs.** The option *Mark white dwarfs the route passes* (`Options.mark_white_dwarfs`) makes `spansh_exact.plot` call `edsm_client.primary_star_types` after the route is plotted.
    - That is the bulk `api-v1/systems` call with `showPrimaryStar`, 40 names per request.
    - `route_planner.mark_white_dwarfs` sets `Leg.white_dwarf` where EDSM reports the main star as a white dwarf.
    - Spansh did not plan with them, so they are extra boosts (`Leg.boost`).
    - A failed lookup leaves `Route.white_dwarf_check == "failed"` and marks nothing.
  - **Route overlay precedence.** `route_overlay.RouteOverlay.card` asks `active_neutron_route()` (the panel's route while it has a jump left) and, if there is one, draws `build_neutron_card` instead of the card made from the game's `NavRoute`. Both go through `navigation_card`.
    - When the last jump is made, the card states that the route has ended (`ended_card`) for `END_SHOW_S` (10 s), then `reset_neutron_route` clears the panel's route (or the tracker's route is dropped).
    - The panel asks the overlay to redraw whenever the route changes.
  - The window's **Expedition** button calls `expedition_panel.open_window`.
  - **Secondary star check.** `PlotterController.check_ahead` (on set, on each arrival and on restore) passes the next `route_secondary.WINDOW` (12) neutron stops that have a system address (`Leg.id64`, from the answer's `id64`) to a `SecondaryChecker`.
    - The checker fetches each system's stars with `spansh_exact.fetch_stars` (`GET /api/system/<id64>`) in the background.
    - `_poll_checks` collects the answers on the main thread into `Route.checked` and `Route.suspect`, which `build_neutron_card` (a `NEUTRON ?` tag in the warning color), the table and the arrival message read.
    - The rule (`neutron_is_secondary`) compares star names with the system's name and falls back to the database's main-star flag.
    - The result is not saved, so a restored route is checked again.
- **Hiding overlay groups.** (Rationale: [DESIGN_NOTES.md](DESIGN_NOTES.md#33-hiding-groups-of-overlay-cards-the-dashboards-two-switches).)
  - `overlay.set_group_hidden(name, prefixes, hidden)` hides the displays whose ids start with any prefix.
  - It sends a clear for the ones remembered in `_last`, and `_remember` stops new ones being sent, as `set_all_hidden` does, for those ids only.
  - It does not touch Settings, so showing a group re-sends what had not expired, which is the set of cards that were switched on.
  - Nothing is saved. Showing everything leaves a group that was hidden on its own hidden.
  - The dashboard's groups are `explore_dashboard.GROUPS`. `tests/test_overlay_group_hide.py` fails if a prefix there stops matching a real card.
- **Data backup.** (Rationale: [DESIGN_NOTES.md](DESIGN_NOTES.md#34-back-up-my-data-restore-and-automatic-backup).)
  - `data_backup.py` zips `_OWN_DATA_FILES` plus the `mining_sessions` folder into `WFMT-data-<date>-<time>.zip` in a folder the user selects (Settings > General > Backup).
  - It writes under a temporary name and renames it when complete, refuses a destination inside the plugin folder, and leaves out `LEFT_OUT` (`rcc_keys.json` and `discord_webhooks.json`, which hold secrets; `codex_catalog.json`, a cache) and `LEFT_OUT_DIRS` (`star_index`).
  - A new data file added to `_OWN_DATA_FILES` is backed up automatically. It is added to `LEFT_OUT` only if it holds a secret or can be fetched again.
  - `backup-info.json` lists the folder `mining_sessions/` as one entry, because those file names carry a commander name.
- **Restore.** A running WFMT holds its data in memory and rewrites the files, so a restore cannot overwrite them while WFMT runs.
  - `inspect_backup` checks a zip and refuses the whole zip on any other member. The rules:
    - it must hold `backup-info.json`
    - every other member must be a protected data file or inside `mining_sessions/`, with no absolute path, `..`, backslash or colon
    - keys and caches are refused
    - at most `MAX_RESTORE_BYTES` (1 GiB) unpacked
  - `stage_restore` unpacks it into `restore_pending/` and writes `ready.json` last.
  - `plugin_start3` calls `apply_pending_restore` before any feature reads a file:
    - it zips the files about to be replaced into `backups/pre-restore-<date>.zip` (the newest `SAFETY_KEEP`, 5, are kept)
    - it moves the staged files into place with `os.replace` and removes the folder
    - a folder without `ready.json` is discarded
  - `restore_pending` is in `_OWN_DIRS`, so the updater's own backup skips it.
- **Automatic backup.** Settings: `wfmt_auto_backup`, `wfmt_auto_backup_folder`, `wfmt_auto_backup_days` (1 to 90, default 7).
  - `load._schedule_startup_backup` runs `run_configured_backup` on a daemon timer 60 seconds after start-up (`STARTUP_BACKUP_DELAY_S`).
  - `UpdateManager._download_and_stage` runs it with `force=True` before the update is applied.
  - Files are named `WFMT-data-auto-<stamp>.zip`. `AUTO_KEEP` (10) of those are kept, and nothing else in the folder is deleted.

## 14. Testing

```bash
npm run test:docker
```

This runs `python -m unittest discover -s tests` and then `tests/import_smoke.py` inside a Linux container on a virtual display, so no window opens on the desktop (see [DEVELOPMENT.md](DEVELOPMENT.md)). Tests are not run on the host.

Suites cover the pure-logic modules:

- procedural name parsing and sequence walking (cross-validated with real boxel data)
- region-sweep queues, waypoint routing, survey log
- Canonn data parsing, organic species matching, Codex tallying
- deposit estimates and Rhino coverage

Test files add the repository root to `sys.path` and import `plugin.<module>` directly, which works because those modules avoid EDMC-only imports (section 6).

**Trade and data files**

- Trade mode's logic is covered by `tests/test_trade.py` and `tests/test_trade_search.py` (ledger, market parsing, Spansh response parsing, commodity names, ship pads, offer ranking, carrier cargo tracking and the journal backfill).
- `tests/test_own_data_files.py` reads the sources and fails if a plugin module defines a `*FILENAME` data file that is missing from `update.py`'s `_OWN_DATA_FILES`.
- `tests/test_import_smoke.py` imports every plugin module (including `load.py`) with EDMC's modules stubbed, in a subprocess, to detect import-time failures that single-module tests miss.

**Tk smoke tests**

- `tests/trade_windows_smoke.py` (run by `tests/test_trade_windows_smoke.py`) opens the Session, Routes and Market windows against a stand-in controller and checks the buttons, the settings and the redraws.
- The settings in windows have the same kind of test: `tests/mining_window_settings_smoke.py`, `missions_types_window_smoke.py`, `powerplay_bgs_settings_smoke.py`, `inventory_settings_smoke.py`, `colonization_settings_smoke.py` and `exploration_settings_smoke.py`, each run by a `tests/test_*.py` wrapper in a subprocess.
- `tests/trade_history_window_smoke.py` opens the History window and visits every tab.
- `tests/trade_view_smoke.py` draws the Trade page in a real window with EDMC stubbed, in a subprocess (skipped when there is no display), and checks widths, redraws and column alignment.

**Other coverage**

- **Help tab buttons:** `tests/test_issue_report.py` (the prefilled address, the log filter, the redaction, the clipboard hand-off, and that the form template carries the `environment` field the code fills in).
- **Engineering:**
  - `tests/test_blueprints.py` pins the corrections and additions (five recipes, seven synthesis rows, the Colonia four's upgrades, the nine materials).
  - `tests/test_engineers.py` covers the 38-engineer location table, its regions and name matching.
  - `tests/materials_smoke.py` opens the Engineering window (every tab, the Show filter, the Ship planner).
- **Ship planner logic:** `tests/test_ship_plan.py` (parsing SLEF and `Loadout`, module types, grades and effects, merging, limits, and that every link in the generated `journal_blueprints.py` points at a row the table has).
- **BGS:**
  - `tests/test_bgs_ledger.py` covers `repair_record` and `merge_records`.
  - `tests/test_bgs_panel_repair.py` (in a subprocess, with EDMC stubbed) covers the panel's roll, replay and filing of a closed period.

Not covered by automation: anything else that needs a live EDMC or a Tk window (panels, dialogs, overlay rendering). Those are checked by hand in an EDMC install. Overlay rendering changes are verified against ModernOverlay's own payload log.

## 15. Gotchas

- **Themed widgets take `foreground=`, not `fg=`.** EDMC's `nb.Label` is ttk-backed. Passing the classic `fg=` raises `TclError: unknown option "-fg"`. One such label broke WFMT's entire Settings window, because the error aborted building the whole tab.
- **`theme.update()` may do nothing.** During `plugin_app`, EDMC's theme registry is still empty and `theme.update(widget)` returns early without registering. It also recolors direct children only. `ui.py` therefore retries `panelkit.apply_theme_deep` at 0.5, 1.5, 3 and 6 seconds, walking the whole subtree.
- **The clipboard needs `update()`.** After `clipboard_append`, `panelkit.copy_to_clipboard` calls `update()` so that ownership transfers before focus returns to the game. Without it, a paste can obtain stale content.
- **Separator color is set statically** from a light-or-dark choice and not read back through the theme, for the same registry-timing reason.
- **A package takes precedence over a same-named module.** The window kit is `plugin/uikit/` and not `plugin/ui/`, because `ui.py` (the main-panel builder) exists.
  - A `ui/` directory replaced it and EDMC reported `module 'WFMT.ui' has no attribute 'create_plugin_app'`.
  - `tests/test_ui_kit.py` and `tests/test_import_smoke.py` guard this.
  - The deploy is a merge-copy that never deletes, so renaming or removing a module leaves the old file in the installed plugin folder. Stale files there must be deleted by hand.
- **ttk is global.** Anything that changes a ttk theme or stock style from a window affects the whole EDMC process. Namespaced style names (`WFMT.X.Treeview`) are safe; stock ones are not.
- **Tk option patterns match widget names**, not paths. `.!toplevel3*Label.background` is read as an application name and matches nothing.
- **A `tk.Label` cannot take a tuple `padx`** (only `pack` and `grid` can). Indentation uses spaces.
- **Case in commander and system names.** Store the original; compare with `casefold()`.
- **No order between Status.json and the journal.** They are independent callbacks.
- **A label that spans columns can stretch them.** In a Tk grid, a widget spanning columns 1 to 3 that is wider than those columns' combined width widens them, so a title column sized for the narrower layout overflows the window. The width each column needs (the wider of the table's numbers and any spanning value) is computed before the title column receives the remainder. `tests/trade_view_smoke.py` detects it.
- **A price-sorted list can be all fleet carriers.** Carriers sell very cheaply and pay very well, so a galaxy-wide search sorted by price returned only carriers and the panel reported that no station had the commodity. Stations and carriers are requested separately with the `type` filter (`trade_prices.STATION_TYPES` and `CARRIER_TYPES`).
- **Spansh market names are exact and case-sensitive.** "Liquid oxygen" works, "Liquid Oxygen" returns zero results with no error, and the journal's plurals can differ from Spansh's. A search that finds nothing without an error is the symptom. Every name is resolved through `trade_commodities.resolve`.
- **Journal files do not sort by name.** The game has used two file-name styles (`Journal.<date>T<time>.01.log` and `Journal.<yymmddhhmmss>.01.log`), so "the newest N" is determined from modified time (`trade_carrier.journal_files`). Sorting by name can select the wrong files.
- **Journal names and EDMC names differ in case.** `EXAMPLECMDR` in the journal, `Examplecmdr` from EDMC. Per-commander keys use `casefold()`.
- **`CarrierStats` is not automatic and is not replayed.** It exists only if the player opened Carrier Management, so state built from it needs a journal backfill at startup, and a baseline from before WFMT started is otherwise missed.
- **A `CargoTransfer` does not state where it went.** The docked station's `MarketID` is compared with `CarrierID`; "my carrier" is not assumed.

**Settings tabs and `pack`**

- EDMC's `myNotebook.Frame.__init__` grids a spacer child into every `nb.Frame`, so `pack` inside one fails with "cannot use geometry manager pack inside ... which already has slaves managed by grid".
- A feature whose `build_settings` raises takes the whole WFMT Settings tab down (`Failed for Plugin "WFMT"` in the EDMC log), on Windows and Linux.
- Use `grid` inside `nb.Frame`s, or pack into a plain `tk.Frame` as `autohonk.py`'s rows do.
- This shipped once, in a build that was withdrawn, because the unit-test stand-ins had no spacer. `tests/test_prefs_smoke.py` now builds every tab with stand-ins that have one. `tests/test_settings_layout.py` fails on any `pack` into an `nb.Frame`.

## 16. Adding a feature

1. Put pure logic in its own module with no Tk and no EDMC-only imports. Add a `unittest` file.
2. Add `xxx_state.py` if the feature persists data: per commander (use `commander_data.py`), atomic write, tolerant load.
   - Give any new file a unique name, add it to `_OWN_DATA_FILES` (section 13) and state in `tests/test_data_files_per_commander.py` how it keeps commanders apart. A commander name must not appear in a file name.
   - Reset any in-memory state about the previous commander when the active one changes.
   - Account for Windows and Linux (UTF-8, `os.replace`, no assumptions about case-sensitive file names) and note in `LINUX_TESTING.md` what is untested on Linux.
3. Add the panel module implementing the contract (section 4). Choose `PANEL_PLACEMENT`.
4. Use `panelkit.wrap_label` for any text from the game, and a hard box for any image (section 5).
5. Put network calls behind the worker, queue and generation-counter pattern (section 7; Trade's one-job-at-a-time variant is described there). Failures return an empty result. Automatic lookups are opt-in.
6. If the feature draws an overlay, use the shared client, a `wfmt_<feature>_` ID prefix, and register a group.
7. Prefix config keys `wfmt_<feature>_`.
8. Add the module to `FEATURES` (`ui.py`) and `_FEATURES` (`load.py`). Call `start` and `stop` from `load.py` if it has them.
9. If it uses another project's code, assets or data, check the license and update `THIRD-PARTY-NOTICES.md` (and `ATTRIBUTIONS.md` for ideas) in the same change, before it ships.
10. If it must not miss play while EDMC is closed, give it a start-up catch-up built on `journal_files.py` with a rule that never counts an event twice (a timestamp watermark, per-fact timestamps or an idempotent merge; see "Catching up on state EDMC missed"), and add its row to the table in the user guide's "If EDMC wasn't running".
11. Update the README and the user guide, including the guide's "What the game does and doesn't tell us, and how to work around it" section: what the journal never records or records late, what the screen shows when it is unsure, and what the player can do.

## 17. Known gaps

- **`_OWN_DATA_FILES` is a hand-kept list.** A new data file must be added to it (and a new data folder to `_OWN_DIRS`) or it is included in the pre-update backup.
  - Data is not at risk of being overwritten, because it is not in the release zip.
  - `tests/test_own_data_files.py` fails when a `*FILENAME` constant is not listed. A data folder is not checked.
- **Mining and other panels have no automated UI tests** (section 14).
- **Tick detection depends on a third-party, plain-HTTP service** with no service-level agreement. When it is unavailable, the tally does not roll over.
- **Trade mode's gaps** are listed in its [spec](TRADE_TECH_SPEC.md#13-verified-assumed-and-known-gaps): a squadron carrier's `CarrierStats` is assumed to match a fleet carrier's, the commodity list and ship pad classes are snapshots, and carrier reserved space is only as current as the last Carrier Management visit.
- **Inventory's start-up sync relies on EDMC rebuilding its state** (backpack, ship locker) from the journal before it sends `StartUp`. This was not verified against every EDMC version.
- **Powerplay hand-in windows are a heuristic.** `PowerplayDeliver` precedes the merits it earns but does not link to them, so the first merit event within 10 minutes and any within 10 seconds of the last are labeled Delivery. A merit from another activity inside that window can be mislabeled.
- **`FactionKillBond` has no ship type**, so an on-foot combat-zone kill counts as a ship kill for mission progress.
- **Boxel Survey's survey log is not caught up** after a restart (its counter is not idempotent).
- **Exobiology and region data are a snapshot.** New species from a game update require regeneration.

## 18. Platform support: Windows and Linux

Except for a few features, WFMT is platform-neutral Python and Tk. The platform-specific parts are isolated in `platform_support.py` (plus the Windows branches in `autohonk.py` and `screenshot_automation.py`).

| Concern | Windows | Linux |
|---|---|---|
| Journals and `Status.json` | EDMC's Journal directory setting (EDMC finds the default) | The same setting, with no default. It must point at `<prefix>/drive_c/users/<user>/Saved Games/Frontier Developments/Elite Dangerous`. An empty value means "nothing to scan" |
| Elite's bindings folder | `%LOCALAPPDATA%\Frontier Developments\Elite Dangerous\Options\Bindings` | The same path inside the Wine/Proton prefix (below) |
| Elite's screenshot folder | Shell "Pictures" known folder (`SHGetKnownFolderPath`), with OneDrive redirect handling | `Pictures/Frontier Developments/Elite Dangerous` inside the prefix, else `~/Pictures` |
| Screenshot event `Filename` | `\ED_Pictures\Screenshot_0001.bmp` | The same Windows-style string (Elite writes it under Proton), so the file name is taken with `screenshot_naming.journal_basename` and not `os.path.basename` |
| Find the game window | `FindWindowW` (ctypes) | `xdotool search --name "^Elite - Dangerous"` |
| Is the game in the foreground | `win32gui.GetForegroundWindow` (bundled pywin32) | `xdotool getactivewindow getwindowname` |
| Send a key | `keybd_event` (ctypes for Auto-Honk, pywin32 for screenshots) | `xdotool` (XTEST); a hold is one `keydown`, `sleep`, `keyup` call (`platform_support.hold_key`) |
| Is a companion app running | `tasklist` | `pgrep -f` |
| Notification sound | `winsound.MessageBeep` | `canberra-gtk-play`, else `paplay` with the freedesktop theme file |
| Overlay | The built-in overlay or EDMCModernOverlay (a choice under Overlay Connection) | EDMCModernOverlay, same TCP protocol (the built-in overlay is Windows only) |
| Modal dialogs | `grab_set` works immediately | `uikit.style.grab_when_visible`: X11 refuses a grab until the window is mapped, so it retries briefly |
| Plain `tk.Listbox` colors | `SystemWindow` / `SystemWindowText` | `white` / `black` (those names are Windows-only Tk colors) |
| Open a link in the browser (Report an issue, the Raven and Inara links) | `webbrowser.open` | `webbrowser.open` (the desktop's default browser, through `xdg-open` or similar). Not checked from a Flatpak EDMC |
| The OS line of a bug report | `platform_support.describe_system()`: Windows release and build | The same function: distribution (`PRETTY_NAME`), `XDG_SESSION_TYPE`, and `Flatpak` when applicable |
| EDMC's log, for Copy diagnostics | The file handler of EDMC's logger, else `<app dir>/logs/EDMarketConnector-debug.log` | The same. A Flatpak EDMC keeps it under `~/.var/app/io.edcd.EDMarketConnector/data/EDMarketConnector/logs/` |
| Paste a ship loadout (Ship planner) | `tk` clipboard (`clipboard_get`) | The same. It needs a clipboard owner on X11 or Wayland, and the box accepts a manual paste if the button reports no text |
| Text symbols in the UI | Any | Only symbols every font has (`×`, `★`, `→`). `✕` is not used because some Linux fonts lack it |
| Settings notes | "This system: Windows - supported" | "This system: Linux, xdotool found / NOT found" (`platform_support.input_support_note`, `sound_support_note`) |

**Wine/Proton prefix**

- Elite is a Windows game. Under Steam Proton it uses a Windows profile stored at `.../steamapps/compatdata/359320/pfx/drive_c/users/steamuser/`, so its "Local AppData" and "Pictures" are ordinary Linux folders inside that prefix.
- `find_elite_prefix` looks in the usual Steam roots (native, `~/.steam` symlinks, Flatpak), follows `libraryfolders.vdf` to other drives, and accepts a user-set path (the prefix, its `pfx` folder, or the `compatdata/<id>` folder).
- Lutris and plain Wine use the real username instead of `steamuser`, which `prefix_user_dir` handles.
- An invalid override does not fall back to auto-detection, so a typo is visible and no different prefix is used silently.

**xdotool through `subprocess`**

- It adds no Python dependency to EDMC's bundled environment, and it works on X11 and on XWayland, where a Proton game's window lives even on a Wayland desktop.
- `python-xlib` would need installation into EDMC's Python, and `evdev` or `uinput` need device permissions.
- Keys are sent with XTEST after focusing the window, because per-window synthetic events (`--window`) are ignored by most games. This corresponds to Windows, where `keybd_event` goes to the foreground window.

**One process per hold**

- XWayland releases a synthetic (XTEST) key about a second after the `xdotool` process that pressed it exits.
- A separate `keydown` process, a Python `sleep` and a `keyup` process therefore held the key for only about a second, and a honk needs several.
- `hold_key` runs `xdotool keydown K sleep N keyup K` as one process, which keeps the key down for the full time.

**Flatpak EDMC**

- The sandbox sees neither host programs nor the game's folders.
- `platform_support._tool_command` uses a sandbox copy of a tool when one exists, and otherwise runs `flatpak-spawn --host --directory=/ <tool>` after probing that the host has the tool (only a successful probe is cached).
- `pgrep` prefers the host, because the sandbox sees only its own processes.
- `--directory=/` is required: `flatpak-spawn` starts the host command in the sandbox's working directory, which for EDMC (`/app/edmarketconnector`) does not exist on the host.
- The user must grant `--talk-name=org.freedesktop.Flatpak` and filesystem access to the journals, Bindings and Pictures folders (see the Linux guide, Step 3).
- EDMCModernOverlay needs the same talk permission to start its overlay window; without it, the overlay's port answers while nothing is drawn.

**Failure behavior**

- Every wrapper returns `False`, `None` or an empty list and does not raise.
- A missing `xdotool` produces an explicit outcome ("xdotool isn't installed") and not a silent no-op.
- `screenshot_automation.SUPPORTED` is false without it, so the timed-capture controls do not appear.

**Journal location**

- EDMC's Journal directory setting is the source for journals and `Status.json`.
- On Linux it usually has no default, so code that reads it treats an empty value as "nothing to scan" (a bare `Path("")` would scan the current directory, and `Path(None)` raises).
- `platform_support.journal_dir_advice` compares that setting with the prefix's `Saved Games/Frontier Developments/Elite Dangerous` (following symlinks) and returns a one-line hint, shown in Settings and logged at startup.
- It only advises. The folder can legitimately be linked elsewhere, so WFMT never changes EDMC's setting.

**Overlay**

- WFMT's overlay client is plain loopback TCP with newline-delimited JSON and is platform-neutral.
- EDMCModernOverlay runs a legacy listener on `127.0.0.1:5010` on both Windows and Linux.
- Plugin Group registration imports ModernOverlay's own module and does nothing if it is absent.

**Case sensitivity**

- Windows ignores file-name case and Linux does not.
- Elite writes `Status.json` (capital S), so code requests that exact name. A lowercase `status.json` works on Windows and fails on Linux.
- Journals match `Journal.*.log`.
- File access uses the game's exact spelling.

**Windows-only behavior** (OneDrive folder-redirection handling, the "Controlled Folder Access" error text and the shell Pictures lookup) is gated on Windows, so Linux users do not see it.

**Settings labeling**

- A feature that depends on the operating system shows a **Works on:** line in its Settings tab, colored green when this machine can run it and orange when it cannot (with the reason).
- The features are Auto-Honk, the Screenshots auto-timer and Thargoid capture, and the Inventory pickup sound. The Overlay Connection tab has no such line; its text states which overlay runs where.
- The BGS tab shows the Linux journal folder hint.
- The wording is in `platform_support.py` and is unit-tested.

**Status**

- The Linux paths are unit-tested with mocked subprocess calls and temporary directories (`tests/test_platform_support.py`).
- What has been run on a real Elite install is recorded in `LINUX_TESTING.md`.
- Key simulation is unsupported on Wayland without XWayland and on macOS.

### 18.1 Platform notes for the session strip (`game_mode.py`, `session_credits.py`)

Both modules are platform-neutral by construction:

- **Journal source.** They read only journal events (`LoadGame`, `StartUp`, `Shutdown`) and EDMC's `state["Credits"]`, which EDMC supplies identically on Windows and Linux. `StartUp` recovery reads the top of the current journal file with an explicit UTF-8 encoding and tolerates a missing or unreadable file.
- **`monitor.logfile`** is a `str` on some EDMC versions and a `pathlib.Path` on others.
  - It is imported lazily (so tests run without EDMC) and converted with `str()` before it is compared or written to JSON.
  - Powerplay's session store uses the same conversion.
  - Journal-file identity is compared as the exact string EDMC provides, so Windows drive-letter paths and Linux Wine/Proton paths behave the same.
- **Saved state.** `session_credits.json` is written to a temp file then `os.replace`d (atomic on both), at most once per 30 seconds plus on start and stop. A read-only plugin folder only logs a warning.
  - Time stamps are UTC and parsed with `calendar.timegm`, not the local-time `mktime`, so a DST change or a different time zone does not skew the hourly rate.
- **Display.** Number formatting is fixed (`f"{n:,}"`) and not locale-dependent. The glyphs used are the ellipsis and ordinary punctuation.
  - Both labels are `panelkit.wrap_label`s inside one frame, so a long private-group name wraps instead of widening EDMC's window.
  - The credits line is shown on every mode.
- `session_merits.py` provides the "Merits this session" line under it (`line_visible`; `ui._apply_panel_mode_visibility` calls `set_hidden` so the Powerplay page, whose Session and Cycle lines carry the merits, does not repeat it).
  - It keeps no data: the merits and the session start come from Powerplay's session record (`powerplay.controller.sessions.current`), and `powerplay._refresh_panel` and the feature dispatch (it runs after Powerplay in `load._FEATURES`) refresh it.
  - It is hidden (`grid_remove`) until the session has a merit, and while the Powerplay mode is showing.
  - The rate is merits over the time from `started_at` (parsed with `calendar.timegm`, as UTC) to now.

### 18.2 Platform notes for Trade mode (`trade_*.py`)

Nothing in Trade is OS-specific.

- It reads journal events, EDMC's `state`, and `Market.json` from the journal folder (`config.get_str("journaldir")`, which on Linux is the Proton prefix's journal path), and makes HTTPS requests with `urllib`.
- All file reads use an explicit UTF-8 encoding (`errors="replace"` for journals), writes are temp-file-then-`os.replace`, and the carrier backfill ignores a missing folder.
- Background work is a plain daemon thread plus `queue` and polling; no thread touches Tk.

The parts that depend on the platform:

- The type-ahead popup (a borderless `Toplevel`, so it depends on the window manager for stacking and focus).
- The backfill finding a Proton journal folder.

`LINUX_TESTING.md` section 6d holds the checks and their status.

### 18.3 Cross-platform review of the modules

The modules in `plugin/` and `plugin/uikit/` are held to the rules below, which keep them free of Windows-only and Linux-only assumptions outside the `platform_support` branches.

1. **A scan of every module** (AST and text) for platform signals: Win32 and `ctypes` use, `subprocess`, `winsound`, `os.startfile`, `sys.platform` branches, `.exe`, PowerShell and `xdotool` strings, Windows-only Tk color names, Windows paths and environment variables, `open()` without an explicit encoding, `strftime` directives that differ by platform, and file-name case.
   - Most modules have no platform signal (pure logic or plain Tk).
   - The ones that do have their platform-relevant code in `platform_support`, `inventory_sound`, `screenshot_automation`, and the key-injection, Settings and path code of `autohonk`, `screenshots`, `screenshot_convert`, `screenshot_naming`, `overlay`, `load`, `update` and the journal readers `codex_backfill`, `mining_journal_backfill` and `exploration_value`.
2. **Cross-cutting rules over all modules:**
   - Relative imports match the real file names exactly (a case mismatch passes on Windows and fails on Linux), and no two tracked paths differ only by case.
   - No `threading.Thread` target touches a Tk widget directly.
   - Every modal dialog uses `uikit.style.grab_when_visible` and not `grab_set()`, which X11 can refuse before the window is mapped.
   - Every mouse-wheel binding handles both Windows deltas and X11 `Button-4/5`.
   - All generated file names avoid characters Windows rejects.
3. **Rules that follow from platform differences:**
   - Screenshot `Filename` values are Windows-style even under Proton, and `os.path.basename` does not split on a backslash on Linux, so the name is taken with `screenshot_naming.journal_basename` (tested).
   - BGS states in Settings, and logs, when no journal folder is set, instead of skipping silently.
   - Settings tabs for OS-dependent features state where they work and whether they can here (for example, Screenshots auto-capture works on Windows and on Linux with `xdotool`).

Not verifiable from a Windows development machine, and covered only by `docs/LINUX_TESTING.md`: real `xdotool` behavior, Tk popup stacking and focus under each Linux window manager, Proton prefix layouts other than Steam's, and sound players.
