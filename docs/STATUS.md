# Where things stand

Read this first when picking the project up on a machine that has not seen the recent work (for example the Linux test machine).

- It is kept in Git because Git is the only thing shared between the two test machines, one Windows and one Linux.
- Last updated 2026-10-31.

## Release

- **1.4.1** is the version number in `plugin/__init__.py` and `package.json`. It is prepared on 2026-11-01 and not yet tagged or published. It is the next release after 1.3.3: the 1.4.0 version number was prepared but never published, so its changes are part of 1.4.1. It adds Where to Buy's own-system-first search and presets, the Engineers tab's path to unlock, status colors, formatted details, a Works on column and requirement checks against your journal, the Engineers button, Where to Buy's shopping route and filters, copying overlay choices from another commander, a separate diagnostic log and window tooltips, recognizes more NPC lines in the Interdiction Warning, makes the Route overlay follow a recalculated route, and brings three engineer requirements (Wellington Beck, Kit Fowler, Hero Ferrari) in line with Frontier's update 18.08. The full list is in [CHANGELOG.md](../CHANGELOG.md). It has had the Docker tests on Linux (3,844 pass, 13 skipped) and no in-game pass yet.
- **1.3.3** was released on 2026-10-30 (tag `v1.3.3`) from the `bugfix/1.3.3` branch, which was merged into `master` and deleted.
  - 1.3.3 adds the Powerplay overlay card (Settings → Overlays → Powerplay): your Power, rank and merits, the cycle's merits, the system's state and holder, what merits there count as, and the merits and estimated Control Points earned there this session, with **No Powerplay Detected in system** where the game gives no Powerplay data.
  - 1.3.3 also adds an opt-in look-ahead (**Look up the system I am jumping to**, which asks Spansh) that turns the card to a jump's destination, with arrivals remembered from the journal and the destination's control progress shown only while under ten minutes old, and the Powerplay merit cap research page.
  - It had the Docker tests on Linux before release; the card has had little time in the game and none on Windows (checks in [TEST_PLAN.md](TEST_PLAN.md) section 9).
- **1.3.2** was released on 2026-10-29 (tag `v1.3.2`) from the `bugfix/1.3.2` branch, which was merged into `master` and deleted.
  - 1.3.2 gives the mode buttons full names (Powerplay, BGS, Explore, Mining, Trade, Missions, Operations, Colony) and every panel and window button a Mixed Case name and a tooltip, and rows of panel buttons wrap instead of widening EDMC's window.
  - 1.3.2 also merges the Powerplay panel's Session and Cycle lines when they would repeat, removes lines that repeated another on the Colony, Trade, Mining, Exploration, Missions and BGS panels, opens pop-out windows on EDMC's monitor (with a Settings tick to always do so), gives the Route Planner and Mining live windows larger minimum sizes, and renames the guide file `field-ops.md` to `operations.md`.
  - 1.3.1 was released on 2026-10-29 (tag `v1.3.1`) from the `bugfix/1.3.1` branch, which was merged into `master` and deleted. It made the Region Sweep EDSM skip option work, started the Colonization Show and List choices at the same place, corrected three Settings texts and brought the documentation in line with the code, with a checker that keeps it so.
  - 1.3.0 was released on 2026-10-29 (tag `v1.3.0`) from the `release/1.3.0` branch, which was merged into `master` and deleted.
  - 1.3.0 adds sharing to Discord (Copy for Discord and Post to Discord for the BGS report and Powerplay progress, with a named list of webhook destinations for each commander and a dialog to customize how the posts look), the Expedition Log's three Start from my last buttons, a shopping-list overlay that follows the Sites window's Show choice, and a README and guides with how-tos and worked examples. It changes expeditions to be managed only in the Expedition window, makes the Bio status card wider and shorter, folds the Organic Scanning section by default, and drops the green under the To haul filter in favor of a tint for the rows in your hold. It fixes sampling a different genus, which now abandons the unfinished one. The full list is in [CHANGELOG.md](../CHANGELOG.md).
  - 1.2.0 was released on 2026-10-28 (tag `v1.2.0`) from the `release/1.2.0` branch, which was merged into `master` and deleted.
  - 1.2.0 adds the Colonization Archive, the offer to create a Raven Colonial project for a new site, a Where to Buy window of its own, Copy To Acquire, one row per candidate species on the Biology overlay card and a brighter footer message. It fixes Create Project on Raven (its dialog opening out of sight and its status message being overwritten) and the layout editor's snapping of large boxes to the top, bottom and sides.
  - 1.1.0 was released on 2026-10-27 (tag `v1.1.0`) from the `release/1.1.0` branch, which was merged into `master` and deleted. It added the color themes and the text size for WFMT's own windows, the Colonization Show / List choice and the Acquire column name, and carried the fleet carrier figure fix.
  - The project was renamed Wayfarer's Multitool (WFMT) and its version history restarted at 1.0.0 on 2026-10-21.
  - Everything built up to 2026-10-26 is the first release, published as 1.0.0.
  - The checks to run first are in [TEST_PLAN.md](TEST_PLAN.md), and the open in-game checks are in [TODO.md](TODO.md).
