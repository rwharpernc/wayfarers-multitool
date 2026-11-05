# Project Status

Scope: the release state, branches, test state and unverified items of Wayfarer's Multitool (WFMT) as of 2026-11-04. The file is kept in Git because Git is the only thing shared between the two test machines, one running Windows and one running Linux.

## Release

| Version | Published | Notes |
| --- | --- | --- |
| 1.5.3 | Not yet published | Patch on 1.5.2, built on `work/1.5.3`. Contains the Copy next system fix and Discord sharing for the Expedition Log and the Expedition plan. Docker tests on Linux: 4,066 passed, 12 skipped. The Copy next system fix was tested in the game on Windows and on Linux on 2026-11-04 with no major issues; the Discord addition has not been tried in the game. |
| 1.5.2 | 2026-11-04 (tag `v1.5.2`) | Built on `test/windows-combined`. Docker tests on Linux before release: 4,031 passed, 12 skipped. No in-game pass of [TEST_PLAN.md](TEST_PLAN.md) section 14 is recorded. |
| 1.5.1 | 2026-11-03 (tag `v1.5.1`) | Patch on 1.5.0, built on `patch/1.5.1`. Docker tests on Linux before release: 3,923 passed, 13 skipped. In-game pass of [TEST_PLAN.md](TEST_PLAN.md) section 13 on Windows and on Linux on 2026-11-03, before publication, with no failures. |
| 1.5.0 | 2026-11-02 (tag `v1.5.0`) | Docker tests on Linux before release: 3,894 passed, 13 skipped. In-game pass of [TEST_PLAN.md](TEST_PLAN.md) section 12 on Windows and on Linux on 2026-11-02, before publication, with no failures. |
| 1.4.2 | 2026-11-01 (tag `v1.4.2`) | Patch on 1.4.1. |
| 1.4.1 | 2026-11-01 (tag `v1.4.1`) | Next release after 1.3.3. The 1.4.0 version number was prepared and never published; its changes are part of 1.4.1. Docker tests on Linux: 3,850 passed, 13 skipped. No in-game pass recorded. |
| 1.3.3 | 2026-10-30 (tag `v1.3.3`) | Built on `bugfix/1.3.3`, merged into `master`, branch deleted. |
| 1.3.2 | 2026-10-29 (tag `v1.3.2`) | Built on `bugfix/1.3.2`, merged into `master`, branch deleted. |
| 1.3.1 | 2026-10-29 (tag `v1.3.1`) | Built on `bugfix/1.3.1`, merged into `master`, branch deleted. |
| 1.3.0 | 2026-10-29 (tag `v1.3.0`) | Built on `release/1.3.0`, merged into `master`, branch deleted. |
| 1.2.0 | 2026-10-28 (tag `v1.2.0`) | Built on `release/1.2.0`, merged into `master`, branch deleted. |
| 1.1.0 | 2026-10-27 (tag `v1.1.0`) | Built on `release/1.1.0`, merged into `master`, branch deleted. |
| 1.0.0 | 2026-10-26 | First release. Contains everything built up to 2026-10-26. |

- The project was renamed Wayfarer's Multitool (WFMT) and its version history restarted at 1.0.0 on 2026-10-21.
- The latest published release is 1.5.2. The repository is public.
- The in-app updater and the README "latest release" link read GitHub's public releases API.
- The full list of changes for each version is in [CHANGELOG.md](../CHANGELOG.md).

### Contents of each release

- **1.5.3** (not yet published)
  - Adds Copy for Discord, Post to Discord and Customize… for the selected expedition in the Expedition Log: name, status, route, exploration and exobiology figures, and the credits its data sales earned.
  - Adds the same three buttons to the Expedition window for an announcement of the chosen expedition's plan: progress, next stop and stops.
  - Fixes **Copy next system** on the Trade Routes window: it follows the leg you are on, moving to the next destination once you dock at the previous one, and wraps for loops and round trips.
  - The updater offers 1.5.3 to installations on 1.5.2 once it is published.
