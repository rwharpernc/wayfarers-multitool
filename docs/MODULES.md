# Module index

Every Python module that ships in `plugin/`, grouped by feature, with a one-line description. For how the pieces fit
together, see [TECHNICAL.md](TECHNICAL.md) (section 2 is the repository layout); each feature's specification goes
deeper. Trade also has its own module table in [TRADE_TECH_SPEC.md](TRADE_TECH_SPEC.md).

Naming convention: a feature's modules share its prefix (`trade_*.py`), with a suffix for the role:

- `_panel`: the feature-module entry point in the main panel.
- `_window` or `_dialog`: a pop-out.
- `_state` or `_data`: JSON persistence.
- `_client`: a network lookup.
- No suffix: pure logic (no Tk, no EDMC) that the unit tests reach directly.

A module with a data file keeps it in the plugin folder beside the code. Those files are listed in `update.py`'s `_OWN_DATA_FILES` so an update never overwrites them.

`tests/test_docs_modules.py` fails if a module is added to `plugin/` without a row here, so this page stays complete.

Non-Python files in `plugin/`:

- `rare_goods.json`: the rare-goods table behind `rare_goods.py`.
- `colonization_costs.json`: the build-cost table behind `build_costs.py` (notice in THIRD-PARTY-NOTICES.md).
- `fonts/`: `SourceSans3-Regular.ttf` and its license file `SourceSans3-OFL.txt`, the bundled font of the built-in overlay (`overlay_fonts.py`); fonts a player adds go in the same folder.
- `icons/`: `timer_enabled.gif` and `timer_disabled.gif`, the Screenshots timer icons (`screenshots.py`).

## Entry point, shell and shared services

Spec: [TECHNICAL.md](TECHNICAL.md) sections 3 to 5 and 10