- The latest published release is 1.3.3, published on 2026-10-30 (1.4.1 is prepared; 1.3.2, 1.3.1 and 1.3.0 were published on 2026-10-29, 1.2.0 was published on 2026-10-28, 1.1.0 on 2026-10-27 and 1.0.0 on 2026-10-26), and the repository is public.
  - The in-app updater and the README's "latest release" link read GitHub's public releases API.

## Branches

There is one long-lived branch, `master`.

- A release is built on a branch named for it (`release/1.3.0` was the last; 1.3.1, 1.3.2 and 1.3.3 were fixes on `bugfix/1.3.1`, `bugfix/1.3.2` and `bugfix/1.3.3`), merged fast-forward into `master` and deleted after it is tagged.
- For a fix to a released version, cut a short branch from `master` (for example `bugfix/1.3.4`), and merge it back.

## Testing

### Windows

- Tested by the maintainer, using a build of the branch being worked on (`npm run deploy`, run by hand).
- The 1.2.0 work, deployed and used on Windows on 2026-10-28 (not run on Linux outside the Docker tests):
  - the Colonization Archive (Archive Finished, Show Archive, Restore) works on Windows
  - the bright footer message color on each theme looks better than the old one
  - Create Project on Raven: the dialog was opening out of sight, and the status message was overwritten by the construction panel; both are fixed (steps in [TEST_PLAN.md](TEST_PLAN.md) section 6)
  - the Where to Buy window, the Biology card's new rows (through Test Cards) and the layout editor's top-edge snap work on Windows; Copy To Acquire was deployed and looked right
  - still to try in the game: the Biology rows on a real body with several candidate species; the offer on the COL page when a new site has no Raven project (needs sharing on and a saved key); the 30-second hold of a button's message
- Bugs found are fixed on `master` or a short bug fix branch.
- Not yet recorded for the released 1.3.0 (2026-10-29) and 1.2.0 (2026-10-28), and still open for 1.1.0 (2026-10-27) and 1.0.0 (2026-10-26): the in-game pass in [TEST_PLAN.md](TEST_PLAN.md), sections 1 to 6 (section 7 is new in 1.3.0). Sections 5 (2026-10-23) and 6 (Colonization, 2026-10-26) are the newest of those:
  - every overlay is off after the first start, for every commander, with one log line
  - a stopped expedition carries on from where it stopped, and Rescan leaves out paused and stopped time
  - Overlay Placement names where the screen size came from, and reads the real hardware size when the game's files are not found
  - long names in the Missions, Source commodities, Ship Builds and My Codex tables
  - saved data from before the spelling change still loads (`Renamed saved names:` once)
- To check on Windows with the 2026-10-27 build (needs a fleet carrier, a registered construction site and EDMC signed in to Frontier; steps in [TEST_PLAN.md](TEST_PLAN.md) section 6):
  - the Colonization FC column keeps cargo you just unloaded at your carrier when Frontier's copy lags behind: a copy that arrives within 15 minutes of your last transfer, or that repeats one already ignored, is left out until Frontier's figure changes (or Rescan Carrier is pressed)
  - each Frontier figure writes one `Carrier cargo from Frontier` line to EDMC's log; press **Copy diagnostics** after a wrong column to gather them (how to read them is in [the Colonization guide](guide/colonization.md))
  - not yet seen on either OS: the 15-minute rule and the unchanged-copy rule have been run in tests only, never against Frontier's live figure
- Native checks already made on Windows on 2026-10-23: the display probe read 3840 x 2160 at 125% scaling; the journals confirmed the Mk II jet cone boost of 6x at a neutron star and 3x at a white dwarf (V-0351).

### Linux, next pass

- Automated: 3,731 tests pass in the Docker container (13 skipped), run on 2026-10-30 for the 1.3.3 release (3,687 for 1.3.2, 3,656 for 1.3.1, 3,639 before 1.3.0, 3,485 on 2026-10-28 before 1.2.0, 3,471 on 2026-10-27 before 1.1.0, 3,447 on 2026-10-26 before 1.0.0).
- Manual: 1.3.0 (and the released 1.2.0, 1.1.0 and 1.0.0) is still to be tested on CachyOS (Arch-based) with KDE Plasma and a Flatpak EDMC.
- The steps and the ordered checks are at the top of `docs/LINUX_TESTING.md` ("Testing: start here").
- Report the session type (Wayland or X11) with the results.