- **1.5.2**
  - Adds a Powerplay sale-merit log: each sale made while pledged is written with the merits that followed it, with a start-up catch-up from the journals, to `sale_merits.csv`. It only collects data and estimates nothing.
  - Adds a Powerplay margin marker (40% line) to the Trade Round trip, a **Start from** station and a **Rank by** choice for it.
  - Adds Rename Site and Refresh from Raven to the Colonization Sites window.
  - Adds 18 engineering blueprints, more modules in the Ship planner, Anduliga Fire Works in the Rare Goods Finder, landing pads for the Anaconda Mk II and the Lynx Highliner, more landing places in Nearest place to land, a page for donation and rescue missions, and game names for consumables and Powerplay items.
  - The updater offers 1.5.2 to installations on 1.5.1.
- **1.5.1**
  - Adds the Combat Record to Operations: kills, PvP kills, deaths and rewards per ship, for this session, every session and in total, kept per commander and read back from the journals.
  - Adds the materials picked up this session to the Engineering row, which now shows what is held and what was picked up as a small table.
  - Shows ship names as the game shows them in the Combat Record, the Expedition Log and Trade (one shared table, `ship_names.py`), instead of the journal's internal names.
  - The updater offers 1.5.1 to installations on 1.5.0.
- **1.5.0**
  - Replaces the ◀ ▶ pages with windows (Trade, Mining, Missions).
  - Moves the display and tuning settings of Trade, Mining, Missions, Powerplay, BGS, Inventory, Colonization (the reporting choices) and Exploration (three windows) out of File → Settings into the windows that use them.
  - Adds running and whole-route totals and the average per leg to Routes.
  - Forgets a scrapped fleet carrier.
  - The updater offers 1.5.0 to installations on 1.4.2.
- **1.4.2**
  - Where to Buy: a Suggested route tab and a Closest stations tab; a route order list (shortest flight, smallest or largest purchase first, farthest first); sections that start minimized with Expand all and Minimize all; a large message while a search runs; a body and data age on each stop.
  - Colony page: a Body line, a Commodities line in done, partly and working on it, and three biggest gaps.
  - The Mining and Missions mode buttons are now Mine and Mission.
- **1.4.1**
  - Where to Buy: own-system-first search and presets, shopping trip (flying order, next-stop card) and filters.
  - Engineers tab: path to unlock, status colors, formatted details, a Works on column, requirement checks against the journal, the Engineers button.
  - Copying overlay choices from another commander, a separate diagnostic log and window tooltips.
  - The Interdiction Warning recognizes more NPC lines; the Route overlay follows a recalculated route.
  - Three engineer requirements (Wellington Beck, Kit Fowler, Hero Ferrari) match Frontier's update 18.08.
- **1.3.3**
  - Powerplay overlay card (Settings → Overlays → Powerplay): the commander's Power, rank and merits, the cycle's merits, the system's state and holder, what merits there count as, and the merits and estimated Control Points earned there this session. The card shows **No Powerplay Detected in system** where the game gives no Powerplay data.
  - Opt-in look-ahead (**Look up the system I am jumping to**, which queries Spansh) that turns the card to a jump's destination. Arrivals are remembered from the journal. The destination's control progress is shown only while under ten minutes old.
  - The Powerplay merit cap research page.
- **1.3.2**
  - Mode buttons have full names (Powerplay, BGS, Explore, Mining, Trade, Missions, Operations, Colony). Every panel and window button has a Mixed Case name and a tooltip. Rows of panel buttons wrap instead of widening EDMC's window.
  - The Powerplay panel merges its Session and Cycle lines when they would repeat. Lines that repeated another are removed from the Colony, Trade, Mining, Exploration, Missions and BGS panels.
  - Pop-out windows open on EDMC's monitor (a Settings tick selects this always). The Route Planner and Mining live windows have larger minimum sizes.
  - The guide file `field-ops.md` is renamed `operations.md`.
