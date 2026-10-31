# WFMT Technical Guide

How Wayfarer's Multitool works, and why it's built that way. This is a learning and reference document: it explains the design decisions, including the mistakes that produced some of them.

Where to go for other things:

- What each feature does for the user: the [README](../README.md).
- Features in depth, the specifications: [Missions](MISSIONS_TECH_SPEC.md), [Mining](MINING_TECH_SPEC.md), [Trade](TRADE_TECH_SPEC.md), [Boxel Survey](BOXEL_SURVEY_TECH_SPEC.md), [BGS](BGS_TECH_SPEC.md), [Organic Scanning](ORGANIC_SCANNING_TECH_SPEC.md), [Powerplay](POWERPLAY_TECH_SPEC.md) and [Screenshots and input automation](SCREENSHOTS_AND_INPUT_TECH_SPEC.md).
- Setting up on-screen overlays: [OVERLAY_SETUP.md](OVERLAY_SETUP.md).
- The reasoning behind the main decisions and what was tried and dropped: [DESIGN_NOTES.md](DESIGN_NOTES.md).
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

**The design principle behind everything below**

- A third-party tool for Elite Dangerous only knows what the game writes to its journal files (and the small, live `Status.json`), and not everything is logged. So WFMT is built journal-first: every feature starts from the events the game does write.
- Where the journal is silent it adds, in this order:
  1. Frontier's own data when EDMC is signed in (CAPI: a carrier's cargo, the Carrier Locker).
  2. Data that players and communities report (Spansh, EDSM, Canonn, edastro, Raven Colonial; section 11).
  3. Its own bookkeeping, estimates and user steps (such as opening Carrier Management so the game writes `CarrierStats`), each labeled as what it is.
- Until Frontier expands the journal or offers a broader API, those workarounds are the design, not exceptions to it.
- Each one is recorded as a gap and a workaround in the matching user guide (the "What the game does and doesn't tell us" table) and, where it shapes the code, in the notes below.

## 1. Where WFMT runs

WFMT is not a program. It is a plugin loaded into **EDMC** (Elite Dangerous Market Connector), a
Python/Tkinter desktop app that watches the game's journal files and lets plugins react to them.
Three consequences shape almost everything below:

- **EDMC owns the process, the window and the event loop.** WFMT never starts its own Tk root or
  main loop. It receives a parent frame and fills it.
- **EDMC calls WFMT; WFMT doesn't poll.** The game writes journal events, EDMC reads them, and EDMC
  calls the plugin's hooks. Status.json and CAPI data arrive through separate hooks (section 9).
- **The main window is shared.** Every installed plugin lives in the same window (section 5).

EDMC discovers a plugin by finding `load.py` in a folder under its `plugins` directory. It then calls
a fixed set of module-level functions if they exist.

## 2. Repository layout, build and deploy

```
plugin/           everything that ships; becomes the Wayfarers-Multitool folder
  load.py         EDMC entry point (the hooks)
  ui.py           main panel, mode buttons, Settings tab: orchestration only
  panelkit.py     shared Tk helpers (wrapping, separators, toggles, tooltips, collapsible sections, theming)
  overlay.py      the one shared overlay client
  update.py       the one self-updater
  <feature>*.py   one or more modules per feature (every module is listed in MODULES.md)
tests/            unittest suites for the pure-logic modules
.github/          ISSUE_TEMPLATE/bug_report.yml, the form the Report an issue button opens (not shipped in the zip)
.githooks/        commit-msg (enforces the commit message form) and pre-commit (runs scripts/check_docs.py); enable with core.hooksPath
docker/           Dockerfile and run-tests.sh for the headless test run (`npm run test:docker`, via scripts/docker-test.mjs)
scripts/          dev only, none of it ships:
  build.mjs, package.mjs, env.mjs     build, zip and install the plugin (env.mjs finds EDMC's plugins folder)
  gen_journal_blueprints.py           regenerates plugin/journal_blueprints.py from public lists (needs the network)
  gen_organic_variants.py             builds plugin/organic_variant_data.py from published color-variant rules
  verify_organic_variants.py          checks the color predictions against your own journals
  analyze_exo_observations.py         checks the species prediction against the recorded finds
  native_overlay_test.py              draws real overlay cards over Elite to look at (Windows only)
  check_docs.py                       checks the docs against the code (links, screen labels, Settings paths, file names, code references, version)
  docker-test.mjs                     runs the tests in the container (`npm run test:docker`)
docs/             this file, the development guide, the feature specs, the overlay guide, acknowledgements
```

[MODULES.md](MODULES.md) lists every module with a one-line description; `tests/test_docs_modules.py` keeps it complete.

`npm run build` copies `plugin/` to `dist/Wayfarers-Multitool`, skipping `__pycache__` and `.pyc`, and also copies
`LICENSE` and `THIRD-PARTY-NOTICES.md` into it. `npm run package` zips that folder, keeping the
`Wayfarers-Multitool/` folder as the zip's top level so extraction produces a ready-to-copy folder.

**Why Node for a Python project?** The scripts only copy files and call a zip tool, and `package.json`
gives a memorable `npm run build` entry point. There is no Python packaging step because EDMC loads
plugin source directly.

**Why the license files are copied into the build:** WFMT is GPL-3.0 and carries some third-party
data whose notices must accompany it. Copying at build time means the notices travel with every
installed copy, not just the repo.

To try a build in EDMC, copy `dist/Wayfarers-Multitool` into EDMC's plugins folder as a *merge*, never
delete-then-copy, because a live plugin folder holds per-commander data files that are not in the
build (section 8). `npm run deploy` does that merge for the current OS. EDMC must be restarted to load the new code. See [DEVELOPMENT.md](DEVELOPMENT.md).

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

`journal_entry` does one thing:

```python
feature_dispatch.dispatch(_FEATURES, entry, cmdr, system, station, state, logger)
```

Every feature receives every event and decides itself whether it cares and whether it is enabled.

- `feature_dispatch.dispatch` calls them one at a time and catches a feature's exception (logging it with its traceback and the event name), so one failing feature cannot stop the ones after it from seeing the event.
- A plain loop would let one failure leave the BGS, Mining, Trade and ledger features without a commander when EDMC started with the game closed.
- `tests/test_feature_dispatch.py` also fails if any plugin module uses a name it never defines.

**Catching up after an EDMC restart**

- EDMC replays nothing to plugins, so a feature that must not miss play with EDMC closed reads the journals itself.
- `journal_files.py` is the shared part (folder, files changed since a moment, a filtered event reader).
- The rules for not counting an event twice are each feature's own and are always a watermark or an idempotent merge:
  - Trade (`trade_journal_scan.py`, timestamps per fact)
  - Powerplay (`powerplay_backfill.py`)
  - BGS (`bgs_journal.py`)
  - Missions (`journal_scan.py`)
  - Colonization (`colonization_catchup.py`, per-site `journal_at`)
  - Codex (`CodexTally.last_event_at`)
  - Boxel Survey's visited systems (a set union)

**Why not route events by type in `load.py`?**

- Then `load.py` would need to know which events each feature reads, and adding or changing a feature would mean editing a central file.
- Calling every handler is cheap: each returns after a dictionary lookup or two. The cost is a few microseconds per event.
- The benefit is that `load.py` never changes when a feature does.
- The one rule that makes this safe is that handlers only *read* `entry` and `state`; none mutate them, so handler order doesn't matter.

## 4. The feature-module contract

Every feature module exposes the same small interface, which `ui.py` and `load.py` rely on:

| Name | Purpose |
|---|---|
| `PANEL_PLACEMENT` | A mode key (`"exploration"`, `"mining"`, ...) to build inside that mode's frame; `"always"` to build once outside any mode; or `None` for a Settings-only feature |
| `build_panel(parent)` | Build the main-window widgets (skipped when placement is `None`) |
| `build_settings(notebook)` / `save_settings()` | Build and persist this feature's Settings tab |
| `handle_event(entry, cmdr, system, station, state)` | React to journal events |

Larger features add `start(plugin_dir)` and `stop()` for loading and flushing state, and optionally
`set_overlay_client(client)`.

**Why a contract instead of `ui.py` building everything?**

- A `ui.py` that every feature reaches into tends to grow into a thousand-line file.
- With the contract, `ui.py` stays a thin orchestrator: it walks the `FEATURES` tuple, builds each feature into its own child frame with a separator between, and never learns feature internals.
- Adding a feature means writing one module and adding it to two tuples (`FEATURES` in `ui.py`, `_FEATURES` in `load.py`).

**Why `panelkit.py` exists**

- Feature modules import `panelkit`, never `ui`. If a popup window imported helpers back out of `ui.py`, that would create a circular dependency.
- Putting shared, content-agnostic helpers in a third module that both sides import breaks that cycle by construction.

**Stacking and pairing**

- `ui._stack_features` gives each feature its own frame and inserts a separator between consecutive ones. Features never pick their own grid rows, which removes the possibility of row collisions.
- A small `_SIDE_BY_SIDE_PAIRS` table puts two narrow features (Auto-Honk and Discovery Alerts) in one row to save vertical space.
- That one row also carries the Neutron Star and White Dwarf buttons (built by `discovery.py`) and Boxel Survey's Random button (`boxel_survey.build_random_button`, called from `ui.py` with `discovery.controller.button_row`, so it stays usable while Boxel Survey is collapsed).
- Every button there is packed with the same 6px gap as the mode buttons.
- The Neutron Star / White Dwarf result line and Random's status line sit below the row.

**Button names and tooltips**

- Every button, on the main panel and in the pop-out windows, has a tooltip: `panelkit.add_tooltip` gives the name and a one-line description on hover ("Name - what it does"). A window button passes it as `tip=` to `FlatButton`, `shell.add_action` or `shell.add_menu`; the tip may be a function, read each time it opens, for a button whose caption changes with its state. The user guide's "Button names" lists the panel's buttons.
- The tooltip is a borderless `Toplevel`, so it can't affect the main window's size.
- The mode buttons carry the `PANEL_MODES` labels as written; their tooltips (`ui._MODE_TOOLTIPS`) give the name and a one-line description.
- EDMC sizes its window to the widest row across all plugins, and the mode row is WFMT's widest. Panel buttons carry their full names, and a row that could pass that width wraps (`panelkit.flow_buttons`), so the window does not grow.
  - So it is held at the size measured from a throwaway row of full-label buttons (`ui._mode_row_full_label_size`), which the buttons now match.
  - Without that, shortening the labels again would make EDMC open far narrower.
  - Don't implement this with a thin spacer widget in the same grid cell: it draws a line across the buttons.

**Settings layout**

- `ui._build_settings_tabs` builds eleven top-level Settings tabs, sorted alphabetically by label (`_sort_tabs`): BGS, Colonization, Discord, Exploration, Operations, General (Window, Updates, Backup, Help, Online lookups, Shortcuts), Mining, Missions, Overlays, Powerplay and Trade.
- A group is a plain tab holding its own `nb.Notebook` (`_settings_group`).
- Everything is placed with `grid`.
- Features not listed fall into "Other" rather than losing their tab.
- Every page is wrapped by `settings_scroll.scrolled_page`, which caps its visible height (between 260 and 640 px, from the screen height less 530 px for the window chrome) and adds a scrollbar past it, so a long page cannot push EDMC's Settings window, and its OK button, off the screen.

The **Overlays** group holds every overlay setting and toggle:

- Overlay Connection, Appearance, Overlay Placement and Hide overlays, then one tab per feature that draws on the overlay (Colonization, Discovery, Inventory, Interdiction Warning, Flight Alerts, Route, System targets, Body info, Exobiology, Expedition Log, Powerplay, Missions, Landing, Surface Compass, Mining, Notable Bodies, Screenshots).
- Interdiction, Landing, Discovery and Notable Bodies are overlay features through and through, so their whole `build_settings` is listed there.
- Colonization, Inventory, Mining and Screenshots keep their other settings in their own tabs (Colonization, Operations, Mining) and expose a second builder, `build_overlay_settings`, for the Overlays group.
  - It shares the controller's variables so `save_settings` is unchanged (it skips a variable whose tab was not built).

In Exploration, POI Reference (GEC and Canonn) and Codex share one "POI Reference" page:

- `_SectionStack` is an `nb.Frame` whose `add()` grids each feature's frame one under the other.
- Features still call `notebook.add(frame, text=...)` unchanged.

**Height fitting**

- Once a window has an explicit size, Tk stops fitting it to its content.
- `ui._sync_mode_holder_height` is the single place the panel's height changes (mode switch, startup, a section expanding), and it schedules `ui._fit_window_height` once at idle.
- `ui._fit_window_height` sets the top-level window's geometry to its current width and the height its content requests (`winfo_reqheight`), so a taller mode is never cut off.
- It is skipped when the window is maximized, minimized or not yet visible, and keeps the width and position.
- The Settings → Window tab has a checkbox (`wfmt_fit_window_height`, default on) that turns it off. That tab is built with `grid` only, per the Settings rule in the development guide.

**Collapsible sections**

- `panelkit.collapsible_section` gives the collapsible panel sections (POI Reference, Codex Completionist, Organic Scanning, Expedition and others) a clickable ▸/▾ title over a body frame.
- Every section starts folded each time EDMC starts: opening one lasts for the session and is not remembered, so the panel is the same height every launch (no collapsed state is stored).
- Boxel Survey keeps its own equivalent, which also starts folded.

**Modes.** `PANEL_MODES` in `ui.py` is the ordered list of mode buttons. Each mode has its own frame.
Switching modes shows one frame and hides the others (`grid_remove`), so it never destroys or
rebuilds widgets. Hidden modes keep receiving journal events (section 3), which is why nothing
pauses when a mode isn't on screen.

## 5. Keeping the main window from growing

**The problem.** EDMC sizes its main window to the widest row among *all* loaded plugins. One plugin
that lets external content set a widget's width widens the window for the whole app, including every
other plugin's panel. For example, a thumbnail capped by height only lets an ultrawide screenshot
produce a very wide image.

**The rule.** Any widget in the main window whose size comes from variable data must have a hard
upper bound on *every* dimension that affects layout.