### Linux, earlier passes

- A pass on 2026-10-18 (KDE Plasma, Wayland, a Flatpak EDMC) went well.
- A quick pass on 2026-10-20 found the unit and smoke tests passing, the plugin loading without errors and the Settings pages right.
- Both passes were of earlier builds of this code, before the 1.0.0 restart and rename. No manual pass has been done on Linux since; the window-fit fixes of 2026-10-21 were checked only in a Docker run (a Linux container).
- Keyboard shortcuts (all six actions) are available on Windows only, so their key choices are grayed out on Linux.
  - To hide the overlays on Linux, click the Overlays line on the panel, press **Hide / show now**, or type `!wf overlays` (turn on **Chat commands** under Settings → WFMT → General → Shortcuts).
  - Whether a Linux key binding is worth adding is an open question in `docs/TODO.md`, under Shortcuts.
- The steps and the ordered list of what to check are at the top of `docs/LINUX_TESTING.md` ("Testing: start here").
- When reporting, give:
  - the distro and desktop
  - X11 or Wayland
  - native or Flatpak EDMC
  - the relevant lines of EDMC's log (`~/.local/share/EDMarketConnector/EDMarketConnector.log`)

### Assumptions not yet confirmed in the game

- `SendText` carries the typed text in a `Message` field.
- The 2 km scanner reach behind the green ground-driven area and the drive rings. Frontier has published no figure. EDRhinoSpotter calls its 2 km "the community figure" and SrvSurvey has none (checked 2026-10-23). It cannot be measured in the game, so it stays a labeled community estimate and is no longer an open item.
- Elite's controls file is found on Linux inside the Proton or Wine folder.

### Where the in-game checks are

- The in-game checks for Materials, Engineering, the Ship planner and Expedition are in [`docs/TODO.md`](TODO.md), the public list of open work.
- The Linux versions are in `docs/LINUX_TESTING.md`.

## To pick up on the Linux machine

Written 2026-10-21 on the Windows machine. This is work done since the last Linux pass that has not been run on Linux at all.

- **Spelling fix and saved-data migration (new, not run on Linux).** British spellings in names were replaced with American ones, including the Colonization modules, tests, saved files and settings.
  - What to check after `git pull --rebase`:
    - Start EDMC once and look at the WFMT lines in the log for `Renamed saved names:`.
    - The Colonization page still shows the current project and its history, the Sites window still lists your sites, and the fleet carrier column still has its figures.
    - The Colonization overlay card is still where you put it, and is still on or off as you left it.
    - A mode you had hidden is still hidden, and the panel opens on the mode you last used.
    - Trade stock and the Exploration surveys still show what they showed before.
  - If the Colonization history looks empty, say so: it can be rebuilt from the journals.
  - The installed plugin folder may still hold modules under their old names (`colonisation_*.py`). They are not loaded and can be deleted.
  - The Docker run passes on Windows (Docker Desktop, 3,342 tests). The migration ran correctly on a copy of the Windows data, and is untested on Linux data.
- **Order to work in on Linux:**
  1. `git pull --rebase`.
  2. Run `fc-match sans`, then `python -m unittest discover -s tests -p "test_window_fit_*_smoke.py"`, and report both.
  3. `npm run test:docker` once Docker is set up.
  4. Build and deploy by hand (`npm run deploy`), then follow `docs/LINUX_TESTING.md` and the checklists in `docs/TODO.md`.
- **Docker test runner.** `npm run test:docker` (see "Running the tests without windows on your screen" in `docs/DEVELOPMENT.md`).
  - Set up Docker first: `sudo pacman -S --needed docker`, enable the service, join the `docker` group, log in again.
  - Confirm the script and image build and run there. So far it has only run on Windows with Docker Desktop.