- **1.3.1**
  - The Region Sweep EDSM skip option works. The Colonization Show and List choices start at the same place. Three Settings texts are corrected. The documentation is brought in line with the code, with a checker that keeps it so.
- **1.3.0**
  - Sharing to Discord: Copy for Discord and Post to Discord for the BGS report and Powerplay progress, a named list of webhook destinations for each commander, and a dialog to customize how the posts look.
  - The Expedition Log's three Start from my last buttons; a shopping-list overlay that follows the Sites window's Show choice; a README and guides with how-tos and worked examples.
  - Expeditions are managed only in the Expedition window. The Bio status card is wider and shorter. The Organic Scanning section is folded by default. The green under the To haul filter is replaced by a tint for rows in the hold.
  - Sampling a different genus abandons the unfinished one.
- **1.2.0**
  - Colonization Archive; the offer to create a Raven Colonial project for a new site; a Where to Buy window of its own; Copy To Acquire; one row per candidate species on the Biology overlay card; a brighter footer message.
  - Fixes Create Project on Raven (the dialog opening out of sight and its status message being overwritten) and the layout editor's snapping of large boxes to the top, bottom and sides.
- **1.1.0**
  - Color themes and a text size for WFMT's own windows; the Colonization Show / List choice and the Acquire column name; the fleet carrier figure fix.
- **1.0.0**
  - First release.

## Branches

- Only two branches exist: `master` and `work/1.5.3`, the work toward the next release. The work of 1.5.2 was done on a branch then named `test/windows-combined`, which was merged into `master` for the 1.5.2 release and renamed `work/1.5.3` on 2026-11-05 to carry on with 1.5.3.
- Earlier, the feature branch `feature/ux-improvements` (version 1.5.0) was merged into it for the 1.5.0 release, and `patch/1.5.1` (version 1.5.1) for the 1.5.1 release.
- From 1.5.3 on, a release is built on `work/<version>` and merged into `master`. Before that, a release was built on a branch named for it (`release/1.3.0` was the last). Releases 1.3.1, 1.3.2 and 1.3.3 were built on `bugfix/1.3.1`, `bugfix/1.3.2` and `bugfix/1.3.3`. Each branch is merged fast-forward into `master` and deleted after the tag is created.
- A fix to a released version is made on a short branch cut from `master` (for example `bugfix/1.3.4`) and merged back.

## Testing

### Automated

| Date | Release | Result |
| --- | --- | --- |
| 2026-11-05 | 1.5.3 (not yet published) | 4,066 passed, 12 skipped (Docker, Linux) |
| 2026-11-04 | 1.5.2 | 4,031 passed, 12 skipped (Docker, Linux) |
| 2026-11-03 | 1.5.1 | 3,923 passed, 13 skipped (Docker, Linux) |
| 2026-11-02 | 1.5.0 | 3,894 passed, 13 skipped (Docker, Linux) |
| 2026-11-01 | 1.4.2 | 3,857 passed, 12 skipped (Docker, Linux) |
| | 1.4.1 | 3,850 passed, 13 skipped (Docker, Linux) |
| | 1.4.0 (unpublished) | 3,805 |
| 2026-10-30 | 1.3.3 | 3,731 passed, 13 skipped (Docker, Linux) |
| | 1.3.2 | 3,687 |
| | 1.3.1 | 3,656 |
| | before 1.3.0 | 3,639 |
| 2026-10-28 | before 1.2.0 | 3,485 |
| 2026-10-27 | before 1.1.0 | 3,471 |
| 2026-10-26 | before 1.0.0 | 3,447 |
| 2026-10-23 | Docker Desktop on Windows | 3,370 passed |

### Windows