**Session strip.** Directly under the mode buttons (a frame at row 2 of the main frame, with a separator at
row 3) are the lines shown in every mode: the plugin version, the game mode, credits, merits (once there is one, and not on the Powerplay page, which shows the session's merits itself), the Overlays shown line, and a catch-up line while one is running. Nothing else hides them. The game mode and credits lines are each a feature
module of its own, independent of Powerplay and of each other (the others are `session_merits.py`, `overlay_visibility.py` and `catchup_status.py`):

- `game_mode.py`: "You are in Solo mode." (Open / Solo / Private Group with its name). Set from `LoadGame`'s
  `GameMode`/`Group`, recovered on `StartUp` (EDMC attached to a running game, no journal replay) by reading
  the `LoadGame` line from the top of the current journal file, cleared on `Shutdown`.
- `session_credits.py`: "Credits this session: +N cr earned (+R cr/hr)" or "-N cr lost".
  - It keeps its own record of the current session (login balance, balance now, journal file, commander) in `session_credits.json`, read from `LoadGame`'s `Credits` and EDMC's `state["Credits"]` on every event.
  - The same journal file and commander is one session (a logout to the menu and back, or an EDMC restart, continues it); anything else starts a new one.
  - Writes are throttled to one per 30 s plus start and stop.

Registration and tests:

- Both are registered in `load.py`'s `_FEATURES` for journal events (and `session_credits` in start/stop) and built into the strip by `ui.py`.
- Text builders and session logic are pure functions with tests (`tests/test_game_mode.py`, `tests/test_session_credits.py`).
- The labels are `panelkit.wrap_label`s, so a long number or private-group name wraps instead of widening EDMC's window.
- `session_credits.json` is on the updater's keep-list.
- Powerplay knows about neither: its session store has no credit fields.

**Switching modes must not change the width**

- Every mode's content sits in one holder in `ui.py` whose width is pinned to the mode-button row's, and whose height follows whichever mode is showing, so the window never grows or shrinks as you switch.
- Content wraps to that width instead of asking for more.

Two traps to remember:

- A bare `tk.Canvas` asks for 10 cm (about 378 px) of width, so scrolling panels (Mining, Missions) set `width=1` and stretch instead.
- The panel's feature frames put spare space in their second column, so a panel with a scrollbar column must give that column weight 0.

`tests/test_panel_width.py` guards both.

How that plays out:

- **Text from the game or journal** (station names, system names, faction names) is unbounded. Use `panelkit.wrap_label`.
  - It creates a label whose `wraplength` tracks the room left of it in its container (the frame's width less where the label starts, `panelkit.available_wrap`) but never drops below its `min_wrap` (`MIN_WRAP`, 300 px, unless the caller passes less).
  - A label beside a button is therefore given only the rest of the row (the narrower of its position and the widths of its row neighbors, `panelkit.row_room`).
  - A label that has not been shown yet is re-wrapped when it is mapped.
  - When the panel widens by 40 px or more, `panelkit._note_growth` writes the widest widgets to EDMC's log.
  - A long name wraps instead of stretching the window. The top-level frame's `<Configure>` event calls `panelkit.on_frame_configure` to update all of them.
  - A section that must not be the widest row in a narrow window (Expedition, Expedition Log, Materials, Nearest place to land, Notes, the Trade watch list) passes `min_wrap=200`: it wraps at 200 px in a narrow window and at the full width of a wide one, so a long name is shown in full instead of being cut short.
- **Character limits are safety caps, not the way text is fitted.** A name is shortened with an
  ellipsis only past a generous cap (64 characters for a station, system or site name, 40 for a
  commodity or material), so the wrapping label, not a short clip, decides how much shows.
- **Images** are resized into a fixed box, on both axes, before display.
  - `screenshots.py` defines explicit max width and height constants for the inline thumbnail (a genuine two-dimensional box), the history thumbnails and the preview popup, and hands them to `screenshot_convert.thumbnail_photo_data`.
  - Bounding only one axis and letting the other follow the source's aspect ratio is exactly the failure this rule exists to prevent.
- **Entry boxes and button rows** depend on the font. An Entry's `width` counts characters, so the same 26 asks for about 190 px in one font and 266 px in another, and a row of buttons gets wider with a wide font.
  - `panelkit.fit_entry(entry, max_px)` lowers the character count until the box asks for no more than the cap.
  - `panelkit.fit_button_row(buttons, max_px)` lowers the buttons' inner padding and then the font (never below 7 pt) until the row fits.
  - The Notes and Surface Compass quick-add rows use both, capped at 190 px.
  - `panelkit.flow_buttons(container, buttons)` wraps a row of buttons onto a second line when the next one would pass the width EDMC's window is already held at (the mode-button row, set once by `panelkit.set_row_cap`; the pure `flow_positions` decides where). The Mining button bar, Region Sweep's Discover row and the Waypoints list row use it, so full-length labels cannot widen the window.
- **Trade pages** measure their number columns with the real font; when the figures would leave the title column under 110 px (a wide font)
  the cells drop to the small font, and the title column never goes under 60 px (the title wraps instead of widening the window).
- **Windows with tables** (the Trade History window) size their minimum width from the widest table (`_fit_width`), capped at the screen
  width less 40 px, so a wide font does not clip the figures.
- **Overlay-drawn or canvas content** uses fixed sizes decided in code, never derived from data (for
  example the Rhino coverage minimap is a fixed square).

Ask of every new widget: *what is the worst-case size of this content, and where is the cap?*

### External windows (`plugin/uikit/`)

Every external (Toplevel) window uses WFMT's own navy look rather than EDMC's theme (gold titles, cyan section labels and table headings, a bright footer message (yellow, or cyan on Amber), green for success); main-window
panels still follow EDMC. See `docs/WINDOW_FRAMEWORK_SPEC.md`. The rules that matter when touching
one:

- **Never change ttk globally.** ttk themes and stock styles (`TButton`, `Treeview`, ...) are application-wide, so `theme_use()` or restyling them would recolor EDMC's main window and every other plugin.
  - The kit uses classic tk widgets plus its own `FlatButton`, `Combobox`, `SlimScrollbar`, `Tabs`, `ProgressBar` and `DataTable` (a Label grid, not a Treeview).
  - `tests/test_ui_kit.py` fails if `plugin/uikit` touches the ttk theme or styles.
- **Themes.** `uikit/palette.py` holds the colors as module attributes (`P.BG`, `P.TEXT`, ...) and four themes in `THEMES`: Navy (the default) and Cyan, Amber and Green, built by `_from_variables` from EDDDT's `mfd.css` colors (its own color becomes `ACCENT`; `TITLE` is its amber). `palette.apply(name)` sets the attributes and returns {old color: new color}. `style.set_theme` applies it, re-skins and recolors every window `skin()` has seen (`_recolor`: color options, canvas items, text tags, and the color strings a kit widget keeps), and calls the theme listeners (`DataTable` remaps its tag colors). The theme is saved as `wfmt_window_theme` by `ui.restore_text_size`. Read palette colors when a widget is built, never at import time or as a default argument (use `None` and `x or P.TOKEN`); a table that maps a role to a color stores the token name and calls `getattr(P, name)` when it draws.
- **Text size.** `uikit/style.py` keeps one setting (`set_text_delta`, -2 to +6 points, saved as `wfmt_window_text_delta` by `ui.restore_text_size`). `style.font` resizes its cached fonts in place (`scaled=False` gives a font that ignores the setting: the stat tiles and the status chips use it), `skin()` gives plain widgets the same body font, and `DataTable` listens (`add_text_listener`) to measure its columns again. The A- and A+ labels sit in the shells' footers (`_make_text_size_buttons`).
- **Table columns.** `DataTable._sync_widths` sizes a column that does not stretch to its content (the declared width is only the least an empty table gives it) and shares spare width in proportion to that.
- **Shell.** `uikit.shell.WindowShell` gives a Toplevel a header (title, subtitle, action buttons), a body, a wrapping status footer, a minimum size and saved geometry. `uikit/placement.py` chooses its position: the saved one while it is still on a connected monitor, otherwise centered over EDMC's window (`root._root()`) inside the monitor EDMC is on, or always there with `wfmt_windows_always_on_edmc_monitor`. `place` is pure; the monitors come from `EnumDisplayMonitors` on Windows (work areas) and the Tk virtual screen elsewhere, and a minimized EDMC changes nothing.
  - It never touches EDMC config: the window passes `load_geometry`/`save_geometry` callables.
  - Windows are built hidden and shown once, after their content is laid out (`_present`), so they never flash at a default size.
  - Windows keep the module-level `show`/`refresh`/`close` singleton convention.
- **Skinning.** `uikit.style.skin(window)` colors the classic widgets created inside a Toplevel via
  Tk's option database, scoped by the window's own *name* (option patterns match names, not full
  paths). Call it right after creating the Toplevel, before adding widgets. Explicit `fg=`/`bg=`
  still win, which is how status colors work. Don't also call `theme.update()` on these windows.
- **Tables.** `DataTable` mirrors the small part of Treeview the windows used (`insert`, `append`,
  `set`, `exists`, `clear`, `selection`, double-click) and adds sorting, `group=True` collapsible
  headings, and `visible_rows` (fit to content up to N rows). A bare `tk.Canvas` requests 7 cm of
  height, which silently props up whatever contains it: give canvases an explicit height.
- **Display scaling.** Default and minimum window sizes are written in 96-dpi pixels and multiplied
  by `uikit.style.dpi_factor` inside `WindowShell`; keep new layouts expressed that way.
- **Width discipline.** Displayed text goes through `uikit.widgets.clip` / per-column `max_chars`. A `DataTable` column marked `stretch` is instead clipped to the width it gets (with an ellipsis, up to 300 characters), so its text never widens the table.

## 6. Pure logic versus UI

Most features split into layers:

```
xxx.py / xxx_tracker.py    pure logic, no Tk, no network        -> unit-testable
xxx_state.py               JSON load/save
xxx_client.py              network calls, no Tk
xxx_panel.py               Tk widgets, wiring
xxx_window.py / _dialog.py popups
```

Examples: `bgs_tracker.py` (pure parsing and tallying) versus `bgs_panel.py` (widgets and polling);
`organic_scan.py` versus `organic_scan_panel.py`; `boxel.py` and `boxel_walker.py` versus
`boxel_survey.py`.

**Why.** Tk code can't run in a plain test, and EDMC-only imports (`config`, `theme`, `myNotebook`)
don't exist outside EDMC. Keeping logic free of both means it can be tested with `unittest` without
launching anything, and bugs in rules (name parsing, merit math, species matching) get caught by a
test run rather than by playing.

Where a logic module needs only EDMC's `appname` for a logger, it uses a fallback so tests can import
it:

```python
try:
    from config import appname
except ImportError:
    appname = "EDMarketConnector"
```

## 7. Threading and network calls

**Rule: Tkinter is not thread-safe.** Only the main thread may touch widgets. Slow work (HTTP) must
not run on the main thread either, or EDMC freezes while waiting. So network features use one
pattern (see `canonn_poi_panel.py`, `boxel_survey.py`, `bgs_panel.py`):

1. A button click bumps a **generation counter**, then starts a daemon `threading.Thread`.
2. The worker does the network call and puts `(generation, result)` onto a `queue.Queue`.
3. The main thread polls the queue with `widget.after(200, ...)`.
4. On each result, the poller compares its generation to the current one and **drops stale results**.

**Why a generation counter?** If a user clicks Find twice, or changes commander or system while a
lookup is in flight, the first lookup's result would arrive later and overwrite the newer state. The
counter makes "latest request wins" cheap and correct. Each new request invalidates all earlier ones.

**Why `after()` polling instead of calling back from the worker?** A callback from the worker thread
would run *on* the worker thread, and touching Tk from there can crash or corrupt the UI. The queue
hands data across the thread boundary safely; `after()` runs the consumer on the main thread.

The updater follows the same rule: it works in a thread, then calls back with a plain version string,
and `load.py` schedules the UI change with `frame.after(0, ...)`.

Trade mode (`trade_panel.py`) uses two simpler variants of the same rule, because each has exactly one consumer.

- A lookup is a `_Job`: a daemon thread that fills in `result`/`error` and sets `done`, which an `after(500)` poller on the Tk thread reads.
  - Only one job runs at a time.
  - **Cancel** sets a `threading.Event` the worker checks while it waits.
- The startup journal read for carrier cargo puts one result on a `queue.Queue` that the Tk thread merges.
- Neither touches a widget from the worker.
- There is no generation counter because a second request can't start while one is running. If a feature can have several requests in flight, use the generation counter above instead.

## 8. Persistence

### Two kinds of storage

- **EDMC's `config`** (EDMC's own settings store) holds small settings and toggles: booleans, ints, strings.
  - Every key is prefixed `wfmt_<feature>_...`, which avoids collisions with EDMC and other plugins and lets one look-up show everything WFMT owns.
  - A key is read under its current name only.
  - The few defensive readers (a one-time overlay reset, the placement keys of a slot, the Surface Compass's copy of the Mining waypoint's settings) are described where they apply.
- **JSON files in the plugin folder** hold real data: sessions, hotspot catalog, survey log, BGS tallies, visited systems, ship builds.
  - Examples: `sessions.json`, `boxel_state.json`, `region_sweep_state.json`, `waypoint_route_state.json`, `visited_systems.json`, `survey_log.json`, `organic_scan_state.json`, `system_surveys.json`, `system_history.json`, `codex_completionist_state.json`, `bgs_state.json`, `powerplay_state.json`, `mining_hotspots.json`, `mining_ring_notes.json`, `mining_coverage.json`, `mining_body_cache.json`, `ship_builds.json`, `stored_modules.json`, `colonization_sites.json`, `colonization_carrier.json`, `colonization_history.json`, `notes.json`, `materials.json`, `blueprint_wishlist.json`, `route_planner_route.json`, `carrier_route.json`, `mission_pins.json`, `engineers.json`, `trade_watch.json`, `surface_marks.json`, `expeditions.json`, `trade_ledger.json`, `trade_carrier.json`, `trade_stock.json`, `trade_history.json`, `trade_journal_scan.json`, `trade_route_start.json`, `overlay_settings.json`, `boxel_survey_export.csv`, `exo_observations.json`, `expedition_log.json`, `income_ledger.json`, `session_credits.json`, `mining_history.json`, `codex_catalog.json`, `rcc_keys.json`, `discord_webhooks.json`, `discord_templates.json`. The full set is `_OWN_DATA_FILES` in `update.py`, which every update, backup and restore protects.
  - `exo_observations.json` is the one data file that is global rather than per commander (facts about bodies and the species found there, pooled to check the prediction; no commander name is stored).
  - `codex_catalog.json` is a cache of a downloaded list rather than commander data, but it is protected from updates the same way.

**Overlay settings are the exception to "settings live in `config`": they are per commander.**

- Per commander: which overlay cards run, their options, every display's placement and Show tick, the screen scaling and mode, and the look (scheme, text size, opacity, font, corners, keep-showing). Two commanders on one install do not share them.
- Shared on purpose, all facts about the machine: the overlay's connection (which overlay draws, host and port), the shortcut keys and the layout picture's size.
- The overlay modules still read EDMC's `config` directly. `overlay_profile.py` keeps the *active commander's* choices there and files every commander's in `overlay_settings.json` (the `commander_data.py` shape).
- `activate(cmdr)` runs at the top of `journal_entry` (and when the last commander is restored at start-up).
  - It files the outgoing commander's choices, then loads the incoming commander's into the config.
  - For a commander seen for the first time, it files a copy of what the config holds, so nothing changes on screen.
- `save_current` runs when Settings are saved and when EDMC closes.
- A key a commander never saved is deleted from the config on a switch, so it falls back to its default instead of showing the last commander's choice.
- Choices saved with no commander known yet go to the first commander seen.
- The keys swapped are `overlay_profile._FIXED` plus the per-display keys `overlay_placement` registers.
- `tests/test_overlay_profile.py` fails on any new `wfmt_*enabled*`/`*overlay*` key not classified as swapped or as shared on purpose.
- A switch calls `overlay_placement.refresh` and re-sends the group offsets.
- A module that caches an overlay setting at start-up keeps its value until restart (none is known to).

**Why files instead of `config`?** `config` is for settings, not structured or growing data. JSON
files are inspectable, easy to back up and easy to hand-repair. The tradeoff is that data lives beside
the code, so deleting the plugin folder deletes it. Section 13 covers how updates avoid that.

### Per-commander keys

**Nothing about a commander's play is shared between commanders.**

- Data that belongs to a commander is stored as `{ "<commander>": {...} }` in one file.
- The commander name is matched case-insensitively (`casefold`).
- **Why:** players have several commanders, and their surveys, tallies, hotspots and sessions must not mix. Matching case-insensitively avoids a duplicate entry if the journal reports the same name with different casing.

`commander_data.py` is the shared helper for new files.

- The shape is `{"version": 2, "commanders": {key: {"name", "data"}}, "legacy": ..., "meta": ...}`.
- The key is the trimmed, case-folded name and is **only ever a JSON key, never part of a file name**, so nothing depends on the Windows/Linux differences in case rules and forbidden characters.
- A defensive reader handles a data file in the pre-per-commander shape, if one is found: its content lands in `legacy`.
  - The first commander seen claims it (hotspots, coverage, survey log).
  - Where it mixes several commanders and can't be split (the Codex tally), it is kept untouched while each commander is rebuilt from their own journals, and the untouched copy is removed after 60 days (`OLD_TALLY_KEEP_DAYS`).
- Some per-commander files (`boxel_state.py`, `region_sweep_state.py`, `waypoint_route_state.py`, `bgs_state.py`, …) use their own equivalent layout instead of the helper.
- When the active commander changes, a feature must also reset anything it kept in memory about the previous one (Trade does this in `_reset_for_commander`; Exploration Value forgets the last data sales).

`tests/test_data_files_per_commander.py` lists every protected data file and how it keeps commanders apart (or why it
holds none), and fails for a new, unclassified one; `tests/test_per_commander_data.py` saves for one commander and loads
for another for each of the converted stores.

Trade's carrier records and per-commander carrier choice take this a step further:

- They are keyed by the *casefolded* name (`trade_carrier.key_for`), because a journal can write `EXAMPLECMDR` where EDMC supplies `Examplecmdr`.
- The list of commanders seen is kept in one config key (`wfmt_trade_commanders`) so the Settings tab can offer a choice for each, since Settings can't ask the game who your commanders are.

### Atomic writes

- State is written to `path.tmp`, then `os.replace(tmp, path)`.
- **Why:** if EDMC is killed or the machine loses power mid-write, a plain overwrite can leave a truncated, unparseable file. `os.replace` is atomic on the same volume, so the file is always either the old version or the new one.
- Loads treat an unreadable or wrong-shaped file as "nothing saved" and log a warning instead of crashing at startup.

### Bounded growth

- Data that would otherwise grow forever is capped (for example `sessions.json` keeps each commander's most recent 200 sessions).
- Derived numbers aren't stored when they can be recomputed. Powerplay stores raw merits per activity and computes Control Points at display time from the current ratio settings, so correcting a ratio retroactively fixes old sessions' estimates.

## 9. Journal, Status.json and CAPI

Three different data sources reach WFMT through three different hooks. They are the "first layer" of the design principle at the top of this guide: the journal is the only source that carries your play, so what it leaves out has to be filled in or worked around elsewhere (sections 11 and 17).

- **Journal events** (`journal_entry`): discrete things the game logs, such as `FSDJump`, `Scan`,
  `Docked`, `MissionCompleted`. Most features run on these.
- **Status.json** (`dashboard_entry`): a live snapshot the game rewrites about once a second. It is
  the only place to get continuous position (latitude and longitude, used for Mining's surface bearing
  and coverage map) and the flags bitmask (used for the earliest interdiction signal). Position and
  flags are not journal events, so features that need them can't be driven by the journal alone.
- **CAPI** (`capi_fleetcarrier`): Frontier's authenticated web API, delivered by EDMC on a throttle.
  Used for the fleet carrier's locker (Inventory) and its cargo hold (Colonization's carrier tally, which it replaces with the carrier's real cargo when that is safe; see the fleet carrier column below).

### Saved-name migration (`legacy_names.py`)

When British spellings were replaced with American ones, some saved names changed. `legacy_names.migrate` moves what users already have.

- It runs in `plugin_start3`, after a pending restore, because an old backup brings the old names back.
- It renames the three data files from their old names (`colonisation_sites.json`, `colonisation_history.json`, `colonisation_carrier.json`).
  - If both names exist, the file saved more recently wins.
- It renames the `wfmt_colonisation_*` settings, the Colonization overlay slot keys, the saved mode key and the hidden-mode flag.
  - A setting already saved under the new key is never overwritten.
- It renames the saved field names from their old names, `tonnes` and `analysed`, to `tons` and `analyzed` in every saved JSON file that has one.
  - Only a whole word in a key is renamed (the key's start or end, or between underscores: `cargo_tonnes` becomes `cargo_tons`), so a key that merely holds the letters, such as a body named after a place, is left alone (the old spelling is matched only as a word). Every old word in a key is renamed.
  - A rewrite that fails removes its temporary file.
- It reads a file's bytes first and rewrites only a file that holds an old name, so later start-ups only read.
- `data_backup.data_file_names` also lists the old file names, so an old backup still restores.

The game's own names are not renamed. The journal's `ColonisationContribution` and similar events, the `ColonisationShip` station type and the `Mission_Colonisation...` names keep the game's spelling, and the code that matches them accepts both.

### Catching up on state EDMC missed

Two situations mean a feature can start with an incomplete picture:

- **EDMC starts while the game is already running.** EDMC synthesizes a `StartUp` event. Features that need current state (current system, region, active mining run) handle it by reading the current journal file backward for the last `FSDJump` or `Location`.
- **EDMC starts and the game is not running.** No event arrives, so no feature would know the commander until the next login.
  - About four seconds after the panel is built, if no live event has arrived, `load.py` calls `restore.dispatch`.
  - The commander is read from the newest journal (`restore.latest_commander`, falling back to EDMC's own value) and every feature gets one neutral `WFMTRestoreCommander` event with that `cmdr`.
  - It is not `StartUp` or `LoadGame`, which mean a game is running (Game Mode, Powerplay and Credits would act on that). Features treat it as any unknown event and only learn the commander and load that commander's saved data.
  - A real login later behaves as before, for the same or another commander.
  - A feature that fails is logged and the rest still get it.
- **The player relogs.** A relog creates a new journal file that does *not* replay earlier `FSSBodySignals`, `Scan` or `ScanOrganic` events. So Organic Scanning persists per-body state to disk (`organic_scan_state.json`) rather than relying on the journal to re-tell it.
- **A job that spans play sessions.** Trade's working session belongs to a commander and lasts until Reset, across logins, journal files and EDMC runs.
  - When EDMC next sees the commander it catches the session up from the journal files written since the last event it counted (`trade_ledger.catch_up`), through the same code the live events use, and only adds.
  - Every event is idempotent (`already_counted`, by time and fingerprint), so replays and live repeats can't double count.
- **A baseline event that is only written on request.** `CarrierStats` (the fleet or squadron carrier's cargo space) is written only when the Carrier Management screen is opened, and EDMC does not replay it when it starts.
  - Trade mode therefore replays the newest 40 journal files on a background thread at startup, parsing only the few event names it needs, to find the last baseline and the transfers after it (about 0.03 s on a real journal folder).
  - See the [Trade spec](TRADE_TECH_SPEC.md#7-fleet-and-squadron-carrier-cargo-space).

**Features whose picture is rebuilt from recent journals at start-up**, each with its own rule for never counting an event twice (`journal_files.py` is the shared file finding and reading):

- Missions (`journal_scan.py`, two weeks): accepted missions, kills (`Bounty` and `FactionKillBond`), redirects, Community Goals and `CargoDepot` progress.
  - The *active* set is normally the login `Missions` event, which EDMC never replays, so it is also derived from the journals.
  - It is the newest `Missions` list, plus each `MissionAccepted` after it, less each `MissionCompleted`, `MissionAbandoned` and `MissionFailed`.
  - The next real login list replaces it.
- Colonization (`colonization_catchup.py`, 14 to 30 days): depot snapshots (idempotent) and contributions (additions).
  - Each site carries `journal_at` and only a newer event is applied; a site saved before that existed uses its `updated` time.
  - The live path uses the same guard.
- Colonization fleet carrier transfers (`colonization_carrier.py`, same 14 to 30 day window, oldest watermark): a `CargoTransfer` made while docked at a `FleetCarrier` station adds or removes tons for that commodity (floor zero).
  - Transfers are additions, so each commander's record keeps `journal_at` and only a newer transfer is applied; the live path uses the same guard.
  - Market purchases, sales, trade orders and other players' moves are not transfers, so the figure is what was seen transferred, not the carrier's hold.
- Codex Completionist (`scan_since`): the active commander's tally only.
  - It reads the files written since its `last_event_at` watermark, counting each newer `CodexEntry` once (a file says whose events follow).
  - A brand-new install only sets the watermark.
  - A commander first seen after the tally became per commander is rebuilt once from all their journals.
- Boxel Survey's visited systems (`visited_systems.arrivals_since`, 14 days): a set union, so no watermark.
- Trade's route start (`trade_route_start.py`), with the time of each dock so a late-read older file cannot win.
- Inventory has no journal pass: on `StartUp` it syncs from EDMC's own state, which EDMC rebuilds from the journal.
- Exploration Value replays the current journal file for the system's scan progress and the last data sales.

Some things are deliberately *not* automatic:

- Codex Completionist's full backfill ("Backfill Journals" in the My Codex window) is a button because reading years of journal files is real I/O; it does no work until asked.
- Boxel Survey's survey log is not caught up either: its `bodies_scanned` counter is not idempotent, so a replay would double-count.

### Reading journals defensively

Fields the game documents poorly are handled conservatively.

- Interdiction Warning combines three signals: the Status.json flag, NPC `ReceiveText` taunts restricted to `Channel == "npc"`, and the authoritative `Interdicted`/`EscapeInterdiction` events.
- It needs all three because they arrive via independent callbacks with no ordering guarantee.
- The channel gate exists because squadron and system chat are other commanders casually typing words like "pirate" with no interdiction happening.

**Surface Compass** (`surface_compass.py`, `surface_marks.py`, `surface_marks_window.py`)

- It takes the live position (`Latitude`, `Longitude`, `Heading`, `PlanetRadius`, `BodyName`, `Flags` bit 21 `HasLatLong`) from `Status.json` through EDMC's `dashboard_entry`, in `load.py` after Mining has refreshed `mining_live_position` from the same entry.
- It works out great-circle distance and initial bearing with `mining_bearing.py` on a sphere of the body's radius (the body's `Scan` radius when `Status.json` has none).
- The target is the book's choice: `auto` (the nearest recorded hotspot with a position for the journal's current system and body), `none`, or a mark's id.
  - A mark is pointed at only when its body name, trimmed and case-folded, matches the body the commander is on.
- Marks and the choice are per commander in `surface_marks.json` (`commander_data.py`; 500 marks, names 60 characters, body names 100).
- The overlay card (an arrow vector, a backing panel and one line of text, group `wfmt_compass`, placement slot `surface_compass`) is drawn on every `Status.json` update while enabled and cleared once when there is no reading.
- A defensive reader (`migrate_old_waypoint_settings`, recorded by `wfmt_compass_migrated_v1`) copies the settings of a Mining waypoint overlay (enabled flag, placement, hidden flag), if it finds them, to the compass's own keys, once.
- The panel row's summary label wraps at 200 px and the quick-name box starts at 26 characters and is lowered until it asks for no more than 190 px (`panelkit.fit_entry`), so nothing the commander or the game supplies can widen EDMC's window.

**Materials and Engineering** (`materials.py`, `materials_panel.py`, `materials_window.py`, `blueprints*.py`, `engineers.py`, `material_traders.py`)

- They keep the commander's Raw, Manufactured and Encoded counts in `materials.json` (`MaterialBook`, per commander).
  - The login `Materials` list sets them, then each journal event that changes a count moves it, within the grade limits (300 to 100).
  - EDMC's own totals fill in a mid-session start.
- Static data:
  - The blueprint table (`blueprints_data.py`, trimmed from a public table and corrected; source and license: see docs/ATTRIBUTIONS.md and THIRD-PARTY-NOTICES.md).
  - Yi Shen's unlock (`blueprints_extra.py`).
  - The engineer location table (`engineers_data.py`, read through `engineers.info`, which also tells the region: Bubble or within 500 ly of Colonia; the Engineers tab's Show choice is kept in `wfmt_engineers_region`).
- Per commander: `blueprint_wishlist.py` (`blueprint_wishlist.json`) and `engineers.py` (`engineers.json`, from `EngineerProgress`).
- `blueprint_needs.py` works out what a blueprint or the wishlist needs against what is held (ship materials, and the Odyssey ship locker).
- The material trader finder is the only online part.
  - When **Find** is pressed it passes the system and the trader type to Spansh's station search on a worker thread, with a two-minute cache.
  - Nothing else is sent.

**Expedition planner** (`expedition.py`, `expedition_window.py`, `expedition_panel.py`)

- It keeps named expeditions of ordered stops in `expeditions.json` (`ExpeditionBook`, per commander), one active at a time.
- The panel feeds arrivals from the journal and ticks the stop whose system matches, counting jumps and distance.
- There are two online parts, both only on a button press.

Spelling and names:

- Adding or changing a stop respells it without a network call where it can (the system the commander is in, then any stop already spelled that way: `expedition_window._spelling`).
- While the box under the editor is ticked (`wfmt_expedition_lookup_names`, on unless turned off), it asks EDSM in the background for the names just added (`_look_up`, 50 to a request).
  - `ExpeditionBook.canonical_names` takes EDSM's spelling for stops whose names match ignoring case and spacing.
  - `set_coords` gives them a position.
- **Locate and reorder (EDSM)** sends system names to EDSM for their positions and orders the stops by nearest neighbor.

Spansh planners:

- **Road to Riches** and **Exomastery** (`spansh_planners.py`, `expedition_plan_dialog.py`) post the start system, the optional end and the chosen numbers to Spansh's `/api/riches/route` or `/api/exobiology/route`.
- They poll `/api/results/<job>` on a worker thread (the answer takes seconds to a couple of minutes), and turn the systems of the answer into a new expedition.
- Each stop is a system with its best body, a note of what the bodies are worth, and Spansh's position for it.
- The jump range offered is the last `Loadout`'s `MaxJumpRange`.
- The endpoints are undocumented; the request and result shapes were taken from Spansh's own page and a live answer (see the module's docstring).
- The **Neutron route** button opens the Route Planner window instead.

**System-name type-ahead**

- System-name boxes get type-ahead from `system_autocomplete.attach(entry, var)`.
  - It puts its own bindtag ahead of the box's so Enter, Up, Down and Escape are seen first (taken with "break" only when a suggestion is highlighted or the list is open), and the box's own Enter handling still runs otherwise.
- The list is a borderless Toplevel under the box, colored from the box itself so it fits both WFMT's dark windows and the themed EDMC panel.
- Suggestions are `system_names.local()` from two letters: the systems seen by `load.journal_entry`, then sources such as the expedition stops and notes registered with `add_source`.
- It adds Spansh's `/api/systems/field_values/system_names?q=` answers from three letters when `wfmt_system_suggest_spansh` is on (off by default).
  - The call is debounced 350 ms, runs on a worker thread, and is cached by typed start for the session.

**Missions card** (`missions_overlay.py`)

- It is a second small text card of the same kind: pure layout (`build_lines`, in the Missions specification section 10b) apart from drawing.
- One fixed width, lines clipped to `LINE_CHARS`, drawn through the shared overlay client at the "Missions list" placement slot (`overlay_placement.SLOTS`, group `wfmt_missions`, registered in `load.py` with the other groups).
- It follows the commander's system and `FSDTarget` from the journal and rereads the Missions mode's active missions on every change and every 30 s.
- Nothing is stored.

**Chemistry** (`chemistry.py`)

- It is the one place that writes a substance the short way (element symbols, formulas for the gases and compounds of an atmosphere and volcanism; `element`, `gas`, `shorten`, `label`).
- The style is saved under `wfmt_chemistry_style` (symbols by default).
- The Body info card is its only user; the other displays that name chemicals (Engineering, Materials) keep full names.

**Expedition Log** (`expedition_log.py` model, `expedition_log_panel.py` journal hook and the Log lines in the panel's Expedition section, `expedition_log_window.py` archive window, `expedition_log_overlay.py` card)

- It keeps per-commander `Run`s in `expedition_log.json` (`commander_data.py`).
- A `Tally` adds each journal event to the running expedition:
  - `FSDJump`/`CarrierJump`/`Location` for systems, jumps and light-years
  - `Scan` for bodies, first discoveries and the scan-value estimate
  - `SAAScanComplete` for mapping
  - the exploration and exobiology sale events for earned credits
  - `ScanOrganic` for samples and species
  - `CodexEntry`, `Touchdown`, and `Loadout` for ships
- Bodies are kept in per-run lists so a body is counted once.
- `rescan` replays the commander's own journals (each begins with their `LoadGame`) between the run's start and end through a fresh `Tally`, leaving out the events inside the run's `gaps`.
- **The clock and `gaps`.** `Run.elapsed` is the end (or now) minus the start minus `paused_for`.
  - A pause adds its length to `paused_for` when it ends (`_unpause`), and a stopped run that is resumed adds the time since it stopped (`_skip_stopped_time`), so the clock picks up from where it stopped.
  - Each of those also records a `[from, to]` pair in `Run.gaps` (at most `MAX_GAPS`, 50), saved with the run. The live `Tally` ignores events while a run is not running, so `rescan` skipping the same spans keeps a rescan equal to the live count.
  - A run saved before `gaps` existed has none, so its earlier pauses are still counted by a rescan. The first version saved the field as `stopped_gaps`; `run_from_raw` still reads that name.
- Rescanning runs on a worker thread and only reads files; the log is changed on the main thread.

**Exobiology cards** (`exobiology_overlay.py`, `exo_radar.py`)

- They read `organic_scan_panel.overlay_view()`, which builds an `organic_scan.BodyView` from the controller's per-body state without any widgets.
- The view holds:
  - each genus (`GenusView`) with its predicted candidates, the confirmed species and color variant (`ScanOrganic` `Variant_Localised`), its stage, the (latitude, longitude) of each Log/Sample taken (from `Status.json` at the time, persisted in `organic_scan_state.py`) and the commander's distance from the last one
  - the body's first-footfall flag (`Scan` `WasFootfalled`) and the biological signal count
  - the commander's position and heading
  - the ship (`Touchdown`/`Liftoff`) and SRV (`LaunchSRV`/`Disembark`/`DockSRV`/`Embark`) positions
- Four `_Display` objects (status, list, radar, popup) each have a `LiveCard`, a placement slot and a settings switch. `Status.json` changes and the relevant journal events refresh them.
- The Bio status card is one wide strip (`STATUS_CHARS`, 108 characters, `WideCardLayout`) that folds the distance line into the headline row when it fits.
- The radar (`exo_radar.build_plan`) turns the positions into pixels with a flat-earth offset rotated to the heading, and picks the scale so every circle fits (the overlay cannot clip).
- `RadarLayout` draws it with circle shapes (`OverlayClient.send_circle`).

**System targets and Body info cards** (`targets_overlay.py`, `body_info_overlay.py`)

- They read one shared model of the current system, `system_survey.py`, which `load.journal_entry` feeds first (it is ahead of both cards in `_FEATURES`).
- It starts a new survey on `FSDJump`, `CarrierJump` or a `Location` in a different system, and hides it on `StartJump` (hyperspace).
- It takes these events:
  - `FSSDiscoveryScan`, `FSSAllBodiesFound`
  - `Scan` (bodies with a `PlanetClass` or `StarType`; belt clusters and events from another system are skipped)
  - `FSSBodySignals` and `SAASignalsFound` (biological and geological counts, and the genera)
  - `SAAScanComplete` (mapped)
  - `ScanOrganic` (an `Analyse` marks a genus done; a body's life is done when its analyzed genera reach its biological signal count, which equals the number of genera in the real journals checked)
- On `StartUp` or the restore event it is rebuilt from the newest journal, from the last arrival.
- The value is `scan_value.py`'s estimate (the pure formula behind the Exploration Value readout).
- Body info picks the body from `Status.json`: `Destination.Body` (when `Destination.System` is this system) else `BodyName`.

Saving surveys between sessions (`system_survey_store.py`):

- Each commander's surveys are saved in `system_surveys.json` (one payload per commander through `commander_data.py`, the 60 most recently visited systems kept).
- After a change to the survey it is written after a short delay. On arrival in a system, or on restore, what was saved is merged back (`SurveyStore.merge_into`): bodies the live survey lacks are added, and for the ones it has the saved copy fills in what the live one does not know, with the live data winning.
- When a system has no saved bodies (`_has_saved_bodies`: a record holding only the honk counts as none) and the commander's journal history says they have been there or have scanned there, `rebuild_system` replays every visit to it from their journals.
  - The history test is `needs_backfill`: two visits or more, or `Visit.scanned`; EDMC starting in the system forces it.
  - It reads only their own journals (each journal begins with their `LoadGame`; at most 80 files) in a background thread, and `SurveyStore.absorb` adds the result to the saved record.
  - The merge into the live survey is applied on the main thread (`apply_pending`, from the journal and Status.json hooks) so the survey is never changed from two threads.
  - The rule looks at `scanned` because a system scanned while EDMC was closed has one visit (a relog into it is not another), so the visit count alone would call it new and the journals would not be read.

When the cards may show:

- The survey also carries `playing`, `docked` and `cmdr`.
- `Shutdown`, a new journal (`Fileheader` part 1) and `Music` `MainMenu` stop it.
- `LoadGame` or an arrival starts it, and a `LoadGame` for a different commander clears it.
- `Docked`/`Undocked` (or `Docked` on a `Location`/`CarrierJump`) hide it while docked.

Card drawing:

- A `CardLayout` builds a plan of every shape and text from the `Card` (title, badge, progress bar, header lines wrapped to the card width, rows with a muted tab column and right-aligned or column values, footer) before sending anything, so the height comes from what the card says.
- Both cards draw through `overlay_card.CardLayout` (a plain dark panel: no outline and no edge bar; the card is planned first, so its height comes from what it says) (the same layout as the Route card: a fixed top and width, every line at the left padding).
- They redraw through `LiveCard` when the card changes or every 3 seconds.
- They share no state with each other except the survey.

**Expedition survey tracking**

- `ExpeditionBook.on_survey` takes these from `expedition_panel.handle_event`: `FSSDiscoveryScan` (`BodyCount`), `FSSAllBodiesFound` (`Count`), `Scan` (`BodyName`, `WasDiscovered`) and `SAAScanComplete` (`BodyName`).
- It counts them against the most recently reached stop whose system matches the event's `StarSystem` or `SystemName` (or the system the commander is in, for events that carry none).
- Body names are stored per stop (`scanned`, `mapped`, `firsts`, at most `MAX_SURVEY_NAMES` each) so a repeat scan counts once; belt clusters are skipped.
- The Route overlay card shows the route only; an expedition's stops are not drawn on it.

**An expedition and its Expedition Log run are linked** (`expedition_link.py`):

- `Expedition.log_run_id` (written only when set) names the run, and `ExpeditionBook.set_log_run` sets it.
- One controller applies Start, Pause, Resume and Stop to both so they never disagree, in either direction (a Log Stop stops the linked expedition, a Log Resume of a stopped run reopens it).
- A linked expedition shows the run's elapsed time, which excludes paused time.
- An unlinked one (the setting `wfmt_expedition_start_log` off, or no Log commander) keeps wall-clock time and its Pause only changes status.
- The link is built in `expedition_panel` and takes the two books and the "start a run" function as arguments, so the module has no imports of either panel.

**Route overlay** (`route_overlay.py`, over the pure `route_plan.py`)

- It draws one overlay card (`navigation_card`): three header lines (`You are navigating to:`, the destination, the jump count), a rule, the names of the systems still to jump to (the next `rows` of them), a rule and the light years left.
- `status_lines` (fuel, range, jumps left, next supercharge) is kept for the Exploration Dashboard and is not on the card.
- The Route Planner's route, when it has a jump left, is used in place of the game's.
- The route is `NavRoute.json` in the journal folder, read when a `NavRoute` event arrives and on `LoadGame`, `StartUp` and the restore event; `NavRouteClear` empties it.
- Progress is the system the ship is in (`FSDJump`, `Location`, `CarrierJump`, or EDMC's own current system).
  - A route is shown only while the ship is in one of its systems (or its place is not known yet), so a diversion or a stale file shows nothing.
- Star kinds come from `StarClass` (`N` neutron, `D*` white dwarf, the rest by `fuel_alerts.is_scoopable`).
- Fuel comes from `fuel_alerts.FuelWatcher`, the range from `Loadout.MaxJumpRange`, the last jump's fuel from `FSDJump.FuelUsed`.
- The card has a fixed top and width, grows downward, and is redrawn when it changes or every 3 seconds, with a one-second tick while a route applies.
- Its group is `wfmt_route`.

**Flight Alerts** (`flight_alerts.py`, over the pure `carrier_jump_timer.py`, `fuel_alerts.py` and `mining_alerts.py`) draws one overlay card.

- Mining alerts come from `ProspectedAsteroid`'s `MotherlodeMaterial`, the `Cargo`/`Loadout` events and EDMC's cargo by name (`state["Cargo"]["drones"]`), and are described in docs/MINING_TECH_SPEC.md.
  - A core asteroid or a rock rich in the target commodity, for 30 seconds.
  - Low limpets and a nearly full hold while a mining event is under 30 minutes old.
- The carrier countdown comes from `CarrierJumpRequest` (`SystemName`, `Body`, `DepartureTime`, parsed as UTC), cleared by `CarrierJumpCancelled` or `CarrierJump`.
  - A request whose departure is already more than 90 s past is ignored (an old journal line).
  - One alert is given as the time left falls to 600, 300, 60 and 0 s (only the nearest when several are crossed at once).
  - On `LoadGame`, `StartUp` or WFMT's restore event the journals modified in the last 3 hours are read once for a request still in the future.
- Fuel comes from `Status.json` (`Fuel.FuelMain`, via EDMC's `dashboard_entry`), the tank size from `Loadout.FuelCapacity.Main`, and the plotted star from `FSDTarget.StarClass`.
  - Scoopable means exactly one of O, B, A, F, G, K, M, so `MS`, `AeBe` and the white-dwarf `D*` classes are not.
  - The flags `InMainShip` (1<<24), `Docked`, `Landed` and `ScoopingFuel` decide when a warning applies.
  - The journal gives no per-jump fuel cost, so the warnings are percentage thresholds.
- A one-second ticker thread runs only while a jump is planned.
- Each draw lasts 4 s on the overlay so a stalled WFMT cannot leave the card up, and an unchanged card is redrawn every 3 s.
- The card has one fixed width (30 characters at 1.6 times the overlay font estimate, 1.3 was seen cutting text off), wraps every message to it (at sentence ends, then spaces, at most 10 card lines) and grows downward.
  - So its top and right edge, which Overlay Placement anchors, never move with what it says.

## 10. The overlay

Overlay features (every card and alert) draw over the game window through one of two overlays, chosen by `wfmt_overlay_backend` (`overlay_native.py`, Settings → Overlays → Overlay Connection):

- **EDMCModernOverlay** (the default; Windows and Linux): a separate helper app that listens on a local TCP port. WFMT is only a client.
- **WFMT's built-in overlay** (Windows only, opt-in): a transparent window WFMT draws itself, described under "The built-in overlay" below.

Every feature draws through `overlay.OverlayClient` (`send_message`, `send_shape`, `send_circle`, `send_vector`) whichever overlay is chosen: `OverlayClient._send_raw` hands the payload to the built-in overlay's scene when it is
chosen and to the socket otherwise, so no feature knows the difference.

**Every overlay switch defaults to off.**

- A one-time reset, `load._reset_overlays_once`, sets every switch in `_OVERLAY_ENABLE_KEYS` to off, recorded by the `wfmt_overlay_reset_v2` config key, before any feature reads its settings.
  - It runs after `overlay_profile.profiles.configure` and clears the switches in every commander's saved choices (`OverlayProfiles.switch_off`) as well as in the config, so no commander keeps an overlay on.
  - Bump the marker's suffix to force the reset again.
- A new overlay switch must be added to `_OVERLAY_ENABLE_KEYS` and default to off.

**Protocol**

- Connect, send one JSON object plus a newline per graphic, for example `{"id": "x", "text": "hi", "color": "red", "x": 200, "y": 100, "ttl": 4}`.
- Nothing is read back; sends are fire-and-forget.
- WFMT's protocol notes come from observed behavior.

### One shared, persistent connection

`overlay.OverlayClient` holds a single connection open for the plugin's lifetime and reconnects
lazily if it drops.

**Why persistent?** The overlay server tags every graphic with the ID of the connection that sent it,
and *wipes all of a connection's graphics the moment it disconnects*, regardless of each graphic's
`ttl`. Connect-send-close would make everything vanish immediately. So the connection must stay open
as long as its graphics should be visible.

**When no overlay is running**

- After a failed connection the client fails new sends immediately for 30 seconds (`COOLOFF_S`) instead of trying again. A user with no overlay program therefore costs almost nothing: no thread waiting on a connection per pickup, screenshot or Mining update.
- The failure is logged once at INFO, and a changed host or port is applied straight away.
- The Settings test buttons build their own client, so they always try for real.
- The Overlay Connection tab (Settings → Overlays) has a **Check connection** button.

**Why one for everything?** A connection per mode would duplicate work, and each would need its own
reconnect logic.

Connect timeout is 1 second.

- It's a loopback connection to an app that is either running (instant) or not (fails fast).
- A long timeout would stall journal processing waiting for an app that isn't there.

### Placement (`overlay_layout.py`, `overlay_placement.py`, `overlay_grid.py`)

EDMCModernOverlay maps a fixed 1280 x 960 canvas onto the game window, and (measured on 3840 x 2160 at 125% display scaling,
fill mode, by drawing probe shapes and photographing the screen) it treats positions and sizes differently:

- A **position** is a fraction of the screen: x / 1280 across, y / 960 down. In fill mode the canvas is stretched over the
  whole window (non-uniformly when the window is not 4:3), so none of it is cut off. In fit mode it keeps its shape with
  bars.
- A **size** (a shape's w and h, and the offsets between the pieces of a registered display) is in logical screen
  pixels, that is device pixels over the operating system's display scaling. A 360-wide card is 360 / 3072 = 12% of the
  width, which is 150 canvas units, not 360.
- On the axis the overlay does not stretch (across, on a wide screen; both in fit mode) it clamps a shape's x + w to 1280,
  mixing a canvas position with a pixel width, and squashes whatever passes it. So a display must start at or before
  `1280 - its pixel width` there. (`Screen.clamped`)
- A **group offset** (`offsetX` of an overlay group) is added *after* that clamp, in canvas units, and is the overlay's own way to
  move a group (the Overlay Controller edits it). It is settable by a plugin through
  `overlay_plugin.overlay_api.define_plugin_group(plugin_group_offset_x=...)`, which merges per field into the overlay's
  groupings file. The anchor, by contrast, does not help on the clamped axis (the overlay pivots on cached bounds there).

Placement is therefore relative to the screen and aware of display size:

- **Model** (`overlay_layout.py`, pure):
  - `Screen` (window size, mode, display scaling), `units_per_px`, `block_units`.
  - `Placement` (a horizontal anchor, a vertical anchor and offsets in screen pixels, or an exact canvas x/y).
  - `block_origin` (where a display of a given pixel size goes; kept on the canvas and before the overlay's clamp).
  - `plan_origin` (the same, for a display whose group can be offset: where to draw it, which is as far right as the clamp allows for its largest size, and the group offset that carries it the rest of the way).
  - `ShiftedClient`.
- **Features keep their own layout.** Each draws at its fixed origin exactly as before and reports the rectangle it occupies (`block_rect()`: left and top on the canvas, width and height in pixels).
  - `overlay_placement.client_for(slot, client, block)` returns the client wrapped so every `send_message`, `send_shape` and `send_vector` is moved by the same canvas offset, which moves the whole display as a unit.
  - A feature that positions itself from an origin (Inventory) uses `origin_for(slot, size)` instead.
  - A slot with an overlay `group` (all but the two Mining ones, which share a group) also gets a group offset.
    - `overlay_placement.apply_group_offsets()` works the offsets out for every slot (from the slot's largest size, so an offset is one fixed number however wide the display's content is).
    - `overlay.set_group_offsets` sends the changed ones through the overlay's API, at start-up, when Settings is saved, when the screen is re-detected or changes, and (typed values, then the saved ones again) around the preview.
    - Clearing is by id, so a clear needs no matching shift.
  - `ShiftedClient` and `HiddenClient` move or clear circles (`send_circle`) as well as text, rectangles and vectors, so a card's circles stay with it.
  - A card that grows is placed from the size it is drawn at: `overlay_placement.client_for_measured(slot, client, block, look)` takes the card's real block (so a bottom or middle anchor sits on the real edge), notes its size for the group offset, and re-applies the offsets when it changes.
  - `overlay_grid.py` is the drag-and-drop layout editor on the Placement tab.
    - It is a to-scale canvas of the screen in logical pixels with a grid, and a draggable box per slot (sized by `slot_size`).
    - The pure conversions are `placement_from_rect` and `rect_from_placement`. In `placement_from_rect` the spot (`_spot`) is the edge a box is within `EDGE_SNAP` pixels of, else the third of the screen the box's center is in, the offset is inward from that edge or from the center line, and within `EDGE_SNAP` pixels it snaps to 0, otherwise to the grid.
    - It reads and writes the same row variables as the table.
    - The picture size is saved at once under `wfmt_overlay_editor_size`.
  - Placement is applied at the call sites (never inside a `render()`), so the render functions stay pure and testable.
  - A saved exact position that would leave the display off the canvas is ignored.
    - The test is `overlay_layout.on_canvas`: at least 40 x 20 canvas units must lie on it, so a leftover `x = 1280` fails.
    - `placement_for` returns the slot's default and logs a warning once per slot; the saved text is not changed.
- **The screen** (`overlay_placement.py`), in this order:
  1. The overlay's own log first (`parse_scaling_line`): the newest "Overlay scaling updated" line gives the real window, mode and display scaling = scale_x / base_scale. It is ignored if the game's `DisplaySettings.xml` is newer.
  2. Then `DisplaySettings.xml` (`platform_support.elite_graphics_dir`, which also finds it inside a Proton prefix) with Windows' scale factor (`shcore.GetScaleFactorForDevice`) and the mode from `EDMCModernOverlay/overlay_settings.json`.
  3. If that file cannot be read (a Flatpak EDMC without the Graphics folder permission, say), the window size comes from the overlay log's `(size=WxHpx scale_x=...)` line (`parse_window_size`, `read_overlay_window_size`), which the overlay writes at normal log level.
     - That line has no display scaling, so the scaling is the chosen one, else Windows', else 100%.
  4. With neither source the primary monitor's size is read from the operating system (`platform_support.primary_display_size`): on Windows `GetDeviceCaps` with `DESKTOPHORZRES` and `DESKTOPVERTRES`, which gives the hardware resolution even for a process that is not DPI aware (`GetSystemMetrics` would give a scaled size, 3072 x 1728 on a 3840 x 2160 screen at 125%); on Linux the primary output of `xrandr --current` (`parse_xrandr`), through `flatpak-spawn --host` from a Flatpak. A multi-monitor desktop is not summed: only the primary output counts.
  5. With that unreadable too, the screen is assumed to be 1920 x 1080.
  - It is cached for 30 seconds; the mode and the scaling can be overridden.
  - Without EDMCModernOverlay installed sizes are assumed to be canvas units (`pixel_sizes = False`) and nothing is rescaled.
- **Settings:** `wfmt_overlay_place_<slot>` holds `h,v,dx,dy` or `custom,x,y`; `wfmt_overlay_display_scaling` and
  `wfmt_overlay_scale_mode` hold the overrides. A slot with no saved value reads its `legacy_x`/`legacy_y` settings, if it has any, and keeps a
  hand-set position as an exact one (`layout.migrated_placement`).
- **Adding an overlay:** add a `Slot` to `SLOTS` (key, label, default spot, pixel size, legacy keys), wrap its client with
  `client_for`, and give its settings a tab in the Overlays group in `ui.py`. Register its ids as an EDMCModernOverlay Plugin
  Group so its pieces scale together.

### Appearance (`overlay_style.py`, `overlay_appearance.py`)

Every overlay draws with one `Look` (`overlay_appearance.current_look()`, read from `wfmt_overlay_scheme` and `wfmt_overlay_text_size`; padding and line spacing are fixed). A `Look` holds:

- A `Palette` of color roles (border, fill, title, header, text, muted, ok, warn, info, danger, three accents, four chart series).
- A text level (0 or 1 as offered, Default or Larger, which steps each display's text token along small / normal / large / huge and stops at the ends).
- Extra padding and line height.

**Sizing cards from estimates**

- Because the overlay cannot measure text for a plugin, the look carries estimates, `CHAR_PX` (character width per size) and `LINE_PX` (line height per size).
- Each display builds its card from them (`look.text_width`, `pad_x`, `pad_y`, `line_px`), so text at any size sits inside its border.
- `LEGACY` is the fixed geometry and colors used as the default argument of every pure layout function, so those functions can be tested without a look.
- Each display exposes `block_rect(..., look)` so placement sees the size the card really has, and `Placement`/`slot_size` scale a slot's nominal size by the look.
- `tests/overlay_look_smoke.py` draws every display at 144 looks (scheme x text size x padding x spacing) and checks every text lies inside its card and that `block_rect` equals what was drawn.

**Widths**

- `text_width` pads every estimate by `WIDTH_PAD` (10%), because the overlay's own font sizing differs from one screen to the next and a box a little too wide looks fine where text past its edge does not.
- `measured_width` is the stricter measure for the Discovery and Notable Bodies cards, whose text is capitals and catalog names.
  - It counts capitals, digits and wide letters (M, W) as wider and spaces and narrow marks as narrower, and is never less than `text_width`.
  - The Notable Bodies text limits (60, 56 and 70 characters) only guard against a runaway value; the card widens to fit.

**Text size and padding**

- The text size is a setting (`wfmt_overlay_text_size`: Default, Larger; it starts at Larger).
- There is no fourth step, Largest, because that is where text runs past its box.
- Interdiction keeps fixed red alert colors.
- `Look.size` never returns less than `MIN_SIZE` ("normal"), so the overlay's "small" is not used (a saved -1 clamps to Default).
- Every card pads its text by the same `CARD_PAD_X` / `CARD_PAD_Y` (plus the fixed extra), with no per-card minimum width.
- Every display draws its text left-justified at its card's padding (Discovery and Notable Bodies too).

### The built-in overlay (`overlay_native.py`, `overlay_scene.py`, `overlay_raster.py`, `overlay_window.py`)

Design and status are in [NATIVE_OVERLAY_SPEC.md](NATIVE_OVERLAY_SPEC.md). In short:

- **Scene** (`overlay_scene.py`, pure): the payloads the features send, kept by id with when each runs out (`ttl`).
  - A resend replaces.
  - A payload that draws nothing removes the id: empty text, a zero-size rectangle, a circle with no color, an empty vector, or just an id with a ttl of 0 (which is what clearing a line or circle sends).
  - Items are returned in drawing order, rectangles then circles and lines then text, each in the order its id first appeared, so text is always above a panel whatever order it was sent in.
- **Picture** (`overlay_raster.py`, Pillow, which EDMC ships): draws the scene on a transparent image the size of the game window. It follows EDMCModernOverlay's conventions, which the features were written for:
  - A *group* (the ids sharing a registered prefix, `overlay_native.set_groups`) is placed at the canvas position of its top left item (a 1280 x 960 canvas stretched over the window).
  - The distances inside the group are logical pixels times the display scaling.
  - A size (width, height, radius, font) is in logical pixels.
  - An item in no group is placed in canvas units.
- **Window** (`overlay_window.py`, ctypes and Win32): a thread inside EDMC owns a layered, topmost, click-through, no-activate window.
  - Every 50 ms it finds Elite's window (class `FrontierDevelopmentsAppWinClass`) and takes its client area and display scaling (`GetDpiForWindow`, the thread is per-monitor DPI aware).
  - It redraws when the scene or the geometry changed, and pushes the bitmap with `UpdateLayeredWindow` (per-pixel alpha).
  - It shows only while Elite is the foreground window, or Windows' own capture tool is (`CAPTURE_TOOLS`, by the program's file name), or the player ticked *Keep showing* (`wfmt_overlay_keep_showing`).
  - While shown it re-asserts `HWND_TOPMOST` every half second (Elite, when brought back, takes its place above other topmost windows).
  - A frame that fails is logged and skipped.
  - Because it is a thread of EDMC it ends with EDMC.
- **Rounded corners:** `OverlayClient.send_shape` adds a `radius` (logical pixels) to a rectangle at least 24 px wide and tall when the built-in overlay is chosen.
  - It comes from `overlay_native.panel_radius`, setting `wfmt_overlay_corners`: square 0, slight 6, rounded 10, very 16.
  - Thinner rectangles are dividers and bars and stay square.
  - The scene keeps the radius on the item and the raster draws a rounded rectangle, the radius held to half the panel.
  - EDMCModernOverlay is sent no extra key.
- **Placement** reads the window's real size and scaling (`overlay_native.screen()`, `Screen.native`: no right-hand clamp, no group offsets).
- **Fonts:** the font file is `overlay_native._font_path()`.
  - It is `wfmt_overlay_builtin_font` in WFMT's own `fonts` folder (`overlay_fonts.own_dir`; the bundled Source Sans 3 and anything the player adds, which an update does not remove), else the bundled font, else a system font.
  - The window re-reads it every two seconds so a change applies without a restart.
  - A text measurer (`overlay_style.set_text_measurer`, `overlay_native.measure`, Pillow's `getlength` at eight times the size) replaces the character-width estimates, so cards are sized from the real text (`Look.text_width`, `measured_width`, and `Look.extent` for right-aligned text).
- **Screenshots:** `overlay_native.snapshot(width, height)` draws the current scene at a screenshot's size.
  - `screenshot_convert.convert_to_png` lays it over the converted copy when `wfmt_screenshot_include_overlay` is on.

**EDMCModernOverlay's font** is separate: `overlay_fonts.py` edits `overlay_client/fonts/preferred_fonts.txt` in its folder (first entry that loads wins; the default is `Eurocaps.ttf`, capitals only), keeping a `.bak` once.

**Hiding every overlay** (`overlay.set_all_hidden`, `overlay_visibility.py`)

- `_send` records the last payload per id (`_last`, with the time) and, while hidden, sends nothing.
- Hiding sends a clear for every id drawn so far, and showing resends what had not run out with its remaining ttl.
- The keyboard shortcut and the `!wf overlays` chat command are in `shortcuts.py`; the panel line and the Settings button work everywhere.

**Duplicate EDMCModernOverlay windows** (`overlay_processes.py`): counts `overlay_client` processes (psutil, `/proc`, or PowerShell), treating a launcher and its child as one window, so Check connection and Copy diagnostics can warn.

### Plugin Groups (EDMCModernOverlay)

EDMCModernOverlay groups a feature's shapes and text so they scale and anchor as one unit.

- `overlay.register_modern_overlay_groups` takes `(group_name, id_prefix)` pairs, so each feature supplies its own without `overlay.py` naming any feature.
- Registration is best-effort: it silently does nothing if ModernOverlay isn't installed, and swallows errors, because a cosmetic nicety must never break startup.

**Why every card registers a group**

- Without a group, a card's background rectangle can render invisible under ModernOverlay, and registering one fixes it, so every card-style overlay registers one.
- The tempting rule "don't group a single rectangle behind narrower text" was tried and turned out to be wrong.
- The general point: when overlay rendering seems wrong, check ModernOverlay's own payload and debug log before assuming a rule is right, and don't turn one observation into a permanent blanket rule.

**Clearing a line or a circle**

- The way to remove one drawn item is a payload that is only its id and `ttl: 0` (`overlay.removal_payload`).
  - EDMCModernOverlay reads that as `legacy_clear` and drops the item, and the built-in scene drops the id.
- The obvious clears do not work there, which was checked against the installed overlay's own normalizer (`normalise_legacy_payload`):
  - A `vect` with no points, or one point and no marker or text, is discarded ("insufficient points": it needs two points, or one with a marker or text) and logs a warning each time, so the clear never arrives.
  - A one-point, marker-less vector is discarded as well, so it is no use as a clear either.
  - A circle sent with no color is given the color white, so a clear drew a dot where the circle was.
- Callers still write `send_vector(id, [], ...)` and `send_circle(id, "", "", ...)` to clear.
  - `OverlayClient` turns those into the removal, and sends it only when the item is on the screen (`_last` remembers what was drawn and not yet run out).
  - So a card may clear every slot it is not using on each draw at no cost.
- Text and rectangles are cleared with the same removal, not with empty text or a zero-size rectangle with a `ttl` of 1.
  - EDMCModernOverlay accepts those but keeps the replaced panel for a few seconds, so turning overlays off would show the text going first and the empty panel a few seconds later.
  - `OverlayClient._send` turns those forms (`overlay.is_clear_form`) into the same removal and sends it only for something that is on the screen.
  - Hiding (everything, or a group) sends the removal for what is on the screen too.
- `tests/test_overlay_clear.py` and `tests/test_overlay_hide.py` hold the rules.

**Showing again**

- Switching overlays back on puts back what was on the screen when they were switched off, and anything drawn since, each with its full `ttl` (`overlay._restore_payload`). Something that had already run out before the switch stays gone.
- Putting back only what still had time left on its `ttl` would leave a card missing until its feature next drew it, because a card's `ttl` is a few seconds.
- Features keep drawing into the remembered set while hidden, so what comes back is current.

**Retrying a draw (Landing)**

- `LandingController._render_overlay_async` keeps only the newest request and one worker thread sends it, so an event and the heartbeat cannot interleave sends.
- If a draw fails with `OSError` (the overlay can take a minute or more to start on Linux), the worker calls `OverlayClient.retry_now()` and tries again every 5 s for up to 180 s (`_RENDER_RETRY_EVERY_S`, `_RENDER_RETRY_FOR_S`), unless a newer request replaces it.
- A failed clear is not retried.

Overlay message IDs use `wfmt_<feature>_*` so a group's prefix matches exactly its own shapes.

## 11. External services

These are the "second layer" of the design principle at the top of this guide: community and Frontier-side data that adds to what the
journal cannot say. They never overrule the journal, and none is needed for the journal-driven core of a mode to work.

| Service | Used for | Trigger |
|---|---|---|
| EDSM | Nearby systems, "does EDSM know this system", bodies, ring reserves | Buttons; some opt-in automatic checks |
| Spansh | Mining price finder and Market research, hotspot and boxel lookups, expedition planners (Road to Riches, Exomastery), ELW rarity, rare-goods origin Power, nearest neutron star and white dwarf (the Neutron Star and White Dwarf buttons), Trade routes and best-price searches | Buttons; opt-in; the Rares window looks up on open |
| edastro.com (GEC) | Nearest exploration POI: the whole list (`/gec/json/all`, ~2 MB, 652 entries) is downloaded and the nearest worked out locally | Button only; kept in memory for 6 hours |
| Canonn sheets | Thargoid and Guardian site lists | Button; downloaded once per session |
| tick.infomancer.uk | BGS tick time | 60-second poll; can be turned off |
| GitHub Releases | Update check | Opt-in, once per EDMC run |

Design decisions that apply to all of them:

- **API endpoints only, never HTML.** Scraping is fragile and impolite. Every call goes to a documented API or a published data file.
- **Degrade to "no result", never crash.**
  - `edsm_client.py` says so in its docstring: any failure (offline, service down, unexpected shape) returns an empty result. A network feature failing must not break journal handling.
  - The BGS tick client is the deliberate exception: it *raises*, and the caller decides, because a fabricated or stale tick would corrupt the tally. It never returns a guessed value.
- **Identify WFMT in every request.** Every call sends a User-Agent naming WFMT, its version and the
  project's address (`http_identity.py`, for example `WFMT/1.3.3 (rare-goods; +https://github.com/...)`),
  so a service operator who sees the traffic can tell what it is and get in touch. EDSM returns HTTP 403
  to the default `python-requests` agent, so its client sends EDMC's own `config.user_agent` followed by
  WFMT's.
- **Respect documented limits.** EDSM's `cube-systems` caps edge length at 200 ly; WFMT uses 100 as a
  middle ground between catching a few procedural systems and keeping responses small.
- **Opt-in by default, and stated.** Anything that phones home on its own is off until enabled.
  The user guide lists which features make network calls.
- **Bundle no service data.** Live queries mean nothing goes stale in the release and no service's
  content is redistributed. The exceptions are static game facts (section 12).
- **Plain HTTP for the tick API.** That is the only address the service offers. It carries a public
  timestamp and nothing sensitive.

### Keeping API traffic low

WFMT is a small, volunteer-made tool that leans on services other volunteers run, so it is built to ask
for as little as it can. These are the measures that are in the code today.

**A shared courtesy layer for Spansh (`spansh_courtesy.py`).** Requests to Spansh go through one function that applies the same limits wherever they come from:

- At most 2 in flight (a semaphore).
- At least 0.25 s between the starts of two requests (a shared gate that sleeps outside its lock).
- Retries on 429, 502, 503 and 504: 3 retries, waits of 2, 6 and 15 s plus up to 25% jitter, or the `Retry-After` header, capped at 60 s.
- A timeout is retried for a GET only. A POST that timed out may have been accepted, and repeating it could start a second job, so a POST is retried only on an explicit busy answer.
- After 5 failed requests in a row (each already retried) a breaker refuses further requests for 300 s with `SpanshBusy`, whose message the callers show.
  - Any answer, including a 400, 404 or 422, counts as Spansh being up and resets the count.
- `cancel` (a `threading.Event`) ends a wait before a retry.
- The clock, sleep, jitter and opener are injectable (`tests/test_spansh_courtesy.py`).
- The counters (`requests`, `retries`, `refused`) are in **Copy diagnostics**.
- Every Spansh request uses it (`tests/test_spansh_through_courtesy.py` fails if a module names a Spansh API address and does not).
- `retries=0` skips the retry waits for a caller answering a keystroke (the system-name suggestions); the breaker and the spacing still apply.
- `stream_to_file` is the same gate, concurrency cap, breaker and GET retry rules for a download too large to hold in memory.
  - It writes to a file, and resumes a dropped stream with a Range request (restarting from the start if the server ignores Range).
  - It returns "not modified" on a 304, refuses past a byte cap, and never counts a local disk error against Spansh.
- `docs/SPANSH_USAGE.md` is the public record of every Spansh endpoint WFMT calls, and it has to change whenever a request is added, removed or changed.

**The optional local neutron-star index (`star_index*.py`)**

The download and the file:

- A user-started download of Spansh's `systems_neutron.json.gz` (one gzip of one JSON array, one system per line, about 173 MiB).
  - It also lists some black holes and B/O stars, which the builder drops by keeping only `mainStar == "Neutron Star"`.
- It is built into `star_index/neutron.wfsi` in the plugin folder, then the dump is deleted.
- The file has:
  - a 2,064-byte header (a JSON block with the counts, section offsets, source URL, ETag, Last-Modified and build date)
  - 13-byte records sorted by 256 ly grid cell (the id64 and a 5-byte position inside the cell at 1/32 ly, the precision of the source)
  - a cell table
  - a sparse name index (every 64th name)
  - compactly coded names

Querying and building:

- A query keeps no file open: it reads the cell table once, caches it, and seeks only to the cells near the position, doubling the search from 256 ly out to 5,000 ly.
- The build is two-pass and streaming (32 temporary bucket files), written to a temporary name and renamed, with progress and cancel.
- On a synthetic 5,000,000-record dump it took 35 s and 103 MB, with queries under 6 ms.

Where it lives and how it is used:

- The folder is global rather than per commander (it holds facts about stars), is protected from the updater (`update._OWN_DIRS`) and left out of Back up my data (`data_backup.LEFT_OUT_DIRS`).
- Neutron Star uses the index when it is installed and enabled and falls back to the Spansh search when it is missing, damaged, of another format version or has nothing within 5,000 ly. White Dwarf always asks Spansh.

**Update** is a top-up when it can be (`star_index_download.choose_update`, `star_index_job._topup`, `star_index_build.build(topup_from=...)`):

- Spansh's `systems_1day.json.gz` and `systems_1week.json.gz` list every system changed since midnight (UTC) 1 or 7 days before the file was made, in the dump's layout.
- The smaller file whose start is at or before the index's date is fetched with `If-Modified-Since`.
  - The index's date is the Last-Modified of what it is current to, kept in the header with the original dump's, a count of top-ups and the file's ETag.
- `StarIndex.records()` streams the old records through the same bucket pass as a full build, dropping each system the file mentions and adding the file's neutron stars. A system whose main star is no longer a neutron star therefore leaves the index.
- The builder checks the file's oldest `updateTime` against the index's date (`TopupGap`).
  - The job then downloads the full dump instead, as it does when the index is more than a week behind, after 20 top-ups or 60 days.
- Checked on the real 1-week and 1-day files: the merged index equals the direct computation record for record.

**Nothing runs in the background by default, apart from three small exceptions.**

- Every lookup is started by a button or is opt-in (off until enabled in Settings). That covers the Mining lookups, the Exploration Value extras (Spansh and EDSM), the Boxel Survey skip checks and alias confirmation, Region Sweep's auto-discover, and the update check.
- The exceptions:
  - The BGS tick poll: one small request a minute to the tick service while BGS is on (it can be switched off).
  - The Codex Completionist catalog, downloaded when you open its details window and the saved copy is missing or over 14 days old.
  - The Rare Goods window, which looks up each origin system the first time you open it (see below).

**Remember answers instead of asking again.**
- Rare Goods: a system's controlling Power is cached for the whole EDMC session, and failed lookups
  are cached too, so a dead network isn't hit on every redraw. Lookups run at most 5 at a time.
- Canonn site lists are downloaded once per session. The Codex catalog is saved on disk
  (`codex_catalog.json`) and reused for 14 days.
- The automatic ring-reserve check (opt-in) is remembered per ring for the session, and is never run
  while the journal is being replayed at start-up.
- Source picks (`source_picks.find`, used by Trade's Best picks button and by the Missions Source commodities window) run one Spansh station search per pick.
  - The picks are cheapest, local, closest, then the 10% band sorted by distance, with a carrier search fifth.
  - They run one after another with a 0.4 s pause, each asking for 25 stations of market data at most 7 days old.
  - The search asks Spansh for a minimum supply (or demand) and, for the band, a `buy_price` / `sell_price` range (`mining_spansh_client.search_best_price_stations(min_quantity=, price_range=)`).
  - The band is the cheapest price up to 110% of it (selling: 90% of the highest up to it).
  - `mission_sources.lookup` runs it for each commodity in turn on a worker thread.
  - Nothing is cached or stored.
- The Where to Buy window (`colonization_buy_window.py`, opened by the Sites window's **Where to Buy** button) holds the search. It knows the Sites window only through a `Host` of four callbacks (the picked commodity, the rows still to buy, the selected site's system and the commander's system); the Sites window tells it when the pick or the site changes (`set_wanted`, `follow_site`). The search choices keep their old settings key, and the window has its own geometry key.
- The Colonization window's Where to buy search remembers an identical search (same system, commodity, radius, pad size, carriers and sort) for 2 minutes, and runs only when you press Find nearest or Find all, asking for at most 25 stations and 10 carriers per commodity.
  - Find all (`colonization_sources.find_whole_list`) is the same search once per outstanding commodity on one worker thread, in order.
    - It pauses 0.4 s before each request that really goes out (answers from memory cost no pause; the cache key is shared with Find nearest).
    - It records a failed commodity and carries on, and checks for a Stop between commodities.
  - With two or more commodities and no failure, one more request asks for the 5 nearest stations that have every one in stock.
    - It is `mining_spansh_client.search_stations_selling_all`: several `market` filters, which Spansh ANDs, checked live 2026-10-13 with 16 filters.
    - Each station is added to every commodity's sources unless already listed, with that commodity's price and supply from the market Spansh returns.
    - A failure of that request is ignored.
  - When the window passes `needs` (tons still to get), that request goes first.
    - A commodity that one returned station can supply in full is skipped (no per-commodity search).
    - After the searches, if `plan_route` still leaves two or more commodities uncovered, one more request (`also=` the other listed commodities) asks for stations selling all the uncovered ones, whose whole markets are merged the same way.
  - The window keeps the closest 5 stations and 2 carriers of each.
  - `plan_route` then builds a shopping route from the full answers.
    - It is greedy by tons a station can supply of what is still outstanding (a station selling several commodities counts for each), ties to the nearer then cheaper, at most 6 stops, shown nearest first.
    - It reports what no returned station can supply and never guesses beyond the stations searched.
- The Colonization window's search choices (radius, pad, carriers, sort) are one JSON string in EDMC's config
  (`wfmt_colonization_search_prefs`, `colonization_sources.SearchPrefs`), written when a search starts and when the window
  closes. They are window preferences like its geometry, so they are shared by every commander; nothing about play is in them.
- "Only what [station] sells": on a `Market` event the Colonization controller reads `Market.json` (checked against the event's `MarketID`, and read again for up to 0.4 s if the game wrote it late) and keeps the commodities with stock and a buy price (`trade_market.sold_keys`).
  - It forgets them on `Undocked`, `FSDJump`, `SupercruiseEntry` and a `Location` without a station, because the file stays on disk after you leave.
  - Not saved; only the market opened this session is known.
- Earth-like-world rarity is remembered per system for the session, and EDSM upload status per
  system for 10 minutes, so re-selecting the same target costs no extra calls.
- The Boxel Survey keeps a local log of systems you've visited, so the Random button never spends an
  EDSM call on a system it already knows you've been to. Region Sweep's "require a full FSS scan" uses the journal's
  `FSSAllBodiesFound` and makes no call.

**Hard limits on how much one click can do.**
- A skip-check run (Sequence mode, or Region Sweep with *Skip systems already visited by anyone (EDSM)* on) makes at most 20 EDSM lookups. Random makes one Spansh search (kept in memory for 10 minutes and 5 ly, so repeat clicks make none) and at most 6 EDSM bodies lookups per click. Sequence's automatic "nearest real system" suggestion happens only in
  response to your own clicks, at most once per 3 **Next** clicks in a row with no jump.
- EDSM nearby-system queries use a 100 ly cube, half the documented 200 ly maximum.
- Reordering a Waypoint Route uses one bulk coordinate request for the whole list, not one per system.

**One at a time, and no retry loops.**
- Each lookup carries a generation number, so a newer request supersedes an older one and a stale
  result is dropped. Region Sweep's auto-discover only fires when the queue is nearly empty, and only
  one lookup is ever in flight (so at most one per jump).
- A failed request returns "no result" and is not retried. The only repeat is the BGS tick's next
  scheduled poll, a minute later.
- Every request has a timeout (8 to 60 seconds), so a slow service never leaves a request hanging.
- Trade's route search is the one lookup that polls: Spansh queues a job and WFMT asks for the result every 5 seconds, for at most 4 minutes (about 48 requests), then gives up. It stops at once on **Cancel**.
- A Near me or Galaxy price search is two requests per press (stations, then fleet carriers; one if carriers are hidden), because carriers are priced so differently that in one list they can fill the page.

**Fewer calls by design.**
- The Rare Goods list is bundled, with EDSM coordinates and Inara and Spansh ids looked up once, so
  those aren't requested at runtime. The exobiology and region tables are bundled for the same reason.
- Only documented APIs and published data files are used, never page scraping.

**If you add a network call,** follow the same rules: opt-in or user-triggered, cache what you can,
cap what one action can do, set a timeout, and identify WFMT with `http_identity.user_agent()`.

**Support the services.** They are funded by their authors and their supporters; `docs/ATTRIBUTIONS.md` has links.

## 12. Feature notes

Short explanations of the non-obvious decisions in each area. Filenames are in `plugin/`.

### Powerplay (`powerplay.py`, `session.py`, `store.py`, `formulas.py`, `powerplay_ledger.py`, `powerplay_state.py`, `powerplay_backfill.py`, `powerplay_systems_tab.py`, `powerplay_overlay.py`, `powerplay_system_lookup.py`)

The journal's `PowerplayMerits` event reports what you earned, after every game multiplier.

- It does not say how many Control Points that is; that depends on the activity, and Frontier hasn't documented it.
- So the merit-per-CP ratios are **user-editable settings**, not constants, because they are community estimates that Frontier retunes.
- Sessions are tied to the journal file, so a logout to the menu and back, or an EDMC restart mid-game, continues the same session instead of splitting it.
- A "last merit timestamp" high-water mark lets a journal rescan tell an already-counted gain from one missed during an EDMC restart.

**Rare Goods Finder** (`rare_goods.py`, `rare_goods_window.py`, `powerplay_control_lookup.py`, `rare_goods.json`)

- Rare-good origins never move, so the 141-entry dataset (coordinates, Inara id and Spansh id64 included) ships as a static file.
- The "nearest" calculation is plain 3D distance from the latest `StarPos` the Powerplay controller saw.
- Only the origin system's controlling Power changes (weekly), so that alone is fetched live from Spansh's `system/<id64>` endpoint on a small thread pool.
- Results are cached per process, including failures, so a redraw or a dead network never re-requests.
- The window marshals results back onto the Tk thread and drops any that belong to a superseded refresh.

The window's filters apply before the number shown:

- **Large pads only** keeps `pad == "L"` (`rare_goods.candidates`).
- **Only my Power** walks the candidates nearest first.
  - It asks Spansh about `POWER_BATCH` (10) uncached origin systems at a time and re-evaluates from the cache after each batch.
  - It stops when `limit` are controlled by the commander's pledged Power (`PowerplayTracker.my_power`, compared by `rare_goods.same_power`) or none are left.
- Both choices are remembered (`wfmt_rares_large_only`, `wfmt_rares_my_power`); the second is unavailable until a Power is known.

**The overlay card** (`powerplay_overlay.py`, spec section 12 in [POWERPLAY_TECH_SPEC.md](POWERPLAY_TECH_SPEC.md)).

- `PowerplayController.overlay_info()` builds an `Info` from the tracker, the session and the cycle ledger. `powerplay_overlay.build_card` turns it into a `Card` (pure), and a `LiveCard` redraws it on every event and once a second.
- `PowerplayTracker.system_activity` and the module function `activity_for` give the Acquisition / Reinforcement / Undermining guess without the side effects of `classify_current_activity`, so a display may call them as often as it likes.
- The card is drawn by `StackedLayout` (new ids when its geometry changes, so the panel stays under the heading text) through `LatestOnly` and a render lock, so redraws do not overlap.
- A `StartJump` to a hyperspace destination is noted by the controller and, only with the `wfmt_powerplay_overlay_lookahead` tick on, looked up through `powerplay_system_lookup.py` (Spansh by system id, via `spansh_courtesy`).

### Boxel Survey (`boxel*.py`, `region_sweep_*.py`, `waypoint_route*.py`, `edsm_client.py`)

- Procedural system names have a fixed shape: sector words, a cube id, a mass letter, and a sequence number.
- WFMT parses that string well enough to step forward and back and to build the next candidate name; the galaxy map then confirms whether it exists.
- It deliberately does **not** decode names into coordinates, which needs Frontier's id64 math.
- That decision was tested: an "increment the cube number" shortcut was built and then reverted because it produced candidates nowhere near the player.

Spatial adjacency therefore comes from a real source:

- EDSM's `cube-systems` query, centered on the journal's `StarPos`, supplies nearby real systems.
- Region Sweep's *Skip systems already visited by anyone (EDSM)* uses `region_sweep_edsm_skip.skip_known_candidates` on a worker thread (the panel polls a result queue, and a newer jump or **Next** press makes an older check stale through a generation number). It steps past candidates `edsm_client.system_known` says EDSM knows, up to 20 per advance, keeps the candidate when a lookup fails, and caches answers (`KnownSystemCache`) for the session.
- Region Sweep never invents a "next cube" itself; it only tracks completion for cubes it was given by a typed seed, EDSM or Spansh.
- **Random** asks Spansh for the real systems nearest you, keeps those with no scan data, and confirms one with EDSM.
  - It checks a local per-commander visited-systems log first, because a visit without a scan leaves no trace in either service, so a system you already visited could otherwise come back as "new".

Details and open questions are in the [Boxel Survey spec](BOXEL_SURVEY_TECH_SPEC.md).

### Exploration Value (`exploration_value.py`, `elw_rarity_spansh.py`)

Estimates the scan payout with the community's formula, as a pure module (`scan_value.py`):

- A base value of k + k x 0.56591828 x mass^0.2 (at least 500) from the planet class's k (plus the terraforming bonus; an Earth-like world always counts as terraformable).
- A first-discovery multiplier of 2.6.
- For a mapped planet, the mapping multipliers: 3.699622554 for a first discovery and first map, 8.0956 for a first map of an already discovered body, 3.3333333 for an already mapped one.
- The Odyssey (30% of the mapping part) and efficiency (1.25) bonuses.

Readouts:

- The readout shows the scan value; the mapped value is on the Body info card and in the Expedition Log.
- System age needs no formula: a star's `Scan` event already carries `Age_MY`.
- The region readout is a local lookup on `StarPos` against a coordinate grid with no network call.

### Discovery Alerts (`discovery.py`)

Uses fields the journal already carries.

- On arrival the game auto-scans the star (`ScanType: "AutoScan"`); its `WasDiscovered` is `False` if nobody has scanned it.
- Any `Scan` has its own `WasDiscovered`.
- `SAAScanComplete` has no flag, so whether you are first to map is taken from the *previous* `Scan` event's `WasMapped` for the same body. It is cached per body and cleared on system change so a stale entry can't leak into the next system.
- It stays silent in the common already-discovered case: it's a celebration, not a status readout.

### Notable Bodies (`notable_rules.py`, `notable.py`)

**The rules** (`notable_rules.py`)

- It is pure (no EDMC or Tk imports): a table of `Rule`s, each a function of one `Scan` event plus the other scans already seen in the system (`bodies`, by `BodyID`), returning a one-line detail or `None`.
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
  - a shepherd moon is one orbiting inside the *outermost* ring's outer edge
  - a close or colliding binary is a pair sharing a barycenter whose radius/semi-major-axis is above 0.4 for both (colliding when their periapsis distances are less than their radii)
- A high-value body is any terraformable or any Earth-like, water or ammonia world, landable or not (its detail says "undiscovered" or "unmapped" from `WasDiscovered` and `WasMapped`).
- Fast rotation and fast orbit apply to planets only here (a neutron star spins in milliseconds), and fast rotation skips tidally locked bodies.
- Green gas giants are matched on planet class plus a table of confirmed surface temperatures (+/-0.001 K), from community research credited in THIRD-PARTY-NOTICES.md.

**The tracker** (`notable.py`, follows `discovery.py`)

- `NotableTracker` keeps the current system's scans keyed by `BodyID` (reset on a new `SystemAddress`).
- When a body arrives it also re-judges the already-scanned bodies that orbit it, since a moon is often scanned before its parent.
- `(BodyID, rule)` pairs alert once.
- One card per body, with the first rule's label as the title and `+N` for more. A body matching several rules gets one card.
- Cards show for 6 s; three can wait and the rest are only counted ("(N more)").
- Title and name are capped (60 and 56 characters, 70 for a name with the "(N more)" count) so a runaway value cannot make the card unreasonably wide; the card widens to fit what is shown.
- Rule choices are saved as a JSON dict in `wfmt_notable_rules`; a rule missing from it uses its default, so a later release can add rules without a migration.
- There are 15 rules, 7 on by default.
- The feature has no panel widget, only a Settings page (Overlays → Notable Bodies).

### Nearest neutron star / white dwarf (`neutron_finder.py`, buttons in `discovery.py`)

The **Neutron Star** and **White Dwarf** buttons ask Spansh's `bodies/search` for the nearest system whose *primary* star is a neutron star or a white dwarf.

- The filters are `subtype` (`Neutron Star`, or the 14 `White Dwarf (xx) Star` classes, which Spansh lists separately) and `is_main_star: true`, sorted by distance.
- The origin is given as `reference_coords` taken from the journal `StarPos`, so it works from a system Spansh has never seen.
- The request shape was worked out from live calls (Spansh doesn't document it); `neutron_finder.py` is the one place to fix if it changes.
- It asks for two results so it can skip the commander's own system.
- The lookup runs on a worker thread with a result queue polled via `after()` (same as the GEC panel), and is manual only.
- It copies the full system name to the clipboard, and truncates the displayed name (`MAX_NAME_CHARS`) so a long name can't widen the window.
- `tests/test_neutron_finder.py` covers the result-picking against canned responses.

### Organic Scanning (`organic_scan*.py`, `organic_*_data.py`)

Predicts species per body from atmosphere, gravity, temperature, pressure, region and other rules, and tracks the Log, Sample, Analyze progression plus how far you must walk between samples.

- It shows estimated credits (a flat per-species value; there is no first-discovery bonus for exobiology).
- It is local and read-only and submits nothing.

- The two `*_data.py` files are **generated** and marked "do not hand-edit", so a new species is a regeneration, not a hand transcription that could silently introduce errors.
- Region lookup holds the game's 42 region boundaries as a coordinate grid indexed from an origin offset.
- See the [Organic Scanning spec](ORGANIC_SCANNING_TECH_SPEC.md).

### Mining (`mining_*.py`)

- **Runs** are bounded by `Undocked` and `Docked` (space) and `LaunchSRV`/`DockSRV` (surface).
  - This is coarser than "from first prospector to next jump" but more reliable: that alternative fragments one stop at a ring into several runs whenever the player supercruise-hops.
- **Deposit estimate** (`mining_deposit.py`) turns Rigs count plus the HUD's Amount and Density readings into a *range* of tons, not a number.
  - The bands come from measured depletion traces, not a documented formula (125-175 t per rig position x a Density factor of High 1, Medium 2, Low 3).
  - Density readings are entered on trust; unknown values widen the range rather than guess.
  - Rigs is capped at 7 in the hotspot dialog.
  - While the Rhino is out, each `MiningRefined` ton is credited to the nearest positioned hotspot within 200 m (`Hotspot.mined_tons`, written on a 5 s throttle and on shutdown), so a Depleted deposit reads "depleted (612 t)".
  - Saving a hotspot from the panel within 100 m of an existing one on the same body updates it instead of adding a second.
- **Windows** (`plugin/uikit/`, `mining_ledger.py`) use WFMT's own navy look - see "External windows" in section 5.
  - The Surface Mining Book (`mining_ledger.py`, data in `mining_ledger_data.py`) is the browser for scanned bodies and saved hotspots.
  - Beyond the list and map it holds the following, each documented in `MINING_TECH_SPEC.md` section 6:
    - dated Depleted marks with an optional assumed refill time (`mining_depletion.py`; the default is unknown and a mark stays)
    - Rhino stops (`mining_stops.py`; the map draws `MapCircle` rings)
    - the deposit within 175 m of the Rhino picked as "you are here"
    - Market research (`mining_market_research.py`, `mining_market_research_dialog.py`; one Spansh station search per system, behind the price finder's switch)
    - one-line sharing of a deposit (`mining_share.py`)
- **Your own rates** (`mining_ground.py`): no third-party dataset is bundled or downloaded.
  - The journal never reports what a surface deposit holds, so `OwnRates` tallies the commander's saved hotspots per kind of ground: "of the deposits you recorded on this kind of body, what share were this material", with the sample size shown.
  - `classify(PlanetClass, Volcanism)` maps a scanned body to a ground key (rocky bodies split on volcanism, tested before anything else; "silicate magma" before "silicate").
  - A hotspot saved from the panel is stamped with `Hotspot.ground` when its body is in the current system's survey; older or imported ones count via the survey while their body is scanned, and are skipped otherwise.
  - Only recorded deposits count, so treat it as "what I have found so far", not what a body holds.
  - The Surface Mining Book hides the section until something is recorded.
- **Minimap markers** are color-blind-safe: pale filled dot = live hotspot, hollow gray ring = depleted, blue outlined dot = you.
  - In the ship (no Rhino out) the map shows only under 2 km altitude, from Status.json's `Altitude`.
- **Coverage** (`mining_coverage.py`) paints a fixed-radius disc at each recorded point.
  - It records where the Rhino has *driven*, not what has been scanned, because nothing in the journal or Status.json says a scan happened.
  - The module says so, and the UI shouldn't claim otherwise.
- **Bearing** (`mining_bearing.py`) computes the relative bearing to a saved hotspot from live Status.json position and draws an overlay arrow.

### Trade (`trade_*.py`)

Full detail is in the [Trade spec](TRADE_TECH_SPEC.md); the decisions worth knowing here:

- **Profit uses the game's own number.** `MarketSell` carries `AvgPricePaid` (what the sold tons cost), so
  profit is `TotalSale - AvgPricePaid x Count` with no stock-lot bookkeeping; stolen cargo has `AvgPricePaid` 0.
  Running costs (fuel, repairs, rearm, limpets) are summed from the journal's cost events and subtracted to give
  a net figure; insurance rebuys and fines are not included.
- **Names go through one resolver.** Spansh's market search is case-sensitive and exact, and the journal's
  plural ("Void Opals") finds nothing where the list's "Void Opal" works. `trade_commodities.resolve` maps
  typed text, journal names and internal symbols to Spansh's exact name, from a generated table;
  Mining's price finder uses it too.
- **Offers are ranked for your load**, not by price per ton: `price x min(tons, demand)`. A station
  paying more per ton but wanting 40 t is worth less to a 200 t hold.
- **Pad filtering is client-side.** Stations your ship can't dock at are dropped after the search (so a
  filtered search asks for 40 stations, not 20). Unknown ship or missing pad data means "don't filter", never
  a guess. Carriers always fit and are listed apart because they can move.
- **History is saved on request, from a richer ledger.**
  - The live ledger keeps a bounded log of every trade and cost with its station, plus jumps and the starting balance.
  - **Save session** snapshots it (and the stock, hold and carrier) into `trade_history.json`; re-saving the same session (however many logins it spans) updates the same record.
  - `trade_stats.py` works out every figure and table row so the Trade History window (`trade_history_window.py`) only lays them out.
  - Totals are exact; the log can be shorter on a very long session.
- **Unsold stock is one book, not two trackers, and an estimate** (kept for Trade History, not shown on the Session page).
  - `trade_stock.py` follows cargo bought and not yet sold per commander across logins, with average cost.
  - A carrier-loading run and a station-to-station run are the same thing to it (buys add, sells remove, carrier transfers change nothing).
  - It applies each event once using the last-event time plus fingerprints of same-second events, and catches up at start by replaying recent journals synchronously, before any live event.
- **A transfer goes to the carrier you are docked at.** `CargoTransfer` doesn't name one; `Docked`/`Location`
  carry the station's `MarketID`, which equals the carrier's `CarrierID`. Docked at someone else's carrier,
  nothing is counted; with two carriers and no dock information, the transfer is skipped rather than guessed.
- **The page is blocks, not text.** Each page is a list of typed blocks (`trade_blocks.py`) drawn by `BlockView`
  (`trade_view.py`), so headings, label/value rows and number columns are real layout instead of text padded with spaces.
  The builders are pure and testable, and an unchanged page isn't redrawn. See the Trade spec for the sizing rules.
- **The page arrows** are the shared `panelkit.nav_arrow` (a raised, bordered, padded label with a large bold
  glyph), also used by Mining and Missions, because the bare triangles they replaced were too small to see in
  EDMC's small window.

### Missions (`missions*.py`, `mission_*.py`, `active_missions.py`, `kill_missions.py`, `all_missions.py`, `kill_tracker.py`)

Data-layer modules keep per-commander state and announce changes through `Notifier` objects (`notifier.py`); derived views and the UI subscribe to them. That avoids the data layer importing UI code.

- A bounded lookback journal scan (`journal_scan.py`, two weeks) restores missions on startup: long enough to catch anything still active, short because missions expire.
- It also works out which missions the journals leave active, so a restart mid-game does not wait for the next login (see "Catching up on state EDMC missed").
- `mission_cargo.py` keeps the newest `CargoDepot` progress per mission.
- `FactionKillBond` kills count like bounties.

### BGS (`bgs_*.py`)

- Pure logic: `bgs_tracker.py` parses journal fields.
- `bgs_ledger.py` (`TickLedger`) holds one tick period's per-faction snapshots (pre-tick `before` and latest `now`) and activity, and runs identically on live events and on a replay of journal files (`bgs_journal.py`).
- Trade and exploration credit are attributed to the *station's* faction, which spans two events (`Docked`, then the market event), so the ledger carries that context.
- `bgs_format.py` is the shared wording.
- The tick client polls every 60 seconds.
  - A new tick archives the closed period (kept for the "archive days" setting) and starts a fresh one.
  - The current period is rebuilt from the journals once per session.
  - The period that just closed is rebuilt from the journals too (`bgs_ledger.repair_record`, up to 14 days back) and filed over the live record, because play made with EDMC closed is not in it.
- See the [BGS spec](BGS_TECH_SPEC.md).

### Operations (`screenshots*.py`, `screenshot_*.py`, `inventory*.py`, `ship_builds*.py`) and Colonization (`colonization*.py`)

- Screenshots convert the game's raw file into a renamed PNG on the `Screenshot` event, with a crop chosen by which HUD panel had focus.
- Inventory works out which vehicle you are in (ship, on foot or SRV) purely from `Embark`, `Disembark`, `LaunchSRV` and `DockSRV`, because EDMC only tracks on-foot versus not.
  - Micro-resource names resolve through a bundled table, then names learned from the journal, then a title-cased fallback.
- Ship Builds is a per-commander list of URLs to builds designed elsewhere; WFMT doesn't design loadouts.

**Build costs**

- `build_costs.py` reads the bundled `colonization_costs.json` once (55 entries, 109 layout names; a copy of a community-compiled table, notice in THIRD-PARTY-NOTICES.md).
- A site's `buildType` is a layout name; an entry's own type wins over another entry that merely lists it as a layout (`tellus`).
- A missing or damaged file gives an empty table, so a cost is simply not shown.
- Raven Colonial's `maxNeed` for a `no_truss` Coriolis (53,723 t) equals the table's total, which is the cross-check.
- The Planned Builds window shows the full cost for planned and building sites, totals the planned ones in its subtitle, and lists the five biggest commodities on a click.

**Planned builds (Raven Colonial)**

- `rcc_client.fetch_system` does one `GET /api/v2/system/<name>` (public, no key; the answer carries the architect, an `open` flag and the `sites`) per press of the Sites window's Planned Builds button (`colonization_builds_window.py`, on a worker thread with a poll, like Where to buy).
- The system name is percent-encoded into one path segment.
- The request carries `http_identity.user_agent("rcc-system")` and a 15 s timeout, and at most 2 MB is read (a real answer is 7-17 KB).
- Malformed entries are skipped and names are clipped.
- An answer (never a failure) is remembered for 60 s, and a 404 means no sites.
- Nothing about the commander is sent.
- The planned sites exist only on that service (the journal never reports them); a site with a market id the commander tracks is marked.

**Raven Colonial writes, key check and links**

- Every write (`rcc_client.send_write`, `complete_project`) and the key check carry `rcc-key` plus `rcc-cmdr0` (the commander's name as base64 of its UTF-8 bytes). Raven's own web app (read from its published script) sends both on every call to its API, so WFMT sends both.
- `rcc_sync` refuses to look anything up or send without a saved key (`_has_key`), because Raven's OpenAPI description declares no authentication at all, so which writes work keyless is unknown.
- `check_key` is `GET /api/Cmdr/_` (401 without a valid key, checked live; changes nothing), run on a worker thread from the Settings page's **Test key** button against the text in the box.
- A build in progress has a `buildId` but no `marketId` on the plan's sites.
  - `find_build_id` therefore falls back to the station's name (`station_part` strips the game's "Orbital Construction Site: " prefix; a build in progress wins over a finished namesake).
  - `build_id_for` adds a second route when the plan names none: `fetch_project_by_market` does `GET /api/system/<address>/<market id>` (public, 404 means none), the lookup SrvSurvey uses. The address is the plan's `id64` or the game state's `SystemAddress`. This finds a standalone project, one named "Primary port", and a station the game has renamed. A failed read raises `RccError`.
- `send_json` is `send_write` that returns the parsed answer (both share `_send_request`: one retry on 429 / 503, 401 / 403 worded without the key).
- The page links are opened with `webbrowser.open`:
  - `home_page_url`
  - `key_page_url` = `/user`
  - `system_page_url` = `/#sys=<name>`
  - `build_page_url` = `/#build=<id>`
  - Only **Open Selected Build on Raven** first reads the system's plan to find the id.
- The Sites window's header uses `uikit.widgets.MenuButton` (a `FlatButton` that posts a `tk.Menu`; `WindowShell.add_menu`).

**Creating a project (Raven Colonial)**

- `rcc_create.py` (pure) and `colonization_create_dialog.py` (the dialog); the flow is `ColonizationWindow._on_create_rcc` -> `_poll_plan` -> dialog -> `rcc_create.create` on a worker thread.
- The plan is read first (cache cleared). `build_id_for` finding a project ends the run ("already has one") and tells `RccSync.note_created`.
- The dialog collects: plan entry (an unbuilt, unlinked planned site, or none), name, location, building, layout, body, architect, notes, due date, primary port, make primary, attach carrier.
  - The building is chosen in three steps: location (`orbital` / `surface`), building (`BuildChoice`, by tier and name) and layout, the build type Raven knows it by (every key in the bundled table: `build_costs.table()` maps layout to building, `layouts_of` lists them with the building's own first). The layout is what is sent as `buildType`.
  - Body choices are `RccSystem.bodies` (`num`, `name`, `subType`; numbers above 999 are belts and rings and are dropped).
  - A construction ship (`is_construction_ship`: either spelling of colonization ship in the raw name) defaults to the name "Primary port" and `isPrimaryPort`.
- `create`: `PUT /api/project` with the market id, system address and name, star position, name, `buildType`, `commodities` still needed (required minus provided), `maxNeed`, a rebuilt `colonisationConstructionDepot`, and the optional fields only when known. A chosen plan entry goes in as `systemSiteId`; none leaves it out, so the project stands alone and the plan is never edited (as SrvSurvey does). The answer's `buildId` is required.
- Then, each reporting its own failure without undoing the project: `PUT /api/project/<id>/link/<cmdr>`, `PUT /api/Cmdr/<cmdr>/primary/<id>`, `PUT /api/project/<id>/fc/<carrier market id>`.
- The system address and position come from the plan (`id64`, `pos`) first, then EDMC's `monitor.state` when the commander is in that system (`rcc_create.locate`). The carrier id is the commander's own, from `CarrierStats` / `CarrierLocation` (`Feeder.own_market_id`).
- **Mark Plan Entry Demolished** sends `PUT /api/v2/system/<address>/sites` with the entry's fields and status `demolish`. Create Project has been used against the live service (during 1.2.0 testing); this write has not (see TODO.md).

**My Projects (Raven Colonial)**

- `colonization_projects_window.py` draws; `rcc_projects.py` (pure) makes the rows, progress, totals, trips and shopping text; `rcc_client` has the reads (`fetch_active`, `fetch_hidden`, `fetch_primary`: `GET /api/Cmdr/<cmdr>/active`, `/hiddenIDs`, `/primary`, public) and the writes (`save_hidden`: `POST .../hiddenIDs`; `set_primary`: `PUT .../primary/<id>`).
- The commander's name is lowercased and percent-encoded into the path. At most 200 projects and 1000 hidden ids are kept.
- "Counted" is the inverse of Raven's hidden list. Saving replaces the whole list, so it asks first. An older answer is dropped (`_request_id`).

**Delivery history**

- The delivery history (and the claim / release / beacon counts beside it, `record["claims"]`, each with its own newest-only mark) is rebuilt once per commander from every journal they have.
- A record whose `backfilled` version is lower than the current one is rebuilt again once.
- On first sight a worker thread runs `colonization_catchup.read_all_events`. A quick byte search skips the files with no deliveries, so years of journals take about a second.
- The Tk thread applies the result with `DeliveryLedger.rebuild`, which:
  - replaces the saved record only if the rebuilt tons and deliveries are at least as large (so deleted journals never shrink it)
  - folds in any live delivery that arrived meanwhile under the newest-only rule
  - marks the record `backfilled`

**The Colonization mode**

- It is `PANEL_PLACEMENT = "colonization"`, the Colony button; the mode key is `colonization`.
- It shows a page built by `colonization_panel.build_panel`: the current project and the commander's history, filled by `_refresh_summary` from the saved sites, the ship's hold and capacity, the carrier record and the delivery ledger.
- The figures and wording live in `colonization_stats.py` (pure; `project_for`, `history_for`, `coverage_text`, `trips_text`, `next_step`, `delivered_text`).
  - The page has no separate Progress line: Delivered reads `N of M t (P%)`. Next does not repeat the Still to get figure, and Covered and Trips left are hidden once nothing is left to deliver.
  - It branches on whether the commander has a fleet carrier: no carrier means no carrier row and one trips figure of whole-ship loads; with a carrier it shows trips to buy and to haul.
  - The sites window follows the same rule (`_arrange_tiles`, one Trips column).
- `colonization_history.py` is the per-commander delivery ledger (`colonization_history.json`: totals by commodity, site and day, a `journal_at` watermark so the start-up catch-up and live events never count a delivery twice).
  - `apply_events` feeds it from every `ColonisationContribution`, with or without a known site.
- A `Site` also records `first_seen` and `completed_at` for the average build time.
- The progress bar is a fixed-size canvas, so it cannot widen EDMC's main window.

**Colonization journal events**

Colonization (`colonization.py` is pure logic, `colonization_data.py` the repository, `colonization_panel.py` and `colonization_window.py` the UI) is built on two journal events:

- `ColonisationConstructionDepot` is an authoritative snapshot of a depot's `ResourcesRequired`, so it replaces the stored list wholesale.
- `ColonisationContribution` only carries the amounts just handed over, so it advances `provided` between snapshots (clamped to `required`).
- Neither event names the station, only a `MarketID`, so the name is remembered from the latest `Docked` for that market and fills a blank only.
  - A `Docked` at a site already tracked is the game's own name for that market id, so `apply_dock_name` replaces the stored name (and system) with it, live and in the start-up catch-up. This is how a rename reaches WFMT.
- Names in these events are decorated (`$steel_name;`) while `state["Cargo"]` is plain (`steel`), so both go through `commodity_key` before being compared.
- The repository only saves when a site really changed, because re-docking re-sends an identical snapshot.
- At start-up `colonization_catchup.py` replays the recent journals into the repository (see "Catching up on state EDMC missed").

**The ship's hold**

- The In Cargo figures (Sites window, Colony page and overlay card) read the hold from the game's `Cargo.json` beside the journals (`journal_files.read_cargo_file`), because the journal's `Cargo` event carries only a count and EDMC's cargo state was seen not to follow a purchase.
- The file is ignored when it is missing, unreadable or describes another vessel (the SRV); `state["Cargo"]` is then used.
- After any event that can change the hold (`Cargo`, `MarketBuy`, `MarketSell`, `CargoTransfer`, `CollectCargo`, `EjectCargo`, `MiningRefined`, the limpet events and `Loadout`) the hold is read again 1.5 s later, in case the game had not finished writing the file.

**The Sites window's Acquire column**

- `colonization_view` keeps two figures per commodity: `remaining` (the site's own need, required less delivered) and `to_get` (that less the hold and the carrier, never below zero). The window's Acquire column, its category totals and its sort show `to_get`; the buy trips divide `to_get` by the ship's capacity and the haul trips divide `remaining`, so haul trips still count everything the site needs.
- The note under the Where to buy buttons is drawn in the accent color while a search runs, while the system check that follows it runs and while a Stop is pending, and in the muted color otherwise (one method sets every update, `_say`).

**Fleet carrier column**

- `colonization_carrier.py` keeps the window's FC column: tons transferred to the commander's fleet carrier, per commander through `commander_data.py`.
- Whether a commander has a fleet carrier is asked of Trade first (`trade_panel.fleet_carrier`: the Settings choice, else a recorded fleet carrier; `None` means unknown) so the two features always agree, falling back to what this module has seen itself.
- It is fed live and caught up from `CargoTransfer` events the same way.
- `apply_capi_cargo` takes the CAPI `cargo` list from `capi_fleetcarrier`. The CAPI copy can lag, and has been seen unchanged for longer than the throttle, so applying every copy undid transfers made just before it arrived. It is applied only when it differs from the tally and neither of these holds:
  - **Recent transfer:** the newest transfer (`journal_at`) is under `CAPI_GRACE` (15 minutes) old.
  - **Repeated copy:** the list equals the one stored as `capi_ignored`, the last copy ignored, and `capi_ignored_at` is under `CAPI_REPEAT_EXPIRY` (1 hour) old. After that the copy is applied, so a stable figure is not ignored for ever.
- An ignored copy is stored in `capi_ignored` with the time in `capi_ignored_at`; an applied one clears both and sets `from_capi`. `replace_from_journals` (Rescan Journals) clears both.
- Each call logs one INFO line (applied, same, or ignored with the reason), which is how a report of a wrong column is diagnosed.

**Best single systems** (`colonization_systems.py`) - no longer used by the Where to Buy window (it showed the suggested route only from 2026-10-31); the module and its tests are kept

- It was run after Find all (`colonization_sources.find_whole_list`) by `find_best_systems` on the same worker thread. It is pure logic around an injected `fetch` (`mining_spansh_client.search_system_stations`), so the tests use no network.
- `candidate_systems` groups the per-commodity answers by system (fleet carriers ignored) and keeps up to 6: the system searched around first, then those with the most commodities and tons, skipping systems found for a single commodity.
- Each candidate costs one request (a station search of distance 0 from the system returns every station with its whole market), paced `SYSTEM_PAUSE` apart. A failed system is recorded and the rest carry on; `cancelled()` is checked between systems, and the Stop button keeps what was found.
- `plan_system` adds up the stations' stock per commodity and reuses `colonization_sources.plan_route` limited to that system (fewest stations, most tons), then orders the stops by arrival distance. `rank` puts systems that cover everything first, then the larger share, the nearer, the cheaper.
- A single commodity asks for nothing. The Spansh names are normalized as the one-stop search does, and compared without regard to case.

**Where to Buy: surface ports and purchases** (`colonization_buy_window.py`, `colonization_sources.py`)

- `SearchPrefs.surface` (default true) is the Include surface ports tick. The raw Find all answer is kept; `_found_view` filters it with `without_surface` at draw time, so toggling needs no request. `surface_only_labels` names the commodities (still to get) whose every source with stock is planetary; `plan_route(..., surface_only=)` marks their `Purchase.surface_only`, and `Stop.is_planetary` marks a surface stop.
- `_check_orbital` (end of `find_whole_list`): for each commodity still to get whose every source with stock is planetary, one `find(..., orbital_only=True)` (station types `ORBITAL_TYPES` only) is merged in, because the nearest sellers can all be on planets. Only a commodity still surface-only after that is named.
- `refresh_needs` is called by the Sites window at the end of `_refresh_detail`: it takes the Acquire tons (`to_buy` rows with `to_get` above zero, for the commodities searched) and, when they differ from the last, replans with `plan_route` and redraws quietly (no change to the note). No request is made. A commodity with no tons left is skipped when the groups are drawn.

**Shopping-list overlay card** (`colonization_overlay.py`)

- It draws the optional shopping-list card, laid out as a table (Commodity, Required, Acquire, FC (only with a carrier), Cargo).
- `build_card` (pure) turns the most recently updated active site, the hold, the carrier tons and the ship's `CargoCapacity` into a frozen `Card`.
  - Acquire is what is still to get: required less delivered, less the hold and the carrier (a zero is drawn as 0). `Row.need` keeps the site's own remaining need for the covered / surplus rules and the trips to haul.
  - Rows are alphabetical at a construction site and grouped under the market's categories elsewhere; the footer has tons remaining and trips.
  - `show` (the setting `wfmt_colonization_overlay_show`: `all`, `buy` or `haul`; until it is saved the older tick box `wfmt_colonization_overlay_hide_covered`, on by default, decides, and on means `buy`) picks the rows through `colonization_view.shown`: `buy` leaves out the rows the hold plus the carrier cover, `haul` keeps the covered rows the hold does not yet hold in full. The Sites window's Show dropdown uses the same function; the row limit and the `+N more` count apply to the rows left, and the footer still counts every commodity.
- `render` / `clear` send it through the shared `OverlayClient` (ids `wfmt_colonization_s<line>_<column>`, registered as a Plugin Group in `load.py`).
- Columns are right-aligned from character counts, since the overlay has no text metrics.
- The controller redraws only when the card or position changes or half the 3600 s time to live has passed, sends on a short-lived daemon thread, and clears synchronously in `plugin_stop`.

**When the card is shown.** The card is drawn only while `Visibility` says so, in one of five cases:

1. `Status.json` `GuiFocus` is Station Services (5, from `dashboard_entry`) and the service opened last was the market, or the commander is docked at a carrier and the last service was not `Outfitting` / `Shipyard`.
   - The market is `Market`, or `CarrierStats` / `CargoTransfer`, or `Market.json` being rewritten. The controller compares its modified time on every `Status.json` update and every 500 ms, because the journal's `Market` event can reach EDMC several seconds late (seen under Proton), and only counts while a station-services screen is open.
   - A carrier is covered separately because the game writes no `Market` event for a carrier's market.
   - `Outfitting`, `Shipyard` and `StoreCargo` mark another service as open, `Docked`, `Undocked`, `LoadGame`, `StartUp` and `Shutdown` reset it, and so does `GuiFocus` leaving 5.
2. The commander is docked at a `FleetCarrier` / `SquadronCarrier` and `GuiFocus` is 1, the right-hand cockpit panel where the cargo transfer to the carrier is done (the game writes no event for opening it, and `CargoTransfer` comes only after a transfer is made).
3. The commander is docked at a construction depot (station type `SpaceConstructionDepot`, `PlanetaryConstructionDepot` or `ColonisationShip`, a "Construction Site" station name, or a `ColonisationConstructionDepot` event) and `GuiFocus` is 0 or 5.
4. The `Music` event's track is `FleetCarrier_Managment` (Carrier Management; both opening and closing are announced).
5. Optionally (`wfmt_colonization_overlay_right_panel`) `GuiFocus` 1 anywhere.

A manual `forced` flag (the Colony page Overlay button) overrides all of it and the enabled setting.

Settings keys: `wfmt_colonization_overlay_enabled` and `wfmt_colonization_overlay_row_limit` (0 shows every row, at most 60). The position is set on Overlay Placement; the older `_x` and `_y` keys are read only as a starting point.

### Report an issue and Copy diagnostics (`issue_report.py`, `ui._create_help_tab`)

Two buttons on Settings → General → Help.

- **Report an issue** opens `.../issues/new?template=bug_report.yml&labels=bug&title=...&environment=...` with `webbrowser.open`.
  - GitHub prefills an issue-form field from a query parameter named after the field's `id`, so `ENVIRONMENT_FIELD` (`environment`) must match `id: environment` in `.github/ISSUE_TEMPLATE/bug_report.yml` (a test checks it).
  - If the address would pass `MAX_URL_LENGTH` (2000) it falls back to the template alone.
- The Environment text is `environment_text()`: WFMT version, EDMC version (`config.appversion`, a function in current EDMC and a string in old ones), Python version and `platform_support.describe_system()` (Windows release and build, or Linux `PRETTY_NAME` + `XDG_SESSION_TYPE` + Flatpak flag).
- **Copy diagnostics** puts `environment_text()` and the newest WFMT log lines on the clipboard (`copy_diagnostics`):

- The log file is the `baseFilename` of the file handler on EDMC's logger (else `<app_dir>/logs/EDMarketConnector-debug.log`);
  `read_log_tail` reads only the last `LOG_TAIL_BYTES` (400 KB).
- `wfmt_log_lines` keeps a record when its header line (one starting with a date) contains `.<plugin folder>.`, with its continuation
  lines, so a traceback stays with its record; the newest `MAX_LOG_LINES` (80) are kept and `MAX_LOG_CHARS` (12,000) caps the text.
- `redact` replaces each commander name, case-insensitively and longest first, with `<commander>`, and the home folder (both slash
  styles) with `~`. The names come from `commander_names()`: `restore.latest_commander()` and `monitor.cmdr`. A commander WFMT cannot
  tell is not caught, which is why the guide tells people to read the text before posting.
- The clipboard is written with `clipboard_clear` / `clipboard_append` / `update()` on the Settings frame; failure returns False and
  the button shows *Could not copy to the clipboard*.

Nothing is sent by WFMT: the browser and the user do the sending, so the feature is listed in
[internet-and-privacy.md](guide/internet-and-privacy.md) but opens no connection of its own. The user-facing how-to is
[reporting-problems.md](guide/reporting-problems.md).

### Ship engineering planner (`ship_plan.py`, `ship_plan_tab.py`, `journal_blueprints.py`)

A ship loadout in the shape of the journal's `Loadout` event (EDSY and Coriolis export the same shape as SLEF, a list of `{header, data}`) becomes a list of blueprints and crafts for the wishlist.

- `ship_plan.parse` accepts a SLEF list, one SLEF object or a bare `Loadout`.
- `plan_module` takes one module's `Engineering` block (`BlueprintName`, `Level` 1 to 5, `ExperimentalEffect`, `EngineerID`).

- **Module type** comes from the item symbol by prefix (`ship_plan.MODULE_TYPES`; armour is `<ship>_armour_*`), because the same journal blueprint is a
  different table row per module type (`Weapon_LightWeight` is "Lightweight Mount" on a weapon, `Misc_LightWeight` is "Lightweight" on a utility).
- **Blueprint** comes from `journal_blueprints.BLUEPRINT_NAMES[journal name][module type]`; grades 1 to `Level` are the table's rows of that type and
  name. **Experimental effect** comes from `SPECIAL_NAMES[journal effect]`, a list of candidate names because the table's spelling differs
  ("Drag Munition" and "Drag Munition (Seeker only)"), and is the grade 0 row of that module type; one craft.
- **Generated data.** `scripts/gen_journal_blueprints.py` (run by hand; needs the network) joins the public ship-module data's `modifications/blueprints.json` and `specials.json` to the table through the module-data UUID the table records per grade.
  - The table gives every blueprint that shares a name the same UUID whatever the module ("Lightweight", "Reinforced", "Shielded"), so the join is limited to the module types of the journal name's family (`FAMILY_TYPES`/`FDNAME_TYPES` in the script) and a link must also agree on the words.
  - What it cannot link is printed, not guessed.
  - Review the diff before committing; `tests/test_ship_plan.py` checks that every link points at rows the table has.
- **Not counted, never guessed.** No `Engineering` block: left out. `EngineerID` 399999 (Frontier's pre-engineered marker): listed, takes nothing. An
  item with no module type, a journal blueprint with no entry for that type, a level outside 1 to 5, or fewer grades in the table than the level:
  listed as not counted or partly counted with the reason.
- **Current ship.** `ship_current.current_build` reads the last `Loadout` event of the newest of the last three journals that has one, on demand.
  - Nothing is stored; a `Loadout` has no commander name, so the newest file is the session being played.
  - `plan(build, current)` compares only when `Build.ship_id` (the journal's `Ship`, such as `federation_corvette`) matches; modules are paired by `Slot`.
  - `_already_on` subtracts when the current module has the same journal blueprint, the same module type and is not pre-engineered: `min(current level, target level)` grades are done and a matching `ExperimentalEffect` is done.
  - A module that is fully done gets the status `already done`.
  - `Plan.compared` says what it was compared with, or why not.
- **In storage.** `stored_modules.match_plan(plan.modules, book.modules(cmdr), where)` says, for each planned module, which stored module would do. It only informs: nothing is subtracted from the plan.
  - Only the stored list counts (`stored_modules.py`); a module fitted to any ship is not in it. A stored module matches on its `Item` (the same module, size and class).
  - `FULL`: it carries the planned journal blueprint (`PlannedModule.journal`) at the planned level or higher. `PARTIAL`: anything else, preferring the same blueprint at a lower level, and including a module swapped out of a ship whose engineering the game did not report.
  - The experimental effect is not compared, because `StoredModules` does not report one.
  - One stored module serves one planned module; full matches are given out before partial ones. With no snapshot yet (`book.asof` is empty) no match is shown.
- **Rolls.** `Plan.entries(rolls)`: each grade `rolls` crafts (1 to 10), an effect one, the same blueprint on several modules added together. The
  `Quality` of the last roll is shown, not planned with.
- **Wishlist.** `WishBook.add_many` validates every entry first and then applies them with one save and one redraw, or changes nothing and raises
  `WishError` (no commander, a blueprint not in the table, more than 100 blueprints, more than 99 crafts of one). Input is capped at 2 MB of text and 100
  modules; nothing is fetched from the network, and every table cell is length-capped.

### Odyssey upgrade planner (`odyssey_upgrade_plan.py`, `odyssey_plan_tab.py`)

**Costs and credits**

- The suit and weapon upgrade rows of the blueprint table (type Suit or Weapon, named for the item, engineer Merchant, grades 2 to 5) take their costs from 17 recorded `UpgradeSuit` / `UpgradeWeapon` journal events.
- The events record the `Class` reached, the `Cost` and the `Resources` spent:
  - 1, 2, 4 and 5 for the schematic, the family item and Manufacturing Instructions (or Health Monitor)
  - 2, 5, 9 and 12 for the item's other two materials, for every item and kind seen
- `tests/test_odyssey_upgrade_plan.py` holds the transcribed events and checks the table and the credit formula against them.
- The credits are not in the table: `CREDIT_UNIT` holds the cost of class 2 for the eight items seen, and class n costs `CLASS_FACTOR[n]` times that (1, 3, 6, 10, confirmed across several items and classes).
  - An unseen item has unknown credits (`None`) and the plan says so.
- To add an item's credits, add its `UpgradeSuit` / `UpgradeWeapon` journal line to `CREDIT_UNIT` (cost divided by the class factor) and to the test.

**Planning**

- `modifications_for` lists a suit's or weapon's grade 0 rows, leaving out the upgrade rows and, for a weapon, the modifications marked for another family.
- `Plan.entries()` is each class step and each modification once, for `WishBook.add_many`.
- `plan(..., fitted=)` counts the fitted modifications against the four slots and does not plan them again.

**Owned gear** (`odyssey_gear.owned_gear`)

- It reads the commander's gear on demand: it goes back through the newest journals of the newest journal's commander (up to 80 files) until two have `SuitLoadout`, `SwitchSuitLoadout` or `CreateSuitLoadout` events.
- `from_loadouts` keeps the newest sighting of each suit (`SuitID`; `SuitName` ends in `_classN`) and weapon (`SuitModuleID`; `ModuleName`, `Class`, `WeaponMods`), raised by any later `UpgradeSuit` / `UpgradeWeapon`.
- The journal's modification ids map to the planner's names in `SUIT_MODS` and `WEAPON_MODS` (range, headshot damage and hip-fire accuracy are one id for all weapons, spelled with the weapon's family).

### Megaship scans (`megaship_scans.py`, `powerplay_megaships_tab.py`)

The Powerplay activity *Scan datalinks at Megaships* is recorded per cycle in the Powerplay ledger (section 11.2f of the [Powerplay specification](POWERPLAY_TECH_SPEC.md)).

- `MegaShipTracker` follows the journal (jumps, the FSS megaship list, `SupercruiseDestinationDrop`, the `$Datascan_ShipUplink;` scan, the `PowerplayMerits` that follows).
- It is fed by both the live controller (`PowerplayController.handle_event`) and the back-fill (`powerplay_backfill.replay_entries`), so the two agree.
- The ledger de-duplicates by megaship and system, and a merit event is counted once (`MegaShipScan.merit_at`).
- Held back during a journal scan like any other live op.
- Tests: `tests/test_megaship_scans.py`.

### Auto-Honk (`autohonk.py`)

Reads the commander's active Elite binds file to find which physical key the chosen fire button is
bound to, then simulates that key being held for a configurable time. On Windows that is
`user32.keybd_event` through `ctypes`, which avoids an extra dependency. On Linux it is `xdotool`
(section 18). Each platform's calls are behind an explicit platform check because EDMC itself runs
on more than Windows.

## 13. Self-update

`update.py` is the single updater for the whole plugin: one version number, one GitHub Releases target.

Flow, all off the main thread:

1. Check the latest non-draft, non-prerelease release.
2. Compare versions numerically (padded to equal length so `1.2` versus `1.2.0` compares correctly).
3. Download the zip.
4. Back up the current install.
5. Unpack over it.
6. Tell the UI to show "restart to apply".

Design decisions:

- **Opt-in.** Auto-update is off unless enabled in Settings. A `disable-auto-update.txt` file in the
  plugin folder forces it off regardless, a handbrake for a folder you're hand-editing.
- **Staged, not hot-reloaded.** Python modules already imported can't be safely swapped in a running
  process. Files are replaced on disk and take effect at the next EDMC start.
- **Data survives updates.** The updater only writes files that are *in the release zip*. Data files
  aren't in the zip, so they are never overwritten. `_OWN_DATA_FILES` and `_OWN_DIRS` add a second
  layer: they keep listed data out of the pre-update backup and out of unpacking. Keep them in sync
  when adding a data file (section 16).
- **Backups.** The last three (`BACKUPS_KEEP`) are kept as timestamped zips; only those are trimmed, never the `pre-restore-` safety zips that share the folder. They hold code only: `_OWN_DATA_FILES` stays out of them.
- **Failure is quiet.** A failed check or download logs and returns; it never interrupts play.

### Design decisions for other features

These sit here for historical reasons; they are not about self-update.

- **Exploration Dashboard.** *(Why a window that holds nothing of its own: [DESIGN_NOTES.md](DESIGN_NOTES.md#36-the-exploration-dashboard).)*
  - `explore_dashboard.py` owns the window (`explore_dashboard_window.py`) and supplies `snapshot()`:
    - the shared `system_survey.survey`
    - `exobiology_overlay.current_view()` (Organic Scanning's view of the body, with the first footfall flag merged from the survey)
    - the newest Status.json (`dashboard_status`, with the position part of the window following at most once a second)
    - `expedition_log_panel.book.running()`
    - the Route overlay's `status_lines`
    - `exploration_value.readouts()`
  - `explore_dashboard_data.py` turns those into rows with no Tk, so it is tested without a screen.
  - Each source is read inside its own try, so one broken feature leaves a blank block and not a blank window.
  - Journal events redraw once, 150 ms after the latest.
  - Blocks and tables compare against what they last drew and rebuild nothing that did not change.
- **Carrier Route.** A separate window (`carrier_route_window.py`, opened from the Route Planner) over `carrier_route.py` (pure), `carrier_route_panel.py` (the owner), `carrier_route_spansh.py` (network) and `carrier_route_state.py` (`carrier_route.json`, one route per commander).
  - It asks Spansh's fleet carrier router (`POST /api/fleetcarrier/route`; the form and the answer are described in the module docstring, read from Spansh's page script and checked against a live Sol to Colonia answer).
  - It uses the same `spansh_planners.fetch_job` the other plotters use (a list in the form is sent as repeated fields, as Spansh's page does).
  - The carrier comes from the journal: `CarrierStats` (`CarrierType`, `Callsign`, `FuelLevel`, `SpaceUsage`), `CarrierLocation`, and `CarrierJump` or `Location` docked at the carrier's own callsign (a visit to another carrier never moves ours).
  - The recent journals are read once per commander when the window first opens.
  - Spansh's carrier constants are capacity 25,000 and mass 25,000 for a fleet carrier and 60,000 and 15,000 for a squadron carrier.
  - `route_planner_panel` feeds it the journal events.
  - The route follows the carrier by system name, as the ship route does.
- **Route Planner.** *(Why it is built this way, and the other designs considered: [DESIGN_NOTES.md](DESIGN_NOTES.md#37-the-route-planner).)*
  - **Which plotter.** It asks Spansh's **exact plotter** (`POST /api/generic/route`), not the neutron router (`/api/route`, which wants a jump range the game does not write for the current load).
    - WFMT carries no code for the neutron router, and the Expedition window's Neutron route button opens this planner.
  - **The request.** `route_planner.params_from_loadout` builds what Spansh's own page builds from a ship (read from its script):
    - `base_mass` = `UnladenMass` + `FuelCapacity.Reserve`
    - `tank_size` = `FuelCapacity.Main`
    - `internal_tank_size` = the reserve
    - the drive's `optimal_mass`/`max_fuel_per_jump` (`fsd_data.FSD`, replaced by the drive module's `FSDOptimalMass` and `MaxFuelPerJump` engineering modifiers), its `fuel_multiplier` and `fuel_power`
    - `supercharge_multiplier` (6 for the Mk II overcharge drive, else 4)
    - `injection_multiplier` 2
    - `range_boost` from a Guardian booster
    - `cargo` is Status.json's `Cargo` at the moment of plotting
  - **Systems** go by `id64`: the source is the arrival event's `SystemAddress` when the start is the current system, else `spansh_exact.lookup_system` (`/api/systems/field_values/system_names`), as is the destination.
  - **The answer.** `spansh_planners.fetch_job` submits and polls (it also serves the older planners).
    - The answer's `result.jumps` lists every system with `distance`, `distance_to_destination`, `fuel_in_tank`, `fuel_used`, `has_neutron`, `must_refuel`, `must_inject` and `is_scoopable`, which become `Leg`s.
    - Spansh assumes a full tank at the start.
    - A drive missing from `fsd_data` raises `PlotterError` (shown in the ship block and when plotting) instead of being guessed.
  - **Saving the route.** The plotted route is saved per commander in `route_planner_route.json` (`route_planner_state.py`, over `commander_data.py`).
    - It is written when a route is set, on each arrival at a leg and when it is cleared.
    - It is put back by `PlotterController._follow_commander` when the first event with a commander arrives after a restart.
    - A route that was already finished is not restored; a route plotted before the commander was known is kept and saved for them.
    - The last choices are in `wfmt_neutron_plotter_options`.
  - **Auto-copy** (`wfmt_neutron_plotter_auto_copy`, **on by default**) is one setting shared by the panel's tickbox and the window's (`PlotterController.set_auto_copy`).
    - `copy_next` runs when a route is set, on each arrival at a leg, and on request.
  - **Status line.** The window's status line says what happened.
    - `overlay_note` adds "Sent to the Route overlay." when `route_overlay.load_config().enabled`.
    - `route_planner_window.announce` says it at each arrival, and at the end of the route.
  - **Fuel scoop.** `ShipInfo.has_fuel_scoop` (an `int_fuelscoop_*` module in the `Loadout`) fills the ship block's Fuel scoop row and the warning after Generate route when there is none and the route has refuel stops.
  - **White dwarfs.** The option *Mark white dwarfs the route passes* (`Options.mark_white_dwarfs`) makes `spansh_exact.plot` ask `edsm_client.primary_star_types` after the route is plotted.
    - That is the bulk `api-v1/systems` call with `showPrimaryStar`, 40 names a request.
    - `route_planner.mark_white_dwarfs` sets `Leg.white_dwarf` where EDSM calls the main star a white dwarf.
    - Spansh did not plan with them, so they are extra boosts (`Leg.boost`).
    - A failed lookup leaves `Route.white_dwarf_check == "failed"` and marks nothing.
  - **The Route overlay prefers the route.**
    - `route_overlay.RouteOverlay.card` asks `active_neutron_route()` (the panel's route while it has a jump left) and, if there is one, draws `build_neutron_card` instead of the card made from the game's `NavRoute`; both go through `navigation_card`.
    - When the last jump is made the card says the route has ended (`ended_card`) for `END_SHOW_S`, then `reset_neutron_route` clears the panel's route (or the tracker's route is dropped).
    - The panel asks the overlay to redraw whenever the route changes.
  - The window's **Expedition** button calls `expedition_panel.open_window`.
  - **Secondary star check.** `PlotterController.check_ahead` (on set, on each arrival and on restore) hands the next `route_secondary.WINDOW` neutron stops that have a system address (`Leg.id64`, from the answer's `id64`) to a `SecondaryChecker`.
    - The checker fetches each system's stars with `spansh_exact.fetch_stars` (`GET /api/system/<id64>`) in the background.
    - `_poll_checks` collects the answers on the main thread into `Route.checked` and `Route.suspect`, which `build_neutron_card` (a `NEUTRON ?` tag in the warning color), the table and the arrival message read.
    - The rule (`neutron_is_secondary`) compares star names with the system's name and falls back to the database's main-star flag.
    - It is not saved, so a restored route is checked again.
- **Hiding overlay groups.** *(Why a prefix in the overlay layer and not the cards' enable settings: [DESIGN_NOTES.md](DESIGN_NOTES.md#33-hiding-groups-of-overlay-cards-the-dashboards-two-switches).)*
  - `overlay.set_group_hidden(name, prefixes, hidden)` hides the displays whose ids start with any prefix.
  - It sends a clear for the ones remembered in `_last` and `_remember` stops new ones being sent, exactly like `set_all_hidden`, but for those ids only.
  - It never touches Settings, so showing a group re-sends what had not run out, which is exactly the cards that were switched on.
  - Nothing is saved. Showing everything leaves a group that was hidden on its own hidden.
  - The dashboard's groups are `explore_dashboard.GROUPS`; `tests/test_overlay_group_hide.py` fails if a prefix there stops matching a real card.
- **Data backup.** *(Why the restore is staged and what is left out: [DESIGN_NOTES.md](DESIGN_NOTES.md#34-back-up-my-data-restore-and-automatic-backup).)*
  - `data_backup.py` is the other direction: it zips `_OWN_DATA_FILES` plus the `mining_sessions` folder into `WFMT-data-<date>-<time>.zip` in a folder the user picks (Settings → General → Backup).
  - It writes under a temporary name and renames it when complete, refuses a destination inside the plugin folder, and leaves out `LEFT_OUT` (`rcc_keys.json` and `discord_webhooks.json`, which hold secrets; `codex_catalog.json`, a cache) and `LEFT_OUT_DIRS` (`star_index`).
  - A new data file added to `_OWN_DATA_FILES` is therefore backed up automatically; add it to `LEFT_OUT` only if it holds a secret or can be fetched again.
  - `backup-info.json` lists the folder `mining_sessions/` as one entry, because those file names carry a commander name.
- **Restore.** A running WFMT holds its data in memory and rewrites the files, so a restore cannot overwrite them live.
  - `inspect_backup` checks a zip and refuses the whole zip on any other member. The rules:
    - it must hold `backup-info.json`
    - every other member must be a protected data file or inside `mining_sessions/`, with no absolute path, `..`, backslash or colon
    - keys and caches are refused
    - at most `MAX_RESTORE_BYTES` unpacked
  - `stage_restore` unpacks it into `restore_pending/` and writes `ready.json` last.
  - `plugin_start3` calls `apply_pending_restore` before any feature reads a file:
    - it zips the files about to be replaced into `backups/pre-restore-<date>.zip` (newest `SAFETY_KEEP`)
    - it moves the staged files into place with `os.replace` and removes the folder
    - a folder without `ready.json` is discarded
  - `restore_pending` is in `_OWN_DIRS`, so the updater's own backup and unpacking skip it.
- **Automatic backup.** Settings `wfmt_auto_backup`, `wfmt_auto_backup_folder`, `wfmt_auto_backup_days` (1 to 90, default 7).
  - `load._schedule_startup_backup` runs `run_configured_backup` on a daemon timer 60 seconds after start-up.
  - `UpdateManager._download_and_stage` runs it with `force=True` before the update is applied.
  - Files are named `WFMT-data-auto-<stamp>.zip`; `AUTO_KEEP` (10) of those are kept and nothing else in the folder is ever deleted.

## 14. Testing

```bash
npm run test:docker
```

This runs `python -m unittest discover -s tests` and then `tests/import_smoke.py` inside a Linux container on a virtual display, so no window opens on the desktop (see [DEVELOPMENT.md](DEVELOPMENT.md)). Suites cover the pure-logic modules:

- procedural name parsing and sequence walking (with real boxel data used to cross-validate)
- region-sweep queues, waypoint routing, survey log
- Canonn data parsing, organic species matching, Codex tallying
- deposit estimates and Rhino coverage

Test files add the repo root to `sys.path` and import `plugin.<module>` directly, which works because those modules avoid EDMC-only imports (section 6).

**Trade and data files**

- Trade mode's logic is covered by `tests/test_trade.py` and `tests/test_trade_search.py` (ledger, market parsing, Spansh response parsing, commodity names, ship pads, offer ranking, carrier cargo tracking and the journal backfill).
- `tests/test_own_data_files.py` reads the sources and fails if any plugin module defines a `*FILENAME` data file that is missing from `update.py`'s `_OWN_DATA_FILES`.

`tests/test_import_smoke.py` additionally imports every plugin module (including `load.py`) with EDMC's modules stubbed, in a subprocess, to catch import-time breakage that single-module tests miss.

Trade mode's drawn page and its History window are the Tk exceptions:

- `tests/trade_history_window_smoke.py` opens the History window the same way and visits every tab.
- The drawn page: `tests/trade_view_smoke.py` draws it in a real window with EDMC stubbed, in a subprocess (skipped when there is no display), and checks widths, redraws and column alignment.

Other coverage:

- **The Help tab's buttons**: `tests/test_issue_report.py` (the prefilled address, the log filter, the redaction, the clipboard hand-off, and that the form template carries the `environment` field the code fills in).
- **Engineering**:
  - `tests/test_blueprints.py` pins the corrections and additions (five recipes, seven synthesis rows, the Colonia four's upgrades, the nine materials).
  - `tests/test_engineers.py` covers the 38-engineer location table, its regions and name matching.
  - `tests/materials_smoke.py` opens the Engineering window (every tab, the Show filter, the Ship planner).
- **The ship planner's logic**: `tests/test_ship_plan.py` (parsing SLEF and `Loadout`, module types, grades and effects, merging, limits, and that every link in the generated `journal_blueprints.py` points at a row the table has).
- **BGS**:
  - `tests/test_bgs_ledger.py` covers `repair_record` and `merge_records`.
  - `tests/test_bgs_panel_repair.py` (in a subprocess, with EDMC stubbed) covers the panel's roll, replay and filing of a closed period.

Not covered by automation: anything else that needs a live EDMC or a Tk window (panels, dialogs, overlay rendering).

- Those are checked by hand in a real EDMC install.
- Overlay rendering changes should be verified against ModernOverlay's own payload log.

## 15. Gotchas

Things that cost time once and are recorded so they don't again.

- **Themed widgets take `foreground=`, not `fg=`.** EDMC's `nb.Label` is ttk-backed. Passing the
  classic `fg=` raises `TclError: unknown option "-fg"`. One such label broke WFMT's *entire* Settings
  window, because the error aborted building the whole tab.
- **`theme.update()` may silently do nothing.** During `plugin_app`, EDMC's theme registry is still
  empty and `theme.update(widget)` returns early without registering. Separately, it only recolors
  direct children. `ui.py` therefore retries `panelkit.apply_theme_deep` at 0.5, 1.5, 3 and 6
  seconds, walking the whole subtree.
- **Clipboard needs `update()`.** After `clipboard_append`, `panelkit.copy_to_clipboard` calls
  `update()` so ownership actually transfers before focus returns to the game. Without it, a paste
  can grab stale content.
- **Separator color is set statically** from a light-or-dark choice, not read back through the
  theme, for the same registry-timing reason as above.
- **A package beats a same-named module.** The window kit is `plugin/uikit/`, not `plugin/ui/`, because `ui.py` (the main-panel builder) already exists.
  - A `ui/` directory silently replaced it and EDMC reported `module 'WFMT.ui' has no attribute 'create_plugin_app'`.
  - `tests/test_ui_kit.py` and `tests/test_import_smoke.py` guard this.
  - Also: the deploy is a merge-copy that never deletes, so renaming or removing a module leaves the old one in the installed plugin folder - delete stale files there by hand.
- **ttk is global.** Anything that changes a ttk theme or stock style from a window affects the whole
  EDMC process. Namespaced style names (`WFMT.X.Treeview`) are safe; stock ones are not.
- **Tk option patterns match widget names**, not paths: `.!toplevel3*Label.background` is read as an
  application name and silently matches nothing.
- **A `tk.Label` can't take a tuple `padx`** (only `pack`/`grid` can); indent with spaces instead.
- **Case in commander and system names.** Store the original, compare with `casefold()`.
- **Never assume order between Status.json and the journal.** They are independent callbacks.
- **A label that spans columns can stretch them.** In a Tk grid a widget spanning columns 1 to 3 that is wider than
  those columns' combined width widens them, so a title column sized for the narrower layout overflows the window. Work
  out the width each column really needs (the wider of the table's numbers and any spanning value) before giving the
  title column the remainder; `tests/trade_view_smoke.py` catches it.
- **A price-sorted list can be all fleet carriers.** Carriers sell very cheaply and pay very well, so a
  galaxy-wide search sorted by price returned only carriers and the panel said no station had it. Ask for stations
  and carriers separately with the `type` filter (`trade_prices.STATION_TYPES` / `CARRIER_TYPES`).
- **Spansh market names are exact and case-sensitive.** "Liquid oxygen" works, "Liquid Oxygen" returns zero
  results with no error, and the journal's own plurals can differ from Spansh's. A search that silently finds
  nothing is the symptom; resolve every name through `trade_commodities.resolve`.
- **Journal files don't sort by name.** The game has used two file-name styles
  (`Journal.<date>T<time>.01.log`, `Journal.<yymmddhhmmss>.01.log`), so "the newest N" must come from modified
  time (`trade_carrier.journal_files`); sorting by name can quietly pick the wrong files.
- **Journal names and EDMC names differ in case.** `EXAMPLECMDR` in the journal, `Examplecmdr` from EDMC. Key
  anything per commander by `casefold()`.
- **`CarrierStats` isn't automatic and isn't replayed.** It exists only if the player opened Carrier
  Management, so state built from it needs a journal backfill at startup, and a baseline from before WFMT
  started is otherwise missed.
- **A `CargoTransfer` doesn't say where it went.** Use the docked station's `MarketID` against
  `CarrierID`; don't assume "my carrier".

**Settings tab and `pack`**

- EDMC's `myNotebook.Frame.__init__` grids a spacer child into every `nb.Frame`, so `pack` inside one always fails with "cannot use geometry manager pack inside ... which already has slaves managed by grid".
- A feature whose `build_settings` raises takes the whole WFMT Settings tab down with it (`Failed for Plugin "WFMT"` in the EDMC log), on Windows and Linux.
- Use `grid` inside `nb.Frame`s, or pack into a plain `tk.Frame` as `autohonk.py`'s rows do.
- This shipped once, in a build that was withdrawn, because the unit-test stand-ins had no spacer.
  - `tests/test_prefs_smoke.py` now builds every tab with stand-ins that do.
  - `tests/test_settings_layout.py` fails on any `pack` into an `nb.Frame`.

## 16. Adding a feature

1. Put pure logic in its own module with no Tk and no EDMC-only imports; add a `unittest` file.
2. Add `xxx_state.py` if it persists data: **per commander** (use `commander_data.py`), atomic write, tolerant load.
   - Give any new file a unique name, add it to `_OWN_DATA_FILES` (section 13) and say in `tests/test_data_files_per_commander.py` how it keeps commanders apart. Never put a commander name in a file name.
   - Reset any in-memory state about the previous commander when the active one changes.
   - Think about Windows and Linux (UTF-8, `os.replace`, no case-sensitive file-name assumptions) and note in `LINUX_TESTING.md` what is untested there.
3. Add the panel module implementing the contract (section 4). Choose `PANEL_PLACEMENT`.
4. Use `panelkit.wrap_label` for any text from the game, and a hard box for any image (section 5).
5. Put network calls behind the worker, queue and generation-counter pattern (section 7; Trade's
   one-job-at-a-time variant is described there too). Fail to an empty result, and make automatic lookups
   opt-in.
6. If it draws an overlay: use the shared client, a `wfmt_<feature>_` ID prefix, and register a group.
7. Prefix config keys `wfmt_<feature>_`.
8. Add the module to `FEATURES` (`ui.py`) and `_FEATURES` (`load.py`); call `start`/`stop` from
   `load.py` if it has them.
9. If it uses another project's code, assets or data, check the license and update
   `THIRD-PARTY-NOTICES.md` (and `ATTRIBUTIONS.md` for ideas) *in the same change*, before it ships.
10. If it must not miss play with EDMC closed, give it a start-up catch-up built on `journal_files.py` with a rule
    that never counts an event twice (a timestamp watermark, per-fact timestamps or an idempotent merge; see "Catching
    up on state EDMC missed"), and add its row to the table in the user guide's "If EDMC wasn't running".
11. Update the README and the user guide, including the guide's "What the game does and doesn't tell us, and how to
    work around it" section: say plainly what the journal never records or records late, what the screen shows when it
    is unsure, and what the player can do.

## 17. Known gaps

- **`_OWN_DATA_FILES` is a hand-kept list.** A new data file must be added to it (and a new data folder to `_OWN_DIRS`) or it will be swept into the pre-update backup.
  - Data is never at risk of being overwritten, since it isn't in the release zip.
  - `tests/test_own_data_files.py` fails when a `*FILENAME` constant isn't listed; a data *folder* is still unchecked.
- **Mining and other panels have no automated UI tests** (section 14).
- **Tick detection depends on a third-party, plain-HTTP service** with no SLA; when it is down the
  tally simply doesn't roll over.
- **Trade mode's gaps** are listed in its [spec](TRADE_TECH_SPEC.md#13-verified-assumed-and-known-gaps): a
  squadron carrier's `CarrierStats` is assumed to match a fleet carrier's, the commodity list and ship pad
  classes are snapshots, and carrier reserved space is only as fresh as the last Carrier Management visit.
- **Inventory's start-up sync relies on EDMC rebuilding its state** (backpack, ship locker) from the journal before it
  sends `StartUp`. That was not checked against every EDMC version.
- **Powerplay hand-in windows are a heuristic.** `PowerplayDeliver` precedes the merits it earns but does not link to
  them, so the first merit event within 10 minutes and any within 10 seconds of the last are labeled Delivery; a merit
  from another activity inside that window can be mislabeled.
- **`FactionKillBond` has no ship type**, so an on-foot combat-zone kill counts as a ship kill for mission progress.
- **Boxel Survey's survey log is not caught up** after a restart (its counter is not idempotent).
- **Exobiology and region data are a snapshot.** New species from a game update require a
  regeneration.

## 18. Platform support: Windows and Linux

Everything except a few features is platform-neutral Python and Tk. The platform-specific parts are
isolated in `platform_support.py` (plus the Windows branches in `autohonk.py` and
`screenshot_automation.py`), so a new platform touches few files.

| Concern | Windows | Linux |
|---|---|---|
| Journals and `Status.json` | EDMC's Journal directory setting (EDMC finds the default) | The same setting, but it has no default: it must point at `<prefix>/drive_c/users/<user>/Saved Games/Frontier Developments/Elite Dangerous`. An empty value means "nothing to scan" |
| Elite's bindings folder | `%LOCALAPPDATA%\Frontier Developments\Elite Dangerous\Options\Bindings` | The same path inside the Wine/Proton prefix (below) |
| Elite's screenshot folder | Shell "Pictures" known folder (`SHGetKnownFolderPath`), with OneDrive redirect handling | `Pictures/Frontier Developments/Elite Dangerous` inside the prefix, else `~/Pictures` |
| Screenshot event `Filename` | `\ED_Pictures\Screenshot_0001.bmp` | Same Windows-style string (Elite writes it even under Proton), so the file name is taken with `screenshot_naming.journal_basename`, not `os.path.basename` |
| Find the game window | `FindWindowW` (ctypes) | `xdotool search --name "^Elite - Dangerous"` |
| Is the game in the foreground | `win32gui.GetForegroundWindow` (bundled pywin32) | `xdotool getactivewindow getwindowname` |
| Send a key | `keybd_event` (ctypes for Auto-Honk, pywin32 for screenshots) | `xdotool` (XTEST); a hold is one `keydown`, `sleep`, `keyup` call (`platform_support.hold_key`) |
| Is a companion app running | `tasklist` | `pgrep -f` |
| Notification sound | `winsound.MessageBeep` | `canberra-gtk-play`, else `paplay` with the freedesktop theme file |
| Overlay | The built-in overlay or EDMCModernOverlay (a choice under Overlay Connection) | EDMCModernOverlay; same TCP protocol (the built-in overlay is Windows only) |
| Modal dialogs | `grab_set` works at once | `uikit.style.grab_when_visible`: X11 refuses a grab until the window is mapped, so it retries briefly |
| Plain `tk.Listbox` colors | `SystemWindow` / `SystemWindowText` | `white` / `black` (those names are Windows-only Tk colors) |
| Open a link in the browser (Report an issue, the Raven and Inara links) | `webbrowser.open` | `webbrowser.open` (the desktop's default browser, through `xdg-open` or similar; not yet checked from a Flatpak EDMC) |
| The OS line of a bug report | `platform_support.describe_system()`: Windows release and build | The same function: distro (`PRETTY_NAME`), `XDG_SESSION_TYPE`, and `Flatpak` when it is one |
| EDMC's log, for Copy diagnostics | The file handler of EDMC's logger, else `<app dir>/logs/EDMarketConnector-debug.log` | The same; a Flatpak EDMC keeps it under `~/.var/app/io.edcd.EDMarketConnector/data/EDMarketConnector/logs/` |
| Paste a ship loadout (Ship planner) | `tk` clipboard (`clipboard_get`) | The same; needs a clipboard owner on X11 or Wayland, and the box accepts a paste by hand if the button reports no text |
| Text symbols in the UI | Any | Only symbols every font has (`×`, `★`, `→`); `✕` is not used because some Linux fonts lack it |
| Settings notes | "This system: Windows - supported" | "This system: Linux, xdotool found / NOT found" (`platform_support.input_support_note`, `sound_support_note`) |

**Why the prefix**

- Elite is a Windows game. Under Steam Proton it sees a fake Windows profile stored at `.../steamapps/compatdata/359320/pfx/drive_c/users/steamuser/`, so its "Local AppData" and "Pictures" are ordinary Linux folders inside that prefix.
- `find_elite_prefix` looks in the usual Steam roots (native, `~/.steam` symlinks, Flatpak), follows `libraryfolders.vdf` to other drives, and also accepts a user-set path (the prefix, its `pfx` folder, or the `compatdata/<id>` folder).
- Lutris and plain Wine use the real username instead of `steamuser`, which `prefix_user_dir` handles.
- A bad override deliberately does *not* fall back to auto-detect, so a typo is visible instead of silently using a different prefix.

**Why xdotool through `subprocess`**

- It adds no Python dependency to EDMC's bundled environment, and it works on X11 and on XWayland, which is where a Proton game's window lives even on a Wayland desktop.
- The alternatives are worse fits: `python-xlib` needs installing into EDMC's Python, and `evdev`/`uinput` needs device permissions.
- Keys are sent with XTEST after focusing the window, because per-window synthetic events (`--window`) are ignored by most games. This mirrors Windows, where `keybd_event` goes to the foreground window.

**One process per hold**

- XWayland releases a synthetic (XTEST) key about a second after the `xdotool` process that pressed it exits.
- A separate `keydown` process, a Python `sleep`, then a `keyup` process therefore held the key for only about a second, and a honk needs several.
- `hold_key` runs `xdotool keydown K sleep N keyup K` as one process, which keeps the key down for the full time.

**Flatpak EDMC**

- The sandbox sees neither host programs nor the game's folders.
- `platform_support._tool_command` uses a sandbox copy of a tool when one exists, and otherwise runs `flatpak-spawn --host --directory=/ <tool>` after probing that the host has it (only a successful probe is cached).
- `pgrep` prefers the host, because the sandbox only sees its own processes.
- `--directory=/` is required: `flatpak-spawn` starts the host command in the sandbox's working directory, which for EDMC (`/app/edmarketconnector`) does not exist on the host.
- The user must grant `--talk-name=org.freedesktop.Flatpak` and filesystem access to the journals, Bindings and Pictures folders (see the Linux guide, Step 3).
- EDMCModernOverlay needs the same talk permission to start its overlay window, so a missing one makes the overlay's port answer while nothing is drawn.

**Failure behavior**

- Every wrapper returns `False`, `None` or an empty list, never raises.
- A missing `xdotool` produces a clear outcome ("xdotool isn't installed") rather than a silent no-op.
- `screenshot_automation.SUPPORTED` is false without it, so the timed-capture controls simply don't appear.

**Journal location**

- EDMC's own Journal directory setting is the source of truth for journals and `Status.json`.
- On Linux it usually has no default, so code that reads it treats an empty value as "nothing to scan" (a bare `Path("")` would silently scan the current directory, and `Path(None)` raises).
- `platform_support.journal_dir_advice` compares that setting with the prefix's `Saved Games/Frontier Developments/Elite Dangerous` (following symlinks) and returns a one-line hint, shown in Settings and logged at startup.
- It only advises: people legitimately link that folder elsewhere, so WFMT never changes EDMC's setting itself.

**Overlay**

- WFMT's overlay client is plain loopback TCP with newline-delimited JSON, so it is platform-neutral.
- EDMCModernOverlay runs a legacy listener on `127.0.0.1:5010` on both Windows and Linux, so no WFMT code changed.
- Plugin Group registration imports ModernOverlay's own module and is a silent no-op if it is absent.

**Case sensitivity**

- Windows ignores filename case and Linux does not.
- Elite writes `Status.json` (capital S), so code must ask for that exact name; a lowercase `status.json` works on Windows and silently fails on Linux.
- Journals match `Journal.*.log`.
- When adding file access, use the game's exact spelling.

**Windows-only behavior stays Windows-only.** OneDrive folder-redirection handling, the "Controlled
Folder Access" error text and the shell Pictures lookup are gated on Windows, so Linux users don't
see irrelevant advice.

**Settings labeling**

- Any feature that depends on the operating system shows a **Works on:** line in its Settings tab, colored green when this machine can run it and orange when it cannot (and why).
- The features are Auto-Honk, the Screenshots auto-timer and Thargoid capture, and the Inventory pickup sound. The Overlay Connection tab has no such line; its text says which overlay runs where.
- The BGS tab shows the Linux journal folder hint.
- Wording lives in one place, `platform_support.py`, and is unit-tested.

**Status**

- The Linux paths are unit-tested with mocked subprocess calls and temporary directories (`tests/test_platform_support.py`).
- What has been run on a real Elite install is recorded in `LINUX_TESTING.md`.
- Wayland without XWayland, and macOS, are unsupported for key simulation.

### 18.1 Platform notes for the session strip (`game_mode.py`, `session_credits.py`)

Both modules are platform-neutral by construction; what was checked, and why it holds on each system:

- **Journal source.** They read only journal events (`LoadGame`, `StartUp`, `Shutdown`) and EDMC's `state["Credits"]`, which EDMC supplies identically on Windows and Linux.
  - `StartUp` recovery reads the top of the current journal file with an explicit UTF-8 encoding and tolerates a missing or unreadable file.
- **`monitor.logfile`** is a `str` on some EDMC versions and a `pathlib.Path` on others.
  - It is imported lazily (so tests run without EDMC), then converted with `str()` before it is compared or written to JSON.
  - Powerplay's session store got the same conversion.
  - Journal-file identity is compared as the exact string EDMC gives, so Windows drive-letter paths and Linux Wine/Proton paths behave the same.
- **Saved state.** `session_credits.json` is written to a temp file then `os.replace`d (atomic on both), at most once per 30 seconds plus on start and stop; a read-only plugin folder only logs a warning.
  - Time stamps are UTC and parsed with `calendar.timegm`, not the local-time `mktime`, so a DST change or a different time zone cannot skew the hourly rate.
- **Display.** Number formatting is fixed (`f"{n:,}"`), not locale-dependent. The glyphs used are the ellipsis and ordinary punctuation.
  - Both labels are `panelkit.wrap_label`s inside one frame, so a long private-group name wraps instead of widening EDMC's window, which matters most on Linux where window managers resize more eagerly.
  - The credits line is shown on every mode.
- `session_merits.py`: the "Merits this session" line under it (`line_visible`; `ui._apply_panel_mode_visibility` calls `set_hidden` so the Powerplay page, whose Session and Cycle lines carry the merits, does not repeat it).
  - It keeps no data: the merits and the session start come from Powerplay's session record (`powerplay.controller.sessions.current`), and `powerplay._refresh_panel` and the feature dispatch (it runs after Powerplay in `load._FEATURES`) refresh it.
  - Hidden (`grid_remove`) until the session has a merit, and while the Powerplay mode is showing.
  - The rate is merits over the time from `started_at` (parsed with `calendar.timegm`, as UTC) to now.

### 18.2 Platform notes for Trade mode (`trade_*.py`)

Nothing in Trade is OS-specific.

- It reads journal events, EDMC's `state`, and `Market.json` from the journal folder (`config.get_str("journaldir")`, which on Linux is the Proton prefix's journal path), and makes HTTPS requests with `urllib`.
- All file reads use an explicit UTF-8 encoding (`errors="replace"` for journals), writes are temp-file-then-`os.replace`, and the carrier backfill ignores a missing folder.
- Background work is a plain daemon thread plus `queue`/polling; no thread touches Tk.

The parts that depend on the platform:

- The type-ahead popup (a borderless `Toplevel`, so it depends on the window manager for stacking and focus).
- The ◀ ▶ glyphs in the page arrows with Linux fonts.
- The backfill finding a Proton journal folder.

`LINUX_TESTING.md` section 6d holds the checks and their status.

### 18.3 Cross-platform review of the modules

The modules in `plugin/` and `plugin/uikit/` (about 365 files, about 97,000 lines) are held to the rules below, which keep
them free of Windows-only and Linux-only assumptions outside the `platform_support` branches. The checks are:

1. **A scan of every module** (AST and text) for platform signals: Win32 and `ctypes` use, `subprocess`, `winsound`, `os.startfile`, `sys.platform` branches, `.exe`/PowerShell/`xdotool` strings, Windows-only Tk color names, Windows paths and environment variables, `open()` without an explicit encoding, `strftime` directives that differ by platform, and file-name case.
   - Most modules have no platform signal at all (pure logic or plain Tk).
   - The ones that do have their platform-relevant code in `platform_support`, `inventory_sound`, `screenshot_automation`, and the key-injection, Settings and path code of `autohonk`, `screenshots`, `screenshot_convert`, `screenshot_naming`, `overlay`, `load`, `update` and the journal readers `codex_backfill`, `mining_journal_backfill` and `exploration_value`.
2. **Cross-cutting rules over all modules:**
   - Relative imports match the real file names exactly (a case mismatch passes on Windows and fails on Linux), and no two
     tracked paths differ only by case.
   - No `threading.Thread` target touches a Tk widget directly.
   - Every modal dialog uses `uikit.style.grab_when_visible` rather than `grab_set()`, which X11 can refuse before the window is mapped.
   - Every mouse-wheel binding handles both Windows deltas and X11 `Button-4/5`.
   - All generated file names avoid characters Windows rejects.
3. **Rules that follow from platform differences:**
   - Screenshot `Filename` values are Windows-style even under Proton, and `os.path.basename` doesn't split on a backslash on
     Linux, so the name is taken with `screenshot_naming.journal_basename` (tested).
   - The self-updater refuses a zip entry that would be written outside the plugin folder (`..`, an absolute path, another
     drive), on both systems.
   - BGS says in Settings, and logs, when no journal folder is set, rather than skipping silently.
   - Settings tabs for OS-dependent features state where they work and whether they can here (for example, Screenshots
     auto-capture works on Windows and on Linux with `xdotool`).

Not verifiable from a Windows development machine, and so covered only by `docs/LINUX_TESTING.md`:
real `xdotool` behavior, Tk popup stacking and focus under each Linux window manager, Proton prefix
layouts other than Steam's, and sound players.
