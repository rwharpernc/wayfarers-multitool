# Design notes: why WFMT is built this way

This page is for the people who work on WFMT: a place to find out **why** something is the way it is, what was considered and not done, and how data from published sources is used. It is not a user guide.

- [TECHNICAL.md](TECHNICAL.md) says *how* things work.
- [ATTRIBUTIONS.md](ATTRIBUTIONS.md) says *whose* ideas and data they are.
- [CHANGELOG.md](../CHANGELOG.md) says *what* is in each release.
- This page keeps the reasoning that connects them.

This page is written for anyone reading it, as plain fact: what a source gives, what WFMT does with it, and why.

- Where an approach was considered and rejected, it says so, because the reasons are the useful part.
- It records the choices made for WFMT's own situation (journal first, per commander, Windows and Linux, inside EDMC) and the checks that back them.

**How to read an entry.**

- *Decision* is what was done.
- *Why* is the reasoning.
- *Not done* is what was considered and rejected.
- *Where to look* points at the code, the test or the doc that holds it.

**Contents**

1. [Principles that shaped everything](#1-principles-that-shaped-everything)
2. [Credits and licenses](#2-credits-and-licenses)
3. [Decision records](#3-decision-records)
4. [Deliberately not built](#4-deliberately-not-built)
5. [Lessons that keep coming back](#5-lessons-that-keep-coming-back)

---

## 1. Principles that shaped everything

These are written as rules so a new feature can be checked against them.

**Journal first, and never guess.**

- *Why:* a third-party tool only knows what the game writes down, and it is easy to fill a gap with a plausible number that is wrong for someone.
- Where the journal is silent WFMT adds data in a stated order (Frontier's CAPI, then data players share, then labeled workarounds), and says which.
- A value that cannot be known is left out, shown as unknown, or reported, never invented.
- *Examples:*
  - The Route Planner reports a frame shift drive it has no figures for instead of guessing them.
  - The jump range is not estimated from fuel and cargo (see 3.7).
  - The Dashboard shows `-` for a body it has not scanned.
- *Where to look:* [TECHNICAL.md](TECHNICAL.md) (the design principle at the top), the "what the game does and doesn't tell us" table ending each guide.

**Estimates are labeled as estimates.**

- *Why:* the scan-value formulas are close to what the game pays, not exact.
- The exobiology odds are an even split among species the body allows, because the data says which are possible and not how likely each is.
- Saying so in the interface keeps the number honest.
- *Where to look:* the Exploration Value and Biology card text; `organic_scan.GenusView.odds`.

**Everything saved about play is per commander.**

- *Why:* two commanders on one install must never see or change each other's data.
- A name used in a file name breaks on the other OS (Windows is case-insensitive and rejects some characters; Linux is case-sensitive). So a commander is only ever a JSON key inside a file, never part of a file name.
- The single exception is `exo_observations.json`: facts about bodies, pooled on purpose to check the species prediction, holding no commander.
- *Where to look:* `commander_data.py`, `tests/test_data_files_per_commander.py` (a new data file fails until it is classified), [DEVELOPMENT.md](DEVELOPMENT.md).

**Nothing goes online unless it is asked to.**

- *Why:* a plugin runs inside someone else's program on their computer.
- Every lookup is either a switch that starts off, or a button that only acts when pressed, and each is listed with what it sends.
- *Where to look:* [internet-and-privacy.md](guide/internet-and-privacy.md), `settings_online.py` (the Online lookups page; `tests/test_settings_online.py` fails when an entry names a setting the code does not have).

**Pure logic apart from the screen, and tests that read the sources.**

- *Why:* a function that takes plain data and returns plain data can be tested in milliseconds on both OSes, and the Tk part shrinks to drawing.
- Several tests read the code instead of running it so that a list cannot quietly drift out of step:
  - Every data file must be in the updater's protected list (`tests/test_own_data_files.py`).
  - Every module must have a row in [MODULES.md](MODULES.md) (`tests/test_docs_modules.py`).
  - The Dashboard's overlay prefixes must be real card prefixes (`tests/test_overlay_group_hide.py`).
- *Where to look:* [TECHNICAL.md](TECHNICAL.md) sections 6 and 14.

**Change live state at a safe moment, not while it is in use.**

- *Why:* WFMT holds its data in memory and rewrites the files, and Python cannot swap modules that are already imported.
- So an update is staged and takes effect at the next EDMC start.
- A restore from a backup is staged and applied at the next start before any feature reads a file (see 3.4).
- Doing either immediately would be undone by the running plugin's next save.

**Never delete what WFMT did not write.**

- *Why:* a live plugin folder, a backup folder and a deploy target all hold things that are not in the build.
- Deploy merges instead of deleting and re-copying.
- The updater only writes files that are in the release zip.
- Automatic backups are named so that pruning can only ever touch the backups WFMT made itself.

**Write safely and portably.**

- Atomic writes (temporary file, then `os.replace`), UTF-8, LF line endings, operating-system specifics only behind `platform_support`.
- A note in [LINUX_TESTING.md](LINUX_TESTING.md) for anything tried on one OS only.
- *Why:* the repository is developed on one Windows and one Linux machine and Git is the only link between them, so a habit that works on one has to be known to work, or marked as untried, on the other.

**Never restyle EDMC.**

- The window kit uses classic widgets and its own buttons and tables. `style.skin(window)` colors a window by name; it never touches the ttk theme.
- *Why:* ttk styles are application-wide, so changing one would recolor EDMC's main window and every other plugin. `tests/test_ui_kit.py` fails if it does.
- For the same reason nothing in the main panel may let outside data widen it: EDMC sizes its window to the widest row of any plugin, so one unbounded widget widens everyone's.
- See [WINDOW_FRAMEWORK_SPEC.md](WINDOW_FRAMEWORK_SPEC.md).

**One word for an overview page: DASHBOARD.**

- *Why:* it is the one label for a page that gathers everything about a mode in one place (Colonization has one, and so does Exploration).
- The same label may sit on buttons in different modes, because the mode already says which one it is, but no mode may have two.
- The Button names table in [getting-started.md](guide/getting-started.md) lists each.

---

## 2. Credits and licenses

Acknowledgements are in [ATTRIBUTIONS.md](ATTRIBUTIONS.md), and the license notices for the data that ships with WFMT are in [THIRD-PARTY-NOTICES.md](../THIRD-PARTY-NOTICES.md).

Those two files are where credit belongs; the rest of this page is about WFMT's own decisions.

---

## 3. Decision records

### 3.1 The built-in overlay

- **Decision:** WFMT can draw its own overlay on Windows, in a window it lays over Elite, and keeps EDMCModernOverlay for Linux and for other plugins. Both can run at once.
- **Why:** EDMCModernOverlay is a separate program with its own font, scaling and lifetime.
  - Its default font is capitals only.
  - An overlay window left running after EDMC closes can reconnect and draw a second copy of every card.
  - WFMT cannot choose a font for its own cards there.
  - Its right-hand clamp has to be worked around in placement.
- **What stays the same:** every feature sends small payloads through `overlay.OverlayClient`.
  - The built-in overlay is just another destination for the same payloads (`overlay_native.py`), and no card is specific to it.
  - The hide-everything switch works on both.
- **Checked first:** `scripts/native_overlay_test.py` shows that a transparent, click-through, layered window is clean, follows the game window, hides on alt-tab and does not stutter.
- **Where to look:** [NATIVE_OVERLAY_SPEC.md](NATIVE_OVERLAY_SPEC.md).

### 3.2 Right-hand overlay cards on Linux with a Flatpak EDMC

- **Decision:** when Elite's `DisplaySettings.xml` cannot be read:
  - Take the overlay window's size from EDMCModernOverlay's log.
  - Add a fifth Flatpak permission (the Graphics folder, read-only) to restore the normal path.
  - Keep telling the user to set Display scaling by hand.
- **Why:**
  - A Flatpak EDMC cannot see the Proton prefix where that file lives. Without the log WFMT would have to assume a 1920 x 1080 screen, which is wrong for most screens and puts right-hand cards in the wrong place.
  - The overlay's log always states its window size, so that is a better second source than a guess.
- **Not done:** estimating scaling. Linux gives no portable way to read it, so the honest answer is to say so and let the user choose it.
- **Where to look:** `overlay_layout.parse_window_size`, `overlay_placement.screen_for`, [linux.md](guide/linux.md).

### 3.3 Hiding groups of overlay cards (the Dashboard's two switches)

- **Decision:** hide by **id prefix in the overlay layer** (`overlay.set_group_hidden`), not saved, not in Settings.
- **Why:** the need is to switch off the exploration and exobiology cards and bring back exactly those.
  - The overlay layer already remembers every payload for the global hide.
  - A prefix filter there is one place and works for both overlays.
  - Showing a group simply replays what had not run out.
- **Not done:** switching each card's enable setting off and on.
  - That is saved into the commander's overlay profile, so a forgotten "off" would come back at the next start, and restoring would mean remembering which were on.
  - Putting a suppress flag in every feature module would touch a dozen files.
- **Where to look:** `overlay.py` (the group functions), `tests/test_overlay_group_hide.py`.

### 3.4 Back up my data, restore and automatic backup

- **Decision:**
  - One zip of everything in the updater's protected list plus the mining run archive, chosen by the user.
  - A restore that is **staged** and applied at the next start.
  - An optional automatic backup.
  - Keys and caches left out.
- **Why each part:**
  - The list is the updater's `_OWN_DATA_FILES`, so a new data file is backed up without anyone remembering to add it. The test that keeps that list complete keeps the backup complete.
  - The Raven Colonial keys are left out because a backup is meant to be copied around and kept in cloud folders.
  - The Codex catalog is left out because it is downloaded again.
  - The destination may not be inside the plugin folder, which an update or a reinstall can clear.
  - The zip is written under a temporary name and renamed, so a failure never leaves half an archive, and an existing zip is never overwritten.
  - A restore cannot overwrite live files, because the running plugin would write its memory back over them.
    - It is unpacked into a staging folder, marked complete last, and applied before any feature reads a file.
    - The files it replaces are zipped first, so it can be undone.
    - A zip that holds anything but WFMT's data files is refused whole, never partly applied.
  - Automatic backups use their own name and keep ten, so pruning cannot reach a backup made by hand.
  - One automatic backup is also made just before an update, because the updater's own backups leave data out on purpose.
  - It is off by default.
- **Not done:** restoring in place, and restoring one commander at a time (a data file holds every commander, so the file is the unit).
- **Where to look:** `data_backup.py`, [getting-started.md](guide/getting-started.md#backing-up-your-data), `tests/test_data_backup.py`.

### 3.5 Compact data files

- **Decision:** write the per-commander files without indentation. Indented files are still read.
- **Why:** measured on real files, `system_history.json` is about 2.0 MB instead of 3.2 MB and the system surveys 227 KB instead of 602 KB for the same data. The largest files are rewritten whole on every save, so smaller is faster as well as smaller.
- **Not done (deferred):** a database for the largest file, and writing less often.
  - Neither is needed at megabytes.
  - A database would make the files unreadable to other tools, which is a loss while the files are still a convenient thing to copy.
- **Cost accepted:** the files are not pleasant to read by hand (any editor's format command fixes that).
- **Where to look:** `commander_data.write`.

### 3.6 The Exploration Dashboard

- **Decision:** a window, opened from a DASHBOARD button on the Exploration panel, that reads what the other features already hold and draws it in four tabs (Overview, Orbit, Surface, Exploration).
- **Why a window:** the overlays draw on the game; sometimes the want is to read the same facts without cluttering the screen.
- **Why it holds nothing of its own:** it asks the system survey, Organic Scanning, the Expedition Log and the Route for their state, so it can never disagree with the cards.
  - All the numbers come from a pure module (`explore_dashboard_data.py`), so they are tested without a screen, and the window only draws.
- **Why Orbit and Surface:** the questions differ (the whole system from space; the body under you on the ground).
  - It opens on the one that fits and follows a landing and a lift-off, leaving a tab the user chose alone.
- **Why the header switches are runtime-only:** see 3.3.

### 3.7 The Route Planner

- **Decision:** plot with Spansh's **exact plotter**, built from the ship's real numbers, and do not estimate a jump range. Two other approaches were considered and rejected.

1. **Spansh's neutron router with a typed jump range.**
   - It asks for a range the game does not write for the current load, so the user would have to read it off the ship statistics panel and retype it whenever the load changes.
   - The Route Planner has its own visible button and window; this router is not used.
2. **Estimating the laden range** from the loadout's maximum, the unladen mass and the fuel and cargo on board.
   - *Not done:* the estimate moves with every jump's fuel, cannot be checked against the game, and ignores that a ship lightens as it burns fuel.
   - A number WFMT cannot know is not made up.
3. **Spansh's exact plotter (chosen).**
   - The plotter takes the ship's real numbers, and its optimal mass is exactly the engineered `FSDOptimalMass` already in the journal's `Loadout`.
   - Spansh's own page script shows the request it builds from a ship: a mass, the fuel tanks, the drive's optimal mass, maximum fuel and fuel formula, the supercharge multiplier and any booster.
   - WFMT builds the same request from the journal and the cargo in `Status.json`.
   - Spansh then works out the range itself, jump by jump, and says where to refuel.

**Data and what is WFMT's own**

- The request has the shape Spansh's exact plotter takes.
- The drive table is a table of published drive data, used as game facts (source and license: see docs/ATTRIBUTIONS.md and THIRD-PARTY-NOTICES.md).
  - It is flagged for checking in `data_verification` (V-0351 to V-0353).
  - A drive missing from it is reported, not guessed.
- Also built:
  - The next system copied to the clipboard after **every** jump, one setting shared by the panel and the window.
  - The plotted route taking over the Route overlay's card (with the overlay's EDSM mark for systems EDSM does not know).
  - A fuel column.
  - The neutron stars and the destination (and the refuel stops) turned into an expedition.
  - The options remembered.
  - A ship block that does not move while flying (fuel is not shown, only cargo, which rarely changes).
- *Lesson:* when a tool already does the thing, look at how it actually does it before building an approximation.

**Entry point and white dwarfs**

- The Expedition window's **Neutron route** button opens the Route Planner.
- A white dwarf also boosts the drive (1.5x, against 4x for a neutron star).
  - Neither Spansh plotter's request nor its answer knows about them (the pages' scripts mention white dwarfs only as star type names).
  - So the Route Planner cannot ask Spansh to plan through them.
- What it offers is an option, named *Mark white dwarfs the route passes*, that asks EDSM for the main star of each system on the finished route and *marks* the white dwarfs.
  - Planning through them would need a router of WFMT's own, which this window does not offer.
- The ship block also says whether a fuel scoop is fitted, because the refuel stops of a route need one and Spansh cannot be told to plan without.
- *Lesson:* a label has to say what the code does, and no more. An option labeled *Also mark white dwarfs* reads as "use them in the route", so the label says *Mark white dwarfs the route passes*.

**One window with three tabs**

- The Expedition window, the Route Planner and the Expedition Log were three windows that a trip moved between, each with its own size and position and its own place on the screen.
- They are now the Plan, Route and Log tabs of one window (`expedition_hub.py`).
- How it works:
  - The windows keep their own code and their own tests. Each was changed only to take its shell as an argument.
  - `uikit.shell.TabShell` gives a tab the same interface as `WindowShell` (the header buttons, Help, subtitle, status line and body), so nothing in them had to be rewritten for the tab.
  - The panels register how to build their tab with the hub, which imports no panel, so the dependency runs one way.
  - A tab is built when it is first shown, and again if its window is closed.
- *Cost:*
  - The three views share one window size and position.
  - The old per-window geometry settings are no longer read by the panels.
  - The standalone windows remain in the code only as the path the tests and `host=None` use.
- The panel's two rows are one section too:
  - The Log has no section of its own (`expedition_log_panel.PANEL_PLACEMENT` is `None`).
  - Its START, PAUSE and STOP are built into the Expedition section by `build_into`.
  - The section words the Log's extra figures under the expedition's own lines instead of saying the name, jumps and time twice.
  - A Log run with no plan behind it is shown as the Log words it.
  - The LOG button went: the archive is a tab of the window.
- *Cost:*
  - The section's folded state is the Expedition section's (the Log row's saved folded state is no longer read).
  - START, PAUSE and STOP are the Log's, so with a planned expedition running they act on it through the link, and with none they start a Log run only.
- **Start expedition** does not switch tabs. It is pressed on the Route tab of an open window, so it stays there and reports in the status line, and **Review** is the way to the Plan tab.

**One linked start for an expedition**

- *The problem:* a trip has two records, the Expedition planner's list of stops and the Expedition Log's run of figures.
  - They used to be started, paused and stopped separately.
  - Starting a planned expedition left the Log, the Dashboard and the overlay card saying that none was running.
  - **Pause** meant two different things (the Log stopped its clock, the planner only changed a word).
- *Decision:* starting an expedition also starts a Log run.
  - The expedition remembers the run (`log_run_id`).
  - Start, Pause and Stop on either side do the same to the other, in one small module (`expedition_link.py`) that both panels call, so the two cannot disagree.
  - The expedition's time is the run's clock, which leaves out the time paused.
  - The Log run is on by default and a Setting turns it off (Settings > WFMT > Exploration > Expedition), for a commander who wants the planner alone.
- How the Route Planner uses it:
  - **Start expedition** does the whole thing in one press and reports it in the status line instead of asking.
  - **Review** opens the Expedition window on the same expedition for a look at the order first.
  - A second press for the same plot picks the expedition made the first time rather than making "(2)".
  - An expedition made from a route is a snapshot of the stops and notes at that moment, so plotting again or clearing the route never changes one that is running.
  - The one word for ending is **Stop**, as in the Log.
- *Cost:* the Log keeps one run running at a time.
  - Starting a second expedition sets the first aside (its run is paused with it, or stopped when the new one gets its own run).
  - An expedition that was set aside and is started again reopens its run as the Log's Resume does. The clock picks up from the time the run stopped at, so the time in between is not counted.

### 3.8 When a relog skips the journals

- **The case:** a system scanned while EDMC is closed must not be empty after logging back in.
  - A rule that decides whether to rebuild a system's survey from the journals by asking "have they been here before?" and counting visits gets this wrong.
  - A relog is not a second visit, so a first visit played with EDMC closed looks new and gets a record holding only the honk, which would stop any later rebuild.
- **Decision:** rebuild whenever the visit history says the commander **scanned** there and no scanned bodies are saved (`system_survey.needs_backfill`).
  - This also repairs a record left holding only the honk.
  - A first visit played live needs nothing, because the live events carry it.
- **Why this and not "always rebuild":** a rebuild reads journals, and most arrivals do not need one.
- **Lesson:** a counter that stands in for a fact ("been here before") breaks where the two come apart; prefer the fact the history actually records.
- The tests for it fail without the rule.

### 3.9 Engineering data

- **Decision:** take a published recipe table as the data source, then correct it from the game's own records.
- **Why:**
  - The table is archived and was last changed in March 2024, so it goes stale as the game changes.
  - The journal records what the game charges now, and other maintained tables disagree in five places.
  - Where sources differ the more recently maintained one wins. The choice is written down in the module's docstring, and a test pins each change so a re-import cannot silently undo it.
- A FSD synthesis recipe whose cost the journal shows two ways (V-0350) is recorded, not resolved by guesswork.

### 3.10 Clearing a line or a circle on the overlay

- **The problem:** the Bio radar clears every slot it is not using on each redraw.
  - Sent as a line with no points, the clear is rejected by EDMCModernOverlay (`Dropping vect payload with insufficient points`).
  - So each redraw would log a warning per slot and the clear would never take effect (a stale pointer stays until its ttl runs out).
  - A one-point line is rejected as well.
- **Decision:** send a removal for the id (the id and a ttl of 0), which the overlay treats as a real removal, and only for items that are on the screen.
- **How it was settled:** by running the installed overlay's own `normalise_legacy_payload` on the candidate payloads, not by guessing at workarounds.
  - The empty line and the one-point line come back as dropped.
  - A circle clear comes back as a visible white circle (a circle with no color is given white).
  - The removal comes back as `legacy_clear`.
- **Why in the overlay layer:** four features clear lines and one clears circles. One place owns it and callers keep their calls (`send_vector(id, [], ...)`, `send_circle(id, "", "", ...)`).
- **Lesson:** check a rule against the source of the thing that enforces it, and write down what was checked.
  - A cheap clear (nothing sent when nothing is drawn) also removes the log noise at its source.

### 3.11 RND: real systems, not guessed names

- **The problem:** a name made by shifting both numbers of a nearby real name does not plot on the galaxy map.
  - In a procedural name `<sector> <LL-L> <mass><N1>-<N2>`, N1 is part of the boxel's identity and N2 is the index inside it.
  - Shifted names are in boxels that do not exist or past the last index of one that does.
  - "EDSM has no record" is then read as "undiscovered", but it is equally true of a name that was never real.
- **Decision:** ask Spansh for the systems that exist around the commander (`systems/search`, nearest first), keep those whose `body_count` is empty, and confirm one with EDSM's bodies list before offering it. Nothing is ever composed from a pattern.
- **Why Spansh first:** it can sort by distance from a position, which EDSM's cube query cannot do for scan state.
- **Limit, stated in the guide:** no scan data does not prove no visit.
  - The Sequence mode keeps the boxel identity and steps only N2, so its names are valid until the boxel's unknown last index.
  - Region Sweep and Find Nearby only use listed systems.
- **Speed:**
  - The Spansh search takes roughly 10 seconds whatever the page size (25 and 100 systems take about the same), so the wait is the server's sort, not the reply.
  - Cutting the page to 25 barely helps, so the list is cached in memory (10 minutes, 5 ly, same request size) and repeat clicks only run the EDSM check, which is always fresh.
  - The page size is a Settings entry (10 to 100, default 25) with a note that more is slower.
  - The cache is not written to disk because a stale list is worse than a short wait after a restart.
- **Lesson:** a negative lookup is evidence only when the thing looked up is known to be real. Start from a list of real things.

### 3.12 Bio radar text stays inside its card

- **The problem:** the lines under the radar plot are laid out left to right, while the card is only as wide as the plot. A long plant name or three distances on one line would overrun it.
- **Decision:** one function (`lay_out_rows`) places the rows for both the card's height and the drawing, so they cannot disagree.
  - Items wrap to a new line, and the card grows by the lines used.
  - An item wider than a line is cut with an ellipsis.
  - The ship and SRV row above the plot never wraps because the plot sits below it; it is cut instead.
- This is the same rule as for EDMC panels: content from outside needs an explicit bound.

### 3.13 POI Reference and the section order

- **Decision:** GEC Nearby POI and Canonn Nearby POI are one section, POI Reference, with one FIND.
  - The controllers are separate modules (`gec_poi_panel.py`, `canonn_poi_panel.py`) because the sources differ. One downloads a single list and caches it for six hours; the other uses two Google-hosted sheets cached for the session, with different settings.
  - `poi_reference_panel.py` owns the buttons and the frame.
  - A small `Collector` waits for both lookups and names the nearer system. It has no Tk so a test can drive it.
- **Why the clipboard takes the nearer one:** with two sources, copying whichever result arrived last would not be the best answer.
- **Section order:** sections within a mode are alphabetical by their visible name, so a section can be found without scanning.
  - The order is the order of `FEATURES`, and `tests/test_panel_order.py` fails if a new section is placed out of order.
  - One consequence: RND is added to the Auto-Honk row before Boxel Survey's panel exists (Boxel Survey sorts after it), so the button creates its own status variable rather than relying on build order.

### 3.14 Cards that leave in one step

- **The problem:** when a card goes away its text can clear first and the empty panel stay for a few more seconds.
- **Cause:** `overlay_card.PANEL_TTL_FACTOR` gives a panel twice the lifetime of its text.
  - That is deliberate: the overlay stacks items in the order they were first drawn, so a panel that lapsed a moment before a refresh would come back above the text and dim it.
  - The cost is that a card which just stops being redrawn (no explicit clear) shows a bare panel for the second half.
- **Decision:** handle it in the overlay layer, not in each card.
  - A sweep every half second looks at what WFMT has drawn (`overlay._last`).
  - It removes a panel that has carried live text before and has none now, together with the shapes drawn over it (`overlay.orphaned`, a pure function with tests).
- **Why not shorten the panel's lifetime:** that brings back the dimming.
- **Why not a timer per card:** there are more than a dozen card types and radar-style drawings, each with its own code. One rule over the remembered drawings covers them all, including ones added later.
- **Limit:**
  - A panel that never had text keeps its own lifetime.
  - Text from another card lying over a panel keeps that panel until the text lapses.

### 3.15 My Codex

- **Decision:** the Codex Completionist section keeps its summary line and has one button, MY CODEX.
  - DASHBOARD is not used because Exploration already has one and a name is never used twice in a mode.
  - The window has an Overview tab and a Where to look column, and the backfill is in the window.
- **Why an overview:** the Found and Not found lists answer "what do I have" but not "what should I go after", and a thousand-row list does not show that one genus is nearly finished. Ranking started types by entries left gives a first answer.
- **Why the hint is built from existing data:**
  - The catalog lists every biological entry as a species plus a color.
  - WFMT already holds the conditions each species needs and what decides each color for the Bio predictions.
  - So a missing entry can say what planet to look for at no new cost and no network use.
- **Limits, stated in the guide:**
  - The hint shows only the first set of conditions.
  - It says where an entry can appear rather than where one is.
  - It has nothing for Thargoid, Guardian or stellar-body entries; those are what POI Reference is for.
- **Not done:** finding the nearest planet that fits a missing entry. It would need a search of scanned bodies (Spansh) and is a separate piece of work.

### 3.16 Wrapped text beside a button

- **The problem:** the main EDMC window can stretch wider with no change anyone made.
- **Cause:** a label whose `wraplength` is the whole width of the plugin frame is right on its own row and wrong when it shares a row with a button.
  - The row (button plus a label as wide as the frame) is wider than the frame.
  - EDMC sizes its window to the widest row, the frame's next resize is larger, and the label is handed that larger width in turn.
  - Any text change that lands in such a label can start the creep. For example, the route summary beside NEUTRON ROUTE changes when a window closes and the route state is refreshed.
- **Decision:** `panelkit.wrap_label` gives a label the room left of where it starts (`available_wrap`) and also subtracts the widths of the other widgets in its row, which are known.
  - A label's own position is not settled at the moment a hidden panel is shown.
  - So it recomputes when a hidden panel is mapped, and gives a label in a hidden panel only a modest width until then.
- **How it is checked:**
  - A test puts a long label beside a button in a frame of fixed width and fails if the label ends past the frame.
  - A log line records which widgets ask for the room whenever the panel widens by 40 px or more, so a recurrence names its own culprit.
- **Lesson:** a bound has to be on the space a widget has, not on the space the whole frame has. This is the rule for anything that can size the main window.

### 3.17 Nested tabs in the Dashboard

- The Orbit tab has a second set of tabs (Worth mapping, Life to analyze, Found by others) beside the Body panel.
- With the page-level `Tabs` style, a second large uppercase bar with the window's dark background sits inside a lighter pane.
- `Tabs(compact=True)` keeps the behavior and changes only the look for a set nested in a pane.
- The Dashboard's Orbit tabs use it. The BGS and Powerplay nested sets have the same shape and could use it with a one-word change each.

### 3.18 Switching overlays off and on

- **The problem:** two things go wrong if hiding and showing are naive.
  - *Off:* hiding by sending each item a replacement that draws nothing (an empty text, a zero-size panel) with a `ttl` of 1 makes EDMCModernOverlay drop the empty text at once and keep the replaced panel for a while.
    - The overlay's own code treats a payload with only an id and `ttl: 0` as a removal (`legacy_clear`), which is how lines and circles are cleared (3.10).
  - *On:* putting back only what still has time left on its `ttl` restores nothing, because a card's `ttl` is four to eight seconds. A card in a quiet cockpit would not be drawn again until something happened.
- **Decision:**
  - Every clear is a removal, sent only for what is on the screen (so the overlay has nothing to log).
  - Showing puts back what was on the screen at the switch-off plus anything drawn since, with its full `ttl`.
  - The features keep drawing into the remembered set while hidden, so the restored card is current.
- **Limit:**
  - A banner that ended while the overlays were off comes back for one `ttl`, because "ended" and "not drawn again yet" cannot be told apart from here.
  - The overlay hides its own window whenever Elite is not in front, which is expected and separate from WFMT's hide.
  - Cards that merely stop being redrawn are covered by 3.14.

### 3.19 Organic Scanning after EDMC was closed

- **The problem:** EDMC is closed while the last Sample and the Analyze of a species are taken.
  - The survey (rebuilt from the journals, 3.8) counts the species as complete.
  - The organism tracker is fed only by the events EDMC passes in, so it keeps its saved stage (2 of 3) and shows it on the Bio status card and the Dashboard.
  - A body scanned entirely with EDMC closed has no saved progress at all.
- **Decision:** the same catch-up pattern as the visited log and the survey.
  - On a worker thread, read the commander's `ScanOrganic` events from the last 14 days.
  - Merge them into the saved per-body progress on the Tk thread.
- **How the catch-up names and merges:**
  - A `ScanOrganic` names its body only by number, so `organic_catchup` learns the name from the `Scan`, `FSSBodySignals`, `SAASignalsFound` and `ApproachBody` events for the same body in the same system. It skips a sample it cannot name.
  - The merge only raises a stage, so it is safe to run on every start and needs no watermark.
  - `OrganicTracker.restore_organism` never lowers a stage, because a saved stage older than the live one would otherwise undo live progress.
- **What else the pass recovers:** what the prediction reads for a body scanned with EDMC closed.
  - Conditions come from its `Scan`, genera from `FSSBodySignals` or `SAASignalsFound`, and there is the first-footfall flag.
  - It goes through one shared pure builder, `organic_scan.conditions_from_scan`, so the live handler and the catch-up cannot drift apart.
  - These are added only where nothing is saved for the body, never over what the live tracker saved.
  - A species left part-way is shown as the active scan again when a body's progress is restored.
- **Limit:** positions are not in `ScanOrganic`, so a caught-up sample adds none. The distance to the last sample on that body is whatever was saved.

### 3.20 Mining History

- **Why:** the Mining pages show only the run in progress, held in memory. A run across an EDMC restart, a relog or an EDMC that was closed vanishes, and nothing adds the runs up.
- **Decision:** build it from the journals, on the pattern of the system history (3.8 and `system_history.py`).
  - Read every finished journal once in the background.
  - Save one record of runs per commander.
  - Read only newer journals afterwards.
  - Read the newest journal afresh each time instead of saving it, so a growing file is never counted twice.
  - This also covers the gap in the live page's own catch-up, which replays only the current journal when EDMC starts with the game running.
- **Definitions:**
  - *A run* is undocking to docking, the same boundary as the live page.
    - Mining with no undocking before it starts a run of its own.
    - Sales after docking go to the run that just ended.
  - *Mining time* is first to last mining event, so travel does not dilute the rate.
  - *Earned* is the sales after the run, and is not profit, which the window says.
- **Reuse:** the table and block widgets come from the Exploration Dashboard, so the two look and sort alike. They could move into the shared kit if a third window wants them.
- **Not done:** a verdict on a single asteroid against a chosen commodity, and earnings on the live page. Both are separate work.

### 3.21 The Route overlay is a plain copy of the route

- **Decision:** the card is a copy of the route and says nothing else.
  - **You are navigating to:**, the destination, **You will be there in N jumps.**, a rule, the systems still to visit, a rule, **N LY left to jump.**
  - A system is taken off as it is reached.
  - Each system shows its star in a color that means one thing: green (fuel can be scooped), yellow (it cannot), blue (neutron), red (white dwarf).
  - At the end it says the route has ended and is being reset, then closes.
- **Why:** a card that also carries fuel, range, last jump, the next supercharge, refuel stops, an EDSM line, the running expedition, numbered rows and a star column is hard to follow.
  - So there is one source of truth (the Route Planner's route, else the game's `NavRoute.json`) and one job (follow the route).
  - The fuel, range and supercharge figures are in the Exploration Dashboard, which has the room for them, and the expedition lines are not on the card.
- **Cost:** a commander who wants the fuel line on the screen has to open the Dashboard. The card is shorter, so it fits the room more easily.
- **Limit:** the end of the route is detected only for a route the overlay has already shown (`_seen`), so a finished route left in `NavRoute.json` from an earlier session says nothing.

### 3.22 Exploration Value lives inside the Dashboard section

- **Decision:** the Exploration Value readouts and the Dashboard window show the same figures (the Dashboard's *Panel readouts* are literally Exploration Value's lines), so they share one panel section.
  - The readout lines are drawn under the DASHBOARD button (`exploration_value.build_rows`).
  - Exploration Value has no section of its own (`PANEL_PLACEMENT = None`).
  - Its Settings tab, switches and the two online extras stay.
- **Why:** two sections would take two lines of a crowded panel to show one thing. The Dashboard and the Route Planner sections fold like the others.

### 3.23 One considerate way to call Spansh

- **The problem:** if each feature that asks Spansh makes its own requests with its own timeouts, nothing limits how many run at once or what happens when Spansh answers that it is busy. The Route Planner's star lookups make the request count worth managing in one place.
- **Decision:** a single module (`spansh_courtesy.py`) that Spansh requests go through:
  - two in flight at most
  - a quarter second apart
  - retries with growing waits on a busy answer
  - a pause after repeated failures
  - a count in the diagnostics
- **Why a module and not a setting:** the limits are the same for every feature and belong in one reviewed place; a user setting would only let them be set higher.
- **Why POSTs are not retried on a timeout:** a submitted job may have been accepted.
- **Cost:** a long polling loop (route jobs poll every 5 seconds) is unchanged. The star lookups for the next dozen neutron stops take a few seconds instead of arriving at once.
- The page `docs/SPANSH_USAGE.md` records every endpoint, so that the use can be read and checked.
- Where Spansh publishes a data dump that covers a need (the neutron-star list), reading a local copy is preferred to asking, and that is planned as an option (see [TODO.md](TODO.md)).

### 3.24 What "Acquire" means in Colonization (formerly "Remaining")

- **The problem:** the column, then called Remaining, was the site's need (required less delivered). A commodity already bought and parked on the fleet carrier still read as outstanding until it was unloaded at the depot, so the column did not fall as the commander worked, and the overlay card needed a second column (To buy) to say what was left to get.
- **Decision:** the column (renamed Acquire after 1.0.0, because it shows what is still to get) is what is still to get: the site's need less the cargo in the ship and on the fleet carrier, and it reaches 0 once the whole amount is acquired wherever it is stored. The window, its category totals and sort, and the overlay card all show it. Required, Delivered and Haul Trips keep the site's own figures, so the trips to carry everything to the site stay honest.
- **Why:** it answers the question the commander is asking while shopping, and it makes the window and the card agree.
- **The hold comes from `Cargo.json`.** The journal's `Cargo` event carries only a count, and EDMC's cargo state was seen not to follow a purchase, so the ship's hold is read from the file the game rewrites on every change, again shortly after any event that can change it. EDMC's state is the fallback when the file is missing or describes the SRV.
- **The middle step (after 1.0.0):** once everything is bought and parked on the carrier, the old *hide covered* filter hid every row. It became a three-way choice: All, To buy (the old behavior) and To haul, which keeps the rows the ship and carrier cover but the ship does not yet hold in full, so a row leaves the list as it is loaded and the site drops it once delivered. One function (`colonization_view.shown`) decides for the window and the overlay card, so they agree.
- **Not done:** counting a commodity on the carrier as delivered. It is not delivered until it is unloaded at the depot, and the carrier column says where it is.
- **Best single systems** (`colonization_systems.py`) follow the same rule of not guessing: the search by commodity names stations, so a system whose stations together stock the list was invisible. The few best candidates are asked of Spansh for every station's whole market (one request each, through the courtesy layer in 3.23), so the stock is counted from what the stations report. Where to look: [TECHNICAL.md](TECHNICAL.md) (Best single systems).

### 3.27 Color themes for WFMT's own windows

- **The problem:** one fixed palette suited some commanders and not others, and the EDDDT app next to WFMT already offers three colors.
- **Decision:** four themes (Navy, the default, and Cyan, Amber and Green after EDDDT's stylesheet), one choice for every pop-out window, from Settings or the window's bottom line. Open windows are recolored by mapping each old color to the new one, because the windows are built from the palette's attributes and keep what they were given.
- **Why a color map and not a rebuild:** windows hold state (selections, scroll positions, a search in progress) that a rebuild would lose.
- **The rule that makes it work:** read palette colors when a widget is built. A color fixed at import time or as a default argument would stay in the old theme, so the kit uses `None` defaults and token names.
- **Not done:** a light theme, themes for the overlay cards (Settings → Overlays → Appearance has its own schemes) and anything in EDMC's own window.

### 3.26 Text size and column fit for WFMT's own windows

- **The problem:** the text of the dashboards was small and fixed, and every table gave each column a declared minimum width and shared spare width equally, so short columns sat wide and long ones were cut.
- **Decision:** one text size for all pop-out windows (-2 to +6 points, remembered), changed from a window's footer (A- and A+) or Settings. Fonts are resized in place, so open windows follow at once. Columns that do not stretch take the width their content needs, and spare width goes to each in proportion to that.
- **Why in the footer:** the narrow-window checks need the header's width for the title.
- **Not done:** a size for the EDMC panel or the overlay cards (EDMC and Settings → Overlays → Appearance own those), and dragging a column border.

### 3.25 The navy theme for WFMT's own windows

- **The problem:** the pop-out windows were near-black with gray text. Headings, table headers and status messages were all the same muted gray, so nothing stood out and the windows read as dull.
- **Decision:** keep the fixed look (3.x, `WINDOW_FRAMEWORK_SPEC.md` section 4) but move the surfaces to navy and give three roles their own color in `uikit/palette.py`: `TITLE` (gold) for a window title, `HEADING` (cyan) for section labels, field labels and table column headers, and `STATUS` (soft blue) for the footer message. Success, caution and failure keep green, yellow and red, a little brighter.
- **Later change (2026-10-28):** `STATUS` was a pale tint of the accent, which blended into the window on every theme. It now has its own bright color per theme (yellow on Navy, Cyan and Green, cyan on Amber), and a test keeps it well apart from the accent, headings and text.
- **Why:** color separates the structure of a window (where a section starts, what a column is) from its data, without adding a setting. Every window gets it because they all read the palette tokens.
- **Not done:** a light variant or a user choice of theme; the in-game overlay cards (which have their own schemes in Settings → Overlays) and the main panel (which follows EDMC) are unchanged.

## 4. Deliberately not built

Each was considered and left out for a reason that still holds. They are in the "Not planned" list of [TODO.md](TODO.md) so they are not proposed again.

- **Guardian ruin and structure surveying.** Surveying a site well is a project of its own; WFMT's exploration aims to give a commander what they need day to day, not to be a dedicated survey tool.
- **Landing-pad layouts the journal cannot supply.**
  - The journal gives a facility type, an economy, the pad counts and a pad number, but no layout variant, orientation or pad positions.
  - A diagram of where the pads sit on a particular station would be invented.
  - Landing Assist draws the diagrams it can from what the journal does provide.
- **An FSS spectrum guide.**
  - The journal never records where a signal sits on the scanner's band.
  - No published table of ranges is available, and the only table found is closed source with no license.
  - So the ranges would have to be measured in the game.
- **Estimating the jump range for the current load** (3.7), and **assuming a screen size** where it cannot be read (3.2), for the same reason as the rule at the top: a number WFMT cannot know is not made up.

---

## 5. Lessons that keep coming back

- **Check the real thing before building a model of it.**
  - Reading how Spansh's own page builds its request removes the need for an approximate range (3.7).
  - The survey rebuild rule (3.8) comes from reading real saved files and journals, not from reasoning about the code.
- **Prefer the record to the counter.** The visit count, the saved-record-exists check and the "scanned" flag are three different ideas of the same question; only the one that mirrors a fact holds up.
- **Keep one source of truth and let the views share it.** The Dashboard, the cards and the panel all read the same survey and the same Organic Scanning view, so they cannot disagree.
- **Make the restore as careful as the backup.** A backup that cannot be restored safely is half a feature, and a restore applied while the program is running is undone by it.
- **Write down a rejected idea with its reason.** The compact-data note says why a database was deferred; the Not planned list says why something is out. It saves a future argument and a future mistake.
- **A test that fails without the rule is the proof the test matters.** The relog test and the group-hide tests are written so that they fail when the behavior they guard is missing.
- **Deterministic tests.** A helper built on Python's randomized `hash()` makes a test fail now and then, so ids in tests are assigned, not hashed.