- Tested by the maintainer with a build of the branch being worked on (`npm run deploy`, run by hand).
- Bugs found are fixed on `master` or on a short bug fix branch.
- The in-game pass of [TEST_PLAN.md](TEST_PLAN.md) section 12 for 1.5.0 was completed on 2026-11-02 with no failures. The in-game pass of section 13 for 1.5.1 was completed on 2026-11-03 with no failures. The 1.5.3 build was tested in the game on Windows on 2026-11-04 with no major issues (section 15). No in-game pass of section 14 is recorded for 1.5.2.
- Native checks made on Windows on 2026-10-23: the display probe read 3840 x 2160 at 125% scaling; the journals confirmed the Mk II jet cone boost of 6x at a neutron star and 3x at a white dwarf (V-0351).
- Recorded for 1.2.0 (deployed and used on Windows on 2026-10-28; not run on Linux outside the Docker tests):
  - The Colonization Archive (Archive Finished, Show Archive, Restore) works.
  - The bright footer message color on each theme was judged better than the previous one.
  - Create Project on Raven: the dialog opened out of sight and the construction panel overwrote the status message; both are fixed (steps in [TEST_PLAN.md](TEST_PLAN.md) section 6).
  - The Where to Buy window, the Biology card's new rows (through Test Cards) and the layout editor's top-edge snap work. Copy To Acquire was deployed and looked correct.
  - Not yet tried in the game: the Biology rows on a real body with several candidate species; the offer on the COL page when a new site has no Raven project (requires sharing on and a saved key); the 30-second hold of a button's message.
- In-game pass of [TEST_PLAN.md](TEST_PLAN.md) sections 1 to 6 not recorded for 1.3.0 (2026-10-29) and 1.2.0 (2026-10-28); still open for 1.1.0 (2026-10-27) and 1.0.0 (2026-10-26). Section 7 is new in 1.3.0. Sections 5 (2026-10-23) and 6 (Colonization, 2026-10-26) are the newest of those. Items:
  - Every overlay is off after the first start, for every commander, with one log line.
  - A stopped expedition carries on from where it stopped, and Rescan leaves out paused and stopped time.
  - Overlay Placement names where the screen size came from, and reads the real hardware size when the game's files are not found.
  - Long names in the Missions, Source commodities, Ship Builds and My Codex tables.
  - Saved data from before the spelling change still loads (`Renamed saved names:` once).
- To check on Windows with the 2026-10-27 build (requires a fleet carrier, a registered construction site and EDMC signed in to Frontier; steps in [TEST_PLAN.md](TEST_PLAN.md) section 6):
  - The Colonization FC column keeps cargo just unloaded at the carrier when Frontier's copy lags behind. A copy that arrives within 15 minutes of the last transfer, or that repeats one already ignored, is left out until Frontier's figure changes or Rescan Carrier is pressed.
  - Each Frontier figure writes one `Carrier cargo from Frontier` line to EDMC's log. **Copy diagnostics** gathers these lines after a wrong column. How to read them is in [the Colonization guide](guide/colonization.md).
  - The 15-minute rule and the unchanged-copy rule have been run in tests only, not against Frontier's live figure, on either OS.

### Linux

- Manual pass target: CachyOS (Arch-based) with KDE Plasma and a Flatpak EDMC. Releases 1.0.0 through 1.4.2 have no manual pass recorded on this setup. The 1.5.0 in-game pass on Linux was completed on 2026-11-02. The 1.5.1 pass (section 7s of `docs/LINUX_TESTING.md`) was completed on 2026-11-03. The 1.5.3 build was tested on Linux on 2026-11-04 with no major issues (section 7u). No pass is recorded for 1.5.2 (section 7t).
- The steps and the ordered checks are at the top of `docs/LINUX_TESTING.md` ("Testing: start here").
- Earlier manual passes:
  - 2026-10-18 (KDE Plasma, Wayland, Flatpak EDMC): completed without recorded problems.
  - 2026-10-20 (quick pass): unit and smoke tests passed, the plugin loaded without errors and the Settings pages were correct.
  - Both passes tested builds from before the 1.0.0 restart and rename. The window-fit fixes of 2026-10-21 were checked only in a Docker run (a Linux container).