| Module | What it is |
|---|---|
| `fsd_data.py` | Frame shift drive base values for the Route Planner (optimal mass, most fuel per jump, fuel multiplier and power for 66 drives, the Guardian booster ranges and the 6x supercharge of the Mk II overcharge drive), generated from public ship-module data (source and license: see docs/ATTRIBUTIONS.md and THIRD-PARTY-NOTICES.md) |
| `spansh_courtesy.py` | The one polite way WFMT calls Spansh: at most two requests at once, spaced a quarter second apart, retried with growing waits when Spansh answers busy (429, 502, 503, 504, honoring Retry-After), a timeout retried only for a GET, and a pause of five minutes after five failures in a row. Every Spansh request goes through it (a test enforces that), and a caller answering a keystroke asks for no retries. Counters feed the diagnostics. See [SPANSH_USAGE.md](SPANSH_USAGE.md) |
| `star_index.py` | The optional local neutron-star index: the file format, the reader, the nearest-star query by grid cell, the name codec, status and the `wfmt_star_index_use` switch; no network |
| `star_index_build.py` | Builds the index from Spansh's neutron-star dump: a two-pass streaming build through temporary bucket files, written atomically, with progress and cancel |
| `star_index_download.py` | The user-started download of the dump: free-space check, resume, conditional request, size cap, one at a time; through the courtesy layer's streaming call |
| `star_index_job.py` | The worker thread that downloads, builds and then removes the dump, with `snapshot`, `cancel` and `delete_index` |
| `star_index_settings.py` | The "Local star index" group on the Online lookups page, with the pure status text and button states |
| `spansh_exact.py` | The Route Planner's network code: the system lookup, and the request to Spansh's exact plotter (`/api/generic/route`) with its answer, built on `spansh_planners.fetch_job` |
| `route_planner.py` | The Route Planner's logic (no Tk, no network): the ship's numbers from the journal's Loadout (`ShipParams`, `ShipInfo`, with the drive from `fsd_data`), the form Spansh's exact plotter takes, its answer as `Leg`s, and a `Route` that follows arrivals, finds the next supercharge and refuel, and lists what is left to copy |
| `route_planner_panel.py` | The Route Planner's owner: the Route Planner section of the Exploration panel (the Plot button, the auto-copy tickbox and the next-jump line), the Loadout, arrival (with the system address) and Status.json (cargo) feeds, arrivals along the route, copying the next system to the clipboard, making an expedition from the route, and redrawing the Route overlay |
| `route_secondary.py` | The Route Planner's check for a neutron star that is probably a secondary star: the name rule over a system's stars (`neutron_is_secondary`), and `SecondaryChecker`, which asks Spansh for the stars of the next neutron stops in the background and hands back the answers |
| `route_planner_state.py` | The Route Planner's plotted route kept in `route_planner_route.json` (`commander_data.py`, one route per commander) so it survives a restart: the route as plain data, read back with every damaged route dropped, and `RouteStore` |
| `route_planner_window.py` | The Route Planner window: the ship block (name, drive, booster, optimal mass, supercharge, cargo), source and destination, the four options and the algorithm, the exact-plotter call on a worker thread with a progress bar, the table of every jump, the copy buttons, **Start expedition** (makes an expedition from the route, starts it and its Expedition Log run) and **Review expedition** (opens the Expedition window on it), and the status line that says what was sent to the Route overlay and copied |
| `explore_dashboard.py` | The Exploration Dashboard's owner: the folding Dashboard section of the Exploration panel (the Dashboard button and the Exploration Value lines), the snapshot of the survey, exobiology view, Status.json, expedition and route it hands the window, the refresh on journal events and Status.json, and the two overlay switches (`GROUPS`: the id prefixes of the exploration and exobiology cards) |
| `explore_dashboard_data.py` | What the dashboard shows, as plain rows and fields (no Tk): system tiles and fields, the bodies table and one body's details, the worth-mapping, life and found-by-others lists, the genus table with odds, rewards and distances, the tracked plants with distance and direction, the expedition fields, and `perspective` (orbit or ground from Status.json) |
| `explore_dashboard_window.py` | The Exploration Dashboard window on the shared window kit: Overview, Orbit, Surface and Exploration tabs, the header buttons that hide and show the overlay groups, and the switch to Surface on landing and back to Orbit on lift-off |
| `data_backup.py` | Back up my data: zips the data files the updater protects (and the mining run archive) into a dated archive in a folder the user picks, leaving out the Raven Colonial keys, the Discord webhook links, the Codex cache and the local star index, with a `backup-info.json`; refuses a folder inside the plugin folder; checks and stages a restore that `load.py` applies at the next start (keeping the replaced files in `backups/`); the optional automatic backup at start-up and before an update, pruned to the newest ten; the Settings → General → Backup tab calls it |
| `commander_data.py` | Per-commander JSON files: a separate payload per commander in one file, the first commander seen claiming data saved before it was per commander |
| `journal_files.py` | Shared start-up catch-up helpers: the journal folder, files changed since a moment, a filtered event reader, and `read_cargo_file`, the ship's hold from the game's `Cargo.json` beside the journals (nothing when the file is missing or describes the SRV) |
| `__init__.py` | The package marker; holds `__version__`, the one place the version number lives (mirrored in `package.json`) |
| `http_identity.py` | The User-Agent every web request sends, so services can tell which WFMT feature is calling |
| `issue_report.py` | The Settings → General → Help **Report an issue** button: builds the prefilled GitHub bug-report address (versions and OS, nothing personal) and opens it in the browser; also **Copy diagnostics**, which puts the versions and the newest WFMT lines of EDMC's log (commander name and home folder redacted) on the clipboard |
| `load.py` | The EDMC entry point: `plugin_start3`, `plugin_app`, `journal_entry`, `dashboard_entry`, `plugin_stop`, the one-time overlay reset, and forwarding to every feature |
| `notifier.py` | A tiny subscribe/notify helper for where one module's data changes and others must redraw |
| `overlay.py` | The one shared overlay client (EDMCModernOverlay over a local TCP port), its Plugin Group registration and group offsets |
| `overlay_layout.py` | Where overlay displays go, the same on any screen: how big a pixel is on the overlay's canvas (positions are screen fractions, sizes are pixels), nine anchor spots plus pixel offsets, the overlay's right-edge clamp, the overlay's clamp and the offset that carries a display past it, a client wrapper that moves a display, and `on_canvas`, which rejects an exact position that would leave a display off the canvas; pure, no Tk |
| `overlay_style.py` | The shared overlay look: six color schemes (color roles, plus one series color for each tracked genus), the panel opacity choice, the text sizes with per-size character width and line height estimates (each width padded by 10%, plus a stricter `measured_width` for cards of capitals and catalog names), padding and line spacing; cards are sized from these so larger text never wraps; pure, no Tk |
| `overlay_appearance.py` | The saved color scheme and text size (Default, Larger), the fixed padding and line spacing, `current_look()` which every overlay draws with, and the Overlays > Appearance Settings tab with its sample |
| `overlay_fonts.py` | The overlay fonts: WFMT's own fonts folder (`plugin/fonts`: the bundled Source Sans 3 and any font file the player adds, kept through updates) for the built-in overlay, and for EDMCModernOverlay the list in its `fonts` folder (adds a font file and puts the pick first in its `preferred_fonts.txt`, keeping a backup); no Tk |
| `overlay_native.py` | The built-in overlay's switch and glue: the Overlay choice (EDMCModernOverlay or WFMT's own window, off until chosen, Windows only), the scene `overlay.OverlayClient` feeds when it is on, the group prefixes, the screen placement reads from the game window, its font (`wfmt_overlay_builtin_font` in WFMT's `fonts` folder) and text measurer, the keep-showing option, `snapshot` for screenshots and the status line; no drawing |
| `overlay_scene.py` | What the built-in overlay has on the screen: the payloads the overlay features send (text, rect, circle, vect, each with an id and a ttl) kept with when they run out, in drawing order with text always above panels; no Tk, no Windows |
| `overlay_raster.py` | Draws the scene as one transparent Pillow picture the size of the game window (a group is placed at its top left item's canvas position and the distances inside it are logical pixels times the display scaling), with the font, color parsing and the shapes; no Windows |
| `overlay_window.py` | The built-in overlay window (Windows): a transparent, click-through, topmost layered window on a thread inside EDMC that follows Elite's window, shows only while Elite (or a Windows capture tool) has the focus, puts itself back above the game every half second and follows a change of font, so no overlay window can outlive EDMC |
| `overlay_processes.py` | Counts the EDMCModernOverlay windows running (a launcher and its child are one window; psutil, `/proc` or PowerShell) so Check connection and Copy diagnostics can say when a second one is drawing every card twice; report only, WFMT never starts or stops the overlay |
| `overlay_visibility.py` | Hide every WFMT overlay for a while: the line in the WFMT panel (click to hide or show) and the Overlays → Hide overlays Settings tab (a button); the switch itself is `overlay.set_all_hidden`, and the keyboard shortcut and chat command are in `shortcuts.py` |
| `elite_keybinds.py` | Reads the keyboard bindings out of Elite's binds file (key and modifiers for each control) and says which match a combination, so a WFMT shortcut can be checked against the game's own controls (pure parsing; `autohonk.py` finds the file) |
| `shortcut_actions.py` | The shortcut list and its pure logic: the six actions (Mark center, Mark border, Rig placed, radar range, Live window, hide overlays), the Ctrl+Alt+Shift key choices, the Windows key codes, the `!wf` chat parser, the freshness check for a journal line and the clash text |
| `shortcuts.py` | The shortcuts' runtime and Settings page (General → Shortcuts): the Windows global key combinations on their own thread, the chat commands read from the journal's `SendText` event, running each action on the Tk thread and the optional sound |
| `overlay_placement.py` | Global overlay placement: reads the real window size, mode and display scaling from EDMCModernOverlay's log (falling back to Elite's `DisplaySettings.xml` and Windows' scaling, then to the window size alone from the overlay's log when that file cannot be read), keeps every display's saved spot, places a card from the size it is drawn at (`client_for_measured`), and the Overlay Placement Settings tab with its preview and the drag-and-drop layout editor |
| `overlay_grid.py` | The drag-and-drop layout editor on the Overlay Placement tab: a to-scale picture of the screen with a grid and a box for every display; dropping a box writes the spot and offset (snapping flush to an edge or the center line, and to the grid); the conversions between a dropped box and a placement are pure |
| `panelkit.py` | Shared Tk helpers for the main panel and Settings: wrapping labels (a `min_wrap` per label, so a section can wrap at the window's width without ever widening a narrow one), separators, toggles, tooltips (`uikit/tooltip.py`'s `add_tooltip`, re-exported), collapsible sections, page arrows, theming, `fit_entry` / `fit_button_row`, which cap an entry box and a row of buttons in pixels whatever the font, and `flow_buttons`, which wraps a row of buttons onto a second line before it passes the width EDMC's window is held at |
| `platform_support.py` | Windows/Linux differences in one place: Elite's folders, key presses (`xdotool`), host programs under Flatpak, the primary display's size from the operating system (`primary_display_size`: `GetDeviceCaps` on Windows, `xrandr` on Linux), "Works on" notes |
| `restore.py` | Names the last commander from the newest journal and tells every feature when EDMC starts without the game running, so nothing waits for a login |
| `settings_scroll.py` | Wraps each Settings page in a height-capped scrolling frame so a long page never pushes the OK button off the screen |
| `ui.py` | The main panel, mode buttons, panel height fitting and the Settings tabs; orchestration only |
| `update.py` | The self-updater: checks GitHub Releases, downloads, stages over the install, and protects per-commander data files (`_OWN_DATA_FILES`) |

## Status lines under the mode buttons

| Module | What it is |
|---|---|
| `game_mode.py` | The "You are in Solo / Open / Private Group" line under the mode buttons |
| `session_merits.py` | The "Merits this session" line under the credits line (Powerplay merits since login, with a per-hour rate; hidden on the Powerplay page, which shows them itself) |
| `session_credits.py` | The "Credits this session" line (earned or lost since login, with a per-hour rate); clicking it opens the Credits Ledger |
| `credits_ledger.py` | The Credits Ledger feature's entry point: folds live income events into the commander's book, rebuilds the past from the journals once on a worker thread, reads the newest `Statistics` event, opens the window |
| `income_ledger.py` | The Credits Ledger's data: income per commander by activity (trade profit, exploration data, exobiology data, mission rewards, bounties and bonds) and by day, counted without double counting; pure, no Tk |
| `income_catchup.py` | Reads a commander's income events from every journal file, for the ledger's one-time rebuild |
| `legacy_names.py` | One-time renames at start-up of saved names from before British spellings were replaced: the `colonisation_*.json` files, the `wfmt_colonisation_*` settings and overlay slot keys, and the field names `tons` and `analyzed` inside saved JSON. Idempotent; runs after a pending restore |
| `ledger_window.py` | The Credits Ledger window: Income (today, 7 days, 30 days, all), By day, and Lifetime tabs |
| `lifetime_stats.py` | The game's lifetime totals (the `Statistics` event) for the ledger's Lifetime tab: parsing, the grouped rows, and finding each commander's newest event in the journals |

## Powerplay

Spec: [POWERPLAY_TECH_SPEC.md](POWERPLAY_TECH_SPEC.md)

| Module | What it is |
|---|---|
| `formulas.py` | Merit to Control Point conversion for Powerplay activities |
| `feature_dispatch.py` | Hands each journal event to every feature in turn without letting one feature's failure stop the others |
| `powerplay.py` | Powerplay mode: pledged Power, merits (the Session and Cycle tally lines, merged into one Cycle pair when they say the same), the current system's Powerplay context and activity classification |
| `powerplay_backfill.py` | Rebuilds the per-system ledger, and the megaship scans, from journal files for cycles played while EDMC was closed |
| `powerplay_clipboard.py` | Formats the Sessions window's "Copy Progress" text, and builds the per-system progress rows (`progress_rows`) that Copy Progress and the Discord copy and post share |
| `powerplay_discord.py` | Powerplay progress as Discord messages: a linked line for each system with merits and estimated CP, and the cycle's total |
| `powerplay_control_lookup.py` | Spansh lookup of which Power controls a system |
| `megaship_scans.py` | Megaship scans for the Powerplay cycle: reads the journal (`DataScanned` uplink, `SupercruiseDestinationDrop`, the FSS megaship list, `PowerplayMerits`) to say which megaship was scanned, where, and what it earned; no Tk |
| `powerplay_ledger.py` | The per-commander, per-system, per-cycle ledger of what you did and how each system moved, and the megaships scanned each cycle (`live_view()` feeds the panel's cycle tally) |
| `powerplay_megaships_tab.py` | The Megaships tab of the Powerplay Sessions window: one row per megaship scanned, cycle by cycle |
| `powerplay_state.py` | JSON persistence for that ledger |
| `powerplay_systems_tab.py` | The Systems tab of the Powerplay Sessions window |
| `powerplay_window.py` | The Powerplay Sessions window (current session, systems, cycles, daily, megaships, history) |
| `powerplay_overlay.py` | The Powerplay overlay card: your Power, rank, merits and the cycle's merits, the system's state and holder, what merits earned here count as, and the merits and estimated Control Points earned here this session by type; shown only in a system with a Powerplay state; the pure `build_card`, the controller's `overlay_info`, Settings → Overlays → Powerplay, one Overlay Placement slot |
| `rare_goods.py` | Finds the nearest rare commodities to the current system (data in `rare_goods.json`) |
| `rare_goods_window.py` | The Rare Goods Finder window |
| `session.py` | Merit tallies for the current game login |
| `store.py` | JSON persistence for Powerplay session history; every session names its commander, and the history limit and views are per commander |

## Exploration

Spec: [ORGANIC_SCANNING_TECH_SPEC.md](ORGANIC_SCANNING_TECH_SPEC.md), [SCREENSHOTS_AND_INPUT_TECH_SPEC.md](SCREENSHOTS_AND_INPUT_TECH_SPEC.md) (Auto-Honk), [TECHNICAL.md](TECHNICAL.md) section 12

| Module | What it is |
|---|---|
| `autohonk.py` | Auto-Honk: holds the Discovery Scanner key on arrival in a system |
| `catchup_status.py` | The line in the WFMT panel that names the journal catch-ups still running (Powerplay, BGS, Codex), shown only once one has run for 1.5 seconds so quick reads never flash it |
| `canonn_poi_data.py` | Canonn's published Thargoid and Guardian site lists, fetched on demand |
| `canonn_poi_panel.py` | The Canonn half of POI Reference: its lookup, cache, result line and Settings (Thargoid or Guardian sites) |
| `codex_hints.py` | Where to look for a missing codex entry (from the species and color data the Bio predictions use) and how far along each type of entry is; no Tk, no network |
| `codex_backfill.py` | Journal readers for Codex Completionist, per commander: the full-history scan behind the Backfill Journals action and the one-time rebuild, and `scan_since` for the start-up catch-up |
| `codex_catalog.py` | The catalog of every codex entry, for the "Not found" tab |
| `codex_completionist.py` | Pure logic for the lifetime tally of everything scanned, with the `last_event_at` watermark |
| `codex_completionist_panel.py` | The Codex Completionist section of Exploration |
| `codex_completionist_state.py` | JSON persistence for the tally, one per commander (a tally in the pre-per-commander shape, if one is found, is kept untouched, then removed after 60 days) |
| `codex_completionist_window.py` | The Codex Completionist detail window (found and not found) |
| `discovery.py` | Discovery Alerts: overlay alerts for never-before-discovered systems and bodies, plus the Neutron Star / White Dwarf buttons |
| `elw_rarity_spansh.py` | Spansh count of known Earth-like worlds around a system |
| `exploration_progress.py` | Bodies scanned against the honk's body count, and what the last exploration and organic data sales paid |
| `exploration_value.py` | Estimated scan payout for the last body scanned, the system's age and region, system scan progress and the last data sales. It has no section of its own: its lines are drawn inside the Dashboard section (`build_rows`), and it keeps its Settings tab |
| `gec_poi_edastro.py` | edastro.com's Galactic Exploration Catalog: downloads the full list once and finds the nearest point of interest locally (their own nearest endpoint does not use the position) |
| `gec_poi_panel.py` | The edastro GEC half of POI Reference: its lookup, result line and Settings |
| `poi_reference_panel.py` | The POI Reference section: one Find POI runs the GEC and Canonn lookups together and copies the nearer system; owns the buttons and joins the two Settings pages |
| `materials_data.py` | The 146 engineering materials with type and grade: 137 from a public material list and nine Thargoid-war and chip materials added by hand (source and license: see docs/ATTRIBUTIONS.md and THIRD-PARTY-NOTICES.md) |
| `blueprints_data.py` | 1,176 engineering blueprints (type, name, grade, engineers, ingredients with counts, effects) and where 262 ingredients are found, trimmed from a public blueprint table and corrected (five recipes, seven synthesis rows, the Colonia engineers' upgrades); source and license: see docs/ATTRIBUTIONS.md and THIRD-PARTY-NOTICES.md |
| `blueprints.py` | Blueprints as objects: browse by type, name and grade, search, ingredient kinds (ship material, Odyssey micro-resource, commodity) matched to the keys the counts use, and a check that every counted ingredient matches; no Tk |
| `blueprint_wishlist.py` | The commander's blueprint wishlist (blueprints and a number of crafts each), kept per commander in `blueprint_wishlist.json`, with limits, and `add_many` to put a whole ship plan on it at once, all or nothing; no Tk |
| `blueprint_needs.py` | What a blueprint or the whole wishlist needs against what is held (ship materials and the Odyssey ship locker), ready in list order, and the combined shopping list; no Tk |
| `journal_blueprints.py` | Generated by `scripts/gen_journal_blueprints.py`: how the journal names an engineering blueprint (`FSD_LongRange`) and an experimental effect (`special_fsd_heavy`) and what the blueprint table calls them, per module type |
| `ship_links.py` | Links that carry a ship loadout: reads a pasted Coriolis import link or EDSY `#/I=` link (gzip and base64 of the `Loadout` JSON) and makes one for a build; refuses the sites' own-code and short links with the reason; no network, no Tk |
| `stored_modules.py` | The modules a commander has in storage and where, from the Module Storage journal events (a snapshot, then store, mass store and retrieve), per commander (`stored_modules.json`), with a start-up catch-up from the newest journals, and `match_plan`, which says which of a Ship planner build's modules are in storage |
| `ship_plan.py` | The ship engineering planner: reads a pasted ship loadout (SLEF from EDSY or Coriolis, a Coriolis or EDSY import link, or a journal `Loadout` line), places each engineered module in the blueprint table, and adds up the grades and experimental effects it takes, optionally minus what the current ship already has; no Tk |
| `odyssey_upgrade_plan.py` | The Odyssey upgrade planner: what it costs to take a suit or weapon from one class to another (materials from the blueprint table, credits from a per-item unit seen in real journals) and fit up to four modifications; no Tk |
| `odyssey_gear.py` | The Odyssey suits and weapons the commander owns, from the journal's loadout events: item, class now and fitted modifications, for the Upgrade planner to fill in; read on demand, nothing stored |
| `odyssey_plan_tab.py` | The Upgrade planner tab of the Engineering window: pick the item (or read your own gear), classes and modifications, see the steps and credits, and add them to the wishlist |
| `missions_overlay.py` | The Missions card on the in-game overlay: the missions for this system and the next jump first, the rest by urgency, capped to a row limit; pure layout plus drawing and its Settings tab |
| `ship_current.py` | The ship being flown, from the newest `Loadout` event in the newest journals, read on demand for the Ship planner to subtract; nothing stored |
| `ship_plan_tab.py` | The Ship planner tab of the Engineering window: paste, read, the module table, rolls per grade, an In storage column, Add plan to wishlist, and copy or open the selected build as a Coriolis or EDSY link |
| `blueprints_extra.py` | Hand-added entries the blueprint table lacks: Yi Shen's unlock, which asks for three sets of items handed to the other Colonia on-foot engineers, with its sources |
| `engineers_data.py` | Where each of the 38 engineers is (system, base, coordinates, planet) and how to find, be invited by and unlock them, permit and on-foot flag (source and license: see docs/ATTRIBUTIONS.md and THIRD-PARTY-NOTICES.md) |
| `engineers.py` | The commander's standing with each engineer (Known, Invited, Unlocked, rank), from the journal's `EngineerProgress`, kept per commander in `engineers.json`; matches the journal's names (with a nickname in quotes) to the table's; also `info(name)` (where an engineer is and how to unlock them, and whether the region is the Bubble or Colonia), the ship engineers' grade thresholds and the one known quirk; no Tk |
| `blueprints_window.py` | The Engineering window: browse and search blueprints, see one craft's ingredients against what you hold and where each is found, add to the wishlist, the wishlist with a combined shopping list and who can do each entry, and an Engineers tab (standing, what they offer, where they are, what unlocking takes, with the details of the one you select, and a Bubble / Colonia / Both filter) and the Ship planner and Upgrade planner tabs |
| `material_traders.py` | Finding a material trader: the closest Raw, Manufactured or Encoded traders to a system from Spansh's station search, with the pad filter, a two-minute cache and the place described; the search is passed in, so it is tested offline; no Tk |
| `materials.py` | The commander's Raw, Manufactured and Encoded materials, kept per commander in `materials.json`: the login list, every event that changes a count, the grade limits (300 to 100), EDMC's totals for a mid-session start, and unknown materials; no Tk |
| `materials_panel.py` | The Materials row in Operations mode: pieces held of each type, the last change, what is at the limit, and the button that opens the window |
| `material_trader_window.py` | The Material trader window: pick a type, distance and pad, search from your system or another, see what you hold of that type by grade, and the closest traders from Spansh; the lookup runs on a worker thread |
| `materials_window.py` | The Materials window: search, type and grade filters, "only at the limit", and a sortable table of held, limit and room |
| `expedition.py` | Expedition planner, the pure part: named expeditions of ordered stops with notes, one active at a time, stops ticked off from arrivals with jump and distance totals, per-stop survey counts (bodies scanned, first discoveries, mapped) from the scan events, nearest-neighbor ordering, CSV and text export, kept per commander in `expeditions.json`; no Tk |
| `expedition_hub.py` | The Expedition window that holds the Plan, Route and Log tabs: the panels register how to build their tab and open it here; each tab is built when first shown; one saved geometry |
| `expedition_window.py` | The Expedition window: pick, create, start, pause, finish, reset and delete expeditions; a table of stops with the next one marked and the distance from you; an editor with a Here button; import from the plotted route or a CSV, locate and reorder by distance through EDSM, copy and export |
| `system_names.py` | Where system-name suggestions come from: the systems you have been in this session, names other parts of WFMT register (expedition stops, notes), and, only when Settings → Window → *Suggest system names from Spansh while typing* is ticked, Spansh's system-name search (kept in memory for the session); no Tk |
| `commodity_autocomplete.py` | `attach(entry, var, preferred)`: the same suggestion list for any box that takes a commodity name (the Hotspot form's Contains, the price finder, the Settings target); nothing is fetched |
| `system_autocomplete.py` | `attach(entry, var)`: a list of system-name suggestions under any text box as you type (Down and Up, Enter or a click to take one, Escape to close; Enter with nothing highlighted still does what the box did); the Spansh call runs on a worker thread |
| `spansh_planners.py` | Spansh's Road to Riches and Expressway to Exomastery planners (and the job polling the Route Planner's exact plotter shares): the form sent, the job polled to its end, and each answer turned into expedition stops (system, the best body, a note of what is worth it, position); opt-in, only when Plot is pressed; no Tk |
| `expedition_plan_dialog.py` | The window behind the Expedition window's **Road to Riches** and **Exomastery** buttons: start, optional end, jump range, radius, results, distance and least worth, then **Plot** (worker thread, progress from Spansh, **Cancel**); its answer is handed back to become an expedition |
| `expedition_panel.py` | The Expedition row in Exploration mode: the tracked expedition's stops done, jumps, light-years and time, the next stop with its distance and note, the stop just reached, what was found, the Log's extra figures, Copy Next and copy-on-arrival (expeditions are started and stopped in the Expedition window); feeds the planner from the journal |
| `expedition_link.py` | Keeps a planned expedition and its Expedition Log run in step: one Start, Pause and Stop for both, and the expedition shows the run's clock (paused time excluded); no Tk |
| `expedition_log.py` | Expedition Log model: an archive of the commander's exploration expeditions, per commander (`expedition_log.json`): `Run` (name, start and end, start and end location, ships, notes, totals), `Tally` (counts journal events: jumps and light-years, systems, bodies scanned, first discoveries, mapped, exploration data sold, scans' estimated value; samples, species analyzed, first footfalls, exobiology sold, species' estimated value), `LogBook` (start, stop, resume, reset, delete, edit with date checks, save), `rescan` (the totals worked out again from the commander's journals between start and end), and the summary and CSV text |
| `expedition_log_panel.py` | The Expedition Log's journal hook: hooks the Expedition section up to the Log (`build_into`, no buttons) and words the Log's extra figures; remembers the system and ship so a new expedition starts with them |
| `expedition_log_window.py` | The Expedition Log window: the archive table, what each expedition recorded, an editor for its details, and Start, Stop, Resume, Reset, Rescan, Delete, Copy summary and Export CSV |
| `expedition_log_overlay.py` | Expedition Log overlay: one card with the running expedition's exploration and exobiology totals and what was earned; Settings → Overlays → Expedition Log, one Overlay Placement slot |
| `notes_data.py` | The commander's notes on a system or body, kept per commander in `notes.json`: validation and limits, search, and an add, change and delete that save at once; no Tk |
| `notes_panel.py` | The Notes row in Exploration mode: how many notes the system you are in has and the newest, a one-line quick add, and the button that opens the window |
| `notes_window.py` | The Notes window: search, a list of every note, and an editor with a Here button for the system and body you are at |
| `surface_marks.py` | The commander's named surface marks (body, latitude, longitude) and compass target, kept per commander in `surface_marks.json`: validation and limits, lookup by body, add, change, delete; no Tk |
| `surface_compass.py` | Surface Compass: points an overlay arrow, name and distance at the nearest hotspot or a chosen mark on the body you are on; the Compass section in Exploration mode (MARK, TARGET, MARKS), its Settings tab, and a one-time copy of the settings of a Mining waypoint overlay, if it finds them |
| `surface_marks_window.py` | The Marks window: every mark with its distance from here, the compass target, and an editor with a Here button |
| `neutron_finder.py` | Spansh search for the nearest neutron-star or white-dwarf primary |
| `notable.py` | Notable Bodies: the overlay banners, queueing and Settings page |
| `notable_rules.py` | The 15 rules deciding which scanned bodies are worth an alert |
| `organic_region_data.py` | Galactic region and Guardian-nebula proximity from a system's coordinates |
| `organic_scan.py` | Pure logic for exobiology tracking: species prediction, scan stages and distances, the per-body view (`BodyView`, `GenusView`, value ranges and even-share odds, `Waypoint`) and the codex-name to genus lookup |
| `organic_scan_panel.py` | The Organic Scanning section of Exploration; also builds the widget-free per-body view (`overlay_view`) that the Exobiology cards read: genera, predicted and confirmed species, sample positions, first footfall, ship and SRV, and the plants identified |
| `organic_scan_state.py` | JSON persistence for per-body exobiology progress (genera, sample stage and positions, color variant, first footfall, plants identified) |
| `organic_species_data.py` | Genus and species reference data (thresholds, values) |
| `organic_variant_data.py` | Exobiology color variants: which variant a species takes, from the class of the star its body orbits or a surface material (generated by `scripts/gen_organic_variants.py`; source and license: see docs/ATTRIBUTIONS.md and THIRD-PARTY-NOTICES.md); used by `organic_scan.predict_variants` |

## Boxel Survey

Spec: [BOXEL_SURVEY_TECH_SPEC.md](BOXEL_SURVEY_TECH_SPEC.md)

| Module | What it is |
|---|---|
| `boxel.py` | Procedural system-name parsing and boxel sequence walking |
| `boxel_state.py` | JSON persistence for the Boxel Survey walker |
| `boxel_survey.py` | The Boxel Survey section: walks a boxel's sequence and copies the next target |
| `boxel_walker.py` | The "advance on jump" state machine |
| `edsm_client.py` | EDSM client for nearby-system queries, whether systems are known (`systems_known`), their positions, and the main star of each (`primary_star_types`, for the Route Planner's white dwarf marking) |
| `region_sweep_edsm_skip.py` | Pure logic for Region Sweep's *Skip systems already visited by anyone (EDSM)*: steps past candidates a lookup says EDSM knows (capped at 20 per advance), keeps the candidate when the lookup fails, and caches answers for the session |
| `region_sweep_panel.py` | Region Sweep, Boxel Survey's second sub-mode |
| `region_sweep_queue.py` | Pure logic for the Region Sweep cube queue |
| `region_sweep_spansh.py` | Spansh systems typeahead used by Region Sweep |
| `undiscovered_nearby.py` | Random's source: Spansh's nearest systems to a position, filtered to those with no scan data and not visited, plus the in-memory cache that lets repeat clicks skip the search; no Tk |
| `region_sweep_state.py` | JSON persistence for the Region Sweep queue |
| `organic_catchup.py` | Catching Organic Scanning's saved progress up from the last 14 days of journals (samples taken with EDMC closed): reading the `ScanOrganic` events, naming their bodies, and raising the saved stages without lowering any |
| `survey_catchup.py` | Catching the survey log up from the last 14 days of journals (scans made with EDMC closed): reading them, and replaying them without counting anything twice |
| `survey_log.py` | The notable-finds log, one per commander, and its JSON persistence |
| `visited_systems.py` | JSON persistence for the per-commander visited-systems log, and the start-up catch-up of jumps made while EDMC was closed |
| `waypoint_route.py` | Pure logic for Waypoint Route, Boxel Survey's third sub-mode |
| `waypoint_route_panel.py` | The Waypoint Route section |
| `waypoint_route_state.py` | JSON persistence for Waypoint Route |

## Mining

Spec: [MINING_TECH_SPEC.md](MINING_TECH_SPEC.md)

| Module | What it is |
|---|---|
| `mining_alerts.py` | Mining alerts for the Flight Alerts card and the Space Mining page: reads a prospected rock (a core asteroid's mineral, the commodity chosen in Settings and its percent), the exact limpets aboard from EDMC's cargo, and when the limpet and hold alerts apply; no Tk, no network |
| `mining_missions.py` | What the active mining missions still need against the hold, as the Space Mining page's "Mission needs" lines; no Tk, no network |
| `mining_bearing.py` | Great-circle distance, bearing and arrow maths, for the Surface Compass and the coverage map |
| `mining_body_survey.py` | The landable bodies the journal has shown in the current system (scans and mining-location signals), which the Surface Mining Book lists and the ground-type rates are worked from |
| `mining_coverage.py` | Where the SRV's scanner has driven, per body, one map per commander; the mining locations the commander marked (center and border, radius, how much of the edge is driven) |
| `mining_coverage_render.py` | Draws that coverage as a small map, and the live window's radar centered on the Rhino (PIL, no Tk) |
| `mining_depletion.py` | Dates a Depleted mark and, if the commander sets a refill time (the default is unknown), takes it off when due (7 days after a look at a still-empty deposit); the status line the Surface Mining Book shows |
| `mining_deposit.py` | Estimates tons left in a recorded hotspot deposit |
| `mining_ground.py` | Ground type of a body and your own base rates of deposits on it |
| `mining_history.py` | The commander's mining runs, read from their journals in the background and saved per commander (`mining_history.json`); the newest journal is read afresh and never saved; no Tk |
| `mining_history_data.py` | The Mining History window's tiles, fields and tables, worked out from the saved runs; no Tk |
| `mining_live_window.py` | The Mining live window (the Live button on each Mining page): on the Surface page a radar centered on the Rhino, the panel's lines and the Mark center, Mark border, Add hotspot and Import/export controls; on the Space page the panel's lines and the lookups; drawn by the same code as the panel, no overlay needed |
| `mining_history_window.py` | The Mining History window (the Dashboard button in Mining mode) |
| `mining_market.py` | The open station market set against the galactic average: a line for each commodity the run refined that the station buys; no network |
| `mining_hotspot_dialog.py` | The shared Add/Edit Hotspot form (on `uikit/form.py`), with `build_hotspot`, which turns the typed text into a hotspot and writes the material in the one spelling |
| `mining_hotspot_finder_dialog.py` | The Find Nearby Hotspots window (Spansh; a sortable results table) |
| `mining_hotspot_import_export.py` | JSON import and export of the hotspot list, and the Import and Export window |
| `mining_hotspot_settings.py` | The hotspot list section of Mining's Settings tab |
| `mining_hotspots.py` | The saved surface-hotspot list, one per commander |
| `mining_journal_backfill.py` | Replays the current journal when EDMC starts mid-session |
| `mining_bodies_data.py` | The bodies the Rhino mined on, read from the journals for the Surface Mining Book: mining locations a DSS scan found, the planet class, and tons refined with a Rhino; no Tk |
| `mining_ring_book.py` | The Space Mining Book window (the Book button on the Space Mining page): every ring with hotspots or mining runs in the journals (and ones you noted, starred or added), with hotspots by mineral, class, reserve level, tons mined, a note and a favorite |
| `mining_names.py` | One spelling for a mineral or commodity name in the mining books and pages (`Tritium`, not `tritium`; the internal and short forms of Low Temp. Diamonds and Void Opal mapped to one name); no Tk |
| `mining_rings.py` | The commander's notes, favorites and rings added by hand for the Space Mining Book, kept in `mining_ring_notes.json` (`commander_data.py`, one record per commander) |
| `mining_rings_data.py` | The Space Mining Book's data: ring records from the journal, joined with the mining runs and the notes into rows; no Tk |
| `mining_ledger.py` | The Surface Mining Book window (bodies, hotspots, detail card with map) |
| `mining_ledger_data.py` | The data side of the Surface Mining Book: grouping and map projection |
| `mining_live_position.py` | Live surface position and heading from `Status.json` |
| `mining_location.py` | The current system name for Mining |
| `mining_market_research.py` | Market Research logic: the commodities worth checking in a system (from your own records) and the markets that buy them |
| `mining_market_research_dialog.py` | The Market Research window (Spansh, opened from the Surface Mining Book): a table grouped by commodity, with a copyable report |
| `mining_methods.py` | Which mining method suits each commodity |
| `mining_overlay.py` | The mining stats overlay |
| `mining_pages.py` | Mining's page order |
| `mining_panel.py` | Mining mode's entry point: page chrome, Settings tab, event dispatch |
| `mining_price_finder_dialog.py` | The Find Best Price window (Spansh; a sortable results table), also opened from Trade's Price finder |
| `mining_rate.py` | The rate now (tons per hour over the last minute) and the run average (tons over mining time, leaving out long gaps), with the text both the panel and the overlay show; no Tk |
| `mining_targets.py` | The target commodities typed in Settings: parsing, a percentage per name, the problems found; no Tk |
| `mining_render.py` | Draws each Mining page's content |
| `mining_reserve_lookup_dialog.py` | The Check Ring Reserve Level window (EDSM; a table of rings, or of every ringed body in a system) |
| `mining_session_archive.py` | Optional per-run JSON archive of finished mining runs |
| `mining_space.py` | Tracks ship-based mining runs |
| `mining_share.py` | One deposit as a pasteable line (`WFMT-SPOT1:...`): encode, strict decode and the duplicate check |
| `mining_spansh_client.py` | Spansh search for hotspots and best-price stations (shared with Trade's price searches) |
| `mining_stops.py` | Rhino stops: saved deposits one parking spot can reach, the best three, and the radius setting's limits |
| `mining_drive_rings.py` | The rings to drive round a marked mining location so the 2 km scanner reach covers it, from its middle out to its border (pure logic; a guide from the community reach figure, not a measurement) |
| `mining_map_picture.py` | The saved map picture of a mining location: the radar's marks centered on the location, sized to fit, with a title and a legend, no commander name (the live window's Save map button writes it as a PNG) |
| `mining_simulation.py` | The Mining simulation (Settings → Mining → Simulation): the Surface Live window on made-up data, a Rhino driving a circle over a made-up planet with saved deposits, marked locations and refining, built on its own in-memory repositories so it cannot touch the commander's data |
| `mining_sources.py` | Where the Mining pages read their data from: WFMT's own state, or the simulation's separate set (`Sources`); the renderers and the Live window take one |
| `mining_body_cache.py` | What Get body info found for each system, kept between sessions per commander (`mining_body_cache.json`, the newest 60 systems), so arriving in the system again or restarting EDMC brings the bodies back with no request |
| `mining_body_lookup.py` | Get body info (no Tk): EDSM's bodies list and Spansh's system dump (through the courtesy layer, by the system's game id) parsed into landable planets (name, kind, volcanism, radius in meters, mining-location count), merged and added to the Mining body list, the known body sizes and the counts without overriding the journal; the status-line wording |
| `mining_rigs.py` | The rigs the commander notes on the body they are on (the Rig placed action: a Live window button, a shortcut, the `!wf rig` chat command): in memory only, forgotten when the Rhino is launched, stowed or destroyed or the body changes; with the rig gap from Settings the radar draws a spacing band round each (no Tk) |
| `mining_radar_view.py` | The Surface radar's picture from the Mining data, one recipe for the Live window and the radar card over the game: the context (position, body size, ground driven, saved deposits), the drive rings, stops and target material, and the shared range setting (no Tk) |
| `mining_radar_overlay.py` | The Mining radar card: the Live radar's picture laid over the game as one image by WFMT's built-in overlay (Windows) while the Rhino is out, updated about once a second on a short-lived thread, with a translucent background, a size and an opacity setting, and a Test radar |
| `mining_what_pays.py` | What pays logic (no Tk, no network): the commodities worth pricing from the commander's own records (target commodity, saved deposits in any system, own rates on the grounds here, typed names), the ranking by best price and the copyable report |
| `mining_what_pays_dialog.py` | The What pays window (Spansh, opened from the Surface Mining Book): one best-sell-price search per commodity on a worker thread, a table that fills in and is ranked when done, Help and a copyable report |
| `mining_surface.py` | Tracks SRV surface-mining runs |

## Trade

Spec: [TRADE_TECH_SPEC.md](TRADE_TECH_SPEC.md) (has its own module table with more detail)

| Module | What it is |
|---|---|
| `trade_blocks.py` | The typed page model Trade draws (headings, label/value rows, tables, notes) and its plain-text form |
| `trade_carrier.py` | Fleet and squadron carrier cargo space and records, journal backfill and `trade_carrier.json` |
| `trade_carrier_ops.py` | Running the carrier: tritium, location, planned jump, trade orders and balance from the carrier journal events |
| `trade_commodities.py` | Commodity name matching and the type-ahead list |
| `trade_commodities_data.py` | The generated commodity table |
| `trade_commodity_entry.py` | The type-ahead Commodity box widget |
| `trade_hold.py` | Mission and stolen tons in the ship's hold, from the `Cargo` inventory, and the Trade panel's "Hold space" text (blank when there is no split to show) |
| `trade_history.py` | Saved sessions, the `HistoryBook` and `trade_history.json` |
| `trade_history_window.py` | The Trade History window (it widens to fit its widest table) |
| `trade_journal_scan.py` | Finds journal files not read yet (or grown) and applies them to the ledger, stock and carrier; `trade_journal_scan.json` |
| `trade_ledger.py` | The per-commander session ledger, running costs, catch-up from journals and `trade_ledger.json` |
| `trade_market.py` | Reads `Market.json` and values your cargo at the docked station |
| `trade_pages.py` | Trade's page order |
| `trade_panel.py` | Trade mode's entry point: chrome, page rendering, buttons, background jobs, Settings tab, journal dispatch |
| `current_system.py` | The system the commander is in now, asked on demand: what the caller tracked, EDMC's state, then the newest journal |
| `mission_progress.py` | How far along each mission is (the game's cargo count, kills, or tons in the hold) and the color band for it; used by the Missions window and the overlay card |
| `current_cargo.py` | The commander's hold by commodity, from EDMC's state, for "held" mission progress |
| `mission_pins.py` | The missions a commander pinned (ids only), kept per commander in `mission_pins.json`; pins go with their mission |
| `missions_board.py` | The Missions window's data: a row per active mission (progress, reward, time left, ready, pinned), the totals line, grouping by place, the detail lines; no Tk |
| `missions_window.py` | The Missions window (Active and By place tabs, detail strip, Pin / Unpin, Pin all here, Unpin all, Copy system, Sources) |
| `mission_sources.py` | The commodities your Collect and Mining missions still need (with the four source picks looked up for each) and the Delivery cargo still to pick up, with the station |
| `mission_sources_window.py` | The Missions "Source commodities" window (Find sources, Copy system) |
| `source_picks.py` | The four answers to "where do I buy or sell this?": closest, best local, cheapest anywhere, recommended (within 10% of the best); used by Trade and Missions |
| `trade_prices.py` | Ranks station offers for your load (sell and buy), carrier split and verdict lines |
| `trade_route_start.py` | Each commander's route start (last real station docked at) and `trade_route_start.json`; the journal scan feeds it docks, newest wins |
| `trade_roundtrip.py` | Finds the best back-and-forth station pair, loaded both ways |
| `trade_ship.py` | Ship to landing-pad size and the fit rule |
| `trade_spansh_client.py` | Spansh trade-route planner client and the profit-per-hour estimate |
| `trade_stats.py` | Every figure and table row shown for a saved session |
| `trade_stock.py` | The stock book: cargo bought and not yet sold, and `trade_stock.json` |
| `trade_view.py` | Draws Trade's page blocks with real layout (figures drop to the small font in a wide font, and the title wraps instead of widening the page) |
| `trade_watch_data.py` | The market watch list: a commander's watched commodities and the prices seen for them at the markets they opened (`Market.json`), kept per commander in `trade_watch.json`, with the Spansh answers held in memory; best buy and sell across both; no Tk |
| `trade_watch_lookup.py` | The watch list's Spansh refresh: the cheapest station to buy and the dearest to sell each watched commodity near a system, stations only, paused between requests and cancellable; the search is passed in, so it is tested offline |
| `trade_watch_panel.py` | The Watch list row in Trade mode: a few short best-price lines, Refresh (Spansh, on a worker thread; needs Trade's lookups on) and Watch (the window); reads `Market.json` on the `Market` event |
| `trade_watch_window.py` | The Watch list window: add a commodity with the type-ahead box, remove one, the best buy and sell with where and how old, and every market a commodity was seen at |

## Missions

Spec: [MISSIONS_TECH_SPEC.md](MISSIONS_TECH_SPEC.md)

| Module | What it is |
|---|---|
| `active_missions.py` | Which missions each commander has accepted and which are active |
| `all_missions.py` | The All Missions view across every mission type |
| `community_goal_state.py` | Community Goal progress and your contribution |
| `journal_scan.py` | Reads two weeks of journals so Missions survives EDMC restarts: accepted missions, kills, cargo progress and the active set |
| `kill_missions.py` | The massacre and settlement-raid missions and their kill progress |
| `kill_tracker.py` | Per-mission completion evidence, kept per commander |
| `mission_cargo.py` | Collect / delivery progress of cargo missions from the journal's `CargoDepot` events |
| `mission_types.py` | Classifies missions into the panel's categories |
| `missions.py` | Missions mode's entry point and event handling |
| `missions_ui.py` | Draws Missions' pages and opens the Missions window |

## Colonization: current project, history, sites window

Guide: [Colonization](guide/colonization.md)

| Module | What it is |
|---|---|
| `colonization.py` | Pure logic for construction-site tracking |
| `colonization_archive.py` | The facts the Archive window shows about a finished site (result, dates, time taken, tons needed) and its clipboard summary |
| `colonization_archive_window.py` | The Colonization Archive window (Manage Sites → Show Archive): finished sites kept for reference, with Restore, Copy Summary and Remove Permanently |
| `colonization_carrier.py` | (Includes `scan_journals`, the rebuild behind Rescan Carrier.) Tons of each commodity transferred to the commander's fleet carrier, for the window's FC column (per commander, caught up from the journals without double counting). Also decides when Frontier's CAPI cargo list may replace the tally: not within 15 minutes of the newest transfer, and not when it repeats a copy already ignored |
| `colonization_catchup.py` | Folds the recent journals into the saved construction sites at start-up, never counting a delivery twice |
| `colonization_data.py` | JSON persistence for construction sites (each carries `journal_at`, the newest journal event folded in) |
| `colonization_history_window.py` | The Colonization History window (History button): Overview, By day, Commodities and Sites tabs, so the panel itself shows no history |
| `colonization_history.py` | What the commander has delivered to construction sites (tons by commodity, site and day), kept per commander and caught up from the journals without double counting |
| `colonization_overlay.py` | The shopping-list card on the in-game overlay: what is still to get for the active site (pure formatting plus drawing); its visibility also follows the game rewriting `Market.json`, so the card shows when a market opens even if the journal's Market event is late |
| `colonization_panel.py` | The Colonization mode's page (current project and history), the overlay card's controller (including the hold, read from `Cargo.json` and read again shortly after any cargo event, with EDMC's cargo state as the fallback) and the settings tabs |
| `build_costs.py` | What each kind of building costs in tons (the bundled `colonization_costs.json`, a copy of a community-compiled table): looked up by a site's layout name, with its biggest commodities |
| `commodity_categories.py` | The market category of each colonization commodity, so the shopping list can be grouped as the in-game market groups it |
| `rcc_sync.py` | Opt-in sharing of live colonization progress with Raven Colonial: depot snapshot, deliveries, commander link and (separately) carrier cargo deltas, one request per event on a worker thread with a bounded queue |
| `overlay_profile.py` | Each commander's overlay choices (which cards run, their options, placement, Show ticks, look), kept in `overlay_settings.json`; the active commander's are loaded into EDMC's config when they are seen, so the overlay modules still read the config as before; `switch_off` clears named on/off switches in every commander's saved choices (the one-time overlay reset) |
| `rcc_keys.py` | Each commander's Raven Colonial key, kept in `rcc_keys.json` (one entry per commander) |
| `rcc_projects.py` | The commander's projects on Raven Colonial as the My Projects window lists them: the rows, which count toward the totals (the inverse of Raven's hidden list), progress, trips, and one project's shopping list |
| `colonization_projects_window.py` | The My Projects window: every active project the commander has on Raven Colonial across systems, with counting, a shopping list copy, set as primary and saving the counted list |
| `rcc_create.py` | Starting a Raven Colonial project for a tracked construction site: the plan is read, a planned site is built from (or the project stands on its own), the project is created from the depot figures, and the commander is linked, made primary and given their carrier; each optional step reports its own failure |
| `colonization_create_dialog.py` | The Create Raven Colonial project dialog: plan entry, name, location, building, layout, body, architect, notes and due date, every field bounded |
| `rcc_client.py` | A thin client for Raven Colonial's API: reading one system's plan (its architect, whether it is open, and its build sites: planned, building, complete), with a bounded read, a user-agent, a timeout and a one-minute memory |
| `colonization_builds_window.py` | The Planned Builds window: Raven Colonial's sites for the picked site's system, fetched on a worker thread when opened or refreshed |
| `colonization_buy_window.py` | The Where to Buy window: Spansh searches for the picked commodity or the whole list, with the best single systems and a shopping route; told the picked commodity, the rows to buy and the site's system by the Sites window |
| `colonization_sources.py` | Where to buy a colonization commodity: the closest stations (and optionally fleet carriers) with it in stock, any landing-pad size by default, via Spansh; the whole-list search (one request per commodity) and the remembered search choices; pure shaping around an injected search |
| `colonization_stats.py` | The figures and wording of the Colonization page: the current project and the history, worded for a commander with or without a fleet carrier; pure, no Tk |
| `colonization_systems.py` | The best single systems for a shopping list: groups the whole-list search by system, checks the best few with Spansh (every station's market in one request each), and ranks them by how much of the list they cover, the distance and the cost; pure logic around an injected search |
| `colonization_view.py` | What the Colonization Sites window shows for a site: the commodity rows after the filters, and the totals (still to get, on the carrier, in the ship, buy and haul trips); pure, no Tk |
| `colonization_window.py` | The Colonization Sites window: sites on the left; the picked site's progress, totals, filters and sortable commodity table, and the Where to buy search, on the right |

## Operations: screenshots, inventory, ship builds

Spec: [SCREENSHOTS_AND_INPUT_TECH_SPEC.md](SCREENSHOTS_AND_INPUT_TECH_SPEC.md), [TECHNICAL.md](TECHNICAL.md) section 12

| Module | What it is |
|---|---|
| `inventory.py` | Backpack, ship locker and carrier locker tracking |
| `inventory_cargo.py` | Ship and SRV cargo-hold tracking |
| `inventory_names.py` | Microresource ID to display name |
| `inventory_names_fdevids.py` | The microresource names, imported from a public list |
| `inventory_panel.py` | The Inventory section of Operations (bars and overlay) |
| `inventory_sound.py` | The optional pickup sound |
| `inventory_suit.py` | Current suit and backpack capacity |
| `inventory_window.py` | The tabbed inventory window |
| `screenshot_automation.py` | The screenshot timer and key press, detecting Elite running |
| `screenshot_convert.py` | Converts screenshots to renamed PNGs and thumbnails |
| `screenshot_gui_focus.py` | GUI-focus detection and per-panel crop rectangles |
| `screenshot_naming.py` | Output file names for captured screenshots |
| `screenshots.py` | The Screenshots section of Operations: capture, conversion, thumbnails, overlay message |
| `ship_builds_data.py` | Per-commander catalog of ship-build links |
| `ship_builds_dialog.py` | The Add/Edit Ship Build form (on `uikit/form.py`), with `build_ship` |
| `ship_builds_panel.py` | The Ship Builds section of Operations |
| `ship_builds_window.py` | The Ship Builds window: a Builds tab and a Stored modules tab |
| `ship_modules_tab.py` | The Stored modules tab of the Ship Builds window: filter box, freshness line and table |

## BGS

Spec: [BGS_TECH_SPEC.md](BGS_TECH_SPEC.md)

| Module | What it is |
|---|---|
| `bgs_discord.py` | The BGS report's selected tick as Discord messages: a block for each system, split under Discord's message limit |
| `bgs_format.py` | Text formatting shared by the BGS panel and report |
| `bgs_journal.py` | Rebuilds the current tick's totals from journal files |
| `bgs_ledger.py` | The per-tick ledger (live events and replay share one path), and the rebuild of a period that just closed from the journals (`repair_record`, `merge_records`) |
| `bgs_panel.py` | BGS mode's entry point |
| `bgs_state.py` | JSON persistence for BGS tracking |
| `bgs_tick_client.py` | The community galaxy-tick time API client |
| `bgs_tracker.py` | Pure parsing of BGS-relevant journal events |
| `bgs_window.py` | The BGS Report window |

## Discord sharing

| Module | What it is |
|---|---|
| `discord_client.py` | Posts, edits, deletes and checks through a Discord webhook: validates the link, sends no mentions, retries once on a pause, and words its errors without the link |
| `discord_customize.py` | The Customize Discord posts dialog: a report and template choice, checkboxes for which parts of a post appear, a live preview with its length, and Save, Save as, Rename and Delete for your own templates |
| `discord_format.py` | Pure Discord text helpers: escaping names, links, code blocks, time tags and splitting a report into messages under 2,000 characters |
| `discord_preview.py` | Pure: draws a post's markdown (bold, italic, links, bullets) as pieces a Text widget can show, for the customize dialog's preview |
| `discord_settings.py` | The Discord Settings tab (the switch and a list of named destinations, each a webhook link and an optional thread id, with Test, Remove, Add and Copy their destinations) and the commander the reports are shared for |
| `discord_share.py` | What the report windows call: copy for Discord, post on a background thread to a chosen destination (a menu when there are several), and edit an earlier post of the same report |
| `discord_templates.py` | The options each report's Discord post offers, the built-in presets (Standard, Compact, Detailed, Plain), and the templates a commander saves and chooses (`discord_templates.json`) |
| `discord_webhooks.py` | Each commander's saved destinations: a list of named webhooks (`discord_webhooks.json`, secrets left out of backups), and the master switch |

## Always on: Landing Assist and Interdiction Warning

Spec: [TECHNICAL.md](TECHNICAL.md) section 12

| Module | What it is |
|---|---|
| `interdiction.py` | Interdiction Warning overlay and detection |
| `carrier_jump_timer.py` | Fleet carrier jump countdown, the pure part: the planned jump from `CarrierJumpRequest` (cleared by a cancel or the jump), time left, one alert at 10, 5 and 1 minute and at departure, and reading a request back from recent journals |
| `carrier_route.py` | The Carrier Route planner's logic: the carrier's details from the journal (`CarrierStats`, `CarrierLocation`), the form Spansh's fleet carrier router takes, its answer as legs, and following the route; no Tk, no network |
| `carrier_route_panel.py` | The Carrier Route planner's owner: follows the commander's carrier through the journal, keeps the plotted route per commander and moves it along when the carrier arrives |
| `carrier_route_spansh.py` | The Carrier Route planner's network code: look the systems up and ask Spansh's fleet carrier router for a route |
| `carrier_route_state.py` | The carrier route kept in `carrier_route.json` (`commander_data.py`, one route per commander) so it survives a restart |
| `carrier_route_window.py` | The Carrier Route window: the carrier's details, the destination, Generate route, and the route as a table to copy from and follow |
| `fuel_alerts.py` | Fuel warnings, the pure part: low fuel at a chosen percentage, and a plotted star that cannot be scooped (`FSDTarget`) with a tank at or under a second percentage; tank size from `Loadout`, fuel from `Status.json` |
| `flight_alerts.py` | Flight Alerts: one overlay card for the carrier jump countdown, the fuel warnings and the mining alerts (`mining_alerts.py`), with its Settings tab, optional sound and a one-second tick while a jump is planned or a mining alert is up |
| `route_plan.py` | Route status, the pure part: the plotted route from `NavRoute.json`, where the ship is on it, jumps and light years left, each star's kind (neutron star, white dwarf, another star that cannot be scooped), the next supercharge, and the fuel and range figures from `Loadout`, `FSDJump` and `Status.json` |
| `settings_online.py` | Settings → General → Online lookups: a read-out of every switch that lets WFMT contact another service, with whether it is on now, who it asks and where to change it; a test checks every entry names a real setting |
| `route_edsm.py` | The Route overlay's optional EDSM check: which of the next systems EDSM does not know. `EdsmChecker` asks once, in the background, for the names it has no usable answer for (`status` is True, False, or None for not asked, asking or failed), keeps a known answer for the session, asks again about an unknown one after 10 minutes and after a failed lookup 5 minutes later; a failure is never read as unknown. No Tk, no EDMC (the lookup is injected) |
| `overlay_link.py` | The "Get EDMCModernOverlay" link at the top of each overlay feature's Settings page, shown only while EDMCModernOverlay is the overlay in use (not when WFMT's built-in overlay is chosen) |
| `route_overlay.py` | Route overlay: one card that copies the route being followed (where you are navigating to, the jump count, the systems still to visit by name and the light years left; the Route Planner's route or else the game's); its Settings tab, Test Card and a one-second tick while there is something to show |
| `overlay_card.py` | The list-style overlay card (and `WideCardLayout`, the short, wide version Bio status uses) shared by the Route, System targets, Body info and Exobiology cards: `Card` (a title with a badge and progress bar, a headline with sample circles, header lines, two-column rows with a muted second column, section labels and detail lines, an optional rule between the header and the rows, a footer of one or more lines), `CardLayout` (a plan built before anything is sent, so the height comes from what the card says; a plain dark panel; fixed top and width; every line at the left padding), `LiveCard` (redraw when changed or every few seconds) and `Ticker` |
| `scan_value.py` | The exploration value estimate as a pure module: the base value (per-class k, mass to the 0.2), the first-discovery multiplier, and the mapped value (the three mapping multipliers with the efficiency and Odyssey bonuses); used by the Exploration Value readout, the System targets and Body info cards and the Expedition Log |
| `system_history.py` | Which systems the commander has been in and scanned in, built from their journals (every finished journal once, in the background, then only new ones) and kept per commander in `system_history.json`: visits, first and last, whether anything was scanned, and the journal files that hold the visits; this session is kept in memory; used by the System targets card's visit line and to rebuild a system's survey from only the journals that matter |
| `system_known.py` | What other commanders found in a system, from Spansh's public system API (one request per system, the system number only, opt-in): the bodies with biology (species, count, reward) or a point of interest (wreck, beacon, Guardian site) and their estimated values, matched to the journal's bodies by name; kept in memory for the session, never raises; used by the System targets card's Known section |
| `system_survey.py` | The bodies of the current system from the journal (`Scan`, `FSSDiscoveryScan`, `FSSAllBodiesFound`, `FSSBodySignals`, `SAASignalsFound`, `SAAScanComplete`, `ScanOrganic`): estimated scan and mapped value, first footfall, what is left to map, which bodies still have life to analyse and which are finished; when the cards may show (the game closing or at its menu, docked, in hyperspace, another commander); rebuilt from the journals when EDMC starts or the commander logs in (reading back through the same commander's earlier journals) and merged with the saved survey of the system; no Tk |
| `system_survey_store.py` | The saved surveys of each system, per commander (`system_surveys.json`): the bodies and what their scans said, the honk, what is mapped and which organisms are analyzed, written after a short delay and merged back when the commander arrives in, or is restored to, the system, so leaving and coming back shows where they left off; the most recent 60 systems are kept |
| `targets_overlay.py` | System targets overlay: one card with the survey's heading and progress bar, a summary line (bodies mapped, life done), the scanned bodies worth mapping (a value threshold), the bodies with life not yet analyzed and the bodies finished (Done); the Known section (biology and points of interest others found, an optional Spansh lookup) and an optional EDSM lookup of bodies other commanders have scanned; its Settings tab and Test Card |
| `body_info_overlay.py` | Body info overlay: a card describing the body you have targeted (unless it is finished) or are close to (class, flags including first footfall, materials as element symbols, scan and mapped value, temperature, gravity, pressure, atmosphere and its composition as formulas, volcanism, life and geology signals, distance); its Settings tab (including symbols or full names) and Test Card |
| `chemistry.py` | Element symbols and compound formulas for the Exploration displays: `element` (Sulphur is S), `gas` (CarbonDioxide is CO2), `shorten` ("thin carbon dioxide atmosphere" becomes "thin CO2 atmosphere") and `label`; symbols by default, full names by a setting on the Body info tab |
| `exobiology_overlay.py` | Exobiology overlay cards for the body you are on, each with its own switch (Settings → Overlays → Exobiology) and Overlay Placement slot: Bio status (analyzed count and a progress bar that moves with each sample; while sampling, the species and color variant with three circles, what it pays with the first-footfall bonus beside the headline when it fits, the distance to the last sample beside that when the strip has room, and a line for each plant being tracked; a wide strip, 108 characters), Biology (each genus with the species it could be or is, the range it could pay, even-share percentages for the candidates, and the total range the body could pay), Bio radar and a Sample popup; all read `organic_scan_panel.overlay_view()`, so they agree with the Organic Scanning panel |
| `exo_analysis.py` | The analysis of the recorded finds, pure: one `Find` per confirmed species (listed by the prediction or not, outside a rule's range or not, with its manual review), the hit rate by genus, observed temperature, gravity and pressure against each species' rule range, species found together, and `report_text` (the whole analysis as text). Shared by the Prediction review window and `scripts/analyze_exo_observations.py` |
| `exo_review_window.py` | The Prediction review window (Review on the Organic Scanning panel): Finds (with a filter, each find's conditions and what was predicted, and a review status and note), Genera, Ranges and Together tabs, and Copy report. Built on the window kit |
| `exo_observations.py` | The record of what lived where, kept to check the species prediction over time: one record per sampled body with its conditions (type, atmosphere and trace gases, gravity, temperature, pressure, volcanism, star, materials, the system's other body types, galactic position), the genera its signals named, and each confirmed species with its color and the species the prediction listed then. Global, not per commander, and it names no commander; filled in from saved per-body state as each commander is seen. `ObservationBook` |
| `exo_radar.py` | The Bio radar's pure geometry and drawing (its lines under the plot wrap and shorten to stay inside the card): a top-down plot centered on you, heading up, with a circle at each sample as wide as the genus's minimum distance (red inside, green clear; drawn within a fixed size band whatever the zoom), the ship and the SRV, a ring, a line and a row for the latest unsampled plant of each genus (in that genus's color), and a little pointer beside each distance under the plot; `build_plan`, `tracked` and `RadarLayout` |
| `landing.py` | Landing Assist: assigned pad, diagram on the overlay and in the panel; one render worker that retries until the overlay is up |
| `landing_finder.py` | Nearest place to land: the Spansh station search by coordinates (`reference_coords`, so a system you have just discovered works), the pad rules (the ship's pad from `trade_ship`, never a pad it cannot use), the stations nearest first, the fleet carriers open to all (`carrier_docking_access` is "All") and recently reported, the age of each record, and the tracker of the last `StarPos` and `Loadout`; the search is passed in, so it is tested without a connection |
| `landing_finder_panel.py` | The Exploration panel's row for it (what it needs and the Find button), the journal hook that keeps the position and ship, and the restore from the newest journals |
| `landing_finder_window.py` | The Nearest place to land window: what you need (fuel, repairs, rearming, outfitting), the pad, carriers and their freshness, the box that allows the lookup, and the two lists; the lookup runs only on Find, off the main thread |

## Shared window kit (`plugin/uikit/`)

Spec: [WINDOW_FRAMEWORK_SPEC.md](WINDOW_FRAMEWORK_SPEC.md). Pure tkinter; nothing here imports EDMC.

| Module | What it is |
|---|---|
| `uikit/__init__.py` | Package marker for the shared window kit |
| `uikit/dialogs.py` | Themed confirm, choice, one-line prompt and message boxes (`confirm`, `choose`, `prompt`, `info`, `warning`, `error`) in place of the operating system's own boxes: modal over the parent, centered, a hard width cap, Esc cancels and Enter takes the default; `set_test_responder` lets tests answer without a window |
| `uikit/form.py` | `FormDialog`: labeled fields under section headings with an error line and Save and Cancel, in the window shell; the shared add/edit form (hotspots, ship builds), with `parse_optional_int` and `parse_optional_float` |
| `uikit/mapview.py` | Canvas map widget (coverage, hotspots, position, dashed rings, zoom) |
| `uikit/palette.py` | Color and font tokens for WFMT's own window look, and its four themes (Navy, Cyan, Amber, Green) with `apply` |
| `uikit/placement.py` | Where a pop-out window opens: the remembered position while it is still on a connected monitor, otherwise over EDMC's window on EDMC's monitor (every time with the "Always open WFMT's windows on EDMC's monitor" setting); `place` is pure, monitors come from user32 on Windows and the Tk virtual screen elsewhere |
| `uikit/shell.py` | The window shell: header (action buttons and menus take a tooltip), body, status footer, saved geometry; and `TabShell`, the same shell for a window that lives in a tab of another window |
| `uikit/style.py` | Fonts and per-window skinning |
| `uikit/tooltip.py` | `add_tooltip`: the hover tooltip every button uses, on the main panel and in the windows (`panelkit` re-exports it); Tk only |
| `uikit/table.py` | `DataTable`, the replacement for `ttk.Treeview` |
| `uikit/widgets.py` | Reusable widgets (buttons with a tooltip, combobox, scrollbar, progress bar, tabs) |