- **Window-fit checks.** The five `test_window_fit_*` tests failed on Windows (Docker Desktop) and on Linux (desktop font Noto Sans, and Docker with DejaVu Sans), so the layouts had real problems at the smallest sizes.
  - They were fixed on Linux on 2026-10-21 (narrower entries, wrapping labels, larger minimum sizes for some windows) and pass in the Docker run (`npm run test:docker`).
  - On 2026-10-24 the native run on the Linux desktop (KDE Wayland, Noto Sans) failed all five. Expedition, the Plan dialogs, Notes and the Price finder were then fixed (taller minimums, fewer table rows, narrower boxes), with `cad6ea5` checked in Docker with DejaVu Sans and with Noto Sans (3,370 tests, 12 skipped). The windows looked right on the Linux desktop afterward by eye; the native suite has not been re-run on that commit.
  - Docker with Noto Sans reproduced only about 10 of the desktop's 101 findings, so a Docker pass does not promise a desktop pass.
  - Not yet checked natively on Windows. The Expedition and Plan dialog minimum heights went up, so check they still fit a small screen.
  - Still to check by eye:
    - Colonization Sites, Surface Mining Book, Notes, Powerplay Sessions, the Route Planner and the Mining live window, whose minimum sizes went up
    - that no minimum is too large for a small screen
  - Stretch columns in tables now clip their text to the width they get, so the checker's cut-text notes are gone. That is also new on both OSes, so look at a long name in a wide and a narrow window.
- **Screen size from the operating system (new, not run on Linux).** With no game files or overlay log to read, the screen size now comes from the primary monitor (`xrandr --current`, through the host from a Flatpak) instead of an assumed 1920 x 1080.
  - Check it: remove or rename the overlay's log so nothing else is found, open Settings → Overlays → Overlay Placement, and read the source line. It should say *using the primary display* with your real resolution.
  - Report the session type (Wayland or X11) and whether `xrandr` is installed. On Windows this reads 3840 x 2160 on the test machine (native check, 2026-10-23).
- **Every overlay off (new, not run on Linux).** One reset switches every overlay off for every commander, once (`wfmt_overlay_reset_v2`).
  - Start EDMC and look for `All WFMT overlays reset to disabled` in the log. No card should show for any commander, and one you turn on stays on after a restart.