- Keyboard shortcuts (all six actions) are available on Windows only; their key choices are disabled on Linux. On Linux, the overlays are hidden by clicking the Overlays line on the panel, by pressing **Hide / show now**, or by typing `!wf overlays` (requires **Chat commands** under Settings → WFMT → General → Shortcuts).
- A test report from Linux contains:
  - the distribution and desktop
  - X11 or Wayland
  - native or Flatpak EDMC
  - the relevant lines of EDMC's log (`~/.local/share/EDMarketConnector/EDMarketConnector.log`)

### Assumptions not confirmed in the game

- `SendText` carries the typed text in a `Message` field.
- The 2 km scanner reach behind the green ground-driven area and the drive rings. Frontier has published no figure. EDRhinoSpotter calls its 2 km "the community figure"; SrvSurvey has none (checked 2026-10-23). The figure cannot be measured in the game and remains a labeled community estimate.
- Elite's controls file is found on Linux inside the Proton or Wine folder.

### Location of the in-game checks

- Materials, Engineering, Ship planner and Expedition: [`docs/TODO.md`](TODO.md).
- The Linux versions: `docs/LINUX_TESTING.md`.

## Work not yet run on Linux

Recorded 2026-10-21 on the Windows machine and extended through 2026-11-01. None of the items below has been run on Linux outside the Docker tests.

### Order of work on Linux

1. Run `git pull --rebase`.
2. Run `fc-match sans`, then `python -m unittest discover -s tests -p "test_window_fit_*_smoke.py"`, and report both results.
3. Run `npm run test:docker` once Docker is set up.
4. Build and deploy by hand (`npm run deploy`), then follow `docs/LINUX_TESTING.md` and the checklists in `docs/TODO.md`.

### Docker test runner

- Command: `npm run test:docker` (see the "Container test run" section of `docs/DEVELOPMENT.md`).
- Setup on Arch: `sudo pacman -S --needed docker`, enable the service, join the `docker` group, log in again.
- The script and image have run on Windows with Docker Desktop and on Linux.

### Spelling fix and saved-data migration

British spellings in names were replaced with American ones, including the Colonization modules, tests, saved files and settings. Checks after `git pull --rebase`:

- Start EDMC once and look for `Renamed saved names:` in the WFMT log lines.
- The Colonization page shows the current project and its history, the Sites window lists the sites, and the fleet carrier column shows its figures.
- The Colonization overlay card keeps its position and its on or off state.
- A hidden mode stays hidden, and the panel opens on the mode last used.
- Trade stock and the Exploration surveys are unchanged.
- If the Colonization history is empty, it can be rebuilt from the journals.
- The installed plugin folder can hold modules under their old names (`colonisation_*.py`). These are not loaded and can be deleted.
- The migration ran correctly on a copy of the Windows data (Docker Desktop, 3,342 tests). It is untested on Linux data.

### Window fit

- The five `test_window_fit_*` tests failed on Windows (Docker Desktop) and on Linux (desktop font Noto Sans; Docker with DejaVu Sans).
- On 2026-10-21 the layouts were fixed on Linux (narrower entries, wrapping labels, larger minimum sizes for some windows); the tests passed in the Docker run.
- On 2026-10-24 the native run on the Linux desktop (KDE Wayland, Noto Sans) failed all five. Expedition, the Plan dialogs, Notes and the Price finder were then fixed (taller minimums, fewer table rows, narrower boxes). Commit `cad6ea5` was checked in Docker with DejaVu Sans and with Noto Sans (3,370 tests, 12 skipped). The windows were inspected by eye on the Linux desktop afterward. The native suite has not been re-run on that commit.
- Docker with Noto Sans reproduced about 10 of the desktop's 101 findings.
- Not checked natively on Windows: the Expedition and Plan dialog minimum heights were raised.
- Still to check by eye: Colonization Sites, Surface Mining Book, Notes, Powerplay Sessions, the Route Planner and the Mining live window (minimum sizes raised), and that no minimum exceeds a small screen.
- Stretch columns in tables clip their text to the width they get, so the checker's cut-text notes no longer appear. Check a long name in a wide and a narrow window on both OSes.

### Items added since the last Linux pass