- **Expedition clock and Rescan (new, not run on Linux).** A stopped expedition started again carries its clock on from where it stopped; Rescan leaves out paused and stopped time. Steps are in `docs/LINUX_TESTING.md`.
- **Ship planner In storage column (new, not run on Linux).** Steps are in `docs/LINUX_TESTING.md`.
- **Table text caps (new, both OSes).** The caps went to 60 on the non-stretch name columns of Missions, Source commodities, Ship Builds and My Codex. Look at a long name at a narrow and a wide size.
- **Colonization, added 2026-10-26 (not run on Linux).** Steps are in `docs/LINUX_TESTING.md` and section 6 of [TEST_PLAN.md](TEST_PLAN.md).
  - Raven Colonial: **Create Project on Raven**, the **My Projects** window (the Projects button) and finding a site's project by market id as well as name. Create Project, Mark Plan Entry Demolished and the My Projects writes have not yet run against the live service.
  - The Sites window's **Acquire** column now shows what is still to get (the need less the ship's hold and the fleet carrier), and the overlay card matches it, with no To buy column and a choice, To buy by default, of which stage of the work it lists (All, To buy or To haul); the window has the same **Show** dropdown.
  - The ship's hold is read from the game's `Cargo.json`, so the In Cargo figures follow a purchase.
  - Where to Buy, added 2026-10-31 (not run on Windows or Linux): Exclude surface ports and Exclude fleet carriers (the carriers tick is on by default since 1.4.1), the route following purchases, and the route block. Steps are in `docs/LINUX_TESTING.md`.
  - Where to Buy, added 2026-11-01 (not run on Windows or Linux): the commander's own system searched first (Find nearest and Find all), the Preset list with Large, then Medium as the default and carriers left out by default, the note when options changed since a search, and the Create Raven Colonial project dialog's primary port tick being unticked and disabled when the system already has one. Steps are in `docs/LINUX_TESTING.md` and section 10 of [TEST_PLAN.md](TEST_PLAN.md).
  - Interdiction Warning (more NPC message keys recognized, a log of the lines before an unwarned interdiction) and the Route overlay (re-reading a rewritten `NavRoute.json`, route logging), added 2026-11-01 (not run in the game).
  - Where to Buy filters, added 2026-10-31 (not run on Windows or Linux): Only stations with enough stock, Only stations with a shipyard and Arrival within (all off by default); the orbital-only check before a commodity is called surface-only; the window is taller at its minimum size.
  - The Colony page in the main window, reorganized 2026-10-31 (not run on Windows or Linux): sections, no Next line, and the last five completed sites when none is under construction.
  - Overlay choices copied from another commander (Overlay Placement tab), 2026-10-31 (not run on Windows or Linux).
  - Windows reopening on the wrong monitor: the saved position is written with an explicit plus sign (2026-10-31; not confirmed on the user's three-monitor setup yet).
  - Engineer unlock paths, the Next step column, the requirement notes and the status colors on the Engineers tab, added 2026-10-31 (not run on Windows or Linux). The checks are in [TEST_PLAN.md](TEST_PLAN.md) section 10.
  - The accent color for a search in progress. (Best single systems, first added here, were removed from the window on 2026-10-31.)
- **Color themes and the text size, added 2026-10-27 (not run on Linux).** Four themes (Navy, Cyan, Amber, Green) and a text size for WFMT's own windows, chosen in a window's bottom line or Settings → General → Window. Steps are in [LINUX_TESTING.md](LINUX_TESTING.md) sections 7k3 and 7k4 and in [TEST_PLAN.md](TEST_PLAN.md) section 6.
- **Navy look and the Acquire header, added 2026-10-27 (not run on Linux).** WFMT's own windows moved from gray to navy with a gold title, cyan headings and a soft blue footer message, and the Colonization **Remaining** column is now **Acquire**. The checks are in [LINUX_TESTING.md](LINUX_TESTING.md) section 7k2 and section 6 of [TEST_PLAN.md](TEST_PLAN.md).
- **Fleet carrier column and a lagging Frontier copy, added 2026-10-27 (not run on Linux).** The check is the same as the Windows one above, and is in section 6 of [TEST_PLAN.md](TEST_PLAN.md). The log is the Flatpak EDMC's; **Copy diagnostics** gathers the `Carrier cargo from Frontier` lines.
- **Tests.** The Docker run on Windows (Docker Desktop, a Linux container) passed all 3,370 tests on 2026-10-23. Run the suite natively on Linux too, from a desktop session, and report the count and any failure.
  - Tests that replay dated journals now use a fixed clock; `docs/DEVELOPMENT.md` explains how to look for the ones that do not.
- **Star index Update.** Update now fetches Spansh's small 1-day or 1-week file instead of the whole 173 MB dump.
  - Follow the "Local star index" steps in `docs/LINUX_TESTING.md`.
  - Report the time an update takes.
- **Expedition window.** The Expedition window, Route Planner and Expedition Log are now the Plan, Route and Log tabs of one window.
  - Follow "One Expedition window" in `docs/LINUX_TESTING.md`.
  - Say whether the window takes the focus when it opens.
- **Mining.** Three additions since the last pass, each with its steps in `docs/TODO.md` ("Verification in the game") and `docs/LINUX_TESTING.md`:
  - Mining History's *credits after limpets*.
  - The *Hold full in* line.
  - The station's price against the galactic average when docked.
  - All three read only the journal and `Market.json`, so what to check on Linux is that the journal folder is found and the lines appear.
- **Expedition section.** The panel's Expedition and Expedition Log rows are now one section.
  - Check it fits the panel and that nothing widens EDMC's window.
- **Start expedition cue.** On the Route tab, a started expedition turns the status line green and the button reads *Started ✓* for four seconds.
  - A press that starts nothing shows neither.
- **Reopening a stopped expedition** (decided 2026-10-23). Its clock picks up from the time it stopped at, and the time stopped is not counted. It applies to the Route tab's Start and the Log's Resume, and is covered by a unit test. Rescan leaves out what happened while a run was paused or between a stop and the restart, as the live count does.

## Working rules for now

- **Deploys.** Nothing deploys by itself.
  - Committing builds nothing. Builds are made by hand when one is wanted, such as when a release is cut.
  - `npm run deploy` then copies the checked-out branch's build over the EDMC plugins folder, replacing the build being tested.
  - A deploy merges: files from an older build that no longer exist stay in the folder, unused.
- **Git.**
  - Commits, pushes, version bumps, tags and releases are made by the maintainer.
  - `git pull --rebase` before starting work, and push when done.
  - Do not commit machine-specific paths or logs.
- **Conventions.**
  - American English everywhere.
  - Everything saved about play is per commander (`plugin/commander_data.py`).
  - Files use LF line endings.
- **Releasing** is described in `docs/DEVELOPMENT.md` ("Releasing").

## Decisions already made

- The tests use Mactavious, the author's own commander name (see the README and [ATTRIBUTIONS.md](ATTRIBUTIONS.md)), as a second test commander, to check that commanders' data stays apart.
- Every online lookup is either opt-in in Settings or runs only when a button is pressed, and is listed in `docs/guide/internet-and-privacy.md`.
- Out of scope: Guardian ruin surveying, landing-pad diagrams and an FSS spectrum guide.
  - The journal lacks what they would need.
  - The spectrum ranges are not in it, and no open table of them exists.