| Item | Date | Check |
| --- | --- | --- |
| Screen size from the operating system | 2026-10-21 | With no game files or overlay log to read, the screen size comes from the primary monitor (`xrandr --current`, through the host from a Flatpak). Remove or rename the overlay's log, open Settings → Overlays → Overlay Placement and read the source line: it reads *using the primary display* with the real resolution. Report the session type and whether `xrandr` is installed. The Windows test machine reads 3840 x 2160 (native check, 2026-10-23). |
| Every overlay off | 2026-10-21 | One reset (`wfmt_overlay_reset_v2`) switches every overlay off for every commander, once. Start EDMC and look for `All WFMT overlays reset to disabled` in the log. No card shows for any commander, and a card turned on stays on after a restart. |
| Expedition clock and Rescan | 2026-10-21 | A stopped expedition started again carries its clock on from where it stopped; Rescan leaves out paused and stopped time. Steps: `docs/LINUX_TESTING.md`. |
| Ship planner In storage column | 2026-10-21 | Steps: `docs/LINUX_TESTING.md`. |
| Table text caps | 2026-10-21 | The caps are 60 on the non-stretch name columns of Missions, Source commodities, Ship Builds and My Codex. Check a long name at a narrow and a wide size, on both OSes. |
| Colonization and Raven Colonial | 2026-10-26 | **Create Project on Raven**, the **My Projects** window (the Projects button), and finding a site's project by market id as well as name. Create Project, Mark Plan Entry Demolished and the My Projects writes have not run against the live service. Steps: `docs/LINUX_TESTING.md` and [TEST_PLAN.md](TEST_PLAN.md) section 6. |
| Sites window Acquire column | 2026-10-26 | Shows what is still to get (the need less the ship's hold and the fleet carrier). The overlay card matches it, with no To buy column and a choice, To buy by default, of which stage of the work it lists (All, To buy or To haul). The window has the same **Show** dropdown. |
| Ship's hold | 2026-10-26 | Read from the game's `Cargo.json`, so the In Cargo figures follow a purchase. |
| Color themes and text size | 2026-10-27 | Four themes (Navy, Cyan, Amber, Green) and a text size for WFMT's own windows, chosen in a window's bottom line or Settings → General → Window. Steps: [LINUX_TESTING.md](LINUX_TESTING.md) sections 7k3 and 7k4 and [TEST_PLAN.md](TEST_PLAN.md) section 6. |
| Navy look and Acquire header | 2026-10-27 | WFMT's own windows use navy with a gold title, cyan headings and a soft blue footer message. The Colonization **Remaining** column is now **Acquire**. Checks: [LINUX_TESTING.md](LINUX_TESTING.md) section 7k2 and [TEST_PLAN.md](TEST_PLAN.md) section 6. |
| Fleet carrier column and lagging Frontier copy | 2026-10-27 | Same check as the Windows one above ([TEST_PLAN.md](TEST_PLAN.md) section 6). The log is the Flatpak EDMC's. **Copy diagnostics** gathers the `Carrier cargo from Frontier` lines. |
| Where to Buy exclusions | 2026-10-31 | Exclude surface ports and Exclude fleet carriers (the carriers tick is on by default since 1.4.1), the route following purchases, and the route block. Steps: `docs/LINUX_TESTING.md`. Not run on Windows or Linux. |
| Where to Buy filters | 2026-10-31 | Only stations with enough stock, Only stations with a shipyard and Arrival within (all off by default); the orbital-only check before a commodity is called surface-only; the window is taller at its minimum size. Not run on Windows or Linux. |
| Colony page in the main window | 2026-10-31 | Sections, no Next line, and the last five completed sites when none is under construction. Not run on Windows or Linux. |
| Overlay choices copied from another commander | 2026-10-31 | Overlay Placement tab. Not run on Windows or Linux. |
| Windows reopening on the wrong monitor | 2026-10-31 | The saved position is written with an explicit plus sign. Not confirmed on a three-monitor setup. |
| Engineers tab | 2026-10-31 | Unlock paths, the Next step column, the requirement notes and the status colors. Checks: [TEST_PLAN.md](TEST_PLAN.md) section 10. Not run on Windows or Linux. |
| Search-in-progress accent color | 2026-10-31 | Best single systems, first added with it, were removed from the window on 2026-10-31. |
| Where to Buy own-system search | 2026-11-01 | The commander's own system is searched first (Find nearest and Find all); the Preset list with Large, then Medium as the default and carriers left out by default; the note when options changed since a search; the Create Raven Colonial project dialog's primary port tick is unticked and disabled when the system already has one. Steps: `docs/LINUX_TESTING.md` and [TEST_PLAN.md](TEST_PLAN.md) section 10. Not run on Windows or Linux. |
| Interdiction Warning and Route overlay | 2026-11-01 | More NPC message keys are recognized and the lines before an unwarned interdiction are logged. The Route overlay re-reads a rewritten `NavRoute.json` and logs the route. Not run in the game. |
| Native test suite | 2026-10-23 | The Docker run on Windows passed all 3,370 tests. The suite is to be run natively on Linux from a desktop session, with the count and any failure reported. Tests that replay dated journals use a fixed clock; `docs/DEVELOPMENT.md` describes how to find those that do not. |
| Star index Update | 2026-10-21 | Update fetches Spansh's 1-day or 1-week file instead of the 173 MB dump. Follow "Local star index" in `docs/LINUX_TESTING.md` and report the time an update takes. |
| Expedition window | 2026-10-21 | The Expedition window, Route Planner and Expedition Log are the Plan, Route and Log tabs of one window. Follow "One Expedition window" in `docs/LINUX_TESTING.md` and report whether the window takes focus when it opens. |
| Mining additions | 2026-10-21 | Mining History's *credits after limpets*; the *Hold full in* line; the station's price against the galactic average when docked. Steps: `docs/TODO.md` ("Verification in the game") and `docs/LINUX_TESTING.md`. All three read only the journal and `Market.json`; the Linux check is that the journal folder is found and the lines appear. |
| Expedition section | 2026-10-21 | The panel's Expedition and Expedition Log rows are one section. Check that it fits the panel and does not widen EDMC's window. |
| Start expedition cue | 2026-10-21 | On the Route tab, a started expedition turns the status line green and the button reads *Started ✓* for four seconds. A press that starts nothing shows neither. |
| Reopening a stopped expedition | 2026-10-23 | The clock continues from the time at which the expedition stopped; the stopped time is not counted. It applies to the Route tab's Start and the Log's Resume and is covered by a unit test. Rescan leaves out what happened while a run was paused or between a stop and the restart, as the live count does. |

## Working rules

- **Deploys**
  - Nothing deploys automatically. Committing builds nothing. Builds are made by hand when one is wanted, such as when a release is cut.
  - `npm run deploy` copies the checked-out branch's build over the EDMC plugins folder, replacing the build being tested.
  - A deploy merges: files from an older build that no longer exist remain in the folder, unused.
- **Git**
  - Commits, pushes, version bumps, tags and releases are made by the maintainer.
  - Run `git pull --rebase` before starting work, and push when done.
  - Machine-specific paths and logs are not committed.
- **Conventions**
  - American English everywhere.
  - Everything saved about play is per commander (`plugin/commander_data.py`).
  - Files use LF line endings.
- **Releasing** is described in `docs/DEVELOPMENT.md` ("Releasing").

## Decisions

- The tests use Mactavious, the author's own commander name (see the README and [ATTRIBUTIONS.md](ATTRIBUTIONS.md)), as a second test commander, to check that commanders' data stays apart.
- Every online lookup is either opt-in in Settings or runs only when a button is pressed. Each is listed in `docs/guide/internet-and-privacy.md`.
- Out of scope: Guardian ruin surveying, landing-pad diagrams and an FSS spectrum guide. The journal lacks the data they require; the spectrum ranges are not in it and no open table of them exists.
